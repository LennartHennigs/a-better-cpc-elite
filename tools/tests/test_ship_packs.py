#!/usr/bin/env python3
"""Test the ship pack ship table hook (missions_flight_k.asm) in cpcxray: with pack N in the flight tail, spawnShip must hand out the extra hull for the redirected
stock types about half the time, the stock hull the rest, and never touch types 8, 15 and 18. A, B and DE must survive the hook (C is scratch: BC is dead there, spawnShip sets B from A and BC for the ldir).

usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_ship_packs.py [PACK ...]      (default: packs 1 to 7)
Needs output/firebird_in_flight.sna and any disk in drive A (the tail is written straight into RAM, no disk load). Method as in tools/tests/test_flight_hull.py.
BUILD=128 (or tools/tests/test_ship_packs128.py): the 128K build: src/elite128, output/flight128.sna (test_flight128.py 3, regenerate it after every build) and disk/elite128.dsk; the pack's flight
image (mxFlightBase..mxFlightEnd of an assembly with -DFL_<pack>) is written into the tail at &9D9E at a stop in handleEntitys. Prints ALL OK at the end.
"""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cheat128  # noqa: E402

B128 = os.environ.get("BUILD") == "128"
SNA = "output/flight128.sna" if B128 else "output/firebird_in_flight.sna"
TRAP = 0x9F00
N = 60
# pack: {stock type: (stock label, extra label)}
PACKS = {
    1: {16: ("SHIPDATPIRATE1", "shipdatGecko")} if not B128 else {16: ("SHIPDATPIRATE1", "shipdatGecko"), 17: ("SHIPDATPIRATE2", "shipdatCobraMk1")},      # the 64K packs 1 and 2 have one hull each (room for the spawn variance routine)
    2: {17: ("SHIPDATPIRATE2", "shipdatMoray")} if not B128 else {16: ("SHIPDATPIRATE1", "shipdatWorm"), 17: ("SHIPDATPIRATE2", "shipdatMoray")},
    3: {16: ("SHIPDATPIRATE1", "shipdatMamba")},
    4: {17: ("SHIPDATPIRATE2", "shipdatAdder")},
    5: {10: ("SHIPDATBIGTRADER", "shipdatBoa")},
    6: {10: ("SHIPDATBIGTRADER", "shipdatAnaconda")},
    7: {9: ("SHIPDATSINGLETRADER", "shipdatShuttle")},
}
UNTOUCHED = {8: "shipdatViper", 15: "shipdatThargoid", 18: "shipdatThargon"}


def build(pack):
    """-> ([(address, bytes) to write into the flight snapshot], {label: address}) with pack N's flight image: the changed bytes of the 64K build against the stock file, or the 128K image slice"""
    with tempfile.TemporaryDirectory() as d:
        if B128:
            syms, raw = cheat128.assemble(ROOT / "src/elite128/commonxx.asm", d, "c", [f"-DFL_{pack}"])
            lo, hi = syms["mxFlightBase"], syms["mxFlightEnd"]
            assert hi - lo <= 0x260, (pack, hi - lo)
            return [(lo, raw[lo - 0x1A40:hi - 0x1A40])], syms
        syms, raw = cheat128.assemble(ROOT / "src/elite/commonxx.asm", d, "c", ["-DMISSIONS", f"-DFL_{pack}"])
        return [(lo, raw[lo - 0x1A40:hi - 0x1A40]) for lo, hi in patch_ranges(raw)], syms


def patch_ranges(new, gap=8):
    old = (ROOT / "work/bin_stock/COMMONXX.BIN").read_bytes()
    ranges = []
    for i, (a, b) in enumerate(zip(new, old)):
        if a != b:
            if ranges and i - ranges[-1][1] <= gap:
                ranges[-1][1] = i + 1
            else:
                ranges.append([i, i + 1])
    return [(0x1A40 + lo, 0x1A40 + hi) for lo, hi in ranges]


async def main():
    packs = [int(a) for a in sys.argv[1:]] or list(PACKS)
    params = StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])
    ok = True
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def c(n, a=None):
                x = await s.call_tool(n, a or {})
                t = "".join(getattr(i, "text", "") for i in x.content)
                try:
                    return json.loads(t)
                except ValueError:
                    return t

            async def call(addr, **regs):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr, **regs}})
                return await c("run", {"max_us": 2_000_000, "timeout_s": 60})

            for pack in packs:
                writes, syms = build(pack)
                if B128:
                    await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
                await c("sna_load", {"path": SNA})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                bp = (await c("breakpoint_add", {"address": syms["handleEntitys"], "kind": "pc"}))["id"]
                rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep
                await c("breakpoint_remove", {"breakpoint_id": bp})
                for addr, data in writes:      # the pack's code in the flight tail (stopped in handleEntitys: bank 7 is visible for getRandomNumber, the tail is bank 2)
                    await c("memory_write", {"address": addr, "data": data.hex()})
                saved = await c("registers_get")
                await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
                hook = syms["mxShipTable"]
                for typ, (stock, extra) in {**PACKS[pack], **{t: (l, l) for t, l in UNTOUCHED.items()}}.items():
                    seen = {"stock": 0, "extra": 0, "other": 0}
                    kept = True
                    for k in range(N):
                        rep = await call(hook, a=typ, bc=0x1234, de=0x5678)
                        if rep.get("pc") != "%04X" % TRAP:
                            print("  hook call did not return to the trap:", rep)
                        regs = await c("registers_get")
                        kept &= (regs["af"] >> 8) == typ and (regs["bc"] >> 8) == 0x12 and regs["de"] == 0x5678      # C is scratch: BC is dead after the hook (spawnShip rewrites it)
                        rec = regs["hl"] + 4 * typ
                        raw = bytes.fromhex((await c("memory_read", {"address": rec, "length": 3}))["hex"])
                        addr = raw[1] | raw[2] << 8
                        if raw[0] != 0xC3:
                            seen["other"] += 1
                        elif addr == syms[stock]:
                            seen["stock"] += 1
                        elif addr == syms[extra]:
                            seen["extra"] += 1
                        else:
                            seen["other"] += 1
                    redirected = typ in PACKS[pack]
                    good = seen["other"] == 0 and kept and ((seen["extra"] >= N // 4 and seen["stock"] >= N // 4) if redirected else seen["extra"] == 0 or stock == extra)
                    ok &= good
                    print(f"{'ok  ' if good else 'FAIL'} pack {pack} type {typ:2d}: stock {seen['stock']:2d}, extra {seen['extra']:2d}, other {seen['other']}, A/B/DE kept {kept}")
                await c("registers_set", {"values": {k: saved[k] for k in ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc") if k in saved}})
    print("ALL OK" if ok else "FAILURES")
    sys.exit(0 if ok else 1)


asyncio.run(main())

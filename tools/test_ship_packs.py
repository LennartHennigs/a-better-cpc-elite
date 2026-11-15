#!/usr/bin/env python3
"""Test the ship pack ship table hook (missions_flight_k.asm) in cpcxray: with pack N in the flight tail, spawnShip must hand out the extra hull for the redirected
stock types about half the time, the stock hull the rest, and never touch types 8, 15 and 18. A, B and DE must survive the hook (C is scratch: BC is dead there, spawnShip sets B from A and BC for the ldir).

usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_ship_packs.py [PACK ...]      (default: packs 1 to 7)
Needs output/firebird_in_flight.sna and any disk in drive A (the tail is written straight into RAM, no disk load). Method as in tools/test_flight_hull.py.
"""
import asyncio
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
TRAP = 0x9F00 + 0x00
N = 60
# pack: {stock type: (stock label, extra label)}
PACKS = {
    1: {16: ("SHIPDATPIRATE1", "shipdatGecko"), 17: ("SHIPDATPIRATE2", "shipdatCobraMk1")},
    2: {16: ("SHIPDATPIRATE1", "shipdatWorm"), 17: ("SHIPDATPIRATE2", "shipdatMoray")},
    3: {16: ("SHIPDATPIRATE1", "shipdatMamba")},
    4: {17: ("SHIPDATPIRATE2", "shipdatAdder")},
    5: {10: ("SHIPDATBIGTRADER", "shipdatBoa")},
    6: {10: ("SHIPDATBIGTRADER", "shipdatAnaconda")},
    7: {9: ("SHIPDATSINGLETRADER", "shipdatShuttle")},
}
UNTOUCHED = {8: "shipdatViper", 15: "shipdatThargoid", 18: "shipdatThargon"}


def build(pack):
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", f"-DFL_{pack}", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
        return out.read_bytes(), syms


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
                new, syms = build(pack)
                await c("sna_load", {"path": "output/firebird_in_flight.sna"})
                for lo, hi in patch_ranges(new):
                    await c("memory_write", {"address": lo, "data": new[lo - 0x1A40:hi - 0x1A40].hex()})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                bp = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
                rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep
                await c("breakpoint_remove", {"breakpoint_id": bp})
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

#!/usr/bin/env python3
"""The ship pack ship table hook on the 128K build (the 128K port of test_ship_packs.py): with pack N's flight image in the tail at &9D9E, mxShipTable must hand out the extra hull for the
redirected stock types about half the time and the stock hull the rest, and never touch types 8, 15 and 18; A, B and DE must survive the hook (C is scratch: BC is dead there).

usage (from work/xray, after `test_flight128.py 3`):  PATH=$HOME/.local/bin:$PATH <cpcxray python> -I /ABSOLUTE/PATH/tools/tests/test_ship_packs128.py [PACK ...]      (default: packs 1 to 7)
Needs output/flight128.sna (regenerate it after every build) and disk/elite128.dsk. The pack's image is assembled from src/elite128/commonxx.asm with -DFL_<pack> (the slice
mxFlightBase..mxFlightEnd, as build_dsk128.py cuts it) and written into RAM at &9D9E (bank 2, always visible) at a stop in handleEntitys (&CF68, bank 7 visible for getRandomNumber).
Method as in test_hulls128.py. Prints ALL OK at the end.
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
TRAP = 0x9F00
HANDLE_ENTITYS = 0xCF68
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
    """-> (the pack's flight image bytes, its load address, {label: address}) from the 128K source"""
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), f"-DFL_{pack}", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite128/commonxx.asm")], check=True, capture_output=True)
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
        lo, hi = syms["mxFlightBase"], syms["mxFlightEnd"]
        return out.read_bytes()[lo - 0x1A40:hi - 0x1A40], lo, syms


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
                image, base, syms = build(pack)
                assert len(image) <= 0x260, (pack, len(image))
                await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
                await c("sna_load", {"path": os.environ.get("SNA", "output/flight128.sna")})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                bp = (await c("breakpoint_add", {"address": HANDLE_ENTITYS, "kind": "pc"}))["id"]
                rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep
                await c("breakpoint_remove", {"breakpoint_id": bp})
                await c("memory_write", {"address": base, "data": image.hex()})      # the pack's image in the tail
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
                    print(f"{'ok  ' if good else 'FAIL'} pack {pack} type {typ:2d}: stock {seen['stock']:2d}, extra {seen['extra']:2d}, other {seen['other']}, A/B/DE kept {kept}", flush=True)
                await c("registers_set", {"values": {k: saved[k] for k in ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc") if k in saved}})
    print("ALL OK" if ok else "FAILURES")
    sys.exit(0 if ok else 1)


asyncio.run(main())

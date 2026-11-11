#!/usr/bin/env python3
"""Draw order of filled hulls (128K plan, Phase 1): spawn a near ship first and a far ship second, so the slot order is wrong for painting, and screenshot with and without the sort.

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_order128.py [NEAR_TYPE [FAR_TYPE [rev]]]
Needs output/flight128.sna and disk/elite128.dsk. Run 1 patches `ld a,1` at hullBegin to `ld a,0` (no queue: slot order, the far ship covers the near one), run 2 leaves it (queue and sort).
Screenshots output/order128_slot.png and output/order128_sorted.png.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
NEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 11
FAR = int(sys.argv[2]) if len(sys.argv) > 2 else 12
REV = len(sys.argv) > 3 and sys.argv[3] == "rev"      # spawn the far ship first (slot allocation order is not known to be ascending)
TRAP = 0x9F00
sym = {m.group(1): int(m.group(2), 16) for l in (ROOT / "work/elite128/relo/c.sym").read_text().splitlines() for m in [re.match(r"(\S+): EQU 0x([0-9A-Fa-f]+)", l)] if m}


async def run(sort):
    async with stdio_client(StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])) as (r, w):
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

            await c("disk_insert", {"drive": "A", "path": "disk/elite128.dsk"})
            await c("sna_load", {"path": "output/flight128.sna"})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            if not sort:
                await c("memory_write", {"address": sym["hullBegin"] + 1, "data": "00"})
            safe = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            await c("breakpoint_remove", {"breakpoint_id": safe})
            saved = await c("registers_get")
            trap = (await c("breakpoint_add", {"address": TRAP, "kind": "pc"}))["id"]
            await c("memory_write", {"address": 0x1C2F, "data": "00 FF 80  00 00 00  B6 7C 01"})
            ships = [(NEAR, 0x0120, 0x00), (FAR, 0x01C0, 0x00)]
            for typ, z, x in (ships[::-1] if REV else ships):
                await call(0x816B)
                ix = (await c("registers_get"))["ix"]
                await call(0x80CD, a=typ, ix=ix)
                ix = (await c("registers_get"))["ix"]
                for off, val in ((0, x), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, z & 255), (7, z >> 8), (8, 0), (27, 0), (37, 0x7F)):
                    await c("memory_write", {"address": ix + off, "data": "%02X" % val})
                flag = (await c("memory_read", {"address": ix + 32, "length": 1}))["hex"]
                await c("memory_write", {"address": ix + 32, "data": "%02X" % (int(flag, 16) & ~0x40)})
                await call(0x82B8, ix=ix)
            await c("breakpoint_remove", {"breakpoint_id": trap})
            await c("registers_set", {"values": {k: saved[k] for k in ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc", "af_", "bc_", "de_", "hl_") if k in saved}})
            await c("run", {"max_us": 1_500_000, "timeout_s": 60})
            await c("screen_image", {"path": "output/order128_%s%s.png" % ("sorted" if sort else "slot", "_rev" if REV else "")})
            reg = await c("registers_get")
            print("sorted" if sort else "slot order", f"pc=&{reg['pc']:04X} sp=&{reg['sp']:04X}", flush=True)


async def main():
    await run(False)
    await run(True)


asyncio.run(main())

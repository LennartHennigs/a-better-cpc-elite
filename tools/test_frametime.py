#!/usr/bin/env python3
"""Frame time of the game loop with one ship ahead: stock wireframe against the 128K filled hull (128K plan, Phase 1 gate: within +25%).

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_frametime.py DISK.dsk SNAPSHOT.sna [TYPE [ZHIGH]]
  e.g. test_frametime.py disk/elite128.dsk output/flight128.sna 12 1        and        test_frametime.py disk/Elite_UK_Firebird_cracked_trainer.dsk output/firebird_in_flight.sna 12 1
TYPE: ship type to spawn straight ahead (none: empty space); ZHIGH: high byte of its z (1 = 256..511). Measures the emulated time between 12 consecutive stops at
handleEntitys (&5066, once per frame) and prints the mean and the spread in ms.
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DISK, SNA = sys.argv[1], sys.argv[2]
TYPE = int(sys.argv[3]) if len(sys.argv) > 3 else None
ZH = int(sys.argv[4]) if len(sys.argv) > 4 else 1
TRAP = 0x9F00


async def main():
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

            await c("disk_insert", {"drive": "A", "path": DISK})
            await c("sna_load", {"path": SNA})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            bp = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            if TYPE is not None:
                saved = await c("registers_get")
                trap = (await c("breakpoint_add", {"address": TRAP, "kind": "pc"}))["id"]
                await c("memory_write", {"address": 0x1C2F, "data": "00 FF 80  00 00 00  B6 7C 01"})
                await call(0x816B)
                ix = (await c("registers_get"))["ix"]
                await call(0x80CD, a=TYPE, ix=ix)
                ix = (await c("registers_get"))["ix"]
                for off, val in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, ZH), (8, 0), (27, 0), (37, 0x7F)):
                    await c("memory_write", {"address": ix + off, "data": "%02X" % val})
                flag = (await c("memory_read", {"address": ix + 32, "length": 1}))["hex"]
                await c("memory_write", {"address": ix + 32, "data": "%02X" % (int(flag, 16) & ~0x40)})
                await call(0x82B8, ix=ix)
                await c("breakpoint_remove", {"breakpoint_id": trap})
                await c("registers_set", {"values": {k: saved[k] for k in ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc", "af_", "bc_", "de_", "hl_") if k in saved}})
            await c("run", {"max_us": 1_000_000, "timeout_s": 60})
            ts = []
            for _ in range(13):
                await c("run", {"max_us": 3_000_000, "timeout_s": 60})
                ts.append((await c("machine_status"))["clock_us"])
            d = [(b - a) / 1000 for a, b in zip(ts, ts[1:])]
            print(f"{DISK.split('/')[-1]} type {TYPE}: frame mean {sum(d) / len(d):.1f} ms  min {min(d):.1f}  max {max(d):.1f}  ({len(d)} frames)")


asyncio.run(main())

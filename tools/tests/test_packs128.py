#!/usr/bin/env python3
"""Ship packs on the 128K build: launch from the docked snapshot with no mission and each pack number k = (jumpCounter + system seed byte) & 7, and check that image k is the one in the tail
(flight id &9DB9 = k, the vector table is the pack's) and that the game then runs (flight pc, screenshot output/packs128_<k>.png).

Needs output/docked128.sna (tools/tests/snap_docked128.py, rebuild it after every code change) and disk/elite128.dsk. usage (from work/xray): <cpcxray python> -I ../../tools/tests/test_packs128.py [K ...]
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

JUMP_COUNTER, SYSTEM_SEED, MISSION, MISSION2, TRUMBLES = 0x38DA, 0x390D, 0x38FD, 0x38FE, 0x3905
FLIGHT_ID = 0x9DB9
PACKS = [int(a) for a in sys.argv[1:]] or list(range(8))


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

            async def rd(a, n=1):
                return bytes.fromhex((await c("memory_read", {"address": a, "length": n}))["hex"])

            ok = True
            for k in PACKS:
                await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
                await c("sna_load", {"path": "output/docked128.sna"})
                await c("run", {"max_us": 1_000_000, "timeout_s": 60})
                await c("memory_write", {"address": MISSION, "data": "00"})
                await c("memory_write", {"address": MISSION2, "data": "00"})
                await c("memory_write", {"address": TRUMBLES, "data": "00 00"})
                await c("memory_write", {"address": JUMP_COUNTER, "data": "%02X" % k})
                await c("memory_write", {"address": SYSTEM_SEED, "data": "00"})
                await c("key_press", {"key": "f1"})
                await c("run", {"max_us": 6_000_000, "timeout_s": 120})
                await c("key_release", {"key": "f1"})
                await c("run", {"max_us": 8_000_000, "timeout_s": 120})
                fid = (await rd(FLIGHT_ID))[0]
                reg = await c("registers_get")
                await c("screen_image", {"path": f"output/packs128_{k}.png"})
                if os.environ.get("SAVE"):      # a flight snapshot with pack k loaded, for test_hulls128.py (SNA=output/pack128_k.sna, types 16 17 9 10 ...)
                    await c("sna_save", {"path": f"output/pack128_{k}.sna"})
                good = fid == k
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} pack {k}: flight id {fid}, tail {(await rd(0x9D9E, 6)).hex(' ')}, pc={reg['pc']:04X}")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

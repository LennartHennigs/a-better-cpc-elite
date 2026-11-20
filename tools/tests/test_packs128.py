#!/usr/bin/env python3
"""Ship packs on the 128K build: the pack is drawn at random at every launch (mxFlightNone: getRandomNumber & 7). This test launches from the docked snapshot with no mission N times
(the random seed is poked differently each time), checks that the id in the tail (&9DB9) is a pack 0-7 whose vector table is in place and that the game runs,
and that more than one pack turns up. Screenshots output/packs128_<n>.png; with SAVE=1 a flight snapshot output/pack128_<id>.sna per pack seen.

Needs output/docked128.sna (tools/tests/snap_docked128.py, rebuild it after every code change) and disk/elite128.dsk. usage (from work/xray): <cpcxray python> -I ../../tools/tests/test_packs128.py [K ...]
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

JUMP_COUNTER, SYSTEM_SEED, MISSION, MISSION2, TRUMBLES = 0x38DA, 0x390D, 0x38FD, 0x38FE, 0x3905
FLIGHT_ID = 0x9DBC
RANDOM_SEED = 0xFA56      # storedRandomSeed (common2x.asm, bank 7 at &C000+)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10      # launches
SEED0 = int(os.environ.get("SEED0", "0"))      # shifts the poked seeds (another set of packs)


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

            ok, seen = True, []
            for n in range(N):
                await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
                await c("sna_load", {"path": "output/docked128.sna"})
                await c("run", {"max_us": 1_000_000, "timeout_s": 60})
                await c("memory_write", {"address": RANDOM_SEED, "data": "%02X %02X" % ((n * 37 + 11 + SEED0) & 255, (n * 91 + 5) & 255)})      # a different random state at the launch (the generator only moves when called)
                await c("memory_write", {"address": MISSION, "data": "00"})
                await c("memory_write", {"address": MISSION2, "data": "00"})
                await c("memory_write", {"address": TRUMBLES, "data": "00 00"})
                await c("key_press", {"key": "f1"})
                await c("run", {"max_us": 6_000_000, "timeout_s": 120})
                await c("key_release", {"key": "f1"})
                await c("run", {"max_us": 8_000_000, "timeout_s": 120})
                fid = (await rd(FLIGHT_ID))[0]
                reg = await c("registers_get")
                tail = await rd(0x9D9E, 3)
                await c("screen_image", {"path": f"output/packs128_{n}.png"})
                if os.environ.get("SAVE"):
                    await c("sna_save", {"path": f"output/pack128_{fid}.sna"})
                good = fid <= 7 and tail[0] == 0xC3
                ok &= good
                seen.append(fid)
                print(f"{'ok  ' if good else 'FAIL'} launch {n}: pack {fid}, tail {tail.hex(' ')}, pc={reg['pc']:04X}", flush=True)
            print("packs seen:", sorted(set(seen)))
            ok &= len(set(seen)) > 1
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

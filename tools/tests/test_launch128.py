#!/usr/bin/env python3
"""Launch from the docked snapshot (tools/snap_docked128.py) with a mission state set and check the flight image copied from bank 5.

usage (from work/xray):  DISK128=disk/elite128.dsk PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_launch128.py [STATE_HEX]    (default 71: Constrictor hunting)
Sets &38D9 = 1 and &38FD = STATE, presses f1, stops at the bank copy routine (&9C83 jump table, mxBankFlight) and at its end, then reports the tail &9D9E and the flight id (&9DBC).
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

STATE = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x71
SLOTS = "01234567CPTSR"      # flight image ids are slot numbers (missions_flight.asm): 0 default, 1-7 ship packs, 8-12 C P T S R


def nm(v):
    return SLOTS[v] if v < len(SLOTS) else "?"


TR = int(os.environ.get("TR", "0"), 0)      # Trumbles aboard (16 bit count at &3905)


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

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("sna_load", {"path": "output/docked128.sna"})
            await c("run", {"max_us": 1_000_000, "timeout_s": 60})
            await c("memory_write", {"address": 0x38D9, "data": "01"})
            await c("memory_write", {"address": 0x38FD, "data": "%02X" % STATE})
            await c("memory_write", {"address": 0x3905, "data": "%02X %02X" % (TR & 255, TR >> 8)})
            print("tail before:", (await rd(0x9D9E, 8)).hex(" "), " id:", nm((await rd(0x9DBC))[0]))
            bp = (await c("breakpoint_add", {"address": 0x9C83, "kind": "pc"}))["id"]
            await c("key_press", {"key": "f1"})
            rep = await c("run", {"max_us": 6_000_000, "timeout_s": 120})
            print("stop:", rep.get("reason"), rep.get("registers"))
            await c("key_release", {"key": "f1"})
            if rep.get("reason") == "breakpoint":
                reg = await c("registers_get")
                print("A =", nm(reg["af"] >> 8), " sp=%04X" % reg["sp"])
                await c("breakpoint_remove", {"breakpoint_id": bp})
                await c("run", {"max_us": 400_000, "timeout_s": 60})
                print("tail after the copy:", (await rd(0x9D9E, 8)).hex(" "), " id:", nm((await rd(0x9DBC))[0]))
                await c("run", {"max_us": 6_000_000, "timeout_s": 120})
            reg = await c("registers_get")
            print("tail at the end:", (await rd(0x9D9E, 8)).hex(" "), " pc=%04X sp=%04X" % (reg["pc"], reg["sp"]))
            await c("screen_image", {"path": "output/launch128.png"})


asyncio.run(main())

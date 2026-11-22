#!/usr/bin/env python3
"""Laser sights of the 128K build (lasersights128.asm, overlay on bankInit): screenshots output/sights128_<type>.png of the front view with laser type 0 (none), 1 pulse, 2 beam, 3 military, 4 mining.

Needs output/flight128.sna (tools/tests/test_flight128.py 3) and disk/elite128.dsk. usage (from work/xray): <cpcxray python> -I ../../tools/tests/test_sights128.py
Look at the centre of each shot: no sight for 0, the cross for 1, bars with ticks for 2, double diagonals for 3, bars without ends and a dot for 4.
"""
import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DISK = os.environ.get("DISK128", "disk/elite128.dsk")
LASER_TYPES = 0x38F4


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

            await c("disk_insert", {"drive": "A", "path": DISK})
            for t in range(5):
                await c("sna_load", {"path": "output/flight128.sna"})
                await c("memory_write", {"address": LASER_TYPES, "data": "%02X" % t})
                await c("run", {"max_us": 2_500_000, "timeout_s": 60})
                await c("screen_image", {"path": f"output/sights128_{t}.png"})
                print("type", t, (await c("registers_get"))["pc"])


asyncio.run(main())

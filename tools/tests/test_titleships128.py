#!/usr/bin/env python3
"""Cycle the title-screen ship (cursor keys, -DTITLESEL) on the 128K disk and take a screenshot of each hull: output/ts128_NN.png.

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_titleships128.py [N]     (default 16 ships; 29 shows them all)
Prints the ship index (splash2Shipnr, &1DA8, bits 0-4) and the demo ship's blueprint pointer (&1B51 + 35) per shot, so each picture can be matched to a ship type.
"""
import asyncio
import os
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

N = int(sys.argv[1]) if len(sys.argv) > 1 else 16


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
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("type_text", {"text": 'RUN"ELITE128\n', "wait": False})
            await c("run", {"max_us": 28_000_000, "timeout_s": 120})
            await c("key_press", {"key": "n"})                  # the ship choice works on the second title screen ("Press Space, Commander")
            await c("run", {"max_us": 1_400_000, "timeout_s": 60})
            await c("key_release", {"key": "n"})
            await c("run", {"max_us": 5_000_000, "timeout_s": 60})
            for i in range(N):
                await c("run", {"max_us": 2_500_000, "timeout_s": 60})
                idx = (await rd(0x1DA8))[0]
                p = await rd(0x1B51 + 35, 2)
                await c("screen_image", {"path": f"output/ts128_{i:02d}.png"})
                print(f"{i:02d} ship index {idx & 0x1F} blueprint &{p[0] | p[1] << 8:04X}", flush=True)
                await c("key_press", {"key": "cursor_right"})
                await c("run", {"max_us": 300_000, "timeout_s": 60})
                await c("key_release", {"key": "cursor_right"})


asyncio.run(main())

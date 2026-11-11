#!/usr/bin/env python3
"""Boot a 128K disk, start a new commander and save the docked state: output/docked128.sna (for quick tests of launch and docking hooks).

usage (from work/xray):  DISK128=disk/elite128_missions.dsk PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/snap_docked128.py
"""
import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


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

            async def press(key, secs):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 120})
                await c("key_release", {"key": key})

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("type_text", {"text": 'RUN"ELITE\n', "wait": False})
            await c("run", {"max_us": 36_000_000, "timeout_s": 120})
            await press("n", 1.4)
            await c("run", {"max_us": 8_000_000, "timeout_s": 120})
            await press("space", 1.4)
            await c("run", {"max_us": 12_000_000, "timeout_s": 120})
            await c("sna_save", {"path": "output/docked128.sna"})
            print("saved output/docked128.sna")


asyncio.run(main())

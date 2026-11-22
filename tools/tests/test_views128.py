#!/usr/bin/env python3
"""Load output/flight128.sna (tools/tests/test_flight128.py) and look through the other views: screenshots output/views128_<key>.png.

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_views128.py [KEY ...]   (default: f2 f3 f4 f1)
"""
import asyncio
import os
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

KEYS = sys.argv[1:] or ["f2", "f3", "f4", "f1"]


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

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("sna_load", {"path": "output/flight128.sna"})
            await c("run", {"max_us": 2_000_000, "timeout_s": 60})
            for k in KEYS:
                await c("key_press", {"key": k})
                await c("run", {"max_us": 1_400_000, "timeout_s": 60})
                await c("key_release", {"key": k})
                await c("run", {"max_us": 3_000_000, "timeout_s": 60})
                reg = await c("registers_get")
                await c("screen_image", {"path": f"output/views128_{k}.png"})
                print(k, f"pc=&{reg['pc']:04X} sp=&{reg['sp']:04X}", flush=True)


asyncio.run(main())

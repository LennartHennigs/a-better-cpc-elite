#!/usr/bin/env python3
"""The ship viewer (RUN"SHOWSHPS) from the 128K disk: SHOWSHPS.BAS starts the game with a poke that skips the first title screen, so it opens on "Press Space, Commander" with the Cobra Mk III;
the right cursor key steps through the ships. Screenshots output/viewer128_<n>.png.

Needs disk/elite128.dsk (tools/build_dsk128.py; SHIPS.BIN comes from tools/mk_showship.py). usage (from work/xray): <cpcxray python> -I ../../tools/tests/test_viewer128.py
No pass/fail: look at the pictures (the first one also shows whether the quote in RUN"SHOWSHPS was typed correctly).
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

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("type_text", {"text": 'run"showshps\n', "wait": False})
            await c("run", {"max_us": 40_000_000, "timeout_s": 200})
            await c("screen_image", {"path": "output/viewer128_0.png"})
            for n in (1, 2):
                await c("key_press", {"key": "cursor_right"})
                await c("run", {"max_us": 600_000, "timeout_s": 60})
                await c("key_release", {"key": "cursor_right"})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                await c("screen_image", {"path": f"output/viewer128_{n}.png"})
            print("pc", (await c("registers_get"))["pc"])


asyncio.run(main())

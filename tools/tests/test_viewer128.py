#!/usr/bin/env python3
"""The ship viewer (RUN"SHOWSHPS) from the 128K disk: SHOWSHPS.BAS loads the ships into RAM banks 4-6 and the viewer (src/viewer128/viewer.asm) at &8000; filled ships turn on the screen,
the cursor keys select, Q returns to BASIC. Screenshots output/viewer128_<n>.png: the first ship, two more after the right cursor key, the last ship after the left cursor key, and BASIC after Q.

Needs disk/elite128.dsk (tools/build_dsk128.py). usage (from work/xray): <cpcxray python> -I ../../tools/tests/test_viewer128.py
No pass/fail: look at the pictures.
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
            await c("run", {"max_us": 45_000_000, "timeout_s": 300})
            await c("screen_image", {"path": "output/viewer128_0.png"})
            for n in (1, 2):
                await c("key_press", {"key": "cursor_right"})
                await c("run", {"max_us": 600_000, "timeout_s": 60})
                await c("key_release", {"key": "cursor_right"})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                await c("screen_image", {"path": f"output/viewer128_{n}.png"})
            for n in (3, 4, 5):      # back round the list: ship 2, ship 1, then the last one (the Constrictor, 29/29)
                await c("key_press", {"key": "cursor_left"})
                await c("run", {"max_us": 600_000, "timeout_s": 60})
                await c("key_release", {"key": "cursor_left"})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("screen_image", {"path": "output/viewer128_last.png"})
            await c("key_press", {"key": "q"})
            await c("run", {"max_us": 400_000, "timeout_s": 60})
            await c("key_release", {"key": "q"})
            await c("run", {"max_us": 3_000_000, "timeout_s": 60})
            await c("screen_image", {"path": "output/viewer128_3.png"})
            print("pc", (await c("registers_get"))["pc"])


asyncio.run(main())

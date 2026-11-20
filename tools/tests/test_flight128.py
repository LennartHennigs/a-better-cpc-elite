#!/usr/bin/env python3
"""Boot the 128K disk, start a new commander, launch and fly: screenshots of the filled hulls in flight (128K plan, Phase 1).

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_flight128.py [FLIGHT_STEPS]
Long (minutes of real time): start it detached, e.g. python3 -c "import subprocess;subprocess.Popen([...], start_new_session=True, stdout=open('output/flight128.log','w'))".
Writes output/flight128_NN.png and output/flight128.sna (the game in flight), prints PC/SP and the state after each step.
"""
import asyncio
import os
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 6


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

            async def look(tag, n):
                reg = await c("registers_get")
                await c("screen_image", {"path": f"output/flight128_{n:02d}.png"})
                print(f"{n:02d} {tag}: pc=&{reg['pc']:04X} sp=&{reg['sp']:04X}", flush=True)

            async def press(key, secs):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 120})
                await c("key_release", {"key": key})

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("type_text", {"text": 'RUN"ELITE\n', "wait": False})
            await c("run", {"max_us": 30_000_000, "timeout_s": 120})
            await look("title", 1)
            await press("n", 1.4)
            await c("run", {"max_us": 6_000_000, "timeout_s": 120})
            await look("after N", 2)
            await press("space", 1.4)
            await c("run", {"max_us": 10_000_000, "timeout_s": 120})
            await look("docked", 3)
            await press("f1", 1.4)
            await c("run", {"max_us": 4_000_000, "timeout_s": 120})
            for i in range(STEPS):
                await c("run", {"max_us": 8_000_000, "timeout_s": 120})
                await look("flight", 4 + i)
            await c("sna_save", {"path": "output/flight128.sna"})
            print("saved output/flight128.sna", flush=True)


asyncio.run(main())

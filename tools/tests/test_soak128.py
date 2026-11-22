#!/usr/bin/env python3
"""Soak test of the 128K build in flight: run MINUTES of emulated time from output/flight128.sna with a PC breakpoint at &0000 (a reset) and report.

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_soak128.py [MINUTES]    (default 10; start it detached)
Runs in 30 s steps, prints pc/sp per step and saves output/soak128_NN.png every 5th step; stops early if the reset breakpoint fires.
"""
import asyncio
import os
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 10


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
            await c("breakpoint_add", {"address": 0x0000, "kind": "pc"})
            for i in range(MIN * 2):
                rep = await c("run", {"max_us": 30_000_000, "timeout_s": 300})
                reg = await c("registers_get")
                print(f"{(i + 1) * 30:4d} s  {rep.get('reason')}  pc=&{reg['pc']:04X} sp=&{reg['sp']:04X}", flush=True)
                if i % 5 == 4:
                    await c("screen_image", {"path": f"output/soak128_{i:02d}.png"})
                if rep.get("reason") == "breakpoint":
                    print("RESET (pc reached &0000)")
                    await c("screen_image", {"path": "output/soak128_reset.png"})
                    break
            else:
                print("no reset")


asyncio.run(main())

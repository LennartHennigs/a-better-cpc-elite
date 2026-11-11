#!/usr/bin/env python3
"""Boot work/xray/disk/elite128.dsk (tools/build_dsk128.py) in cpcxray and look at the title screen: screenshots and the state of bank 6.

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_boot128.py [SECONDS]
Types RUN"ELITE, runs SECONDS (default 40) of emulated time in 5 s steps, saves output/boot128_NN.png each step, then saves output/boot128.sna and checks the
snapshot: RAM config (byte 0x41), the first bytes of bank 6 (the fill module, flat 128K layout: bank n at 0x100 + n * 0x4000) and the fill table.
"""
import asyncio
import os
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SECS = int(sys.argv[1]) if len(sys.argv) > 1 else 40


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
            await c("type_text", {"text": 'RUN"ELITE\n', "wait": False})
            for i in range(SECS // 5):
                await c("run", {"max_us": 5_000_000, "timeout_s": 120})
                await c("screen_image", {"path": f"output/boot128_{i:02d}.png"})
                reg = await c("registers_get")
                print(f"{(i + 1) * 5:3d} s  pc=&{reg['pc']:04X} sp=&{reg['sp']:04X}", flush=True)
            await c("sna_save", {"path": "output/boot128.sna"})
            d = Path("output/boot128.sna").read_bytes()
            b6 = d[0x100 + 6 * 0x4000:0x100 + 7 * 0x4000]
            print("RAM config byte:", hex(d[0x41]), " bank 6 starts:", b6[:12].hex(" "), " table at +0x6000-0x4000:", b6[0x2000:0x2010].hex(" "))
            print("edge block (+0x1D00):", b6[0x1D00:0x1D08].hex(" "), " squares (+0x1500):", b6[0x1500:0x1508].hex(" "))


asyncio.run(main())

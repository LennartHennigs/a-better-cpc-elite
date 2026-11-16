#!/usr/bin/env python3
"""Screenshots of the docked screens with the -DENHANCED changes (headlines in column 2, status labels, cash on the quantity line) in cpcxray.

Build first:  python3 -I tools/build_dsk.py --de|--fr ; cp work/elite_{de,fr}_rebuilt.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_station_screens.py en|de|fr
Boots the disk, starts a new commander (N, then Space), then writes output/station_<loc>_{status,chart,buy,inventory}.png (keys 8, 5, 2 + a good, 9).
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

LOC = sys.argv[1] if len(sys.argv) > 1 else "de"
DISK, RUN = {"en": ("disk/elite_rebuilt.dsk", 'run"elite\n'), "de": ("disk/elite_de_rebuilt.dsk", 'run"elite\n'), "fr": ("disk/elite_fr_rebuilt.dsk", 'run"el\n')}[LOC]


async def main():
    params = StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def c(name, args=None):
                x = await s.call_tool(name, args or {})
                t = "".join(getattr(i, "text", "") for i in x.content)
                try:
                    return json.loads(t)
                except ValueError:
                    return t

            async def tap(key, secs=1.3):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 60})
                await c("key_release", {"key": key})
                await c("run", {"max_us": 800_000, "timeout_s": 60})

            async def shot(name):
                await c("screen_image", {"path": f"output/station_{LOC}_{name}.png"})

            await c("disk_insert", {"drive": "A", "path": DISK})
            await c("run", {"max_us": 3_000_000, "timeout_s": 60})
            await c("type_text", {"text": RUN, "wait": False})
            bp = (await c("breakpoint_add", {"address": 0x1CD9, "kind": "pc"}))["id"]   # the first title loop
            for _ in range(8):
                if (await c("run", {"max_us": 10_000_000, "timeout_s": 120})).get("reason") == "breakpoint":
                    break
            await c("breakpoint_remove", {"breakpoint_id": bp})
            await c("run", {"max_us": 1_000_000, "timeout_s": 60})
            await tap("n")
            await c("run", {"max_us": 3_000_000, "timeout_s": 60})
            await tap("space")
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            for key, name in (("8", "status"), ("5", "chart"), ("9", "inventory")):
                await tap(key)
                await shot(name)
            await tap("2")
            await tap("1", 0.5)
            await shot("buy")
            print("wrote output/station_%s_*.png" % LOC)


asyncio.run(main())

"""Boot a disk in cpcxray, run 45 s of emulated time and save a screenshot of the title.

usage (from work/xray): ~/.local/share/uv/tools/cpcxray/bin/python -I ../../.claude/skills/release/boot_check.py disk/X.dsk ELITE64 output/x.png
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

disk, program, out = sys.argv[1:4]


async def main():
    params = StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def c(name, args=None):
                x = await s.call_tool(name, args or {})
                text = "".join(getattr(i, "text", "") for i in x.content)
                try:
                    return json.loads(text)
                except ValueError:
                    return text

            await c("run", {"max_us": 3_000_000})
            await c("disk_insert", {"drive": "A", "path": disk})
            await c("type_text", {"text": f'RUN"{program}\r', "wait": False})
            await c("run", {"max_us": 45_000_000, "timeout_s": 120})
            await c("screen_image", {"path": out})
            print(disk, "pc=%04X" % (await c("registers_get"))["pc"], "->", out)


asyncio.run(main())

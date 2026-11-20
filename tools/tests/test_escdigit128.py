#!/usr/bin/env python3
"""Esc at the second digit of a buy quantity must undo the first digit's trade (128K build, -DENHANCED; main's ad72b30). Prints the Food hold and the cash after "1" and after "1", Esc.

Needs output/docked128.sna (tools/tests/snap_docked128.py) and disk/elite128.dsk. usage (from work/xray): <cpcxray python> -I ../../tools/tests/test_escdigit128.py
Pass: after "1" the hold has 1 t of Food and less cash; after Esc the hold and the cash are back to the start values. "ok"/"FAIL" is printed.
"""
import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DISK = os.environ.get("DISK128", "disk/elite128.dsk")


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

            async def rd(addr, n):
                return bytes.fromhex((await c("memory_read", {"address": addr, "length": n}))["hex"])

            async def tap(key, secs=1.3):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 60})
                await c("key_release", {"key": key})
                await c("run", {"max_us": 800_000, "timeout_s": 60})

            await c("disk_insert", {"drive": "A", "path": DISK})
            await c("sna_load", {"path": "output/docked128.sna"})
            await tap("2", 0.6)                               # buy menu; the first prompt waits for a key
            start = (await rd(0x38E2, 1), await rd(0x38DD, 4))
            await tap("1", 0.12)
            mid = (await rd(0x38E2, 1), await rd(0x38DD, 4))
            await tap("esc", 0.12)
            end = (await rd(0x38E2, 1), await rd(0x38DD, 4))
            print("start", [x.hex() for x in start], "after 1", [x.hex() for x in mid], "after Esc", [x.hex() for x in end])
            print("ok" if mid != start and end == start else "FAIL")


asyncio.run(main())

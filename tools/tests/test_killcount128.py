#!/usr/bin/env python3
"""Kill count on the commander page of the 128K build ("Rating: Poor - 20"): screenshots output/kc128_<name>.png for 600, 20 and 3 kills (no pass/fail, look at them).
Needs output/docked128.sna (tools/tests/snap_docked128.py) and disk/elite128.dsk. usage (from work/xray): <cpcxray python> -I ../../tools/tests/test_killcount128.py
Sets the kill word at killScore+1 (&38D8), opens the market (8) and then the commander page (9): the snapshot already shows the old page, so it would not redraw."""
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    async with stdio_client(StdioServerParameters(command="cpcxray", args=["mcp","--config","config/cpc6128.toml"])) as (r,w):
        async with ClientSession(r,w) as s:
            await s.initialize()
            async def c(n,a=None):
                x=await s.call_tool(n,a or {}); t="".join(getattr(i,"text","") for i in x.content)
                try: return json.loads(t)
                except ValueError: return t
            for name,kills in (("big",600),("poor",20),("harmless",3),):
                await c("disk_insert",{"drive":"A","path":"disk/elite128.dsk"})
                await c("sna_load",{"path":"output/docked128.sna"})
                await c("memory_write",{"address":0x38D8,"data":"%02X %02X"%(kills&255,kills>>8)})
                await c("key_press",{"key":"8"}); await c("run",{"max_us":1_300_000,"timeout_s":60}); await c("key_release",{"key":"8"}); await c("run",{"max_us":1_500_000,"timeout_s":60}); await c("key_press",{"key":"9"}); await c("run",{"max_us":1_300_000,"timeout_s":60}); await c("key_release",{"key":"9"})
                r=await c("run",{"max_us":3_000_000,"timeout_s":60})
                await c("screen_image",{"path":f"output/kc128_{name}.png"})
asyncio.run(main())

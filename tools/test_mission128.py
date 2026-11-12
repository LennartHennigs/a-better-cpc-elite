#!/usr/bin/env python3
"""128K build, missions from RAM banks: docked overlay and flight image without the disk (128K plan, Phase 2).

Build first:  python3 -I tools/build_dsk128.py ; cp work/elite128.dsk work/xray/disk/
usage (from work/xray):  DISK128=disk/elite128.dsk PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_mission128.py
Boots, starts a new commander (N, space: docked at Lave), sets 256 kill points and the Constrictor state "hunting, all hints" (&71), calls the docking hook (&1714) and takes a
screenshot (output/mission128_docked.png: the overlay was copied from bank 4); the launch check is tools/test_launch128.py. Prints bytes read back so a failure is visible. Long: start it detached.
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

            async def rd(a, n=1):
                return bytes.fromhex((await c("memory_read", {"address": a, "length": n}))["hex"])

            async def press(key, secs):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 120})
                await c("key_release", {"key": key})

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("type_text", {"text": 'RUN"ELITE\n', "wait": False})
            await c("run", {"max_us": 36_000_000, "timeout_s": 120})
            await c("screen_image", {"path": "output/mission128_0title.png"})
            await press("n", 1.4)
            await c("run", {"max_us": 8_000_000, "timeout_s": 120})
            await c("screen_image", {"path": "output/mission128_1n.png"})
            await press("space", 1.4)
            await c("run", {"max_us": 12_000_000, "timeout_s": 120})
            await c("screen_image", {"path": "output/mission128_2docked.png"})
            print("overlay area before:", (await rd(0x17FD, 8)).hex(" "))
            await c("memory_write", {"address": 0x38D9, "data": "01"})      # 256 kill points
            await c("memory_write", {"address": 0x38FD, "data": "00"})      # no mission yet: the Constrictor offer at the next docking
            await c("memory_write", {"address": 0x1F00, "data": "00"})
            sp = (await c("registers_get"))["sp"] - 2
            TRAP = 0x9F00
            await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
            await c("registers_set", {"values": {"sp": sp, "pc": 0x1714}})
            await c("run", {"max_us": 4_000_000, "timeout_s": 120})
            print("overlay area after the hook:", (await rd(0x17FD, 8)).hex(" "))
            await c("screen_image", {"path": "output/mission128_docked.png"})
            # The hook was injected with a return address at TRAP (&9F00, zeros), so it cannot be left by a key press: the launch part is test_launch128.py (state &71, image C copied from bank 5).
            reg = await c("registers_get")
            print(f"pc=&{reg['pc']:04X} sp=&{reg['sp']:04X}")


asyncio.run(main())

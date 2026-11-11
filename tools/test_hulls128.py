#!/usr/bin/env python3
"""Spawn every ship type (0..18) straight ahead in the 128K build, one at a time, and screenshot it: output/hulls128_NN.png (128K plan, Phase 1).

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_hulls128.py [TYPE ...]
Needs output/flight128.sna (tools/test_flight128.py) and disk/elite128.dsk. Method of tools/test_flight_hull.py: stop at handleEntitys (&5066), lookforFreeSlot (&816B) gives IX,
spawnShip (&80CD) builds the type, the position is set ahead (z = &180, big hulls farther), setDirectionofEntity (&82B8) builds the orientation (nose pointing away from us),
run 1 s, screenshot, then the slot is emptied. With identity orientation every hull is seen from behind.
"""
import asyncio
import os
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TRAP = 0x9F00
TYPES = [int(a) for a in sys.argv[1:]] or list(range(19))
FAR = {0: 0x0700, 15: 0x0300, 11: 0x0300, 10: 0x0300, 6: 0x0200, 7: 0x0200}      # z high byte word: stations and big hulls farther away


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

            async def call(addr, **regs):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr, **regs}})
                return await c("run", {"max_us": 2_000_000, "timeout_s": 60})

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("sna_load", {"path": "output/flight128.sna"})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            safe = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            await c("breakpoint_remove", {"breakpoint_id": safe})
            saved = await c("registers_get")
            trap_bp = (await c("breakpoint_add", {"address": TRAP, "kind": "pc"}))["id"]
            await c("memory_write", {"address": 0x1C2F, "data": "00 FF 80  00 00 00  B6 7C 01"})      # planet far to the left
            for t in TYPES:
                await call(0x816B)
                ix = (await c("registers_get"))["ix"]
                await call(0x80CD, a=t, ix=ix)
                ix = (await c("registers_get"))["ix"]
                z = FAR.get(t, 0x0180)
                for off, val in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, z & 255), (7, z >> 8), (8, 0), (27, 0), (37, 0x7F)):
                    await c("memory_write", {"address": ix + off, "data": "%02X" % val})
                flag = (await c("memory_read", {"address": ix + 32, "length": 1}))["hex"]
                await c("memory_write", {"address": ix + 32, "data": "%02X" % (int(flag, 16) & ~0x40)})
                await call(0x82B8, ix=ix)
                await c("registers_set", {"values": {k: saved[k] for k in ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc", "af_", "bc_", "de_", "hl_") if k in saved}})
                await c("run", {"max_us": 1_000_000, "timeout_s": 60})
                await c("screen_image", {"path": f"output/hulls128_{t:02d}.png"})
                reg = await c("registers_get")
                print(f"type {t:2d}: pc=&{reg['pc']:04X} sp=&{reg['sp']:04X}", flush=True)
                await c("memory_write", {"address": ix + 34, "data": "00"})                              # empty the slot
                await c("run", {"max_us": 300_000, "timeout_s": 60})
                rep = await c("run_until", {"address": 0x5066, "max_us": 3_000_000})
                saved = await c("registers_get")


asyncio.run(main())

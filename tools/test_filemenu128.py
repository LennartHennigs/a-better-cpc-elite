#!/usr/bin/env python3
"""128K disk menu test: catalogue, save a commander, change a byte, load it back (the game stack lives in bank 7, so the firmware calls run on discStack).

usage (from work/xray, after `python3 -I tools/snap_docked128.py`):
  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_filemenu128.py
Works on a copy of the disk (disk/elite128_w.dsk, inserted writable); the emulator only changes its in-memory image. Calls FileMenu (&0D28) from output/docked128.sna.
The key presses after a menu choice leak one character into the name prompt, so the save is named "2" and the load types "1", DEL, "2".
"""
import asyncio
import json
import shutil
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CMDR_BYTE = 0x38E0   # a field inside the 104-byte commander block


async def main():
    shutil.copy("disk/elite128.dsk", "disk/elite128_w.dsk")
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

            async def key(k, hold=250_000, after=12_000_000):
                await c("key_press", {"key": k})
                await c("run", {"max_us": hold, "timeout_s": 60})
                await c("key_release", {"key": k})
                await c("run", {"max_us": after, "timeout_s": 120})

            async def typ(t):
                await c("type_text", {"text": t, "wait": False})
                await c("run", {"max_us": 6_000_000, "timeout_s": 120})
                await c("run", {"max_us": 15_000_000, "timeout_s": 120})

            async def byte():
                return int((await c("memory_read", {"address": CMDR_BYTE, "length": 1}))["hex"], 16)

            await c("disk_insert", {"drive": "A", "path": "disk/elite128_w.dsk", "writable": True})
            await c("sna_load", {"path": "output/docked128.sna"})
            await c("run", {"max_us": 500_000, "timeout_s": 60})
            sp = (await c("registers_get"))["sp"] - 2
            await c("memory_write", {"address": sp, "data": "00 9F"})
            await c("registers_set", {"values": {"sp": sp, "pc": 0x0D28}})
            await c("run", {"max_us": 1_500_000, "timeout_s": 60})
            ok = True

            await key("3")                                   # catalogue
            await c("screen_image", {"path": "output/fm_cat.png"})
            await key("space", after=1_000_000)
            await key("2")                                   # save
            await typ("TEST\n")
            files = [f["name"] for f in (await c("disk_catalog", {"drive": "A"}))["files"]]
            print("save:", "2.BIN" in files)
            ok &= "2.BIN" in files
            before = await byte()
            await c("memory_write", {"address": CMDR_BYTE, "data": "%02X" % (before ^ 0x55)})
            await key("1")                                   # load
            await key("del", after=500_000)
            await typ("2")
            await key("return")
            after = await byte()
            print("load: byte %02X -> %02X -> %02X" % (before, before ^ 0x55, after))
            ok &= after == before
            await c("screen_image", {"path": "output/fm_load.png"})
            print("PASS" if ok else "FAIL")
            return ok


sys.exit(0 if asyncio.run(main()) else 1)

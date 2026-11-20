"""Tokenise src/cheats/$PROG.ASC (default TRAINER.ASC) with the CPC's own BASIC (cpcxray, headless).

Run from work/xray with cpcxray's interpreter (tools/build_cheat.sh does this):
    ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/cheat_tokenise.py
Expects disk/tmp_asc.dsk (the ASCII file on a scratch disk); writes disk/tmp_tok.dsk with TRAINER.BAS (or $PROG.BAS).
"""
import asyncio
import os
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def main():
    params = StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def call(name, **args):
                await s.call_tool(name, args)

            await call("run", max_us=3_000_000)
            await call("disk_insert", path="disk/tmp_asc.dsk", drive="A", writable=True)
            prog = os.environ.get("PROG", "TRAINER")
            for cmd in (f'LOAD"{prog}.ASC"\r', f'SAVE"{prog}.BAS"\r'):
                await call("type_text", text=cmd, wait=True, timeout_s=60)
                await call("run", max_us=8_000_000)
            await call("disk_save", drive="A", path="disk/tmp_tok.dsk")


asyncio.run(main())

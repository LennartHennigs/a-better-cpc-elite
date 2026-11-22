#!/usr/bin/env python3
"""Probe: what do the projected vertices (buf_5860) and the line endpoints look like in the stock engine? (128K plan, Phase 1 step 5/6)

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/probe_vertices.py
Loads output/firebird_at_entry.sna (title screen, the Cobra turns), stops at todo_parseEdges (&5D67), dumps buf_5860 (x, y, flag per vertex), then stops at the
first call of SUB_ram_7c45 (the line routine) and prints its arguments (HL, DE = the two endpoints, C = flags), so the coordinate system can be read off.
"""
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PARSE_EDGES, LINE, BUF = 0x5D67, 0x7C45, 0x5860


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

            await c("disk_insert", {"drive": "A", "path": "disk/Elite_UK_Firebird_cracked_trainer.dsk"})
            await c("sna_load", {"path": "output/firebird_at_entry.sna"})
            b1 = (await c("breakpoint_add", {"address": PARSE_EDGES, "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 15_000_000, "timeout_s": 120})
            print("stop:", rep.get("reason"))
            reg = await c("registers_get")
            hdr = bytes.fromhex((await c("memory_read", {"address": reg["iy"], "length": 23}))["hex"])
            nv = hdr[3]
            buf = bytes.fromhex((await c("memory_read", {"address": BUF, "length": 3 * nv}))["hex"])
            print(f"IY=&{reg['iy']:04X} IX=&{reg['ix']:04X} vertices {nv}, edges {hdr[4]}, header {hdr.hex()}")
            for i in range(nv):
                x, y, f = buf[3 * i:3 * i + 3]
                print(f"  v{i:2d}: x={x:3d} y={y:3d} flag={f:02X}")
            await c("breakpoint_remove", {"breakpoint_id": b1})
            await c("breakpoint_add", {"address": LINE, "kind": "pc"})
            for k in range(4):
                rep = await c("run", {"max_us": 5_000_000, "timeout_s": 60})
                reg = await c("registers_get")
                print(f"line {k}: stop {rep.get('reason')}  HL=&{reg['hl']:04X} (h={reg['hl'] >> 8} l={reg['hl'] & 255})  DE=&{reg['de']:04X} (d={reg['de'] >> 8} e={reg['de'] & 255})  C=&{reg['bc'] & 255:02X}")
                await c("step", {"count": 1})
asyncio.run(main())

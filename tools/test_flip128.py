#!/usr/bin/env python3
"""Page flip check (128K plan, phase 3): from output/flight128.sna (tools/test_flight128.py) sample the flip state for a few seconds and compare the two screens.

usage (from work/xray):  DISK128=disk/elite128m.dsk PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_flip128.py
Prints curCfg / dbShown / dbOn at 40 instants (the two banks must alternate), then saves a snapshot, and compares the cockpit rows (rows 16-23 of each 2 KB scan line block) of bank 1 and
bank 3 (they differ only for the bytes of the frame in progress) and the view rows (they must differ: one frame apart).
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
sym = {}
for l in (ROOT / "work/elite128/fill.sym").read_text().splitlines():
    pass
csym = {}
for p in ("work/elite128/relo/c.sym",):
    f = ROOT / p
    if f.exists():
        for l in f.read_text().splitlines():
            m = re.match(r"(\S+): EQU 0x([0-9A-Fa-f]+)", l)
            if m:
                csym[m.group(1)] = int(m.group(2), 16)


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
            await c("sna_load", {"path": "output/flight128.sna"})
            await c("run", {"max_us": 2_000_000, "timeout_s": 60})
            seen = []
            for i in range(40):
                await c("run", {"max_us": 137_000, "timeout_s": 60})
                m = bytes.fromhex((await c("memory_read", {"address": csym["curCfg"], "length": 1}))["hex"])
                sh = bytes.fromhex((await c("memory_read", {"address": csym["dbShown"], "length": 3}))["hex"])
                seen.append("%02X/%02X/%d" % (m[0], sh[0], sh[2]))
            print(" ".join(seen))
            await c("sna_save", {"path": "output/flip128.sna"})
    d = open("output/flip128.sna", "rb").read()
    b1, b3 = d[0x100 + 0x4000:0x100 + 0x8000], d[0x100 + 0xC000:0x100 + 0x10000]
    cock = [(k * 0x800 + 0x400 + i) for k in range(8) for i in range(512)]
    view = [(k * 0x800 + i) for k in range(8) for i in range(0x400)]
    print("cockpit bytes differing:", sum(b1[i] != b3[i] for i in cock), "of", len(cock))
    print("view bytes differing:", sum(b1[i] != b3[i] for i in view), "of", len(view))


asyncio.run(main())

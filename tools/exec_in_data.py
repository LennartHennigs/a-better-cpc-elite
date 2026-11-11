#!/usr/bin/env python3
"""Find code that the disassembly still holds as data: put execute breakpoints on every data range of the stock image and play (cpcxray).

usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/exec_in_data.py OUT.json RANGES.json [RANGES2.json ...] [--presses N] [--sna FILE] [--seed S]
RANGES.json: [[start, end], ...] from tools/db_ranges.py. Loads output/firebird_in_flight.sna (or --sna), adds one pc breakpoint per range, presses random keys (1.3 s holds as CLAUDE.md
says) and runs. A hit at PC means the byte at PC is executed although the disassembly calls it data; the hit is recorded and the range split around it so the next different address
is found too. OUT.json = {"hits": [addresses], "sna": ..., "presses": N}, written after every press. Feed the hits to tools/disasm_stock.py as extra seeds (docs: tools/db_ranges.py).
"""
import asyncio
import json
import random
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

args = sys.argv[1:]
out = Path(args.pop(0))
presses, sna, seed = 200, "output/firebird_in_flight.sna", 1
files = []
while args:
    a = args.pop(0)
    if a == "--presses":
        presses = int(args.pop(0))
    elif a == "--sna":
        sna = args.pop(0)
    elif a == "--seed":
        seed = int(args.pop(0))
    else:
        files.append(a)
KEYS = list("abcdefghijklmnopqrstuvwxyz0123456789") + ["space", "enter", "cursor_left", "cursor_right", "cursor_up", "cursor_down", "f1", "f2", "f3", "f4"]


async def main():
    random.seed(seed)
    ranges = [tuple(r) for f in files for r in json.loads(Path(f).read_text())]
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
            await c("sna_load", {"path": sna})
            bps = {}
            for a, b in ranges:
                rep = await c("breakpoint_add", {"address": a, "end": b, "kind": "pc"})
                bps[rep["id"]] = (a, b)
            print(len(bps), "breakpoints", flush=True)
            hits = []

            async def drain(max_us):
                while True:
                    rep = await c("run", {"max_us": max_us, "timeout_s": 120})
                    if rep.get("reason") != "breakpoint":
                        return
                    pc = int(rep["pc"], 16) if isinstance(rep["pc"], str) else rep["pc"]
                    hit = next((i for i, (a, b) in bps.items() if a <= pc <= b), None)
                    if hit is None:
                        return
                    a, b = bps.pop(hit)
                    await c("breakpoint_remove", {"breakpoint_id": hit})
                    hits.append(pc)
                    for lo, hi in ((a, pc - 1), (pc + 1, b)):
                        if lo <= hi:
                            bps[(await c("breakpoint_add", {"address": lo, "end": hi, "kind": "pc"}))["id"]] = (lo, hi)

            for n in range(presses):
                k = random.choice(KEYS)
                await c("key_press", {"key": k})
                await drain(1_300_000)
                await c("key_release", {"key": k})
                await drain(500_000)
                out.write_text(json.dumps({"hits": sorted(set(hits)), "sna": sna, "presses": n + 1}))
                if n % 10 == 0:
                    print(f"press {n + 1}: {len(set(hits))} distinct hits", flush=True)


asyncio.run(main())

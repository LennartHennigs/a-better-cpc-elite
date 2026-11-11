#!/usr/bin/env python3
"""Which bytes of the screen-page gaps does the game write at run time? (128K plan, phase 3: gap contents are duplicated in two screen banks, so anything written there must move.)

usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/write_in_gaps.py OUT.json [--presses N] [--sna FILE] [--seed S]
Loads the snapshot (default output/firebird_in_flight.sna), sets a write breakpoint on every gap range (rows 24-31 of each 2 KB chunk of &C000-&FFFF: &C600-&C7FF, &CE00-&CFFF, ...) and
on the few non-blank bytes in the visible rows (&C000-&C0FF), plays random keys (1.3 s holds) and records every written address with the PC that wrote it (the range is split around a
known address so each new one is found). OUT.json: {"writes": {"EFF6": ["PC", ...], ...}}.
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
presses, sna, seed = 120, "output/firebird_in_flight.sna", 1
while args:
    a = args.pop(0)
    if a == "--presses":
        presses = int(args.pop(0))
    elif a == "--sna":
        sna = args.pop(0)
    elif a == "--seed":
        seed = int(args.pop(0))
KEYS = list("abcdefghijklmnopqrstuvwxyz0123456789") + ["space", "enter", "cursor_left", "cursor_right", "cursor_up", "cursor_down", "f1", "f2", "f3", "f4"]
RANGES = [(0xC600 + k * 0x800, 0xC7FF + k * 0x800) for k in range(8)]


async def main():
    random.seed(seed)
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
            bps, writes = {}, {}
            for a, b in RANGES:
                bps[(await c("breakpoint_add", {"address": a, "end": b, "kind": "write"}))["id"]] = (a, b)

            async def drain(max_us):
                while True:
                    rep = await c("run", {"max_us": max_us, "timeout_s": 120})
                    if rep.get("reason") != "breakpoint":
                        return
                    bp = rep.get("breakpoint") or {}
                    adr = bp.get("address")
                    pc = bp.get("pc") or (rep["pc"] if isinstance(rep["pc"], str) else "%04X" % rep["pc"])
                    if adr is None:
                        return
                    a = int(adr, 16) if isinstance(adr, str) else adr
                    writes.setdefault("%04X" % a, set()).add(pc)
                    hit = next((i for i, (lo, hi) in bps.items() if lo <= a <= hi), None)
                    if hit is None:
                        return
                    lo, hi = bps.pop(hit)
                    await c("breakpoint_remove", {"breakpoint_id": hit})
                    for q in ((lo, a - 1), (a + 1, hi)):
                        if q[0] <= q[1]:
                            bps[(await c("breakpoint_add", {"address": q[0], "end": q[1], "kind": "write"}))["id"]] = q

            for n in range(presses):
                k = random.choice(KEYS)
                await c("key_press", {"key": k})
                await drain(1_300_000)
                await c("key_release", {"key": k})
                await drain(500_000)
                out.write_text(json.dumps({"writes": {a: sorted(p) for a, p in sorted(writes.items())}, "presses": n + 1}))
                if n % 10 == 0:
                    print(f"press {n + 1}: {len(writes)} distinct gap addresses written", flush=True)


asyncio.run(main())

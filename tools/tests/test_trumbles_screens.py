#!/usr/bin/env python3
"""Watch the Trumbles multiply on the real flight screen in cpcxray and take screenshots at several stages. No pass/fail: look at the pictures.

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_trumbles_screens.py

Loads the in-flight snapshot, writes the patches of a COMMONXX built with -DMISSIONS -DFL_T (as tools/tests/test_trumbles.py), starts with one Trumble and lets the
game run. Between stages the game's own arrival code (mxArrive, one hyperspace jump each) doubles the count, and above 255 the spawn check adds one now and then.
Screenshots: output/trumbles_1_one.png, _2_after_jump.png, _3_after_jumps.png, _4_swarm.png (what is drawn: one sprite per Trumble up to six).
"""
import asyncio
import json
import re
import subprocess
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
TRAP = 0x9FF4 - 4
COUNT = 0x3905
KEEP = ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc")


def build():
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", "-DFL_T", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], check=True, capture_output=True)
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
        return out.read_bytes(), syms


def patch_ranges(new, gap=8):
    old = (ROOT / "work/bin_stock/COMMONXX.BIN").read_bytes()
    ranges = []
    for i, (a, b) in enumerate(zip(new, old)):
        if a != b:
            if ranges and i - ranges[-1][1] <= gap:
                ranges[-1][1] = i + 1
            else:
                ranges.append([i, i + 1])
    return [(0x1A40 + lo, 0x1A40 + hi) for lo, hi in ranges]


async def main():
    new, syms = build()
    sites = patch_ranges(new)
    params = StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def c(n, a=None):
                x = await s.call_tool(n, a or {})
                t = "".join(getattr(i, "text", "") for i in x.content)
                try:
                    return json.loads(t)
                except ValueError:
                    return t

            async def count():
                b = bytes.fromhex((await c("memory_read", {"address": COUNT, "length": 2}))["hex"])
                return b[0] | b[1] << 8

            async def set_count(n):
                await c("memory_write", {"address": COUNT, "data": "%02X %02X" % (n & 255, n >> 8)})

            async def stop_at_entitys():
                bp = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
                rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep
                await c("breakpoint_remove", {"breakpoint_id": bp})

            async def jump():
                """one hyperspace arrival through the game's own mxArrive, then back to where the game was"""
                await stop_at_entitys()
                saved = await c("registers_get")
                sp = saved["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": syms["mxArrive"], "af": 0x0100}})
                rep = await c("run", {"max_us": 5_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint" and rep.get("pc") == "%04X" % TRAP, rep
                await c("registers_set", {"values": {k: saved[k] for k in KEEP if k in saved}})

            async def watch(seconds, name, text):
                await c("run", {"max_us": seconds * 1_000_000, "timeout_s": 300})
                shot = f"output/trumbles_{name}.png"
                await c("screen_image", {"path": shot})
                print(f"{text}: count {await count()}  -> work/xray/{shot}")

            await c("disk_insert", {"drive": "A", "path": "disk/elite_missions.dsk"})
            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await stop_at_entitys()
            for lo, hi in sites:
                await c("memory_write", {"address": lo, "data": new[lo - 0x1A40:hi - 0x1A40].hex()})
            await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
            await set_count(1)
            await watch(20, "1_one", "one Trumble aboard, 20 s of flight")
            await jump()
            await watch(25, "2_after_jump", "after one jump (2 x ((1 + 0..15) OR 4))")
            await jump()
            await jump()
            await watch(30, "3_after_jumps", "after two more jumps")
            while await count() < 256:
                await jump()
            await watch(60, "4_swarm", "256 or more: six drawn, the spawn check now adds one and squeaks")


asyncio.run(main())

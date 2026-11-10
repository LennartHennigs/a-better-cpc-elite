#!/usr/bin/env python3
"""Build and run the filled-ship prototype in cpcxray.

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/proto_fill/run.py [--noguard] [--664] [--ship NAME]
  --noguard  assemble with -DGUARD=0: the 300 Hz handler calls &6000 while bank 4 is mapped there
  --664      run on the 64 KB machine config (no banking): the RAM check must report 0
  --flip     the page-flip build (flip.asm) instead of the bounding-box build (fill.asm)
  --ship N   other ArcElite ship (runs tools/proto_fill/gen.py first)
Writes screenshots output/proto_fill_*.png and prints: has128, the 300 Hz tick counts, and the emulated time per frame (clear, draw).
"""
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
PD = ROOT / "tools/proto_fill"
WORK = ROOT / "work/proto_fill"
NOGUARD = "--noguard" in sys.argv
M664 = "--664" in sys.argv
FLIP = "--flip" in sys.argv
SHIP = sys.argv[sys.argv.index("--ship") + 1] if "--ship" in sys.argv else "COBRA"


def build():
    subprocess.run([sys.executable, "-I", str(PD / "gen.py")] + (["--ships"] if FLIP else [SHIP]), check=True)
    name = "flip" if FLIP else "proto"
    sym = WORK / f"{name}.sym"
    flags = ["-DGUARD=0"] if NOGUARD and not FLIP else []
    subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), *flags, f"--sym={sym}", "flip.asm" if FLIP else "fill.asm"], cwd=PD, check=True, capture_output=True)
    labels = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+): EQU 0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
    if FLIP:                    # the ship files and the program go on the disk the program loads them from
        subprocess.run([sys.executable, "-I", str(PD / "mkdsk.py")], check=True)
        subprocess.run(["cp", str(WORK / "proto.dsk"), str(ROOT / "work/xray/disk/proto.dsk")], check=True)
    return (WORK / f"{name}.bin").read_bytes(), labels


async def main():
    blob, lab = build()
    cfg = "config/cpc664.toml" if M664 else "config/cpc6128.toml"
    params = StdioServerParameters(command="cpcxray", args=["mcp", "--config", cfg])
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

            async def rd(addr, n):
                return bytes.fromhex((await c("memory_read", {"address": addr, "length": n}))["hex"])

            await c("run", {"max_us": 4_000_000, "timeout_s": 60})          # boot to BASIC
            if FLIP:                    # the whole file as RUN would load it: ship data at &1000, the program at &8000
                await c("memory_write", {"address": 0x1000, "data": (WORK / "flip.img").read_bytes().hex()})
            else:
                await c("memory_write", {"address": 0x8000, "data": blob.hex()})
            await c("registers_set", {"values": {"pc": lab["start"]}})
            await c("run", {"max_us": 12_000_000 if FLIP else 3_000_000, "timeout_s": 120})   # the flip build loads its ships from disk first
            has = (await rd(lab["has128"], 1))[0]
            print("has128 =", has, "(machine config", cfg + ")")
            if not has:
                print(await c("screen_image", {"path": "output/proto_fill_no128.png"}))
                return
            bp = (await c("breakpoint_add", {"address": lab["frameDone"], "kind": "pc"}))["id"]
            times = []
            for i in range(48):
                t0 = (await c("machine_status"))["clock_us"]
                rep = await c("run", {"max_us": 2_000_000, "timeout_s": 60})
                t1 = (await c("machine_status"))["clock_us"]
                if rep.get("reason") != "breakpoint":
                    print("no frame end after", (t1 - t0) / 1000, "ms: the program stopped drawing. reason:", rep.get("reason"), "pc:", (await c("registers_get"))["pc"])
                    break
                times.append((t1 - t0) / 1000)
                if i == 8:
                    print(await c("screen_image", {"path": "output/proto_fill_a.png"}))
                if i == 14:
                    print(await c("screen_image", {"path": "output/proto_fill_b.png"}))
            await c("breakpoint_remove", {"breakpoint_id": bp})
            tl = await rd(lab["tickLog"], 96)
            print("frame times ms (breakpoint to breakpoint):", [round(t) for t in times[8:24]])
            if times:
                print("frame time ms: min %.0f mean %.0f max %.0f" % (min(times[4:]), sum(times[4:]) / len(times[4:]), max(times[4:])))
            ticks = [(tl[4 * k] | tl[4 * k + 1] << 8, tl[4 * k + 2] | tl[4 * k + 3] << 8) for k in range(24)]
            print("300 Hz ticks per frame (clear, draw):", ticks)
            ic = (await rd(lab["isrCount"], 2))
            print("isrCount", ic[0] | ic[1] << 8)
asyncio.run(main())

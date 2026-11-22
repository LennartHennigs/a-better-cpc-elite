#!/usr/bin/env python3
"""Frame time of the flight loop: stock wireframe against the 128K filled build, in the same view (optionally a ship straight ahead).

usage (from work/xray, absolute script path):
  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I SCRIPT DISK.dsk SNAPSHOT.sna SYMFILE [options]
  128K:  DISK=disk/elite128.dsk  SNAPSHOT=output/flight128.sna          SYMFILE=../../work/elite128/c128.sym   (run test_flight128.py 3 first)
  64K:   DISK=disk/Elite_UK_Firebird_cracked_trainer.dsk  SNAPSHOT=output/firebird_in_flight.sna  SYMFILE=../../work/elite128/c.sym
options:
  --ship TYPE[,ZHIGH]   spawn this ship type straight ahead (z = ZHIGH*256, default 1); none: no ship
  --clean               empty the ship slots first (cleanShipSlots): the 128K launch snapshot has a second entity beside the planet, the 64K one has the planet only
  --poke ADDR=HEX,...   write bytes at the frame stop, e.g. 1A47=50 (slot 0's z high byte: the planet leaves the scanner range)
  --frames N            number of frames to time (default 12)
  --shot FILE.png       screenshot after the run
  --phases              also stop at the phase marks (transferBuffertoScreen; 128K: the flip, the vsync wait, the copy) and print the mean time from one mark to the next
  --marks A,B,...       stop at these symbols instead (names from SYMFILE or from the fill.sym beside it, or hex addresses); implies --phases
Symbols come from SYMFILE (handleEntitys, lookforFreeSlot, spawnShip, setDirectionofEntity, cleanShipSlots; the 128K ones move with every build, which is how the old fixed
addresses went stale) and, for the flip marks in bank 6, from fill.sym in the same folder. Time is measured between stops at handleEntitys (once per frame), as emulated clock.
"""
import asyncio
import json
import os
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

args = sys.argv[1:]
DISK, SNA, SYM = args[0], args[1], args[2]
opts = args[3:]


def opt(name, default=None):
    """the value after an option, or the default when the option is absent"""
    return opts[opts.index(name) + 1] if name in opts else default


SHIP = opt("--ship")
FRAMES = int(opt("--frames", 12))
SHOT = opt("--shot")
POKE = opt("--poke")
EXTRA = opt("--marks")
PHASES = "--phases" in opts or EXTRA is not None
CLEAN = "--clean" in opts
TRAP = 0x9F00


def load_sym(path):
    d = {}
    for ln in open(path):
        m = re.match(r"(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", ln)
        if m:
            d[m.group(1)] = int(m.group(2), 16)
    return d


sym = load_sym(SYM)
fill = load_sym(os.path.join(os.path.dirname(SYM), "fill.sym")) if os.path.exists(os.path.join(os.path.dirname(SYM), "fill.sym")) else {}
FRAME = sym["handleEntitys"]

# Phase marks, in the order they are hit within one frame. 64K: the start and the end of transferBuffertoScreen (the buffer-to-screen copy; the `ret` is the byte before
# tbmLoopCounter). 128K: the same start, then the flip (dbFlipTail = end of the transfer; fill.sym labels in bank 6: dbfw1 = start of the vsync wait, dbfCmp = the wait and the
# CRTC switch are over, dbfGaps = the cockpit zones are copied).
MARKS = {"xfer": sym["transferBuffertoScreen"]}
if "dbFlipTail" in sym:
    MARKS["flipTail"] = sym["dbFlipTail"]
    MARKS.update({n: fill[n] for n in ("dbfw1", "dbfCmp", "dbfGaps") if n in fill})
else:
    MARKS["xferEnd"] = sym["tbmLoopCounter"] - 1
if EXTRA is not None:
    names = {**fill, **sym}
    MARKS = {n: (names[n] if n in names else int(n, 16)) for n in EXTRA.split(",") if n in names or re.fullmatch(r"[0-9A-Fa-f]{3,4}", n)}   # names the symbol files lack are skipped


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

            await c("disk_insert", {"drive": "A", "path": DISK})
            await c("sna_load", {"path": SNA})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("breakpoint_add", {"address": FRAME, "kind": "pc"})
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            if SHIP is not None or CLEAN or POKE:
                saved = await c("registers_get")
                trap = (await c("breakpoint_add", {"address": TRAP, "kind": "pc"}))["id"]
                if CLEAN:
                    await call(sym["cleanShipSlots"])
                for item in (POKE.split(",") if POKE else []):
                    a_, _, v_ = item.partition("=")
                    await c("memory_write", {"address": int(a_, 16), "data": v_.replace(":", " ")})
                if SHIP is not None:
                    ty, _, zs = SHIP.partition(",")
                    await call(sym["lookforFreeSlot"])
                    ix = (await c("registers_get"))["ix"]
                    await call(sym["spawnShip"], a=int(ty), ix=ix)
                    ix = (await c("registers_get"))["ix"]
                    await c("memory_write", {"address": ix, "data": "00 00 00 00 00 00 00 %02X 00" % int(zs or 1)})      # x, y, z = 0, 0, ZHIGH*256 (all positive)
                    await c("memory_write", {"address": ix + 27, "data": "00"})
                    await c("memory_write", {"address": ix + 37, "data": "7F"})
                    flag = (await c("memory_read", {"address": ix + 32, "length": 1}))["hex"]
                    await c("memory_write", {"address": ix + 32, "data": "%02X" % (int(flag, 16) & ~0x40)})
                    await call(sym["setDirectionofEntity"], ix=ix)
                await c("breakpoint_remove", {"breakpoint_id": trap})
                await c("registers_set", {"values": {k: saved[k] for k in ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc", "af_", "bc_", "de_", "hl_") if k in saved}})
            await c("run", {"max_us": 1_000_000, "timeout_s": 60})
            marks = {}
            if PHASES:
                for name, addr in MARKS.items():
                    marks[addr] = name
                    await c("breakpoint_add", {"address": addr, "kind": "pc"})
            ev = []
            while True:
                rep = await c("run", {"max_us": 3_000_000, "timeout_s": 60})
                t = (await c("machine_status"))["clock_us"]
                pc = int(rep["pc"], 16) if isinstance(rep, dict) and "pc" in rep else -1
                ev.append((t, "frame" if pc == FRAME else marks.get(pc, "?%04X" % pc)))
                if sum(1 for _, n in ev if n == "frame") > FRAMES:
                    break
            if SHOT:
                await c("screen_image", {"path": SHOT})
            fr = [t for t, n in ev if n == "frame"]
            d = [(b - a) / 1000 for a, b in zip(fr, fr[1:])]
            print(f"{DISK.split('/')[-1]} ship {SHIP}: frame mean {sum(d) / len(d):.1f} ms  min {min(d):.1f}  max {max(d):.1f}  ({len(d)} frames)")
            if PHASES:
                # per frame, the marks in the order they were first hit; the time from the previous mark (or the frame stop) is collected per mark name
                acc, cur, start, last = {}, set(), None, None
                for t, n in ev:
                    if n == "frame":
                        if start is not None:
                            acc.setdefault("-> next frame", []).append((t - last) / 1000)
                        start, last, cur = t, t, set()
                    elif start is not None and n not in cur:
                        cur.add(n)
                        acc.setdefault(n, []).append((t - last) / 1000)
                        last = t
                for k, v in acc.items():
                    print(f"  {'to ' + k if k[0] != '-' else k:28s} mean {sum(v) / len(v):6.1f} ms  min {min(v):6.1f}  max {max(v):6.1f}  ({len(v)})")

asyncio.run(main())

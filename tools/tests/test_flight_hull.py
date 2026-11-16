#!/usr/bin/env python3
"""Spawn the Constrictor (ship type 19) in cpcxray and look at it.

Build and copy first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_flight_hull.py [TYPE] [--fl TAG] [--extra LABEL]
(--fl 3 --extra shipdatMamba 16 builds ship pack 3 and spawns type 16 until the pack's Mamba comes up, as the pack hook redirects half the spawns)

From output/firebird_in_flight.sna: lookforFreeSlot (&816B) gives IX, spawnShip (&80CD) builds type TYPE (default 19) there, the position is set
ahead of the player, then 2 s run and a screenshot (output/missions_ship.png). Prints the blueprint address stored in the slot (ix+35/36) and whether the
slot survived (ix+34 non-zero after the run). The addresses are for the -DMISSIONS build (spawnShip &80CD, lookforFreeSlot &816B); stock has the same.
"""
import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TRAP = 0x9F00
ROOT = Path(__file__).resolve().parent.parent.parent


def patch_ranges(new, gap=8):
    """byte ranges where the built COMMONXX differs from the stock one (call sites, the tail, the CPC+ byte): written into the snapshot's RAM"""
    old = (ROOT / "work/bin_stock/COMMONXX.BIN").read_bytes()
    ranges = []
    for i, (a, b) in enumerate(zip(new, old)):
        if a != b:
            if ranges and i - ranges[-1][1] <= gap:
                ranges[-1][1] = i + 1
            else:
                ranges.append([i, i + 1])
    return [(0x1A40 + lo, 0x1A40 + hi) for lo, hi in ranges]


FL = sys.argv[sys.argv.index("--fl") + 1] if "--fl" in sys.argv else "C"
EXTRA = sys.argv[sys.argv.index("--extra") + 1] if "--extra" in sys.argv else None
SYMS = {}


def built_commonxx():
    """assemble COMMONXX with -DMISSIONS (the snapshot holds the stock code; only LARGEAXX comes from the disk)"""
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", f"-DFL_{FL}", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        import re
        SYMS.update({m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)})
        return out.read_bytes()
TYPE = int(next((a for a in sys.argv[1:] if a.isdigit()), 19))
PRINTCHAR = 0x44A9   # printCharAtLocationXY


async def main():
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

            async def call(addr, **regs):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr, **regs}})
                return await c("run", {"max_us": 2_000_000, "timeout_s": 60})

            await c("disk_insert", {"drive": "A", "path": "disk/elite_missions.dsk"})
            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            new, base = built_commonxx(), 0x1A40
            for lo, hi in patch_ranges(new):   # every call site and the flight tail
                await c("memory_write", {"address": lo, "data": new[lo - base:hi - base].hex()})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})   # the snapshot is still undocking: let the launch finish
            # Stop at a safe point before injecting calls: the screen-fill routines use SP as a write pointer inside the bitmap, and a call
            # pushed there draws stray lines (or crashes the game). handleEntitys (&5066) runs with the normal stack.
            safe = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            await c("breakpoint_remove", {"breakpoint_id": safe})
            saved = await c("registers_get")      # restored after the injected calls: the game must resume where it stopped
            trap_bp = (await c("breakpoint_add", {"address": TRAP, "kind": "pc"}))["id"]
            rep = await call(0x816B)
            ix = (await c("registers_get"))["ix"]
            print("free slot IX = %04X" % ix)
            for _ in range(40 if EXTRA else 1):
                rep = await call(0x80CD, a=TYPE, ix=ix)
                ix = (await c("registers_get"))["ix"]
                bpa = bytes.fromhex((await c("memory_read", {"address": ix + 35, "length": 2}))["hex"])
                if not EXTRA or bpa[0] | bpa[1] << 8 == SYMS[EXTRA]:
                    break
            else:
                sys.exit(f"{EXTRA} never came up")
            hdr = bytes.fromhex((await c("memory_read", {"address": ix + 34, "length": 3}))["hex"])
            print("slot flags %02X, blueprint address %04X" % (hdr[0], hdr[1] | hdr[2] << 8))
            for off, val in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0x01), (6, 0x80), (8, 0), (27, 0), (37, 0x7F)):   # z 384 straight ahead, speed 0 so it hangs there, hostile flags like spawnCommand1
                await c("memory_write", {"address": ix + off, "data": "%02X" % val})
            flag = (await c("memory_read", {"address": ix + 32, "length": 1}))["hex"]
            await c("memory_write", {"address": ix + 32, "data": "%02X" % (int(flag, 16) & ~0x40)})   # res 6,(ix+32): spawnShip sets it, the game re-places such ships (loc_83AA clears it)
            await c("memory_write", {"address": 0x1C2F, "data": "00 FF 80  00 00 00  B6 7C 01"})   # posDataPlanet far to the left (as `far` in test_star_occlusion.py): the view is full of the planet otherwise and a ship ahead would be inside it
            print("  after writes:", (await c("memory_read", {"address": ix, "length": 9}))["hex"])
            await call(0x82B8, ix=ix)
            print("  after setDirectionofEntity:", (await c("memory_read", {"address": ix, "length": 9}))["hex"])                     # setDirectionofEntity: builds the orientation, without it the ship is not drawn
            await c("breakpoint_remove", {"breakpoint_id": trap_bp})
            await c("registers_set", {"values": {k: saved[k] for k in ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc", "af_", "bc_", "de_", "hl_") if k in saved}})
            if "--fill" in sys.argv:   # watch the stack loads of the fill routine (ld sp,hl at &F636): HL must stay inside the bitmap &A000-&C000
                fb = (await c("breakpoint_add", {"address": 0xF636, "kind": "pc"}))["id"]
                bad, seen = [], 0
                for _ in range(300):
                    rep = await c("run", {"max_us": 200_000, "timeout_s": 30})
                    if rep.get("reason") != "breakpoint":
                        continue
                    seen += 1
                    hl = (await c("registers_get"))["hl"]
                    if not 0xA000 <= hl <= 0xC000:
                        bad.append(hl)
                        if len(bad) > 3:
                            break
                print("fill entries seen", seen, "with HL outside the bitmap:", [hex(x) for x in bad])
                await c("breakpoint_remove", {"breakpoint_id": fb})
            if "--disc" in sys.argv:   # who calls the disc fill (todoDrawFilledCircle &E787 / clearCircle &E795)?
                ids = [(await c("breakpoint_add", {"address": a, "kind": "pc"}))["id"] for a in (0xE787, 0xE795)]
                for _ in range(60):
                    rep = await c("run", {"max_us": 200_000, "timeout_s": 30})
                    if rep.get("reason") == "breakpoint":
                        st = await c("stack_get", {})
                        print("disc entry", rep.get("pc"), rep.get("registers"))
                        print("  stack top words:", [w["value"] for w in st["words"][:8]])
                        print("  params circleOffsetY/Xlo/Xhi/radius &20C7:", (await c("memory_read", {"address": 0x20C7, "length": 4}))["hex"])
                        break
                for i in ids:
                    await c("breakpoint_remove", {"breakpoint_id": i})
            if "--text" in sys.argv:   # find who prints: break on printCharAtLocationXY and show the stack
                pcx = (await c("breakpoint_add", {"address": PRINTCHAR, "kind": "pc"}))["id"]
                for _ in range(40):
                    rep = await c("run", {"max_us": 250_000, "timeout_s": 30})
                    if rep.get("reason") == "breakpoint":
                        print("char print at", rep.get("pc"), rep.get("registers"))
                        print(await c("stack_get", {}))
                        break
                await c("breakpoint_remove", {"breakpoint_id": pcx})
            await c("run", {"max_us": 400_000, "timeout_s": 60})
            print("position bytes ix+0..8 after the run:", (await c("memory_read", {"address": ix, "length": 9}))["hex"])
            alive = (await c("memory_read", {"address": ix + 34, "length": 1}))["hex"]
            print("slot flag after 2 s:", alive)
            print(await c("screen_image", {"path": "output/missions_ship.png"}))


asyncio.run(main())

#!/usr/bin/env python3
"""Spawn variance of the 64K build (-DSPAWN_VARIANCE with -DMISSIONS: spawnShip ends with jp mxSpawnVar, src/elite/missions_flight.asm; docs/_ship_spawning.md), in cpcxray.

usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_spawnvar.py [N]
Needs output/firebird_in_flight.sna and any disk in drive A (the built COMMONXX is written into the snapshot as patches over the stock file, like test_ship_packs.py). For the default image, a ship
pack image (3: Mamba stands in for the Sidewinder) and the Constrictor image (C: no routine, the stock start) it calls spawnShip N times (default 60) per type with a free slot (the game does not run, so nothing is used up) and checks:
  hostile types (Sidewinder 16, Krait 17, Python pirate 11, Thargoid 15): x_hi, y_hi 0..63, z_hi 32..63, none in the rear cone, some behind and some in front, the places differ
  a trader (9) and a Viper (8): the stock start (x_hi, y_hi 0..7, z_hi &32, in front)
  every spawn: A = 0 on return, ix+37 = &7E, ix+38 = 0 (the stock values the code in front of the jp sets)
  image C: the hostile types keep the stock corner (x_hi = y_hi = z_hi = &32)
Prints ALL OK at the end; exit code 1 on a failure.
"""
import asyncio
import json
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cheat128  # noqa: E402

TRAP = 0x9F00
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
FLAGS = ["-DENHANCED", "-DTITLESEL", "-DTRAFFIC", "-DMISSIONS", "-DSPAWN_VARIANCE"]
fails = []


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what, flush=True)
    if not ok:
        fails.append(what)


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
                await c("run", {"max_us": 2_000_000, "timeout_s": 60})
                assert (await c("registers_get"))["pc"] == TRAP

            for image in ("0", "3", "C"):
                with tempfile.TemporaryDirectory() as d:
                    syms, raw = cheat128.assemble(ROOT / "src/elite/commonxx.asm", d, "c", FLAGS + ([f"-DFL_{image}"] if image != "0" else []))
                print(f"-- image {image}: {syms['mxFlightEnd'] - syms['mxFlightBase']} bytes", flush=True)
                await c("sna_load", {"path": "output/firebird_in_flight.sna"})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                bp = (await c("breakpoint_add", {"address": syms["handleEntitys"], "kind": "pc"}))["id"]
                rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep
                await c("breakpoint_remove", {"breakpoint_id": bp})
                for lo, hi in patch_ranges(raw):
                    await c("memory_write", {"address": lo, "data": raw[lo - 0x1A40:hi - 0x1A40].hex()})
                await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
                await call(syms["lookforFreeSlot"])
                ix = (await c("registers_get"))["ix"]

                async def spawn(t):
                    ps, okx = [], True
                    for _ in range(N):
                        await call(syms["spawnShip"], a=t, ix=ix)
                        regs = await c("registers_get")
                        b = bytes.fromhex((await c("memory_read", {"address": ix, "length": 40}))["hex"])
                        okx &= (regs["af"] >> 8) == 0 and b[37] == 0x7E and b[38] == 0
                        ps.append(b)
                    return ps, okx

                for t, name in ((16, "Sidewinder"), (17, "Krait"), (11, "Python pirate"), (15, "Thargoid")):
                    ps, okx = await spawn(t)
                    his = [(b[1], b[4], b[7]) for b in ps]
                    if image == "C":
                        check(all(h == (0x32, 0x32, 0x32) for h in his) and okx, f"image C {name}: the stock corner start, A = 0")
                        continue
                    behind = sum(1 for b in ps if b[8] & 0x80)
                    check(all(x < 64 and y < 64 and 32 <= z < 64 for x, y, z in his), f"image {image} {name}: x_hi, y_hi 0..63, z_hi 32..63")
                    check(not any((b[8] & 0x80) and b[1] < b[7] and b[4] < b[7] for b in ps), f"image {image} {name}: none in the rear cone")
                    check(0 < behind < N and len(set(his)) > N // 2, f"image {image} {name}: {behind} of {N} behind, the places differ")
                    check(okx, f"image {image} {name}: A = 0 and ix+37/38 as the stock code sets them")
                for t, name in ((9, "Cobra Mk III (trader)"), (8, "Viper")):
                    ps, okx = await spawn(t)
                    check(all(b[1] < 8 and b[4] < 8 and b[7] == 0x32 and not b[8] & 0x80 for b in ps) and okx, f"image {image} {name}: the stock start, A = 0")
    print("ALL OK" if not fails else f"{len(fails)} FAILED")
    sys.exit(1 if fails else 0)


asyncio.run(main())

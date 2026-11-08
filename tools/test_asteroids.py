#!/usr/bin/env python3
"""Test the flight side of the asteroid mission (-DFL_A image) in cpcxray: asteroids spawn at Ceerdi only while clearing, kills of asteroids count down. (The docked part is tested by tools/test_mission_hook.py.)

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_asteroids.py

Same method as tools/test_mission_flight.py: start from output/firebird_in_flight.sna, let the launch finish, stop at handleEntitys (&5066), write the
freshly assembled COMMONXX patches (-DMISSIONS), set variables, call the routine with a trap return address. The docked module is in LARGEAXX, which comes
from the disk after a call to loadLARGEAXX (&8732).
"""
import asyncio
import json
import re
import subprocess
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
TRAP = 0x9F90
SITES = ((0x72A8, 0x72AB), (0x80CD, 0x80D0), (0x83EF, 0x83F2), (0x518E, 0x5191), (0x7AA2, 0x7AA5), (0x3691, 0x3694), (0x9D9E, 0xA000))
DOCKED_UNUSED = {   # name: (state, killScoreHigh, galaxy, x, y, state after, message, reward)
    "brief":           (0x02, 5, 2, 10, 10, 0x06, True, False),
    "brief_low_rank":  (0x02, 4, 2, 10, 10, 0x02, False, False),
    "brief_galaxy_1":  (0x02, 5, 0, 10, 10, 0x02, False, False),
    "constrictor_open": (0x01, 5, 2, 10, 10, 0x01, False, False),
    "ceerdi":          (0x06, 5, 2, 215, 84, 0x0A, True, False),
    "ceerdi_wrong":    (0x06, 5, 2, 215, 85, 0x06, False, False),
    "birera":          (0x0A, 5, 2, 63, 72, 0x0E, True, True),
    "birera_too_early": (0x06, 5, 2, 63, 72, 0x06, False, False),
    "done":            (0x0E, 6, 2, 63, 72, 0x0E, False, False),
}


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


def build(flag="-DFL_P"):
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", flag, f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
        return out.read_bytes(), syms


async def main():
    new, syms = build("-DFL_A")
    SITES = patch_ranges(new)
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

            async def wr(addr, val):
                await c("memory_write", {"address": addr, "data": "%02X" % val})

            async def rd(addr, n=1):
                return bytes.fromhex((await c("memory_read", {"address": addr, "length": n}))["hex"])

            async def start():
                await c("disk_insert", {"drive": "A", "path": "disk/elite_missions.dsk"})
                await c("sna_load", {"path": "output/firebird_in_flight.sna"})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                bp = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
                rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep
                await c("breakpoint_remove", {"breakpoint_id": bp})
                for lo, hi in SITES:
                    await c("memory_write", {"address": lo, "data": new[lo - 0x1A40:hi - 0x1A40].hex()})
                await c("breakpoint_add", {"address": TRAP, "kind": "pc"})

            async def call(addr, limit=3_000_000, **regs):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr, **regs}})
                return await c("run", {"max_us": limit, "timeout_s": 120})

            ok = True
            AST = 0x38FE

            async def slots():
                kinds = {}
                for i in range(1, 7):
                    b = await rd(0x1A40 + 0x27 * i + 34, 3)
                    if b[0]:
                        bp = b[1] | b[2] << 8
                        kinds[bp] = kinds.get(bp, 0) + 1
                return kinds

            # spawn: (label, state, galaxy, x, y, asteroids expected)
            for label, st, gal, x, y, want in (("clearing at Ceerdi", 0x1E, 2, 215, 84, True), ("wrong place", 0x1E, 2, 215, 85, False), ("wrong galaxy", 0x1E, 1, 215, 84, False),
                                               ("not clearing (plans done)", 0x0E, 2, 215, 84, False), ("cleared", 0x2E, 2, 215, 84, False)):
                await start()
                await wr(0x38FD, st); await wr(syms["currentGalaxy"], gal); await wr(syms["presentSystemX"], x); await wr(syms["presentSystemY"], y)
                before = await slots()
                for _ in range(30):
                    await call(syms["mxSpawnCheck"])
                n = (await slots()).get(syms["shipdatAsteroid"], 0) - before.get(syms["shipdatAsteroid"], 0)
                good = (n >= 1) if want else (n == 0)
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} spawn {label:26s} after 30 checks: {n} new asteroids ({'some' if want else 'none'})")
            # kill hook: (label, state, place ok, blueprint, count before, count after, state after)
            for label, st, x, bpname, cnt, want_cnt, want_st in (("asteroid, 3 left", 0x1E, 215, "shipdatAsteroid", 3, 2, 0x1E), ("last asteroid", 0x1E, 215, "shipdatAsteroid", 1, 0, 0x2E),
                                                                  ("other ship", 0x1E, 215, "shipdatViper", 3, 3, 0x1E), ("asteroid elsewhere", 0x1E, 216, "shipdatAsteroid", 3, 3, 0x1E),
                                                                  ("not clearing", 0x0E, 215, "shipdatAsteroid", 3, 3, 0x0E)):
                await start()
                await wr(0x38FD, st); await wr(AST, cnt); await wr(syms["currentGalaxy"], 2); await wr(syms["presentSystemX"], x); await wr(syms["presentSystemY"], 84)
                regs = await call(syms["mxKillHook"], iy=syms[bpname], de=0)
                c1, s1 = (await rd(AST))[0], (await rd(0x38FD))[0]
                good = c1 == want_cnt and s1 == want_st
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} kill  {label:20s} count {cnt} -> {c1} (want {want_cnt}), state {st:02X} -> {s1:02X} (want {want_st:02X})")
            # live: the real game loop at Ceerdi for a few seconds: its own spawn check calls the hook; no hang, asteroids appear, screenshot for the eye
            await start()
            hb = (await c("breakpoint_add", {"address": syms["mxSpawnCheck"], "kind": "pc"}))["id"]
            await wr(0x38FD, 0x1E); await wr(AST, 20); await wr(syms["currentGalaxy"], 2); await wr(syms["presentSystemX"], 215); await wr(syms["presentSystemY"], 84)
            await c("memory_write", {"address": syms["heNotOnThargonMission"] + 12, "data": "00 00"})   # the test snapshot is next to the station: drop the `jr nz` that skips the spawn when it is near
            await wr(syms["todoLaunchFlag"], 0); await wr(syms["todoLaserVar2"], 2)
            rep = await c("run", {"max_us": 40_000_000, "timeout_s": 200})
            print("     run:", str(rep)[:300], "todoLaserVar2", (await rd(syms["todoLaserVar2"]))[0], "FlagStationNear", (await rd(syms["FlagStationNear"]))[0])
            print("     first live hit of mxSpawnCheck:", rep.get("reason"), rep.get("pc"))
            await c("breakpoint_remove", {"breakpoint_id": hb})
            await wr(syms["todoLaserVar2"], 2)
            await c("run", {"max_us": 6_000_000, "timeout_s": 100})
            n = (await slots()).get(syms["shipdatAsteroid"], 0)
            await c("screen_image", {"path": "output/asteroids_live.png"})
            good = n >= 1
            ok &= good
            print(f"{'ok  ' if good else 'FAIL'} live game loop at Ceerdi (spawn timer forced), 40 s: {n} asteroids in the slots; screenshot work/xray/output/asteroids_live.png")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

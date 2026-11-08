#!/usr/bin/env python3
"""Test the flight side of the stolen police ship (-DFL_S image) in cpcxray: one non-police Viper at Birera in stage 3, its kill makes stage 4, jumps are counted in stage 1. (The docked part is tested by tools/test_mission_hook.py.)

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_stolen_ship.py

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


def build(flag):
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", flag, f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
        return out.read_bytes(), syms


async def main():
    new, syms = build("-DFL_S")
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
            CNT = 0x38FE

            async def vipers():
                out = []
                for i in range(1, 7):
                    ix = 0x1A40 + 0x27 * i
                    b = await rd(ix + 33, 4)     # +33 flags, +34 energy, +35/36 blueprint
                    if b[1] and (b[2] | b[3] << 8) == syms["shipdatViper"]:
                        out.append((ix, b[0], b[1], (await rd(ix + 37))[0]))
                return out

            for label, state, gal, x, y, want in (("hunting at Birera", 0x3E, 2, 63, 72, True), ("wrong place", 0x3E, 2, 63, 73, False), ("wrong galaxy", 0x3E, 1, 63, 72, False),
                                                  ("waiting (stage 1)", 0x1E, 2, 63, 72, False), ("killed (stage 4)", 0x4E, 2, 63, 72, False), ("plans not finished", 0x32, 2, 63, 72, False)):
                await start()
                await wr(0x38FD, state); await wr(syms["currentGalaxy"], gal); await wr(syms["presentSystemX"], x); await wr(syms["presentSystemY"], y)
                for _ in range(60):
                    await call(syms["mxSpawnCheck"])
                v = await vipers()
                good = (len(v) == 1 and (v[0][1] & 0x62) == 0 and v[0][2] == 0xC8 and (v[0][3] & 1) == 1 and (v[0][1] & 0x60) == 0) if want else (len(v) == 0)
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} spawn {label:20s} after 60 checks: {len(v)} Viper(s) {[(hex(f), hex(e)) for _, f, e, _ in v]} ({'exactly one, flags 0 (no offence), energy 0xC8, hostile' if want else 'none'})")
            for label, flags, x, state, want in (("stolen Viper", 0x00, 63, 0x3E, 0x4E), ("police Viper", 0x42, 63, 0x3E, 0x3E), ("stolen Viper elsewhere", 0x00, 64, 0x3E, 0x3E), ("stolen Viper, not hunting", 0x00, 63, 0x1E, 0x1E)):
                await start()
                ix = 0x1A40 + 0x27
                bp = syms["shipdatViper"]
                await c("memory_write", {"address": ix + 33, "data": "%02X C8 %02X %02X" % (flags, bp & 255, bp >> 8)})
                await wr(0x38FD, state); await wr(syms["currentGalaxy"], 2); await wr(syms["presentSystemX"], x); await wr(syms["presentSystemY"], 72)
                await call(syms["mxKillHook"], ix=ix, iy=bp, de=0)
                s1 = (await rd(0x38FD))[0]
                good = s1 == want
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} kill  {label:26s} state {state:02X} -> {s1:02X} (want {want:02X})")
            for label, st, cnt, want_cnt, want_st in (("waiting, 5 left", 0x1E, 5, 4, 0x1E), ("waiting, last jump", 0x1E, 1, 0, 0x2E), ("hunting: jumps do not count", 0x3E, 9, 9, 0x3E),
                                                      ("plans done, no stage", 0x0E, 7, 7, 0x0E)):
                await start()
                await wr(0x38FD, st); await wr(CNT, cnt); await wr(syms["tunnelFlag2"], 0)
                await call(syms["mxArrive"], af=0x0100)
                regs = await c("registers_get")
                c1, s1, tf = (await rd(CNT))[0], (await rd(0x38FD))[0], (await rd(syms["tunnelFlag2"]))[0]
                good = c1 == want_cnt and s1 == want_st and tf == 1 and (regs["af"] >> 8) == 1
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} arrive {label:28s} count {cnt} -> {c1} (want {want_cnt}), state {st:02X} -> {s1:02X} (want {want_st:02X}), tunnelFlag2 {tf}, A {regs['af'] >> 8}")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

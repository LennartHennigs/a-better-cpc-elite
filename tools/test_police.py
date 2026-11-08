#!/usr/bin/env python3
"""Test the flight side of the stolen police ship (-DFL_V image) in cpcxray: one non-police Viper at Birera while hunting, its kill sets the state. (The docked part is tested by tools/test_mission_hook.py.)

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_police.py

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
    new, syms = build("-DFL_V")
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
            ST = 0x38FE

            async def vipers():
                out = []
                for i in range(1, 7):
                    ix = 0x1A40 + 0x27 * i
                    b = await rd(ix + 33, 4)     # +33 flags, +34 energy, +35/36 blueprint
                    if b[1] and (b[2] | b[3] << 8) == syms["shipdatViper"]:
                        out.append((ix, b[0], b[1], (await rd(ix + 37))[0]))
                return out

            for label, state, p, gal, x, y, want in (("hunting at Birera", 0x5E, 1, 2, 63, 72, True), ("wrong place", 0x5E, 1, 2, 63, 73, False), ("wrong galaxy", 0x5E, 1, 1, 63, 72, False),
                                                     ("not offered (p 0)", 0x5E, 0, 2, 63, 72, False), ("killed (p 2)", 0x5E, 2, 2, 63, 72, False), ("asteroids not paid", 0x3E, 1, 2, 63, 72, False)):
                await start()
                await wr(0x38FD, state); await wr(ST, p); await wr(syms["currentGalaxy"], gal); await wr(syms["presentSystemX"], x); await wr(syms["presentSystemY"], y)
                for _ in range(60):
                    await call(syms["mxSpawnCheck"])
                v = await vipers()
                good = (len(v) == 1 and (v[0][1] & 0x62) == 0 and v[0][2] == 0xC8 and (v[0][3] & 1) == 1) if want else (len(v) == 0)
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} spawn {label:20s} after 60 checks: {len(v)} Viper(s) {[(hex(f), hex(e)) for _, f, e, _ in v]} ({'exactly one, flags 0, energy 0xC8, hostile' if want else 'none'})")
            # kill: (label, flags of the dead Viper, place ok, p, p after)
            for label, flags, x, p, want in (("stolen Viper", 0x00, 63, 1, 2), ("police Viper", 0x42, 63, 1, 1), ("stolen Viper elsewhere", 0x00, 64, 1, 1), ("stolen Viper, not hunting", 0x00, 63, 0, 0)):
                await start()
                ix = 0x1A40 + 0x27
                bp = syms["shipdatViper"]
                await c("memory_write", {"address": ix + 33, "data": "%02X C8 %02X %02X" % (flags, bp & 255, bp >> 8)})
                await wr(0x38FD, 0x5E); await wr(ST, p); await wr(syms["currentGalaxy"], 2); await wr(syms["presentSystemX"], x); await wr(syms["presentSystemY"], 72)
                await call(syms["mxKillHook"], ix=ix, iy=bp, de=0)
                p1 = (await rd(ST))[0]
                good = p1 == want
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} kill  {label:26s} state {p} -> {p1} (want {want})")
            # the fugitive rule of the kill code tests (ix+33) & 0x60: the spawned stolen Viper passes it
            await start()
            await wr(0x38FD, 0x5E); await wr(ST, 1); await wr(syms["currentGalaxy"], 2); await wr(syms["presentSystemX"], 63); await wr(syms["presentSystemY"], 72)
            for _ in range(60):
                await call(syms["mxSpawnCheck"])
            v = await vipers()
            good = len(v) == 1 and (v[0][1] & 0x60) == 0
            ok &= good
            print(f"{'ok  ' if good else 'FAIL'} legal status: the stolen Viper's flags {v[0][1]:#04x} & 0x60 = {v[0][1] & 0x60} (0: its kill is no offence)" if v else "FAIL no viper")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

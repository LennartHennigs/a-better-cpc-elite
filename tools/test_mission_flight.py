#!/usr/bin/env python3
"""Test the flight-time mission code in cpcxray: mxSpawnCheck (Constrictor at Orarra) and mxKillHook (kill marks state 3).

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_mission_flight.py

Each scenario starts from output/firebird_in_flight.sna, lets the launch finish, stops at handleEntitys (&5066, a safe point: the fill routines use SP as a
write pointer in the bitmap), writes the freshly assembled COMMONXX patches (call sites and tail), sets variables and calls the routine with a trap return address.
Addresses of mxSpawnCheck and mxKillHook come from the sjasmplus symbol file of the build.
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
TRAP = 0x9F80
SITES = ((0x72A8, 0x72AB), (0x80CD, 0x80D0), (0x83EF, 0x83F2), (0x518E, 0x5191), (0x7AA2, 0x7AA5), (0x9D9E, 0xA000))   # call sites and the tail (see size_report output)
HULL = None


def build():
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
        return out.read_bytes(), syms


# name: (state, galaxy, x, y, what, expectation)
SPAWN = {
    "orarra_stage7": (0x71, 1, 144, 33, True),
    "wrong_system":  (0x71, 1, 144, 34, False),
    "stage6":        (0x61, 1, 144, 33, False),
    "wrong_galaxy":  (0x71, 0, 144, 33, False),
    "not_hunting":   (0x70, 1, 144, 33, False),
}
KILL = {   # name: (state, iy is the Constrictor, state after)
    "kill_hunting":  (0x71, True, 0x73),
    "kill_other":    (0x71, False, 0x71),
    "kill_notbegun": (0x00, True, 0x00),
    "kill_done":     (0x02, True, 0x02),
}


LASER = {   # name: (constrictor?, laser power C, energy before, energy expected after)   A passed in = energy - C, flags from that subtraction
    "pulse_vs_constrictor":    (True, 0x0F, 100, 100),   # no damage
    "beam_vs_constrictor":     (True, 0x0F, 100, 100),
    "military_vs_constrictor": (True, 0x17, 100, 77),    # damaged
    "mining_vs_constrictor":   (True, 0x32, 100, 50),
    "pulse_vs_viper":          (False, 0x0F, 100, 85),   # other ships unchanged
}


async def main():
    new, syms = build()
    hull = syms["shipdatConstrictor"]
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

            async def call(addr, **regs):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr, **regs}})
                rep = await c("run", {"max_us": 3_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint" and rep.get("pc") == "%04X" % TRAP, rep
                return rep

            async def constrictors():
                n = 0
                for i in range(1, 7):
                    ix = 0x1A40 + 0x27 * i
                    b = bytes.fromhex((await c("memory_read", {"address": ix + 34, "length": 3}))["hex"])
                    if b[0] and (b[1] | b[2] << 8) == hull:
                        n += 1
                return n

            ok = True
            for name, (st, gal, x, y, want) in SPAWN.items():
                await start()
                await wr(0x38FD, st); await wr(0x38DC, gal); await wr(0x3910, x); await wr(0x390E, y)
                before = await constrictors()
                await call(syms["mxSpawnCheck"])
                n1 = await constrictors()
                await call(syms["mxSpawnCheck"])          # a second call must not add another one
                n2 = await constrictors()
                good = (before == 0) and (n1 == (1 if want else 0)) and n2 == n1
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} spawn {name:14s} constrictors before {before}, after one call {n1}, after two {n2} (want {int(want)})")
            for name, (st, is_c, want_st) in KILL.items():
                await start()
                await wr(0x38FD, st)
                iy = hull if is_c else syms["shipdatViper"]
                await call(syms["mxKillHook"], iy=iy, de=0)
                st1 = int.from_bytes(bytes.fromhex((await c("memory_read", {"address": 0x38FD, "length": 1}))["hex"]), "little")
                good = st1 == want_st
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} kill  {name:14s} state {st:02X} -> {st1:02X} (want {want_st:02X})")
            for name, (is_c, power, e0, want) in LASER.items():
                await start()
                ix = 0x1A40 + 0x27       # slot 1 (free in this snapshot)
                bp = hull if is_c else syms["shipdatViper"]
                await c("memory_write", {"address": ix + 34, "data": "%02X %02X %02X" % (e0, bp & 255, bp >> 8)})
                a = (e0 - power) & 255
                await call(syms["mxLaserHook"], ix=ix, bc=power, af=(a << 8) | 0x00)   # flags: NZ, NC like a normal hit that does not kill
                e1 = bytes.fromhex((await c("memory_read", {"address": ix + 34, "length": 1}))["hex"])[0]
                af = (await c("registers_get"))["af"]
                z, cy = bool(af & 0x40), bool(af & 0x01)
                good = e1 == want and not z and not cy
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} laser {name:24s} energy {e0} -> {e1} (want {want}), flags Z={int(z)} C={int(cy)} (want 0 0)")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

#!/usr/bin/env python3
"""Test the flight side of the Thargoid plans mission in cpcxray: 22% Thargoid + Thargon spawn, Navy energy unit recharge. (The docked modules are tested by tools/test_mission_hook.py.)

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_plans.py

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
DOCKED = {   # name: (state, killScoreHigh, galaxy, x, y, state after, message, reward)
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


def build():
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
        return out.read_bytes(), syms


async def main():
    new, syms = build()
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
            # flight: 22% Thargoid + Thargon
            for label, st, calls in (("plans aboard", 0x0A, 60), ("not aboard", 0x06, 60)):
                await start()
                await wr(0x38FD, st)
                for _ in range(calls):
                    await call(syms["mxSpawnCheck"])
                kinds = {}
                for i in range(1, 7):
                    ix = 0x1A40 + 0x27 * i
                    b = await rd(ix + 34, 3)
                    if b[0]:
                        bp = b[1] | b[2] << 8
                        kinds[bp] = kinds.get(bp, 0) + 1
                th, tg = kinds.get(syms["shipdatThargoid"], 0), kinds.get(syms["shipdatThargon"], 0)
                good = (th >= 1 and tg >= 1 and th == tg) if st == 0x0A else (th == 0 and tg == 0)
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} flight {label:13s} after {calls} spawn checks: Thargoids {th}, Thargons {tg}")
            # recharge: steps per call
            for unit, want in ((0x00, 1), (0xFF, 2), (0xFE, 3)):
                await start()
                await wr(0x3902, unit)
                bank = syms["shipEnergyBank4"]
                for i in range(4):
                    await wr(bank + i, 0x10)
                await call(syms["RechargeEnergy"])
                got = sum(await rd(bank, 4)) - 4 * 0x10
                good = got == want
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} recharge unit {unit:02X}: {got} step(s) per call (want {want})")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

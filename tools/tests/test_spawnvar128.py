#!/usr/bin/env python3
"""Spawn variance of the 128K build (SPAWN_VARIANCE, src/elite128/spawnmod.asm, docs/_ship_spawning.md): samples spawnShip and checks the rules.

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_spawnvar128.py [N]
Needs output/flight128.sna (tools/tests/test_flight128.py 3 after every build) and disk/elite128.dsk. Method of test_hulls128.py: stop at handleEntitys, take a free slot, call the routines
with a trap return address and read the slot back; the game does not run between the samples, so no slot is used up. N samples per case (default 60). Checks:
  hostile types (Sidewinder 16, Krait 17, Python pirate 11, Thargoid 15): x_hi, y_hi in 0..63, z_hi in 32..63, never in the rear cone, some behind (z negative), some in front
  a trader (Cobra Mk III 9) and a Viper (8): the stock start (x_hi, y_hi in 0..7, z_hi = &32)
  rocks (spawnShip 6 + spawnRock): the heading (the high bytes of nosev) points at the player: dot(nosev, -position) > 0.6 for every sample, the frame is orthonormal (|v| 0.95..1.05, dots < 0.1)
  packs (spawnPackShip with C = 3, 2, 1): the second and third ship within 600 units per axis of the first, the same signs
Exit code 1 on a failure.
"""
import asyncio
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TRAP = 0x9F00
SYM = {m.group(1): int(m.group(2), 16) for m in (re.match(r"(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", l) for l in open(os.environ.get("SYM128", Path(__file__).resolve().parents[2] / "work/elite128/c128.sym"))) if m}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
fails = []


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what, flush=True)
    if not ok:
        fails.append(what)


def pos(b):
    """(x, y, z) as signed numbers in units of 256 from 9 bytes (lo, hi, sign each)"""
    return [((b[3 * k + 1] + b[3 * k] / 256) * (-1 if b[3 * k + 2] & 0x80 else 1)) for k in range(3)]


def sm(h):
    return -(h & 0x7F) / 127 if h & 0x80 else h / 127


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
                rep = await c("run", {"max_us": 2_000_000, "timeout_s": 60})
                assert (await c("registers_get"))["pc"] == TRAP, rep

            async def ship(ix):
                return bytes.fromhex((await c("memory_read", {"address": ix, "length": 40}))["hex"])

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("sna_load", {"path": os.environ.get("SNA", "output/flight128.sna")})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            safe = (await c("breakpoint_add", {"address": SYM["handleEntitys"], "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            await c("breakpoint_remove", {"breakpoint_id": safe})
            await c("sna_save", {"path": "output/spawnvar_banks.sna"})      # the banks bankInit filled: bank 6 holds the fill module (&4000), the spawn module (&4600) and the pack hull records (&6800)
            sna = open("output/spawnvar_banks.sna", "rb").read()
            b6 = lambda addr, n: sna[0x100 + 6 * 0x4000 + addr - 0x4000:][:n]
            root = Path(__file__).resolve().parents[2]
            packs = (root / "work/elite128/fill128_packs.bin").read_bytes()
            check(b6(0x6800, len(packs)) == packs, "bank 6 &6800: the pack hull records (fill128_packs.bin)")
            fill = (root / "work/elite128/fill.bin").read_bytes()
            check(b6(0x4000, 0x500) == fill[:0x500], "bank 6 &4000: the fill module (fill.bin; the last bytes are variables it changes)")
            with tempfile.TemporaryDirectory() as d:
                subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "--nologo", f"--raw={d}/sm.bin", str(root / "src/elite128/spawnmod.asm")], cwd=root / "src/elite128", capture_output=True, check=True)
                mod = Path(f"{d}/sm.bin").read_bytes()
            check(b6(0x4600, len(mod)) == mod, "bank 6 &4600: the spawn module (spawnmod.asm)")
            await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
            await call(SYM["lookforFreeSlot"])
            ix = (await c("registers_get"))["ix"]

            for t, name in ((16, "Sidewinder"), (17, "Krait"), (11, "Python pirate"), (15, "Thargoid")):
                ps = []
                for _ in range(N):
                    await call(SYM["spawnShip"], a=t, ix=ix)
                    ps.append(await ship(ix))
                his = [(b[1], b[4], b[7]) for b in ps]
                behind = sum(1 for b in ps if b[8] & 0x80)
                check(all(x < 64 and y < 64 and 32 <= z < 64 for x, y, z in his), f"{name}: x_hi, y_hi 0..63, z_hi 32..63")
                check(not any((b[8] & 0x80) and b[1] < b[7] and b[4] < b[7] for b in ps), f"{name}: none in the rear cone")
                check(0 < behind < N, f"{name}: {behind} of {N} behind the player")
                check(len({h for h in his}) > N // 2, f"{name}: the places differ")
            for t, name in ((9, "Cobra Mk III (trader)"), (8, "Viper")):
                ps = []
                for _ in range(N // 2):
                    await call(SYM["spawnShip"], a=t, ix=ix)
                    ps.append(await ship(ix))
                check(all(b[1] < 8 and b[4] < 8 and b[7] == 0x32 and not b[8] & 0x80 for b in ps), f"{name}: the stock start")

            bad, mind = [], 1.0
            heads = {}
            for _ in range(N * 2):
                await call(SYM["spawnShip"], a=6, ix=ix)
                await call(SYM["spawnRock"], ix=ix)
                b = await ship(ix)
                p = pos(b[0:9])
                v = [[sm(b[10 + 6 * i + 2 * k]) for k in range(3)] for i in range(3)]      # nosev, roofv, sidev (high bytes of x, y, z)
                n = v[0]
                pl = math.sqrt(sum(q * q for q in p))
                d = sum(-p[k] / pl * n[k] for k in range(3))
                mind = min(mind, d)
                heads[tuple(round(q, 1) for q in n)] = 1
                lens = [math.sqrt(sum(q * q for q in w)) for w in v]
                dots = [abs(sum(v[i][k] * v[j][k] for k in range(3))) for i, j in ((0, 1), (0, 2), (1, 2))]
                if d < 0.6 or any(not 0.95 < ln < 1.05 for ln in lens) or any(dd > 0.1 for dd in dots):
                    bad.append((p, v))
            check(not bad, f"rocks: heading towards the player (worst cosine {mind:.2f}), orthonormal frames ({len(bad)} bad of {N * 2})")
            check(len(heads) >= 8, f"rocks: {len(heads)} different headings")

            far = []
            for _ in range(N // 2):
                got = []
                for k, left in enumerate((3, 2, 1)):      # three neighbouring slots (the game does not run, so what is in them does not matter)
                    await call(SYM["spawnPackShip"], a=16, ix=ix + 0x27 * k, bc=left)
                    got.append(await ship(ix + 0x27 * k))
                lead = pos(got[0][0:9])
                for g in got[1:]:
                    q = pos(g[0:9])
                    if any(abs(q[k] - lead[k]) > 2.5 for k in range(3)) or any((g[3 * k + 2] ^ got[0][3 * k + 2]) & 0x80 for k in range(3)):
                        far.append((lead, q))
            check(not far, f"packs: the followers stay within about 500 units of the leader ({len(far)} of {N} apart)")
    print("ALL OK" if not fails else f"{len(fails)} FAILED")
    sys.exit(1 if fails else 0)


asyncio.run(main())

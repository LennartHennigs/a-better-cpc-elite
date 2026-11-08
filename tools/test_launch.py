#!/usr/bin/env python3
"""Test the launch hook (mxLaunchEntry in the flight tail) in cpcxray: the right flight image must be in the COMMONXX tail after it.

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_launch.py

Method as in tools/test_mission_hook.py: stop at handleEntitys (&5066), write the built COMMONXX patches (default image, -DMISSIONS), call loadLARGEAXX so the stub is in
RAM, then for each scenario set missionState (&38FD), the Trumble count (&3905) and the flight id byte (&9DB6, the image "already loaded"), call mxLaunchEntry with a trap return address and compare
the tail (&9D9E..) with the MFLIGHTx.BIN file on the disk. The stub loads the file with the game's loadFile, then continues with loadIndicator.
"""
import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import dskx  # noqa: E402

TRAP = 0x9F90 + 0x20
BASE = 0x9D9E
# name: (state, id already in RAM, id expected afterwards)
SCENARIOS = {
    "nothing_active":          (0x00, "0", "0"),
    "hunting":                 (0x01, "0", "C"),
    "killed_waiting_reward":   (0x73, "0", "C"),
    "hunting_already_loaded":  (0x11, "C", "C"),
    "constrictor_done":        (0x02, "C", "0"),
    "plans_briefed":           (0x06, "0", "0"),
    "plans_aboard":            (0x0A, "0", "P"),
    "plans_aboard_from_C":     (0x0A, "C", "P"),
    "plans_done":              (0x0E, "P", "0"),
    "asteroids_waiting":       (0x1E, "0", "A"),
    "asteroids_waiting_from_P": (0x1E, "P", "A"),
    "asteroids_ready":         (0x2E, "A", "0"),
    "asteroids_clearing":      (0x3E, "0", "A"),
    "asteroids_cleared":       (0x4E, "A", "0"),
    "asteroids_paid":          (0x5E, "A", "0"),
    "trumbles_aboard":         (0x0E, "0", "T"),
    "trumbles_from_C":         (0x01, "C", "T"),
    "trumbles_gone":           (0x8E, "T", "0"),
}
TRUMBLES = {"trumbles_aboard", "trumbles_from_C"}   # these run with a non-zero count in &3905
FLIGHT_ID = 0x9DB6   # mxFlightId: the id byte after the 8-entry vector table


def patches():
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], check=True, capture_output=True)
        new = out.read_bytes()
        import re
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
    old = (ROOT / "work/bin_stock/COMMONXX.BIN").read_bytes()
    ranges = []
    for i, (a, b) in enumerate(zip(new, old)):
        if a != b:
            if ranges and i - ranges[-1][1] <= 8:
                ranges[-1][1] = i + 1
            else:
                ranges.append([i, i + 1])
    return [(0x1A40 + lo, new[lo:hi]) for lo, hi in ranges], syms


async def main():
    files = dskx.read_files(dskx.load_sectors(ROOT / "work/elite_missions.dsk"))
    images = {}
    for t in "0CPTA":
        raw = files[(0, f"MFLIGHT{t}.BIN")]
        images[t] = raw[128:128 + dskx.amsdos_header(raw)["length"]]   # the file is padded to whole records after the real length
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

            async def call(addr, limit):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr}})
                return await c("run", {"max_us": limit, "timeout_s": 300})

            await c("disk_insert", {"drive": "A", "path": "disk/elite_missions.dsk"})
            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            bp = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            await c("breakpoint_remove", {"breakpoint_id": bp})
            ranges, syms = patches()
            global FLIGHT_ID
            FLIGHT_ID = syms["mxFlightId"]
            for addr, data in ranges:
                await c("memory_write", {"address": addr, "data": data.hex()})
            await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
            rep = await call(0x8732, 20_000_000)            # loadLARGEAXX: the stub appears in the LARGEAXX tail
            assert rep.get("pc") == "%04X" % TRAP, rep
            await c("sna_save", {"path": "output/_launch_after_load.sna"})
            ok = True
            for name, (st, have, want) in SCENARIOS.items():
                await c("sna_load", {"path": "output/_launch_after_load.sna"})
                await c("memory_write", {"address": 0x38FD, "data": "%02X" % st})
                await c("memory_write", {"address": 0x3905, "data": "03 00" if name in TRUMBLES else "00 00"})
                if have != "0":     # pretend the tail holds that image already
                    img = images[have]
                    await c("memory_write", {"address": BASE, "data": img.hex()})
                rep = await call(syms["mxLaunchEntry"], 80_000_000)
                ms = rep.get("emulated_us", 0) / 1000
                back = rep.get("pc") == "%04X" % TRAP
                ident = chr(int((await c("memory_read", {"address": FLIGHT_ID, "length": 1}))["hex"], 16))
                img = images[want]
                ram = bytes.fromhex((await c("memory_read", {"address": BASE, "length": len(img)}))["hex"])
                good = back and ident == want and ram == img
                if ram != img:
                    d = [i for i in range(min(len(ram), len(img))) if ram[i] != img[i]]
                    print('   differing offsets', d[:12], 'ram', ram[d[0]:d[0] + 6].hex() if d else '', 'file', img[d[0]:d[0] + 6].hex() if d else '', 'len', len(ram), len(img))
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} launch {name:24s} state {st:02X}: image {have} -> {ident} (want {want}), bytes {'match' if ram == img else 'DIFFER'} the disk file, returned={back} [{ms:.0f} ms]")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

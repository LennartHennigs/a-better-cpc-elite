#!/usr/bin/env python3
"""Test the launch hook (mxLaunchEntry in the flight tail) in cpcxray: the right flight image must be in the COMMONXX tail after it.

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_launch.py

Method as in tools/tests/test_mission_hook.py: stop at handleEntitys (&5066), write the built COMMONXX patches (default image, -DENHANCED -DTITLESEL -DTRAFFIC -DMISSIONS -DSPAWN_VARIANCE as on the disk), call loadLARGEAXX so the stub is in
RAM, then for each scenario set missionState (&38FD), the Trumble count (&3905) and the flight id byte (mxFlightId, the image "already loaded"), call mxLaunchEntry with a trap return address and compare
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

ROOT = Path(__file__).resolve().parent.parent.parent
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
    "stolen_waiting":       (0x1E, "0", "S"),
    "stolen_waiting_from_P": (0x1E, "P", "S"),
    "stolen_ready":         (0x2E, "S", "0"),
    "stolen_clearing":      (0x3E, "0", "S"),
    "stolen_cleared":       (0x4E, "S", "0"),
    "stolen_paid":          (0x5E, "S", "0"),
    "trumbles_aboard":         (0x0E, "0", "T"),
    "trumbles_from_C":         (0x01, "C", "T"),
    "trumbles_gone":           (0x8E, "T", "0"),
    "rocks_hunting":          (0x5E, "0", "R"),
    "rocks_hunting_from_S":   (0x5E, "S", "R"),
    "rocks_killed":           (0x5E, "R", "0"),
    "rocks_paid":             (0x5E, "R", "0"),
    "pack_picked":            (0x00, "0", "3"),     # no mission: the pack is (jumpCounter + presentSystemSeed) & 7, see PACKSEL
    "pack_already_loaded":    (0x00, "3", "3"),
    "pack_none_picked":       (0x00, "5", "0"),
    "pack_after_mission":     (0x02, "C", "7"),
    "mission_beats_pack":     (0x01, "0", "C"),
    "trumbles_beat_pack":     (0x0E, "0", "T"),
}
PACKSEL = {"pack_picked": (2, 1), "pack_already_loaded": (1, 2), "pack_none_picked": (8, 0), "pack_after_mission": (4, 3), "mission_beats_pack": (1, 0), "trumbles_beat_pack": (6, 6)}   # (jumpCounter low byte, presentSystemSeed); default (0, 0) = no pack
POLICE = {"rocks_hunting": 1, "rocks_hunting_from_S": 1, "rocks_killed": 2, "rocks_paid": 3}   # &38FE (stolen police ship state, bits 0-1)
TRUMBLES = {"trumbles_aboard", "trumbles_from_C", "trumbles_beat_pack"}   # these run with a non-zero count in &3905
FLIGHT_ID = 0x9DB9   # mxFlightId: the id byte after the 9-entry vector table (main() reads the real address from the symbols)


def patches():
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DENHANCED", "-DTITLESEL", "-DTRAFFIC", "-DMISSIONS", "-DSPAWN_VARIANCE", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], check=True, capture_output=True)   # the flags build_dsk.py uses: -DENHANCED adds the kill count to the shared head, so the default image differs without it
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
    for t in "0CPTSR1234567":
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
                await c("memory_write", {"address": 0x38FE, "data": "%02X" % POLICE.get(name, 0)})
                await c("memory_write", {"address": 0x3905, "data": "03 00" if name in TRUMBLES else "00 00"})
                jc, seed = PACKSEL.get(name, (0, 0))
                await c("memory_write", {"address": syms["jumpCounter"], "data": "%02X 00" % jc})
                await c("memory_write", {"address": syms["presentSystemSeed"], "data": "%02X" % seed})
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

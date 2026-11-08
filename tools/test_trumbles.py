#!/usr/bin/env python3
"""Test the Trumbles flight image (-DFL_T) in cpcxray: breeding on arrival, slow breeding, heat death, inventory line.

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_trumbles.py

As tools/test_mission_flight.py: start from output/firebird_in_flight.sna, stop at handleEntitys (&5066), write the patches of a COMMONXX built with -DMISSIONS -DFL_T
(call sites and tail), set variables, call the vector with a trap return address. The Trumble count is the word at &3905.
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
TRAP = 0x9FF0
COUNT, FOOD, NARC, FREE, TUNNEL2, TEMP, STORED = 0x3905, 0x38E2, 0x38E8, 0x38F3, 0x38C2, 0x1C0D, None


def build():
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", "-DFL_T", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], check=True, capture_output=True)
        syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
        return out.read_bytes(), syms


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
    new, syms = build()
    sites = patch_ranges(new)
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

            async def wr(addr, *vals):
                await c("memory_write", {"address": addr, "data": " ".join("%02X" % (v & 255) for v in vals)})

            async def rd(addr, n=1):
                return bytes.fromhex((await c("memory_read", {"address": addr, "length": n}))["hex"])

            async def word(addr):
                b = await rd(addr, 2)
                return b[0] | b[1] << 8

            async def start():
                await c("disk_insert", {"drive": "A", "path": "disk/elite_missions.dsk"})
                await c("sna_load", {"path": "output/firebird_in_flight.sna"})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                bp = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
                rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep
                await c("breakpoint_remove", {"breakpoint_id": bp})
                for lo, hi in sites:
                    await c("memory_write", {"address": lo, "data": new[lo - 0x1A40:hi - 0x1A40].hex()})
                await c("breakpoint_add", {"address": TRAP, "kind": "pc"})

            async def call(addr, **regs):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr, **regs}})
                rep = await c("run", {"max_us": 5_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint" and rep.get("pc") == "%04X" % TRAP, rep
                return await c("registers_get")

            ok = True

            def report(good, text):
                nonlocal ok
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} {text}")

            # arrival with Trumbles: 2 * ((3 + 0..15) OR 4) = 8..44, food and narcotics eaten, tonnes returned, A kept
            await start()
            await wr(COUNT, 3, 0); await wr(FOOD, 5); await wr(NARC, 2); await wr(FREE, 10); await wr(TUNNEL2, 0)
            await call(syms["mxArrive"], af=0x0100)
            n, food, narc, free, tf = await word(COUNT), (await rd(FOOD))[0], (await rd(NARC))[0], (await rd(FREE))[0], (await rd(TUNNEL2))[0]
            report(8 <= n <= 44 and food == 0 and narc == 0 and free == 17 and tf == 1, f"arrival, 3 Trumbles: count {n} (8-44), food {food}, narcotics {narc}, free hold {free} (17), tunnelFlag2 {tf} (1)")
            # arrival without Trumbles: nothing changes
            await start()
            await wr(COUNT, 0, 0); await wr(FOOD, 5); await wr(NARC, 2); await wr(FREE, 10)
            await call(syms["mxArrive"], af=0x0100)
            n, food, free = await word(COUNT), (await rd(FOOD))[0], (await rd(FREE))[0]
            report(n == 0 and food == 5 and free == 10, f"arrival, no Trumbles: count {n}, food {food} (5), free hold {free} (10)")
            # cap at &7FFF
            await start()
            await wr(COUNT, 0x00, 0x50)
            await call(syms["mxArrive"], af=0x0100)
            n = await word(COUNT)
            report(n == 0x7FFF, f"arrival, 20480 Trumbles: count {n:#x} (0x7fff)")
            # cap again: a count at the cap and just below it must stay at 0x7FFF, not wrap
            for cnt in (0x7FFF, 0x7FF0, 0x4000, 0x3FFF):
                await start()
                await wr(COUNT, cnt & 255, cnt >> 8)
                await call(syms["mxArrive"], af=0x0100)
                n = await word(COUNT)
                # new count = 2 * ((count + random 0..15) OR 4); a sum of 0x4000 or more is held at 0x7FFF
                allowed = {0x7FFF if cnt + r >= 0x4000 else 2 * ((cnt + r) | 4) for r in range(16)}
                want_cap = cnt >= 0x4000
                good = n in allowed and (n == 0x7FFF or not want_cap)
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} arrival, {cnt:#06x} Trumbles: count {n:#06x} (one of {sorted(allowed)[:3]}... : {'capped at 0x7fff' if want_cap else 'doubled, no wrap'})")
            # sun: halves at cabin temperature 240, A kept, HL = CockpitTemp
            for temp, want in ((240, 50), (239, 100)):
                await start()
                await wr(COUNT, 100, 0); await wr(TEMP, temp)
                regs = await call(syms["mxSun"], af=0x5500)
                n = await word(COUNT)
                report(n == want and regs["hl"] == TEMP and (regs["af"] >> 8) == 0x55, f"sun at temperature {temp}: count {n} ({want}), HL {regs['hl']:#x} ({TEMP:#x}), A {regs['af'] >> 8:#x} (0x55)")
            # slow breeding: only with 256 or more, about 14% of the checks
            for start_count, expect_growth in ((300, True), (100, False)):
                await start()
                await wr(COUNT, start_count & 255, start_count >> 8)
                for _ in range(100):
                    await call(syms["mxSpawnCheck"])
                n = await word(COUNT)
                report((start_count < n <= start_count + 100) if expect_growth else n == start_count, f"100 spawn checks from {start_count} Trumbles: count {n} ({'grows by a few' if expect_growth else 'unchanged'})")
            # squeak: sound bit 5 of sfxFlags2Bitmap, chance high byte / 64 per check (never below 256 Trumbles)
            for start_count, expect_sound in ((2560, True), (100, False)):
                await start()
                await wr(COUNT, start_count & 255, start_count >> 8)
                await wr(syms["sfxFlags2Bitmap"], 0)
                for _ in range(100):
                    await call(syms["mxSpawnCheck"])
                f = (await rd(syms["sfxFlags2Bitmap"]))[0]
                report(bool(f & 0x20) == expect_sound and (f & ~0x20) == 0, f"100 spawn checks from {start_count} Trumbles: sfxFlags2Bitmap {f:#04x} ({'squeak bit set' if expect_sound else 'silent'}, nothing else touched)")
            # inventory line: screenshot of the real Inventory screen with 42 Trumbles
            await start()
            await wr(COUNT, 42, 0); await wr(FOOD, 3); await wr(0x1C23, 0)
            await call(syms["Inventory"])
            await c("screen_image", {"path": "output/trumbles_inventory.png"})
            print("     screenshot: work/xray/output/trumbles_inventory.png (check the Trumbles line by eye)")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

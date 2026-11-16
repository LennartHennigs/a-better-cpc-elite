#!/usr/bin/env python3
"""Test the Trumble sprites (mxFlightDraw in the -DFL_T image) in cpcxray.

Build first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_trumble_sprites.py

As tools/tests/test_trumbles.py (stop at handleEntitys, write the patches of a COMMONXX built with -DMISSIONS -DFL_T, call the vector with a trap return address). mxFlightDraw draws into
the off-screen bitmap at &A000 and ends with `jp transferBuffertoScreen`, so after the call the sprites are also on the screen. Checks:
 - blit: with the bitmap cleared and the Trumble at x 10, y 20, the shape bytes there equal the right-facing shape; the second Trumble (odd) uses the mirrored one;
 - how many are drawn for counts 0, 1, 3, 11 and 300 (0, 1, 3, 6, 6): each Trumble's rectangle is non-zero, an undrawn one's stays zero;
 - 300 draw calls: every position stays inside x 3-57, y 2-114, and something moved.
Screenshots: output/trumble_sprites_*.png.
"""
import asyncio
import json
import re
import subprocess
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
TRAP = 0x9FF4 - 4
COUNT = 0x3905
BITMAP = 0xA000


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


def shape():
    """the sprite bytes and its number of rows, from the generated source"""
    rows = [bytes(int(x, 16) for x in re.findall(r"0x([0-9A-F]{2})", l)) for l in (ROOT / "src/elite/missions_trumble_data.asm").read_text().splitlines() if l.strip().startswith("db")]
    return b"".join(rows), len(rows), len(rows[0])


async def main():
    new, syms = build()
    sites = patch_ranges(new)
    shape_bytes, nrows, ncols = shape()
    state, tick = syms["mxTrState"], syms["mxTrTick"]
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

            async def wr(addr, data):
                await c("memory_write", {"address": addr, "data": data.hex() if isinstance(data, (bytes, bytearray)) else "%02X" % data})

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
                for lo, hi in sites:
                    await c("memory_write", {"address": lo, "data": new[lo - 0x1A40:hi - 0x1A40].hex()})
                await c("breakpoint_add", {"address": TRAP, "kind": "pc"})

            async def call(addr):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr}})
                rep = await c("run", {"max_us": 8_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint" and rep.get("pc") == "%04X" % TRAP, rep

            async def clear_bitmap():
                await wr(BITMAP, bytes(0x2000))

            async def rect(x, y):
                out = b""
                for row in range(nrows):
                    out += await rd(BITMAP + (y + row) * 64 + x, ncols)
                return out

            ok = True

            def report(good, text):
                nonlocal ok
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} {text}")

            # blit
            await start()
            await clear_bitmap()
            await wr(COUNT, bytes([2, 0]))
            await wr(tick, 6)                       # the Trumble moved this call is number 6 (not shown), so nothing moves
            await wr(state, bytes([10, 20, 0, 0, 30, 40, 0, 0]))
            await call(syms["mxFlightDraw"])
            got0, got1 = await rect(10, 20), await rect(30, 40)
            report(got0 == shape_bytes and got1 == shape_bytes, f"two Trumbles at (10,20) and (30,40): each {nrows} x {ncols} bytes equal the shape")
            await c("screen_image", {"path": "output/trumble_sprites_two.png"})
            # regression: a call that moves a Trumble must not change how many are drawn (mxMoveSprite once clobbered C, the count, and the draw loop ran off the state array)
            await start()
            await clear_bitmap()
            await wr(COUNT, bytes([2, 0]))
            await wr(tick, 0)                       # Trumble 0 moves in this call (velocity 0, so it stays put)
            await wr(state, bytes([10, 20, 0, 0, 30, 40, 0, 0]))
            await call(syms["mxFlightDraw"])
            bm = b"".join([await rd(BITMAP + k * 0x400, 0x400) for k in range(8)])
            inside = set()
            for x, y in ((10, 20), (30, 40)):
                for row in range(nrows):
                    for col in range(ncols):
                        inside.add((y + row) * 64 + x + col)
            frame = lambda i: i // 64 in (0, 127) or i % 64 in (2, 61)      # the viewport frame that transferBuffertoScreen draws into the bitmap
            stray = [i for i, v in enumerate(bm) if v and i not in inside and not frame(i)]
            report(not stray, f"a call that moves a Trumble: {len(stray)} stray bitmap bytes outside the two sprites and the frame (want 0)")
            # how many are drawn
            for count, want in ((0, 0), (1, 1), (3, 3), (11, 6), (300, 6)):
                await start()
                await clear_bitmap()
                await wr(COUNT, bytes([count & 255, count >> 8]))
                await wr(tick, 7)
                await wr(state, bytes([10, 10, 0, 0, 30, 20, 0, 0, 45, 40, 0, 0, 15, 60, 0, 0, 35, 80, 0, 0, 50, 100, 0, 0]))
                await call(syms["mxFlightDraw"])
                pos = [(10, 10), (30, 20), (45, 40), (15, 60), (35, 80), (50, 100)]
                drawn = 0
                for x, y in pos:
                    if any(await rect(x, y)):
                        drawn += 1
                report(drawn == want, f"count {count}: {drawn} Trumbles drawn (want {want})")
                if count == 11:
                    await c("screen_image", {"path": "output/trumble_sprites_six.png"})
            # movement stays inside the frame
            await start()
            await wr(COUNT, bytes([11, 0]))
            for _ in range(300):
                await call(syms["mxFlightDraw"])
            st = await rd(state, 24)
            xs, ys = st[0::4], st[1::4]
            inside = all(3 <= x <= 57 for x in xs) and all(2 <= y <= 114 for y in ys)      # 12 x 12 sprite: x up to 64 - 3 - 3 + 1, y up to 128 - 12 - 2
            moved = st != bytes([10, 10, 0, 0, 30, 20, 0, 0, 45, 40, 0, 0, 15, 60, 0, 0, 35, 80, 0, 0, 50, 100, 0, 0])
            report(inside and moved, f"300 draw calls: x {list(xs)} y {list(ys)} inside the frame, moved: {moved}")
            await c("screen_image", {"path": "output/trumble_sprites_moved.png"})
            # live: the real flight loop calls the hook every frame (the game clears the bitmap each time), no smear expected
            await start()
            await wr(COUNT, bytes([11, 0]))
            await c("run", {"max_us": 12_000_000, "timeout_s": 120})
            await c("screen_image", {"path": "output/trumble_sprites_live.png"})
            print("     live run screenshot: work/xray/output/trumble_sprites_live.png (check by eye)")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

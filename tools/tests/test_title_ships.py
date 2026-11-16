#!/usr/bin/env python3
"""Test the title-screen ship selection (-DTITLESEL, hook code in the MUSIQUEX tail at &6E21) in cpcxray.

Build first:  python3 -I tools/build_dsk.py ; cp work/elite_rebuilt.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_title_ships.py [de|fr]
With `de` the German build is tested: python3 -I tools/build_dsk.py --de ; cp work/elite_de_rebuilt.dsk work/xray/disk/ ; it is booted from the disk (RUN"ELITE),
because the entry snapshot holds the English code.
With `fr` likewise: python3 -I tools/build_dsk.py --fr ; cp work/elite_fr_rebuilt.dsk work/xray/disk/ ; booted with RUN"EL.

Boots the entry snapshot, lets the first title screen come up, then taps the cursor keys and checks that the ship index (splash2Shipnr, &1DA8, bits 0-2)
and the blueprint pointer of the demo ship (&1B51 + 35) change as expected, that a held key steps only once, and that the press-space screen still follows.
"""
import asyncio
import json
import sys
import subprocess
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
IDX, SHIP = 0x1DA8, 0x1B51 + 35
COBRA_AT_START = 2


def patches():
    """Byte ranges where the -DTITLESEL COMMONXX differs from the stock one (the entry snapshot holds the stock code; only MUSIQUEX comes from the disk)."""
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "c.bin"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DTITLESEL", f"--raw={out}", str(ROOT / "src/elite/commonxx.asm")], check=True, capture_output=True)
        new = out.read_bytes()
    old = (ROOT / "work/bin_stock/COMMONXX.BIN").read_bytes()
    ranges = []
    for i, (a, b) in enumerate(zip(new, old)):
        if a != b:
            if ranges and i - ranges[-1][1] <= 8:
                ranges[-1][1] = i + 1
            else:
                ranges.append([i, i + 1])
    return [(0x1A40 + lo, new[lo:hi]) for lo, hi in ranges]


async def main():
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

            async def rd(a, n=1):
                return bytes.fromhex((await c("memory_read", {"address": a, "length": n}))["hex"])

            async def state():
                i = (await rd(IDX))[0]
                p = await rd(SHIP, 2)
                return i, p[0] | p[1] << 8

            async def tap(key, secs=0.3):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 60})
                await c("key_release", {"key": key})
                await c("run", {"max_us": 400_000, "timeout_s": 60})

            if "de" in sys.argv[1:] or "fr" in sys.argv[1:]:
                fr = "fr" in sys.argv[1:]
                await c("disk_insert", {"drive": "A", "path": "disk/elite_fr_rebuilt.dsk" if fr else "disk/elite_de_rebuilt.dsk"})
                await c("run", {"max_us": 3_000_000, "timeout_s": 60})
                await c("type_text", {"text": 'run"el\n' if fr else 'run"elite\n', "wait": False})
                bp = (await c("breakpoint_add", {"address": 0x1CD9, "kind": "pc"}))["id"]   # the first title loop
                for _ in range(8):
                    if (await c("run", {"max_us": 10_000_000, "timeout_s": 120})).get("reason") == "breakpoint":
                        break
                await c("breakpoint_remove", {"breakpoint_id": bp})
                await c("run", {"max_us": 1_000_000, "timeout_s": 60})
            else:
                await c("disk_insert", {"drive": "A", "path": "disk/elite_rebuilt.dsk"})
                await c("sna_load", {"path": "output/firebird_at_entry.sna"})
                for addr, data in patches():
                    await c("memory_write", {"address": addr, "data": data.hex()})
                await c("run", {"max_us": 8_000_000, "timeout_s": 120})
            ok = True
            seen = {}

            def check(name, cond, info):
                nonlocal ok
                ok &= bool(cond)
                print(f"{'ok  ' if cond else 'FAIL'} {name}: {info}")

            ia, pa = await state()
            check("start on the Cobra Mk III", ia & 7 == COBRA_AT_START, f"index {ia:02X}, blueprint &{pa:04X}")
            await tap("cursor_right")
            ib, pb = await state()
            check("the first screen ignores the arrows", ib == ia and pb == pa, f"index {ib:02X}, blueprint &{pb:04X}")
            await tap("n", 1.4)       # to the press-space screen, which opens on the Cobra Mk III
            await c("run", {"max_us": 3_000_000, "timeout_s": 60})
            i0, p0 = await state()
            seen[i0] = p0
            await c("screen_image", {"path": "output/title_%s.png" % ("fr" if "fr" in sys.argv[1:] else "de" if "de" in sys.argv[1:] else "en")})   # look at it: the ship name replaces the ELITE title
            check("press-space screen opens on the Cobra Mk III", (i0 & 7) == COBRA_AT_START, f"{ia & 7} -> {i0 & 7}, blueprint &{p0:04X}")
            await tap("cursor_right")
            i1, p1 = await state()
            check("right steps +1", (i1 & 7) == (i0 + 1) & 7 and p1 != p0, f"index {i1:02X}, blueprint &{p1:04X}")
            await c("key_press", {"key": "cursor_right"})
            await c("run", {"max_us": 2_000_000, "timeout_s": 60})
            await c("key_release", {"key": "cursor_right"})
            i2, p2 = await state()
            check("held key steps once", (i2 & 7) == (i1 + 1) & 7, f"index {i2:02X}")
            await c("run", {"max_us": 400_000, "timeout_s": 60})
            ships = {}
            for k in range(8):
                await tap("cursor_left")
                i, p = await state()
                ships[i & 7] = p
            check("eight left taps visit eight different hulls", len(set(ships.values())) == 8, {k: f"{v:04X}" for k, v in sorted(ships.items())})
            await c("memory_write", {"address": IDX, "data": "00"})
            await tap("cursor_left")
            iw, _ = await state()
            check("one left tap at index 0 lands exactly on 7", iw == 7, f"index {iw:02X}")
            await c("key_press", {"key": "cursor_right"})
            await c("run", {"max_us": 2_000_000, "timeout_s": 60})
            await c("key_release", {"key": "cursor_right"})
            await c("run", {"max_us": 400_000, "timeout_s": 60})
            iw2, _ = await state()
            check("held right at index 7 wraps to 0 once", iw2 == 0, f"index {iw2:02X}")
            i3, _ = await state()
            check("bit 7 clear when no key is down", i3 & 0x80 == 0, f"index {i3:02X}")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

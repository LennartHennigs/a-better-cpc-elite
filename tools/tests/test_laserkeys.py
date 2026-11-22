#!/usr/bin/env python3
"""Test the laser position keys of the equipment menu (F, B, L, R instead of 0-3; src/elite/largeaxx.asm, eqLaserSlot) in cpcxray, 64K and 128K.

Build first: 64K: python3 -I tools/build_dsk.py --missions and cp build/elite_missions.dsk work/xray/disk/;
             128K: python3 -I tools/build_dsk128.py, cp build/elite128.dsk work/xray/disk/ and make output/docked128.sna with snap_docked128.py (run_all.py --emu128 does all of it).
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I /ABSOLUTE/PATH/tools/tests/test_laserkeys.py [128|64] [disk/NAME.dsk]

Starts docked with a new commander (128K: output/docked128.sna; 64K: boots the disk, N, Space), gives 16,000 Cr and no lasers, opens the equipment menu (key 4), buys item 5 (pulse laser)
and checks the position screen: it reads "F Front", "B Back", "L Left", "R Right"; each of F, B, L, R puts the laser in its own slot of laserTypes (&38F4-&38F7: front, rear, left, right)
and the price stays taken; another key (digits included) leaves the menu with no laser and the price back. Then it launches and checks that view key 2 reads "Back View".
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BUILD = sys.argv[1] if len(sys.argv) > 1 else "128"
DISK = sys.argv[2] if len(sys.argv) > 2 else ("disk/elite128.dsk" if BUILD == "128" else "disk/elite_missions.dsk")
LASERS, CASH = 0x38F4, 0x38DD
START_CASH = bytes.fromhex("10000000")      # 16,000 Cr
CASES = [(k, v) for k, v in zip("fblr", range(4))] + [(k, None) for k in "0x2"]      # key, view it must fill (None: leaves and refunds)


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

            async def tap(key, secs=1.3):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 60})
                await c("key_release", {"key": key})
                await c("run", {"max_us": 800_000, "timeout_s": 60})

            async def rd():
                """cash (4 bytes at CASH) and laserTypes (4 bytes at LASERS) in one read"""
                blk = bytes.fromhex((await c("memory_read", {"address": CASH, "length": LASERS + 4 - CASH}))["hex"])
                return blk[:4], blk[LASERS - CASH:]

            await c("disk_insert", {"drive": "A", "path": DISK})
            if BUILD == "128":
                await c("sna_load", {"path": "output/docked128.sna"})
            else:
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                await c("type_text", {"text": 'RUN"ELITE\n', "wait": False})
                await c("run", {"max_us": 36_000_000, "timeout_s": 120})
                await tap("n", 1.4)
                await c("run", {"max_us": 8_000_000, "timeout_s": 120})
                await tap("space", 1.4)
                await c("run", {"max_us": 12_000_000, "timeout_s": 120})
            await c("memory_write", {"address": LASERS, "data": "00 00 00 00"})
            await c("memory_write", {"address": CASH, "data": START_CASH.hex(" ")})
            await c("sna_save", {"path": f"output/laserkeys{BUILD}_dock.sna"})
            await tap("4", 0.3)                        # equipment menu (a key held longer is read again as the item number)
            await tap("5", 0.12)
            await c("type_text", {"text": "\r", "wait": True, "timeout_s": 60})      # the item prompt takes digits and Return
            await c("run", {"max_us": 1_000_000, "timeout_s": 60})
            txt = "\n".join((await c("screen_text"))["lines"])
            print(txt)
            ok = True
            for want in ("F Front", "B Back", "L Left", "R Right"):      # exact case: the first letter must be a capital too
                print(f"  screen shows {want!r}: {want in txt}")
                ok &= want in txt
            ok &= "0 Front" not in txt and "Rear" not in txt
            await c("screen_image", {"path": f"output/laserkeys{BUILD}_screen.png"})
            snap = f"output/laserkeys{BUILD}_pos.sna"
            await c("sna_save", {"path": snap})
            cash0 = (await rd())[0]                    # after the price of the item was taken
            ok &= cash0 != START_CASH
            for key, view in CASES:
                await c("sna_load", {"path": snap})
                await tap(key, 0.12)
                cash, lasers = await rd()
                print(f"  key {key.upper()}: lasers {lasers.hex()} cash {cash.hex()}")
                want_lasers = bytes(1 if i == view else 0 for i in range(4))
                ok &= lasers == want_lasers and cash == (cash0 if view is not None else START_CASH)
            await c("sna_load", {"path": f"output/laserkeys{BUILD}_dock.sna"})      # the rear view of the cockpit shares the string token: it must read "Back View" too
            await tap("1", 0.3)                        # launch
            await c("run", {"max_us": 30_000_000, "timeout_s": 200})
            await tap("2", 0.3)
            await c("run", {"max_us": 2_500_000, "timeout_s": 60})      # a flight frame takes long: read the title only after the redraw
            view = [l for l in (await c("screen_text"))["lines"] if "View" in l]
            print("  flight view 2:", view)
            ok &= any("Back View" in l for l in view)
            print("ALL OK" if ok else "FAIL")
            return ok


sys.exit(0 if asyncio.run(main()) else 1)

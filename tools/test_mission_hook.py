#!/usr/bin/env python3
"""Test the docked mission code in cpcxray (Constrictor offer, hints, reward).

Build first:  python3 -I tools/build_dsk.py --missions   and copy work/elite_missions.dsk to work/xray/disk/.
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_mission_hook.py

From output/firebird_in_flight.sna the script calls loadLARGEAXX (&8732) so the rebuilt LARGEAXX tail is in RAM, then for each scenario sets
variables with memory_write (missionState &38FD, killScoreHigh &38D9, galaxy &38DC, system x/y &3910/&390E), clears todoUnknownStatusFlags
(&1C23, a real docking does), calls missionsDockedEntry (&1714) with a trap return address at &9F00, takes a screenshot
(output/missions_<name>.png), presses a key and reports missionState and the credits (&38DD thousands word) after the call.
chkMissions has a single call site, the docking sequence, so a plain new-commander start never reaches the hook.
"""
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TRAP = 0x9F00
# name: (state, killScoreHigh, galaxy, x, y, expected state after, expected credit thousands added, expect a message)
SCENARIOS = {
    "offer_g1":   (0x00, 1, 0, 10, 10, 0x01, 0, True),     # 256 kill points, galaxy 1: briefing, hunting, stage 0
    "offer_low":  (0x00, 0, 0, 10, 10, 0x00, 0, False),    # no kill points: nothing
    "offer_g2":   (0x00, 1, 1, 10, 10, 0x21, 0, True),     # galaxy 2: stage 2
    "hint0":      (0x01, 1, 0, 149, 101, 0x11, 0, True),   # at Reesdice in stage 0
    "hint_wrong": (0x01, 1, 0, 150, 101, 0x01, 0, False),  # elsewhere: nothing
    "hint6":      (0x61, 1, 1, 148, 68, 0x71, 0, True),    # Usleri, last hint, stage becomes 7
    "reward":     (0x73, 1, 1, 10, 10, 0x02, 5, True),     # killed: 5,000 Cr, finished, stage bits cleared
    "done":       (0x72, 1, 1, 148, 68, 0x72, 0, False),   # finished: nothing
}


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

            async def wr(addr, val):
                await c("memory_write", {"address": addr, "data": "%02X" % val})

            async def rd(addr, n=1):
                return bytes.fromhex((await c("memory_read", {"address": addr, "length": n}))["hex"])

            async def call(addr, limit):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr}})
                return await c("run", {"max_us": limit, "timeout_s": 120})

            await c("disk_insert", {"drive": "A", "path": "disk/elite_missions.dsk"})
            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
            r1 = await call(0x8732, 20_000_000)
            assert r1.get("reason") == "breakpoint", r1
            snap = "output/_after_load.sna"
            await c("sna_save", {"path": snap})
            ok = True
            for name, (st, ksh, gal, x, y, want_st, want_cr, msg) in SCENARIOS.items():
                await c("sna_load", {"path": snap})
                await wr(0x38FD, st); await wr(0x38D9, ksh); await wr(0x38DC, gal); await wr(0x3910, x); await wr(0x390E, y)
                await wr(0x3926, 0); await wr(0x1C23, 0)
                cr0 = int.from_bytes(await rd(0x38DD, 2), "little")
                rep = await call(0x1714, 3_000_000)
                shown = rep.get("reason") == "time_limit"          # waiting for a key = a message box is up
                if shown:
                    await c("screen_image", {"path": f"output/missions_{name}.png"})
                    await c("key_press", {"key": "space"})
                    rep = await c("run", {"max_us": 4_000_000, "timeout_s": 60})
                    await c("key_release", {"key": "space"})
                back = rep.get("reason") == "breakpoint" and rep.get("pc") == "9F00"
                st1 = (await rd(0x38FD))[0]
                cr1 = int.from_bytes(await rd(0x38DD, 2), "little")
                good = shown == msg and back and st1 == want_st and cr1 - cr0 == want_cr
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} {name:11s} message={shown} returned={back} state {st:02X}->{st1:02X} (want {want_st:02X}) credits +{cr1 - cr0} (want {want_cr})")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

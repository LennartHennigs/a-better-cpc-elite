#!/usr/bin/env python3
"""Test the docked mission stub and both overlays (Constrictor MISSIONC.BIN, Thargoid plans MISSIONP.BIN) in cpcxray.

Build first:  python3 -I tools/build_dsk.py --missions   and copy work/elite_missions.dsk to work/xray/disk/.
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_mission_hook.py

From output/firebird_in_flight.sna the script lets the launch finish, stops at handleEntitys (&5066), calls loadLARGEAXX (&8732) so the stub in the LARGEAXX tail is in
RAM, then for each scenario sets variables with memory_write (missionState &38FD, killScoreHigh &38D9, galaxy &38DC, system x/y &3910/&390E), clears
todoUnknownStatusFlags (&1C23, a real docking does), and calls missionsDockedEntry (&1714) with a trap return address at &9F00. The stub loads the overlay file from
the disk (real firmware disk access, a few emulated seconds). A message box is detected by a breakpoint on WaitForKeypress (&3E5E); then a key is pressed. Reports
missionState, killScoreHigh, the Navy unit byte and the credits after the call. chkMissions has a single call site, the docking sequence.
"""
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TRAP = 0x9F00
WAITKEY = 0x3E5E
# name: (state, killScoreHigh, galaxy, x, y, state after, credit thousands added, navy unit after, message, killScoreHigh added)
SCENARIOS = {
    "c_offer_g1":    (0x00, 1, 0, 10, 10, 0x01, 0, 0x00, True, 0),
    "c_offer_low":   (0x00, 0, 0, 10, 10, 0x00, 0, 0x00, False, 0),
    "c_offer_g2":    (0x00, 1, 1, 10, 10, 0x21, 0, 0x00, True, 0),
    "c_hint0":       (0x01, 1, 0, 149, 101, 0x11, 0, 0x00, True, 0),
    "c_hint_wrong":  (0x01, 1, 0, 150, 101, 0x01, 0, 0x00, False, 0),
    "c_hint6":       (0x61, 1, 1, 148, 68, 0x71, 0, 0x00, True, 0),
    "c_reward":      (0x73, 1, 1, 10, 10, 0x02, 5, 0x00, True, 1),
    "p_brief":       (0x02, 5, 2, 10, 10, 0x06, 0, 0x00, True, 0),
    "p_brief_low":   (0x02, 4, 2, 10, 10, 0x02, 0, 0x00, False, 0),
    "p_brief_g1":    (0x02, 5, 0, 10, 10, 0x02, 0, 0x00, False, 0),
    "p_ceerdi":      (0x06, 5, 2, 215, 84, 0x0A, 0, 0x00, True, 0),
    "p_ceerdi_wrong": (0x06, 5, 2, 215, 85, 0x06, 0, 0x00, False, 0),
    "p_birera":      (0x0A, 5, 2, 63, 72, 0x0E, 0, 0xFE, True, 1),
    "p_birera_early": (0x06, 5, 2, 63, 72, 0x06, 0, 0x00, False, 0),
    "all_done":      (0x0E, 6, 2, 63, 72, 0x0E, 0, 0x00, False, 0),
}
# Trumbles offer: extra setup per scenario: cash (thousands word, decicredits word), the count before, the key pressed, and the count / cash change expected
EXTRA = {
    "t_offer_yes":    dict(cash=(6, 0), key="y", count_after=1, cash_delta=-5),
    "t_offer_no":     dict(cash=(6, 0), key="space", count_after=0, cash_delta=0),
    "t_cash_exact":   dict(cash=(5, 176), key="space", count_after=0, cash_delta=0),
    "t_cash_short":   dict(cash=(5, 175), key="space", count_after=0, cash_delta=0),
    "t_poor":         dict(cash=(4, 9999), key="space", count_after=0, cash_delta=0),
    "t_offered_before": dict(cash=(9, 0), key="space", count_after=0, cash_delta=0),
    "t_aboard":       dict(cash=(9, 0), key="space", count=5, count_after=5, cash_delta=0),
}
SCENARIOS.update({
    "t_offer_yes":    (0x0E, 6, 2, 10, 10, 0x8E, 0, 0x00, True, 0),
    "t_offer_no":     (0x0E, 6, 2, 10, 10, 0x8E, 0, 0x00, True, 0),
    "t_cash_exact":   (0x0E, 6, 2, 10, 10, 0x8E, 0, 0x00, True, 0),
    "t_cash_short":   (0x0E, 6, 2, 10, 10, 0x0E, 0, 0x00, False, 0),
    "t_poor":         (0x0E, 6, 2, 10, 10, 0x0E, 0, 0x00, False, 0),
    "t_offered_before": (0x8E, 6, 2, 10, 10, 0x8E, 0, 0x00, False, 0),
    "t_aboard":       (0x0E, 6, 2, 10, 10, 0x0E, 0, 0x00, False, 0),
})


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

            async def call(addr, limit, **regs):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr, **regs}})
                return await c("run", {"max_us": limit, "timeout_s": 200})

            await c("disk_insert", {"drive": "A", "path": "disk/elite_missions.dsk"})
            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            safe = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            await c("breakpoint_remove", {"breakpoint_id": safe})
            await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
            wk = (await c("breakpoint_add", {"address": WAITKEY, "kind": "pc"}))["id"]
            rep = await call(0x8732, 20_000_000)          # loadLARGEAXX
            assert rep.get("pc") == "%04X" % TRAP, rep
            await c("sna_save", {"path": "output/_missions_after_load.sna"})
            ok = True
            for name, (st, ksh, gal, x, y, want, want_cr, want_unit, msg, want_ksh) in SCENARIOS.items():
                await c("sna_load", {"path": "output/_missions_after_load.sna"})
                await wr(0x38FD, st); await wr(0x38D9, ksh); await wr(0x38DC, gal); await wr(0x3910, x); await wr(0x390E, y)
                await wr(0x3926, 0); await wr(0x1C23, 0); await wr(0x3902, 0)
                ex = EXTRA.get(name, {})
                if "cash" in ex:
                    await c("memory_write", {"address": 0x38DD, "data": "%02X %02X %02X %02X" % (ex["cash"][0] & 255, ex["cash"][0] >> 8, ex["cash"][1] & 255, ex["cash"][1] >> 8)})
                await c("memory_write", {"address": 0x3905, "data": "%02X 00" % ex.get("count", 0)})
                cr0 = int.from_bytes(await rd(0x38DD, 2), "little")
                rep = await call(0x1714, 60_000_000)
                ms = rep.get("emulated_us", 0) / 1000   # includes the overlay load from disk (none when the stub returns early)
                shown = rep.get("pc") == "%04X" % WAITKEY
                if shown:
                    await c("screen_image", {"path": f"output/missions_{name}.png"})
                    await c("key_press", {"key": ex.get("key", "space")})
                    rep = await c("run", {"max_us": 30_000_000, "timeout_s": 200})
                    await c("key_release", {"key": ex.get("key", "space")})
                    for _ in range(3):      # a second message (the Trumbles purchase) waits for one more key
                        if rep.get("pc") != "%04X" % WAITKEY:
                            break
                        await c("key_press", {"key": "space"})
                        rep = await c("run", {"max_us": 30_000_000, "timeout_s": 200})
                        await c("key_release", {"key": "space"})
                back = rep.get("pc") == "%04X" % TRAP
                st1 = (await rd(0x38FD))[0]
                cr1 = int.from_bytes(await rd(0x38DD, 2), "little")
                unit = (await rd(0x3902))[0]
                ksh1 = (await rd(0x38D9))[0]
                count1 = int.from_bytes(await rd(0x3905, 2), "little")
                want_cr = ex.get("cash_delta", want_cr)
                good = shown == msg and back and st1 == want and cr1 - cr0 == want_cr and unit == want_unit and ksh1 - ksh == want_ksh and count1 == ex.get("count_after", 0)
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} {name:15s} message={shown} returned={back} state {st:02X}->{st1:02X} (want {want:02X}) credits +{cr1 - cr0} count {count1} unit {unit:02X} killScoreHigh +{ksh1 - ksh}  [{ms:.0f} ms to the message or return]")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

#!/usr/bin/env python3
"""Test the A key of the sell menu (src/elite/sell_all.asm, -DENHANCED) in cpcxray.

Build first:  python3 -I tools/build_dsk.py --missions   (or without --missions) and copy the disk to work/xray/disk/.
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_sellall.py [disk/NAME.dsk]

Boots the disk, starts a new commander (N, Space), fills the hold (cargoHold &38E2, 17 goods) and the cash, opens the sell menu (key 3) and presses a key at the first
quantity prompt. Then it runs to Inventory (&4A40), where the menu has ended. Cases: A sells every good (the hold ends empty, the cash rises), another letter leaves with the
hold unchanged, A with an empty hold: the menu has no prompt and ends by itself (the Inventory stop comes before the key). Each case reloads a snapshot taken while docked.
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DISK = sys.argv[1] if len(sys.argv) > 1 else "disk/elite_missions.dsk"
INVENTORY = 0x4A40
HOLD = [5, 0, 3, 0, 0, 7, 0, 1, 0, 0, 0, 2, 0, 0, 0, 4, 0]     # goods 0..16
CASES = {"a_sells_all": ("a", HOLD, True), "a_empty_hold": ("a", [0] * 17, True), "x_leaves": ("x", HOLD, False)}


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

            async def rd(addr, n=1):
                return bytes.fromhex((await c("memory_read", {"address": addr, "length": n}))["hex"])

            async def tap(key, secs=1.3):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 60})
                await c("key_release", {"key": key})
                await c("run", {"max_us": 800_000, "timeout_s": 60})

            await c("disk_insert", {"drive": "A", "path": DISK})
            await c("run", {"max_us": 3_000_000, "timeout_s": 60})
            await c("type_text", {"text": 'run"elite\n', "wait": False})
            bp = (await c("breakpoint_add", {"address": 0x1CD9, "kind": "pc"}))["id"]   # the first title loop
            for _ in range(8):
                if (await c("run", {"max_us": 10_000_000, "timeout_s": 120})).get("reason") == "breakpoint":
                    break
            await c("breakpoint_remove", {"breakpoint_id": bp})
            await c("run", {"max_us": 1_000_000, "timeout_s": 60})
            await tap("n")
            await c("run", {"max_us": 3_000_000, "timeout_s": 60})
            await tap("space")
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("sna_save", {"path": "output/_sellall_docked.sna"})
            ok = True
            await c("breakpoint_add", {"address": INVENTORY, "kind": "pc"})
            for name, (key, hold, sells) in CASES.items():
                await c("sna_load", {"path": "output/_sellall_docked.sna"})
                await c("memory_write", {"address": 0x38E2, "data": " ".join("%02X" % b for b in hold)})
                await c("memory_write", {"address": 0x38DD, "data": "10 00 00 00"})    # 16 thousand Cr
                cash0 = 0x10
                await tap("3", 0.6)                    # the sell menu: the first prompt waits for a key
                await c("screen_image", {"path": f"output/sellall_{name}_menu.png"})
                if any(hold):                          # an empty hold has no prompt: the menu already ended
                    await c("key_press", {"key": key})
                rep = await c("run", {"max_us": 30_000_000, "timeout_s": 300})
                await c("key_release", {"key": key})
                at_inv = rep.get("pc") == "%04X" % INVENTORY
                after = list(await rd(0x38E2, 17))
                cash1 = int.from_bytes(await rd(0x38DD, 4), "little")
                good = (at_inv or not any(hold)) and (after == [0] * 17 if sells else after == hold) and ((cash1 > cash0) if (sells and any(hold)) else (cash1 == cash0))
                ok &= good
                print(f"{'ok  ' if good else 'FAIL'} {name:13s} at Inventory={at_inv} hold {after} cash {cash0}->{cash1}")
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

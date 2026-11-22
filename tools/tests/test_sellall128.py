#!/usr/bin/env python3
"""Test the A key of the sell menu on the 128K build (src/elite128/sell_all.asm) in cpcxray.

Build first:  python3 -I tools/build_dsk128.py && cp build/elite128.dsk work/xray/disk/, and make output/docked128.sna with tools/tests/snap_docked128.py.
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I <this file> [disk/elite128.dsk]

Starts from output/docked128.sna, fills the hold (cargoHold &38E2, 17 goods) and the cash, opens the sell menu (key 3) and presses a key at the first quantity prompt, then runs to
Inventory (&C942), where the menu has ended. Cases: A sells every good (hold empty, cash up), another letter leaves with the hold unchanged, A with an empty hold ends by itself.
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DISK = sys.argv[1] if len(sys.argv) > 1 else "disk/elite128.dsk"
INVENTORY = 0xC942
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
            ok = True
            await c("breakpoint_add", {"address": INVENTORY, "kind": "pc"})
            for name, (key, hold, sells) in CASES.items():
                await c("sna_load", {"path": "output/docked128.sna"})
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

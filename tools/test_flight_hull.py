#!/usr/bin/env python3
"""Spawn the Constrictor (ship type 19) in cpcxray and look at it.

Build and copy first:  python3 -I tools/build_dsk.py --missions ; cp work/elite_missions.dsk work/xray/disk/
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_flight_hull.py [TYPE]

From output/firebird_in_flight.sna: lookforFreeSlot (&816B) gives IX, spawnShip (&80CD) builds type TYPE (default 19) there, the position is set
ahead of the player, then 2 s run and a screenshot (output/missions_ship.png). Prints the blueprint address stored in the slot (ix+35/36) and whether the
slot survived (ix+34 non-zero after the run). The addresses are for the -DMISSIONS build (spawnShip &80CD, lookforFreeSlot &816B); stock has the same.
"""
import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TRAP = 0x9F00
ROOT = Path(__file__).resolve().parent.parent


def built_commonxx():
    """assemble COMMONXX with -DMISSIONS (the snapshot holds the stock code; only LARGEAXX comes from the disk)"""
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "c.bin"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DMISSIONS", f"--raw={out}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        return out.read_bytes()
TYPE = int(sys.argv[1]) if len(sys.argv) > 1 else 19


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

            async def call(addr, **regs):
                sp = (await c("registers_get"))["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr, **regs}})
                return await c("run", {"max_us": 2_000_000, "timeout_s": 60})

            await c("disk_insert", {"drive": "A", "path": "disk/elite_missions.dsk"})
            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            new, base = built_commonxx(), 0x1A40
            for lo, hi in ((0x80CD, 0x80D0), (0x9D9E, 0xA000)):   # call site in spawnShip, the flight tail
                await c("memory_write", {"address": lo, "data": new[lo - base:hi - base].hex()})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})   # the snapshot is still undocking: let the launch finish
            await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
            rep = await call(0x816B)
            ix = (await c("registers_get"))["ix"]
            print("free slot IX = %04X" % ix)
            rep = await call(0x80CD, a=TYPE, ix=ix)
            ix = (await c("registers_get"))["ix"]
            hdr = bytes.fromhex((await c("memory_read", {"address": ix + 34, "length": 3}))["hex"])
            print("slot flags %02X, blueprint address %04X" % (hdr[0], hdr[1] | hdr[2] << 8))
            for off, val in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0x03), (8, 0), (37, 0x7F)):   # z 768 straight ahead, hostile flags like spawnCommand1
                await c("memory_write", {"address": ix + off, "data": "%02X" % val})
            await call(0x82B8, ix=ix)                     # setDirectionofEntity: builds the orientation, without it the ship is not drawn
            await c("breakpoint_remove", {"breakpoint_id": 1})
            await c("run", {"max_us": 120_000, "timeout_s": 60})
            print("position bytes ix+0..8 after the run:", (await c("memory_read", {"address": ix, "length": 9}))["hex"])
            alive = (await c("memory_read", {"address": ix + 34, "length": 1}))["hex"]
            print("slot flag after 2 s:", alive)
            print(await c("screen_image", {"path": "output/missions_ship.png"}))


asyncio.run(main())

#!/usr/bin/env python3
"""Which zero runs of the parked firmware RAM survive the game's disk operations while docked? Companion of tools/tests/test_parked_ram.py (TODO.md "Parked firmware RAM").

Docked, the parked copy of &0040-&1A3F lives at &A600-&BFFF, the firmware's own upper RAM, which AMSDOS uses as workspace during disk writes. Method: copy the Firebird
disk to work/xray/disk/parked_probe.dsk (inserted writable), load firebird_in_flight.sna, fill every zero run of 16+ bytes in &0040-&1A3F with a marker, fly, jump into the end of
the docking sequence (as test_parked_ram.py) and save that docked state. Then, each from the docked state: the game's commander save (PC at the `call SaveSavegame` in
saveGame, &0E63), a second save under another name, a load of the saved file (`call loadFile` in loadGame, &0DA8), a load of a file that does not exist (the DISK ERROR path), and
a launch followed by flight. After each, the marker bytes that changed are collected; the end of the run lists, per run, how many bytes any operation touched and the longest span
nothing touched.
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_parked_save.py [MARK]
  BUILD=128 for the 128K build (absolute script path in the worktree; needs output/flight128.sna and disk/elite128.dsk; LARGEAXX is at the same addresses there).
"""
import asyncio
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parked_common import DISK_BASE, DOCK_CONT, HANDLE, SNA_FLIGHT, marker, zero_runs  # noqa: E402
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MARK = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0xAA
SAVE_CALL, SAVE_RET = 0x0E63, 0x0E6C   # `call SaveSavegame` in saveGame; where it returns (6 inline parameter bytes)
LOAD_CALL, LOAD_RET = 0x0DA8, 0x0DAF   # `call loadFile` in loadGame; 4 inline parameter bytes
MENU = 0x0D40               # Filemenuloop: where the DISK ERROR path ends
NAME = 0x0E6E               # SaveGameName, 8 characters
OUT = Path("output")
DISK = Path("disk/parked_probe.dsk")


async def main():
    shutil.copy(DISK_BASE, DISK)
    async with stdio_client(StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def c(n, a=None):
                x = await s.call_tool(n, a or {})
                return getattr(x.content[0], "text", "") if x.content else ""

            async def snap(name):
                await c("sna_save", {"path": f"output/{name}.sna"})
                return (OUT / f"{name}.sna").read_bytes()[0x100:0x100 + 65536]

            async def hold(key, secs=1.4):
                await c("key_press", {"key": key})
                await c("run", {"max_us": int(secs * 1e6), "timeout_s": 120})
                await c("key_release", {"key": key})
                await c("run", {"max_us": 300000, "timeout_s": 60})

            dirty = set()

            def collect(tag, ram, base):
                bad = {k for a, l in runs for k in range(a, a + l) if ram[base + k - 0x40] != MARK}
                dirty.update(bad)
                print(f"{tag}: {len(bad)} of {sum(l for _, l in runs)} marker bytes changed", flush=True)

            async def op(tag, calls):
                """Restore the docked state, run each (pc, return-pc, name) call, report the parked copy."""
                await c("sna_load", {"path": "output/_psave_docked.sna"})
                for pc, ret, name in calls:
                    await c("memory_write", {"address": NAME, "data": " ".join(f"{ord(ch):02X}" for ch in name)})
                    await c("breakpoint_add", {"address": ret, "kind": "pc"})
                    await c("registers_set", {"values": {"pc": pc}})
                    res = await c("run", {"max_us": 40000000, "timeout_s": 240})
                    print(f"  {tag} {name!r}: {res[:90].replace(chr(10), ' ')}", flush=True)
                    for bp in range(1, 8):
                        await c("breakpoint_remove", {"breakpoint_id": bp})
                await c("run", {"max_us": 2000000, "timeout_s": 60})
                collect(tag, await snap("_psave_op"), 0xA600)

            await c("disk_insert", {"drive": "A", "path": str(DISK), "writable": True})
            await c("sna_load", {"path": SNA_FLIGHT})
            runs = zero_runs(await snap("_psave0"))
            print("zero runs >= 16 bytes:", len(runs), "total", sum(l for _, l in runs), flush=True)
            for a, l in runs:
                await c("memory_write", {"address": a, "data": marker(MARK, l)})
            await c("run", {"max_us": 5000000, "timeout_s": 120})
            await c("breakpoint_add", {"address": HANDLE, "kind": "pc"})
            await c("run", {"max_us": 10000000, "timeout_s": 120})
            await c("registers_set", {"values": {"pc": DOCK_CONT}})
            await c("breakpoint_remove", {"breakpoint_id": 1})
            await c("run", {"max_us": 20000000, "timeout_s": 120})
            collect("docked", await snap("_psave_docked"), 0xA600)

            await op("save", [(SAVE_CALL, SAVE_RET, "PROBE   ")])
            print("catalog:", " ".join(f["name"] for f in __import__("json").loads(await c("disk_catalog", {"drive": "A"}))["files"]), flush=True)
            await op("two saves", [(SAVE_CALL, SAVE_RET, "PROBE   "), (SAVE_CALL, SAVE_RET, "SECOND  ")])
            await op("load", [(LOAD_CALL, LOAD_RET, "PROBE   ")])
            await op("load missing file", [(LOAD_CALL, MENU, "NOFILE  ")])

            await c("sna_load", {"path": "output/_psave_docked.sna"})
            await hold("f1", 1.4)
            await c("run", {"max_us": 25000000, "timeout_s": 120})
            collect("launch (low memory)", await snap("_psave_l1"), 0x40)
            await c("run", {"max_us": 10000000, "timeout_s": 120})
            collect("10 s flight", await snap("_psave_l2"), 0x40)

            print("\nper run (low address, length, A600-half address): bytes touched by any operation, longest untouched span", flush=True)
            for a, l in sorted(runs, key=lambda x: -x[1]):
                hit = [k for k in range(a, a + l) if k in dirty]
                best = cur = 0
                start = a
                for k in range(a, a + l):
                    if k in dirty:
                        cur = 0
                    else:
                        cur += 1
                        if cur > best:
                            best, start = cur, k - cur + 1
                print(f"  {a:04X} {l:4d} {0xA600 + a - 0x40:04X}  touched {len(hit):4d}  longest clean {best:4d} at {start:04X}", flush=True)


asyncio.run(main())

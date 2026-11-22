#!/usr/bin/env python3
"""Is the zero space in the parked firmware RAM (low memory &0040-&1A3F in flight) really unused? (docs/_memory_map.md "The bitmap and the swap")

Method: load firebird_in_flight.sna, fill every zero run of 16+ bytes in &0040-&1A3F with a marker, fly (chart screens, keys), jump into the end of the docking
sequence (after todoDockingProcedure: InitVariables, loadLARGEAXX, docked screens), wait, launch (F1 + launchSequence swap), fly again. After each phase save a
snapshot and count the marker bytes that changed; in the docked phase the parked copy lives at &A600 (low memory holds LARGEAXX), so the marker run is read there.
usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_parked_ram.py [MARK]
  BUILD=128 for the 128K build (absolute script path in the worktree; needs output/flight128.sna and disk/elite128.dsk).
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parked_common import DISK_BASE, DOCK_CONT, HANDLE, SNA_FLIGHT, marker, zero_runs  # noqa: E402
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MARK = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0xAA
OUT = Path("output")


async def main():
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

            async def report(tag, ram, base):
                bad = []
                for a, l in runs:
                    for k in range(a, a + l):
                        if ram[base + k - 0x40] != MARK:
                            bad.append(k)
                print(f"{tag}: {len(bad)} of {sum(l for _, l in runs)} marker bytes changed", flush=True)
                # runs of changed bytes
                out, i = [], 0
                while i < len(bad):
                    j = i
                    while j + 1 < len(bad) and bad[j + 1] == bad[j] + 1:
                        j += 1
                    out.append(f"{bad[i]:04X}-{bad[j]:04X}")
                    i = j + 1
                print("   changed:", " ".join(out[:60]), flush=True)

            await c("disk_insert", {"drive": "A", "path": DISK_BASE})
            await c("sna_load", {"path": SNA_FLIGHT})
            ram = await snap("_parked0")
            runs = zero_runs(ram)
            print("zero runs >= 16 bytes:", len(runs), "total", sum(l for _, l in runs), flush=True)
            for a, l in runs:
                await c("memory_write", {"address": a, "data": marker(MARK, l)})

            # phase 1: flight with keys
            await c("run", {"max_us": 3000000, "timeout_s": 120})
            for k in ("5", "6", "7", "5"):
                await hold(k)
            await c("run", {"max_us": 3000000, "timeout_s": 120})
            await report("flight", await snap("_parked1"), 0x40)

            # phase 2: docking tail, docked screens
            await c("breakpoint_add", {"address": HANDLE, "kind": "pc"})
            res = await c("run", {"max_us": 10000000, "timeout_s": 120})
            await c("registers_set", {"values": {"pc": DOCK_CONT}})
            await c("breakpoint_remove", {"breakpoint_id": 1})
            await c("run", {"max_us": 20000000, "timeout_s": 120})
            ram = await snap("_parked2")
            await report("docked (parked copy at A600)", ram, 0xA600)

            # phase 3: launch and fly
            await hold("f1", 1.4)
            await c("run", {"max_us": 25000000, "timeout_s": 120})
            await report("after launch", await snap("_parked3"), 0x40)
            await c("run", {"max_us": 5000000, "timeout_s": 120})
            await report("after 5 s flight", await snap("_parked4"), 0x40)

            # phase 4: hyperspace (chart cursor tap, h), more flight keys, then a second dock and launch cycle
            await hold("6", 1.4)
            await hold("cursor_left", 0.2)
            await hold("h", 1.4)
            await c("run", {"max_us": 25000000, "timeout_s": 120})
            for k in ("5", "7", "6"):
                await hold(k)
            await c("run", {"max_us": 10000000, "timeout_s": 120})
            await report("after hyperspace", await snap("_parked5"), 0x40)
            await c("breakpoint_add", {"address": HANDLE, "kind": "pc"})
            await c("run", {"max_us": 10000000, "timeout_s": 120})
            await c("registers_set", {"values": {"pc": DOCK_CONT}})
            bps = await c("breakpoint_list")
            await c("breakpoint_remove", {"breakpoint_id": 2})
            await c("run", {"max_us": 20000000, "timeout_s": 120})
            await report("second docking (A600 copy)", await snap("_parked6"), 0xA600)
            await hold("f1", 1.4)
            await c("run", {"max_us": 25000000, "timeout_s": 120})
            await report("second launch", await snap("_parked7"), 0x40)
            await c("run", {"max_us": 10000000, "timeout_s": 120})
            await report("end", await snap("_parked8"), 0x40)

asyncio.run(main())

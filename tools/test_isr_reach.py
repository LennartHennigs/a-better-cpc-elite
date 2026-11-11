#!/usr/bin/env python3
"""Phase 0a of the 128K plan: which addresses does the interrupt service routine execute, flight and title screen?

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_isr_reach.py [N_ISR]

Loads output/firebird_in_flight.sna, finds the ISR from the jump at &0038, and single-steps N_ISR (default 12, enough to cover all six counter values twice)
interrupts from the entry until the return to the interrupted code. Prints the executed PCs as address ranges and flags every one outside
bank 0/2 (&0000-&3FFF, &8000-&BFFF), i.e. the part the 128K layout would hide behind a window or the screen. Writes nothing but the report.
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

N_ISR = int(sys.argv[1]) if len(sys.argv) > 1 else 12


def ranges(pcs):
    out, a = [], None
    for p in sorted(pcs):
        if a is None:
            a = b = p
        elif p - b <= 3:
            b = p
        else:
            out.append((a, b))
            a = b = p
    if a is not None:
        out.append((a, b))
    return out


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

            await c("disk_insert", {"drive": "A", "path": "disk/Elite_UK_Firebird_cracked_trainer.dsk"})
            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            await c("run", {"max_us": 3_000_000, "timeout_s": 60})
            vec = (await c("memory_read", {"address": 0x38, "length": 3}))["hex"].replace(" ", "")
            assert vec[:2].lower() == "c3", f"no jp at &0038: {vec}"
            isr = int(vec[4:6] + vec[2:4], 16)
            print(f"ISR entry (target of the jp at &0038): &{isr:04X}")
            bp = (await c("breakpoint_add", {"address": isr, "kind": "pc"}))["id"]
            pcs = set()
            for n in range(N_ISR):
                rep = await c("run", {"max_us": 200_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep
                reg = await c("registers_get")
                sp0 = reg["sp"]
                rb = (await c("memory_read", {"address": sp0, "length": 2}))["hex"].replace(" ", "")
                ret = int(rb[2:4] + rb[0:2], 16)
                await c("breakpoint_enable", {"breakpoint_id": bp, "enabled": False})
                steps = 0
                while True:
                    reg = await c("registers_get")
                    if reg["pc"] == ret and reg["sp"] == sp0 + 2 and steps > 0:
                        break
                    pcs.add(reg["pc"])
                    await c("step", {"count": 1})
                    steps += 1
                    assert steps < 20000, "ISR did not return"
                print(f"  interrupt {n + 1}: {steps} instructions, returned to &{ret:04X}", flush=True)
                await c("breakpoint_enable", {"breakpoint_id": bp, "enabled": True})
            print("\nExecuted PCs (merged ranges):")
            bad = []
            for a, b in ranges(pcs):
                bank = "ok " if (b < 0x4000 or 0x8000 <= a < 0xC000) else "!! "
                if bank == "!! ":
                    bad.append((a, b))
                print(f"  {bank}&{a:04X}-&{b:04X}")
            print(f"\n{len(pcs)} distinct PCs; ranges outside banks 0/2: {len(bad)}")


asyncio.run(main())

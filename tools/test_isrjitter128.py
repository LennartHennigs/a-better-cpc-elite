#!/usr/bin/env python3
"""Jitter of the interrupt entry (raster split timing) in flight, 128K build (plan step "raster split jitter").

usage (from work/xray):  DISK128=disk/elite128.dsk SNA=output/flight128.sna PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_isrjitter128.py [N]
Loads SNA, breakpoints the interrupt vector (&0038) N times (default 300), and takes the emulated clock of each entry modulo the interrupt period (the gate array raises 6 per
frame, 3328 us apart at 50 Hz). Prints the lateness of each entry against the earliest phase seen (0 = on time): max, 95th percentile, mean. A flip build whose copy keeps interrupts
off for long chunks shows late entries; the stock game shows only the small delay of its own di sections.
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
PERIOD = 19968 / 6


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

            await c("disk_insert", {"drive": "A", "path": os.environ.get("DISK128", "disk/elite128.dsk")})
            await c("sna_load", {"path": os.environ.get("SNA", "output/flight128.sna")})
            await c("run", {"max_us": 1_000_000, "timeout_s": 60})
            await c("breakpoint_add", {"address": 0x38, "kind": "pc"})
            ph = []
            for i in range(N):
                rep = await c("run", {"max_us": 500_000, "timeout_s": 60})
                if rep.get("reason") != "breakpoint":
                    break
                ph.append((await c("machine_status"))["clock_us"] % PERIOD)
                await c("step", {})
    base = min(ph)
    # the interrupt grid is fixed by the gate array; entries are late by whatever the code did with interrupts off
    late = sorted(((p - base) % PERIOD) for p in ph)
    # re-anchor on the earliest cluster: use the 5th percentile as "on time"
    ref = late[len(late) // 20]
    late = sorted(max(0.0, x - ref) for x in late)
    print("top lateness (us):", [round(x) for x in late[-12:]])
    print(f"{len(ph)} entries: max late {late[-1]:.0f} us, p95 {late[int(len(late) * .95)]:.0f} us, mean {sum(late) / len(late):.0f} us (one scan line = 64 us)")


asyncio.run(main())

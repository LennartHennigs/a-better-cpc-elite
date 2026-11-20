#!/usr/bin/env python3
"""Time the key pre-delay (sub_403E, src/elite/commonxx.asm) in cpcxray: stock operand 0x80 against the -DENHANCED one.

usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_keydelay.py

From output/firebird_in_flight.sna, stopped at handleEntitys (&5066, normal stack), calls sub_403E (&403E) with each operand and prints the emulated time
until it returns (a halt loop: B interrupts, 300 per second). The operand of the built ENHANCED file comes from its symbol file.
"""
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
TRAP = 0x9F00
SUB = 0x403E


def enhanced_operand():
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DENHANCED", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        addr = next(int(l.split()[-1], 16) for l in sym.read_text().splitlines() if l.startswith("predelayOperand:"))
        return out.read_bytes()[addr - 0x1A40]


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
            await c("run", {"max_us": 6_000_000, "timeout_s": 60})
            safe = (await c("breakpoint_add", {"address": 0x5066, "kind": "pc"}))["id"]
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            await c("breakpoint_remove", {"breakpoint_id": safe})
            saved = await c("registers_get")
            await c("breakpoint_add", {"address": TRAP, "kind": "pc"})
            assert (await c("memory_read", {"address": SUB, "length": 2}))["hex"].lower() == "0680", "snapshot does not hold the stock sub_403E"
            for name, val in (("stock", 0x80), ("enhanced", enhanced_operand())):
                await c("memory_write", {"address": SUB + 1, "data": "%02X" % val})
                sp = saved["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": SUB}})
                t0 = (await c("machine_status"))["clock_us"]
                rep = await c("run", {"max_us": 3_000_000, "timeout_s": 60})
                t1 = (await c("machine_status"))["clock_us"]
                print(f"{name}: B={val:#04x}  {(t1 - t0) / 1000:.0f} ms  (stopped: {rep.get('reason')}, expected {val * 1000 / 300:.0f} ms)")
            await c("registers_set", {"values": {k: saved[k] for k in ("af", "bc", "de", "hl", "ix", "iy", "sp", "pc") if k in saved}})


asyncio.run(main())

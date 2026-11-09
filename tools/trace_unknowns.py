#!/usr/bin/env python3
"""Who reads and writes the still-unnamed variables? (cpcxray access breakpoints, see TODO.md "dat_" item)

usage (from work/xray, with cpcxray's own interpreter):
  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/trace_unknowns.py OUT.json [PRESSES] [SEED] [quiet]

Loads output/firebird_in_flight.sna, puts access breakpoints on the variables below (addresses come from a sjasmplus --sym build of
src/elite/commonxx.asm), then presses keys (1.3 s each) with the galactic hyperdrive fitted, and records for every variable the program
counters that touched it (access kind and byte value). Map the pcs to routines with the same symbol table.
"quiet" leaves out sEntityunknown (the entity loops hit it thousands of times) and presses only screen and jump keys.
"""
import asyncio, json, random, re, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ["sEntityunknown", "fuelPriceByte", "dat_3D2D", "creditsHighWordHi", "dat_38E1"]   # labels in src/elite/commonxx.asm
KEYS = list("0123456789") + ["h", "g", "space", "enter", "cursor_left", "cursor_right", "cursor_up", "cursor_down", "n", "t", "m"]
QUIET_KEYS = ["g", "g", "8", "9", "4", "5", "7", "h", "space", "g", "enter", "1", "2", "3"]
MAX_STOPS = 3000


def symbols():
    with tempfile.TemporaryDirectory() as d:
        sym = Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), f"--raw={Path(d) / 'c.bin'}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")],
                       check=True, capture_output=True)
        return {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}


async def main():
    out = sys.argv[1]
    presses = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    quiet = len(sys.argv) > 4 and sys.argv[4] == "quiet"
    syms = symbols()
    names = [n for n in TARGETS if not (quiet and n == "sEntityunknown")]
    by_addr = {syms[n]: n for n in names}
    keys = QUIET_KEYS if quiet else KEYS
    params = StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def call(name, args=None):
                x = await s.call_tool(name, args or {})
                t = "".join(getattr(i, "text", "") for i in x.content)
                try:
                    return json.loads(t)
                except ValueError:
                    return t

            await call("sna_load", {"path": "output/firebird_in_flight.sna"})
            for a in by_addr:
                await call("breakpoint_add", {"address": a, "kind": "access"})
            await call("memory_write", {"address": syms["galacticHyperdrive"], "data": "FF"})
            await call("memory_write", {"address": syms["fuel"], "data": "46"})
            hits = {n: defaultdict(lambda: {"n": 0, "values": []}) for n in names}
            stops = 0
            for n in range(presses):
                key = random.choice(keys)
                await call("key_press", {"key": key})
                left = 1_300_000
                while left > 0 and stops < MAX_STOPS:
                    rep = await call("run", {"max_us": left, "timeout_s": 120})
                    if not isinstance(rep, dict):
                        break
                    left -= rep.get("emulated_us", left)
                    if rep.get("reason") == "time_limit":
                        break
                    stops += 1
                    bp = rep.get("breakpoint") or {}
                    name = by_addr.get(int(bp.get("address", "0"), 16))
                    if name:
                        h = hits[name][f"{bp.get('access')}@{bp.get('pc')}"]
                        h["n"] += 1
                        if bp.get("value") not in h["values"] and len(h["values"]) < 8:
                            h["values"].append(bp.get("value"))
                await call("key_release", {"key": key})
                print(f"press {n}/{presses} key {key} stops {stops}", flush=True)
            json.dump(hits, open(out, "w"), indent=1)
            print("done", out)


asyncio.run(main())

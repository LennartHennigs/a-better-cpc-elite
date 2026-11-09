#!/usr/bin/env python3
"""Who reads and writes the still-unnamed variables? (cpcxray access breakpoints, see TODO.md "dat_" item)

usage (from work/xray, with cpcxray's own interpreter):
  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/trace_unknowns.py OUT.json [PRESSES] [SEED]

Loads output/firebird_in_flight.sna, puts access breakpoints on the addresses below, then presses keys (1.3 s each) with the
galactic hyperdrive fitted, and records for every address the program counters that touched it (with the byte value at the stop).
Map the pcs to routines with a sjasmplus --sym of src/elite/commonxx.asm.
"""
import asyncio, json, random, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TARGETS = {"sEntityunknown": 0x1A66, "dat_2F36": 0x2F36, "dat_3D2D": 0x3D2D, "dat_38DE": 0x38DE, "dat_38E1": 0x38E1}
GALACTIC_HYPERDRIVE = 0x3904   # galacticHyperdrive in src/elite/commonxx.asm
KEYS = list("0123456789") + ["h", "g", "space", "enter", "cursor_left", "cursor_right", "cursor_up", "cursor_down", "n", "t", "m"]


async def main():
    out = sys.argv[1]
    presses = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    if len(sys.argv) > 4 and sys.argv[4] == "quiet":   # leave out sEntityunknown (hit thousands of times by the entity loops) and press the screen keys
        TARGETS.pop("sEntityunknown")
        KEYS[:] = ["g", "g", "8", "9", "4", "5", "7", "h", "space", "g", "enter", "1", "2", "3"]
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
            for name, a in TARGETS.items():
                await call("breakpoint_add", {"address": a, "kind": "access"})
            await call("memory_write", {"address": GALACTIC_HYPERDRIVE, "data": "FF"})
            await call("memory_write", {"address": 0x38F9, "data": "46"})   # fuel
            hits = {n: {} for n in TARGETS}
            stops = 0
            for n in range(presses):
                key = random.choice(KEYS)
                try:
                    await call("key_press", {"key": key})
                except Exception:
                    continue
                left = 1_300_000
                while left > 0 and stops < 3000:
                    rep = await call("run", {"max_us": left, "timeout_s": 120})
                    if not isinstance(rep, dict):
                        break
                    left -= rep.get("emulated_us", left)
                    if rep.get("reason") == "time_limit":
                        break
                    stops += 1
                    bp = rep.get("breakpoint") or {}
                    addr = int(bp.get("address", "0"), 16)
                    for name, ta in TARGETS.items():
                        if ta == addr:
                            k = f"{bp.get('access')}@{bp.get('pc')}"
                            h = hits[name].setdefault(k, {"n": 0, "values": []})
                            h["n"] += 1
                            if bp.get("value") not in h["values"] and len(h["values"]) < 8:
                                h["values"].append(bp.get("value"))
                await call("key_release", {"key": key})
                print(f"press {n}/{presses} key {key} stops {stops}", flush=True)
            json.dump(hits, open(out, "w"), indent=1, default=str)
            print("done", out)


asyncio.run(main())

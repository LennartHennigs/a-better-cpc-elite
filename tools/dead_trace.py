#!/usr/bin/env python3
"""Dynamic check of dead-code candidates in cpcxray (see docs/_architecture.md, "Dead code and free space").

usage (from work/xray, with cpcxray's own interpreter):
  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/dead_trace.py OUT.json [PRESSES] [SEED]

Loads output/firebird_in_flight.sna, puts execute breakpoints on the candidates and on positive controls
(routines that must run), then presses random keys (1.3 s each, as CLAUDE.md says keys need) and forces some state
(cloak flag, Thargoid mission variable) between presses. A hit on a control proves the harness works; a hit on a
candidate means it is live. Also reports read/write hits on the LARGEAXX tail (&1714-&1A3F) and the bytes of the code
image &1A40-&9FFF that changed between start and end (self-modified code and buffers: the "dynamic labels").
Addresses come from the sjasmplus listing of src/elite (CANDIDATES/CONTROLS below).
"""
import asyncio
import json
import random
import sys
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CANDIDATES = {  # dead according to tools/deadcode.py and the labels "Probably dead"
    "altJrPoint3": 0x7198, "alt_animated_effect_reset": 0x719D, "LAB_ram_8aaa": 0x8AAA,
    "unusedGetFlightMode": 0x204E, "unusedGetCloakFlag": 0x2053,
}
CONTROLS = {  # the db-run chains of docs/_architecture.md (live) and routines that must run
    "LAB_ram_53cf": 0x53CF, "SUB_ram_5dcf": 0x5DCF, "execSpawncmd4": 0x8242,
    "spawnAtEntityCoordinates": 0x8364, "LAB_ram_89f4": 0x89F4, "LAB_ram_8a10": 0x8A10,
    "chkCloak": 0x2017, "handleEntitys": 0x5066, "spawnCommand0": 0x83EF, "loadLARGEAXX": 0x8732,
}
KEYS = list("abcdefghijklmnopqrstuvwxyz0123456789") + ["space", "enter", "cursor_left", "cursor_right", "cursor_up", "cursor_down"]
MISSIONFLAG = 0x3927      # docs/_cheats.md
THARGON_VAR = 0x3926


async def main():
    out = sys.argv[1]
    presses = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
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
            img0 = bytearray()
            for a in range(0x1A40, 0xA000, 0x1000):
                img0 += bytes.fromhex(await read_hex(call, a, min(0x1000, 0xA000 - a)))
            ids = {}
            for name, addr in {**CANDIDATES, **CONTROLS}.items():
                ids[name] = (await call("breakpoint_add", {"address": addr, "kind": "pc"}))["id"]
            tail = (await call("breakpoint_add", {"address": 0x1714, "end": 0x1A3F, "kind": "access"}))["id"]
            first_hit, log, stops = {}, [], 0
            t0 = time.time()
            for n in range(presses):
                key = random.choice(KEYS)
                try:
                    await call("key_press", {"key": key})
                except Exception as e:  # unknown key name: note it once and go on
                    log.append(f"key {key!r}: {e}")
                    continue
                left = 1_300_000
                while left > 0:
                    rep = await call("run", {"max_us": left, "timeout_s": 120})
                    if not isinstance(rep, dict):
                        break
                    left -= rep.get("emulated_us", left)
                    if rep.get("reason") == "time_limit":
                        break
                    stops += 1
                    pc = rep.get("pc")
                    log.append(f"press {n} key {key}: stop {rep.get('reason')} pc={pc}")
                    for name, addr in {**CANDIDATES, **CONTROLS}.items():
                        if pc and int(pc, 16) == addr and name not in first_hit:
                            first_hit[name] = n
                            if name in CONTROLS:   # controls fire often: turn off after the first sighting
                                await call("breakpoint_enable", {"breakpoint_id": ids[name], "enabled": False})
                    if pc and 0x1714 <= int(pc, 16) <= 0x1A3F:
                        pass
                    if stops > 400:
                        left = 0
                await call("key_release", {"key": key})
                if n % 25 == 24:   # force a few states so rarely used paths get their chance
                    await call("memory_write", {"address": MISSIONFLAG, "data": "%02X" % random.choice([0x00, 0x40, 0x42, 0x01])})
                    await call("memory_write", {"address": THARGON_VAR, "data": "%02X" % random.choice([0, 1, 4, 5])})
                if n % 10 == 0:
                    print(f"press {n}/{presses} wall {time.time()-t0:.0f}s hits {sorted(first_hit)}", flush=True)
            bps = await call("breakpoint_list")
            img1 = bytearray()
            for a in range(0x1A40, 0xA000, 0x1000):
                img1 += bytes.fromhex(await read_hex(call, a, min(0x1000, 0xA000 - a)))
            changed, i = [], 0
            while i < len(img0):
                if img0[i] != img1[i]:
                    j = i
                    while j + 1 < len(img0) and (img0[j + 1] != img1[j + 1] or (j + 2 < len(img0) and img0[j + 2] != img1[j + 2])):
                        j += 1
                    changed.append([0x1A40 + i, 0x1A40 + j])
                    i = j + 1
                else:
                    i += 1
            json.dump({"breakpoints": bps, "first_hit_press": first_hit, "changed_ranges": changed, "log": log[:300],
                       "tail_bp_id": tail, "presses": presses}, open(out, "w"), indent=1)
            print("done", out)


async def read_hex(call, addr, length):
    """memory_read returns text; normalise to a hex string (RAM view, ram:0 shows RAM under ROM)."""
    rep = await call("memory_view", {"address": addr, "length": length, "view": "cpu"})
    if isinstance(rep, dict):
        for k in ("hex", "data", "bytes"):
            if k in rep:
                return "".join(rep[k].split()) if isinstance(rep[k], str) else bytes(rep[k]).hex()
    raise RuntimeError(f"unexpected memory_view reply: {str(rep)[:200]}")


asyncio.run(main())

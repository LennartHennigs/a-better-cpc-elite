#!/usr/bin/env python3
"""The 128K build's version of test_parked_save.py: which zero runs of the parked firmware RAM survive the game's own disk menu while docked?

Docked, the parked copy of &0040-&1A3F lives at &A600-&BFFF (bank 2, always visible), the firmware's upper RAM, which AMSDOS uses as workspace during disk operations. Method: load
output/docked128.sna (tools/tests/snap_docked128.py), fill every zero run of 16+ bytes of the copy at &A600-&BFFF with a marker, then use the menu exactly as test_filemenu128.py does
(FileMenu at &0D28: catalogue 3, save 2 with a name, load 1) on a writable copy of the disk, and after each step count the marker bytes that changed. test_parked_save.py drives the
64K game's save routine by forcing the PC, which does not complete on the 128K build (with BUILD=128 its save and load calls ran into the time limit with the PC inside &A600-&BFFF:
the disc calls go through the trampolines on their own stack), so this one uses the menu.
RUNSEL=a:b marks only the zero runs a..b-1 of the list (largest first); RUNSEL=0:0 marks none (the control: the save must work), the default marks all.
usage (from work/xray, absolute script path):  PATH=$HOME/.local/bin:$PATH <cpcxray python> -I /ABS/tools/tests/test_parked_save128.py [MARK]
Prints, per run, how many bytes any step touched and the longest untouched span: a probe, no pass/fail (the rule it backs is "no code in the zero runs of the parked block").
"""
import asyncio
import json
import os
import shutil
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MARK = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0xAA
LO, HI = 0xA600, 0xC000
OUT = Path("output")
DISK = "disk/parked_probe128.dsk"


def zero_runs(ram, lo=LO, hi=HI, minimum=16):
    runs, i = [], lo
    while i < hi:
        if ram[i] == 0:
            j = i
            while j < hi and ram[j] == 0:
                j += 1
            if j - i >= minimum:
                runs.append((i, j - i))
            i = j
        else:
            i += 1
    return runs


async def main():
    shutil.copy("disk/elite128.dsk", DISK)
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

            async def snap(name):
                await c("sna_save", {"path": f"output/{name}.sna"})
                return (OUT / f"{name}.sna").read_bytes()[0x100:0x100 + 65536]      # banks 0-3 of the flat file: bank 2 holds &8000-&BFFF

            async def key(k, hold=250_000, after=12_000_000):
                await c("key_press", {"key": k})
                await c("run", {"max_us": hold, "timeout_s": 60})
                await c("key_release", {"key": k})
                await c("run", {"max_us": after, "timeout_s": 120})

            async def typ(t):
                await c("type_text", {"text": t, "wait": False})
                await c("run", {"max_us": 6_000_000, "timeout_s": 120})
                await c("run", {"max_us": 15_000_000, "timeout_s": 120})

            dirty = set()

            def collect(tag, ram):
                bad = {k for a, l in marked for k in range(a, a + l) if ram[k] != MARK}
                dirty.update(bad)
                print(f"{tag}: {len(bad)} of {sum(l for _, l in marked)} marker bytes changed", flush=True)

            await c("disk_insert", {"drive": "A", "path": DISK, "writable": True})
            await c("sna_load", {"path": "output/docked128.sna"})
            await c("run", {"max_us": 500_000, "timeout_s": 60})
            runs = zero_runs(await snap("_psave128_0"))
            print("zero runs >= 16 bytes in &A600-&BFFF:", len(runs), "total", sum(l for _, l in runs), flush=True)
            lo_sel, hi_sel = (int(v) for v in os.environ.get("RUNSEL", f"0:{len(runs)}").split(":"))
            marked = sorted(runs, key=lambda x: -x[1])[lo_sel:hi_sel]
            print("marked runs:", [f"{a:04X}+{l}" for a, l in marked], flush=True)
            for a, l in marked:
                await c("memory_write", {"address": a, "data": " ".join(f"{MARK:02X}" for _ in range(l))})
            sp = (await c("registers_get"))["sp"] - 2
            await c("memory_write", {"address": sp, "data": "00 9F"})
            await c("registers_set", {"values": {"sp": sp, "pc": 0x0D28}})      # FileMenu
            await c("run", {"max_us": 1_500_000, "timeout_s": 60})
            collect("menu open", await snap("_psave128_1"))
            await key("3")                                   # catalogue
            collect("catalogue", await snap("_psave128_2"))
            await key("space", after=1_000_000)
            await key("2")                                   # save
            await typ("TEST\n")
            files = [f["name"] for f in (await c("disk_catalog", {"drive": "A"}))["files"]]
            print("save worked:", "2.BIN" in files, flush=True)      # the key press that chose "save" leaks one character into the name prompt (see test_filemenu128.py)
            collect("save", await snap("_psave128_3"))
            await key("1")                                   # load
            await key("del", after=500_000)
            await typ("2")
            await key("return")
            collect("load", await snap("_psave128_4"))

            print("\nper run (address, length): bytes touched by any step, longest untouched span", flush=True)
            for a, l in marked:
                best = cur = 0
                start = a
                for k in range(a, a + l):
                    if k in dirty:
                        cur = 0
                    else:
                        cur += 1
                        if cur > best:
                            best, start = cur, k - cur + 1
                print(f"  {a:04X} {l:4d}  touched {sum(1 for k in range(a, a + l) if k in dirty):4d}  longest clean {best:4d} at {start:04X}", flush=True)


asyncio.run(main())

#!/usr/bin/env python3
"""Standalone test of src/elite128/fill.asm in cpcxray (128K plan, Phase 1): fill a hull into the game bitmap through bank 6, look at it.

Build first:  python3 -I tools/ship128.py ; sjasmplus --raw=work/elite128/fill.bin src/elite128/fill.asm
usage (from work/xray):  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_fill128.py [TYPE [FRAMES [VISPOS]]]
  TYPE    ship type 0..18 (index in shipGFXdataTable; 12 = Cobra Mk III, 8 = Viper, 13 = Asp, default 12)
  FRAMES  number of turning frames (default 6); VISPOS is baked into fill.bin: assemble with -DVISPOS=0 to test the other winding.
Boots output/firebird_in_flight.sna to handleEntitys (&5066), maps bank 6 at &4000 with a snippet in the flight tail (&9F00), loads the module and the fill
records, runs fillInit, then for each frame writes the projected vertices (x magnitude, y magnitude, flag, like buf_5860) into VBUF, calls fillHull
through the same map/unmap sequence the game glue will use, reads the bitmap &A000-&BFFF and writes work/elite128/fill_TYPE_FRAME.png.
"""
import asyncio
import json
import math
import struct
import sys
import zlib
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/elite128"
TYPE = int(sys.argv[1]) if len(sys.argv) > 1 else 12
FRAMES = int(sys.argv[2]) if len(sys.argv) > 2 else 6
VBUF, SNIP, TRAP = 0x9D9E, 0x9F00, 0x9FE0
MAP, UNMAP, CALL, INIT = SNIP, SNIP + 0x10, SNIP + 0x20, SNIP + 0x40


def png(path, w, h, rows):
    raw = b"".join(b"\0" + bytes(r) for r in rows)
    pal = [(0, 0, 0), (0, 0, 160), (0, 200, 200), (255, 255, 255)]
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 3, 0, 0, 0)) + chunk(b"PLTE", b"".join(bytes(c) for c in pal)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    Path(path).write_bytes(data)


def project(points, ang, tilt=-0.3, dist=None):
    pr = []
    for x, y, z in points:
        x, z = x * math.cos(ang) + z * math.sin(ang), -x * math.sin(ang) + z * math.cos(ang)
        y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
        pr.append((x, y, z))
    r = max(math.dist((0, 0, 0), p) for p in pr)
    dist = dist or r * 3.0
    scale = 55 / r * 2.2
    out = []
    for x, y, z in pr:
        f = dist / (dist + z)
        sx, sy = x * scale * f, y * scale * f                 # y up
        flag = (2 if sx < 0 else 0) | (1 if sy < 0 else 0)      # bit 1 left of centre, bit 0 below the centre
        out += [min(127, int(round(abs(sx)))), min(63, int(round(abs(sy)))), flag]
    return bytes(out)


async def main():
    pts = json.loads((OUT / "ship128_points.json").read_text())[str(TYPE)]
    print("ship", TYPE, pts["name"], len(pts["points"]), "vertices")
    mod, data = (OUT / "fill.bin").read_bytes(), (OUT / "fill128.bin").read_bytes()
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

            def hx(b):
                return " ".join("%02X" % v for v in b)

            await c("disk_insert", {"drive": "A", "path": "disk/Elite_UK_Firebird_cracked_trainer.dsk"})
            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("breakpoint_add", {"address": 0x5066, "kind": "pc"})
            rep = await c("run", {"max_us": 10_000_000, "timeout_s": 60})
            assert rep.get("reason") == "breakpoint", rep
            saved = await c("registers_get")
            await c("breakpoint_add", {"address": TRAP, "kind": "pc"})

            async def call(addr):
                sp = saved["sp"] - 2
                await c("memory_write", {"address": sp, "data": "%02X %02X" % (TRAP & 255, TRAP >> 8)})
                await c("registers_set", {"values": {"sp": sp, "pc": addr}})
                rep = await c("run", {"max_us": 3_000_000, "timeout_s": 60})
                assert rep.get("reason") == "breakpoint", rep

            # the game stack lives in the window (&7497), so a snippet that maps bank 6 must not `ret` through it: MAP and UNMAP end with jp TRAP
            # snippets: map bank 6 / back, and the glue shape: map, ld a,type, call fillHull, unmap
            await c("memory_write", {"address": MAP, "data": hx([0x01, 0xC6, 0x7F, 0xED, 0x49, 0xC3, TRAP & 255, TRAP >> 8])})
            await c("memory_write", {"address": UNMAP, "data": hx([0x01, 0xC0, 0x7F, 0xED, 0x49, 0xC3, TRAP & 255, TRAP >> 8])})
            await c("memory_write", {"address": CALL, "data": hx([0x01, 0xC6, 0x7F, 0xED, 0x49, 0x3E, TYPE, 0xCD, 0x00, 0x40, 0x01, 0xC0, 0x7F, 0xED, 0x49, 0xC9])})
            await c("memory_write", {"address": INIT, "data": hx([0x01, 0xC6, 0x7F, 0xED, 0x49, 0xCD, 0x03, 0x40, 0x01, 0xC0, 0x7F, 0xED, 0x49, 0xC9])})
            await call(MAP)
            await c("memory_write", {"address": 0x4000, "data": hx(mod)})
            await c("memory_write", {"address": 0x6000, "data": hx(data)})
            await call(UNMAP)
            await call(INIT)
            for k in range(FRAMES):
                ang = 2 * math.pi * k / FRAMES
                await c("memory_write", {"address": VBUF, "data": hx(project(pts["points"], ang))})
                await c("memory_write", {"address": 0xA000, "data": hx([0x0F] * 8192)})
                await call(CALL)
                reg = await c("registers_get")
                bm = b""
                for o in range(0, 8192, 1024):
                    bm += bytes.fromhex((await c("memory_read", {"address": 0xA000 + o, "length": 1024}))["hex"])
                rows = []
                for y in range(128):
                    row = []
                    for bx in range(64):
                        b = bm[y * 64 + bx]
                        for px in range(4):
                            row.append(((b >> (7 - px)) & 1) << 1 | ((b >> (3 - px)) & 1))
                    rows.append(row)
                png(OUT / f"fill_{TYPE}_{k}.png", 256, 128, rows)
                print(f"frame {k}: angle {math.degrees(ang):5.1f}  drawn pixels {sum(1 for r in rows for v in r if v != 1)}  png work/elite128/fill_{TYPE}_{k}.png")


asyncio.run(main())

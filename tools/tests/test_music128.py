#!/usr/bin/env python3
"""The title music of the 128K build (src/elite128/musiquex.asm, hook in lasersights128.asm): it plays on the title screen only.

usage (from work/xray):  DISK128=disk/elite128.dsk PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I <absolute path>/tools/tests/test_music128.py
Boots the disk and samples the PSG registers (the AY block of a snapshot header, offsets 0x5B-0x6A) every 250 ms of emulated time on the title: the mixer (register 7) must leave
0x3F and the tone periods must change (the tune plays), musicState (address from work/elite128/c128.sym, written by check_src128.sh) must be >= 1 and the player must sit in the slot
of the code block in RAM bank 7. Then space (twice: the second title screen, then the commander page): the music stops (mixer 0x3F, musicState 0) and the slot holds the flight code
again, byte for byte NOTMUSIC.BIN of the disk. The snapshots are read as flat files (bank n at 0x100 + n * 0x4000), whatever RAM configuration was active when they were saved.
Prints ALL OK.
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import dskx  # noqa: E402

DISK = os.environ.get("DISK128", "disk/elite128.dsk")
SYM = (ROOT / "work/elite128/c128.sym").read_text()


def sym(name):
    m = re.search(rf"^{name}:\s*EQU\s*0x([0-9A-Fa-f]+)", SYM, re.M)
    assert m, f"{name} not in c128.sym (run tools/check_src128.sh)"
    return int(m.group(1), 16)


def bank(d, n, off, length=1):
    o = 0x100 + n * 0x4000 + off
    return d[o:o + length]


async def main():
    slot = sym("loc_604A") - 0x4A - 0xC000    # offset of the 4 KB slot in bank 7
    state = sym("musicState") - 0x8000        # the overlay on bankInit is in bank 2
    notmusic = dskx.read_files(dskx.load_sectors(Path(DISK) if Path(DISK).exists() else ROOT / "work/xray" / DISK))[(0, "NOTMUSIC.BIN")][128:128 + 0x1000]
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
                return Path(f"output/{name}.sna").read_bytes()

            await c("disk_insert", {"drive": "A", "path": DISK})
            await c("run", {"max_us": 4_000_000, "timeout_s": 60})
            await c("type_text", {"text": 'RUN"ELITE128\n', "wait": False})
            await c("run", {"max_us": 30_000_000, "timeout_s": 200})
            mixers, tones = [], set()
            for i in range(24):
                await c("run", {"max_us": 250_000, "timeout_s": 60})
                d = await snap("music128_title")
                ay = d[0x5B:0x6B]
                mixers.append(ay[7])
                tones.add((ay[0] | ay[1] << 8, ay[2] | ay[3] << 8, ay[4] | ay[5] << 8))
            on = bank(d, 2, state)[0]
            tick = bank(d, 7, slot, 0x1000).find(bytes([0xF5, 0xC5, 0xD5, 0xE5, 0xFD, 0xE5, 0xDD, 0xE5, 0x3A]))          # the first bytes of the tick: push af, bc, de, hl, iy, ix; ld a,(nn)
            player = tick >= 0
            print(f"title: musicState={on}, mixer values {sorted(set(mixers))}, {len(tones)} different tone settings, the tick is {'in the slot at +%04X' % tick if player else 'MISSING from the slot'} (bank 7)")
            ok = on >= 1 and player and any(m != 0x3F for m in mixers) and len(tones) >= 3
            for _ in range(2):
                await c("key_press", {"key": "space"})
                await c("run", {"max_us": 1_300_000, "timeout_s": 60})
                await c("key_release", {"key": "space"})
                await c("run", {"max_us": 12_000_000, "timeout_s": 120})
            d = await snap("music128_docked")
            on_after = bank(d, 2, state)[0]
            mixer_after = d[0x5B + 7]
            restored = bank(d, 7, slot, 0x1000) == notmusic
            print(f"docked: musicState={on_after}, mixer={mixer_after:02X}, slot {'restored (NOTMUSIC.BIN)' if restored else 'NOT restored'}")
            ok = ok and on_after == 0 and mixer_after == 0x3F and restored
            await c("screen_image", {"path": "output/music128_docked.png"})
            print("ALL OK" if ok else "FAILURES")


asyncio.run(main())

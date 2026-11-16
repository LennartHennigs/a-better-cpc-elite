#!/usr/bin/env python3
"""Look at the star occlusion (STAR_OCCLUDE in src/elite/commonxx.asm) in cpcxray: stars must not be drawn over the planet or sun disc.

usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_star_occlusion.py [off] [far] [sun]

Loads output/firebird_in_flight.sna (stock code), writes the two patched slots of the built COMMONXX (dustPlotPixel..ClearBitmap and dust70..+16; with `off`
nothing is written, the stock game), runs a few seconds in flight and saves output/stars_on.png (or stars_off.png). With `far` the planet is pushed
away first (as tools/tests/test_flight_hull.py does), so the view is open space and the stars must still be there.
"""
import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
OFF = "off" in sys.argv
FAR = "far" in sys.argv
SUN = "sun" in sys.argv   # the sun (posDataSun &1C26) straight ahead, the planet (posDataPlanet &1C2F) moved far to the side


def build():
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DENHANCED", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], check=True, capture_output=True)
        labels = {l.split()[0].rstrip(":"): int(l.split()[-1], 16) for l in sym.read_text().splitlines() if "EQU" in l}
        return out.read_bytes(), labels


async def main():
    new, lab = build()
    base = 0x1A40
    slots = [(lab["dustPlotPixel"], lab["ClearBitmap"]), (lab["dust70"], lab["dust70"] + 16)]
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

            await c("sna_load", {"path": "output/firebird_in_flight.sna"})
            if not OFF:
                for lo, hi in slots:
                    await c("memory_write", {"address": lo, "data": new[lo - base:hi - base].hex()})
            await c("run", {"max_us": 6_000_000, "timeout_s": 60})
            if FAR:
                await c("memory_write", {"address": 0x1C2F, "data": "00 FF 80  00 00 00  B6 7C 01"})   # posDataPlanet: far to the side (x = -&FF00; `sun` uses &7000 for a planet that stays in the view edge) (&1A40+7 is the scratch entity, not the planet)
            if SUN:
                await c("memory_write", {"address": 0x1C26, "data": "00 00 00  00 00 00  00 00 03"})
                await c("memory_write", {"address": 0x1C2F, "data": "00 70 80  00 00 00  B6 7C 01"})
            await c("run", {"max_us": 3_000_000, "timeout_s": 60})
            print(await c("screen_image", {"path": "output/stars_%s%s.png" % ("off" if OFF else "on", ("_far" if FAR else "") + ("_sun" if SUN else ""))}))


asyncio.run(main())

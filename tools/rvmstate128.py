#!/usr/bin/env python3
"""Convert an RVM (Retro Virtual Machine) .rvmstate file to a CPC 128K .sna snapshot (v2) that cpcxray can load.

usage: python3 -I tools/rvmstate.py IN.rvmstate OUT.sna [CURCFG_ADDR]
Format (found by inspection): zlib of a JSON-like text. snap.ram holds eight '<base64 of a zlib block>' entries = RAM banks 0-7 (16 KB each), snap.cpu the Z80
registers (af, bc, de, hl, ix, iy, sp, pc, shadow set, imodew, iffw), snap.crtc the 18 register values, snap.gateArray the multi-configuration byte.
RVM stores no RAM-configuration byte, so it is taken from the game variable curCfg (src/elite128/commonxx.asm; default address 0x9864, pass another one after
a size change) when that holds C0..C7, else C1. Inks come out as one default colour (not needed to debug).
"""
import base64
import re
import struct
import sys
import zlib

src, dst = sys.argv[1:3]
t = zlib.decompress(open(src, "rb").read()).decode("latin1")
i = t.index("ram : {")
banks = [zlib.decompress(base64.b64decode(b)) for b in re.findall(r"<([^>]*)>", t[i:t.index("upd765", i)])]
assert len(banks) == 8 and all(len(b) == 0x4000 for b in banks), [len(b) for b in banks]
ram = b"".join(banks)
cpu = {k: int(v) for k, v in re.findall(r"\b([a-z]+) : (\d+)", t[t.index("cpu : {"):t.index("level :")])}
crtc = [int(x) for x in re.findall(r"\d+", t[t.index("crtc : {") + 8:t.index("ma :")])][:18]
crtc = [crtc[17]] + crtc[:17]      # RVM lists R1..R17 first and R0 last
ga = int(re.search(r"gateArray : (\d+)", t).group(1))
addr = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x9864
cfg = ram[addr]
if not 0xC0 <= cfg <= 0xC7:
    cfg = 0xC1
h = bytearray(0x100)
h[:8] = b"MV - SNA"
h[0x10] = 2


def w16(o, v):
    h[o:o + 2] = struct.pack("<H", v & 0xFFFF)


w16(0x11, cpu["af"]); w16(0x13, cpu["bc"]); w16(0x15, cpu["de"]); w16(0x17, cpu["hl"])
h[0x19] = cpu["ir"] & 0xFF                  # R
h[0x1A] = (cpu["ir"] >> 8) & 0xFF           # I
h[0x1B] = h[0x1C] = 1 if cpu["iffw"] & 0xFF else 0
w16(0x1D, cpu["ix"]); w16(0x1F, cpu["iy"]); w16(0x21, cpu["sp"]); w16(0x23, cpu["pc"])
h[0x25] = cpu["imodew"] & 3
w16(0x26, cpu["afp"]); w16(0x28, cpu["bcp"]); w16(0x2A, cpu["dep"]); w16(0x2C, cpu["hlp"])
for k in range(17):
    h[0x2F + k] = 0x54
h[0x40] = ga & 0xFF
h[0x41] = cfg
h[0x42] = 12
for k, v in enumerate(crtc):
    h[0x43 + k] = v & 0xFF
h[0x6B:0x6D] = struct.pack("<H", 128)
open(dst, "wb").write(bytes(h) + ram)
print("%s: pc=%04X sp=%04X cfg=%02X R12=%d" % (dst, cpu["pc"], cpu["sp"], cfg, crtc[12]))

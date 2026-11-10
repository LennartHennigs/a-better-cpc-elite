#!/usr/bin/env python3
"""List code that forms a pc-relative address (add/sub rX,pc,#imm) pointing at given file offsets or address ranges.
usage: arc_xref.py IMAGE.bin ADDR [ADDR...]   (addresses in hex, the image base is &8000; matches target..target+3)"""
import struct, sys
d = open(sys.argv[1], 'rb').read()
want = [int(x, 16) for x in sys.argv[2:]]
for o in range(0, 0x51ed8, 4):
    w = struct.unpack_from('<I', d, o)[0]
    if w & 0x0FFF0000 in (0x028F0000, 0x024F0000):
        v = w & 0xFF; r = ((w >> 8) & 0xF) * 2
        imm = ((v >> r) | (v << (32 - r))) & 0xFFFFFFFF if r else v
        t = 0x8000 + o + 8 + (imm if w & 0x00800000 else -imm)
        for a in want:
            if a <= t <= a + 3:
                print(f'{0x8000+o:05X} -> {t:05X} (wanted {a:05X}) rd=r{(w>>12)&15}')

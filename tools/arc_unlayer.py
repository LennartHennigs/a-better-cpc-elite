#!/usr/bin/env python3
"""Peel the XOR layers of ArcElite's `ilite` (see docs/_arcelite.md): arc_unlayer.py IN OUT.
Each layer is `mov r0,#&8000 / sub r1,pc,#12 / mov r3,#K / ... eor / add r3,r3,#S / ... b prev`, decrypting [&8000, layer start)."""
import struct, sys

def imm(w):  # ARM modified immediate
    v = w & 0xFF; r = ((w >> 8) & 0xF) * 2
    return ((v >> r) | (v << (32 - r))) & 0xFFFFFFFF if r else v

d = bytearray(open(sys.argv[1], 'rb').read())
base = 0x8000
w = lambda a: struct.unpack_from('<I', d, a - base)[0]
# the outermost layer is the last `mov r0,#0x8000` (e3a00902) in the file
a = None
for o in range(len(d) - 4, 0, -4):
    if struct.unpack_from('<I', d, o)[0] == 0xE3A00902:
        a = base + o; break
layers = 0
while a is not None and w(a) == 0xE3A00902 and w(a + 4) == 0xE24F100C:
    k = imm(w(a + 8)); step = imm(w(a + 0x18))
    assert w(a + 0xC) == 0xE5902000 and w(a + 0x14) == 0xE4802004, hex(a)
    print(f'layer at {a:X}: key {k:#x} step {step:#x}')
    for o in range(0, a - base, 4):
        struct.pack_into('<I', d, o, struct.unpack_from('<I', d, o)[0] ^ k)
        k = (k + step) & 0xFFFFFFFF
    layers += 1
    # the layer ends with a self-patched branch; the next layer starts 0x48 bytes earlier in these builds
    nxt = None
    for cand in range(a - 0x200, a, 4):
        if w(cand) == 0xE3A00902 and w(cand + 4) == 0xE24F100C:
            nxt = cand
    a = nxt
print(layers, 'layers')
open(sys.argv[2], 'wb').write(d)

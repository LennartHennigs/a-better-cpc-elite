#!/usr/bin/env python3
"""Disassemble a flat ARM (26-bit era) binary: armdis.py FILE BASE START END  (hex). Needs capstone (uv run --with capstone)."""
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
f, base, a, b = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4], 16)
d = open(f, 'rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
for o in range(a - base, b - base, 4):
    w = d[o:o + 4]
    i = next(md.disasm(w, base + o), None)
    print(f'{base+o:08X}  {w[::-1].hex()}  ' + (f'{i.mnemonic} {i.op_str}' if i else '???'))

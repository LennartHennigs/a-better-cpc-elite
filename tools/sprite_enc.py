#!/usr/bin/env python3
"""Turn ASCII pixel art into Mode 1 sprite bytes for sjasmplus.

usage: python3 -I tools/sprite_enc.py ART.txt LABEL [LABEL_MIRRORED] > OUT.asm

ART.txt: lines starting with '#' are comments; every other line is one row, one character per pixel ('.' pen 0, '1' '2' '3' pen 1-3), 16 pixels (4 bytes) wide.
CPC Mode 1: a byte holds 4 pixels; pixel p (0 = leftmost) of pen v has bit 7-p = high bit of v and bit 3-p = low bit of v. So pen 2 is %1111_0000 for four pixels and pen 1
is %0000_1111. The optional second label gets the art mirrored left to right.
"""
import sys

rows = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
assert rows and all(len(r) == 16 for r in rows), "rows must be 16 pixels wide"


def encode(row):
    out = []
    for b in range(4):
        byte = 0
        for p in range(4):
            c = row[b * 4 + p]
            v = 0 if c == "." else int(c)
            byte |= ((v >> 1) & 1) << (7 - p) | (v & 1) << (3 - p)
        out.append(byte)
    return out


for label, mirror in [(sys.argv[2], False)] + ([(sys.argv[3], True)] if len(sys.argv) > 3 else []):
    print(f"{label}:   ; {len(rows)} rows of 4 bytes" + (", mirrored" if mirror else ""))
    for r in rows:
        print("    db " + ",".join("0x%02X" % b for b in encode(r[::-1] if mirror else r)) + "   ; " + (r[::-1] if mirror else r))

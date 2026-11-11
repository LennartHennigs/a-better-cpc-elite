#!/usr/bin/env python3
"""Tile cropped, halved copies of cpcxray screenshots into one PNG (pure Python, no PIL).

usage: python3 -I tools/png_montage.py OUT.png COLS X0 Y0 X1 Y1 IN1.png IN2.png ...
Crops each input to [X0,X1) x [Y0,Y1) (screen pixels of the 768x544 screenshot), keeps every second pixel, tiles COLS per row.
"""
import struct
import sys
import zlib


def read_png(path):
    d = open(path, "rb").read()
    pos, idat = 8, b""
    while pos < len(d):
        n = struct.unpack(">I", d[pos:pos + 4])[0]
        t, b = d[pos + 4:pos + 8], d[pos + 8:pos + 8 + n]
        pos += 12 + n
        if t == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", b[:10])
        elif t == b"IDAT":
            idat += b
    assert bd == 8 and ct in (2, 6), (bd, ct)
    bpp = 3 if ct == 2 else 4
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev = [], bytearray(stride)
    p = 0
    for _ in range(h):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b_ = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b_) & 255
            elif f == 3:
                line[i] = (line[i] + ((a + b_) >> 1)) & 255
            elif f == 4:
                pa, pb, pc = abs(b_ - c), abs(a - c), abs(a + b_ - 2 * c)
                pr = a if pa <= pb and pa <= pc else (b_ if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(line)
        prev = line
    return w, h, bpp, rows


def write_png(path, w, h, rows):
    raw = b"".join(b"\0" + bytes(r) for r in rows)
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


out, cols = sys.argv[1], int(sys.argv[2])
x0, y0, x1, y1 = map(int, sys.argv[3:7])
files = sys.argv[7:]
tw, th = (x1 - x0) // 2, (y1 - y0) // 2
nrows = -(-len(files) // cols)
canvas = [bytearray(tw * cols * 3) for _ in range(th * nrows)]
for k, f in enumerate(files):
    w, h, bpp, rows = read_png(f)
    cx, cy = (k % cols) * tw, (k // cols) * th
    for y in range(th):
        src = rows[y0 + 2 * y]
        for x in range(tw):
            o = (x0 + 2 * x) * bpp
            canvas[cy + y][(cx + x) * 3:(cx + x) * 3 + 3] = src[o:o + 3]
write_png(out, tw * cols, th * nrows, canvas)
print("wrote", out, tw * cols, "x", th * nrows)

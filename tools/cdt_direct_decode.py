#!/usr/bin/env python3
"""Decode the direct-recording block (TZX/CDT block 0x15) of Elite.cdt into the blocks ELITE1's custom loader reads.

ELITE1 (the 512 byte binary at &3B00) reads the tape with its own routine: each pulse is one bit (a pulse longer than
63 loop passes is a 1, MSB first), a block is a run of pilot bytes P, then ~P, then P, then 0x0108+K bytes: 256 bytes
of data, block number, destination address (lo, hi), a count A, then A bytes up to a small code stub, and an XOR
checksum of everything before it. The checksum also gives the next block's length (K = (chk & 7) + 1) and, after the
first block, the next pilot byte ((chk & 7F) | 8). Each block's 256 bytes are copied to its destination and the stub
runs (normally `jp &3B41`, to read the next block).

The direct recording samples the tape at 1313 T per sample and every pulse is exactly 1 sample (0) or 2 samples (1).

usage: cdt_direct_decode.py Elite.cdt OUTDIR   (writes blocks.txt and image.bin, a 64K image of the 256 byte pages)"""
import sys
from pathlib import Path


def direct_block(d):
    o = 10
    while o < len(d):
        t = d[o]
        o += 1
        if t == 0x11:
            o += 18 + (d[o + 15] | d[o + 16] << 8 | d[o + 17] << 16)
        elif t == 0x10:
            o += 4 + int.from_bytes(d[o + 2:o + 4], "little")
        elif t == 0x20:
            o += 2
        elif t == 0x15:
            n = d[o + 5] | d[o + 6] << 8 | d[o + 7] << 16
            return int.from_bytes(d[o:o + 2], "little"), d[o + 8:o + 8 + n], d[o + 4]
        else:
            raise SystemExit(f"unknown block {t:#x}")
    raise SystemExit("no direct recording block")


def pulse_bits(blk, used):
    bits = [(b >> k) & 1 for b in blk for k in range(7, -1, -1)]
    bits = bits[:len(bits) - 8 + used]
    runs, cur, n = [], bits[0], 1
    for x in bits[1:]:
        if x == cur:
            n += 1
        else:
            runs.append(n)
            cur, n = x, 1
    return "".join("1" if r >= 2 else "0" for r in runs)


def find_sync(s, i, p):
    pat = format(p, "08b") * 5
    m = s.find(pat, i)
    while m >= 0:
        j = m
        while s[j:j + 8] == format(p, "08b"):
            j += 8
        if s[j:j + 8] == format(~p & 255, "08b") and s[j + 8:j + 16] == format(p, "08b"):
            return m, j + 16
        m = s.find(pat, m + 1)
    return -1, -1


def decode(s):
    p, k, pos, blocks = 0x0F, 8, 0, []
    while True:
        a, b = find_sync(s, pos, p)
        if a < 0:
            return blocks
        n = 0x0108 + k
        if b + 8 * n > len(s):
            return blocks
        by = bytes(int(s[b + 8 * i:b + 8 * i + 8], 2) for i in range(n))
        x = 0
        for v in by[:-1]:
            x ^= v
        if x != by[-1]:
            raise SystemExit(f"checksum error in block {len(blocks)}")
        blocks.append((p, k, by))
        pos = b + 8 * n
        if len(blocks) == 1:
            p = (by[-1] & 0x7F) | 8
        k = (by[-1] & 7) + 1


def main():
    d = Path(sys.argv[1]).read_bytes()
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    tpp, blk, used = direct_block(d)
    blocks = decode(pulse_bits(blk, used))
    mem, lines = bytearray(65536), []
    for i, (p, k, by) in enumerate(blocks):
        dest = by[257] | by[258] << 8
        mem[dest:dest + 256] = by[:256]
        entry = 260 + by[259]
        lines.append(f"{i:3d} pilot {p:02X} len {len(by)} index {by[256]} dest {dest:04X} stub {by[entry:entry + 4].hex()} chk {by[-1]:02X}")
    (out / "blocks.txt").write_text("\n".join(lines) + "\n")
    (out / "image.bin").write_bytes(bytes(mem))
    print(f"{len(blocks)} blocks, all checksums good; wrote {out}/blocks.txt and image.bin")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Byte budget for the 128K plan (docs: plan "Phase 0b"): what sits in the stock screen page and how much room a relocated layout has.

usage: python3 -I tools/gap_map.py [IMAGE]       (default work/stock_mem_image.bin, the three stock code files laid out in a 64K image)

Reports, from the 64K image:
  - the screen page &C000-&FFFF in its 8 chunks of 2 KB (one per scanline of a character row): the 512-byte gap (rows 24-31) and the visible
    part (rows 0-23, 1536 bytes), with the runs of non-zero bytes (code and tables hiding in "blank" screen bytes);
  - the block &3F60-&7D5D that Fessor's relocation (and the double-buffer branch) moves up to &C000, and what is left of the 16 KB there;
  - the free tail at the end of COMMONXX and the zero runs of at least 16 bytes in &1A40-&9FFF.
It only reads; nothing is written.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
img = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "work/stock_mem_image.bin"
mem = img.read_bytes()
if len(mem) != 0x10000:
    sys.exit(f"{img}: expected 65536 bytes, got {len(mem)}")


def runs(lo, hi, zero, minlen=1):
    """Maximal runs in [lo, hi) of zero (zero=True) or non-zero bytes, as (start, end)."""
    out, a = [], None
    for i in range(lo, hi):
        hit = (mem[i] == 0) == zero
        if hit and a is None:
            a = i
        if not hit and a is not None:
            if i - a >= minlen:
                out.append((a, i))
            a = None
    if a is not None and hi - a >= minlen:
        out.append((a, hi))
    return out


print(f"image {img.relative_to(ROOT) if img.is_relative_to(ROOT) else img}")
print("\nScreen page &C000-&FFFF, per 2 KB chunk (non-zero bytes in the visible rows 0-23 / in the gap rows 24-31):")
tot_vis = tot_gap = 0
for c in range(8):
    base = 0xC000 + c * 0x800
    vis = sum(1 for i in range(base, base + 0x600) if mem[i])
    gap = sum(1 for i in range(base + 0x600, base + 0x800) if mem[i])
    tot_vis += vis
    tot_gap += gap
    print(f"  chunk {c}  &{base:04X}-&{base + 0x7FF:04X}  visible {vis:4d} of 1536   gap {gap:3d} of 512")
print(f"  total non-zero: visible {tot_vis}, gap {tot_gap}  => {tot_vis + tot_gap} bytes of code/tables/charset live in the screen page")

print("\nNon-zero runs of 8 or more bytes in the screen page:")
for a, b in runs(0xC000, 0x10000, False, 8):
    print(f"  &{a:04X}-&{b - 1:04X}  {b - a:4d} bytes")

print("\nRelocated block &3F60-&7D5D (Fessor's 'AdrChangeStart'..'Endofblock'):")
size = 0x7D5E - 0x3F60
print(f"  {size} bytes go to bank 7 at &C000 (the page holds 16384): {16384 - size} bytes are left for new code (glue, element table, hooks)")
print(f"  COMMON2X's {tot_vis + tot_gap} bytes stay where they are, in the gaps of the screen page, which becomes the &4000 page (identical copy in banks 1 and 3, read-only)")

print("\nFree space in COMMONXX (zero runs of at least 16 bytes in &1A40-&9FFF), largest first:")
z = sorted(runs(0x1A40, 0xA000, True, 16), key=lambda r: r[0] - r[1])
for a, b in z[:12]:
    print(f"  &{a:04X}-&{b - 1:04X}  {b - a:4d} bytes")
print(f"  total of those runs: {sum(b - a for a, b in z)} bytes (includes buffers that are zero at load time, so not all of it is free)")

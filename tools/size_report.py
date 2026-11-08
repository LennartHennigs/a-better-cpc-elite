#!/usr/bin/env python3
"""Report how many bytes of the free tails an assembled build uses, against the stock files.

usage: size_report.py COMMONXX.bin LARGEAXX.bin [STOCK_DIR]       (STOCK_DIR defaults to work/bin_stock)

Free regions (docs/_architecture.md, "Dynamic labels" and docs/_missions.md section 4):
  COMMONXX tail   &9D9E-&9FFF  610 bytes, flight time. The stack sits at &A000 in some states and pushes at &9FFE-&9FFF, so
                  the top STACK_RESERVE bytes are counted as not available (default 256, until the depth is measured).
  LARGEAXX tail   &1714-&1A3F  812 bytes, docked only (reloaded from disk at every docking).
Also checks that nothing outside those tails differs from stock except the listed allowed patches, and prints the
differing ranges so a mission's footprint (hooks in existing code) is visible.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STACK_RESERVE = 256
REGIONS = {"COMMONXX": (0x1A40, 0x9D9E, 0xA000), "LARGEAXX": (0x0840, 0x1714, 0x1A40)}


def used(data, base, start, end):
    """bytes from start up to the last non-zero byte before end (end exclusive)"""
    seg = data[start - base:end - base]
    last = max((i for i, b in enumerate(seg) if b), default=-1)
    return last + 1


def diff_ranges(a, b, base, skip):
    out, i = [], 0
    n = min(len(a), len(b))
    while i < n:
        if a[i] != b[i] and not (skip[0] <= base + i < skip[1]):
            j = i
            while j + 1 < n and a[j + 1] != b[j + 1]:
                j += 1
            out.append((base + i, base + j))
            i = j + 1
        else:
            i += 1
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    stock_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "work" / "bin_stock"
    for name, path in (("COMMONXX", sys.argv[1]), ("LARGEAXX", sys.argv[2])):
        base, tail, end = REGIONS[name]
        new = Path(path).read_bytes()
        old = (stock_dir / f"{name}.BIN").read_bytes()
        reserve = STACK_RESERVE if name == "COMMONXX" else 0
        size = end - tail
        u = used(new, base, tail, end)
        print(f"{name}: file {len(new)} bytes (stock {len(old)})")
        print(f"  tail &{tail:04X}-&{end - 1:04X}: {size} bytes, used {u}, free {size - u}"
              + (f" ({size - u - reserve} after the {reserve}-byte stack reserve)" if reserve else ""))
        if name == "LARGEAXX":   # the save key is the 0x68 bytes at EquipShip (docs/_savegame.md): changing them breaks every old save
            ok = new[0x2BE:0x2BE + 0x68] == old[0x2BE:0x2BE + 0x68]
            print("  save key window (file offset &2BE, &68 bytes):", "unchanged" if ok else "CHANGED: old saves will not load")
        r = diff_ranges(new, old, base, (tail, end))
        patched = sum(b - a + 1 for a, b in r)
        print(f"  changed outside the tail: {patched} bytes in {len(r)} ranges"
              + (": " + ", ".join(f"&{a:04X}-&{b:04X}" for a, b in r[:12]) if r else ""))


main()

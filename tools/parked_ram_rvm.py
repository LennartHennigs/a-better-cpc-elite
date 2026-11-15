#!/usr/bin/env python3
"""Hand test of the parked firmware RAM in RVM (tools/test_parked_ram.py, TODO.md "Parked firmware RAM") through RVM's own .rvmstate files.

An .rvmstate is zlib-compressed text; its `ram : { ... }` holds the 16 KB banks as <base64(zlib(bank))>. The banks are listed 1, 2, 3, 4..7 and finally the one labelled `0 :`, which
is the bank at &0000 (the game's COMMONXX at &1A40 sits in it). Bank 0 holds &0000-&3FFF, bank 2 &8000-&BFFF.

  python3 -I tools/parked_ram_rvm.py mark IN.rvmstate OUT.rvmstate [MARK]   # MARK (default AA) into every zero run of 16+ bytes of the parked block: low memory &0040-&1A3F in the
                                                                           # flight layout, or &A600-&BFFF when LARGEAXX is resident (docked layout); runs go to work/parked_ram/rvm_runs.txt
  python3 -I tools/parked_ram_rvm.py check STATE.rvmstate [MARK]            # marker bytes still intact in both places, per run
"""
import base64
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "work/parked_ram/rvm_runs.txt"
BANK_RE = re.compile(r"<([A-Za-z0-9+/=]+)>")


def load(path):
    text = zlib.decompress(Path(path).read_bytes()).decode("latin-1")
    lines = text.split("\n")
    start = next(i for i, l in enumerate(lines) if l.strip() == "ram : {")
    idx = [i for i in range(start + 1, start + 12) if BANK_RE.search(lines[i])]
    assert len(idx) == 8, idx
    banks = {}
    for n, i in enumerate(idx):          # list order 1,2,3,4,5,6,7, then the entry labelled `0 :`
        bank = 0 if n == 7 else n + 1
        banks[bank] = (i, bytearray(zlib.decompress(base64.b64decode(BANK_RE.search(lines[i]).group(1)))))
    return lines, banks


def mem(banks, addr, n):
    b = banks[addr >> 14][1]
    o = addr & 0x3FFF
    return b[o:o + n]


def zero_runs(img, base, minlen=16):
    runs, i = [], 0
    while i < len(img):
        if img[i] == 0:
            j = i
            while j < len(img) and img[j] == 0:
                j += 1
            if j - i >= minlen:
                runs.append((base + i, j - i))
            i = j
        else:
            i += 1
    return runs


def is_docked(banks):
    """LARGEAXX resident (docked layout) or not: the firmware jumpblock `C3 40 1D` at &BDF4 means the parked copy is at &A600."""
    return bytes(mem(banks, 0xBDF4, 3)) == b"\xC3\x40\x1D"


mode = sys.argv[1]
if mode == "mark":
    src, dst = sys.argv[2], sys.argv[3]
    mark = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0xAA
    lines, banks = load(src)
    docked = is_docked(banks)
    base = 0xA600 if docked else 0x0040
    runs = zero_runs(bytes(mem(banks, base, 0x1A00)), base)
    for a, l in runs:
        banks[a >> 14][1][(a & 0x3FFF):(a & 0x3FFF) + l] = bytes([mark]) * l
    for bank in {a >> 14 for a, _ in runs}:
        i, data = banks[bank]
        enc = base64.b64encode(zlib.compress(bytes(data), 9)).decode()
        lines[i] = re.sub(r"<[A-Za-z0-9+/=]+>", "<" + enc + ">", lines[i], count=1)
    Path(dst).write_bytes(zlib.compress("\n".join(lines).encode("latin-1"), 6))
    RUNS.parent.mkdir(exist_ok=True)
    RUNS.write_text("\n".join(f"{a:04X} {l}" for a, l in runs))
    print(f"{dst}: parked block at &{base:04X} ({'docked' if docked else 'flight'} layout), {len(runs)} runs, {sum(l for _, l in runs)} bytes set to {mark:02X}")
else:
    lines, banks = load(sys.argv[2])
    mark = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0xAA
    runs = [(int(a, 16), int(l)) for a, l in (x.split() for x in RUNS.read_text().splitlines())]
    delta = 0xA600 - 0x0040
    print("layout now:", "docked (parked block at &A600)" if is_docked(banks) else "flight (parked block at &0040)")
    for tag, shift in (("at the marked place", 0), ("at the other half", delta if runs[0][0] < 0xA600 else -delta)):
        bad = [(a, l, [k for k in range(a, a + l) if mem(banks, a + shift + (k - a), 1)[0] != mark]) for a, l in runs]
        total = sum(len(b) for _, _, b in bad)
        print(f"{tag}: {total} of {sum(l for _, l in runs)} marker bytes changed")
        if shift == 0:
            for a, l, b in sorted(bad, key=lambda x: -x[1])[:10]:
                print(f"   {a:04X} {l:4d}  changed {len(b):4d}")

#!/usr/bin/env python3
"""Read a Retro Virtual Machine (RVM 2.1) state file (*.rvmstate): CPU registers, the 64K RAM image, the ship slots.

usage:  python3 -I tools/rvmstate.py STATE [--regs] [--ram OUT.bin] [--slots]
  --regs       Z80 registers and the game's mode bytes
  --ram OUT    the 64 KB CPU view (address = file offset), assuming the default RAM configuration (pages 0-3 in order)
  --slots      the seven entity slots at &1A40 (39 bytes each): position, flags, blueprint address, orientation words
Format notes: docs/_build.md "RVM state files". Read-only; with no option it prints --regs and --slots.
"""
import base64
import re
import sys
import zlib

SLOT0, SLOT_SIZE, SLOTS = 0x1A40, 0x27, 7   # sEntityxlo; lookforFreeSlot steps 0x27 over 6 more slots after slot 0


def load(path):
    """the state text (zlib-compressed; not JSON: no quotes on keys, arrays as `1, 2, 0 : first`)"""
    return zlib.decompress(open(path, "rb").read()).decode("latin1")


def regs(text):
    block = re.search(r"\n    cpu : \{(.*?)\n    \}", text, re.S).group(1)
    return {k: int(v) for k, v in re.findall(r"(\w+) : (\d+)", block)}


def ram_pages(text):
    """the eight 16 KB RAM pages in index order. Each page is `<base64 of a zlib stream>`; the serializer prints an array's
    elements 1..n first and element 0 last (`0 : <...>`), so page 0 is the LAST one in the file"""
    start = text.index("\n    ram : {")
    body = text[start:text.index("\n    },", start)]
    printed = [zlib.decompress(base64.b64decode(b)) for b in re.findall(r"<([A-Za-z0-9+/=]+)>", body)]
    assert len(printed) == 8 and all(len(p) == 0x4000 for p in printed), "unexpected RAM layout"
    return [printed[-1]] + printed[:-1]


def ram64k(text):
    return b"".join(ram_pages(text)[:4])


def word(lo, hi):
    """sign-magnitude 16-bit: bit 15 is the sign"""
    v = lo | hi << 8
    return -(v & 0x7FFF) if v & 0x8000 else v


def slots(ram):
    for k in range(SLOTS):
        s = ram[SLOT0 + k * SLOT_SIZE:SLOT0 + (k + 1) * SLOT_SIZE]
        pos = [-(s[i] | s[i + 1] << 8) if s[i + 2] & 0x80 else s[i] | s[i + 1] << 8 for i in (0, 3, 6)]
        vec = [word(s[9 + 2 * i], s[10 + 2 * i]) / 0x7FFF for i in range(9)]
        yield k, SLOT0 + k * SLOT_SIZE, s[34], s[35] | s[36] << 8, pos, vec, s[27]


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    text = load(args[0])
    opts = args[1:]
    if "--ram" in opts:
        out = opts[opts.index("--ram") + 1]
        open(out, "wb").write(ram64k(text))
        print("wrote", out)
    if "--regs" in opts or not opts:
        r = regs(text)
        print("  ".join(f"{k}={r[k]:04X}" for k in ("pc", "sp", "af", "bc", "de", "hl", "ix", "iy") if k in r))
    if "--slots" in opts or not opts:
        ram = ram64k(text)
        print("slot  addr  flags  blueprint  x, y, z (sign-magnitude)   speed  nose/roof/side words (1.0 = &7FFF)")
        for k, addr, flags, bp, pos, vec, speed in slots(ram):
            if flags or bp:
                print(f"{k:3}  {addr:04X}   {flags:02X}     {bp:04X}     {pos}   {speed:3}   "
                      + " ".join(f"{v:+.2f}" for v in vec))


if __name__ == "__main__":
    main()

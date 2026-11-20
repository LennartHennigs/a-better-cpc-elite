#!/usr/bin/env python3
"""Read a Retro Virtual Machine (RVM 2.1) state file (*.rvmstate): CPU registers, the 64K RAM image, the ship slots, a snapshot.

usage:  python3 -I tools/rvmstate.py STATE [--regs] [--ram OUT.bin] [--slots] [--sna OUT.sna [--curcfg [ADDR]]]
  --regs       Z80 registers
  --ram OUT    the 64 KB CPU view (address = file offset), assuming the default RAM configuration (pages 0-3 in order)
  --slots      the seven entity slots at &1A40 (39 bytes each): position, flags, blueprint address, orientation words
  --sna OUT    a standard .sna snapshot (version 3, 128 KB RAM) that cpcxray (`sna_load`) or any emulator loads: the game resumes
               exactly where the state was saved, mid-frame if it was paused there. Registers, Gate Array (palette, mode, ROM
               switches), CRTC, PPI, PSG and all eight RAM pages come from the state; the RAM configuration is not in the state
               and is written as 0. Not carried over: disk, tape, timers, the interrupt counter.
  --curcfg [ADDR]  with --sna, for a 128K game state: take the RAM configuration (&C0-&C7) from the game variable curCfg, at ADDR or, without
               it, at the label's address in work/elite128/c128.sym (tools/check_src128.sh writes it). Without this a 128K state loads with the wrong banks.
Format notes: docs/_build.md "RVM state files". Read-only; with no option it prints --regs and --slots. Run it with `python3 -I`.
"""
import base64
import re
import sys
import zlib
from pathlib import Path

SLOT0, SLOT_SIZE, SLOTS = 0x1A40, 0x27, 7   # sEntityxlo; lookforFreeSlot steps 0x27 over 6 more slots after slot 0

# hardware ink number -> (red, green, blue) level 0, 1, 2 (the 27 colours of the Gate Array)
HW_INKS = {
    0x14: (0, 0, 0), 0x04: (0, 0, 1), 0x15: (0, 0, 2), 0x1C: (1, 0, 0), 0x18: (1, 0, 1), 0x1D: (1, 0, 2), 0x0C: (2, 0, 0),
    0x05: (2, 0, 1), 0x0D: (2, 0, 2), 0x16: (0, 1, 0), 0x06: (0, 1, 1), 0x17: (0, 1, 2), 0x1E: (1, 1, 0), 0x00: (1, 1, 1),
    0x1F: (1, 1, 2), 0x0E: (2, 1, 0), 0x07: (2, 1, 1), 0x0F: (2, 1, 2), 0x12: (0, 2, 0), 0x02: (0, 2, 1), 0x13: (0, 2, 2),
    0x1A: (1, 2, 0), 0x19: (1, 2, 1), 0x1B: (1, 2, 2), 0x0A: (2, 2, 0), 0x03: (2, 2, 1), 0x0B: (2, 2, 2),
}


def load(path):
    """the state text (zlib-compressed; not JSON: no quotes on keys, arrays as `1, 2, 0 : first`)"""
    return zlib.decompress(open(path, "rb").read()).decode("latin1")


def regs(text):
    block = re.search(r"\n    cpu : \{(.*?)\n    \}", text, re.S).group(1)
    return {k: int(v) for k, v in re.findall(r"(\w+) : (\d+)", block)}


def scalar(text, key):
    """a top-level number of `snap` (`gateArray : 141`)"""
    return int(re.search(r"\n    %s : (\d+)" % key, text).group(1))


def array(text, key):
    """the numbers of a `snap` array in index order. The serializer prints elements 1..n first and element 0 last (`0 : value`);
    named keys that follow the elements (the CRTC's `output`, `r`, ...) end the array"""
    start = text.index("\n    %s : {" % key) + 1
    items, first = [], None
    for line in text[start:].split("\n")[1:]:
        m = re.fullmatch(r"\s*(\d+),?", line)
        if m:
            items.append(int(m.group(1)))
            continue
        m = re.fullmatch(r"\s*0 : (\d+),?", line)
        if m:
            first = int(m.group(1))
        break
    return [first] + items


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


def hardware_ink(rgb):
    """the Gate Array ink number whose colour is nearest to an RVM 24-bit RGB value (RVM's levels sit near 0, 127 and 243)"""
    chan = (rgb >> 16 & 255, rgb >> 8 & 255, rgb & 255)
    return min(HW_INKS, key=lambda k: sum((c - 127.5 * lv) ** 2 for c, lv in zip(chan, HW_INKS[k])))


def sna(text, cfg=0):
    """a version 3 snapshot with 128 KB of RAM. Header layout: CPCWiki "Snapshot Format Version 3" (offsets in the comments)"""
    r = regs(text)
    h = bytearray(0x100)
    h[0:8] = b"MV - SNA"
    h[0x10] = 3

    def put16(off, v):
        h[off], h[off + 1] = v & 255, v >> 8 & 255
    for off, key in ((0x11, "af"), (0x13, "bc"), (0x15, "de"), (0x17, "hl")):   # F A, C B, E D, L H
        put16(off, r[key])
    h[0x19], h[0x1A] = r["ir"] & 255, r["ir"] >> 8 & 255                          # R, I
    h[0x1B], h[0x1C] = r["iffw"] & 255, r["iffw"] >> 8 & 255                      # IFF1, IFF2
    put16(0x1D, r["ix"])
    put16(0x1F, r["iy"])
    put16(0x21, r["sp"])
    put16(0x23, r["pc"])
    h[0x25] = r["imodew"] & 255                                                    # interrupt mode
    for off, key in ((0x26, "afp"), (0x28, "bcp"), (0x2A, "dep"), (0x2C, "hlp")):
        put16(off, r[key])
    h[0x2E] = scalar(text, "penS")                                                 # selected pen
    pens = array(text, "palette")
    for i in range(16):
        h[0x2F + i] = hardware_ink(pens[i])                                        # pen 0-15
    h[0x3F] = hardware_ink(scalar(text, "border"))                                 # border
    h[0x40] = scalar(text, "gateArray")                                            # multi-configuration (mode, ROM enables)
    h[0x41] = cfg                                                                  # RAM configuration: not in the state (0, or the game's curCfg with --curcfg)
    h[0x42] = scalar(text, "crtcS")                                                # selected CRTC register
    for i, v in enumerate(array(text, "crtc")[:18]):
        h[0x43 + i] = v
    h[0x55] = scalar(text, "romSelect")
    h[0x56:0x5A] = bytes((scalar(text, "ppiA"), scalar(text, "ppiB"), scalar(text, "ppiC"), scalar(text, "ppiControl")))
    h[0x5A] = scalar(text, "aySelect")
    for i, v in enumerate(array(text, "ay")[:16]):
        h[0x5B + i] = v
    h[0x6B], h[0x6C] = 128, 0                                                      # dump size in KB
    h[0x6D] = 2                                                                    # CPC 6128
    return bytes(h) + b"".join(ram_pages(text))


def curcfg_value(text, spec):
    """the RAM configuration byte (&C0-&C7) of a 128K game state: the game variable curCfg, at the address SPEC (number) or, when SPEC is None, the address of the
    label curCfg in work/elite128/c128.sym (written by tools/check_src128.sh). RAM bank 2 sits at &8000 in every configuration, so the address is read there."""
    if spec is None:
        sym = Path(__file__).resolve().parent.parent / "work/elite128/c128.sym"
        m = re.search(r"^curCfg:\s*EQU\s*0x([0-9A-Fa-f]+)", sym.read_text() if sym.exists() else "", re.M)
        if not m:
            sys.exit("--curcfg: no curCfg in work/elite128/c128.sym (run tools/check_src128.sh) and no address given")
        spec = "0x" + m.group(1)
    addr = int(spec, 0)
    if not 0x8000 <= addr <= 0xBFFF:
        sys.exit("--curcfg: the address must be in &8000-&BFFF (RAM bank 2, the same in every configuration)")
    cfg = ram_pages(text)[2][addr - 0x8000]
    if not 0xC0 <= cfg <= 0xC7:
        sys.exit(f"--curcfg: byte at &{addr:04X} is {cfg:02X}, not a RAM configuration (&C0-&C7): wrong address or not a 128K game state")
    return cfg


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
    if "--sna" in opts:
        out = opts[opts.index("--sna") + 1]
        cfg = 0
        if "--curcfg" in opts:
            nxt = opts[opts.index("--curcfg") + 1:][:1]
            cfg = curcfg_value(text, nxt[0] if nxt and not nxt[0].startswith("-") else None)
        open(out, "wb").write(sna(text, cfg))
        print("wrote", out, f"(RAM configuration &{cfg:02X})")
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

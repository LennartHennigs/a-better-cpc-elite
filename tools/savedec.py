#!/usr/bin/env python3
"""Decrypt and decode an Elite CPC commander save (104 bytes, load &39D2 / in RAM at &38CB).

usage: python3 -I tools/savedec.py SAVE.BIN DISK.dsk              key read from the game disk (tools/elitekey.py)
       python3 -I tools/savedec.py SAVE.BIN LARGEAXX.BIN KEYOFFSET  key from an extracted file
  KEYOFFSET is the file offset of `EquipShip` in LARGEAXX (stock English 0x2BE, German 0x2C2).
The save is XORed with the 0x68 bytes of code at EquipShip. Checksums: byte &66 is the XOR of bytes
0-&65, byte &67 is the sum of bytes 0-&66 (mod 256).
"""
import sys
from functools import reduce

def decode(save, big, off):
    key = big[off:off + 0x68]
    p = bytes(a ^ b for a, b in zip(save[:0x68], key))
    ok_x = reduce(lambda a, b: a ^ b, p[:0x66]) == p[0x66]
    ok_s = sum(p[:0x67]) & 255 == p[0x67]
    return p, ok_x, ok_s

def main(sv, big, off):
    """big: LARGEAXX bytes; off: file offset of the key in it."""
    p, ok_x, ok_s = decode(open(sv, "rb").read(), big, off)
    le = lambda a, n: int.from_bytes(p[a:a + n], "little")
    print("checksums:", "xor ok" if ok_x else "xor BAD", "sum ok" if ok_s else "sum BAD")
    print("name         ", p[:11].split(b"\0")[0].decode("latin1"), "(11-byte field, 10 chars plus NUL; stale tail chars after the NUL)")
    print("legal status ", p[0x0B])
    print("kill score   ", int.from_bytes(p[0x0C:0x0F], "little"), "(24 bits, &38D7-&38D9)")
    print("galaxy       ", p[0x11] + 1)
    print("jump counter ", le(0x0F, 2))
    print("credits      ", (le(0x12, 2) * 10000 + le(0x14, 2)) / 10, "Cr (high word at &12 counts 1,000 Cr, low word at &14 holds the decicredits below 10,000)")
    print("cargo (17)    ", list(p[0x17:0x28]), "(byte &16 before it, role unknown:", p[0x16], ")")
    print("free hold    ", p[0x28], "t")
    print("lasers       ", list(p[0x29:0x2D]))
    print("equipment    ", {"cargo bay": p[0x30], "ECM": p[0x31], "scoops": p[0x34], "pod": p[0x35], "bomb": p[0x36], "energy unit": p[0x37], "docking comp": p[0x38], "gal. hyperdrive": p[0x39]})
    print("flight mode  ", p[0x2D])
    print("fuel         ", p[0x2E] / 10, "LY")
    print("missiles     ", p[0x2F])
    print("galaxy seed  ", p[0x3C:0x42].hex(" "))
    print("system seed  ", p[0x42:0x48].hex(" "))
    print("market stock ", list(p[0x49:0x5A]))
    print("raw          ", p.hex(" "))

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[2].lower().endswith(".dsk"):
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import elitekey
        la = elitekey.largeaxx_from_disk(sys.argv[2])
        main(sys.argv[1], la, elitekey.find_key(la)[0])
    else:
        main(sys.argv[1], open(sys.argv[2], "rb").read(), int(sys.argv[3], 0))

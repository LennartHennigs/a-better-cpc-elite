#!/usr/bin/env python3
"""Get the commander-save key straight from a game disk (no extracted files needed).

A save is XORed with the 104 bytes of game code at `EquipShip` inside LARGEAXX. Every build has its own key (English
LARGEAXX offset 0x2BE, German 0x2C2), so the key is read from the disk the saves belong to.

usage: python3 -I tools/elitekey.py DISK.dsk [KEY.bin]     print the build's key offset and key; optionally write it

As a module: key_from_disk(path) -> (offset, key); find_key(largeaxx_bytes) -> (offset, key);
find_key_by_save(largeaxx_bytes, save_bytes) -> (offset, key) tries every offset until both checksums verify.
"""
import re
import sys
from functools import reduce
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dskx  # noqa: E402

KEYLEN = 0x68
# The code at EquipShip (loadGame/saveGame menu code), addresses wildcarded so it matches every build:
#   call .. / ld de,.. / call .. / call .. / ld b,..? -> CD..11..CD..CD..063ECF CD..CD..B9CD
SIGNATURE = re.compile(rb"\xcd..\x11..\xcd..\xcd..\x06\x3e\xcf\xcd..\xcd..\xb9\xcd", re.DOTALL)


def largeaxx_from_disk(path):
    files = dskx.read_files(dskx.load_sectors(path))
    for (_user, name), data in files.items():
        if name.upper() == "LARGEAXX.BIN":
            return data[128:] if dskx.amsdos_header(data) else data
    raise SystemExit(f"{path}: no LARGEAXX.BIN (is this a game disk?)")


def checks_ok(plain):
    return (reduce(lambda a, b: a ^ b, plain[:0x66]) == plain[0x66]
            and sum(plain[:0x67]) & 255 == plain[0x67])


def find_key(largeaxx):
    hits = [m.start() for m in SIGNATURE.finditer(largeaxx)]
    if len(hits) != 1:
        raise SystemExit(f"key signature found {len(hits)} times; use find_key_by_save with a known save")
    off = hits[0]
    return off, largeaxx[off:off + KEYLEN]


def find_key_by_save(largeaxx, save):
    """Fallback without the signature: the offset whose key makes both checksums of `save` verify."""
    for off in range(len(largeaxx) - KEYLEN):
        key = largeaxx[off:off + KEYLEN]
        if checks_ok(bytes(a ^ b for a, b in zip(save[:KEYLEN], key))):
            return off, key
    raise SystemExit("no key in this LARGEAXX decrypts the save")


def key_from_disk(path):
    return find_key(largeaxx_from_disk(path))


if __name__ == "__main__":
    off, key = key_from_disk(sys.argv[1])
    print(f"LARGEAXX offset 0x{off:X}, key:")
    print(key.hex(" "))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_bytes(key)
        print("written", sys.argv[2])

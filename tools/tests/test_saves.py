#!/usr/bin/env python3
"""Pin the commander save format with the saves of the original disks. Host only, no emulator, a second.

usage: python3 -I tools/tests/test_saves.py

For the saves on Elite_DE_savegames.dsk (German key) and the UK original (1.BIN, UK key):
  key        each build's key is where it should be (UK and French/German offsets) and the key is 104 bytes
  decode     the save decrypts with its own build's key and both checksums verify, and not with another build's key
  roundtrip  decode, recompute the checksums, encrypt again: the original bytes come back
  convert    German -> UK -> German (the `saveedit.py --to-key-disk` conversion) is lossless
Exit code 0 only if everything passes.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import elitekey  # noqa: E402
import saveedit  # noqa: E402

DISKS = ROOT / "disks"
BUILDS = {"UK": "Elite_UK_Firebird_cracked_trainer.dsk", "DE": "Elite_DE_cracked.dsk", "FR": "Elite (1985)(Firebird Software)(fr).dsk"}
OFFSETS = {"UK": 0x2BE, "DE": 0x2C2, "FR": 0x2C2}
SAVES = [("DE", "Elite_DE_savegames.dsk", n) for n in ("PETER.BIN", "PETE.BIN", "LEN.BIN")] + [("UK", "Elite_UK_original_protected.dsk", "1.BIN")]

fails = []


def check(ok, what):
    print(f"{'ok  ' if ok else 'FAIL'} {what}")
    if not ok:
        fails.append(what)


def main():
    keys = {}
    for b, disk in BUILDS.items():
        p = DISKS / disk
        if not p.exists():
            print(f"missing {p}: the original disks belong in disks/")
            return 2
        off, key = elitekey.key_from_disk(str(p))
        keys[b] = key
        check(off == OFFSETS[b] and len(key) == 104, f"{b} key: 104 bytes at LARGEAXX offset &{OFFSETS[b]:X}")
    check(len({bytes(k) for k in keys.values()}) == 3, "the three builds have three different keys")
    for build, disk, name in SAVES:
        enc, _hdr, _d = saveedit.read_save(f"{DISKS / disk}:{name}")
        key = keys[build]
        plain = saveedit.decrypt(enc, key)
        check(saveedit.checks_ok(plain), f"{name} ({build}): decodes with the {build} key, both checksums verify")
        others = [b for b in keys if b != build]
        check(not any(saveedit.checks_ok(saveedit.decrypt(enc, keys[o])) for o in others), f"{name}: fails with the other builds' keys")
        again = bytearray(plain)
        saveedit.checksums(again)
        check(saveedit.encrypt(again, key) == bytes(enc), f"{name}: decode, recompute checksums, encode gives the original bytes")
        if build == "DE":
            uk = saveedit.encrypt(plain, keys["UK"])
            back = saveedit.encrypt(saveedit.decrypt(uk, keys["UK"]), key)
            check(back == bytes(enc) and saveedit.checks_ok(saveedit.decrypt(uk, keys["UK"])), f"{name}: German -> UK -> German is lossless")
    print(f"\n{len(fails)} failed" if fails else "\nall passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

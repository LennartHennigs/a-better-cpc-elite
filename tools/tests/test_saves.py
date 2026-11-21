#!/usr/bin/env python3
"""Pin the commander save format with the saves of the original disks. Host only, no emulator, a second.

usage: python3 -I tools/tests/test_saves.py

For the saves on Elite_DE_savegames.dsk (German key) and the UK original (1.BIN, UK key):
  key        each build's key is where it should be (UK and French/German offsets) and the key is 104 bytes
  decode     the save decrypts with its own build's key and both checksums verify, and not with another build's key
  roundtrip  decode, recompute the checksums, encrypt again: the original bytes come back
  convert    German -> UK -> German (the `saveedit.py --to-key-disk` conversion) is lossless, and every save goes to the 128K build's key and back (what CONVSAVE.BAS does)
Exit code 0 only if everything passes.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cheat128  # noqa: E402
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
    keys["128K"] = cheat128.save_key()      # the 128K build (src/elite128): the same code at EquipShip, relocated, so a different key
    check(len(keys["128K"]) == 104 and keys["128K"] != keys["UK"], "128K key: 104 bytes of src/elite128 LARGEAXX, not the UK key")
    check(len({bytes(k) for k in keys.values()}) == 4, "the four builds have four different keys")
    for build, disk, name in SAVES:
        enc, _hdr, _d = saveedit.read_save(f"{DISKS / disk}:{name}")
        key = keys[build]
        plain = saveedit.decrypt(enc, key)
        check(saveedit.checks_ok(plain), f"{name} ({build}): decodes with the {build} key, both checksums verify")
        others = [b for b in keys if b != build]      # includes the 128K key
        check(not any(saveedit.checks_ok(saveedit.decrypt(enc, keys[o])) for o in others), f"{name}: fails with the other builds' keys")
        again = bytearray(plain)
        saveedit.checksums(again)
        check(saveedit.encrypt(again, key) == bytes(enc), f"{name}: decode, recompute checksums, encode gives the original bytes")
        to128 = saveedit.encrypt(plain, keys["128K"])
        check(saveedit.checks_ok(saveedit.decrypt(to128, keys["128K"])) and saveedit.encrypt(saveedit.decrypt(to128, keys["128K"]), key) == bytes(enc), f"{name}: {build} -> 128K -> {build} is lossless")
        if build == "DE":
            uk = saveedit.encrypt(plain, keys["UK"])
            back = saveedit.encrypt(saveedit.decrypt(uk, keys["UK"]), key)
            check(back == bytes(enc) and saveedit.checks_ok(saveedit.decrypt(uk, keys["UK"])), f"{name}: German -> UK -> German is lossless")
    print(f"\n{len(fails)} failed" if fails else "\nall passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

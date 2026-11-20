#!/usr/bin/env python3
"""Check the disks the make targets deliver (build/*.dsk) against the project rules. Host only, no emulator, a few seconds.

usage: python3 -I tools/tests/test_disks.py [DISK.dsk ...]      (default: every build/*.dsk; `make test` builds them first)

Per disk:
  visible    CAT shows only .BAS and .TXT files (and commander saves, which stay visible so the game's load menu lists them)
  headers    every .BIN/.BAS has a valid AMSDOS header (checksum), a .TXT may be plain text
  sectors    every allocated block lies on a track with the standard sector ids &C1-&C9 (AMSDOS cannot read odd-sector tracks)
  files      the files the build needs are there (core game files; mission, trainer and viewer files on the expanded and mission disks)
  key        the 104 save-key bytes at EquipShip equal those of the original game of the same language (else old saves stop loading)
Exit code 0 only if every check of every disk passes.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import dskx  # noqa: E402
import elitekey  # noqa: E402

STD = set(range(0xC1, 0xCA))
REF = {"en": "Elite_UK_Firebird_cracked_trainer.dsk", "de": "Elite_DE_cracked.dsk", "fr": "Elite (1985)(Firebird Software)(fr).dsk"}
CORE = ["LARGEAXX.BIN", "COMMONXX.BIN", "COMMON2X.BIN", "MUSIQUEX.BIN", "INDICATO.BIN", "NOTMUSIC.BIN", "PICTURE.BIN"]
MISSIONS = ["MISSIONC.BIN", "MISSIONP.BIN", "MISSIONT.BIN", "MISSIONR.BIN"] + [f"MFLIGHT{c}.BIN" for c in "0CPTSR1234567"]
EXPANDED = ["TRAINER.BAS", "CHEATB.BIN", "EDITSAVE.BAS", "LISTSAVE.BAS", "SHOWSHPS.BAS", "SHIPS.BIN", "README.TXT"]


def directory(secs):
    first = min(r for (t, r) in secs if t == 0)
    d = b"".join(secs[(0, first + i)] for i in range(4))
    files = {}
    for i in range(64):
        e = d[i * 32:(i + 1) * 32]
        if e[0] == 0xE5:
            continue
        name = bytes(b & 0x7F for b in e[1:9]).decode("latin1").strip() + "." + bytes(b & 0x7F for b in e[9:12]).decode("latin1").strip()
        f = files.setdefault(name, {"system": [], "blocks": []})
        f["system"].append(bool(e[10] & 0x80))
        f["blocks"] += [b for b in e[16:32] if b]
    return first, files


def language(path):
    n = path.name
    return "de" if n.endswith("_de.dsk") else "fr" if n.endswith("_fr.dsk") else "en"


def check(path):
    fails = []
    secs = dskx.load_sectors(path)
    first, files = directory(secs)
    data = dskx.read_files(secs)
    by_name = {k[1]: v for k, v in data.items()}
    for name, f in sorted(files.items()):
        flags = set(f["system"])
        hidden = flags == {True}
        if len(flags) != 1:
            fails.append(f"{name}: the System attribute differs between extents")
        raw = by_name.get(name, b"")
        h = dskx.amsdos_header(raw)
        save = bool(h) and h["load"] == 0x39D2 and h["length"] == 0x68
        ext = name.rsplit(".", 1)[-1]
        if not hidden and ext not in ("BAS", "TXT") and not save:
            fails.append(f"{name}: visible in CAT (only .BAS, .TXT and saves may be)")
        if ext in ("BAS", "BIN") and not h:
            fails.append(f"{name}: no valid AMSDOS header")
        for b in f["blocks"]:
            for s in (0, 1):
                ls = b * 2 + s
                if (ls // 9, first + ls % 9) not in secs:
                    fails.append(f"{name}: block {b} lies on a track with no standard sector &{first + ls % 9:02X} (track {ls // 9})")
    for t in {t for t, _ in secs}:
        ids = {r for (tt, r) in secs if tt == t}
        if ids != STD and any((t == (b * 2 + s) // 9) for f in files.values() for b in f["blocks"] for s in (0, 1)):
            fails.append(f"track {t} holds file data but its sector ids are {sorted(hex(i) for i in ids)}")
    lang = language(path)
    need = ["LARGEAXX.BIN", "COMMONXX.BIN", "COMMON2X.BIN"] if lang == "fr" else CORE + ["ELITE.BAS"]
    if "expanded" in path.name or "missions" in path.name:
        need += MISSIONS
    if "expanded" in path.name:
        need += EXPANDED
    for n in need:
        if n not in files:
            fails.append(f"{n}: missing")
    if lang == "fr" and not any(n.endswith(".BAS") for n in files):
        fails.append("no .BAS loader")
    ref = ROOT / "disks" / REF[lang]
    if ref.exists() and "LARGEAXX.BIN" in files:
        off, key = elitekey.key_from_disk(str(path))
        roff, rkey = elitekey.key_from_disk(str(ref))
        if (off, key) != (roff, rkey) and not path.name.startswith("elite128"):      # the 128K build relocates the code the key is read from: saves are not compatible (TODO_128K.md, "Save key")
            fails.append(f"save key differs from {ref.name} (offset &{off:X} against &{roff:X}): old saves will not load")
    return fails, len(files)


def main():
    paths = [Path(a) for a in sys.argv[1:]] or sorted((ROOT / "build").glob("*.dsk"))
    if not paths:
        print("no disks in build/: run make original expanded missions first")
        return 2
    bad = 0
    for p in paths:
        fails, n = check(p)
        print(f"{'FAIL' if fails else 'ok  '} {p.name} ({n} files)")
        for f in fails:
            print(f"       {f}")
        bad += bool(fails)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

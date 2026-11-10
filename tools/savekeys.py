#!/usr/bin/env python3
"""Shared by tools/mk_editsave.py and tools/mk_listsave.py: the three build keys (UK, French, German; read from the game disks by tools/elitekey.py) as BASIC
DATA lines, and the writer for src/cheats/<NAME>.ASC (CRLF lines, ends with Ctrl-Z)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import elitekey  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DISKS = [("UK", "Elite_UK_Firebird_cracked_trainer.dsk"), ("FRENCH", "Elite (1985)(Firebird Software)(fr).dsk"), ("GERMAN", "Elite_DE_cracked.dsk")]

def key_data_lines(first=300):
    """DATA lines with the three build keys (UK, French, German) as hex strings, numbered from `first`."""
    out = []
    for i, (name, disk) in enumerate(DISKS):
        off, key = elitekey.key_from_disk(ROOT / disk)
        out.append(f"{first + 10 * i} DATA {name},{key.hex().upper()}")
    return out


def write_asc(name, lines):
    text = "".join(l + "\r\n" for l in lines) + "\x1a"
    (ROOT / "src/cheats" / f"{name}.ASC").write_bytes(text.encode("latin-1"))
    print(f"wrote src/cheats/{name}.ASC", len(text), "bytes")

#!/usr/bin/env python3
"""Give every file that is not a .BAS or .TXT the System attribute, in place, so CAT lists only the programs and texts (LOAD and RUN still find the rest).

usage: python3 -I tools/hide_files.py IMAGE.dsk [IMAGE.dsk ...]
Used by tools/build_cheat.sh on the trainer disks; tools/build_dsk.py does the same while it builds. Never run it on the original disks in disks/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dskx import is_original, sector_offsets  # noqa: E402


def hide_entries(d, secs, first):
    """Set the System attribute (bit 7 of e[10], the second extension byte) on every directory entry that is not a .BAS or .TXT file, in the bytearray d. Returns (hidden names, visible names)."""
    hidden, shown = [], set()
    for i in range(64):
        off = secs[(0, first + i // 16)][0] + (i % 16) * 32
        e = d[off:off + 32]
        if e[0] == 0xE5:
            continue
        name = bytes(b & 0x7F for b in e[1:9]).decode("latin1").strip() + "." + bytes(b & 0x7F for b in e[9:12]).decode("latin1").strip()
        if name.endswith((".BAS", ".TXT")):
            shown.add(name)
        elif not e[10] & 0x80:
            d[off + 10] = e[10] | 0x80
            hidden.append(name)
    return hidden, shown


def hide(path):
    d = bytearray(Path(path).read_bytes())
    secs = sector_offsets(d)
    hidden, shown = hide_entries(d, secs, min(r for (t, r) in secs if t == 0))
    Path(path).write_bytes(d)
    print(f"{path}: {len(hidden)} entries hidden, visible: {', '.join(sorted(shown))}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        if is_original(p):
            sys.exit(f"{p}: refusing to touch a disk in the project root or disks/")
        hide(p)

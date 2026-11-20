#!/usr/bin/env python3
"""Add files to a DSK image with dskx (not iDSK, which may fill the two odd-sector tracks that AMSDOS cannot read), replacing a file of the same name.

usage: python3 -I tools/add_files.py IMAGE.dsk [-NAME.EXT] [NAME.EXT=]FILE ...
-NAME.EXT deletes that file from the image first (the Firebird disk's own CHEAT.BAS, when TRAINER.BAS takes its place); a name that is not there is not an error.
FILE is written as it is (AMSDOS header included); the disk name is NAME.EXT, or FILE's own name when no NAME.EXT= is given. Run tools/hide_files.py afterwards to
hide what CAT should not show. Never run it on the original disks in disks/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dskx  # noqa: E402



def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    disk = Path(argv[0])
    if dskx.is_original(disk):
        sys.exit(f"{disk}: refusing to touch a disk in the project root or disks/")
    d = bytearray(disk.read_bytes())
    secs = dskx.sector_offsets(d)
    first = min(r for (t, r) in secs if t == 0)
    for arg in argv[1:]:
        if arg.startswith("-"):
            name, _, ext = arg[1:].upper().partition(".")
            n = dskx.remove_file(d, secs, first, name, ext)
            print(f"{disk.name}: {name}.{ext} " + ("deleted" if n else "not on the disk"))
            continue
        target, _, path = arg.rpartition("=")
        data = Path(path).read_bytes()
        name, _, ext = (target or Path(path).name).upper().partition(".")
        if not (1 <= len(name) <= 8 and len(ext) <= 3 and "." not in ext):
            sys.exit(f"{target or path}: not an AMSDOS 8.3 name (NAME.EXT=FILE sets one)")
        removed = dskx.add_padded(d, secs, first, name, ext, data, replace=True)
        print(f"{disk.name}: {name}.{ext} {len(data)} bytes" + (" (replaced)" if removed else ""))
    disk.write_bytes(d)


if __name__ == "__main__":
    main(sys.argv[1:])

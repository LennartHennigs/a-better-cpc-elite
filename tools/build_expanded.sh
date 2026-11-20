#!/bin/bash
# The expanded game on one disk: enhancements, all added missions, all ship packs and traffic, our trainer and cheats (TRAINER, EDITSAVE, LISTSAVE) and the ship viewer.
#   usage: bash tools/build_expanded.sh [en|de|fr]      (default en; make expanded [LOC=de|fr])
#   output: build/elite64.dsk (the pieces it is made from stay in work/); its loader is ELITE64.BAS: RUN"ELITE64
# Order matters: the viewer first (build_dsk.py --missions picks up SHOWSHPS.BAS and SHIPS.BIN), then build_cheat.sh, which tokenises the trainers, runs
# build_dsk.py --missions and adds EDITSAVE and LISTSAVE to the mission disk. German and French have no missions, ship packs or viewer yet: the language is
# accepted so the entry point stays the same when they are ported.
set -e
cd "$(dirname "$0")/.."
LOC=${1:-en}
if [ "$LOC" != en ]; then
  echo "the expanded build exists for English only: missions, ship packs and the viewer are not ported to German/French yet (make original LOC=$LOC, or bash tools/build_cheat.sh for the trainer disk)" >&2
  exit 1
fi
bash tools/build_showship.sh
bash tools/build_cheat.sh
mkdir -p build
cp work/missions_cheat.dsk build/elite64.dsk
# the 64K expanded disk starts with RUN"ELITE64: Firebird's ELITE.BAS renamed in place (directory entry, AMSDOS header name and checksum), and the README says so
python3 -I - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "tools")
import dskx
p = Path("build/elite64.dsk")
d = bytearray(p.read_bytes())
secs = dskx.sector_offsets(d)
first = min(r for (t, r) in secs if t == 0)
assert dskx.rename_file(d, secs, first, "ELITE", "BAS", "ELITE64"), "ELITE.BAS is not on the disk"
txt = dskx.read_files(dskx.load_sectors(p))[(0, "README.TXT")].rstrip(b"\x1a")
new = txt.replace(b'RUN"ELITE\r\n', b'RUN"ELITE64\r\n').replace(b'RUN"ELITE\n', b'RUN"ELITE64\n')
assert new != txt, 'README.TXT has no RUN"ELITE line'
dskx.add_padded(d, secs, first, "README", "TXT", new, replace=True)
p.write_bytes(d)
PY
# a ready commander: LEN from the German saves disk (Elite_DE_savegames.dsk), re-keyed for the English game; left visible (no hide_files after it), like the saves of work/de_savegames.dsk
python3 -I tools/saveedit.py edit disks/Elite_DE_savegames.dsk:LEN.BIN --key-disk disks/Elite_DE_cracked.dsk --to-key-disk build/elite64.dsk -o build/elite64.dsk:LEN.BIN >/dev/null
echo "built build/elite64.dsk (RUN\"ELITE64, RUN\"TRAINER, RUN\"SHOWSHPS, RUN\"EDITSAVE, RUN\"LISTSAVE)"

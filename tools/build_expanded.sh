#!/bin/bash
# The expanded game on one disk: enhancements, all added missions, all ship packs and traffic, our trainer and cheats (TRAINER, EDITSAVE, LISTSAVE) and the ship viewer.
#   usage: bash tools/build_expanded.sh [en|de|fr]      (default en; make expanded [LOC=de|fr])
#   output: work/elite_expanded.dsk (also copied to work/xray/disk/)
# Order matters: the viewer first (build_dsk.py --missions picks up SHOWSHIP.BAS and SHIPS.BIN), then build_cheat.sh, which tokenises the trainers, runs
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
cp work/missions_cheat.dsk work/elite_expanded.dsk
# a ready commander: LEN from the German saves disk (Elite_DE_savegames.dsk), re-keyed for the English game; left visible (no hide_files after it), like the saves of work/de_savegames.dsk
python3 -I tools/saveedit.py edit Elite_DE_savegames.dsk:LEN.BIN --key-disk Elite_DE_cracked.dsk --to-key-disk work/elite_expanded.dsk -o work/elite_expanded.dsk:LEN.BIN >/dev/null
mkdir -p work/xray/disk && cp work/elite_expanded.dsk work/xray/disk/
echo "built work/elite_expanded.dsk (RUN\"ELITE, RUN\"TRAINER, RUN\"SHOWSHIP, RUN\"EDITSAVE, RUN\"LISTSAVE)"

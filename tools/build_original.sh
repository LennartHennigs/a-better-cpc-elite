#!/bin/bash
# The original game on a disk: the four code files assembled with no flags (original bytes, CPC+ keyboard fix included) written into a copy of the base disk.
#   usage: bash tools/build_original.sh [en|de|fr]      (default en; make original [LOC=de|fr])
#   output: work/elite_original.dsk, work/elite_original_de.dsk, work/elite_original_fr.dsk (also copied to work/xray/disk/)
# The English base is the Firebird disk, so its own CHEAT.BAS stays on it. Nothing of ours is added.
set -e
cd "$(dirname "$0")/.."
LOC=${1:-en}
case $LOC in
  en) FLAG=""; OUT=work/elite_original.dsk ;;
  de) FLAG="--de"; OUT=work/elite_original_de.dsk ;;
  fr) FLAG="--fr"; OUT=work/elite_original_fr.dsk ;;
  *) echo "usage: $0 [en|de|fr]" >&2; exit 1 ;;
esac
python3 -I tools/build_dsk.py --stock $FLAG "$OUT"
mkdir -p work/xray/disk && cp "$OUT" work/xray/disk/
echo "built $OUT (boot: RUN\"$([ $LOC = fr ] && echo EL || echo ELITE))"

#!/usr/bin/env bash
# Build Fessor's patched Elite from extended/source with RASM and check it against the beta disk.
# Run it yourself: bash scripts/build-fessor.sh
# Works on a fresh copy in work/build_fessor_run (wiped each run); extended/source and
# work/build_fessor are never touched. Needs tools/bin/rasm (see CLAUDE.md for how it is built).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/extended/source"
RUN="$ROOT/work/build_fessor_run"
RASM="$ROOT/tools/bin/rasm"
REF="$ROOT/work/bin_ext"   # files read off ELITE_EXT.DSK, no AMSDOS header

[ -x "$RASM" ] || { echo "missing $RASM (build RASM first, see CLAUDE.md)" >&2; exit 1; }
[ -d "$SRC" ] || { echo "missing $SRC" >&2; exit 1; }

rm -rf "$RUN"
mkdir -p "$RUN"
cp "$SRC"/*.asm "$RUN"/

cd "$RUN"
"$RASM" EliteMasterSource.asm -s -sq

echo
echo "Built into $RUN. Comparing with the beta disk (AMSDOS header stripped):"
status=0
for f in LARGEAXP COMMONXP COMMON2P NOTMUSIP SHIPSETB; do
  if [ ! -f "$f.BIN" ]; then echo "  $f: not produced"; status=1; continue; fi
  if cmp -s <(tail -c +129 "$f.BIN") "$REF/$f.BIN"; then
    echo "  $f: identical"
  else
    echo "  $f: DIFFERS"; status=1
  fi
done
exit $status

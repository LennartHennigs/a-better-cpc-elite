#!/usr/bin/env bash
# Write the flat, readable listing of the 128K build: every module assembled with the flags of the real build (tools/check_src128.sh), includes expanded,
# address and bytes next to each source line (sjasmplus --lst, with the label table at the end).
# usage: bash tools/listing6128.sh [OUTDIR]     (default build/listing6128; `make listing6128` calls it)
# Result: OUTDIR/<module>.lst for largeaxx, commonxx, common2x, musiquex, fill and tt, and OUTDIR/elite6128.lst with all of them in one file (a banner line per module).
# The generated hull data (work/elite128/, made from ArcElite's table by tools/ship128.py) is part of the listing, so keep OUTDIR out of git (build/ and work/ are ignored; NOTICE item 10).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/listing6128}"
mkdir -p "$OUT" || exit 1
rm -f "$OUT"/*.lst
LISTDIR="$OUT" bash "$ROOT/tools/check_src128.sh" || { echo "listing6128: check_src128.sh failed, no listing written"; exit 1; }
ALL="$OUT/elite6128.lst"
: > "$ALL"
for pair in largeaxx:largeaxx.asm commonxx:commonxx.asm common2x:common2x.asm musiquex:musiquex.asm fill:fill.asm tt:fill_tt.asm; do
  n=${pair%%:*}; src=${pair#*:}
  [ -s "$OUT/$n.lst" ] || { echo "listing6128: $n.lst is missing or empty"; exit 1; }
  printf '\n;==================== %s (src/elite128/%s) ====================\n' "$n" "$src" >> "$ALL"
  cat "$OUT/$n.lst" >> "$ALL"
done
echo "listing6128: $(wc -l < "$ALL" | tr -d ' ') lines in $ALL (and one .lst per module next to it)"

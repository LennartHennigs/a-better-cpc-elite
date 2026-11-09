#!/usr/bin/env bash
# Assemble src/elite*/*.asm with sjasmplus and compare with the original binaries.
# usage: bash tools/check_src.sh [de]     (no argument: stock English, src/elite vs work/bin_stock;
#                                          de: German, src/elite_de vs work/bin_german)
#        exit 0 only if the default (stock) build is byte-exact, apart from the one-byte CPC+ fix in src/elite and src/elite_fr (docs/_cpcplus.md),
#        and the -DENHANCED build differs only in the documented places (ESC byte, star occlusion)
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${1:-}" = "fr" ]; then SRC="$ROOT/src/elite_fr"; BIN="$ROOT/work/bin_fr"; elif [ "${1:-}" = "de" ]; then SRC="$ROOT/src/elite_de"; BIN="$ROOT/work/bin_german"; else SRC="$ROOT/src/elite"; BIN="$ROOT/work/bin_stock"; fi
OUT="$(mktemp -d)"
export PATH="$HOME/.local/bin:$PATH"
rc=0
for p in "largeaxx LARGEAXX" "commonxx COMMONXX" "common2x COMMON2X" "musiquex MUSIQUEX"; do
  read -r n f <<<"$p"
  if ! sjasmplus --raw="$OUT/$n.bin" --sym="$OUT/$n.sym" "$SRC/$n.asm" >"$OUT/$n.log" 2>&1; then echo "$n: assemble FAILED"; tail -5 "$OUT/$n.log"; rc=1; continue; fi
  REF="$OUT/$n.ref"; cp "$BIN/$f.BIN" "$REF"
  if [ "$n" != commonxx ]; then
    if cmp -s "$OUT/$n.bin" "$REF"; then echo "$n: ok"; else echo "$n: DIFFERS"; rc=1; fi
    continue
  fi
  # COMMONXX: the default build (no flags) must equal the original bytes, apart from the CPC+ fix (ED 79 -> ED 49 in getPPI_Input, see docs/_cpcplus.md; the German stock
  # disk already has it), which the reference gets. The -DENHANCED build (STAR_OCCLUDE + ESC_KEYCODE=0x7F) may differ only in the ESC byte (value &7F, row 8 bit 2 of
  # tblKeyboardmatrix) and inside dustPlotPixel's slot (unusedViewBorderFill..ClearBitmap) and the dust loop dust70..dust70+16.
  sym() { awk -v k="$1:" '$2 == k || $1 == k { print $NF }' "$OUT/$n.sym"; }
  [ "$SRC" != "$ROOT/src/elite_de" ] && printf '\x49' | dd of="$REF" bs=1 seek=$(( $(sym getPPI_Input) + 20 - 0x1A40 )) conv=notrunc 2>/dev/null
  ESCP=$(( $(sym tblKeyboardmatrix) + 66 - 0x1A40 ))
  if ! cmp -s "$OUT/$n.bin" "$REF"; then echo "$n (default build): DIFFERS from the original"; rc=1; continue; fi
  if ! sjasmplus -DENHANCED --raw="$OUT/$n.enh.bin" --sym="$OUT/$n.enh.sym" "$SRC/$n.asm" >/dev/null 2>&1; then echo "$n -DENHANCED: assemble FAILED"; rc=1; continue; fi
  esym() { awk -v k="$1:" '$2 == k || $1 == k { print $NF }' "$OUT/$n.enh.sym"; }
  LO=$(( $(esym dustPlotPixel) - 0x1A40 )); HI=$(( $(esym ClearBitmap) - 0x1A40 )); DL=$(( $(esym dust70) - 0x1A40 ))
  if cmp -l "$OUT/$n.enh.bin" "$REF" | awk -v lo=$LO -v hi=$HI -v dl=$DL -v esc=$((ESCP+1)) '{o=$1-1; if ($1==esc) { if ($2!="177" || $3!="377") bad=1; seen=1 } else if (!((o>=lo && o<hi) || (o>=dl && o<dl+16))) bad=1} END{exit (bad || !seen)}'; then echo "$n: ok (default = original; -DENHANCED differs only in the ESC byte and the two star-occlusion slots)"; else echo "$n -DENHANCED: differs outside the ESC byte and the star-occlusion slots"; rc=1; fi
done
# English only: the -DMISSIONS variant (src/elite/missions_*.asm in the free tails) must keep both files the same length
if [ "$SRC" = "$ROOT/src/elite" ]; then
  for p in "largeaxx LARGEAXX" "commonxx COMMONXX"; do
    read -r n f <<<"$p"
    if sjasmplus -DMISSIONS --raw="$OUT/$n.m.bin" "$SRC/$n.asm" >"$OUT/$n.m.log" 2>&1 && [ "$(wc -c <"$OUT/$n.m.bin")" -eq "$(wc -c <"$BIN/$f.BIN")" ]; then echo "$n -DMISSIONS: ok (same length)"; else echo "$n -DMISSIONS: FAILED"; tail -3 "$OUT/$n.m.log"; rc=1; fi
  done
fi
# -DTITLESEL (title screen ship selection; hook code in the zero tail of MUSIQUEX) keeps the lengths, and the addresses musiquex.asm
# hard-codes for COMMONXX must be the real ones (English also with -DMISSIONS)
TSYMS=""; TFLAGS=""
case "$SRC" in
  "$ROOT/src/elite")    TSYMS="setCommandsCPL:4531 setCommandsNOP:4535 transferBuffertoScreen:1ED1 spawnCommandParser:809C dataFromPPI:8D2D splash2Shipnr:1DA8"; TFLAGS="-DMISSIONS";;
  "$ROOT/src/elite_de") TSYMS="setCommandsCPL:463E setCommandsNOP:4642 transferBuffertoScreen:1ED1 spawnCommandParser:81E3 dataFromPPI:8E75 splash2Shipnr:1DA8";;
esac
if [ -n "$TSYMS" ]; then
  for fl in "" $TFLAGS; do
  if sjasmplus -DTITLESEL $fl --raw="$OUT/c.t.bin" --sym="$OUT/c.t.sym" "$SRC/commonxx.asm" >"$OUT/c.t.log" 2>&1 \
     && sjasmplus -DTITLESEL --raw="$OUT/m.t.bin" "$SRC/musiquex.asm" >"$OUT/m.t.log" 2>&1 \
     && [ "$(wc -c <"$OUT/c.t.bin")" -eq "$(wc -c <"$BIN/COMMONXX.BIN")" ] && [ "$(wc -c <"$OUT/m.t.bin")" -eq "$(wc -c <"$BIN/MUSIQUEX.BIN")" ]; then
    bad=0
    for pr in $TSYMS; do
      n=${pr%%:*}; v=${pr##*:}
      grep -qi "^$n: EQU 0x0000$v" "$OUT/c.t.sym" && grep -qi "^$n equ 0x$v" "$SRC/musiquex.asm" || { echo "TITLESEL $fl: $n is not at &$v"; bad=1; }
    done
    [ $bad -eq 0 ] && echo "commonxx/musiquex -DTITLESEL $fl: ok (same length, hook addresses match)" || rc=1
  else echo "-DTITLESEL $fl: FAILED"; tail -3 "$OUT/c.t.log" "$OUT/m.t.log"; rc=1; fi
  done
fi
# the three source trees must agree on the ESC values (0x7F enhanced, 0xFF default)
if [ "$(for t in elite elite_de elite_fr; do grep -h '^ESC_KEYCODE equ' "$ROOT/src/$t/commonxx.asm" | awk '{print $3}' | tr '\n' ' '; echo; done | sort -u | wc -l)" -ne 1 ]; then echo "ESC_KEYCODE values differ between src/elite, src/elite_de and src/elite_fr"; rc=1; fi
rm -rf "$OUT"; exit $rc

#!/usr/bin/env bash
# Assemble src/elite*/*.asm with sjasmplus and compare with the original binaries.
# usage: bash tools/check_src.sh [de]     (no argument: stock English, src/elite vs work/bin_stock;
#                                          de: German, src/elite_de vs work/bin_german)
#        exit 0 only if the default (stock) build is byte-exact, apart from the one-byte CPC+ fix in src/elite and src/elite_fr (docs/_cpcplus.md),
#        and the -DENHANCED build differs only in the documented places (ESC byte, star occlusion, station-screen tabs and labels, cash on the quantity line,
#        escape-pod cargo clear); the LARGEAXX save-key window (EquipShip, 104 bytes) must stay the stock bytes
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
    if cmp -s "$OUT/$n.bin" "$REF"; then echo "$n: ok"; else echo "$n: DIFFERS"; rc=1; continue; fi
    # LARGEAXX -DENHANCED (cash on the quantity line, English only): differs only in the 16-byte clrLineCash slot and the operands of the two `call clrLineCash` sites
    if [ "$n" = largeaxx ] && grep -q '^ *IFDEF ENHANCED' "$SRC/largeaxx.asm"; then
      if sjasmplus -DENHANCED --raw="$OUT/$n.enh.bin" --sym="$OUT/$n.enh.sym" "$SRC/$n.asm" >/dev/null 2>&1; then
        esym() { awk -v k="$1:" '$2 == k || $1 == k { print $NF }' "$OUT/$n.enh.sym"; }
        ST=$(( $(esym statusToken) - 0x840 )); CL=$(( $(esym clrLineCash) - 0x840 )); PQ=$(( $(esym printInputQuestionforQuantity) - 0x840 )); EQ=$(( $(esym eqShoppingloop) - 0x840 ))
        # the 104 bytes at EquipShip are the save key: any change breaks every existing save 
        KW=$(( $(esym EquipShip) - 0x840 ))
        if ! cmp -s <(dd if="$OUT/$n.enh.bin" bs=1 skip=$KW count=104 2>/dev/null) <(dd if="$REF" bs=1 skip=$KW count=104 2>/dev/null); then echo "$n -DENHANCED: save key window (EquipShip, 104 bytes) CHANGED: old saves will not load"; rc=1; fi
        if cmp -l "$OUT/$n.enh.bin" "$REF" | awk -v cl=$CL -v st=$ST -v pq=$PQ -v eq=$EQ '{o=$1-1; if (!((o>=cl && o<cl+16) || (o>=st && o<st+7) || o==pq+1 || o==pq+2 || o==eq+1 || o==eq+2)) bad=1} END{exit bad}'; then echo "$n -DENHANCED: ok (differs only in the clrLineCash slot, its two call sites and the status label)"; else echo "$n -DENHANCED: differs outside the clrLineCash slot and its call sites"; rc=1; fi
      else echo "$n -DENHANCED: assemble FAILED"; rc=1; fi
    fi
    # COMMON2X -DENHANCED (English): only the fuel-line tab (call operand and inline byte)
    if [ "$n" = common2x ] && grep -q '^ *IFDEF ENHANCED' "$SRC/common2x.asm"; then
      if sjasmplus -DENHANCED --raw="$OUT/$n.enh.bin" --sym="$OUT/$n.enh.sym" "$SRC/$n.asm" >/dev/null 2>&1; then
        FT=$(( $(awk '$2 == "fuelTab:" || $1 == "fuelTab:" { print $NF }' "$OUT/$n.enh.sym") - 0xC000 )); TT=$(( $(awk '$2 == "titleTab:" || $1 == "titleTab:" { print $NF }' "$OUT/$n.enh.sym") - 0xC000 ))
        if cmp -l "$OUT/$n.enh.bin" "$REF" | awk -v ft=$FT -v tt=$TT '{o=$1-1; if (!((o>=ft && o<ft+4) || o==tt)) bad=1} END{exit bad}'; then echo "$n -DENHANCED: ok (differs only in the fuel-line tab and the headline tab)"; else echo "$n -DENHANCED: differs outside the fuel-line tab"; rc=1; fi
      else echo "$n -DENHANCED: assemble FAILED"; rc=1; fi
    fi
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
  # offset of a COMMONXX label in the file; -99999 (matches nothing) when the tree has no such label (the English-only slots)
  off() { local v; v=$(esym "$1"); if [ -n "$v" ]; then echo $(( v - 0x1A40 )); else echo -99999; fi; }
  LO=$(off dustPlotPixel); HI=$(off ClearBitmap); DL=$(off dust70)
  SB=$(off statusLabels); CP=$(off statusColonPrint); TC=$(off statusTitleCol); HC=$(off chartTitleCol); CC=$(off statusColon)
  SL=$(off statusToken)   # English: "STATUS" instead of "LEGAL STATUS"
  CH=$(off cashHome); PC=$(off podCleanOperand); PD=$(off predelayOperand); HP=$(off hyperCountPos)   # English: cashHome (&1FEA, 7 bytes); all trees: the pod cargo clear start (low operand byte)
  if cmp -l "$OUT/$n.enh.bin" "$REF" | awk -v lo=$LO -v hi=$HI -v dl=$DL -v sl=$SL -v cc=$CC -v tc=$TC -v hc=$HC -v sb=$SB -v cp=$CP -v ch=$CH -v pc=$PC -v pd=$PD -v hp=$HP -v esc=$((ESCP+1)) '{o=$1-1; if ($1==esc) { if ($2!="177" || $3!="377") bad=1; seen=1 } else if (!((o>=lo && o<hi) || (o>=dl && o<dl+16) || (o>=sl && o<sl+7) || o==cc || o==tc || o==hc || (o>=sb && o<sb+12) || (o>=cp && o<cp+4) || (o>=ch && o<ch+7) || o==pc || o==pd || o==hp)) bad=1} END{exit (bad || !seen)}'; then echo "$n: ok (default = original; -DENHANCED differs only in the ESC byte, the star-occlusion slots, the status/title tabs and labels, cashHome, the pod cargo clear, the key pre-delay and the hyperspace count position)"; else echo "$n -DENHANCED: differs outside the documented slots"; rc=1; fi
done
# English only: the -DMISSIONS variant (src/elite/missions_*.asm in the free tails) must keep both files the same length
if [ "$SRC" = "$ROOT/src/elite" ]; then
  for p in "largeaxx LARGEAXX" "commonxx COMMONXX"; do
    read -r n f <<<"$p"
    for fl in "-DMISSIONS" "-DENHANCED -DMISSIONS"; do   # the second is the build that goes on the disks (tools/build_dsk.py)
      if sjasmplus $fl --raw="$OUT/$n.m.bin" "$SRC/$n.asm" >"$OUT/$n.m.log" 2>&1 && [ "$(wc -c <"$OUT/$n.m.bin")" -eq "$(wc -c <"$BIN/$f.BIN")" ]; then echo "$n $fl: ok (same length)"; else echo "$n $fl: FAILED"; tail -3 "$OUT/$n.m.log"; rc=1; fi
    done
  done
fi
# -DTITLESEL (title screen ship selection; hook code in the zero tail of MUSIQUEX) keeps the lengths, and the addresses musiquex.asm
# hard-codes for COMMONXX must be the real ones (English also with -DMISSIONS)
TSYMS=""; TFLAGS=()
case "$SRC" in
  "$ROOT/src/elite")    TSYMS="setCommandsCPL:4531 setCommandsNOP:4535 transferBuffertoScreen:1ED1 spawnCommandParser:809C dataFromPPI:8D2D splash2Shipnr:1DA8"; TFLAGS=("-DMISSIONS" "-DENHANCED -DMISSIONS");;
  "$ROOT/src/elite_de") TSYMS="setCommandsCPL:463E setCommandsNOP:4642 transferBuffertoScreen:1ED1 spawnCommandParser:81E3 dataFromPPI:8E75 splash2Shipnr:1DA8";;
  "$ROOT/src/elite_fr") TSYMS="setCommandsCPL:4664 setCommandsNOP:4668 transferBuffertoScreen:1ED1 spawnCommandParser:823C dataFromPPI:8ECC splash2Shipnr:1DA8";;
esac
if [ -n "$TSYMS" ]; then
  for fl in "" ${TFLAGS[@]+"${TFLAGS[@]}"}; do
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

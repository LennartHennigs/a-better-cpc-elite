#!/usr/bin/env bash
# Assemble src/elite*/*.asm with sjasmplus and compare with the original binaries.
# usage: bash tools/check_src.sh [de]     (no argument: stock English, src/elite vs work/bin_stock;
#                                          de: German, src/elite_de vs work/bin_german)
#        exit 0 only if all four files are byte-exact apart from the documented one-byte patches below
#        (src/elite and src/elite_fr have the one-byte CPC+ fix; the check expects it, see docs/_cpcplus.md)
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
  # COMMONXX carries two one-byte changes to the stock bytes; their runtime addresses come from the symbol table (nothing is hard-coded per build):
  #  - the CPC+ fix (ED 79 -> ED 49 in getPPI_Input, see docs/_cpcplus.md; the German stock disk already has it): the reference gets that byte;
  #  - ESC_KEYCODE (the key code of ESC in tblKeyboardmatrix: &FF = no key in the stock game, &7F here so that the buy, sell and equipment prompts leave on Escape).
  # The ESC change is proved, not patched into the reference: the build with -DESC_KEYCODE=0xFF must equal the reference, and the default build must differ from it in exactly one byte, the ESC byte, with the value &7F.
  sym() { awk -v k="$1:" '$2 == k || $1 == k { print $NF }' "$OUT/$n.sym"; }
  ESCP=$(( $(sym tblKeyboardmatrix) + 66 ))                  # row 8 bit 2 of the table
  [ "$SRC" != "$ROOT/src/elite_de" ] && printf '\x49' | dd of="$REF" bs=1 seek=$(( $(sym getPPI_Input) + 20 - 0x1A40 )) conv=notrunc 2>/dev/null
  if ! sjasmplus -DESC_KEYCODE=0xFF --raw="$OUT/$n.stock.bin" "$SRC/$n.asm" >/dev/null 2>&1 || ! cmp -s "$OUT/$n.stock.bin" "$REF"; then echo "$n -DESC_KEYCODE=0xFF: DIFFERS from the original"; rc=1
  elif [ "$(cmp -l "$OUT/$n.bin" "$REF" | awk '{print $1":"$2":"$3}')" = "$((ESCP-0x1A40+1)):177:377" ]; then echo "$n: ok"   # cmp -l: 1-based offset, octal values
  else echo "$n: DIFFERS (expected only the ESC byte)"; rc=1; fi
done
# English only: the -DMISSIONS variant (src/elite/missions_*.asm in the free tails) must keep both files the same length
if [ "$SRC" = "$ROOT/src/elite" ]; then
  for p in "largeaxx LARGEAXX" "commonxx COMMONXX"; do
    read -r n f <<<"$p"
    if sjasmplus -DMISSIONS --raw="$OUT/$n.m.bin" "$SRC/$n.asm" >"$OUT/$n.m.log" 2>&1 && [ "$(wc -c <"$OUT/$n.m.bin")" -eq "$(wc -c <"$BIN/$f.BIN")" ]; then echo "$n -DMISSIONS: ok (same length)"; else echo "$n -DMISSIONS: FAILED"; tail -3 "$OUT/$n.m.log"; rc=1; fi
  done
fi
# English only: -DTITLESEL (title screen ship selection; hook code in the zero tail of MUSIQUEX) keeps the lengths, and the
# addresses musiquex.asm hard-codes for COMMONXX must be the real ones
if [ "$SRC" = "$ROOT/src/elite" ]; then
  if sjasmplus -DTITLESEL --raw="$OUT/c.t.bin" --sym="$OUT/c.t.sym" "$SRC/commonxx.asm" >"$OUT/c.t.log" 2>&1 \
     && sjasmplus -DTITLESEL --raw="$OUT/m.t.bin" "$SRC/musiquex.asm" >"$OUT/m.t.log" 2>&1 \
     && [ "$(wc -c <"$OUT/c.t.bin")" -eq "$(wc -c <"$BIN/COMMONXX.BIN")" ] && [ "$(wc -c <"$OUT/m.t.bin")" -eq "$(wc -c <"$BIN/MUSIQUEX.BIN")" ]; then
    bad=0
    for pr in setCommandsCPL:4531 setCommandsNOP:4535 transferBuffertoScreen:1ED1 spawnCommandParser:809C dataFromPPI:8D2D splash2Shipnr:1DA8; do
      n=${pr%%:*}; v=${pr##*:}
      grep -qi "^$n: EQU 0x0000$v" "$OUT/c.t.sym" && grep -qi "^$n equ 0x$v" "$SRC/musiquex.asm" || { echo "TITLESEL: $n is not at &$v"; bad=1; }
    done
    [ $bad -eq 0 ] && echo "commonxx/musiquex -DTITLESEL: ok (same length, hook addresses match)" || rc=1
  else echo "-DTITLESEL: FAILED"; tail -3 "$OUT/c.t.log" "$OUT/m.t.log"; rc=1; fi
fi
# the three source trees must agree on the ESC default
if [ "$(grep -h '^ESC_KEYCODE equ' "$ROOT"/src/elite/commonxx.asm "$ROOT"/src/elite_de/commonxx.asm "$ROOT"/src/elite_fr/commonxx.asm | awk '{print $3}' | sort -u | wc -l)" -ne 1 ]; then echo "ESC_KEYCODE defaults differ between src/elite, src/elite_de and src/elite_fr"; rc=1; fi
rm -rf "$OUT"; exit $rc

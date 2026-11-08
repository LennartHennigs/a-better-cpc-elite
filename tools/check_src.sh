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
  if ! sjasmplus --raw="$OUT/$n.bin" "$SRC/$n.asm" >"$OUT/$n.log" 2>&1; then echo "$n: assemble FAILED"; tail -5 "$OUT/$n.log"; rc=1; continue; fi
  REF="$BIN/$f.BIN"
  # src/elite and src/elite_fr carry the one-byte CPC+ fix (ED 79 -> ED 49 in getPPI_Input, see docs/_cpcplus.md): the stock byte is expected to differ.
  # Runtime address of the patched byte: English &8DA0, French &8F3F. (German stock disk already has the fix, so it needs no exception.)
  # Both builds also carry the Escape key patch (the key code of ESC in tblKeyboardmatrix, &FF = no key, becomes &7F so that the buy, sell and equipment prompts leave on Escape):
  # runtime address of that byte: English &8C98, German &8DE0, French &8E37.
  REF="$OUT/$n.ref"; cp "$BIN/$f.BIN" "$REF"
  if [ "$n" = commonxx ]; then
    case "$SRC" in
      "$ROOT/src/elite")    CPCP=$((0x8DA0)); ESCP=$((0x8C98));;
      "$ROOT/src/elite_fr") CPCP=$((0x8F3F)); ESCP=$((0x8E37));;
      "$ROOT/src/elite_de") CPCP="";         ESCP=$((0x8DE0));;
    esac
    [ -n "$CPCP" ] && printf '\x49' | dd of="$REF" bs=1 seek=$((CPCP-0x1A40)) conv=notrunc 2>/dev/null
    printf '\x7F' | dd of="$REF" bs=1 seek=$((ESCP-0x1A40)) conv=notrunc 2>/dev/null
  fi
  if cmp -s "$OUT/$n.bin" "$REF"; then echo "$n: ok"; else echo "$n: DIFFERS"; rc=1; fi
done
rm -rf "$OUT"; exit $rc

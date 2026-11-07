#!/usr/bin/env bash
# Build Caprice32 (https://github.com/ColinPitrat/caprice32) from source on macOS, for testing disks.
# Run it yourself: bash scripts/install-caprice32.sh
# Needs: git, make, a C++ compiler, and Homebrew sdl2, freetype, libpng, pkgconf (brew install sdl2 freetype libpng pkgconf).
# Source is cloned to work/tools/src/caprice32 and built in place (its Makefile needs the source tree); the project root stays clean.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/work/tools/src/caprice32"
JOBS="$(sysctl -n hw.ncpu 2>/dev/null || echo 4)"
REF="${CAPRICE32_REF:-}"          # pin a tag or commit if you want, e.g. CAPRICE32_REF=v4.6.0

for tool in git make pkg-config; do
  command -v "$tool" >/dev/null || { echo "missing: $tool" >&2; exit 1; }
done
for lib in sdl2 freetype2 libpng; do
  pkg-config --exists "$lib" || { echo "missing library: $lib (brew install sdl2 freetype libpng)" >&2; exit 1; }
done

mkdir -p "$(dirname "$SRC")"
if [ -d "$SRC/.git" ]; then
  git -C "$SRC" fetch --depth 1 origin ${REF:+"$REF"}
  git -C "$SRC" checkout --quiet FETCH_HEAD
else
  git clone --depth 1 ${REF:+--branch "$REF"} https://github.com/ColinPitrat/caprice32.git "$SRC"
fi
echo "caprice32 at $(git -C "$SRC" rev-parse --short HEAD)"

make -C "$SRC" -j"$JOBS"
echo
echo "Built: $SRC/cap32"
echo "Run it from that folder (it finds roms/ and cap32.cfg there):"
echo "  cd \"$SRC\" && ./cap32 \"$ROOT/work/elite_plus.dsk\""
echo "CPC Plus: check the machine setting in the F1 menu (or the 'model' entry in cap32.cfg) for a 6128+/464+ option."

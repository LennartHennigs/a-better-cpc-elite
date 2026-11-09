#!/usr/bin/env bash
# Build and install sjasmplus and iDSK from source into ~/.local/bin (macOS, needs git and cmake).
# Run it yourself: bash scripts/install-tools.sh
# Sources are cloned into work/tools/src and built in work/tools/build, never in the project root.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/work/tools/src"
BUILD="$ROOT/work/tools/build"
BIN="${PREFIX_BIN:-$HOME/.local/bin}"
JOBS="$(sysctl -n hw.ncpu 2>/dev/null || echo 4)"

# Override to pin a tag or commit, e.g. SJASMPLUS_REF=v1.21.0
# Defaults are the versions this project was built and checked with (sjasmplus 1.24.0; the iDSK commit in use).
SJASMPLUS_REF="${SJASMPLUS_REF:-v1.24.0}"
IDSK_REF="${IDSK_REF:-bd620361720b2f45aafd9c100a1000c56957cb05}"

for tool in git cmake make; do
  command -v "$tool" >/dev/null || { echo "missing: $tool (brew install $tool)" >&2; exit 1; }
done

mkdir -p "$SRC" "$BUILD" "$BIN"

fetch() { # name url ref
  local name="$1" url="$2" ref="$3"
  if [ -d "$SRC/$name/.git" ]; then
    git -C "$SRC/$name" fetch --depth 1 origin ${ref:+"$ref"}
    git -C "$SRC/$name" checkout --quiet FETCH_HEAD
  else
    git clone "$url" "$SRC/$name"
    [ -z "$ref" ] || git -C "$SRC/$name" checkout --quiet "$ref"
  fi
  # sjasmplus vendors LuaBridge as a submodule; a plain shallow clone leaves it empty.
  git -C "$SRC/$name" submodule update --init --depth 1 --recursive
  echo "$name at $(git -C "$SRC/$name" rev-parse --short HEAD)"
}

build_cmake() { # name binary-name
  local name="$1" exe="$2"
  rm -rf "$BUILD/$name"
  cmake -S "$SRC/$name" -B "$BUILD/$name" -DCMAKE_BUILD_TYPE=Release
  cmake --build "$BUILD/$name" --parallel "$JOBS"
  local found
  found="$(find "$BUILD/$name" -type f -perm -u+x -iname "$exe" | head -n 1)"
  [ -n "$found" ] || { echo "built $name but could not find '$exe'" >&2; exit 1; }
  install -m 755 "$found" "$BIN/$exe"
  echo "installed $BIN/$exe"
}

fetch sjasmplus https://github.com/z00m128/sjasmplus.git "$SJASMPLUS_REF"
build_cmake sjasmplus sjasmplus

fetch idsk https://github.com/cpcsdk/idsk.git "$IDSK_REF"
build_cmake idsk iDSK

echo
case ":$PATH:" in
  *":$BIN:"*) ;;
  *) echo "Add to your shell profile:  export PATH=\"$BIN:\$PATH\"" ;;
esac
"$BIN/sjasmplus" --version 2>&1 | head -n 1 || true
"$BIN/iDSK" 2>&1 | head -n 2 || true

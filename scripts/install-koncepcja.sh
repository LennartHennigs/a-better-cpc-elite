#!/usr/bin/env bash
# Build konCePCja (https://github.com/ikari-pl/konCePCja), a pin-level CPC emulator with a TCP IPC server, into work/ext_koncepcja/.
# Used as a second opinion next to cpcxray for raster-timing effects (colour split bands, interrupt phase); IPC notes in docs/_build.md.
# Source-available licence (personal and hobby use): do not copy it into the repo or publish builds. Run it yourself: ! bash scripts/install-koncepcja.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/work/ext_koncepcja"
brew install freetype zlib libpng cmake
if [ ! -d "$DEST/.git" ]; then
  git clone --recurse-submodules https://github.com/ikari-pl/konCePCja.git "$DEST"
fi
cd "$DEST"
(cd vendor/SDL && cmake -B build -DCMAKE_BUILD_TYPE=Release -DSDL_SHARED=ON -DSDL_STATIC=OFF -DCMAKE_INSTALL_PREFIX="$(pwd)/install" \
  && cmake --build build -j"$(sysctl -n hw.ncpu)" && cmake --install build)
make ARCH=macos APP_PATH="$PWD" -j"$(sysctl -n hw.ncpu)"
ls -l "$DEST/koncepcja"
echo "built. Try: $DEST/koncepcja --headless   (IPC on port 6543)"

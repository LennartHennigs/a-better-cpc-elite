#!/usr/bin/env bash
# Installs CDTconvert (CDT/TZX tape image -> WAV, https://github.com/lastic/CDTconvert, MIT) into ~/.local/bin.
# Uses the v1.0 macOS arm64 release; falls back to building the source with make.
# Run it yourself: ! bash scripts/install-cdtconvert.sh
set -euo pipefail

DEST="$HOME/.local/bin"
URL="https://github.com/lastic/CDTconvert/releases/download/v1.0/CDTconvert-1.0-macos-arm64.zip"
SHA256="37cfeeb384a0e9c13a01cfa52cb12ffb68b65d5f46b26c727e2c04bfb59a258b"   # of that zip, taken 2026-11-15 on the first download (the project publishes none)
REF="282e3af1a9a2a550679985a46f619b2db7bbff4e"   # commit of tag v1.0, for the source fallback
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$DEST"

install_release() {
    curl -fsSL -o "$TMP/cdt.zip" "$URL" || return 1
    [ "$(shasum -a 256 "$TMP/cdt.zip" | cut -d' ' -f1)" = "$SHA256" ] || { echo "checksum mismatch for $URL" >&2; return 1; }
    mkdir "$TMP/rel"
    unzip -q "$TMP/cdt.zip" -d "$TMP/rel" || return 1
    BIN="$(find "$TMP/rel" -type f -name 'CDTconvert' | head -1)"
    [ -n "$BIN" ] || return 1
    xattr -d com.apple.quarantine "$BIN" 2>/dev/null || true
    chmod +x "$BIN"
    cp "$BIN" "$DEST/CDTconvert"
    "$DEST/CDTconvert" -v >/dev/null 2>&1
}

install_source() {
    git clone --quiet https://github.com/lastic/CDTconvert "$TMP/src"
    git -C "$TMP/src" checkout --quiet "$REF"
    (cd "$TMP/src" && make)
    BIN="$(find "$TMP/src" -type f -name 'CDTconvert' -perm -u+x | head -1)"
    cp "$BIN" "$DEST/CDTconvert"
}

if install_release; then
    echo "installed release build"
else
    echo "release install failed, building from source"
    install_source
fi

"$DEST/CDTconvert" -v
echo "CDTconvert is at $DEST/CDTconvert (add $DEST to PATH if it is not there)"

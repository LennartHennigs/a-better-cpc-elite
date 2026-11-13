#!/usr/bin/env bash
# Assemble src/elite128 (the 128K fork, src/elite128/README.md) and report each file's size next to the same file from src/elite.
# usage: bash tools/check_src128.sh [--strict]
#   Smoke test, not a byte compare: the fork is meant to diverge. Without --strict it only needs every file to assemble (exit 1 otherwise).
#   --strict also requires the output to equal src/elite's (useful right after forking, before the first change).
# The 128K build has one variant; its flags are in src/elite128/config.inc (the src/elite reference is assembled without flags: only the size column is meaningful).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT=0; [ "${1:-}" = "--strict" ] && STRICT=1
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
export PATH="$HOME/.local/bin:$PATH"
rc=0
# generated, third-party derived inputs (work/elite128/, never committed): the blueprints that commonxx.asm includes and the bank 6 fill records
python3 -I "$ROOT/tools/ship128.py" >/dev/null || { echo "ship128.py FAILED"; exit 1; }
for p in "largeaxx" "commonxx" "common2x" "musiquex"; do
  set -- $p; n=$1; shift
  if ! sjasmplus "$@" --raw="$OUT/$n.128" "$ROOT/src/elite128/$n.asm" >"$OUT/$n.128.log" 2>&1; then echo "$n: assemble FAILED"; tail -5 "$OUT/$n.128.log"; rc=1; continue; fi
  sjasmplus "$@" --raw="$OUT/$n.ref" "$ROOT/src/elite/$n.asm" >/dev/null 2>&1
  a=$(wc -c <"$OUT/$n.128"); b=$(wc -c <"$OUT/$n.ref")
  if cmp -s "$OUT/$n.128" "$OUT/$n.ref"; then echo "$n: $a bytes, same as src/elite"; else echo "$n: $a bytes (src/elite: $b), differs"; [ $STRICT = 1 ] && rc=1; fi
done
# the bank 6 module needs the address of the resident vertex buffer from commonxx.asm
sjasmplus --raw="$OUT/c.bin" --sym="$OUT/c.sym" "$ROOT/src/elite128/commonxx.asm" >/dev/null 2>&1
VB=$(awk '$1 == "hullVertexBuf:" || $2 == "hullVertexBuf:" { print $NF }' "$OUT/c.sym")
sym() { awk -v n="$1:" '$1 == n || $2 == n { print $NF }' "$OUT/c.sym"; }
# every symbol the flip module needs must exist: an empty one would make the shell arithmetic below silently 0 (a module that pokes address 0)
for n in curCfg dbOn dbShown dbCnt dbCopy dbScanFlag missileCount FlagStationNear missileLockState pressedKey splash2Shipnr printSplashscreen1 printPressSpace movementspeed todoLaunchFlag hullVertexBuf; do
  [ -n "$(sym $n)" ] || { echo "fill: symbol $n missing in commonxx.asm (renamed?)"; exit 1; }
done
DBDEF="-DDB_CURCFG=$(($(sym curCfg))) -DDB_ON=$(($(sym dbOn))) -DDB_SHOWN=$(($(sym dbShown))) -DDB_CNT=$(($(sym dbCnt))) -DDB_COPY=$(($(sym dbCopy))) -DDB_SCAN=$(($(sym dbScanFlag))) -DDB_MISS=$(($(sym missileCount))) -DDB_STAT=$(($(sym FlagStationNear))) -DDB_LOCK=$(($(sym missileLockState))) -DDB_KEY=$(($(sym pressedKey))) -DDB_SHIPNR=$(($(sym splash2Shipnr))) -DDB_PRT1=$(($(sym printSplashscreen1))) -DDB_PRT2=$(($(sym printPressSpace))) -DDB_VARS=$(($(sym movementspeed))) -DDB_VLEN=$(($(sym todoLaunchFlag) - $(sym movementspeed)))"
if [ -n "$VB" ] && sjasmplus -DVBUF=$((VB)) $DBDEF --raw="$ROOT/work/elite128/fill.bin" --sym="$ROOT/work/elite128/fill.sym" "$ROOT/src/elite128/fill.asm" >"$OUT/fill.log" 2>&1; then echo "fill: $(wc -c <"$ROOT/work/elite128/fill.bin") bytes (VBUF=$VB)"
  DBB=$(awk '$1 == "dbBases:" || $2 == "dbBases:" { print $NF }' "$ROOT/work/elite128/fill.sym")
  if sjasmplus -DDBBASES=$((DBB)) -DDB_CURCFG=$(($(sym curCfg))) -DDB_COPY=$(($(sym dbCopy))) -DDB_SHIPNR=$(($(sym splash2Shipnr))) -DDB_PRT1=$(($(sym printSplashscreen1))) -DDB_PRT2=$(($(sym printPressSpace))) -DDB_SEEN=$(($(sym titleSeen))) --raw="$ROOT/work/elite128/tt.bin" "$ROOT/src/elite128/fill_tt.asm" >"$OUT/tt.log" 2>&1; then echo "tt: $(wc -c <"$ROOT/work/elite128/tt.bin") bytes"; else echo "tt: assemble FAILED"; tail -3 "$OUT/tt.log"; rc=1; fi
else echo "fill: assemble FAILED"; tail -3 "$OUT/fill.log"; rc=1; fi
exit $rc

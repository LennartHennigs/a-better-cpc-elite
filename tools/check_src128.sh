#!/usr/bin/env bash
# Assemble src/elite128 (the 128K fork, src/elite128/README.md) and report each file's size next to the same file from src/elite.
# usage: [HULLS=stock|arcelite] bash tools/check_src128.sh [--strict]      (HULLS: where the filled hulls come from, default stock; tools/ship128.py)
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
# LISTDIR=dir: also write an sjasmplus listing per module there (used by tools/listing6128.sh, `make listing6128`); unset = nothing changes
LST=()
lst() { LST=(); if [ -n "${LISTDIR:-}" ]; then mkdir -p "$LISTDIR"; LST=("--lst=$LISTDIR/$1.lst" --lstlab); fi; return 0; }
# generated, third-party derived inputs (work/elite128/, never committed): the blueprints that commonxx.asm includes and the bank 6 fill records
HULLS="${HULLS:-stock}"      # hull source: stock (the CPC's own blueprints, the default) or arcelite (ArcElite's hulls, needs work/arcelite/): tools/ship128.py
python3 -I "$ROOT/tools/ship128.py" --source "$HULLS" >/dev/null || { echo "ship128.py FAILED (HULLS=$HULLS)"; exit 1; }
echo "hulls: $HULLS"
for p in "largeaxx" "commonxx" "common2x" "musiquex"; do
  set -- $p; n=$1; shift
  lst $n
  if ! sjasmplus "$@" ${LST[@]+"${LST[@]}"} --raw="$OUT/$n.128" "$ROOT/src/elite128/$n.asm" >"$OUT/$n.128.log" 2>&1; then echo "$n: assemble FAILED"; tail -5 "$OUT/$n.128.log"; rc=1; continue; fi
  sjasmplus "$@" --raw="$OUT/$n.ref" "$ROOT/src/elite/$n.asm" >/dev/null 2>&1
  a=$(wc -c <"$OUT/$n.128"); b=$(wc -c <"$OUT/$n.ref")
  if cmp -s "$OUT/$n.128" "$OUT/$n.ref"; then echo "$n: $a bytes, same as src/elite"; else echo "$n: $a bytes (src/elite: $b), differs"; [ $STRICT = 1 ] && rc=1; fi
done
# the bank 6 module needs the address of the resident vertex buffer from commonxx.asm
sjasmplus --raw="$OUT/c.bin" --sym="$OUT/c.sym" "$ROOT/src/elite128/commonxx.asm" >/dev/null 2>&1
cp "$OUT/c.sym" "$ROOT/work/elite128/c128.sym" 2>/dev/null     # tools/rvmstate.py --curcfg reads curCfg from here (c.sym there is ship128.py's stock one: do not overwrite it)
VB=$(awk '$1 == "hullVertexBuf:" || $2 == "hullVertexBuf:" { print $NF }' "$OUT/c.sym")
sym() { awk -v n="$1:" '$1 == n || $2 == n { print $NF }' "$OUT/c.sym"; }
# every symbol the flip module needs must exist: an empty one would make the shell arithmetic below silently 0 (a module that pokes address 0)
for n in curCfg dbOn dbShown dbCnt dbCopy dbScanFlag missileCount FlagStationNear missileLockState pressedKey splash2Shipnr printSplashscreen1 printPressSpace movementspeed todoLaunchFlag hullVertexBuf; do
  [ -n "$(sym $n)" ] || { echo "fill: symbol $n missing in commonxx.asm (renamed?)"; exit 1; }
done
DBDEF="-DDB_CURCFG=$(($(sym curCfg))) -DDB_ON=$(($(sym dbOn))) -DDB_SHOWN=$(($(sym dbShown))) -DDB_CNT=$(($(sym dbCnt))) -DDB_COPY=$(($(sym dbCopy))) -DDB_SCAN=$(($(sym dbScanFlag))) -DDB_MISS=$(($(sym missileCount))) -DDB_STAT=$(($(sym FlagStationNear))) -DDB_LOCK=$(($(sym missileLockState))) -DDB_KEY=$(($(sym pressedKey))) -DDB_SHIPNR=$(($(sym splash2Shipnr))) -DDB_PRT1=$(($(sym printSplashscreen1))) -DDB_PRT2=$(($(sym printPressSpace))) -DDB_VARS=$(($(sym movementspeed))) -DDB_VLEN=$(($(sym todoLaunchFlag) - $(sym movementspeed)))"
lst fill
if [ -n "$VB" ] && sjasmplus -DVBUF=$((VB)) $DBDEF ${LST[@]+"${LST[@]}"} --raw="$ROOT/work/elite128/fill.bin" --sym="$ROOT/work/elite128/fill.sym" "$ROOT/src/elite128/fill.asm" >"$OUT/fill.log" 2>&1; then echo "fill: $(wc -c <"$ROOT/work/elite128/fill.bin") bytes (VBUF=$VB)"
  DBB=$(awk '$1 == "dbBases:" || $2 == "dbBases:" { print $NF }' "$ROOT/work/elite128/fill.sym")
  lst tt
  if sjasmplus -DDBBASES=$((DBB)) -DDB_CURCFG=$(($(sym curCfg))) -DDB_COPY=$(($(sym dbCopy))) -DDB_SHIPNR=$(($(sym splash2Shipnr))) -DDB_PRT1=$(($(sym printSplashscreen1))) -DDB_PRT2=$(($(sym printPressSpace))) -DDB_SEEN=$(($(sym titleSeen))) ${LST[@]+"${LST[@]}"} --raw="$ROOT/work/elite128/tt.bin" "$ROOT/src/elite128/fill_tt.asm" >"$OUT/tt.log" 2>&1; then echo "tt: $(wc -c <"$ROOT/work/elite128/tt.bin") bytes"; else echo "tt: assemble FAILED"; tail -3 "$OUT/tt.log"; rc=1; fi
else echo "fill: assemble FAILED"; tail -3 "$OUT/fill.log"; rc=1; fi
# cross-file equ lines (common2x.asm, largeaxx.asm) go stale when commonxx.asm changes size: everything assembles, the game crashes at runtime
if python3 -I "$ROOT/tools/sync_equs.py" "$ROOT/src/elite128" --check >"$OUT/equs.log" 2>&1; then echo "equs: in sync"; else echo "equs: STALE or sync_equs.py failed (fix: python3 -I tools/sync_equs.py src/elite128 --write)"; tail -8 "$OUT/equs.log"; rc=1; fi
# the trainer's poke addresses and the save key in src/cheats must match this source (tools/cheat128.py derives them; fix: tools/mk_editsave.py, mk_listsave.py, mk_convsave.py, the 830 line of CHEATB.ASC, then bash tools/build_cheat.sh)
if python3 -I "$ROOT/tools/cheat128.py" --check >"$OUT/cheat.log" 2>&1; then echo "trainer and save tools: match the source"; else echo "trainer and save tools: STALE"; cat "$OUT/cheat.log"; rc=1; fi
exit $rc

#!/bin/bash
# Build SHOWSHPS.BAS for the 128K disk: the loader of the ship viewer (src/viewer128/SHOWSHPS.ASC: the ships into RAM banks 4-6, viewer.bin at &8000, CALL &8000, Q returns).
# src/viewer128/SHOWSHPS.ASC (CRLF lines, Ctrl-Z at the end) is tokenised with the CPC's own BASIC (cpcxray headless, as tools/build_cheat.sh does):
# output src/viewer128/SHOWSHPS.BAS (AMSDOS header) and SHOWSHPS.BAS.txt (listing). tools/build_dsk128.py puts it on the disk with the ship data (tools/mk_viewer128.py, src/viewer128/viewer.asm).
set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"   # absolute: in a worktree work/xray is a symlink into the main checkout, so ../../tools from there is the main checkout's
export PATH="$HOME/.local/bin:$PATH"
D=src/viewer128
P=SHOWSHPS
rm -f work/tmp_asc.dsk work/xray/disk/tmp_asc.dsk work/xray/disk/tmp_tok.dsk
iDSK work/tmp_asc.dsk -n >/dev/null 2>&1
iDSK work/tmp_asc.dsk -i $D/$P.ASC -t 0 >/dev/null 2>&1
cp work/tmp_asc.dsk work/xray/disk/tmp_asc.dsk
(cd work/xray && PROG=$P ~/.local/share/uv/tools/cpcxray/bin/python -I "$ROOT/tools/cheat_tokenise.py")
rm -rf work/tmp_tok; mkdir work/tmp_tok
python3 -I tools/dskx.py work/xray/disk/tmp_tok.dsk work/tmp_tok >/dev/null
cp work/tmp_tok/$P.BAS.raw $D/$P.BAS
python3 -I tools/bastok.py $D/$P.BAS --header > $D/$P.BAS.txt
echo "built $D/$P.BAS ($(wc -c < $D/$P.BAS) bytes with header)"
rm -rf work/tmp_asc.dsk work/tmp_tok work/xray/disk/tmp_asc.dsk work/xray/disk/tmp_tok.dsk

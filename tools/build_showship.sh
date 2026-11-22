#!/bin/bash
# Build the ship viewer: work/showship/SHIPS.BIN and src/cheats/SHOWSHPS.ASC (tools/mk_showship.py), tokenise the program with the CPC's own BASIC (cpcxray headless,
# as tools/build_cheat.sh does), write src/cheats/SHOWSHPS.BAS and its listing, and put both on work/showship.dsk (a blank data disk; SHOWSHPS.BAS visible, SHIPS.BIN
# System-hidden like every other non-BAS file). Run it with `RUN"SHOWSHPS`.
set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"   # absolute: in a worktree work/xray is a symlink into the main checkout, so ../../tools from there is the main checkout's
export PATH="$HOME/.local/bin:$PATH"
D=src/cheats
P=SHOWSHPS
python3 -I tools/mk_showship.py
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
rm -f work/showship.dsk
iDSK work/showship.dsk -n >/dev/null 2>&1   # a blank data disk: the Firebird disk has two tracks with odd sector ids that iDSK may fill, and AMSDOS cannot read them
iDSK work/showship.dsk -i $D/$P.BAS -t 2 -f >/dev/null
iDSK work/showship.dsk -i work/showship/SHIPS.BIN -t 1 -c 4000 -e 4000 -f >/dev/null
python3 -I tools/hide_files.py work/showship.dsk
rm -rf work/tmp_asc.dsk work/tmp_tok work/xray/disk/tmp_asc.dsk work/xray/disk/tmp_tok.dsk
echo "built work/showship.dsk (RUN\"SHOWSHPS)"

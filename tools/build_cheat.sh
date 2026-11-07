#!/bin/bash
# Rebuild CHEAT.BAS from its ASCII source and a test disk with it added.
#   source : src/cheats/CHEAT.ASC  (edit this, CRLF lines, ends with Ctrl-Z)
#   output : src/cheats/CHEAT.BAS (AMSDOS header) and .txt (listing)
#            work/firebird_cheat.dsk  (copy of the Firebird disk plus CHEAT.BAS)
# The CPC's own BASIC does the tokenising (cpcxray headless), so the result is a real tokenised file.
set -e
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
D=src/cheats
DISK=Elite_UK_Firebird_cracked_trainer.dsk
rm -f work/tmp_asc.dsk work/xray/disk/tmp_asc.dsk work/xray/disk/tmp_tok.dsk
iDSK work/tmp_asc.dsk -n >/dev/null 2>&1
iDSK work/tmp_asc.dsk -i $D/CHEAT.ASC -t 0 >/dev/null 2>&1
cp work/tmp_asc.dsk work/xray/disk/tmp_asc.dsk
(cd work/xray && ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/cheat_tokenise.py)
rm -rf work/tmp_tok; mkdir work/tmp_tok
python3 -I tools/dskx.py work/xray/disk/tmp_tok.dsk work/tmp_tok >/dev/null
cp work/tmp_tok/CHEAT.BAS.raw $D/CHEAT.BAS
python3 -I tools/bastok.py $D/CHEAT.BAS --header > $D/CHEAT.BAS.txt
cp $DISK work/firebird_cheat.dsk
iDSK work/firebird_cheat.dsk -i $D/CHEAT.BAS -t 2 -f >/dev/null 2>&1
cp work/firebird_cheat.dsk work/xray/disk/firebird_cheat.dsk
rm -rf work/tmp_asc.dsk work/tmp_tok work/xray/disk/tmp_asc.dsk work/xray/disk/tmp_tok.dsk
echo "built $D/CHEAT.BAS ($(wc -c < $D/CHEAT.BAS) bytes with header) and work/firebird_cheat.dsk"

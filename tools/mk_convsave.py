#!/usr/bin/env python3
"""Generate src/cheats/CONVSAVE.ASC: a CPC BASIC program that converts a commander save between the builds (UK, French, German, 128K).

Every build encrypts the 104-byte save with its own key (the code at EquipShip), so a save of one build does not load in another. The program asks for the disk with the save,
finds the build whose key makes both checksums verify, asks for the target build, encrypts again (the plain data and both checksums stay as they are) and asks for the disk to
write to (the same or another one) before it SAVEs. The host counterpart is `tools/saveedit.py edit SAVE --to-key-disk GAME.dsk` (the converter is tested against it).
usage: python3 -I tools/mk_convsave.py        (then bash tools/build_cheat.sh tokenises it)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import savekeys  # noqa: E402

LINES = [
    '10 MODE 1:PRINT"CONVERT A SAVE (UK, FR, DE, 128K)":PRINT',
    '15 PRINT"Put the disk with the save in":PRINT"drive A, then press a key.":CALL &BB18:PRINT',
    '20 INPUT"Save file (e.g. PETER.BIN)";f$:f$=UPPER$(f$)',
    '30 MEMORY &5FFF:DIM p(103),k(103,4),n$(4):ON ERROR GOTO 900',
    '40 LOAD f$,&6000:ON ERROR GOTO 0',
    '50 RESTORE:FOR b=1 TO 4:READ n$(b),k$:FOR i=0 TO 103:k(i,b)=VAL("&"+MID$(k$,2*i+1,2)):NEXT:NEXT',
    '60 FOR b=1 TO 4:FOR i=0 TO 103:p(i)=PEEK(&6000+i) XOR k(i,b):NEXT',
    '70 x=0:s=0:FOR i=0 TO 101:x=x XOR p(i):s=s+p(i):NEXT',
    '80 IF x=p(102) AND ((s+p(102)) AND 255)=p(103) THEN 110',
    '90 NEXT:PRINT"No UK, French, German or 128K key fits this file":END',
    '110 PRINT"Build:  ";n$(b):PRINT"Name:   ";:i=0:WHILE p(i)>0 AND i<10:PRINT CHR$(p(i));:i=i+1:WEND:PRINT:PRINT',
    '120 PRINT"1 UK  2 French  3 German  4 128K":INPUT"Convert to (1-4)";t:t=INT(t)',
    '130 IF t<1 OR t>4 THEN 120',
    '135 IF t=b THEN PRINT"Already a ";n$(b);" save":END',
    '140 INPUT"New file name (Enter = same)";g$:g$=UPPER$(g$):IF g$="" THEN g$=f$',
    '150 FOR i=0 TO 103:POKE &6000+i,p(i) XOR k(i,t):NEXT',
    '160 PRINT"Put the disk to save to in drive A,":PRINT"then press a key.":CALL &BB18',
    '170 ON ERROR GOTO 900:SAVE g$,b,&6000,104:PRINT"Saved ";g$;" as ";n$(t):END',
    '900 PRINT"Cannot load or save ";f$:END',
]

if __name__ == "__main__":
    savekeys.write_asc("CONVSAVE", LINES + savekeys.key_data_lines(300))

#!/usr/bin/env python3
"""Generate src/cheats/EDITSAVE.ASC: a CPC BASIC save editor (the on-CPC counterpart of tools/saveedit.py).

It loads a commander save, finds the build (UK, French or German) whose key makes both checksums verify, shows kills, jumps, cash, legal status and the added-mission state, asks for new values (Enter keeps the old one),
recomputes both checksums, encrypts again and writes the file back with SAVE (AMSDOS keeps the old file as .BAK). Use a copy of the disk. Keys come from the game disks as in tools/mk_showsave.py.
usage: python3 -I tools/mk_editsave.py        (then bash tools/build_cheat.sh)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mk_showsave  # noqa: E402

lines = [
    '10 MODE 1:PRINT"EDIT SAVE (work on a copy of the disk)":PRINT',
    '20 INPUT"Save file (e.g. PETER.BIN)";f$',
    '30 MEMORY &5FFF:DIM p(103),k(103):ON ERROR GOTO 900',
    '40 LOAD f$,&6000:ON ERROR GOTO 0',
    '50 RESTORE:FOR b=1 TO 3:READ n$,k$',
    '60 FOR i=0 TO 103:k(i)=VAL("&"+MID$(k$,2*i+1,2)):p(i)=PEEK(&6000+i) XOR k(i):NEXT',
    '70 x=0:s=0:FOR i=0 TO 101:x=x XOR p(i):s=s+p(i):NEXT',
    '80 IF x=p(102) AND ((s+p(102)) AND 255)=p(103) THEN 110',
    '90 NEXT:PRINT"No UK, French or German key fits this file":END',
    '110 PRINT"Build:  ";n$:i=0:PRINT"Name:   ";:WHILE p(i)>0 AND i<10:PRINT CHR$(p(i));:i=i+1:WEND:PRINT',
    '120 PRINT"Kills:  ";p(13)+256*p(14):PRINT"Jumps:  ";p(15)+256*p(16)',
    '130 PRINT"Cash:   ";(p(18)+256*p(19))*1000+(p(20)+256*p(21))/10;"Cr":PRINT"Legal:  ";p(11):PRINT"Mission bytes: ";p(50);p(51):PRINT',
    '140 PRINT"Enter keeps the old value":PRINT',
    '150 INPUT"Kills (<32768)";a$:IF a$<>"" THEN v=MIN(INT(VAL(a$)),32767):p(13)=v-256*INT(v/256):p(14)=INT(v/256)',
    '160 INPUT"Jumps (<32768)";a$:IF a$<>"" THEN v=MIN(INT(VAL(a$)),32767):p(15)=v-256*INT(v/256):p(16)=INT(v/256)',
    '170 INPUT"Cash Cr";a$:IF a$<>"" THEN c=INT(MIN(VAL(a$),6.5E7)*10):u=INT(c/10000):v=c-u*1E4:p(18)=u-256*INT(u/256):p(19)=INT(u/256):p(20)=v-256*INT(v/256):p(21)=INT(v/256)',
    '180 INPUT"Legal status 0-255";a$:IF a$<>"" THEN p(11)=MIN(INT(VAL(a$)),255)',
    '190 INPUT"Own cloak y/n";a$:a$=UPPER$(a$):IF a$="Y" THEN p(92)=(p(92) AND 191)+64 ELSE IF a$="N" THEN p(92)=p(92) AND 191',
    '200 INPUT"Added missions 0-4";a$:IF a$="" THEN 250',
    '210 z=INT(VAL(a$)):IF z<0 OR z>4 THEN 250',
    '220 p(50)=2-44*(z>1)-48*(z>2):p(51)=-3*(z=4):IF z=0 THEN p(50)=0',
    '230 IF z>1 THEN p(55)=254',
    '250 x=0:s=0:FOR i=0 TO 101:x=x XOR p(i):s=s+p(i):NEXT:p(102)=x:p(103)=(s+x) AND 255',
    '260 FOR i=0 TO 103:POKE &6000+i,p(i) XOR k(i):NEXT',
    '270 SAVE f$,b,&6000,104:PRINT"Saved ";f$:END',
    '900 PRINT"Cannot load or save ";f$:END',
]
mk_showsave.write_asc("EDITSAVE", lines + mk_showsave.key_data_lines())

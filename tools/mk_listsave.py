#!/usr/bin/env python3
"""Generate src/cheats/LISTSAVE.ASC: a CPC BASIC program that lists every commander save on the disk in drive A.

It prints a note in pen 2 (MODE 1) and runs CAT with pen 1 hidden (INK 1 = paper colour), reads the catalogue back from the screen (COPYCHR$), clears the screen, prints how many files it will check, loads each file that is not .BAS or .TXT and that CAT shows as 1K (a save is 104 bytes plus the 128-byte AMSDOS header = 232 bytes, so 1K) to &6000 and decodes it with the UK, French
and German save keys (same test as SHOWSAVE: both checksums must verify). One line per save: file, build, kills, cash.
Bigger files are skipped by the size test, small ones that are not saves are marked. System (hidden) files do not show in CAT, so the saves must be visible on the disk; the size test also keeps a large .BIN from being loaded over BASIC's memory.
usage: python3 -I tools/mk_listsave.py        (then tools/build_cheat.sh tokenises it and puts LISTSAVE.BAS on work/de_savegames.dsk)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mk_showsave  # noqa: E402

LINES = [
    '10 MODE 1:PEN 2:PRINT"LIST SAVES":PRINT:PRINT"Reading the catalogue, please wait...":PEN 1:INK 1,1:CAT',
    '20 MEMORY &5FFF:DIM p(103),n$(40),o$(3):FOR b=1 TO 3:READ o$(b),k$:FOR i=0 TO 103:POKE &6100+104*b+i,VAL("&"+MID$(k$,2*i+1,2)):NEXT:NEXT',
    '30 r=VPOS(#0)-1:FOR y=4 TO r:l$="":FOR x=1 TO 40:LOCATE x,y:l$=l$+COPYCHR$(#0):NEXT',
    '40 i=INSTR(l$,"."):WHILE i>0',
    '50 e$=MID$(l$,i+1,3):z=VAL(MID$(l$,i+4,5)):IF i>8 AND z=1 AND e$<>"BAS" AND e$<>"TXT" AND c<40 THEN GOSUB 300',
    '60 i=INSTR(i+1,l$,"."):WEND:NEXT',
    '70 CLS:INK 1,24:PRINT"LIST SAVES":PRINT:PRINT"Files to check:";c:PRINT"This takes a few seconds per file.":PRINT:PRINT"File         Build    Kills Cash":ON ERROR GOTO 200',
    '80 FOR f=1 TO c:PRINT n$(f);SPACE$(13-LEN(n$(f)));:GOSUB 400:NEXT:END',
    '200 PRINT"cannot load":RESUME NEXT',
    '300 m$=MID$(l$,i-8,8):WHILE RIGHT$(m$,1)=" ":m$=LEFT$(m$,LEN(m$)-1):WEND',
    '310 c=c+1:n$(c)=m$+"."+e$:RETURN',
    '400 LOAD n$(f),&6000:b=0',
    '410 b=b+1:IF b>3 THEN PRINT"not a save":RETURN',
    '420 FOR i=0 TO 103:p(i)=PEEK(&6000+i) XOR PEEK(&6100+104*b+i):NEXT',
    '430 x=0:s=0:FOR i=0 TO 101:x=x XOR p(i):s=s+p(i):NEXT',
    '440 IF x<>p(102) OR ((s+p(102)) AND 255)<>p(103) THEN 410',
    '460 PRINT o$(b);SPACE$(9-LEN(o$(b)));',
    '470 PRINT p(13)+256*p(14);" ";(p(18)+256*p(19))*1000+(p(20)+256*p(21))/10;"Cr":RETURN',
]

if __name__ == "__main__":
    mk_showsave.write_asc("LISTSAVE", LINES + mk_showsave.key_data_lines(600))

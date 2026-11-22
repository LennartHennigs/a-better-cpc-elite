#!/usr/bin/env python3
"""Generate src/cheats/LISTSAVE.ASC: a CPC BASIC program that lists every commander save on the disk in drive A (file, build, kills, cash).

One page, no CLS, no colour changes and no catalogue on screen. The program needs the directory (BASIC has no other way to get the file names), so it runs CAT into a
screen buffer that is not displayed: MEMORY &3FFF keeps BASIC out of &4000-&7FFF, a 6-byte stub (LD A,&40 / CALL &BC08 = SCR SET BASE / RET at &9000, the same with &C0 at
&9006) moves the firmware's text output there, two OUTs keep the CRTC showing &C000, CAT prints into the hidden buffer, COPYCHR$ reads it back, and the stub at &9006 returns
the output to the visible screen. The visible page is the title, the note ("This takes a few seconds per file"), "Files to check: n" and the table.
Each file that is not .BAS or .TXT and that CAT shows as 1K (a save is 104 bytes plus the 128-byte AMSDOS header = 232 bytes, so 1K) is loaded to &9100 and decoded with the
UK, French, German and 128K save keys (kept at &9200+); both checksums must verify. Bigger files are skipped by the size test, small ones that are not saves are marked. System
(hidden) files do not show in CAT, so the saves must be visible on the disk.
usage: python3 -I tools/mk_listsave.py        (then tools/build_cheat.sh tokenises it and puts LISTSAVE.BAS on work/de_savegames.dsk)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import savekeys  # noqa: E402

LINES = [
    '10 MODE 1:MEMORY &3FFF:PRINT"LIST SAVES":PRINT:PRINT"This takes a few seconds per file.":PRINT:PRINT"Reading the catalogue..."',
    '20 DIM p(103),n$(40),o$(4),l$(30):FOR b=1 TO 4:READ o$(b),k$:FOR i=0 TO 103:POKE &9200+104*b+i,VAL("&"+MID$(k$,2*i+1,2)):NEXT:NEXT:FOR i=0 TO 11:READ a:POKE &9000+i,a:NEXT',
    '30 CALL &9000:OUT &BC00,12:OUT &BD00,&30:CLS:CAT',
    '32 r=VPOS(#0)-1:FOR y=1 TO r:FOR x=1 TO 40:LOCATE x,y:l$(y)=l$(y)+COPYCHR$(#0):NEXT:NEXT',
    '34 CALL &9006:OUT &BC00,12:OUT &BD00,&30',
    '40 FOR y=1 TO r:l$=l$(y):i=INSTR(l$,"."):WHILE i>0',
    '50 e$=MID$(l$,i+1,3):z=VAL(MID$(l$,i+4,5)):IF i>8 AND z=1 AND e$<>"BAS" AND e$<>"TXT" AND c<40 THEN GOSUB 300',
    '60 i=INSTR(i+1,l$,"."):WEND:NEXT',
    '70 LOCATE 1,5:PRINT"Files to check:";c;SPACE$(10):PRINT:PRINT"File";TAB(14);"Build";TAB(21);"Kills";TAB(32);"Cash Cr":ON ERROR GOTO 200',
    '80 FOR f=1 TO c:PRINT n$(f);:GOSUB 400:NEXT:END',
    '200 PRINT"cannot load":RESUME NEXT',
    '300 m$=MID$(l$,i-8,8):WHILE RIGHT$(m$,1)=" ":m$=LEFT$(m$,LEN(m$)-1):WEND',
    '310 c=c+1:n$(c)=m$+"."+e$:RETURN',
    '400 LOAD n$(f),&9100:b=0',
    '410 b=b+1:IF b>4 THEN PRINT TAB(14);"not a save":RETURN',
    '420 FOR i=0 TO 103:p(i)=PEEK(&9100+i) XOR PEEK(&9200+104*b+i):NEXT',
    '430 x=0:s=0:FOR i=0 TO 101:x=x XOR p(i):s=s+p(i):NEXT',
    '440 IF x<>p(102) OR ((s+p(102)) AND 255)<>p(103) THEN 410',
    '460 PRINT TAB(14);o$(b);:PRINT TAB(21);:PRINT USING "#####";p(13)+256*p(14);:PRINT TAB(28);:PRINT USING "#########.#";(p(18)+256*p(19))*1000+(p(20)+256*p(21))/10:RETURN',
]

if __name__ == "__main__":
    savekeys.write_asc("LISTSAVE", LINES + savekeys.key_data_lines(600) + ["650 DATA 62,64,205,8,188,201,62,192,205,8,188,201"])

#!/usr/bin/env python3
"""Generate src/cheats/SHOWSAVE.ASC: a short CPC BASIC program that shows the kills, jumps and origin (UK, French or German build) of a commander save.

The origin comes from the save key: every build XORs the 104-byte save with its own 104 bytes of game code (tools/elitekey.py reads them from the game disks).
The program holds the three keys as hex DATA, tries each on the loaded save and takes the one for which both checksums verify (byte &66 = XOR of bytes 0-&65, byte &67 = sum of bytes 0-&66).
usage: python3 -I tools/mk_showsave.py        (then tools/build_cheat.sh tokenises it and adds SHOWSAVE.BAS to the trainer disks)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import elitekey  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DISKS = [("UK", "Elite_UK_Firebird_cracked_trainer.dsk"), ("FRENCH", "Elite (1985)(Firebird Software)(fr).dsk"), ("GERMAN", "Elite_DE_cracked.dsk")]

lines = [
    '10 MODE 1:PRINT"SHOW SAVE: kills, jumps, origin":PRINT',
    '20 INPUT"Save file (e.g. PETER.BIN)";f$',
    '30 MEMORY &5FFF:DIM p(103):ON ERROR GOTO 200',
    '40 LOAD f$,&6000:ON ERROR GOTO 0',
    '50 RESTORE:FOR b=1 TO 3:READ n$,k$',
    '60 FOR i=0 TO 103:p(i)=PEEK(&6000+i) XOR VAL("&"+MID$(k$,2*i+1,2)):NEXT',
    '70 x=0:s=0:FOR i=0 TO 101:x=x XOR p(i):s=s+p(i):NEXT',
    '80 IF x=p(102) AND ((s+p(102)) AND 255)=p(103) THEN 110',
    '90 NEXT:PRINT"Origin: unknown (no UK, French or German key fits)":END',
    '110 PRINT"Origin: ";n$',
    '120 PRINT"Name:   ";:i=0:WHILE p(i)>0 AND i<10:PRINT CHR$(p(i));:i=i+1:WEND:PRINT',
    '130 PRINT"Kills:  ";p(13)+256*p(14)',
    '140 PRINT"Jumps:  ";p(15)+256*p(16)',
    '150 PRINT"Cash:   ";(p(18)+256*p(19))*1000+(p(20)+256*p(21))/10;"Cr"',
    '160 PRINT"Galaxy: ";p(17)+1:END',
    '200 PRINT"Cannot load ";f$:END',
]
for name, disk in DISKS:
    off, key = elitekey.key_from_disk(ROOT / disk)
    lines.append(f"{300 + 10 * len(lines)} DATA {name},{key.hex().upper()}")
# renumber the DATA lines in order 300, 310, 320
out = []
n = 300
for l in lines:
    if " DATA " in l.split(":")[0][:12]:
        l = f"{n} " + l.split(" ", 1)[1]
        n += 10
    out.append(l)
text = "".join(l + "\r\n" for l in out) + "\x1a"
(ROOT / "src/cheats/SHOWSAVE.ASC").write_bytes(text.encode("latin-1"))
print("wrote src/cheats/SHOWSAVE.ASC", len(text), "bytes")

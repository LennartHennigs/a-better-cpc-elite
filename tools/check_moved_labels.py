#!/usr/bin/env python3
"""Find raw numbers in src/elite128 that still point at a stock address whose label moved (128K plan, process gap behind the stale-operand bugs).

usage: python3 -I tools/check_moved_labels.py [--all]
Assembles src/elite and src/elite128 (flags of the missions disk), pairs labels by name, and lists every label whose address differs. Then greps the 128K sources (code lines only,
no `equ`, no comments, no SCREEN+/STAGE+ expressions) for 4-digit hex literals equal to the STOCK address of a moved label (or label+1..+3, the usual operand byte of a self-patched
instruction) and prints file:line. A hit is a stale operand unless the number is an immediate that only looks like an address: check each. Exit 1 when there are hits.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SJ = str(Path.home() / ".local/bin/sjasmplus")
FLAGS = {"commonxx": ["-DENHANCED", "-DTITLESEL", "-DMISSIONS"], "largeaxx": ["-DENHANCED", "-DFIREBIRD", "-DMISSIONS"], "common2x": ["-DENHANCED", "-DTITLESEL", "-DMISSIONS"]}


def syms(tree):
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for f, flags in FLAGS.items():
            sym = Path(tmp) / f"{f}.sym"
            fl = flags if tree == "elite" else []      # the 128K tree gets its flags from config.inc
            r = subprocess.run([SJ, *fl, f"--sym={sym}", f"--raw={Path(tmp) / (f + '.bin')}", str(ROOT / "src" / tree / f"{f}.asm")], capture_output=True, text=True)
            if not sym.exists():
                sys.exit(f"{tree}/{f}: assemble failed\n{r.stdout[-300:]}")
            for l in sym.read_text().splitlines():
                m = re.match(r"(\S+): EQU 0x([0-9A-Fa-f]+)", l)
                if m:
                    out[(f, m.group(1))] = int(m.group(2), 16)
    return out


stock, new = syms("elite"), syms("elite128")
moved = {}
for (f, n), a in stock.items():
    b = new.get((f, n))
    if b is not None and b != a and 0x100 <= a < 0xFFFF:
        moved.setdefault(a, []).append((f, n, b))
print(f"{len(moved)} stock addresses whose label moved")
if "--all" in sys.argv:
    for a in sorted(moved):
        print(hex(a), moved[a][:2])
hits = 0
IGNORE = {0x4000, 0x2710, 0x403F, 0x4980, 0x8000, 0x8066}      # window size, BCD limit, laser screen coordinates, bank copy destination: not addresses of moved labels; 0x8000 and 0x8066 are the rotation constants that stock labels happened to sit on
ISR_ZONE = range(0x2800, 0x2940)            # self-patch operands of the ISR and disc code, shifted by hand by +4 (README "Relocated layout"): the literal equals a stock label by coincidence
for src in sorted((ROOT / "src/elite128").glob("*.asm")):
    for n, line in enumerate(src.read_text().split("\n"), 1):
        code = line.split(";")[0]
        if re.search(r"\bequ\b", code, re.I) or "SCREEN+" in code or "STAGE+" in code:
            continue
        for m in re.finditer(r"\b0x([0-9A-Fa-f]{4})\b", code):
            v = int(m.group(1), 16)
            if v in IGNORE or v in ISR_ZONE or re.match(r"\s*(org|assert|ds)\b", code, re.I):
                continue
            for d in range(0, 4):
                if v - d in moved and not re.match(r"\s*(and|or|xor|cp|add a|sub|ld [bcdehl],0x[0-9A-F]{2}\b)", code):
                    f, nm, b = moved[v - d][0]
                    print(f"{src.name}:{n}: {code.strip()[:60]}  <- stock {nm}{'+%d' % d if d else ''} {hex(v - d)} (now {hex(b)})")
                    hits += 1
                    break
print(f"{hits} suspicious raw operands")
sys.exit(1 if hits else 0)

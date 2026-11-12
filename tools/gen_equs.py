#!/usr/bin/env python3
"""Add the `name equ 0x0000` lines a file needs for labels that live in another file, then let tools/sync_equs.py put the real addresses in (128K plan, phase 3).

usage: python3 -I tools/gen_equs.py DIR [--write]         DIR = src/elite128
For each of commonxx, largeaxx, common2x, musiquex: assemble (mission-disk flags); every `Label not found: NAME` whose NAME is defined as a label (`NAME:`) in another file (commonxx.asm and its
INCLUDE gaps.asm count as one file) gets an equ line with a placeholder value right after the `SCREEN equ` line. Repeats until no file reports a missing label that some other file defines.
Also removes equ lines whose name the same file defines as a label (they cannot coexist). Names nobody defines are listed.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

d = Path(sys.argv[1])
write = "--write" in sys.argv
FLAGS = {"commonxx": [], "largeaxx": [], "common2x": [], "musiquex": []}      # flags live in src/elite128/config.inc
FILES = {"commonxx": ["commonxx.asm", "gaps.asm", "missions_flight.asm"], "largeaxx": ["largeaxx.asm"], "common2x": ["common2x.asm"], "musiquex": ["musiquex.asm"]}
SJ = str(Path.home() / ".local/bin/sjasmplus")


def labels_of(f):
    out = set()
    for fn in FILES[f]:
        p = d / fn
        if p.exists():
            for line in p.read_text().split("\n"):
                m = re.match(r"([A-Za-z_][A-Za-z0-9_]*):", line) or re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s+equ\s+(?!0x)", line)
                if m:
                    out.add(m.group(1))
    return out


def assemble(f):
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([SJ, *FLAGS[f], f"--raw={Path(tmp) / 'o.bin'}", str(d / f"{f}.asm")], capture_output=True, text=True)
    return r.stdout + r.stderr


added_total = 0
for rnd in range(12):
    own = {f: labels_of(f) for f in FILES}
    changed = False
    for f in FILES:
        p = d / f"{f}.asm"
        text = p.read_text()
        # drop equ lines duplicating a label of this very file
        kept, dropped = [], 0
        for line in text.split("\n"):
            m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s+equ\s+0x[0-9A-Fa-f]+", line)
            if m and m.group(1) in own[f] and not line.startswith("SCREEN"):
                dropped += 1
                continue
            kept.append(line)
        if dropped:
            text = "\n".join(kept)
            changed = True
            print(f"{f}: dropped {dropped} equ line(s) of its own labels")
            if write:
                p.write_text(text)
        out = assemble(f)
        missing = sorted(set(re.findall(r"Label not found: (\w+)", out)))
        add = []
        for name in missing:
            owners = [g for g in FILES if g != f and name in own[g]]
            if owners:
                add.append(f"{name} equ 0x0000   ; generated: label of {owners[0]}")
        if add:
            changed = True
            added_total += len(add)
            print(f"{f}: +{len(add)} equ line(s)")
            if write:
                lines = p.read_text().split("\n")
                k = next(i for i, l in enumerate(lines) if l.startswith("SCREEN equ"))
                lines[k + 1:k + 1] = add
                p.write_text("\n".join(lines))
        rest = [n for n in missing if not any(n in own[g] for g in FILES if g != f)]
        if rest:
            print(f"{f}: undefined everywhere: {rest[:20]}")
    if not changed or not write:
        break
print("added", added_total)

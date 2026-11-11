#!/usr/bin/env python3
"""Keep the numeric `name equ 0xNNNN` lines of one source file equal to the real address of the label of that name in another file (128K plan, phase 3).

usage: python3 -I tools/sync_equs.py DIR [--write]      DIR = src/elite128
The four files are assembled separately and name each other's labels with numeric equ lines. After code moves (the &3F60-&7D5D block to bank 7, COMMON2X's contents to the &4000 page) those numbers go
stale. For every equ line `name equ 0xNNNN` in file F whose name is a label (`name:`) of another file G, the address from G's symbol file replaces the number. Mid-instruction equates
(`; inside the instruction at ...`) and names defined as labels in their own file are skipped. Assembles with the flags of the mission disk. Repeat until it reports nothing: a value can
change the size of nothing (equ only), so one pass is enough unless two files exchange names.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
d = Path(sys.argv[1])
write = "--write" in sys.argv
FLAGS = {"commonxx": ["-DENHANCED", "-DTITLESEL", "-DMISSIONS"], "largeaxx": ["-DENHANCED", "-DFIREBIRD", "-DMISSIONS"], "common2x": ["-DENHANCED"], "musiquex": ["-DENHANCED", "-DTITLESEL"]}
SJ = str(Path.home() / ".local/bin/sjasmplus")
syms, owner = {}, {}
with tempfile.TemporaryDirectory() as tmp:
    for f, flags in FLAGS.items():
        sym = Path(tmp) / f"{f}.sym"
        r = subprocess.run([SJ, *flags, f"--sym={sym}", f"--raw={Path(tmp) / (f + '.bin')}", str(d / f"{f}.asm")], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{f}: assemble failed\n{r.stdout[-500:]}")
        syms[f] = {}
        for l in sym.read_text().splitlines():
            p = l.split()
            if len(p) >= 3 and p[1] == "EQU":
                syms[f][p[0].rstrip(":")] = int(p[2], 16)
    # a name is "owned" by the file that defines it as a label (line `name:`), not by an equ
    for f in FLAGS:
        for line in (d / f"{f}.asm").read_text().split("\n"):
            m = re.match(r"([A-Za-z_][A-Za-z0-9_]*):", line)
            if m:
                owner.setdefault(m.group(1), f)
changes = 0
for f in FLAGS:
    p = d / f"{f}.asm"
    lines = p.read_text().split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s+equ\s+)0x([0-9A-Fa-f]+)(.*)$", line)
        if not m or "inside the instruction" in m.group(5):
            continue
        name = m.group(2)
        g = owner.get(name)
        if not g or g == f or name not in syms[g]:
            continue
        real = syms[g][name]
        if real != int(m.group(4), 16):
            changes += 1
            print(f"{f}:{i + 1}: {name} 0x{m.group(4).upper()} -> 0x{real:04X}   (label in {g})")
            lines[i] = f"{m.group(1)}{name}{m.group(3)}0x{real:04X}{m.group(5)}"
    if write:
        p.write_text("\n".join(lines))
print(f"{changes} stale equ line(s)" + (" fixed" if write and changes else ""))

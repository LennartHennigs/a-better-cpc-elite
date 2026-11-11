#!/usr/bin/env python3
"""List (and optionally replace) raw numeric addresses that point into a block that is going to move (128K plan: &3F60-&7D5D to bank 7).

usage: python3 -I tools/relo_numbers.py DIR [--lo HEX --hi HEX] [--write]      DIR = src/elite128
For every 4-digit hex literal in LO..HI in operand and `equ` positions of commonxx/largeaxx/common2x/musiquex .asm (db/dw data is not scanned):
  call/jp/jr targets and `ld (nn),r` / `ld r,(nn)` operands are addresses: replaced by the label at that address (or label+k inside an instruction/data run);
  `ld rr,nn`, `equ` lines and anything else are only listed (they can be numbers; review by hand, mark real numbers with `; number` so they are skipped).
The label table comes from assembling commonxx.asm (COMMONXX labels) with sjasmplus. Checks nothing by itself: run tools/check_src.sh / check_src128.sh afterwards.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
d = Path(sys.argv[1])
lo, hi = 0x3F60, 0x7D5D
if "--lo" in sys.argv:
    lo = int(sys.argv[sys.argv.index("--lo") + 1], 16)
if "--hi" in sys.argv:
    hi = int(sys.argv[sys.argv.index("--hi") + 1], 16)
write = "--write" in sys.argv
with tempfile.TemporaryDirectory() as tmp:
    sym = Path(tmp) / "c.sym"
    subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), f"--sym={sym}", f"--raw={Path(tmp) / 'c.bin'}", str(d / "commonxx.asm")], capture_output=True, check=True)
    names = {}
    for l in sym.read_text().splitlines():
        p = l.split()
        if len(p) >= 3 and p[1] == "EQU":
            names.setdefault(int(p[2], 16), []).append(p[0].rstrip(":"))
starts = sorted(a for a in names if lo - 64 <= a <= hi + 64)


def label_for(v):
    if v in names:
        good = [n for n in names[v] if not n.startswith("equ_")]
        return sorted(good, key=lambda n: (n.startswith(("LAB_", "loc_", "SUB_", "dat_", "sub_")), len(n)))[0]
    prev = [a for a in starts if a < v]
    if prev and v - prev[-1] <= 8:
        return f"{label_for(prev[-1])}+{v - prev[-1]}"
    return None


ADDR_OPS = ("call", "jp", "djnz")
rows = []
for f in ("commonxx", "largeaxx", "common2x", "musiquex"):
    p = d / f"{f}.asm"
    lines = p.read_text().split("\n")
    for n, line in enumerate(lines):
        code = line.split(";")[0]
        cmt = line[len(code):]
        if "number" in cmt or re.match(r"\s*(db|dw|ds|org|assert)\b", code, re.I):
            continue
        for m in re.finditer(r"0x([0-9A-Fa-f]{4})\b", code):
            v = int(m.group(1), 16)
            if not lo <= v <= hi:
                continue
            tok = code.split()
            mn = tok[0].lower() if tok else ""
            kind = "equ" if re.match(r"\s*\w+\s+equ\b", code, re.I) else mn
            is_mem = bool(re.search(r"\(0x%s\)" % m.group(1), code, re.I))
            auto = (mn in ADDR_OPS or (mn == "ld" and is_mem)) and kind != "equ"
            rows.append((f, n + 1, v, kind, auto, label_for(v), line.strip()))
            if write and auto and label_for(v):
                lines[n] = lines[n].replace("0x" + m.group(1), label_for(v), 1)
    if write:
        p.write_text("\n".join(lines))
auto_n = sum(1 for r in rows if r[4] and r[5])
print(f"{len(rows)} numeric addresses in range; {auto_n} replaceable automatically (call/jp/ld (nn)), {sum(1 for r in rows if r[4] and not r[5])} of those without a label, {sum(1 for r in rows if not r[4])} to review")
for r in rows:
    if not (write and r[4] and r[5]):
        print(f"  {r[0]}:{r[1]:5d} &{r[2]:04X} {r[3]:5s} -> {r[5] or '(no label)'}   {r[6][:70]}")

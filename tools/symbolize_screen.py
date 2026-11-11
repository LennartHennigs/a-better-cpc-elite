#!/usr/bin/env python3
"""Replace numeric addresses in the screen page &C000-&FFFF by SCREEN+offset (128K plan, phase 3: the screen page moves to &4000).

usage: python3 -I tools/symbolize_screen.py DIR [--write]       DIR = src/elite128
`SCREEN equ 0xC000` is added to each file; every 4-digit hex literal 0xC000-0xFFFF in an instruction operand (not db/dw/ds, not equ lines of other files' labels) becomes `SCREEN+0xNNN`
(`SCREEN` itself for 0xC000). Left alone: 0xFFFF/0xFFFE (constants), the `+0x40 and wrap` row deltas 0xC040, `ld sp,0xC000` at the end of the off-screen bitmap, the flight message ids
0xC202/0xC005/0xC106, the PPI constant 0xF40E. Lines carrying `; number` are skipped. The bytes must not change: assemble before and after (done by the caller, check_src128.sh).
"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1])
write = "--write" in sys.argv
SKIP_VALUES = {0xFFFF, 0xFFFE, 0xC040, 0xC202, 0xC005, 0xC106, 0xF40E}
n_total = 0
for f in ("commonxx", "largeaxx", "common2x"):
    p = d / f"{f}.asm"
    lines = p.read_text().split("\n")
    n = 0
    for i, line in enumerate(lines):
        code, sep, cmt = line.partition(";")
        if "number" in cmt or re.match(r"\s*(db|dw|ds|org|assert)\b", code, re.I):
            continue
        if re.match(r"\s*\w+\s+equ\b", code, re.I) and "bankInitStage" not in code:
            continue
        def sub(m):
            v = int(m.group(1), 16)
            if not 0xC000 <= v <= 0xFFFF or v in SKIP_VALUES:
                return m.group(0)
            if v == 0xC000 and re.search(r"ld\s+sp\s*,", code, re.I):
                return m.group(0)                     # ClearBitmap: the end of the off-screen bitmap, which does not move
            return "SCREEN" if v == 0xC000 else "SCREEN+0x%03X" % (v - 0xC000)
        new = re.sub(r"0x([0-9A-Fa-f]{4})\b", sub, code)
        if new != code:
            n += 1
            lines[i] = new + sep + cmt
    if write and n:
        text = "\n".join(lines)
        if not re.search(r"^SCREEN\s+equ", text, re.M):
            text = "SCREEN equ 0xC000            ; the screen page: &C000 in the 64K layout, &4000 in the 128K one (docs: src/elite128/README.md)\n" + text
        p.write_text(text)
    print(f"{f}: {n} line(s)")
    n_total += n
print(n_total, "lines" + (" rewritten" if write else " would change"))

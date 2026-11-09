#!/usr/bin/env python3
"""Convert Fessor's Constrictor.asm (RASM syntax, CPC blueprint layout) into src/elite/missions_hull.asm (sjasmplus syntax).

usage: python3 -I tools/fessor_hull.py [extended/source/Constrictor.asm [OUT.asm]]

Only this one ship file is used; the rest of extended/ stays out of the repository (extended/CLAUDE.md). Fessor gave his permission for the hull,
and for using his names and findings in the source, by private mail. His post presenting the Constrictor: https://www.cpcwiki.eu/forum/programming/expanding-elite/msg205425/#msg205425
The conversion only rewrites syntax: `#hh` -> `0xHH`, labels get a colon.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "extended/source/Constrictor.asm"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "src/elite/missions_hull.asm"
lines = [
    "; Constrictor blueprint (261 bytes: 23-byte header, 17 vertices, 24 edges, 10 faces) in the CPC ship layout.",
    "; Hull data by Fessor (Constrictor.asm, CPCWiki thread \"Expanding Elite\", https://www.cpcwiki.eu/forum/programming/expanding-elite/msg205425/#msg205425), converted to sjasmplus syntax by tools/fessor_hull.py.",
    "; Used with Fessor's permission (confirmed by private mail). Credit for the CPC ship layout and this hull goes to him.",
]
for raw in src.read_text(errors="replace").splitlines():
    s = raw.strip()
    if not s:
        continue
    code, _, comment = s.partition(";")
    code = code.strip()
    if not code:
        continue
    code = re.sub(r"#([0-9A-Fa-f]+)", lambda m: "0x" + m.group(1).upper(), code)
    if code.lower().startswith(("db", "dw")):
        lines.append("    " + code + ("   ; " + comment.strip() if comment.strip() else ""))
    else:
        lines.append(code.split()[0] + ":")
out.write_text("\n".join(lines) + "\n")
print("wrote", out)

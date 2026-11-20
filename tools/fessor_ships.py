#!/usr/bin/env python3
"""Convert Fessor's per-ship files (RASM syntax, CPC blueprint layout) into src/elite/missions_ships.asm (sjasmplus syntax).

usage: python3 -I tools/fessor_ships.py [extended/source [OUT.asm]]      (default OUT: src/elite/missions_ships.asm)

Ships: Gecko, CobraMk1, Worm, Moray, Mamba, Adder, Boa, Boulder, Anaconda, Shuttle. Each becomes `shipdat<Name>:` inside `IFDEF HULL_<NAME>` so a ship pack
(src/elite/missions_flight_k.asm) assembles only its own hulls. Like tools/fessor_hull.py this only rewrites syntax: `#hh` and `hhh` hex suffixes become `0xHH`,
labels get a colon, and label case is made uniform (RASM ignores case, sjasmplus does not; Boulder mixes `...Vertices...` and `...Verticesstart`).
Used with Fessor's permission (docs/_ship_packs.md).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
srcdir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "extended/source"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "src/elite/missions_ships.asm"
SHIPS = ["Gecko", "CobraMk1", "Worm", "Moray", "Mamba", "Adder", "Boa", "Boulder", "Anaconda", "Shuttle"]

lines = [
    "; Extra ship blueprints in the CPC ship layout (23-byte header, then vertices, edges, faces; offsets are relative to the blueprint).",
    "; Hull data by Fessor (CPCWiki thread \"Expanding Elite\", https://www.cpcwiki.eu/forum/programming/expanding-elite/), converted to sjasmplus syntax by",
    "; tools/fessor_ships.py. Used with his permission. Credit for the CPC ship layout and these hulls goes to him.",
    "; Each hull is assembled only when its HULL_<NAME> is defined (the ship packs in missions_flight_k.asm define them).",
]
HEX = re.compile(r"(?<![\w])#([0-9A-Fa-f]+)\b|(?<![\w])([0-9][0-9A-Fa-f]*|[A-Fa-f][0-9A-Fa-f]*)h\b")


def num(m):
    return "0x" + (m.group(1) or m.group(2)).upper()


for ship in SHIPS:
    src = (srcdir / f"{ship}.asm").read_text(errors="replace").splitlines()
    names = {}
    body = []
    for raw in src:
        code, _, comment = raw.partition(";")
        code = code.strip()
        if not code:
            continue
        m = re.match(r"^([A-Za-z_]\w*)\s*:?$", code)
        if m:
            code = m.group(1)
            isLabel = True
        else:
            assert re.match(r"(?i)(db|dw)\b", code), (ship, raw)
            isLabel = False
        body.append((isLabel, code, comment.strip()))

    def canon(w):
        return names.setdefault(w.lower(), w)

    # first-seen spelling wins; labels are defined before they are used except the face/edge ends, so scan labels first
    for isLabel, code, _ in body:
        if isLabel:
            canon(code)
    lines.append(f"    IFDEF HULL_{ship.upper()}")
    for isLabel, code, comment in body:
        if isLabel:
            lines.append(canon(code) + ":")
            continue
        op, _, rest = code.partition(" ")
        rest = HEX.sub(num, rest.strip())
        rest = re.sub(r"[A-Za-z_]\w*", lambda m: canon(m.group(0)) if m.group(0).lower() in names else m.group(0), rest)
        lines.append("    " + op.lower() + " " + rest + ("   ; " + comment if comment else ""))
    lines.append("    ENDIF")
out.write_text("\n".join(lines) + "\n")
print("wrote", out)

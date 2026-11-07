"""Shared sjasmplus listing parser for tools/deadcode.py and tools/dbcode.py.

parse(listing_dir, name) reads `<listing_dir>/<name>.lst` and returns one block per label that is followed by at
least one source line: dict(file, name, addr, size, text, data). `text` is the stripped source lines (comments removed), `data`
whether the first of them is a db/dw/ds run.
"""
import re
from pathlib import Path

LINE = re.compile(r"^\s*\d+\+?\s+([0-9A-Fa-f]{4})\s(.*)$")
LABEL = re.compile(r"^(\w+):\s*(;.*)?$")
HEX = re.compile(r"[0-9A-Fa-f]{2}")
DATA_OPS = ("db", "dw", "ds", "defb", "defw", "defs")


def parse(listing_dir, name):
    blocks, cur = [], None
    for raw in (Path(listing_dir) / f"{name}.lst").read_text(errors="replace").splitlines():
        m = LINE.match(raw)
        if not m:
            continue
        rest = m.group(2)
        hexb = [x for x in rest[:12].split() if HEX.fullmatch(x)]   # fixed listing columns
        text = rest[13:].split(";")[0].rstrip()
        if text and not text.startswith((" ", "\t")) and LABEL.match(text.strip()):
            cur = dict(file=name, name=LABEL.match(text.strip()).group(1), addr=int(m.group(1), 16),
                       size=0, text=[], data=None)
            blocks.append(cur)
        elif cur is not None:
            cur["size"] += len(hexb)
            if text.strip():
                cur["text"].append(text.strip())
                if cur["data"] is None:
                    cur["data"] = text.strip().split()[0].lower() in DATA_OPS
    return [b for b in blocks if b["text"]]

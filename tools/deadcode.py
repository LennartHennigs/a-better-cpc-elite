#!/usr/bin/env python3
"""Find dead code in src/elite/: labelled routines that nothing refers to (directly or only from other dead code).

usage: python3 -I tools/deadcode.py [LISTING_DIR]      (default work/dead; make it with the sjasmplus lines below)
    for f in commonxx largeaxx common2x musiquex; do
        sjasmplus --raw=work/dead/$f.bin --lst=work/dead/$f.lst src/elite/$f.asm; done

A routine is a labelled run of instructions (not db/dw/ds). It counts as referenced if its name appears in the
source of a live block, or if its address occurs as a little-endian word anywhere in the memory image outside dead
blocks (tables, `ld hl,addr`, vectors). Relative jumps (jr, djnz) are source references. Candidates are *candidates*:
code reached by self-modification, `rst` tricks, BASIC or the firmware can still look dead.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lstparse import parse  # noqa: E402

D = Path(sys.argv[1] if len(sys.argv) > 1 else "work/dead")
BASES = {"largeaxx": 0x0840, "commonxx": 0x1A40, "common2x": 0xC000}
IDENT = re.compile(r"[A-Za-z_]\w*")


def terminal(b):
    last = b["text"][-1].lower().split()
    if not last:
        return False
    op, rest = last[0], " ".join(last[1:])
    if op in ("reti", "retn"):
        return True
    if op == "ret":
        return not rest
    if op in ("jp", "jr"):
        return "," not in rest
    return False


def main():
    blocks = sorted((b for n in BASES for b in parse(D, n)), key=lambda b: (b["file"], b["addr"]))
    mem = bytearray(0x10000)
    for n, base in BASES.items():
        data = (D / f"{n}.bin").read_bytes()
        mem[base:base + len(data)] = data
    by_name = {b["name"]: b for b in blocks}
    by_addr = {}
    for b in blocks:
        by_addr.setdefault(b["addr"], b)
    # edges
    edges = {b["name"]: set() for b in blocks}
    for i, b in enumerate(blocks):
        for line in b["text"]:
            for tok in IDENT.findall(line):
                if tok in by_name and tok != b["name"]:
                    edges[b["name"]].add(tok)
        nxt = blocks[i + 1] if i + 1 < len(blocks) else None
        if nxt and nxt["file"] == b["file"] and nxt["addr"] == b["addr"] + b["size"] and (b["data"] or not terminal(b)):
            # falls through, or follows a db run that may be code the disassembler did not reach
            edges[b["name"]].add(nxt["name"])
        for off in range(b["addr"], b["addr"] + b["size"] - 1):          # numeric references
            w = mem[off] | mem[off + 1] << 8
            for cand in (w, w + 1):                       # w + 1: tables of address-1 for push/ret dispatch
                t = by_addr.get(cand)
                if t and t["name"] != b["name"]:
                    edges[b["name"]].add(t["name"])
    roots = [b["name"] for b in blocks if b["data"] or b["file"] == "musiquex"]
    roots += [b["name"] for b in blocks if b["addr"] == 0x1C82 and b["file"] == "commonxx"]
    live, todo = set(roots), list(roots)
    while todo:
        for t in edges[todo.pop()]:
            if t not in live:
                live.add(t)
                todo.append(t)
    dead = [b for b in blocks if b["name"] not in live and not b["data"] and b["size"] >= 1 and b["file"] != "musiquex"]
    dead.sort(key=lambda b: (b["file"], b["addr"]))
    # safety check: a numeric operand (jp/call/ld ..., 0xNNNN) in live code that points into the middle of a dead block
    deadset = {b["name"] for b in dead}
    suspects = []
    for b in blocks:
        if b["name"] in deadset or b["data"] or b["file"] == "musiquex":
            continue
        for line in b["text"]:
            for m in re.finditer(r"0x([0-9A-Fa-f]{4})\b", line):
                w = int(m.group(1), 16)
                for d in dead:
                    if d["file"] != "common2x" and d["addr"] <= w < d["addr"] + d["size"]:
                        suspects.append((b["name"], line, w, d["name"]))
    if suspects:
        print("numeric operands in live code that point into a dead block (check by hand):")
        for x in suspects[:40]:
            print(f"  {x[0]}: {x[1]}  -> &{x[2]:04X} in {x[3]}")
        print()
    regions = []
    for b in dead:
        if regions and regions[-1]["file"] == b["file"] and regions[-1]["end"] == b["addr"]:
            regions[-1]["end"] += b["size"]
            regions[-1]["names"].append(b["name"])
        else:
            regions.append(dict(file=b["file"], start=b["addr"], end=b["addr"] + b["size"], names=[b["name"]]))
    print("| Region | Bytes | File | First label | Blocks |\n|---|---|---|---|---|")
    for r in regions:
        print(f"| `&{r['start']:04X}-&{r['end'] - 1:04X}` | {r['end'] - r['start']} | `{r['file']}.asm` | `{r['names'][0]}` | {len(r['names'])} |")
    print(f"\n{len(regions)} regions, {len(dead)} blocks, {sum(b['size'] for b in dead)} bytes")


main()

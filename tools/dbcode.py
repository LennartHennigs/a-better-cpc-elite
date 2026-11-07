#!/usr/bin/env python3
"""Find code hiding in the `db` runs of src/elite/commonxx.asm: byte runs that decode as a complete Z80 routine,
call or jump only to known labels, and that nothing refers to. These are the dead (or never-disassembled) routines.

usage: python3 -I tools/dbcode.py [LISTING_DIR] [--min N]       (needs the listings of tools/deadcode.py's header)

A candidate is a chain of valid instructions that ends in ret/reti/retn/jp/jr, is at least N bytes long (default 12),
whose absolute call/jp targets are all label addresses of the source, and whose relative jumps stay inside the chain.
Whether it is really unused still needs a trace (an execute breakpoint in cpcxray over a play session).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import z80dis  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
D = Path(args[0] if args else "work/dead")
MIN = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 12
if "--min" in sys.argv and args and args[-1] == str(MIN):
    args.remove(str(MIN))
    D = Path(args[0] if args else "work/dead")
BASES = {"largeaxx": 0x0840, "commonxx": 0x1A40, "common2x": 0xC000}
LINE = re.compile(r"^\s*\d+\+?\s+([0-9A-Fa-f]{4})\s(.*)$")
LABEL = re.compile(r"^(\w+):\s*(;.*)?$")


def parse(name):
    out, cur = [], None
    for raw in (D / f"{name}.lst").read_text(errors="replace").splitlines():
        m = LINE.match(raw)
        if not m:
            continue
        rest = m.group(2)
        hexb = [x for x in rest[:12].split() if re.fullmatch(r"[0-9A-Fa-f]{2}", x)]
        text = rest[13:].split(";")[0].rstrip()
        if text and not text.startswith((" ", "\t")) and LABEL.match(text.strip()):
            cur = dict(name=LABEL.match(text.strip()).group(1), addr=int(m.group(1), 16), size=0, first=None)
            out.append(cur)
        elif cur is not None:
            cur["size"] += len(hexb)
            if text.strip() and cur["first"] is None:
                cur["first"] = text.strip().split()[0].lower()
    return [b for b in out if b["first"]]


def main():
    mem = bytearray(0x10000)
    for n, base in BASES.items():
        d = (D / f"{n}.bin").read_bytes()
        mem[base:base + len(d)] = d
    blocks = [b for n in BASES for b in parse(n)]
    labels = {b["addr"] for b in blocks}
    runs = []
    for b in sorted((b for b in parse("commonxx")), key=lambda b: b["addr"]):
        if b["first"] in ("db", "dw", "ds"):
            if runs and runs[-1][1] == b["addr"]:
                runs[-1][1] += b["size"]
            else:
                runs.append([b["addr"], b["addr"] + b["size"]])
    found = []
    for lo, hi in runs:
        a = lo
        while a < hi:
            chain, pc, ok = [], a, False
            while pc < hi:
                i = z80dis.decode(mem, pc)
                if not i.valid or pc + i.length > hi:
                    break
                chain.append((pc, i))
                pc += i.length
                if i.flow in ("ret", "stop") or (i.flow == "jump"):
                    ok = True
                    break
            if ok and pc - a >= MIN:
                good = True
                span = (a, pc)
                for p, i in chain:
                    if i.addr_kind in ("call", "jp") and i.addr not in labels:
                        good = False
                    if i.target is not None and not (span[0] <= i.target < span[1]) and i.target not in labels:
                        good = False
                    if i.flow == "stop" and mem[p] == 0x76:      # halt
                        good = False
                if good:
                    refs = [w for w in range(0x40, 0xFFFE) if (mem[w] | mem[w + 1] << 8) in (a, a - 1)
                            and not (a <= w < pc)]
                    found.append((a, pc, len(chain), refs))
                    a = pc
                    continue
            a += 1
    print("| Start | Bytes | Instructions | Words that point at it |\n|---|---|---|---|")
    total = 0
    for a, e, n, refs in found:
        total += e - a
        r = ", ".join(f"`&{x:04X}`" for x in refs[:3]) or "none"
        print(f"| `&{a:04X}-&{e - 1:04X}` | {e - a} | {n} | {r} |")
    unref = [f for f in found if not f[3]]
    print(f"\n{len(found)} candidate routines, {total} bytes; {len(unref)} with no pointing word, {sum(f[1] - f[0] for f in unref)} bytes")


main()

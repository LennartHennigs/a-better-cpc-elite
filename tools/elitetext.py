#!/usr/bin/env python3
"""Expand Elite CPC token strings from a stock memory image (work/stock_mem_image.bin).

usage: elitetext.py TABLE_ADDR INDEX [INDEX ...]   e.g. elitetext.py 0xFCA 0xdf
       elitetext.py --flight TOKEN [TOKEN ...]       in-flight message tokens (table &2FAF)
A table is NUL-terminated token strings; INDEX is 1-based as in printStringA. Tokens: 0x20-0x5A ASCII;
0x81-0xD6 recurse into the same table; 0xD7+ digram (table at &8DC8); <0x20 and 0x5B-0x80 are dynamic
(planet names, random descriptions) and print as {jNN} / {dNN}.
"""
import sys
from pathlib import Path

MEM = Path(__file__).resolve().parent.parent / "work" / "stock_mem_image.bin"
DIGRAMS = 0x8DC8


def strings_at(mem, addr, index):
    for _ in range(index - 1):
        addr = mem.index(0, addr) + 1
    end = mem.index(0, addr)
    return mem[addr:end]


def expand(mem, table, tokens, depth=0):
    out = []
    for t in tokens:
        if t < 0x20:
            out.append("{j%02X}" % t)
        elif t < 0x5B:
            out.append(chr(t))
        elif t < 0x81:
            out.append("{d%02X}" % t)
        elif t < 0xD7 and depth < 6:
            out.append(expand(mem, table, strings_at(mem, table, t), depth + 1))
        else:
            k = (t - 0xD7) * 2
            pair = mem[DIGRAMS + k:DIGRAMS + k + 2]
            out.append("".join(chr(c) for c in pair if c != 0x3F))
    return "".join(out)


FLIGHT_TABLE, DOCKED_DIGRAMS = 0x2FAF, 0x8DE2


def expand_flight(mem, tok, depth=0):
    """printString namespace (in-flight messages, system descriptions): table at &2FAF."""
    if tok < 0x0E:
        return "{j%02X}" % tok
    if tok < 0x60 and tok >= 0x20:
        return chr(tok)
    if tok < 0x20 or tok < 0x80 or tok >= 0xA0:
        if depth > 6:
            return "{...}"
        idx = tok + 0x72 if tok < 0x20 else tok if tok < 0x80 else tok - 0xA0
        return "".join(expand_flight(mem, t, depth + 1) for t in strings_at(mem, FLIGHT_TABLE, idx + 1))
    k = (tok - 0x80) * 2
    return "".join(chr(c) for c in mem[DOCKED_DIGRAMS + k:DOCKED_DIGRAMS + k + 2] if c != 0x3F)


if __name__ == "__main__" and sys.argv[1:2] == ["--flight"]:
    mem = MEM.read_bytes()
    for a in sys.argv[2:]:
        t = int(a, 0)
        print(f"{t:#04x}: {expand_flight(mem, t)}")
    sys.exit(0)

if __name__ == "__main__":
    mem = MEM.read_bytes()
    table = int(sys.argv[1], 0)
    for a in sys.argv[2:]:
        i = int(a, 0)
        print(f"{i:#04x}: {expand(mem, table, strings_at(mem, table, i))}")

#!/usr/bin/env python3
"""Encode plain text into Elite CPC docked-table tokens (table A, stringsTable2 rules) and measure the size.

usage: textenc.py --selftest            re-encode every existing string from its expansion, check the round trip
       textenc.py "SOME TEXT" [...]     print the token bytes and the size of each string
       textenc.py --file FILE.txt       one string per line; prints the total
       textenc.py --asm FILE.txt        sjasmplus `db` lines for a string table (one string per line, NUL-terminated entries)

Same token rules as tools/elitetext.py and tools/textcomp.py (printStringA in commonxx.asm): 0x20-0x5A are ASCII,
0x81-0xD6 reference string N of the table (1-based), 0xD7+ are digrams (table &8DC8). The parser is optimal for a
fixed token set (dynamic programming). New strings may reference the 214 existing strings and the digrams only;
it does not add tokens. Output ends with a NUL, as table entries do.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textcomp  # noqa: E402

TB = textcomp.Table("A stringsTable2 (&0FCA)", 0xFCA, 0x1714, "A")
TB.cur = [list(s) for s in TB.strs]
_memo = {}
EXP = [TB.expand_str(j, _memo, frozenset()) for j in range(TB.n)]
DIGS = [(t, d) for t, d in TB.digs.items() if len(d) == 2]
CANDS = [(TB.ref_token(j), EXP[j]) for j in range(TB.n) if len(EXP[j]) >= 2 and TB.ref_token(j) is not None
         and TB.ref_token(j) not in TB.digs]


def to_bytes(text):
    """latin-1 bytes of a string; {0C} style escapes give raw bytes (0C is the newline token of the docked tables)"""
    if not isinstance(text, str):
        return bytes(text)
    import re
    parts = re.split(r"\{([0-9A-Fa-f]{2})\}", text)
    return b"".join(q.encode("latin-1") if i % 2 == 0 else bytes([int(q, 16)]) for i, q in enumerate(parts))


def encode(text):
    """Fewest-token encoding of text (bytes or str) with the existing refs and digrams; returns list of tokens."""
    T = tuple(to_bytes(text))
    L, INF = len(T), 10 ** 9
    best, how = [INF] * (L + 1), [None] * (L + 1)
    best[0] = 0
    for p in range(L):
        if best[p] == INF:
            continue
        c = best[p] + 1
        if TB.is_literal(T[p]) and c < best[p + 1]:
            best[p + 1], how[p + 1] = c, (p, T[p])
        for t, d in DIGS:
            if p + 2 <= L and T[p:p + 2] == d and c < best[p + 2]:
                best[p + 2], how[p + 2] = c, (p, t)
        for t, e in CANDS:
            q = p + len(e)
            if q <= L and T[p:q] == e and c < best[q]:
                best[q], how[q] = c, (p, t)
    if best[L] == INF:
        raise ValueError("cannot encode %r" % text)
    seq, p = [], L
    while p:
        p0, t = how[p]
        seq.append(t)
        p = p0
    return seq[::-1]


def decode(tokens):
    out = []
    for t in tokens:
        out.extend(TB.expand_tok(t, _memo, frozenset()))
    return bytes(out)


def selftest():
    total_orig = total_new = 0
    for j in range(TB.n):
        orig = TB.strs[j]
        if not orig:
            continue
        exp = bytes(EXP[j])
        # a string may not be encoded with a reference to itself (it would loop): remove it from the candidates
        saved = [c for c in CANDS]
        CANDS[:] = [c for c in CANDS if c[0] != TB.ref_token(j)]
        try:
            seq = encode(exp)
        except ValueError:
            seq = list(orig)
        CANDS[:] = saved
        assert decode(seq) == exp, "round trip failed at string %d" % (j + 1)
        total_orig += len(orig) + 1
        total_new += min(len(seq), len(orig)) + 1
    print(f"{TB.n} strings round-trip ok; token bytes {total_orig} -> {total_new} with the optimal parse")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--selftest"]:
        return selftest()
    if args[:1] == ["--asm"]:
        for s in open(args[1]).read().splitlines():
            seq = encode(s)
            assert decode(seq) == to_bytes(s)
            print("    db " + ",".join("0x%02X" % t for t in seq + [0]) + "   ; " + s)
        return
    lines = open(args[1]).read().splitlines() if args[:1] in (["--file"],) else args
    total = 0
    for s in lines:
        seq = encode(s)
        assert decode(seq) == to_bytes(s)
        total += len(seq) + 1
        print(f"{len(s):4d} chars -> {len(seq) + 1:4d} bytes  {s[:60]}")
    print("total", total, "bytes")


if __name__ == "__main__":
    main()

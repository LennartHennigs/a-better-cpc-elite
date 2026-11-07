#!/usr/bin/env python3
"""Re-tokenise Elite CPC text tables with an optimal parse and report the size.

usage: textcomp.py [--emit FILE.json]

Works on work/stock_mem_image.bin. Two tables (token rules from printStringA and printString in
commonxx.asm, same as tools/elitetext.py):
  A  stringsTable2 at &0FCA   1-based refs 0x81-0xD6, digrams 0xD7+ (table &8DC8)
  B  stringsTable  at &2FAF   refs 0x0E-0x1F (+0x72), 0x60-0x7F, 0xA0-0xFF (-0xA0); digrams 0x80-0x9F (&8DE2)
Every string keeps its index (code and refs address strings by position). Each string is re-encoded
with the fewest tokens (dynamic programming) using the existing refs and digrams; the decoder and the
token table are unchanged. Output expansion is checked equal to the original.
"""
import json
import sys
from functools import lru_cache
from pathlib import Path

MEM = Path(__file__).resolve().parent.parent / "work" / "stock_mem_image.bin"
mem = MEM.read_bytes()


def digram(addr, n):
    out = []
    for k in range(n):
        p = mem[addr + 2 * k:addr + 2 * k + 2]
        out.append(tuple(c for c in p if c != 0x3F))
    return out


class Table:
    def __init__(self, name, start, end, kind):
        self.name, self.start, self.end, self.kind = name, start, end, kind
        raw = mem[start:end]
        self.strs = raw.split(b"\x00")
        # last element is whatever follows the final NUL
        self.tail = self.strs.pop()
        self.n = len(self.strs)
        if kind == "A":
            self.digs = {0xD7 + k: d for k, d in enumerate(digram(0x8DC8, 0x29))}
        else:
            self.digs = {0x80 + k: d for k, d in enumerate(digram(0x8DE2, 0x20))}

    def ref_index(self, t):
        """0-based string index a ref token points at, or None"""
        if self.kind == "A":
            return t - 1 if 0x81 <= t <= 0xD6 else None
        if 0x0E <= t < 0x20:
            return t + 0x72
        if 0x60 <= t < 0x80:
            return t
        if t >= 0xA0:
            return t - 0xA0
        return None

    def ref_token(self, j):
        """a token that references string j, or None"""
        if self.kind == "A":
            return j + 1 if 0x80 <= j <= 0xD5 else None
        if 0 <= j <= 0x5F:
            return j + 0xA0
        if 0x60 <= j <= 0x7F:
            return j
        if 0x80 <= j <= 0x91:
            return j - 0x72
        return None

    def is_literal(self, t):
        if self.kind == "A":
            return 0x01 <= t <= 0x5A or 0x5B <= t <= 0x80
        return 0x01 <= t <= 0x0D or 0x20 <= t <= 0x5F

    def expand_tok(self, t, memo, stack):
        if self.is_literal(t):
            return (t,)
        if t in self.digs:
            return self.digs[t]
        j = self.ref_index(t)
        if j is None or j >= self.n:
            raise ValueError("bad token %#x" % t)
        return self.expand_str(j, memo, stack)

    def expand_str(self, j, memo, stack):
        if j in memo:
            return memo[j]
        if j in stack:
            raise ValueError("cycle at %d" % j)
        out = []
        for t in self.cur[j]:
            out.extend(self.expand_tok(t, memo, stack | {j}))
        memo[j] = tuple(out)
        return memo[j]

    def refs_of(self, enc):
        return {self.ref_index(t) for t in enc
                if not self.is_literal(t) and t not in self.digs}

    def depth(self, j, memo):
        if j not in memo:
            memo[j] = 1 + max([self.depth(k, memo) for k in self.refs_of(self.cur[j])] + [0])
        return memo[j]

    def reach(self, a):
        seen, todo = set(), [a]
        while todo:
            x = todo.pop()
            for k in self.refs_of(self.cur[x]):
                if k not in seen:
                    seen.add(k)
                    todo.append(k)
        return seen


def optimise(tb):
    tb.cur = [list(s) for s in tb.strs]
    orig_exp = {}
    exp = [tb.expand_str(j, orig_exp, frozenset()) for j in range(tb.n)]
    d0 = max(tb.depth(j, {}) for j in range(tb.n))
    lit_ok = tb.is_literal
    digs = [(t, d) for t, d in tb.digs.items() if len(d) == 2]
    before = sum(len(s) + 1 for s in tb.strs)
    changed = True
    passes = 0
    while changed:
        changed = False
        passes += 1
        for i in range(tb.n):
            T = exp[i]
            if len(T) < 2:
                continue
            blocked = {k for k in range(tb.n) if i in tb.reach(k) or k == i}
            cands = [(j, tb.ref_token(j)) for j in range(tb.n)
                     if j not in blocked and len(exp[j]) >= 2 and tb.ref_token(j) is not None
                     and tb.ref_token(j) not in tb.digs]
            L = len(T)
            INF = 10 ** 9
            best = [INF] * (L + 1)
            how = [None] * (L + 1)
            best[0] = 0
            for p in range(L):
                if best[p] == INF:
                    continue
                c = best[p] + 1
                if lit_ok(T[p]) and c < best[p + 1]:
                    best[p + 1], how[p + 1] = c, (p, T[p])
                for t, d in digs:
                    if p + 2 <= L and T[p:p + 2] == d and c < best[p + 2]:
                        best[p + 2], how[p + 2] = c, (p, t)
                for j, t in cands:
                    e = exp[j]
                    q = p + len(e)
                    if q <= L and T[p:q] == e and c < best[q]:
                        best[q], how[q] = c, (p, t)
            if best[L] == INF:
                continue
            seq, p = [], L
            while p:
                p0, t = how[p]
                seq.append(t)
                p = p0
            seq.reverse()
            if len(seq) < len(tb.cur[i]):
                old = tb.cur[i]
                tb.cur[i] = seq
                if max(tb.depth(j, {}) for j in range(tb.n)) > d0:
                    tb.cur[i] = old
                    continue
                changed = True
    new_exp = {}
    for j in range(tb.n):
        assert tb.expand_str(j, new_exp, frozenset()) == exp[j], "expansion changed at %d" % j
    after = sum(len(s) + 1 for s in tb.cur)
    return before, after, passes, d0


def main():
    tables = [Table("A stringsTable2 (&0FCA)", 0xFCA, 0x1714, "A"),
              Table("B stringsTable  (&2FAF)", 0x2FAF, 0x3383, "B")]
    result = {}
    tot_b = tot_a = 0
    for tb in tables:
        b, a, passes, d0 = optimise(tb)
        tot_b += b
        tot_a += a
        print(f"{tb.name}: {tb.n} strings, {b} -> {a} bytes ({b - a} saved, {100 * (b - a) / b:.1f}%), "
              f"{passes} passes, max nesting {d0}")
        changed = sum(1 for x, y in zip(tb.strs, tb.cur) if list(x) != y)
        print(f"   {changed} strings re-encoded")
        result[tb.name[:1]] = {"start": tb.start, "strings": [bytes(s).hex() for s in tb.cur]}
    print(f"total {tot_b} -> {tot_a} ({tot_b - tot_a} bytes saved)")
    if "--emit" in sys.argv:
        Path(sys.argv[sys.argv.index("--emit") + 1]).write_text(json.dumps(result))


if __name__ == "__main__":
    main()

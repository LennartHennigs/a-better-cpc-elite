#!/usr/bin/env python3
"""Map Fessor's labels onto the stock Elite binaries.

Fessor's patched build (RASM output + rasmoutput.sym) has names for ~2700 addresses, but its code is
shifted against the stock game, so absolute call/jump/load operands differ. Method:

1. For each label, take the bytes at the label, mask every 16-bit operand, and search the stock image.
   Longer prefixes are tried when a short one is ambiguous. A single hit is a candidate anchor.
2. Anchors that break the address order (patched order vs stock order) are dropped (longest increasing
   subsequence), which removes false matches.
3. Every other label is placed using the nearest anchors on both sides: ambiguous hits are narrowed to
   the one between the anchors, and a label between two anchors with the same offset gets that offset.

Output lines carry a confidence tag: stock (from the stock symbol file), exact, bracket, delta+bytes, delta.

usage: map_labels.py PATCHED_BIN_DIR PATCHED.sym STOCK_BIN_DIR OUT.sym [STOCK_TRUTH.sym] [--eval]
  PATCHED_BIN_DIR needs LARGEAXP.BIN COMMONXP.BIN COMMON2P.BIN (AMSDOS header included, from rasm)
  STOCK_BIN_DIR   needs LARGEAXX.BIN COMMONXX.BIN COMMON2X.BIN (header stripped, from dskx.py)
  --eval          hold out the names in STOCK_TRUTH.sym and report how many are recovered correctly
"""
import bisect
import re
import sys
from collections import Counter
from pathlib import Path

PLACE = [("LARGEAXX.BIN", "LARGEAXP.BIN", 0x0840), ("COMMONXX.BIN", "COMMONXP.BIN", 0x1A40),
         ("COMMON2X.BIN", "COMMON2P.BIN", 0xC000)]
ADDR3 = {0x01, 0x11, 0x21, 0x31, 0x22, 0x2A, 0x32, 0x3A, 0xC2, 0xCA, 0xD2, 0xDA, 0xE2, 0xEA, 0xF2,
         0xFA, 0xC3, 0xC4, 0xCC, 0xCD, 0xD4, 0xDC, 0xE4, 0xEC, 0xF4, 0xFC}
IMM1 = {0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E, 0xC6, 0xCE, 0xD6, 0xDE, 0xE6, 0xEE, 0xF6,
        0xFE, 0xD3, 0xDB, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38}
ED_ADDR = {0x43, 0x4B, 0x53, 0x5B, 0x63, 0x6B, 0x73, 0x7B}
IDX_MEM = {0x34, 0x35, 0x46, 0x4E, 0x56, 0x5E, 0x66, 0x6E, 0x70, 0x71, 0x72, 0x73, 0x74, 0x75,
           0x77, 0x7E, 0x86, 0x8E, 0x96, 0x9E, 0xA6, 0xAE, 0xB6, 0xBE}
LENGTHS = (14, 24, 40)


def decode(b, i):
    """Return (length, address_operand_offset or None) of the instruction at b[i]."""
    op = b[i]
    if op in (0xDD, 0xFD):
        o2 = b[i + 1]
        if o2 in (0x21, 0x22, 0x2A):
            return 4, 2
        if o2 in (0xCB, 0x36):
            return 4, None
        if o2 in IDX_MEM:
            return 3, None
        return 2, None
    if op == 0xED:
        return (4, 2) if b[i + 1] in ED_ADDR else (2, None)
    if op == 0xCB:
        return 2, None
    if op in ADDR3:
        return 3, 1
    if op in IMM1:
        return 2, None
    return 1, None


def masked(b, start, n):
    """Decode about n bytes from start; return (bytes, mask), or None on overrun."""
    out, mask, i = bytearray(), bytearray(), start
    while len(out) < n:
        if i + 4 > len(b):
            return None
        ln, ao = decode(b, i)
        out += b[i:i + ln]
        m = bytearray(b"\xff" * ln)
        if ao is not None:
            m[ao] = m[ao + 1] = 0
        mask += m
        i += ln
    return bytes(out), bytes(mask)


def to_regex(pat):
    data, mask = pat
    body = b"".join(re.escape(bytes([d])) if m else b"." for d, m in zip(data, mask))
    return re.compile(b"(?=" + body + b")", re.S)   # lookahead: report overlapping hits too


def load_image(directory, names_addrs, skip):
    img = bytearray(65536)
    for fname, addr in names_addrs:
        d = (Path(directory) / fname).read_bytes()[skip:]
        img[addr:addr + len(d)] = d
    return bytes(img)


def hits_for(patched, stock, ranges, addr, n):
    pat = masked(patched, addr, n)
    if pat is None:
        return None, 0
    rx = to_regex(pat)
    hits = []
    for lo, hi in ranges:
        hits += [lo + m.start() for m in rx.finditer(stock[lo:hi])]
    return hits, sum(pat[1])


def lis_keep(pairs):
    """pairs: [(patched, stock)] sorted by patched. Keep the longest strictly increasing run in stock."""
    tails, idx, prev = [], [], [-1] * len(pairs)
    for i, (_, s) in enumerate(pairs):
        k = bisect.bisect_left(tails, s)
        if k == len(tails):
            tails.append(s)
            idx.append(i)
        else:
            tails[k] = s
            idx[k] = i
        prev[i] = idx[k - 1] if k else -1
    keep, i = [], idx[-1] if idx else -1
    while i >= 0:
        keep.append(pairs[i])
        i = prev[i]
    return keep[::-1]


def resolve(labels, patched, stock, ranges, holdout=frozenset()):
    """labels: [(name, patched_addr)]. Returns {name: (stock_addr, tag)}.

    Names in holdout take no part as anchors and get no short-prefix retry (used to test accuracy).
    """
    cands, anchors = {}, []
    for name, addr in labels:
        if not any(lo <= addr < hi for lo, hi in ranges) or not any(patched[addr:addr + 8]):
            continue
        best = []
        for n in LENGTHS:
            hits, fixed = hits_for(patched, stock, ranges, addr, n)
            if hits is None:
                break
            if fixed < 6:
                continue
            best = hits
            if len(hits) == 1:
                break
        if not best:   # code changed near the label: try a short prefix
            hits, fixed = hits_for(patched, stock, ranges, addr, 7)
            best = hits if hits is not None and fixed >= 5 and len(hits) <= 6 else []
        cands[name] = (addr, best)
        if len(best) == 1 and name not in holdout:
            anchors.append((addr, best[0]))
    # each file loads at the same address in both builds, so its first byte is a fixed anchor
    anchors += [(lo, lo) for lo, _ in ranges if not any(a == lo for a, _ in anchors)]
    anchors = lis_keep(sorted(anchors))
    apat = [a for a, _ in anchors]
    astk = dict(anchors)
    out = {n: (astk[a], "exact") for n, (a, h) in cands.items()
           if a in astk and len(h) == 1 and a not in (lo for lo, _ in ranges)}
    for name, (addr, hits) in cands.items():
        if name in out:
            continue
        k = bisect.bisect_right(apat, addr)
        lo = anchors[k - 1] if k else None
        hi = anchors[k] if k < len(anchors) else None
        inside = [h for h in hits if lo[1] < h < hi[1]] if lo and hi else []
        same = lo and hi and lo[1] - lo[0] == hi[1] - hi[0]
        pred = addr + lo[1] - lo[0] if same else None
        if pred is not None and pred in hits:
            out[name] = (pred, "delta+bytes")
        elif len(inside) == 1:
            out[name] = (inside[0], "bracket")
        elif pred is not None and not hits:
            out[name] = (pred, "delta")
    return out


def main(pbin, psym, sbin, outfile, truth=None, evaluate=False):
    patched = load_image(pbin, [(p, a) for _, p, a in PLACE], 128)
    stock = load_image(sbin, [(s, a) for s, _, a in PLACE], 0)
    labels = []
    for line in Path(psym).read_text(errors="replace").splitlines():
        m = re.match(r"(\S+)\s+#([0-9A-Fa-f]+)\s+B\d+\s+L", line)
        if m:
            labels.append((m.group(1), int(m.group(2), 16)))
    paddr = dict(labels)
    ranges = [(a, a + len((Path(sbin) / s).read_bytes())) for s, _, a in PLACE]
    known = {}
    if truth:
        for m in re.finditer(r"^(\w+)\s+equ\s+#([0-9a-fA-F]+)", Path(truth).read_text(), re.M):
            known[m.group(1).upper()] = (m.group(1), int(m.group(2), 16))
    if evaluate:
        held = {n for n, _ in labels if n.upper() in known}
        res = resolve(labels, patched, stock, ranges, holdout=held)
        tally = Counter()
        for n in held:
            if n in res:
                tally[(res[n][1], res[n][0] == known[n.upper()][1])] += 1
            else:
                tally[("unresolved", None)] += 1
        print("hold-out of", len(held), "known names, (tag, correct):", dict(tally))
        return
    res = resolve(labels, patched, stock, ranges)
    in_range = sum(1 for _, a in labels if any(lo <= a < hi for lo, hi in ranges))
    print("labels:", len(labels), "in code ranges:", in_range,
          "resolved:", dict(Counter(t for _, t in res.values())), "unresolved:", in_range - len(res))
    rows = [(s, n, t, paddr[n]) for n, (s, t) in res.items() if n.upper() not in known]
    rows += [(a, n, "stock", None) for n, a in known.values()]
    rows.sort(key=lambda r: (r[0], r[1]))
    with open(outfile, "w") as f:
        f.write("; Fessor label -> stock Elite address (see tools/map_labels.py)\n")
        f.write("; tags: stock = Fessor's stock symbol file; exact = unique masked-byte match;\n")
        f.write(";       bracket / delta+bytes = narrowed using neighbouring matches; delta = offset only\n")
        for s, n, t, p in rows:
            extra = "" if p is None else f" patched #{p:04X}"
            f.write(f"{n} equ #{s:04X} ; {t}{extra}\n")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(*args[:5], evaluate="--eval" in sys.argv)

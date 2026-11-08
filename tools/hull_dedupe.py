#!/usr/bin/env python3
"""Measure duplicated byte runs across the ship blueprints in COMMONXX (stock English).
Reads shipGFXdataTable (19 x 'C3 lo hi n'), cuts each blueprint at the next blueprint start,
then reports bytes covered by runs (>= MINRUN) that already occur earlier in another/same blueprint."""
import sys
BASE = 0x1A40
MINRUN = int(sys.argv[1]) if len(sys.argv) > 1 else 8
d = open('work/stock_bin/COMMONXX.BIN', 'rb').read()
# locate table: 19 records of C3 lo hi n with n in 0..4, first n values 0,0,1,...
pat = None
for i in range(len(d) - 76):
    ok = all(d[i+4*k] == 0xC3 and d[i+4*k+3] <= 4 for k in range(19))
    if ok and [d[i+4*k+3] for k in range(19)] == [0,0,1,1,1,1,1,2,2,2,2,3,3,3,3,3,4,4,4]:
        pat = i; break
assert pat is not None, 'table not found'
ents = [d[pat+4*k+1] | d[pat+4*k+2] << 8 for k in range(19)]
starts = sorted(set(ents))
# last blueprint end: assume it follows the largest start by 'size' from header-less scan; use next 23-byte-stub-free guess
bounds = {}
for s, e in zip(starts, starts[1:]):
    bounds[s] = e
last = starts[-1]
bounds[last] = last + 23  # lower bound; refine below if needed
print('table at file offset %#x, %d distinct blueprints' % (pat, len(starts)))
tot = 0
seen = set()          # windows (as bytes) already seen
saved = 0
rows = []
order = [s for s in sorted(starts)]
for s in order:
    bp = d[s-BASE:bounds[s]-BASE]
    tot += len(bp)
    cov = [False]*len(bp)
    for i in range(len(bp)-MINRUN+1):
        if bytes(bp[i:i+MINRUN]) in seen:
            for j in range(i, i+MINRUN): cov[j] = True
    for i in range(len(bp)-MINRUN+1):
        seen.add(bytes(bp[i:i+MINRUN]))
    n = sum(cov)
    saved += n
    names = [k for k, e in enumerate(ents) if e == s]
    rows.append((s, len(bp), n, names))
for s, l, n, names in rows:
    print('&%04X  len %4d  dup %4d  table idx %s' % (s, l, n, names))
print('total %d bytes, duplicated-run bytes %d (minrun %d)' % (tot, saved, MINRUN))
print('(a pointer-share saving is less: each shared run needs the header offset to reach it)')

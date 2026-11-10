#!/usr/bin/env python3
"""Decode ArcElite's token-compressed mission text: arc_text.py IMAGE.bin > text.txt
Token table at &23A10 (records: length byte incl. header and NUL, text, NUL); text is plain bytes with 1B nn = token nn-1, NUL ends a message."""
import sys
d = open(sys.argv[1], 'rb').read()
B = 0x8000
o = 0x23A10 - B; toks = []
while d[o] >= 3 and d[o + d[o] - 1] == 0:
    toks.append(d[o + 1:o + d[o] - 1].decode('latin1')); o += d[o]
toks[7] = 'Commander'; toks[11] = 'Commander, '   # 'c' and 'C, ' are the capitalised forms in context
toks[59] = '\n'
toks[8] = toks[9] = toks[10] = '<VAR>'               # XXX placeholders (filled in by the game)
a, end = 0x28529 - B, 0x31000 - B
out = ''; start = a
while a < end:
    b = d[a]
    if b == 0x1B:
        k = d[a + 1]; a += 2; out += toks[k - 1] if 0 < k <= len(toks) else '<?%02x>' % k
    elif b == 0:
        if out.strip(): print(f'--- &{B+start:05X}\n{out}')
        out = ''; a += 1; start = a
    else:
        out += chr(b) if 32 <= b < 127 or b == 10 else '<%02x>' % b; a += 1

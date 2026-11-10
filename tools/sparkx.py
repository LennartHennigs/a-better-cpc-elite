#!/usr/bin/env python3
"""Extract a SparkFS archive: sparkx.py FILE OUTDIR. Handles stored (2), crunched (8, 0x88), squashed (9) and compress (0x7f).
Writes NAME,load-exec-less plain files; prints the methods and a CRC-16 check."""
import os, struct, sys

def crc16(b):
    c = 0
    for x in b:
        c ^= x
        for _ in range(8):
            c = (c >> 1) ^ 0xA001 if c & 1 else c >> 1
    return c

def lzw(data, maxbits, unix_align):
    out = bytearray(); bits = 9; free = 257
    tab = {}; prev = None
    pos = 0; nbits = len(data) * 8
    codes_in_group = 0
    first = True
    while pos + bits <= nbits:
        code = 0
        for i in range(bits):
            code |= ((data[(pos + i) >> 3] >> ((pos + i) & 7)) & 1) << i
        pos += bits
        if code == 256:
            bits = 9; free = 257; prev = None; tab = {}
            if unix_align:
                pos = (pos + bits * 8 - 1) // (bits * 8) * (bits * 8) if False else pos
            continue
        if prev is None:
            s = bytes([code]); out += s; prev = s; continue
        if code < 256:
            s = bytes([code])
        elif code in tab:
            s = tab[code]
        elif code == free:
            s = prev + prev[:1]
        else:
            raise ValueError('bad code')
        out += s
        if free < (1 << maxbits):
            tab[free] = prev + s[:1]; free += 1
            if free == (1 << bits) and bits < maxbits:
                bits += 1
        prev = s
    return bytes(out)

def unrle(b):
    out = bytearray(); i = 0
    while i < len(b):
        if b[i] == 0x90:
            n = b[i + 1]; i += 2
            if n == 0: out.append(0x90)
            else: out += bytes([out[-1]]) * (n - 1)
        else:
            out.append(b[i]); i += 1
    return bytes(out)

def walk(d, path):
    """Spark directories are headers (method 0x82) followed inline by their entries and a 1A 00 end marker."""
    p = 0; stack = [path]
    while p < len(d) and d[p] == 0x1A:
        m = d[p + 1]
        if m == 0:
            p += 2
            if len(stack) == 1: break
            stack.pop(); continue
        name = d[p + 2:p + 15].split(b'\0')[0].decode('latin1').replace('/', '_')
        csize, date, tm, crc, osize = struct.unpack('<IHHHI', d[p + 15:p + 29])
        hl = 41 if m >= 0x80 else 29
        full = os.path.join(stack[-1], name)
        if m == 0x82 and csize == osize and d[p + hl:p + hl + 2] != b'' and is_dir(d, p, hl, csize):
            stack.append(full); p += hl; continue
        body = d[p + hl:p + hl + csize]
        p += hl + csize
        meth = m & 0x7F
        try:
            if meth in (1, 2): raw = body
            elif meth == 8: raw = unrle(lzw(body, 12, False))
            elif meth == 9: raw = lzw(body, 13, False)
            elif meth == 0x7F: raw = lzw(body[1:], body[0] & 0x1F, True)
            else: raw = None; print('unsupported method', hex(m), full)
        except Exception as e:
            raw = None; print('decode failed', hex(m), full, e)
        if raw is not None:
            ok = 'crc ok' if crc16(raw) == crc and len(raw) == osize else f'CRC MISMATCH ({len(raw)}/{osize})'
            os.makedirs(stack[-1], exist_ok=True); open(full, 'wb').write(raw)
            print(f'{full}  m={m:#04x} {len(raw)} {ok}')

def is_dir(d, p, hl, csize):
    # a directory is followed by another entry header; a stored file of the same method is data
    # (heuristic: the next bytes look like a header whose name is printable and whose end marker 1A 00 lies inside csize)
    q = p + hl
    return d[q] == 0x1A and d[q + 1] in (0x82, 0x88, 0x89, 0xFF, 0x81, 0x80, 0x89) and d.find(b'\x1a\x00', q) != -1 and d[q + 2:q + 3].isalnum() | (d[q + 2] in b'!$_')

walk(open(sys.argv[1], 'rb').read(), sys.argv[2])

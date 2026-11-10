#!/usr/bin/env python3
"""List and extract files from an ADFS E-format ADF (RISC OS): adfs_e.py DISK.ADF OUTDIR"""
import os, struct, sys

def main(adf, out):
    d = open(adf, 'rb').read()
    r = d[4:64]  # disc record
    idlen = r[4]; bpmb = 1 << r[5]; secsize = 1 << r[0]
    root = struct.unpack('<I', r[12:16])[0]
    # fragment map: zone 0 map data starts after the 4-byte header and 60-byte disc record
    bits = lambda p, n: sum(((d[(p + i) >> 3] >> ((p + i) & 7)) & 1) << i for i in range(n))
    frags = {}
    p = 64 * 8
    end = secsize * 8
    while p < end:
        fid = bits(p, idlen)
        q = p + idlen
        while q < end and not (d[q >> 3] >> (q & 7)) & 1:
            q += 1
        if q >= end:
            break
        q += 1
        if fid:
            frags.setdefault(fid, []).append(((p - 512) * bpmb, (q - p) * bpmb))
        p = q

    def read(sin, length):
        fid, off = sin >> 8, sin & 0xFF
        buf = b''
        skip = max(off - 1, 0) * secsize
        for a, l in frags.get(fid, []):
            if skip >= l:
                skip -= l
                continue
            buf += d[a + skip:a + l]
            skip = 0
        return buf[:length]

    def walk(sin, length, path):
        data = read(sin, length)
        assert data[1:5] in (b'Nick', b'Hugo'), (path, data[:8])
        pos = 5
        while data[pos] != 0:
            name = data[pos:pos + 10].split(b'\r')[0].split(b'\0')[0].decode('latin1')
            name = ''.join(chr(ord(c) & 0x7F) for c in name)
            load, exe, ln = struct.unpack('<III', data[pos + 10:pos + 22])
            ind = int.from_bytes(data[pos + 22:pos + 25], 'little')
            attr = data[pos + 25]
            pos += 26
            full = os.path.join(path, name.replace('/', '_'))
            # directories: attr bit 3 set and dir header at the block
            blk = read(ind, 5)
            if attr & 8 and blk[1:5] in (b'Nick', b'Hugo'):
                walk(ind, 2048, full)
                continue
            os.makedirs(path, exist_ok=True)
            open(full, 'wb').write(read(ind, ln))
            print(f'{full}  load={load:08X} exec={exe:08X} len={ln}')
    walk(root, 2048, out)

main(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
"""List the entries of a SparkFS/ARC archive: sparkls.py FILE"""
import struct, sys
d = open(sys.argv[1], 'rb').read()
p = 0
while p < len(d) and d[p] == 0x1A:
    m = d[p + 1]
    if m == 0:
        break
    name = d[p + 2:p + 15].split(b'\0')[0].decode('latin1')
    csize, date, time, crc, osize = struct.unpack('<IHHHI', d[p + 15:p + 29])
    load, exe, attr = struct.unpack('<III', d[p + 29:p + 41]) if m >= 0x80 else (0, 0, 0)
    print(f'{name:14} method={m:#04x} csize={csize} osize={osize} load={load:08X} exec={exe:08X}')
    p += (41 if m >= 0x80 else 29) + csize

#!/usr/bin/env python3
"""Unpack a Microsoft EXEPACK DOS executable (16-byte header, 'RB' signature).

usage: python3 -I tools/unexepack.py IN.EXE OUT.EXE [OUT.BIN]
OUT.EXE is a plain MZ file with relocations restored; OUT.BIN is the raw load image.
"""
import struct
import sys


def unpack(d):
    hdr_paras = struct.unpack_from('<H', d, 8)[0]
    minalloc, maxalloc, ss, sp, _, ip, cs = struct.unpack_from('<7H', d, 0x0A)
    base = hdr_paras * 16
    h = base + cs * 16
    real_ip, real_cs, mem_start, stub_len, real_sp, real_ss, dest_len, sig = struct.unpack_from('<8H', d, h)
    if sig != 0x4252:
        raise SystemExit('no EXEPACK signature at %#x' % h)
    # compressed data: load module start .. header; trailing 0xFF is padding
    src = bytearray(d[base:h])
    while src and src[-1] == 0xFF:
        src.pop()
    out = bytearray(dest_len * 16)
    di = len(out)
    si = len(src) - 1
    while True:
        op = src[si]; si -= 1
        cnt = src[si - 1] | (src[si] << 8); si -= 2
        if op & 0xFE == 0xB0:
            v = src[si]; si -= 1
            di -= cnt
            out[di:di + cnt] = bytes([v]) * cnt
        elif op & 0xFE == 0xB2:
            si -= cnt - 1
            di -= cnt
            out[di:di + cnt] = src[si:si + cnt]
            si -= 1
        else:
            raise SystemExit('bad opcode %#x at %#x' % (op, si))
        if op & 1:
            break
    # the compressed block sits at the top of the image; anything below di is the uncompressed head
    out[:di] = src[:di]
    # relocation table: 16 blocks of (count, offsets...) for segments 0x0000, 0x1000, ... 0xF000
    r = d.index(b'corrupt', h) + 7  # table follows the stub's error message
    relocs = []
    for blk in range(16):
        n = struct.unpack_from('<H', d, r)[0]; r += 2
        for _ in range(n):
            relocs.append((blk * 0x1000, struct.unpack_from('<H', d, r)[0])); r += 2
    return bytes(out), relocs, (real_ip, real_cs, real_ss, real_sp, minalloc, maxalloc)


def write_exe(path, image, relocs, regs):
    ip, cs, ss, sp, minalloc, maxalloc = regs
    reloc_off = 0x1C
    hdr = (reloc_off + 4 * len(relocs) + 15) & ~15
    # trim trailing zero padding is unsafe; keep whole image
    total = hdr + len(image)
    mz = struct.pack('<2s13H', b'MZ', total % 512, (total + 511) // 512, len(relocs), hdr // 16,
                     minalloc, maxalloc, ss, sp, 0, ip, cs, reloc_off, 0)
    t = bytearray(mz)
    for seg, off in relocs:
        t += struct.pack('<HH', off, seg)
    t += b'\0' * (hdr - len(t))
    open(path, 'wb').write(bytes(t) + image)


if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    image, relocs, regs = unpack(d)
    print('image %d bytes, %d relocs, cs:ip=%04x:%04x ss:sp=%04x:%04x' %
          (len(image), len(relocs), regs[1], regs[0], regs[2], regs[3]))
    write_exe(sys.argv[2], image, relocs, regs[:4] + regs[4:])
    if len(sys.argv) > 3:
        open(sys.argv[3], 'wb').write(image)

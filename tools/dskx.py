#!/usr/bin/env python3
"""List and extract AMSDOS files from a CPC DSK image (standard or extended). Read-only.

usage: dskx.py IMAGE.dsk [OUTDIR]
Prints one line per file with the AMSDOS header (load, exec, length); with OUTDIR also
writes each file (header stripped) as NAME and the raw bytes as NAME.raw.
"""
import struct
import sys
from pathlib import Path


def load_sectors(path):
    d = Path(path).read_bytes()
    ext = d[:8] == b"EXTENDED"
    ntracks, nsides = d[0x30], d[0x31]
    sizes = d[0x34:0x34 + ntracks * nsides] if ext else None
    secs, off = {}, 0x100
    for t in range(ntracks * nsides):
        tlen = sizes[t] * 256 if ext else struct.unpack("<H", d[0x32:0x34])[0]
        if tlen == 0:
            continue
        info = d[off:off + 0x100]
        pos = off + 0x100
        for i in range(info[0x15]):
            c, h, r, n = info[0x18 + 8 * i:0x1C + 8 * i]
            actual = struct.unpack("<H", info[0x1E + 8 * i:0x20 + 8 * i])[0] or (128 << n)
            secs[(t, r)] = d[pos:pos + actual]
            pos += actual
        off += tlen
    return secs


def read_files(secs):
    first = min(r for (t, r) in secs if t == 0)
    dirdata = b"".join(secs[(0, first + i)] for i in range(4))
    files = {}
    for i in range(64):
        e = dirdata[i * 32:(i + 1) * 32]
        if e[0] == 0xE5:
            continue
        name = bytes(b & 0x7F for b in e[1:9]).decode("latin1").strip()
        ext = bytes(b & 0x7F for b in e[9:12]).decode("latin1").strip()
        blocks = [b for b in e[16:32] if b]
        files.setdefault((e[0], f"{name}.{ext}"), []).append((e[12], e[15], blocks))
    out = {}
    for key, exts in files.items():
        data = b""
        for _, rc, blocks in sorted(exts):
            for b in blocks:
                for s in (0, 1):
                    ls = b * 2 + s
                    data += secs.get((ls // 9, first + ls % 9), b"\0" * 512)
        # each extent holds rc records of 128 bytes
        out[key] = data[:sum(rc for _, rc, _ in exts) * 128]
    return out


def amsdos_header(b):
    if len(b) < 128:
        return None
    if sum(b[:67]) & 0xFFFF != struct.unpack("<H", b[67:69])[0]:
        return None
    return dict(type=b[18], load=struct.unpack("<H", b[21:23])[0],
                length=struct.unpack("<H", b[24:26])[0],
                exec=struct.unpack("<H", b[26:28])[0])


if __name__ == "__main__":
    files = read_files(load_sectors(sys.argv[1]))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    for (user, name), data in sorted(files.items(), key=lambda kv: kv[0][1]):
        h = amsdos_header(data)
        desc = (f"type={h['type']} load={h['load']:04X} exec={h['exec']:04X} len={h['length']:04X}"
                if h else "no AMSDOS header")
        print(f"{name:14} user={user} size={len(data):6}  {desc}")
        if out:
            safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
            (out / (safe + ".raw")).write_bytes(data)
            (out / safe).write_bytes(data[128:128 + h["length"]] if h else data)

#!/usr/bin/env python3
"""Assemble src/elite and write the four code files into a copy of the Firebird DSK, keeping the AMSDOS headers.

usage: python3 -I tools/build_dsk.py [--missions] [OUT.dsk]      (default work/elite_rebuilt.dsk; base is Elite_UK_Firebird_cracked_trainer.dsk)

The base disk is never modified. Each file keeps its 128-byte AMSDOS header and its size: the new bytes must have the
same length as the old ones (the build is byte-exact apart from the CPC+ fix), otherwise the script stops.
LARGEAXX is assembled with -DFIREBIRD, because the Firebird disk carries that one-byte variant (largeaxx.asm).
"""
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dskx import amsdos_header  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "Elite_UK_Firebird_cracked_trainer.dsk"
MISSIONS = "--missions" in sys.argv   # assemble LARGEAXX and COMMONXX with -DMISSIONS (src/elite/missions_*.asm in the free tails)
args = [a for a in sys.argv[1:] if a != "--missions"]
OUT = Path(args[0]) if args else ROOT / "work" / ("elite_missions.dsk" if MISSIONS else "elite_rebuilt.dsk")
SJASM = Path.home() / ".local/bin/sjasmplus"
FILES = {"LARGEAXX": ["-DFIREBIRD"], "COMMONXX": [], "COMMON2X": [], "MUSIQUEX": []}


def sector_offsets(d):
    """(track, sector id) -> (file offset, size) for a standard or extended DSK."""
    ext = d[:8] == b"EXTENDED"
    ntr = d[0x30] * d[0x31]
    sizes = d[0x34:0x34 + ntr] if ext else None
    out, off = {}, 0x100
    for t in range(ntr):
        tlen = sizes[t] * 256 if ext else struct.unpack("<H", d[0x32:0x34])[0]
        if tlen == 0:
            continue
        info, pos = d[off:off + 0x100], off + 0x100
        for i in range(info[0x15]):
            r, n = info[0x1A + 8 * i], info[0x1B + 8 * i]
            size = struct.unpack("<H", info[0x1E + 8 * i:0x20 + 8 * i])[0] or (128 << n)
            out[(t, r)] = (pos, size)
            pos += size
        off += tlen
    return out


def make_header(name, ext, load, length, exe=0):
    """128-byte AMSDOS header of a binary file (user 0, type 2)."""
    h = bytearray(128)
    h[1:9] = name.ljust(8).encode()
    h[9:12] = ext.ljust(3).encode()
    h[18] = 2
    h[21:23] = struct.pack("<H", load)
    h[24:26] = struct.pack("<H", length)
    h[26:28] = struct.pack("<H", exe)
    h[64:67] = struct.pack("<I", length)[:3]
    h[67:69] = struct.pack("<H", sum(h[:67]) & 0xFFFF)
    return bytes(h)


def add_file(d, secs, first, name, ext, data, load):
    """Add a new AMSDOS file (header + data) to the image: free directory entry, free 1 KB blocks, one extent (files up to 16 KB)."""
    entries = []
    for i in range(64):
        off = secs[(0, first + i // 16)][0] + (i % 16) * 32
        entries.append(off)
    used, free_entry = {0, 1}, None
    for i, off in enumerate(entries):
        e = d[off:off + 32]
        if e[0] == 0xE5:
            free_entry = free_entry if free_entry is not None else i
        else:
            used.update(b for b in e[16:32] if b)
    if free_entry is None:
        sys.exit("no free directory entry")
    payload = make_header(name, ext, load, len(data)) + data
    records = -(-len(payload) // 128)
    if records > 128:
        sys.exit(f"{name}: more than one extent needed")
    nblocks = -(-len(payload) // 1024)
    blocks = [b for b in range(2, 180) if b not in used][:nblocks]
    if len(blocks) < nblocks:
        sys.exit("disk full")
    payload = payload.ljust(nblocks * 1024, b"\xE5")
    for k, b in enumerate(blocks):
        for half in (0, 1):
            ls = b * 2 + half
            pos, size = secs[(ls // 9, first + ls % 9)]
            d[pos:pos + 512] = payload[k * 1024 + half * 512:k * 1024 + half * 512 + 512]
    e = bytearray(32)
    e[0] = 0
    e[1:9] = name.ljust(8).encode()
    e[9:12] = ext.ljust(3).encode()
    e[15] = records
    e[16:16 + len(blocks)] = bytes(blocks)
    d[entries[free_entry]:entries[free_entry] + 32] = e
    return blocks


def flight_image(tag):
    """Assemble COMMONXX with -DMISSIONS (-DFL_<tag> for C/P; "0" is the default image) and slice mxFlightBase..mxFlightEnd (the COMMONXX tail)."""
    with tempfile.TemporaryDirectory() as tmp:
        out, sym = Path(tmp) / "c.bin", Path(tmp) / "c.sym"
        flags = ["-DMISSIONS"] + ([f"-DFL_{tag}"] if tag != "0" else [])
        r = subprocess.run([str(SJASM), *flags, f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"flight image {tag}: assemble failed\n{r.stdout[-400:]}")
        labels = {}
        for line in sym.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] in ("mxFlightBase:", "mxFlightEnd:"):
                labels[parts[0][:-1]] = int(parts[2], 16)
        return labels["mxFlightBase"], out.read_bytes()[labels["mxFlightBase"] - 0x1A40:labels["mxFlightEnd"] - 0x1A40]


def overlay(tag):
    """Assemble LARGEAXX with -DMISSIONS -DOVL_<tag> and slice mxOverlayBase..mxOverlayEnd (labels from the symbol file)."""
    with tempfile.TemporaryDirectory() as tmp:
        out, sym = Path(tmp) / "l.bin", Path(tmp) / "l.sym"
        r = subprocess.run([str(SJASM), "-DMISSIONS", f"-DOVL_{tag}", "-DFIREBIRD", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/largeaxx.asm")],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"overlay {tag}: assemble failed\n{r.stdout[-400:]}")
        labels = {}
        for line in sym.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] in ("mxOverlayBase:", "mxOverlayEnd:"):
                labels[parts[0][:-1]] = int(parts[2], 16)
        return labels["mxOverlayBase"], out.read_bytes()[labels["mxOverlayBase"] - 0x840:labels["mxOverlayEnd"] - 0x840]


def main():
    d = bytearray(BASE.read_bytes())
    secs = sector_offsets(d)
    first = min(r for (t, r) in secs if t == 0)
    dirdata = b"".join(d[secs[(0, first + i)][0]:secs[(0, first + i)][0] + 512] for i in range(4))
    ents = {}
    for i in range(64):
        e = dirdata[i * 32:(i + 1) * 32]
        if e[0] == 0xE5:
            continue
        name = (bytes(b & 0x7F for b in e[1:9]).decode().strip() + "." + bytes(b & 0x7F for b in e[9:12]).decode().strip())
        ents.setdefault(name, []).append((e[12], e[15], [b for b in e[16:32] if b]))

    def file_slots(name):
        """Disk offsets of every 512-byte half block of a file, in file order, plus its length in bytes."""
        slots, total = [], 0
        for _, rc, blocks in sorted(ents[name]):
            total += rc * 128
            for b in blocks:
                for s in (0, 1):
                    ls = b * 2 + s
                    slots.append(secs[(ls // 9, first + ls % 9)][0])
        return slots, total

    with tempfile.TemporaryDirectory() as tmp:
        for n, defs in FILES.items():
            out = Path(tmp) / f"{n}.bin"
            extra = ["-DMISSIONS"] if MISSIONS and n in ("LARGEAXX", "COMMONXX") else []
            r = subprocess.run([str(SJASM), *defs, *extra, f"--raw={out}", str(ROOT / "src/elite" / f"{n.lower()}.asm")],
                               capture_output=True, text=True)
            if r.returncode:
                sys.exit(f"{n}: assemble failed\n{r.stdout[-400:]}{r.stderr[-400:]}")
            new = out.read_bytes()
            slots, total = file_slots(f"{n}.BIN")
            hdr = bytes(d[slots[0]:slots[0] + 128])
            h = amsdos_header(hdr)
            if h is None or h["length"] != len(new):
                sys.exit(f"{n}: header length {h and h['length']} != built length {len(new)}")
            data = hdr + new
            data += b"\0" * (total - len(data))   # old file keeps its record padding
            for k, off in enumerate(slots):
                chunk = data[k * 512:(k + 1) * 512]
                if len(chunk) == 0:
                    break
                d[off:off + len(chunk)] = chunk
            print(f"{n}.BIN: {len(new)} bytes written, header kept (load {h['load']:04X})")
    if MISSIONS:
        for tag in ("C", "P", "T"):
            base, data = overlay(tag)
            blocks = add_file(d, secs, first, f"MISSION{tag}", "BIN", data, base)
            print(f"MISSION{tag}.BIN: {len(data)} bytes at &{base:04X}, blocks {blocks}")
        for tag in ("0", "C", "P", "T", "A"):
            base, data = flight_image(tag)
            blocks = add_file(d, secs, first, f"MFLIGHT{tag}", "BIN", data, base)
            print(f"MFLIGHT{tag}.BIN: {len(data)} bytes at &{base:04X}, blocks {blocks}")
    OUT.write_bytes(d)
    print("wrote", OUT)


main()

#!/usr/bin/env python3
"""Assemble src/elite and write the four code files into a copy of the Firebird DSK, keeping the AMSDOS headers.

usage: python3 -I tools/build_dsk.py [--missions | --de | --fr] [OUT.dsk]      (default work/elite_rebuilt.dsk; base is Elite_UK_Firebird_cracked_trainer.dsk;
       --de assembles src/elite_de into a copy of Elite_DE_cracked.dsk, default work/elite_de_rebuilt.dsk;
       --fr assembles src/elite_fr into a copy of the French Firebird disk, default work/elite_fr_rebuilt.dsk)

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
import dskx  # noqa: E402
from dskx import amsdos_header, sector_offsets  # noqa: E402
from hide_files import hide_entries  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DE = "--de" in sys.argv
FR = "--fr" in sys.argv
if DE and FR:
    sys.exit("--de and --fr cannot be combined")
BASE = ROOT / ("Elite_DE_cracked.dsk" if DE else "Elite (1985)(Firebird Software)(fr).dsk" if FR else "Elite_UK_Firebird_cracked_trainer.dsk")
SRC = ROOT / ("src/elite_de" if DE else "src/elite_fr" if FR else "src/elite")
MISSIONS = "--missions" in sys.argv   # assemble LARGEAXX and COMMONXX with -DMISSIONS (src/elite/missions_*.asm in the free tails)
if (DE or FR) and MISSIONS:
    sys.exit("--de/--fr and --missions cannot be combined: the missions exist for the English build only (src/elite)")
args = [a for a in sys.argv[1:] if a not in ("--missions", "--de", "--fr")]
OUT = Path(args[0]) if args else ROOT / "work" / ("elite_de_rebuilt.dsk" if DE else "elite_fr_rebuilt.dsk" if FR else "elite_missions.dsk" if MISSIONS else "elite_rebuilt.dsk")
if OUT.resolve() == BASE.resolve() or OUT.resolve().parent == ROOT:   # CLAUDE.md: never modify the original disks in the project root
    sys.exit(f"{OUT}: refusing to write a disk into the project root (the originals live there); use work/")
SJASM = Path.home() / ".local/bin/sjasmplus"
FILES = {"LARGEAXX": [] if DE or FR else ["-DFIREBIRD"], "COMMONXX": ["-DTITLESEL"], "COMMON2X": [], "MUSIQUEX": ["-DTITLESEL"]}   # TITLESEL: cursor keys change the title ship


def add_file(d, secs, first, name, ext, data, load):
    """Add a new AMSDOS file (header + data); files up to 16 KB (one extent)."""
    payload = dskx.make_header(name, ext, load, len(data)) + data
    return dskx.add_payload(d, secs, first, name, ext, payload, -(-len(payload) // 128))


def flight_image(tag):
    """Assemble COMMONXX with -DMISSIONS (-DFL_<tag> for C/P/T/S/R; "0" is the default image) and slice mxFlightBase..mxFlightEnd (the COMMONXX tail)."""
    with tempfile.TemporaryDirectory() as tmp:
        out, sym = Path(tmp) / "c.bin", Path(tmp) / "c.sym"
        flags = ["-DENHANCED", *FILES["COMMONXX"], "-DMISSIONS"] + ([f"-DFL_{tag}"] if tag != "0" else [])   # the flags of the COMMONXX that goes on the disk
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
        r = subprocess.run([str(SJASM), "-DENHANCED", *FILES["LARGEAXX"], "-DMISSIONS", f"-DOVL_{tag}", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/largeaxx.asm")],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"overlay {tag}: assemble failed\n{r.stdout[-400:]}")
        labels = {}
        for line in sym.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] in ("mxOverlayBase:", "mxOverlayEnd:"):
                labels[parts[0][:-1]] = int(parts[2], 16)
        return labels["mxOverlayBase"], out.read_bytes()[labels["mxOverlayBase"] - 0x840:labels["mxOverlayEnd"] - 0x840]


def add_readme(d, secs, first):
    """src/disk/README.TXT as an ASCII file (CRLF, ends with Ctrl-Z, last record padded with Ctrl-Z)."""
    data = (ROOT / "src/disk/README.TXT").read_bytes()
    records = -(-len(data) // 128)
    dskx.add_payload(d, secs, first, "README", "TXT", data.ljust(records * 128, b"\x1a"), records)
    print(f"README.TXT: {len(data)} bytes")


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
            r = subprocess.run([str(SJASM), "-DENHANCED", *defs, *extra, f"--raw={out}", str(SRC / f"{n.lower()}.asm")],
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
        for tag in ("C", "P", "T", "R"):
            base, data = overlay(tag)
            blocks = add_file(d, secs, first, f"MISSION{tag}", "BIN", data, base)
            print(f"MISSION{tag}.BIN: {len(data)} bytes at &{base:04X}, blocks {blocks}")
        for tag in ("0", "C", "P", "T", "S", "R"):
            base, data = flight_image(tag)
            blocks = add_file(d, secs, first, f"MFLIGHT{tag}", "BIN", data, base)
            print(f"MFLIGHT{tag}.BIN: {len(data)} bytes at &{base:04X}, blocks {blocks}")
    if MISSIONS:
        add_readme(d, secs, first)
    hidden, shown = hide_entries(d, secs, first)   # System attribute on everything but .BAS and .TXT (CLAUDE.md rule; code in tools/hide_files.py)
    print(f"{len(hidden)} directory entries hidden (System attribute), visible: {', '.join(sorted(shown))}")
    OUT.write_bytes(d)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

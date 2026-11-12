#!/usr/bin/env python3
"""Assemble src/elite128 and write the four code files into a copy of the Firebird DSK (128K build, filled hulls). Based on tools/build_dsk.py.

usage: python3 -I tools/build_dsk128.py [OUT.dsk]    (default work/elite128.dsk; base is
       Elite_UK_Firebird_cracked_trainer.dsk, never modified). The disk always carries the mission overlays and flight images (src/elite128/config.inc defines the flags; --missions is accepted and ignored)
       as tools/build_dsk.py does (README.TXT included).

Needs the generated inputs of tools/check_src128.sh (it makes them): work/elite128/shipdata128.asm, fill.bin (assembled with the address of hullVertexBuf) and fill128.bin.
In the relocated layout COMMON2X.BIN is the code block for RAM bank 7 (loaded at &C000, copied by bankInit) and the window page (&4000-&7FFF of COMMONXX.BIN) carries the stage areas: the fill module and its records ride in its blank screen rows: fill.bin at +&800, fill128.bin at +&1000; bankInit
(commonxx.asm) copies them into RAM bank 6 at the start of Init_. Each file keeps its size and AMSDOS header. Hides everything but .BAS and .TXT (CLAUDE.md rule).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dskx  # noqa: E402
from dskx import amsdos_header, sector_offsets  # noqa: E402
from hide_files import hide_entries  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "Elite_UK_Firebird_cracked_trainer.dsk"
MISSIONS = True      # the 128K build has one variant (src/elite128/config.inc): missions, enhanced UI, title selection
_args = [a for a in sys.argv[1:] if a != "--missions"]      # --missions is accepted and ignored (old command lines)
OUT = Path(_args[0]) if _args else ROOT / "work/elite128.dsk"
if OUT.resolve() == BASE.resolve() or OUT.resolve().parent == ROOT:
    sys.exit(f"{OUT}: refusing to write a disk into the project root (the originals live there); use work/")
SJASM = Path.home() / ".local/bin/sjasmplus"
SRC = ROOT / "src/elite128"
FILES = {"LARGEAXX": [], "COMMONXX": [], "COMMON2X": [], "MUSIQUEX": []}      # flags live in src/elite128/config.inc
STAGE_FILL, STAGE_DATA = 0x0800, 0x1000          # offsets in COMMON2X (&C800, &D000); the mission overlays and images use &D800-&FDFF


def add_file(d, secs, first, name, ext, data, load):
    payload = dskx.make_header(name, ext, load, len(data)) + data
    return dskx.add_payload(d, secs, first, name, ext, payload, -(-len(payload) // 128))


def sliced(src, flags, lo_label, hi_label, base_addr):
    """Assemble SRC with FLAGS and slice lo_label..hi_label (labels from the symbol file); returns (address, bytes)."""
    with tempfile.TemporaryDirectory() as tmp:
        out, sym = Path(tmp) / "x.bin", Path(tmp) / "x.sym"
        r = subprocess.run([str(SJASM), *flags, f"--raw={out}", f"--sym={sym}", str(SRC / src)], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{src} {flags}: assemble failed\n{r.stdout[-400:]}")
        labels = {}
        for line in sym.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] in (lo_label + ":", hi_label + ":"):
                labels[parts[0][:-1]] = int(parts[2], 16)
        return labels[lo_label], out.read_bytes()[labels[lo_label] - base_addr:labels[hi_label] - base_addr]


def main():
    work = ROOT / "work/elite128"
    for f in ("fill.bin", "fill128.bin"):
        if not (work / f).exists():
            sys.exit(f"missing {work / f}: run bash tools/check_src128.sh first")
    fill, data = (work / "fill.bin").read_bytes(), (work / "fill128.bin").read_bytes()
    assert len(fill) <= 0x600 and len(data) <= 0x600, (len(fill), len(data))
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
            extra = []
            r = subprocess.run([str(SJASM), *defs, *extra, f"--raw={out}", str(SRC / f"{n.lower()}.asm")], capture_output=True, text=True)
            if r.returncode:
                sys.exit(f"{n}: assemble failed\n{r.stdout[-400:]}{r.stderr[-400:]}")
            new = bytearray(out.read_bytes())
            if n == "COMMONXX":
                PAGE = 0x4000 - 0x1A40                       # the window page inside COMMONXX.BIN: blank screen rows that bankInit finds at &C000+offset in RAM bank 3
                stage = [(STAGE_FILL, fill), (STAGE_DATA, data)]
                if MISSIONS:      # overlays (bank 4: slots of 0x240 at &D800, &DC80, &E000, &E480) and flight images (bank 5: 0x260 at &E800, &EC60, &F000, &F460, &F800, &FC60); bankInit copies them
                    for i, tag in enumerate("CPTR"):
                        base, blob = sliced("largeaxx.asm", [f"-DOVL_{tag}"], "mxOverlayBase", "mxOverlayEnd", 0x840)
                        assert len(blob) <= 0x240, (tag, len(blob))
                        stage.append((0x1800 + (i // 2) * 0x800 + (i % 2) * 0x240, blob))
                    for i, tag in enumerate("0CPTSR"):
                        flags = ([f"-DFL_{tag}"] if tag != "0" else [])
                        base, blob = sliced("commonxx.asm", flags, "mxFlightBase", "mxFlightEnd", 0x1A40)
                        assert len(blob) <= 0x260, (tag, len(blob))
                        stage.append((0x2800 + (i // 2) * 0x800 + (i % 2) * 0x260, blob))
                for off, blob in stage:
                    assert not any(new[PAGE + off:PAGE + off + len(blob)]), f"the window page is not blank at +{off:04X}"
                    new[PAGE + off:PAGE + off + len(blob)] = blob
            slots, total = file_slots(f"{n}.BIN")
            hdr = bytes(d[slots[0]:slots[0] + 128])
            h = amsdos_header(hdr)
            if h is None or h["length"] != len(new):
                sys.exit(f"{n}: header length {h and h['length']} != built length {len(new)}")
            blob = hdr + bytes(new)
            blob += b"\0" * (total - len(blob))
            for k, off in enumerate(slots):
                chunk = blob[k * 512:(k + 1) * 512]
                if len(chunk) == 0:
                    break
                d[off:off + len(chunk)] = chunk
            print(f"{n}.BIN: {len(new)} bytes written, header kept (load {h['load']:04X})")
    if MISSIONS:
        txt = (ROOT / "src/disk/README.TXT").read_bytes()
        recs = -(-len(txt) // 128)
        dskx.add_payload(d, secs, first, "README", "TXT", txt.ljust(recs * 128, b"\x1a"), recs)
    hidden, shown = hide_entries(d, secs, first)
    print(f"{len(hidden)} directory entries hidden (System attribute), visible: {', '.join(sorted(shown))}")
    OUT.write_bytes(d)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

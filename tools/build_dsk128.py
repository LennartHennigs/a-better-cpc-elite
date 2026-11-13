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
from dskx import sector_offsets  # noqa: E402
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
    for f in ("fill.bin", "fill128.bin", "fill128_late.bin", "tt.bin"):
        if not (work / f).exists():
            sys.exit(f"missing {work / f}: run bash tools/check_src128.sh first")
    fill, data = (work / "fill.bin").read_bytes(), (work / "fill128.bin").read_bytes()
    assert len(data) <= 0x540, f"fill128.bin ({len(data)} bytes) runs into the title cache module at 0x6540"
    data = data.ljust(0x540, b"\0") + (work / "tt.bin").read_bytes()      # fill_tt.asm is assembled for 0x6540: its bytes follow the records
    assert len(data) <= 0x5C0, f"the title cache module ({len(data)} bytes in all) runs into the late records at 0x65C0"
    data = data.ljust(0x5C0, b"\0") + (work / "fill128_late.bin").read_bytes()      # alloy plate and Constrictor records (ship128.py LATE)
    assert len(fill) <= 0x600 and len(data) <= 0x800, (len(fill), len(data))      # bankInit copies 0x800 bytes of the data stage; overlays start at +0x1800
    d = bytearray(BASE.read_bytes())
    secs = sector_offsets(d)
    first = min(r for (t, r) in secs if t == 0)
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
            h = dskx.overwrite_file(d, secs, first, f"{n}.BIN", new)
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

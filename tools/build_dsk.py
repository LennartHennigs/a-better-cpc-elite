#!/usr/bin/env python3
"""Assemble src/elite and write the four code files into a copy of the Firebird DSK, keeping the AMSDOS headers.

usage: python3 -I tools/build_dsk.py [--stock] [--missions | --de | --fr] [OUT.dsk]      (default work/elite_rebuilt.dsk; base is Elite_UK_Firebird_cracked_trainer.dsk;
       --stock assembles with no enhancement flags (the original bytes, CPC+ fix included) and adds nothing: work/elite_original.dsk, with --de/--fr work/elite_original_de.dsk / _fr.dsk;
       --de assembles src/elite_de into a copy of Elite_DE_cracked.dsk, default work/elite_de_rebuilt.dsk;
       --fr assembles src/elite_fr into a copy of the French Firebird disk, default work/elite_fr_rebuilt.dsk)

The base disk is never modified. Each file keeps its 128-byte AMSDOS header and its size: the new bytes must have the
same length as the old ones (the build is byte-exact apart from the CPC+ fix), otherwise the script stops.
LARGEAXX is assembled with -DFIREBIRD, because the Firebird disk carries that one-byte variant (largeaxx.asm).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dskx  # noqa: E402
from dskx import sector_offsets  # noqa: E402
from hide_files import hide_entries  # noqa: E402
from symfile import read_sym  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DE = "--de" in sys.argv
FR = "--fr" in sys.argv
if DE and FR:
    sys.exit("--de and --fr cannot be combined")
BASE = ROOT / "disks" / ("Elite_DE_cracked.dsk" if DE else "Elite (1985)(Firebird Software)(fr).dsk" if FR else "Elite_UK_Firebird_cracked_trainer.dsk")
SRC = ROOT / ("src/elite_de" if DE else "src/elite_fr" if FR else "src/elite")
STOCK = "--stock" in sys.argv         # original bytes: no -DENHANCED, -DTITLESEL or -DTRAFFIC
MISSIONS = "--missions" in sys.argv   # assemble LARGEAXX and COMMONXX with -DMISSIONS (src/elite/missions_*.asm in the free tails)
if (DE or FR) and MISSIONS:
    sys.exit("--de/--fr and --missions cannot be combined: the missions exist for the English build only (src/elite)")
if STOCK and MISSIONS:
    sys.exit("--stock and --missions cannot be combined: the missions need the enhanced build")
args = [a for a in sys.argv[1:] if a not in ("--stock", "--missions", "--de", "--fr")]
OUT = Path(args[0]) if args else ROOT / "work" / ("elite_original" + ("_de" if DE else "_fr" if FR else "") + ".dsk" if STOCK else "elite_de_rebuilt.dsk" if DE else "elite_fr_rebuilt.dsk" if FR else "elite_missions.dsk" if MISSIONS else "elite_rebuilt.dsk")
if OUT.resolve() == BASE.resolve() or dskx.is_original(OUT):   # CLAUDE.md: never modify the original disks (disks/)
    sys.exit(f"{OUT}: refusing to write a disk into the project root or disks/ (the originals live there); use work/")
SJASM = Path.home() / ".local/bin/sjasmplus"
FILES = {"LARGEAXX": [] if DE or FR else ["-DFIREBIRD"], "COMMONXX": ["-DTITLESEL", "-DTRAFFIC"], "COMMON2X": [], "MUSIQUEX": ["-DTITLESEL"]}   # TITLESEL: cursor keys change the title ship; TRAFFIC: C64-like spawn odds (docs/_ship_packs.md)
if MISSIONS:      # the hostile ships start at a random distance and direction (the routine is in the flight tail, src/elite/missions_flight.asm; docs/_ship_spawning.md)
    FILES["COMMONXX"].append("-DSPAWN_VARIANCE")
if STOCK:
    FILES = {"LARGEAXX": [], "COMMONXX": [], "COMMON2X": [], "MUSIQUEX": []}   # no -DFIREBIRD either: it drops the cargo-capacity test (LARGEAXX &0998)


def flight_image(tag):
    """Assemble COMMONXX with -DMISSIONS (-DFL_<tag> for C/P/T/S/R and the ship packs 1-7; "0" is the default image) and slice mxFlightBase..mxFlightEnd (the COMMONXX tail)."""
    with tempfile.TemporaryDirectory() as tmp:
        out, sym = Path(tmp) / "c.bin", Path(tmp) / "c.sym"
        flags = ["-DENHANCED", *FILES["COMMONXX"], "-DMISSIONS"] + ([f"-DFL_{tag}"] if tag != "0" else [])   # the flags of the COMMONXX that goes on the disk
        r = subprocess.run([str(SJASM), *flags, f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"flight image {tag}: assemble failed\n{r.stdout[-400:]}")
        labels = read_sym(sym, "mxFlightBase", "mxFlightEnd")
        return labels["mxFlightBase"], out.read_bytes()[labels["mxFlightBase"] - 0x1A40:labels["mxFlightEnd"] - 0x1A40]


def overlay(tag):
    """Assemble LARGEAXX with -DMISSIONS -DOVL_<tag> and slice mxOverlayBase..mxOverlayEnd (labels from the symbol file)."""
    with tempfile.TemporaryDirectory() as tmp:
        out, sym = Path(tmp) / "l.bin", Path(tmp) / "l.sym"
        r = subprocess.run([str(SJASM), "-DENHANCED", *FILES["LARGEAXX"], "-DMISSIONS", f"-DOVL_{tag}", f"--raw={out}", f"--sym={sym}", str(ROOT / "src/elite/largeaxx.asm")],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"overlay {tag}: assemble failed\n{r.stdout[-400:]}")
        labels = read_sym(sym, "mxOverlayBase", "mxOverlayEnd")
        return labels["mxOverlayBase"], out.read_bytes()[labels["mxOverlayBase"] - 0x840:labels["mxOverlayEnd"] - 0x840]


def add_readme(d, secs, first):
    """src/disk/README.TXT as an ASCII file (CRLF, ends with Ctrl-Z, last record padded with Ctrl-Z)."""
    data = (ROOT / "src/disk/README.TXT").read_bytes()
    dskx.add_padded(d, secs, first, "README", "TXT", data)
    print(f"README.TXT: {len(data)} bytes")


def add_showship(d, secs, first):
    """The ship viewer (tools/build_showship.sh): SHOWSHPS.BAS (visible) and SHIPS.BIN (hidden, loaded to &4000). Added with dskx, not iDSK: iDSK may put blocks on the
    two odd-sector tracks of the base disk, which AMSDOS cannot read."""
    bas, ships = ROOT / "src/cheats/SHOWSHPS.BAS", ROOT / "work/showship/SHIPS.BIN"
    if not (bas.exists() and ships.exists()):
        print("SHOWSHPS: not added (run tools/build_showship.sh first)")
        return
    data = bas.read_bytes()   # AMSDOS header included
    dskx.add_padded(d, secs, first, "SHOWSHPS", "BAS", data)
    dskx.add_file(d, secs, first, "SHIPS", "BIN", ships.read_bytes(), 0x4000)
    print(f"SHOWSHPS.BAS {len(data)} bytes, SHIPS.BIN {ships.stat().st_size} bytes")


def replace_trainer(d, secs, first):
    """The base disk carries Firebird's own CHEAT.BAS (wrong cloak entry, loads the game itself); delete it and put ours there (TRAINER.BAS, src/cheats/TRAINER.BAS, which chains to the hidden CHEATB.BIN =
    src/cheats/CHEATB.BAS; docs/_cheats.md). Both files keep the AMSDOS header the tokeniser gave them."""
    cheat, cheatb = ROOT / "src/cheats/TRAINER.BAS", ROOT / "src/cheats/CHEATB.BAS"
    if not (cheat.exists() and cheatb.exists()):
        sys.exit("trainer: src/cheats/TRAINER.BAS or CHEATB.BAS missing (tools/build_cheat.sh makes them)")
    removed = dskx.remove_file(d, secs, first, "CHEAT", "BAS")
    dskx.add_padded(d, secs, first, "TRAINER", "BAS", cheat.read_bytes(), replace=True)
    dskx.add_padded(d, secs, first, "CHEATB", "BIN", cheatb.read_bytes(), replace=True)
    print(f"TRAINER.BAS: removed Firebird's CHEAT.BAS ({removed} entry), added ours and CHEATB.BIN")


def main():
    d = bytearray(BASE.read_bytes())
    secs = sector_offsets(d)
    first = min(r for (t, r) in secs if t == 0)
    with tempfile.TemporaryDirectory() as tmp:
        for n, defs in FILES.items():
            out = Path(tmp) / f"{n}.bin"
            extra = ["-DMISSIONS"] if MISSIONS and n in ("LARGEAXX", "COMMONXX") else []
            r = subprocess.run([str(SJASM), *([] if STOCK else ["-DENHANCED"]), *defs, *extra, f"--raw={out}", str(SRC / f"{n.lower()}.asm")],
                               capture_output=True, text=True)
            if r.returncode:
                sys.exit(f"{n}: assemble failed\n{r.stdout[-400:]}{r.stderr[-400:]}")
            new = out.read_bytes()
            h = dskx.overwrite_file(d, secs, first, f"{n}.BIN", new)
            print(f"{n}.BIN: {len(new)} bytes written, header kept (load {h['load']:04X})")
    if MISSIONS:
        for tag in ("C", "P", "T", "R"):
            base, data = overlay(tag)
            blocks = dskx.add_file(d, secs, first, f"MISSION{tag}", "BIN", data, base)
            print(f"MISSION{tag}.BIN: {len(data)} bytes at &{base:04X}, blocks {blocks}")
        for tag in ("0", "C", "P", "T", "S", "R", "1", "2", "3", "4", "5", "6", "7"):   # 1-7: ship packs (docs/_ship_packs.md)
            base, data = flight_image(tag)
            blocks = dskx.add_file(d, secs, first, f"MFLIGHT{tag}", "BIN", data, base)
            print(f"MFLIGHT{tag}.BIN: {len(data)} bytes at &{base:04X}, blocks {blocks}")
    if MISSIONS:
        add_readme(d, secs, first)
        add_showship(d, secs, first)
        replace_trainer(d, secs, first)
    hidden, shown = hide_entries(d, secs, first)   # System attribute on everything but .BAS and .TXT (CLAUDE.md rule; code in tools/hide_files.py)
    print(f"{len(hidden)} directory entries hidden (System attribute), visible: {', '.join(sorted(shown))}")
    dskx.write_atomic(OUT, d)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

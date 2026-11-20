#!/usr/bin/env python3
"""Assemble src/elite128 and write the four code files into a copy of the Firebird DSK (128K build, filled hulls). Based on tools/build_dsk.py.

usage: python3 -I tools/build_dsk128.py [OUT.dsk]    (default build/elite128.dsk; base is
       disks/Elite_UK_Firebird_cracked_trainer.dsk, never modified). The disk always carries the mission overlays and flight images (src/elite128/config.inc defines the flags; --missions is accepted and ignored)
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
BASE = ROOT / "disks" / "Elite_UK_Firebird_cracked_trainer.dsk"
MISSIONS = True      # the 128K build has one variant (src/elite128/config.inc): missions, enhanced UI, title selection
_args = [a for a in sys.argv[1:] if a != "--missions"]      # --missions is accepted and ignored (old command lines)
OUT = Path(_args[0]) if _args else ROOT / "build/elite128.dsk"
if OUT.resolve() == BASE.resolve() or dskx.is_original(OUT):      # CLAUDE.md: never modify the original disks (disks/)
    sys.exit(f"{OUT}: refusing to write a disk into the project root or disks/ (the originals live there); use build/ or work/")
SJASM = Path.home() / ".local/bin/sjasmplus"
SRC = ROOT / "src/elite128"
FLIGHT_TAGS = "01234567CPTSR"      # flight image tags in slot order (the FLS_x numbers of missions_flight.asm)
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


def symbols(src, flags=()):
    """Assemble SRC (only for its symbol file) and return {label: address}."""
    with tempfile.TemporaryDirectory() as tmp:
        sym = Path(tmp) / "x.sym"
        r = subprocess.run([str(SJASM), *flags, f"--raw={Path(tmp) / 'x.bin'}", f"--sym={sym}", str(SRC / src)], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{src}: assemble failed\n{r.stdout[-400:]}")
        out = {}
        for line in sym.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0].endswith(":"):
                out[parts[0][:-1]] = int(parts[2], 16)
        return out


def laser_sights():
    """The laser sights overlay (lasersights128.asm): assembled at the address of bankInit, carried in the data stage and copied over bankInit by its last step."""
    cx, c2 = symbols("commonxx.asm"), symbols("common2x.asm")
    defs = [f"-DHOME={cx['bankInit']}", f"-DVIEWDIR={cx['Viewdirection']}", f"-DLASERTYPES={cx['laserTypes']}", f"-DCURCFG={cx['curCfg']}", f"-DDRAWLINE={c2['drawLaserLine']}"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "ls.bin"
        r = subprocess.run([str(SJASM), *defs, f"--raw={out}", str(SRC / "lasersights128.asm")], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"lasersights128.asm: assemble failed\n{r.stdout[-400:]}")
        blob = out.read_bytes()
    size = cx["laserSightsSize"]
    assert len(blob) <= size, f"the laser sights ({len(blob)} bytes) do not fit laserSightsSize ({size})"
    print(f"laser sights: {len(blob)} of {size} bytes, at &{cx['laserSightsHome']:04X}")
    return blob.ljust(size, b"\0")


def main():
    work = ROOT / "work/elite128"
    for f in ("fill.bin", "fill128.bin", "fill128_late.bin", "fill128_packs.bin", "tt.bin"):
        if not (work / f).exists():
            sys.exit(f"missing {work / f}: run bash tools/check_src128.sh first")
    hulls = (work / "hulls_source.txt").read_text().strip() if (work / "hulls_source.txt").exists() else "unknown"
    print(f"hull source: {hulls} (HULLS=stock|arcelite, tools/ship128.py)")
    fill, data = (work / "fill.bin").read_bytes(), (work / "fill128.bin").read_bytes()
    packs_records = (work / "fill128_packs.bin").read_bytes()
    assert len(packs_records) <= 0x600, len(packs_records)      # the stage area at +0x2800 is one blank 0x600 block; bankInit copies it to bank 6 &6800
    assert len(data) <= 0x540, f"fill128.bin ({len(data)} bytes) runs into the title cache module at 0x6540"
    data = data.ljust(0x540, b"\0") + (work / "tt.bin").read_bytes()      # fill_tt.asm is assembled for 0x6540: its bytes follow the records
    assert len(data) <= 0x5C0, f"the title cache module ({len(data)} bytes in all) runs into the late records at 0x65C0"
    data = data.ljust(0x5C0, b"\0") + (work / "fill128_late.bin").read_bytes()      # alloy plate and Constrictor records (ship128.py LATE)
    assert len(fill) <= 0x600 and len(data) <= 0x700, (len(fill), len(data))      # the laser sights ride at +0x700 of the data stage      # bankInit copies 0x800 bytes of the data stage; overlays start at +0x1800
    d = bytearray(BASE.read_bytes())
    secs = sector_offsets(d)
    first = min(r for (t, r) in secs if t == 0)
    flight_images = []
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
                stage = [(STAGE_FILL, fill), (STAGE_DATA, data), (STAGE_DATA + 0x700, laser_sights()), (0x2800, packs_records)]
                if MISSIONS:      # overlays (bank 4: slots of 0x240 at &D800, &DC80, &E000, &E480) and flight images (bank 5: 0x260 at &E800, &EC60, &F000, &F460, &F800, &FC60); bankInit copies them
                    for i, tag in enumerate("CPTR"):
                        base, blob = sliced("largeaxx.asm", [f"-DOVL_{tag}"], "mxOverlayBase", "mxOverlayEnd", 0x840)
                        assert len(blob) <= 0x240, (tag, len(blob))
                        stage.append((0x1800 + (i // 2) * 0x800 + (i % 2) * 0x240, blob))
                    for tag in FLIGHT_TAGS:
                        flags = ([f"-DFL_{tag}"] if tag != "0" else [])
                        base, blob = sliced("commonxx.asm", flags, "mxFlightBase", "mxFlightEnd", 0x1A40)
                        assert len(blob) <= 0x260, (tag, len(blob))
                        flight_images.append(blob.ljust(0x260, b"\0"))
                for off, blob in stage:
                    assert not any(new[PAGE + off:PAGE + off + len(blob)]), f"the window page is not blank at +{off:04X}"
                    new[PAGE + off:PAGE + off + len(blob)] = blob
            h = dskx.overwrite_file(d, secs, first, f"{n}.BIN", new)
            print(f"{n}.BIN: {len(new)} bytes written, header kept (load {h['load']:04X})")
    # The flight images (mission images, order FLIGHT_TAGS, 0x260 bytes each) ride behind INDICATO: bankInit loads the file into bank 5 at &5000, so slot 0 is at &6000 (mxBankFlightImpl).
    ind = dskx.read_files(dskx.load_sectors(BASE))[(0, "INDICATO.BIN")]
    ind_data = ind[128:128 + 0x1000]
    assert len(ind_data) == 0x1000 and dskx.amsdos_header(ind)["length"] == 0x1000, "unexpected INDICATO.BIN"
    new_ind = ind_data + b"".join(flight_images)
    assert 0x1000 + len(flight_images) * 0x260 <= 0x3000, "the flight images run past the end of bank 5"
    dskx.remove_file(d, secs, first, "INDICATO", "BIN")
    dskx.add_file(d, secs, first, "INDICATO", "BIN", new_ind, 0x5000)
    print(f"INDICATO.BIN: {len(new_ind)} bytes (INDICATO + {len(flight_images)} flight images)")
    if MISSIONS:
        txt = (ROOT / "src/disk/README.TXT").read_bytes().replace(b'RUN"ELITE\r\n', b'RUN"ELITE128\r\n').replace(b'RUN"ELITE\n', b'RUN"ELITE128\n')
        txt = txt.replace(b"Amstrad CPC 464 / 6128", b"Amstrad CPC 6128 only")
        for gone in (b'RUN"TRAINER   cheats', b'RUN"EDITSAVE  edit a saved CMDR', b'RUN"LISTSAVE  list saved CMDRs'):      # tools of the 64K disk, not on this one
            txt = txt.replace(gone + b"\r\n", b"").replace(gone + b"\n", b"")
        txt = txt.replace(b"every ship in 3D", b"the ships, filled")
        recs = -(-len(txt) // 128)
        dskx.add_payload(d, secs, first, "README", "TXT", txt.ljust(recs * 128, b"\x1a"), recs)
    # The ship viewer (RUN"SHOWSHPS): a stand-alone program like the 64K disk's, but with the filled hulls of the game. SHOWSHPS.BAS loads the ships into RAM banks 4-6 and the program
    # (src/viewer128/viewer.asm, the page flip prototype) at &8000; the data come from tools/mk_viewer128.py. The binaries are hidden like every other non-BASIC file.
    subprocess.run([sys.executable, "-I", str(ROOT / "tools/mk_viewer128.py")], check=True, capture_output=True)
    r = subprocess.run([str(SJASM), "--nologo", "--msg=err", "viewer.asm"], cwd=ROOT / "src/viewer128", capture_output=True, text=True)
    if r.returncode:
        sys.exit("viewer.asm: assemble failed\n" + r.stdout[-400:])
    vdir = ROOT / "work/viewer128"
    bas = ROOT / "src/viewer128/SHOWSHPS.BAS"
    if bas.exists():
        dskx.add_padded(d, secs, first, "SHOWSHPS", "BAS", bas.read_bytes())
        for n in (4, 5, 6):
            dskx.add_file(d, secs, first, f"SHIPS{n}", "BIN", (vdir / f"ships{n}.bin").read_bytes(), 0x4000)
        dskx.add_file(d, secs, first, "VIEWER", "BIN", (vdir / "viewer.bin").read_bytes(), 0x8000)
        print("ship viewer: SHOWSHPS.BAS, SHIPS4-6.BIN, VIEWER.BIN")
    else:
        print("SHOWSHPS: not added (bash tools/build_show128.sh makes SHOWSHPS.BAS)")
    # The loader is ELITE128.BAS on this disk (RUN"ELITE128): Firebird's ELITE.BAS, same program, renamed with its AMSDOS header (name and checksum) so that nobody starts the 128K disk as the 64K game.
    if not dskx.rename_file(d, secs, first, "ELITE", "BAS", "ELITE128"):
        sys.exit("ELITE.BAS is not on the base disk")
    print("ELITE.BAS renamed ELITE128.BAS")
    # Firebird's own CHEAT.BAS pokes 64K addresses (docs/_cheats.md): on the relocated layout it would write into the wrong bytes, so the disk does not carry it.
    removed = dskx.remove_file(d, secs, first, "CHEAT", "BAS")
    print(f"CHEAT.BAS (Firebird's, 64K pokes): {removed} directory entries removed")
    hidden, shown = hide_entries(d, secs, first)
    print(f"{len(hidden)} directory entries hidden (System attribute), visible: {', '.join(sorted(shown))}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(d)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

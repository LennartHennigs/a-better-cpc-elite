#!/usr/bin/env python3
"""Generate the ship viewer: work/showship/SHIPS.BIN (every blueprint in one file) and src/cheats/SHOWSHPS.ASC (the CPC BASIC program that draws them).

usage: python3 -I tools/mk_showship.py        (then tools/build_showship.sh tokenises the program and builds work/showship.dsk)

SHIPS.BIN is loaded to &4000 by the program (everything must stay below &A67B, where AMSDOS keeps its work area): the Z80 routine (showship.asm) fills the first &1000 bytes and the ship data follows at &5000. Layout: byte 0 = number of ships, then 24-byte entries from byte 1 (20 bytes name, NUL padded; word offset of the
blueprint from the start of the file; 2 spare bytes), then the blueprints. A blueprint is the 23-byte CPC header (counts at +3 vertices, +4 edges, +5 faces; word offsets
at +12 vertices, +14 edges, +16 faces; bounty +8; speed +6; energy +7; kill score +21) followed by 6-byte vertices (x y z magnitudes, signs in bits 7/6/5 of byte 3),
4-byte edges (distance, vertex a, vertex b, two face numbers as nibbles) and 4-byte faces (normal x y z magnitudes, signs in bits 7/6/5 of byte 3), see docs/_ship_packs.md.
Stock hulls are cut out of work/bin_stock/COMMONXX.BIN, the extra ones from an assembly of src/elite/missions_ships.asm and missions_hull.asm.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SJASM = Path.home() / ".local/bin/sjasmplus"
OUT = ROOT / "work/showship/ships.dat"
ASC = ROOT / "src/cheats/SHOWSHPS.ASC"
CODE = ROOT / "work/showship/SHOWCODE.BIN"
COMBINED = ROOT / "work/showship/SHIPS.BIN"   # code at &4000, ships at &5000: one file

# (display name, label); the first block is in the stock COMMONXX, the second in the extra hulls
STOCK = [
    ("CORIOLIS STATION", "shipdatCoriolis"), ("MISSILE", "shipdatMissile"), ("ESCAPE POD", "shipdatCapsule"), ("ALLOY PLATE", "shipdatAlloy"),
    ("CARGO CANISTER", "shipdatCargo"), ("SPLINTER", "shipdatSplinter"), ("ASTEROID", "shipdatAsteroid"), ("ROCK HERMIT", "shipdatRockHermit"),
    ("VIPER", "shipdatViper"), ("COBRA MK III", "SHIPDATSINGLETRADER"), ("PYTHON", "SHIPDATBIGTRADER"), ("PYTHON PIRATE", "shipdatPythonPirate"),
    ("COBRA MK III PIRATE", "shipdatCobraMk3Pirate"), ("ASP MK II", "shipdatAspMk2"), ("FER-DE-LANCE", "shipdatFerDeLance"), ("THARGOID", "shipdatThargoid"),
    ("SIDEWINDER", "SHIPDATPIRATE1"), ("KRAIT", "SHIPDATPIRATE2"), ("THARGON", "shipdatThargon"),
]
EXTRA = [
    ("GECKO", "shipdatGecko"), ("COBRA MK I", "shipdatCobraMk1"), ("WORM", "shipdatWorm"), ("MORAY", "shipdatMoray"), ("MAMBA", "shipdatMamba"),
    ("ADDER", "shipdatAdder"), ("BOA", "shipdatBoa"), ("BOULDER", "shipdatBoulder"), ("ANACONDA", "shipdatAnaconda"), ("SHUTTLE", "shipdatShuttle"),
    ("CONSTRICTOR", "shipdatConstrictor"),
]
HULLS = ["GECKO", "COBRAMK1", "WORM", "MORAY", "MAMBA", "ADDER", "BOA", "BOULDER", "ANACONDA", "SHUTTLE"]


def assemble(src, defines, org, tmp):
    raw, sym = Path(tmp) / "o.bin", Path(tmp) / "o.sym"
    r = subprocess.run([str(SJASM), *defines, f"--raw={raw}", f"--sym={sym}", str(src)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{src}: assemble failed\n{r.stdout[-600:]}")
    syms = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^(\w+):\s+EQU\s+0x([0-9A-Fa-f]+)", sym.read_text(), re.M)}
    return raw.read_bytes(), syms


def blueprint(data, off, name):
    """cut one blueprint out of data at off, check its header, return the bytes"""
    h = data[off:off + 23]
    nv, ne, nf = h[3], h[4], h[5]
    vo, eo, fo = (h[12] | h[13] << 8), (h[14] | h[15] << 8), (h[16] | h[17] << 8)
    n = max(vo + 6 * nv, eo + 4 * ne, fo + 4 * nf if nf else 0)   # the alloy plate has no faces (offset 0); the order is vertices, edges, faces otherwise
    bp = data[off:off + n]
    assert len(bp) == n, (name, len(bp), n)
    for e in range(ne):
        d, a, b, f = bp[eo + 4 * e:eo + 4 * e + 4]
        assert a < nv and b < nv, (name, "edge", e, a, b, nv)
        assert nf == 0 or ((f >> 4) < nf and (f & 15) < nf), (name, "edge face", e, f, nf)
    return bp


def pack(name, bp):
    """the record the Z80 routine copies into its tables: 11-byte header (nv ne nf ha nfp kill bounty speed energy), vertices x y z 0 0 0 0 0 scaled to +-125,
    edges a b f1 f2, faces nx ny nz 0 with the normal scaled to +-64 (a ship without faces gets one zero face and ha = 1: all its edges are drawn)"""
    import math
    nv, ne, nf = bp[3], bp[4], bp[5]
    vo, eo, fo = (bp[12] | bp[13] << 8), (bp[14] | bp[15] << 8), (bp[16] | bp[17] << 8)
    V = []
    for j in range(nv):
        x, y, z, g = bp[vo + 6 * j:vo + 6 * j + 4]
        V.append((-x if g & 128 else x, -y if g & 64 else y, -z if g & 32 else z))
    r = max(math.sqrt(x * x + y * y + z * z) for x, y, z in V) or 1
    sc = 125 / r
    out = bytearray([nv, ne, nf or 1, 1 if nf == 0 else 0, nf]) + bytes(bp[21:23]) + bytes(bp[8:10]) + bytes([bp[6], bp[7]])
    for x, y, z in V:
        out += bytes([int(round(x * sc)) & 255, int(round(y * sc)) & 255, int(round(z * sc)) & 255, 0, 0, 0, 0, 0])
    for j in range(ne):
        d, a, b, f = bp[eo + 4 * j:eo + 4 * j + 4]
        out += bytes([a, b, f >> 4, f & 15])
    if nf == 0:
        out += bytes(4)
    for j in range(nf):
        x, y, z, g = bp[fo + 4 * j:fo + 4 * j + 4]
        fm = max(x, y, z, 1)
        sx, sy, sz = (int(round(c * 64 / fm)) for c in (x, y, z))
        out += bytes([(-sx if g & 128 else sx) & 255, (-sy if g & 64 else sy) & 255, (-sz if g & 32 else sz) & 255, 0])
    return bytes(out)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        stock_raw, stock_syms = assemble(ROOT / "src/elite/commonxx.asm", [], 0x1A40, tmp)
        wrap = Path(tmp) / "extra.asm"
        wrap.write_text("".join(f"    DEFINE HULL_{h}\n" for h in HULLS) + f'    ORG 0x8000\n    INCLUDE "{ROOT}/src/elite/missions_ships.asm"\n    INCLUDE "{ROOT}/src/elite/missions_hull.asm"\n')
        extra_raw, extra_syms = assemble(wrap, [], 0x8000, tmp)
    stock_file = (ROOT / "work/bin_stock/COMMONXX.BIN").read_bytes()
    # the default build is the stock game byte for byte (check_src.sh), either file would do; the original binary is the reference
    ships = []
    for name, label in STOCK:
        ships.append((name, blueprint(stock_file, stock_syms[label] - 0x1A40, name)))
    for name, label in EXTRA:
        ships.append((name, blueprint(extra_raw, extra_syms[label] - 0x8000, name)))
    n = len(ships)
    packed = [(name, pack(name, bp)) for name, bp in ships]
    body = bytearray()
    table = bytearray()
    base = 1 + 24 * n
    for name, rec in packed:
        assert len(name) <= 20, name
        table += name.encode().ljust(20, b"\0") + (base + len(body)).to_bytes(2, "little") + b"\0\0"
        body += rec
    blob = bytes([n]) + bytes(table) + bytes(body)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(blob)
    for i, (name, bp) in enumerate(ships):
        print(f"{i + 1:2d} {name:20s} {len(bp):4d} bytes  vertices {bp[3]:2d} edges {bp[4]:2d} faces {bp[5]:2d}")
    print(f"wrote {OUT} ({len(blob)} bytes, {n} ships)")
    write_program(n)
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "code.bin"
        r = subprocess.run([str(SJASM), f"--raw={raw}", str(ROOT / "src/cheats/showship.asm")], capture_output=True, text=True)
        if r.returncode:
            sys.exit("showship.asm: assemble failed\n" + r.stdout[-600:])
        CODE.write_bytes(raw.read_bytes())
    print(f"wrote {CODE} ({CODE.stat().st_size} bytes)")
    code = CODE.read_bytes()
    assert len(code) <= 0x1000
    COMBINED.write_bytes(code.ljust(0x1000, b"\0") + blob)
    print(f"wrote {COMBINED} ({COMBINED.stat().st_size} bytes, loads at &4000: code, then the ships at &5000)")


# the BASIC program (line numbers 10 ..); the ship count comes from the file. The hot loop (rotation and line drawing) is the Z80 routine in src/cheats/showship.asm (SHOWCODE.BIN at &4000);
# the ship tables it reads (vertices &4810, faces &4A10, edges &4A50, old segments &4B50, parameters &4800) are filled by its `select` entry (CALL &4003) from the packed
# record of the ship (pack() below), so a change of ship is one CALL.
LINES = [
    '10 MODE 1:MEMORY &3FFF:BORDER 0:INK 0,0:INK 1,25:INK 2,11:INK 3,1',
    '20 LOAD"SHIPS.BIN",&4000:n=PEEK(&5000):DEG',
    '35 POKE &4806,INT(COS(-20)*127+.5) AND 255:POKE &4807,INT(SIN(-20)*127+.5) AND 255',
    '40 i=0:a=0:GOSUB 1000',
    '100 a=a+6:IF a>=360 THEN a=a-360',
    '110 POKE &4804,INT(COS(a)*127+.5) AND 255:POKE &4805,INT(SIN(a)*127+.5) AND 255',
    '120 CALL &4000',
    '130 k$=INKEY$:IF k$="" THEN 100',
    '140 IF k$=CHR$(243) OR k$="." THEN i=(i+1) MOD n:GOSUB 1000:GOTO 100',
    '150 IF k$=CHR$(242) OR k$="," THEN i=(i+n-1) MOD n:GOSUB 1000:GOTO 100',
    '160 IF k$="q" OR k$="Q" THEN INK 0,1:INK 1,24:INK 2,20:INK 3,6:BORDER 1:MODE 1:END',
    '170 GOTO 100',
    '1000 REM select ship i: the Z80 routine copies its packed record into the tables; draw the frame, print the name and the facts (Elite colours: black, sky blue lines, yellow text)',
    '1010 e=&5001+24*i:t$="":FOR j=0 TO 19:q=PEEK(e+j):IF q>0 THEN t$=t$+CHR$(q)',
    '1020 NEXT:b=&5000+PEEK(e+20)+256*PEEK(e+21)',
    '1030 POKE &480C,b AND 255:POKE &480D,b\\256:CALL &4003',
    '1040 CLS:GRAPHICS PEN 2:MOVE 16,44:DRAW 624,44:DRAW 624,344:DRAW 16,344:DRAW 16,44',
    '1050 t$=t$+" ("+MID$(STR$(i+1),2)+"/"+MID$(STR$(n),2)+")":PEN 1:LOCATE 21-LEN(t$)\\2,2:PRINT t$',
    '1060 LOCATE 1,24:PEN 2:PRINT "KILLS ";:PEN 1:PRINT USING "##.## ";(PEEK(b+5)+256*PEEK(b+6))/512;:PEN 2:PRINT "BOUNTY ";:PEN 1:PRINT USING "###.# ";(PEEK(b+7)+256*PEEK(b+8))/10;',
    '1070 PEN 2:PRINT "SPD ";:PEN 1:PRINT USING "### ";PEEK(b+9);:PEN 2:PRINT "EN ";:PEN 1:PRINT USING "###";PEEK(b+10);',
    '1080 PEN 2:LOCATE 18,25:PRINT CHR$(242);" ";CHR$(243);" Q";:PEN 1',
    '1090 RETURN',
]


def write_program(n):
    ASC.write_bytes(("\r\n".join(LINES) + "\r\n").encode("ascii") + b"\x1a")
    print(f"wrote {ASC} ({len(LINES)} lines)")


main()

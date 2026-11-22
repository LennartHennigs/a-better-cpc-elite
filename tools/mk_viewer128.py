#!/usr/bin/env python3
"""Data for the 128K ship viewer (RUN"SHOWSHPS): every ship of the 128K build, filled, as pre-projected rotation frames, in the format of the page flip prototype (tools/proto_fill/flip.asm).

usage: python3 -I tools/mk_viewer128.py [--source stock|arcelite]      (or the HULLS environment variable, like tools/ship128.py; default stock)
The hulls and their fill triangles come from tools/ship128.py: the same triangles the game fills, from the same source (stock: the stock blueprints through tools/hullfill.py; arcelite: ArcElite's
hulls fitted to the stock axes, third party, so the files in work/viewer128/ stay out of git; the Constrictor and the nine ship pack hulls come from Fessor's data in both). Each ship turns about its y axis with a fixed tilt; per ship the file holds 160 bytes of triangles (v0 v1 v2 pattern) and NFRAMES frames of 104 bytes
(x[32], y[32], draw order[36], bounding box), the logic of tools/proto_fill/gen.py. Writes into work/viewer128/: ships4.bin, ships5.bin, ships6.bin (RAM banks 4-6, SHIPS_PER_BANK ships each),
info.inc, winding.inc, tables.bin, rowtab_flip.bin.
info.inc holds one record per ship for the Z80 viewer: the screen address of its name line and of its facts line (centred), the name with the "(n/29)" counter and the four numbers of the
blueprint header (kill score, bounty, speed, energy) as text, like the 64K viewer's (tools/mk_showship.py): "KILLS 1.23 BOUNTY 40.0 SPD 28 EN 20".
"""
import importlib.util
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work/viewer128"
NFRAMES = 12
FRAMESZ = 104
SHIPSZ = 160 + NFRAMES * FRAMESZ
SHIPS_PER_BANK = 11
sys.argv = [sys.argv[0]] + [a for i, a in enumerate(sys.argv) if a == "--source" or (i and sys.argv[i - 1] == "--source")]      # ship128.py reads --source from sys.argv, nothing else


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s128 = load("ship128", "tools/ship128.py")
gen = s128.gen
# (shown name, label of the blueprint whose geometry is drawn, label of the blueprint whose header gives the numbers): the order of the 64K viewer (tools/mk_showship.py). The traders and the
# Rock Hermit share the geometry of the blueprint after them (tools/ship128.py STUB_OF) but have their own header.
STOCK = [("CORIOLIS STATION", "shipdatCoriolis", "shipdatCoriolis"), ("MISSILE", "shipdatMissile", "shipdatMissile"), ("ESCAPE POD", "shipdatCapsule", "shipdatCapsule"),
         ("ALLOY PLATE", "shipdatAlloy", "shipdatAlloy"), ("CARGO CANISTER", "shipdatCargo", "shipdatCargo"), ("SPLINTER", "shipdatSplinter", "shipdatSplinter"),
         ("ASTEROID", "shipdatAsteroid", "shipdatAsteroid"), ("ROCK HERMIT", "shipdatAsteroid", "shipdatRockHermit"), ("VIPER", "shipdatViper", "shipdatViper"),
         ("COBRA MK III", "shipdatCobraMk3Pirate", "SHIPDATSINGLETRADER"), ("PYTHON", "shipdatPythonPirate", "SHIPDATBIGTRADER"), ("PYTHON PIRATE", "shipdatPythonPirate", "shipdatPythonPirate"),
         ("COBRA MK III PIRATE", "shipdatCobraMk3Pirate", "shipdatCobraMk3Pirate"), ("ASP MK II", "shipdatAspMk2", "shipdatAspMk2"), ("FER-DE-LANCE", "shipdatFerDeLance", "shipdatFerDeLance"),
         ("THARGOID", "shipdatThargoid", "shipdatThargoid"), ("SIDEWINDER", "SHIPDATPIRATE1", "SHIPDATPIRATE1"), ("KRAIT", "SHIPDATPIRATE2", "SHIPDATPIRATE2"), ("THARGON", "shipdatThargon", "shipdatThargon")]
PACK_NAMES = {"Gecko": "GECKO", "CobraMk1": "COBRA MK I", "Worm": "WORM", "Moray": "MORAY", "Mamba": "MAMBA", "Adder": "ADDER", "Boa": "BOA", "Anaconda": "ANACONDA", "Shuttle": "SHUTTLE"}


def extra_headers():
    """{label: 23-byte blueprint header} of the Constrictor and the ship pack hulls: src/elite/missions_hull.asm and missions_ships.asm assembled as tools/mk_showship.py does"""
    with tempfile.TemporaryDirectory() as tmp:
        wrap = Path(tmp) / "extra.asm"
        hulls = "".join(f"    DEFINE HULL_{h.upper()}\n" for h in PACK_NAMES)
        wrap.write_text(hulls + f'    ORG 0x8000\n    INCLUDE "{ROOT}/src/elite/missions_ships.asm"\n    INCLUDE "{ROOT}/src/elite/missions_hull.asm"\n')
        raw, sym = Path(tmp) / "o.bin", Path(tmp) / "o.sym"
        r = subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), f"--raw={raw}", f"--sym={sym}", str(wrap)], capture_output=True, text=True)
        if r.returncode:
            sys.exit("extra hulls: assemble failed\n" + r.stdout[-400:])
        img = raw.read_bytes()
        out = {}
        for line in sym.read_text().splitlines():
            p = line.split()
            if len(p) >= 3 and p[0].endswith(":") and p[0][:-1].startswith("shipdat"):
                a = int(p[2], 16) - 0x8000
                out[p[0][:-1]] = img[a:a + 23]
    return out


def ships():
    """-> [(shown name, vertices, triangles (v0, v1, v2, pattern, group), blueprint header)]"""
    m, sym = s128.stock_image(), s128.symbols()
    extra = extra_headers()
    out = []
    for shown, label, hlabel in STOCK:
        if label == "shipdatAlloy":
            q, tris, _ = s128.alloy(m, sym[label])
            tris = [(a, b, c, {118: s128.PATTERNS[0], 42: s128.PATTERNS[1]}[col], g) for a, b, c, col, g in tris]      # brightest first, as record() ranks them
        elif s128.SOURCE == "arcelite":      # as ship128.py main() does: the ArcElite hull on the stock axes, its colours ranked into the patterns like record()
            q, tris, _, _, _, _ = s128.fit(s128.stock_points(m, sym[label]), *s128.gen.parse(s128.HULL[label]), label)
            pat = {c: s128.PATTERNS[i % len(s128.PATTERNS)] for i, c in enumerate(sorted({t[3] for t in tris}, reverse=True))}
            tris = [(a, b, c, pat[col], g) for a, b, c, col, g in tris]
        else:
            q, tris, _, _, _, _ = s128.stock_fit(m, sym[label], label)
        out.append((shown, q, tris, bytes(m[sym[hlabel]:sym[hlabel] + 23])))
    _, q, tris, _ = s128.constrictor()
    _, packs, _ = s128.pack_hulls()
    for name, shown in PACK_NAMES.items():
        out.append((shown, packs[name][0], packs[name][1], extra[f"shipdat{name}"]))
    out.append(("CONSTRICTOR", q, tris, extra["shipdatConstrictor"]))
    return out


def sub(a, b): return [a[i] - b[i] for i in range(3)]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def dot(a, b): return sum(x * y for x, y in zip(a, b))


def build_ship(name, pts, tris):
    """gen.build_ship with our triangles: the pattern is given, the groups too. -> (facet bytes, frames bytes, screen winding, vertices, triangles)"""
    assert len(pts) <= 32 and len(tris) <= 40, (name, len(pts), len(tris))
    facets = [[t[0], t[1], t[2], t[3], t[4]] for t in tris]
    g = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    signs = []
    for f in facets:
        a_, b_, c_ = (pts[i] for i in f[:3])
        n = cross(sub(b_, a_), sub(c_, a_))
        signs.append(1 if dot(n, sub([(a_[i] + b_[i] + c_[i]) / 3 for i in range(3)], g)) > 0 else -1)
    major = 1 if sum(signs) >= 0 else -1
    facets = [[f[0], f[2], f[1]] + f[3:] if (sg != major) != (major > 0) else f for f, sg in zip(facets, signs)]
    wind = -1
    group_of = {i: f[4] for i, f in enumerate(facets)}
    radius = max(math.dist(p, g) for p in pts)
    scale = 62 / radius
    dist = radius * 3.2
    frames = bytearray()
    orders, shots = [], []
    for k in range(NFRAMES):
        ang = 2 * math.pi * k / NFRAMES
        tilt = math.radians(-18)
        pr = []
        for p in pts:
            x, y, z = (p[i] - g[i] for i in range(3))
            x, z = x * math.cos(ang) + z * math.sin(ang), -x * math.sin(ang) + z * math.cos(ang)
            y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
            pr.append((x, y, z))
        xs, ys = [], []
        for x, y, z in pr:
            f = dist / (dist + z)
            xs.append(max(0, min(255, round(128 + x * scale * f))))
            ys.append(max(0, min(127, round(64 - y * scale * f))))
        depth = {}
        for i, f in enumerate(facets):
            a, b, c = (pr[j] for j in f[:3])
            n = [wind * v for v in cross(sub(b, a), sub(c, a))]
            cen = [(a[t] + b[t] + c[t]) / 3 for t in range(3)]
            if dot(n, [-cen[0], -cen[1], -dist - cen[2]]) > 0:
                depth[i] = -(a[2] + b[2] + c[2]) / 3
        gdepth = {}
        for i in depth:
            gdepth.setdefault(group_of[i], []).append(depth[i])
        vis = sorted((sum(gdepth[group_of[i]]) / len(gdepth[group_of[i]]), group_of[i], i) for i in depth)
        order = []
        for _, _, i in vis:
            f = facets[i]
            cr = (xs[f[1]] - xs[f[0]]) * (ys[f[2]] - ys[f[0]]) - (xs[f[2]] - xs[f[0]]) * (ys[f[1]] - ys[f[0]])
            order.append((i, cr))
        orders.append(order)
        shots.append((xs, ys))
    pos = sum(1 for o in orders for _, cr in o if cr > 0)
    neg = sum(1 for o in orders for _, cr in o if cr < 0)
    clockwise = pos >= neg
    dropped = min(pos, neg)
    assert dropped * 4 <= pos + neg, f"{name}: {dropped} of {pos + neg} visible triangles wound the other way on the screen"
    for (xs, ys), o in zip(shots, orders):
        order = [i for i, cr in o if cr != 0 and (cr > 0) == clockwise]
        assert len(order) <= 35
        used = {v for i in order for v in facets[i][:3]}
        bx = [xs[v] for v in used] or [0]
        by = [ys[v] for v in used] or [0]
        box = bytes([max(0, min(bx) - 1), min(255, max(bx) + 1), max(0, min(by) - 1), min(127, max(by) + 1)])
        frames += bytes(xs + [0] * (32 - len(xs))) + bytes(ys + [0] * (32 - len(ys))) + bytes(order + [0xFF] * (36 - len(order))) + box
    fac = b"".join(bytes([f[0], f[1], f[2], f[3]]) for f in facets)
    return fac, bytes(frames), clockwise, len(pts), len(facets)


NAME_ROW, FACT_ROW = 2, 22      # text rows of the name line and the facts line (the hint is on row 24, the frame round the viewport at lines 37 and 170)
NAMESZ, VALSZ = 28, 20


def write_info(infos):
    """info.inc: NSHIPS, INFOSZ and infoTable, one record per ship: dw name address, dw facts address, the name line (NAMESZ bytes, NUL padded), four NUL-terminated numbers (VALSZ bytes)"""
    n = len(infos)
    recs = []
    for i, (name, h) in enumerate(infos):
        kills = (h[21] + 256 * h[22]) / 512
        vals = [f"{kills:.2f}", f"{(h[8] + 256 * h[9]) / 10:.1f}", f"{h[6]}", f"{h[7]}"]
        title = f"{name} ({i + 1}/{n})"
        facts = f"KILLS {vals[0]} BOUNTY {vals[1]} SPD {vals[2]} EN {vals[3]}"
        assert len(title) < NAMESZ and len(facts) <= 40, (title, facts)
        cell = lambda row, length: 0x4000 + 80 * row + 2 * ((40 - length) // 2)
        blob = cell(NAME_ROW, len(title)).to_bytes(2, "little") + cell(FACT_ROW, len(facts)).to_bytes(2, "little")
        blob += title.encode().ljust(NAMESZ, b"\0") + b"".join(v.encode() + b"\0" for v in vals).ljust(VALSZ, b"\0")
        assert len(blob) == 4 + NAMESZ + VALSZ
        recs.append((blob, facts))
    with open(OUT / "info.inc", "w") as fh:
        fh.write(f"NSHIPS equ {n}\nINFOSZ equ {4 + NAMESZ + VALSZ}\ninfoTable:\n")
        for (blob, facts), (name, _) in zip(recs, infos):
            fh.write(f"    db {','.join(str(b) for b in blob)}    ; {name}: {facts}\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    gen.OUT = OUT
    blocks, infos, clock = [], [], set()
    lst = ships()
    for shown, pts, tris, head in lst:
        fac, frames, clockwise, nv, nt = build_ship(shown, pts, tris)
        clock.add(clockwise)
        blocks.append(fac.ljust(160, b"\0") + frames)
        infos.append((shown, head))
        print(f"{shown:16s} {nv:2d} vertices {nt:2d} triangles")
    assert len(clock) == 1, "ships with different screen winding"
    gen.write_common(clock.pop())
    n = len(blocks)
    assert n <= 3 * SHIPS_PER_BANK and all(len(b) == SHIPSZ for b in blocks)
    for bank in range(3):
        chunk = blocks[bank * SHIPS_PER_BANK:(bank + 1) * SHIPS_PER_BANK]
        (OUT / f"ships{4 + bank}.bin").write_bytes(b"".join(chunk).ljust(SHIPSZ * SHIPS_PER_BANK, b"\0")[:0x4000])
    write_info(infos)
    (OUT / "hulls_source.txt").write_text(s128.SOURCE + "\n")
    print(f"{n} ships ({s128.SOURCE} hulls),", NFRAMES, "frames,", SHIPSZ, "bytes each")


if __name__ == "__main__":
    main()

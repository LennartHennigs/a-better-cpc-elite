#!/usr/bin/env python3
"""Blueprints plus fill data for the 128K build: the filled hulls, from one of two sources (--source, or the HULLS environment variable; default stock).

usage: python3 -I tools/ship128.py [--source stock|arcelite]
  stock     the triangles are built from the CPC's own blueprints (tools/hullfill.py): vertices, edges and face normals of the stock game, plus a few details of our
            own; no third-party data. The Constrictor is based on Fessor's hull (src/elite/missions_hull.asm): his header and vertices, the triangles built from his edges
            and faces.
  arcelite  ArcElite's hulls (Ian Bell's ship table, third party, work/arcelite/) turned into CPC blueprints: the original look of this build. That data and everything
            generated from it stay out of git (NOTICE item 10).
Both fill the same fixed slot of the resident area (HULL_REGION_SIZE in src/elite128/commonxx.asm), so every address stays the same and switching needs no sync_equs.
The text below describes the ArcElite path (the stock path is the same pipeline with tools/hullfill.py in place of the axis fit).

Inputs (all under work/, third party data never enters the repo):
  src/elite/commonxx.asm         assembled here (work/elite128/c.bin, c.sym): the blueprints and the ship table `shipGFXdataTable` at &1B78
  work/elite128/c.sym            symbol file of src/elite/commonxx.asm (made here with sjasmplus if missing)
  work/arcelite/x_ships/B5052480.C   ArcElite's tables, read through tools/proto_fill/gen.py (`parse`)
Outputs in work/elite128/:
  shipdata128.asm   one blueprint per stock ship label, same label names and order as the stock data: the 23-byte header is the stock header
                    (energy, laser, bounty, scale, ... stay classic) with the counts and offsets patched; the geometry is the ArcElite hull as
                    vertices only (6 bytes each: |x|, |y|, |z|, signs<<5 | 0x1F, face nibbles 0x00 = always visible); edges and faces are empty
                    (the filled path culls by screen winding, see docs_other/_filled_ships.md, local only). The alloy plate has no ArcElite hull: its four stock
                    vertices become two double-sided quads' worth of triangles (one colour per side).
  fill128.bin       bank 6 payload: byte 20 (ship types), 20 words (offset of the type's record from the start of the file, 0 = none), then records
                    ntri, flags (bit 0: convex), ntri x (v0, v1, v2, pattern<<5 | group). The records of the alloy plate and the Constrictor do not fit in front of
                    the title cache module (0x540): they are in fill128_late.bin, which tools/build_dsk128.py places at LATE (after that module)
  hull_constrictor.asm  the mission hull (ship type 19) for src/elite128/missions_hull.asm, based on Fessor's hull: his header, with vertices only: his own vertices
                    (stock) or the ArcElite CONSTRICTOR vertices fitted to his hull (arcelite; his own vertices only pick the axis map and the scale)
  ship128_points.json  the quantised vertices per ship type (for tests)
  ship128_report.txt  per hull: chosen axis map, quantisation error, vertex/triangle/group counts
  hulls_source.txt  which source (stock or arcelite) made the files in this folder

The axis map (permutation and signs, 48 candidates) is chosen per hull by a scale-free nearest-point match between the stock vertices and the ArcElite
vertices; ArcElite and the CPC do not agree on the nose direction. The match is only a guess: look at every hull in the engine before relying on it,
and override a wrong pick in AXIS_OVERRIDE.
"""
import importlib.util
import itertools
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work/elite128"
spec = importlib.util.spec_from_file_location("gen", ROOT / "tools/proto_fill/gen.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
spec = importlib.util.spec_from_file_location("hullfill", ROOT / "tools/hullfill.py")
hullfill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hullfill)
SOURCE = (sys.argv[sys.argv.index("--source") + 1] if "--source" in sys.argv else os.environ.get("HULLS", "stock")).lower()
if SOURCE not in ("stock", "arcelite"):
    sys.exit(f"ship128.py: unknown hull source {SOURCE!r} (stock or arcelite)")

# stock blueprint label -> ArcElite hull ("ALLOY": no ArcElite hull, see alloy()). Stubs (RockHermit, SingleTrader, BigTrader) share the geometry of the blueprint
# that follows them and are patched from it.
HULL = {"shipdatCoriolis": "CORIOLIS", "shipdatMissile": "MISSILE", "shipdatCapsule": "ESCAPEPOD", "shipdatAlloy": "ALLOY", "shipdatCargo": "CANNISTER",
        "shipdatSplinter": "FRAGMENT", "shipdatAsteroid": "ASTEROID", "shipdatViper": "VIPER", "shipdatPythonPirate": "PYTHON",
        "shipdatCobraMk3Pirate": "COBRA", "shipdatAspMk2": "ASP", "shipdatFerDeLance": "FERDELANCE", "shipdatThargoid": "THARGOID",
        "SHIPDATPIRATE1": "SIDEWINDER", "SHIPDATPIRATE2": "KRAIT", "shipdatThargon": "THARGON"}
STUB_OF = {"shipdatRockHermit": "shipdatAsteroid", "SHIPDATSINGLETRADER": "shipdatCobraMk3Pirate", "SHIPDATBIGTRADER": "shipdatPythonPirate"}
# The Coriolis is a cube: the extents rule cannot tell its axes apart. The entry slot is what matters: stock has it on the +z face (4 vertices at z = +160, 20 wide in x, 60 tall in y),
# ArcElite on the +y face (4 vertices at y = +750, 300 along x, 100 along z). So stock (x, y, z) = (arc z, arc x, arc y): a rotation (cyclic permutation, no sign change).
AXIS_OVERRIDE = {"shipdatCoriolis": ((2, 0, 1), (1, 1, 1))}      # label -> (perm, signs), e.g. "shipdatViper": ((0, 1, 2), (1, 1, -1)); applied to the ArcElite point (x, y, z)
CONVEX = {"shipdatCoriolis", "shipdatMissile", "shipdatCapsule", "shipdatCargo", "shipdatSplinter", "shipdatViper", "SHIPDATPIRATE1", "shipdatThargon"}  # unchecked guess; the tool does not test convexity yet
TABLE = 0x1B78
LATE = 0x5C0                 # file offset of fill128_late.bin (fill_tt.asm sits at 0x540, 117 bytes)
MAIN_END = 0x540
FESSOR_HULL = ROOT / "src/elite/missions_hull.asm"
TYPE_CONSTRICTOR = 19
PACKS_ASM = ROOT / "src/elite/missions_ships.asm"      # Fessor's hulls in the CPC layout (used with his permission), the ship packs of docs/_ship_packs.md
PACK_HULLS = ["Gecko", "CobraMk1", "Worm", "Moray", "Mamba", "Adder", "Boa", "Anaconda", "Shuttle"]      # ship types 20..28 (src/elite128/missions_ships.asm has the same order in its type chain)
TYPE_PACK0 = 20
N_TYPES = TYPE_PACK0 + len(PACK_HULLS)
# The title screen's ship viewer (src/elite128/common2x.asm titleSpawn): per ship (name, base ship type, flight image slot, wanted hull type or 0xFF, distance = z high byte).
# Slot 0 = the default image (no pack), 1-7 = ship pack k, 8 = the Constrictor's image. A pack hull is spawned from its base type until the image's mxHullType names the wanted type.
# The first eight are the ships the title screen always had (index 2, the Cobra Mk III, is where the press-space screen starts).
VIEW = [("VIPER", 8, 0, 0xFF, 2), ("ASP MK II", 13, 0, 0xFF, 2), ("COBRA MK III", 9, 0, 0xFF, 3), ("FER-DE-LANCE", 14, 0, 0xFF, 2), ("SIDEWINDER", 16, 0, 0xFF, 2),
        ("KRAIT", 17, 0, 0xFF, 2), ("ROCK HERMIT", 7, 0, 0xFF, 2), ("THARGOID", 15, 0, 0xFF, 5),
        ("CORIOLIS", 0, 0, 0xFF, 7), ("MISSILE", 1, 0, 0xFF, 1), ("ESCAPE POD", 2, 0, 0xFF, 1), ("ALLOY PLATE", 3, 0, 0xFF, 1), ("CARGO CANISTER", 4, 0, 0xFF, 1),
        ("SPLINTER", 5, 0, 0xFF, 1), ("ASTEROID", 6, 0, 0xFF, 3), ("PYTHON", 10, 0, 0xFF, 4), ("PYTHON PIRATE", 11, 0, 0xFF, 4), ("COBRA PIRATE", 12, 0, 0xFF, 2),
        ("THARGON", 18, 0, 0xFF, 1), ("CONSTRICTOR", 19, 8, 0xFF, 2),
        ("GECKO", 16, 1, 20, 2), ("COBRA MK I", 17, 1, 21, 2), ("WORM", 16, 2, 22, 1), ("MORAY", 17, 2, 23, 2), ("MAMBA", 16, 3, 24, 2), ("ADDER", 17, 4, 25, 1),
        ("BOA", 10, 5, 26, 3), ("ANACONDA", 10, 6, 27, 4), ("SHUTTLE", 9, 7, 28, 1)]
VIEW_TABLE, VIEW_NAMES = 0x300, 0x380      # offsets in the pack file (titleViewTable &6B00, titleViewNames &6B80 in bank 6)
PACKS_AT = 0x800             # offset in the fill file (bank 6 &6800) of the pack hulls' records (fill128_packs.bin, staged at STAGE+0x2800, copied by bankInit)
PATTERNS = [p for p in gen.PATTERN_ORDER if p != 0]      # brightest first; pattern 0 is solid pen 1, the colour of the empty view, so a hull face in it would vanish


def stock_image():
    """the stock game's COMMONXX in a 64K image (index = address): assembled from src/elite, so nothing under work/ but the generated files is needed"""
    symbols()
    return bytes(0x1A40) + (OUT / "c.bin").read_bytes()


def symbols():
    sym = OUT / "c.sym"
    src = ROOT / "src/elite/commonxx.asm"
    if not sym.exists() or sym.stat().st_mtime < src.stat().st_mtime:      # regenerate when the stock source changed
        OUT.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), f"--raw={OUT / 'c.bin'}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], check=True, capture_output=True)
    out = {}
    for l in sym.read_text().splitlines():
        p = l.split()
        if p and p[0].lower().startswith("shipdat"):
            out[p[0].rstrip(":")] = int(p[-1], 16)
        if p and p[0].rstrip(":") == "shipGFXdataTable":
            assert int(p[-1], 16) == TABLE, "TABLE is out of date"
    return out


def stock_points(m, a):
    h = m[a:a + 23]
    vo = h[12] | h[13] << 8
    pts = []
    for i in range(h[3]):
        v = m[a + vo + 6 * i:a + vo + 6 * i + 6]
        pts.append((-v[0] if v[3] & 0x80 else v[0], -v[1] if v[3] & 0x40 else v[1], -v[2] if v[3] & 0x20 else v[2]))
    return pts


def apply(p, perm, sg):
    return tuple(sg[i] * p[perm[i]] for i in range(3))


def normalise(pts):
    s = max(max(abs(c) for c in p) for p in pts) or 1
    return [tuple(c / s for c in p) for p in pts]


def chamfer(a, b):
    def one(x, y):
        return sum(min(sum((u - v) ** 2 for u, v in zip(p, q)) ** .5 for q in y) for p in x) / len(x)
    return (one(a, b) + one(b, a)) / 2


def radius(pts):
    return max(sum(c * c for c in p) ** .5 for p in pts) or 1


def extents(pts):
    r = radius(pts)
    return [max(abs(p[i]) for p in pts) / r for i in range(3)]


def nose_sign(pts):
    """+1 when the narrow end (the nose) of the hull is at +z: compare the mean |x| of the vertices on both sides of z = 0."""
    pos = [abs(p[0]) for p in pts if p[2] > 0]
    neg = [abs(p[0]) for p in pts if p[2] < 0]
    if not pos or not neg:
        return 1
    return 1 if sum(pos) / len(pos) <= sum(neg) / len(neg) else -1


def best_axis(stock, arc, label):
    """Axis map for an ArcElite hull: the permutation whose normalised extents (extent / radius) are closest to the stock hull's, z flipped so that the nose
    (narrow end) points to +z like the CPC hulls, y flipped (or not) by the smaller nearest-point distance to the stock vertices (both scaled to the same radius)."""
    if label in AXIS_OVERRIDE:
        return AXIS_OVERRIDE[label], 0.0
    es = extents(stock)
    best = None
    for perm in itertools.permutations(range(3)):
        ea = extents([tuple(p[perm[i]] for i in range(3)) for p in arc])
        cost = sum(abs(x - y) for x, y in zip(es, ea))
        if best is None or cost < best[0] - 1e-9:
            best = (cost, perm)
    perm = best[1]
    pp = [tuple(p[perm[i]] for i in range(3)) for p in arc]
    sz = nose_sign(pp)
    ns = nose_sign(stock)
    if ns != 1:
        report_note.append(f"{label}: stock nose is at {'-' if ns < 0 else '+'}z by the width rule, not +z (rule unreliable for this hull)")
    cands = []
    for sy in (1, -1):
        sg = (1, sy, sz)
        mapped = [tuple(sg[i] * p[i] for i in range(3)) for p in pp]
        k = radius(stock) / radius(mapped)
        cands.append((chamfer(normalise(stock), normalise([tuple(c * k for c in p) for p in mapped])), sg))
    err, sg = min(cands)
    return (perm, sg), err


report_note = []


def triangles(facets, pts):
    """-> list of (v0, v1, v2, colour, group) wound counterclockwise as seen from outside (majority rule of gen.build_ship), groups from the fifth number."""
    g = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    signs = []
    for f in facets:
        a, b, c = (pts[i] for i in f[:3])
        n = gen.cross(gen.sub(b, a), gen.sub(c, a))
        signs.append(1 if gen.dot(n, gen.sub([(a[i] + b[i] + c[i]) / 3 for i in range(3)], g)) > 0 else -1)
    major = 1 if sum(signs) >= 0 else -1
    out, gid, i, n_groups = [], {}, 0, 0
    while i < len(facets):
        for j in range(i, min(len(facets), i + facets[i][4] + 1)):
            gid[j] = n_groups
        i += facets[i][4] + 1
        n_groups += 1
    for j, (f, sg) in enumerate(zip(facets, signs)):
        v0, v1, v2 = f[:3]
        if sg != major:
            v1, v2 = v2, v1                       # against the majority: flip it (concave spots or a stray winding)
        if major < 0:
            v1, v2 = v2, v1                       # whole hull wound the other way: flip all, so that every hull ends up outward counterclockwise
        out.append((v0, v1, v2, f[3], gid[j]))
    return out, n_groups


def fit(stock, pts_a, facets, label):
    """ArcElite hull -> (quantised vertices, triangles, group count, axis map, match error, scale), at the stock hull's radius."""
    assert len(pts_a) <= 28, (label, len(pts_a))
    (perm, sg), err = best_axis(stock, pts_a, label)
    tp = [apply(p, perm, sg) for p in pts_a]
    k = radius(stock) / radius(tp)       # same bounding radius as the stock hull (rotation invariant, so a wrong axis map does not skew the size)
    q = [tuple(int(round(c * k)) for c in p) for p in tp]
    assert all(abs(c) <= 255 for p in q for c in p), label
    tris, ngroups = triangles(facets, tp)
    assert ngroups <= 31 and len(tris) < 256
    return q, tris, ngroups, (perm, sg), err, k


def stock_fit(m, a, label):
    """stock source: the blueprint's own vertices (already the engine's axes: no mapping), triangles with their dither patterns from tools/hullfill.py"""
    b = hullfill.build_stock(m, a, label)
    q, tris = b["verts"], b["tris"]
    assert all(abs(c) <= 255 for p in q for c in p) and len(q) <= 28, (label, len(q))
    ngroups = len({t[4] for t in tris})
    assert ngroups <= 31 and len(tris) < 256, (label, ngroups, len(tris))
    if b["stats"]["convex"]:
        CONVEX.add(label)
    return q, tris, ngroups, ((0, 1, 2), (1, 1, 1)), 0.0, 1.0


def record(label, tris, direct=False):
    """direct: the triangles carry their dither pattern (tools/hullfill.py); otherwise their colour, ranked into the patterns"""
    if direct:
        return bytes([len(tris), 1 if label in CONVEX else 0]) + b"".join(bytes([t[0], t[1], t[2], t[3] << 5 | t[4]]) for t in tris)
    cols = sorted({t[3] for t in tris}, reverse=True)
    pat = {c: PATTERNS[i % len(PATTERNS)] for i, c in enumerate(cols)}
    return bytes([len(tris), 1 if label in CONVEX else 0]) + b"".join(bytes([t[0], t[1], t[2], pat[t[3]] << 5 | t[4]]) for t in tris)


def gun_vertex(q):
    return max(range(len(q)), key=lambda i: (q[i][2], -abs(q[i][0])))    # gun vertex (lookup_vertex_coords): the nose, the vertex furthest along +z


def alloy(m, a):
    """The plate: its 4 stock vertices, two triangles per side (the fill culls by winding, so each side shows its own pair); the sides get different colours."""
    q = stock_points(m, a)
    return q, [(0, 1, 2, 118, 0), (0, 2, 3, 118, 1), (0, 2, 1, 42, 2), (0, 3, 2, 42, 3)], 4


def fessor_constrictor():
    """(header lines, vertices) of Fessor's Constrictor in src/elite/missions_hull.asm."""
    lines = FESSOR_HULL.read_text().splitlines()
    i0 = next(i for i, l in enumerate(lines) if l.startswith("shipdatConstrictor:"))
    i1 = next(i for i, l in enumerate(lines) if l.startswith("constrictorVertices:"))
    i2 = next(i for i, l in enumerate(lines) if l.startswith("constrictorEdges:"))
    pts = []
    for l in lines[i1 + 1:i2]:
        v = [int(x, 16) for x in l.split(";")[0].strip()[3:].split(",")]
        pts.append(tuple((-1 if v[3] & b else 1) * v[i] for i, b in enumerate((0x80, 0x40, 0x20))))
    return lines[i0 + 1:i1], pts


def constrictor():
    """-> (asm text of the blueprint, vertices, triangles, report line). Based on Fessor's Constrictor hull in src/elite/missions_hull.asm (used with his permission):
    his header in both sources; the vertices and triangles from ArcElite's CONSTRICTOR (arcelite) or from his own vertices, edges and faces (stock)."""
    head, stock = fessor_constrictor()
    if SOURCE == "arcelite":
        pts_a, facets = gen.parse("CONSTRICTOR")
        ctr = [min(p[i] for p in pts_a) + max(p[i] for p in pts_a) for i in range(3)]       # this hull is not centred on its origin (x runs -52..17): centre the bounding box (doubled units)
        pts_a = [[2 * p[i] - ctr[i] for i in range(3)] for p in pts_a]
        q, tris, ngroups, (perm, sg), err, k = fit(stock, pts_a, facets, "Constrictor")
        title = "based on Fessor's Constrictor hull: his header with the ArcElite CONSTRICTOR vertices (third party data): do not commit, see NOTICE item 10"
        note = f"{'shipdatConstrictor':24s} CONSTRICTOR axes {perm} signs {sg}  match error {err:.3f}  scale {k:.3f}  {len(q)} vertices {len(tris)} triangles {ngroups} groups  (Fessor's {len(stock)} vertices as reference)"
    else:
        b = hullfill.build(*hullfill.parse_asm_blueprint(FESSOR_HULL, "constrictor"), label="shipdatConstrictor")
        q, tris = b["verts"], b["tris"]
        ngroups = len({t[4] for t in tris})
        assert len(q) <= 28 and ngroups <= 31 and len(tris) < 256, (len(q), ngroups, len(tris))
        if b["stats"]["convex"]:
            CONVEX.add("shipdatConstrictor")
        title = "based on Fessor's Constrictor hull: his header and vertices, the triangles built from his edges and faces (tools/hullfill.py)"
        note = f"{'shipdatConstrictor':24s} CONSTRICTOR (Fessor's own hull) {len(q)} vertices {len(tris)} triangles {ngroups} groups"
    out = []
    for n, l in enumerate(head):
        code = l.split(";")[0].strip()
        if n in (3, 4, 5):                                       # vertex, edge and face counts
            l = f"    db {len(q) if n == 3 else 0}   ; " + ("vertices" if n == 3 else "edges" if n == 4 else "faces") + " (vertices only: the fill needs no edges)"
        elif code.startswith("dw constrictorEdges") or code.startswith("dw constrictorFaces"):
            l = l.replace("constrictorEdges", "constrictorEnd").replace("constrictorFaces", "constrictorEnd")
        out.append(l)
    # header byte 20 is the gun vertex: the line holding "Gun-Vertex"
    out = [f"    db {gun_vertex(q)}   ; Gun-Vertex (the nose)" if "Gun-Vertex" in l else l for l in out]
    lines = [f"; generated by tools/ship128.py: {title}", "shipdatConstrictor:"]
    lines += out + ["constrictorVertices:"]
    lines += ["    db " + ",".join(f"0x{x:02X}" for x in vertex_bytes(p)) for p in q]
    lines += ["constrictorEnd:", ""]
    return "\n".join(lines), q, tris, note


def pack_hulls():
    """-> (asm text, {name: (vertices, triangles)}, report lines). The ship pack hulls of src/elite/missions_ships.asm as vertices-only blueprints (the same header, counts and
    offsets patched) with fill triangles built from their own edges and faces (tools/hullfill.py), one IFDEF HULL_<NAME> block each like the source file."""
    lines = PACKS_ASM.read_text().splitlines()
    out = ["; generated by tools/ship128.py from src/elite/missions_ships.asm (Fessor's hulls, used with his permission): vertices only, the triangles are in fill128_packs.bin.",
           "; Each hull is assembled only when its HULL_<NAME> is defined (the ship packs in missions_flight_k.asm define them)."]
    result, report = {}, []
    for name in PACK_HULLS:
        i0 = next(i for i, l in enumerate(lines) if l.startswith(f"shipdat{name}:"))
        iv = next(i for i, l in enumerate(lines) if l.startswith(f"{name}VerticesStart:"))
        ie = next(i for i, l in enumerate(lines) if l.startswith(f"{name}EdgesStart:"))
        if_ = next(i for i, l in enumerate(lines) if l.startswith(f"{name}FacesStart:"))
        iz = next(i for i, l in enumerate(lines) if l.startswith(f"{name}FacesEnd:"))
        def body(a, b):
            vals = []
            for l in lines[a + 1:b]:
                t = l.split(";")[0].strip()
                if t.lower().startswith("db"):
                    vals += [int(x.split("/")[0], 0) // int(x.split("/")[1], 0) if "/" in x else int(x, 0) for x in t[2:].split(",") if x.strip()]      # edge vertex numbers are written as 0x14/4
            return vals
        v, e, f = body(iv, ie), body(ie, if_), body(if_, iz)
        sg = lambda byte, bit: -1 if byte & bit else 1
        verts = [(sg(v[k + 3], 0x80) * v[k], sg(v[k + 3], 0x40) * v[k + 1], sg(v[k + 3], 0x20) * v[k + 2]) for k in range(0, len(v), 6)]
        edges = [(e[k + 1], e[k + 2], e[k + 3] & 15, e[k + 3] >> 4) for k in range(0, len(e), 4)]
        faces = [(sg(f[k + 3], 0x80) * f[k], sg(f[k + 3], 0x40) * f[k + 1], sg(f[k + 3], 0x20) * f[k + 2]) for k in range(0, len(f), 4)]
        b = hullfill.build(verts, edges, faces, label=f"shipdat{name}")
        q, tris = b["verts"], b["tris"]
        ngroups = len({t[4] for t in tris})
        assert len(q) <= 28 and ngroups <= 31 and len(tris) < 256, (name, len(q), ngroups, len(tris))
        if b["stats"]["convex"]:
            CONVEX.add(f"shipdat{name}")
        head = lines[i0 + 1:iv]
        blk = [f"    IFDEF HULL_{name.upper()}", f"shipdat{name}:"]
        for n, l in enumerate(head):
            if n in (3, 4, 5):
                l = f"    db {len(q) if n == 3 else 0}   ; " + ("vertices" if n == 3 else "edges" if n == 4 else "faces") + " (vertices only: the fill needs no edges)"
            elif l.strip().startswith("dw " + name + "EdgesStart") or l.strip().startswith("dw " + name + "FacesStart"):
                l = f"    dw {name}End-shipdat{name}"
            elif "GunVertex" in l:
                l = f"    db {gun_vertex(q)}   ; GunVertex (the nose)"
            blk.append(l)
        blk.append(f"{name}VerticesStart:")
        blk += ["    db " + ",".join(f"0x{x:02X}" for x in vertex_bytes(p)) for p in q]
        blk += [f"{name}End:", "    ENDIF"]
        out += blk
        result[name] = (q, tris)
        report.append(f"shipdat{name:16s} (Fessor's own hull) {len(q)} vertices {len(tris)} triangles {ngroups} groups")
    return "\n".join(out) + "\n", result, report


def vertex_bytes(p):
    x, y, z = p
    return bytes([abs(x), abs(y), abs(z), (0x80 if x < 0 else 0) | (0x40 if y < 0 else 0) | (0x20 if z < 0 else 0) | 0x1F, 0x00, 0x00])


def main():
    m = stock_image()
    sym = symbols()
    OUT.mkdir(parents=True, exist_ok=True)
    order = sorted((a, n) for n, a in sym.items())
    ends = {n: (order[i + 1][0] if i + 1 < len(order) else None) for i, (a, n) in enumerate(order)}
    report, blobs, fill, pts_by = [], {}, {}, {}
    for a, label in order:
        if label in STUB_OF:
            continue
        if label == "shipdatAlloy":
            q, tris, ngroups = alloy(m, a)
            perm, sg, err, k = (0, 1, 2), (1, 1, 1), 0.0, 1.0
        elif label not in HULL:
            end = ends[label]
            blobs[label] = m[a:end] if end else m[a:a + 23]
            report.append(f"{label:24s} kept (stock bytes)")
            continue
        elif SOURCE == "stock":
            q, tris, ngroups, (perm, sg), err, k = stock_fit(m, a, label)
        else:
            q, tris, ngroups, (perm, sg), err, k = fit(stock_points(m, a), *gen.parse(HULL[label]), label)
        hdr = bytearray(m[a:a + 23])
        hdr[3], hdr[4], hdr[5] = len(q), 0, 0
        hdr[20] = gun_vertex(q)
        vo = 23
        vert = b"".join(vertex_bytes(p) for p in q)
        end_off = vo + len(vert)
        hdr[12:14] = vo.to_bytes(2, "little")
        hdr[14:16] = end_off.to_bytes(2, "little")
        hdr[16:18] = end_off.to_bytes(2, "little")
        blobs[label] = bytes(hdr) + vert
        fill[label] = record(label, tris, direct=SOURCE == "stock" and label != "shipdatAlloy")
        pts_by[label] = q
        report.append(f"{label:24s} {HULL.get(label) or 'ALLOY':10s} axes {perm} signs {sg}  match error {err:.3f}  scale {k:.3f}  {len(q)} vertices {len(tris)} triangles {ngroups} groups  blueprint {len(blobs[label])} bytes (stock {ends[label] - a if ends[label] else '?'})")
    for stub, donor in STUB_OF.items():
        hdr = bytearray(m[sym[stub]:sym[stub] + 23])
        d = blobs[donor]
        hdr[3], hdr[4], hdr[5], hdr[20] = d[3], 0, 0, d[20]
        hdr[12:14] = (23 + 23).to_bytes(2, "little")
        # the donor's header sits right after the stub (23 bytes) and its geometry follows it, so the stub's offsets are relative to the stub: 23 + len(donor)
        hdr[14:16] = (23 + len(d)).to_bytes(2, "little")
        hdr[16:18] = (23 + len(d)).to_bytes(2, "little")
        blobs[stub] = bytes(hdr)
        report.append(f"{stub:24s} stub of {donor}")
    # asm in the stock label order
    lines = ["; generated by tools/ship128.py from ArcElite hulls (third party data): do not commit, see NOTICE item 10" if SOURCE == "arcelite"
             else "; generated by tools/ship128.py from the stock blueprints (HULLS=stock): triangles from tools/hullfill.py"]
    for a, label in order:
        lines.append(f"{label}:")
        b = blobs[label]
        for i in range(0, len(b), 16):
            lines.append("    db " + ",".join(f"0x{x:02X}" for x in b[i:i + 16]))
    (OUT / "shipdata128.asm").write_text("\n".join(lines) + "\n")
    # fill file: ship type = index in the stock table
    types = []
    for i in range(19):
        addr = m[TABLE + 4 * i + 1] | m[TABLE + 4 * i + 2] << 8
        label = next(n for n, a in sym.items() if a == addr)
        types.append(STUB_OF.get(label, label))
    asm, cq, ctris, note = constrictor()
    (OUT / "hull_constrictor.asm").write_text(asm)
    report.append(note)
    fill["shipdatConstrictor"] = record("shipdatConstrictor", ctris, direct=SOURCE == "stock")
    pts_by["shipdatConstrictor"] = cq
    types.append("shipdatConstrictor")
    assert len(types) == TYPE_CONSTRICTOR + 1
    packs_asm, packs, packs_report = pack_hulls()
    (OUT / "hull_packs.asm").write_text(packs_asm)
    report.extend(packs_report)
    for name in PACK_HULLS:
        fill[f"shipdat{name}"] = record(f"shipdat{name}", packs[name][1], direct=True)
        pts_by[f"shipdat{name}"] = packs[name][0]
        types.append(f"shipdat{name}")
    assert len(types) == N_TYPES
    LATE_TYPES = {"shipdatAlloy", "shipdatConstrictor"}      # their records go behind the title cache module
    body, late, offs, placed = b"", b"", [], {}
    base = 1 + 2 * N_TYPES
    packs_bin = b""
    for t in range(N_TYPES):
        lab = types[t]
        if t >= TYPE_PACK0:
            offs.append(PACKS_AT + len(packs_bin))
            packs_bin += fill[lab]
        elif lab in LATE_TYPES:
            offs.append(LATE + len(late))
            late += fill[lab]
        elif lab in fill:
            if lab not in placed:                  # the stub types (single trader, big trader, Rock Hermit) share their donor's record
                placed[lab] = base + len(body)
                body += fill[lab]
            offs.append(placed[lab])
        else:
            offs.append(0)
    assert base + len(body) <= MAIN_END, f"fill records ({base + len(body)} bytes) run into the title cache module at {MAIN_END:#x}"
    import json
    (OUT / "ship128_points.json").write_text(json.dumps({str(t): {"name": types[t], "points": pts_by[types[t]]} for t in range(N_TYPES) if types[t] in pts_by}))
    (OUT / "fill128.bin").write_bytes(bytes([N_TYPES]) + b"".join(o.to_bytes(2, "little") for o in offs) + body)
    (OUT / "fill128_late.bin").write_bytes(late)
    assert len(packs_bin) <= 0x300, f"the pack records ({len(packs_bin)} bytes) run into the title viewer table"
    assert len(VIEW) == 29 and len(packs_bin) <= VIEW_TABLE, (len(VIEW), len(packs_bin))      # TITLE_SHIPS in src/elite128/config.inc
    view = bytearray(0x600)
    view[:len(packs_bin)] = packs_bin
    for i, (name, base, slot, want, z) in enumerate(VIEW):
        assert len(name) <= 15, name
        view[VIEW_TABLE + 4 * i:VIEW_TABLE + 4 * i + 4] = bytes([base, slot, want, z])
        view[VIEW_NAMES + 16 * i:VIEW_NAMES + 16 * i + len(name)] = name.encode()
    (OUT / "fill128_packs.bin").write_bytes(bytes(view))
    report.extend(report_note)
    report.append(f"fill128.bin: {base + len(body)} bytes (limit {MAIN_END}), pack records {len(packs_bin)} bytes, late records {len(late)} bytes at {LATE:#x}; blueprints replaced: {sum(len(b) for b in blobs.values())} bytes (stock region {sum((ends[n] or a + 23) - a for a, n in order)})")
    (OUT / "ship128_report.txt").write_text("\n".join(report) + "\n")
    (OUT / "hulls_source.txt").write_text(SOURCE + "\n")      # which source the generated files in this folder come from (tools/build_dsk128.py prints it)
    print("\n".join(report))


if __name__ == "__main__":
    main()

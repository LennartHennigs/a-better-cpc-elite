#!/usr/bin/env python3
"""Turn the prototype's ArcElite hulls into CPC engine blueprints plus fill data for the 128K build (plan: Phase 1, step 5).

usage: python3 -I tools/ship128.py [--report]

Inputs (all under work/, third party data never enters the repo):
  work/stock_mem_image.bin       the stock game in a 64K image (blueprints and the ship table `shipGFXdataTable` at &1B78)
  work/elite128/c.sym            symbol file of src/elite/commonxx.asm (made here with sjasmplus if missing)
  work/arcelite/x_ships/B5052480.C   ArcElite's tables, read through tools/proto_fill/gen.py (`parse`)
Outputs in work/elite128/:
  shipdata128.asm   one blueprint per stock ship label, same label names and order as the stock data: the 23-byte header is the stock header
                    (energy, laser, bounty, scale, ... stay classic) with the counts and offsets patched; the geometry is the ArcElite hull as
                    vertices only (6 bytes each: |x|, |y|, |z|, signs<<5 | 0x1F, face nibbles 0x00 = always visible); edges and faces are empty
                    (the filled path culls by screen winding, see docs/_filled_ships.md). Ships without an ArcElite hull (the alloy plate) keep
                    their stock bytes and no fill record.
  fill128.bin       bank 6 payload: byte 20 (ship types), 20 words (offset of the type's record from the start of the file, 0 = none), then records
                    ntri, flags (bit 0: convex), ntri x (v0, v1, v2, pattern<<5 | group)
  ship128_points.json  the quantised vertices per ship type (for tests)
  ship128_report.txt  per hull: chosen axis map, quantisation error, vertex/triangle/group counts

The axis map (permutation and signs, 48 candidates) is chosen per hull by a scale-free nearest-point match between the stock vertices and the ArcElite
vertices; ArcElite and the CPC do not agree on the nose direction. The match is only a guess: look at every hull in the engine before relying on it,
and override a wrong pick in AXIS_OVERRIDE.
"""
import importlib.util
import itertools
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work/elite128"
spec = importlib.util.spec_from_file_location("gen", ROOT / "tools/proto_fill/gen.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

# stock blueprint label -> ArcElite hull (None: keep the stock geometry). Stubs (RockHermit, SingleTrader, BigTrader) share the geometry of the blueprint
# that follows them and are patched from it.
HULL = {"shipdatCoriolis": "CORIOLIS", "shipdatMissile": "MISSILE", "shipdatCapsule": "ESCAPEPOD", "shipdatAlloy": None, "shipdatCargo": "CANNISTER",
        "shipdatSplinter": "FRAGMENT", "shipdatAsteroid": "ASTEROID", "shipdatViper": "VIPER", "shipdatPythonPirate": "PYTHON",
        "shipdatCobraMk3Pirate": "COBRA", "shipdatAspMk2": "ASP", "shipdatFerDeLance": "FERDELANCE", "shipdatThargoid": "THARGOID",
        "SHIPDATPIRATE1": "SIDEWINDER", "SHIPDATPIRATE2": "KRAIT", "shipdatThargon": "THARGON"}
STUB_OF = {"shipdatRockHermit": "shipdatAsteroid", "SHIPDATSINGLETRADER": "shipdatCobraMk3Pirate", "SHIPDATBIGTRADER": "shipdatPythonPirate"}
AXIS_OVERRIDE = {}      # label -> (perm, signs), e.g. "shipdatViper": ((0, 1, 2), (1, 1, -1)); applied to the ArcElite point (x, y, z)
CONVEX = {"shipdatCoriolis", "shipdatMissile", "shipdatCapsule", "shipdatCargo", "shipdatSplinter", "shipdatViper", "SHIPDATPIRATE1", "shipdatThargon"}  # unchecked guess; the tool does not test convexity yet
TABLE = 0x1B78
PATTERNS = [p for p in gen.PATTERN_ORDER if p != 0]      # brightest first; pattern 0 is solid pen 1, the colour of the empty view, so a hull face in it would vanish


def stock_image():
    return (ROOT / "work/stock_mem_image.bin").read_bytes()


def symbols():
    sym = OUT / "c.sym"
    if not sym.exists():
        OUT.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), f"--raw={OUT / 'c.bin'}", f"--sym={sym}", str(ROOT / "src/elite/commonxx.asm")], check=True, capture_output=True)
    out = {}
    for l in sym.read_text().splitlines():
        p = l.split()
        if p and p[0].lower().startswith("shipdat"):
            out[p[0].rstrip(":")] = int(p[-1], 16)
    return out


def stock_points(m, a):
    h = m[a:a + 23]
    vo = h[12] | h[13] << 8
    pts = []
    for i in range(h[3]):
        v = m[a + vo + 6 * i:a + vo + 6 * i + 6]
        pts.append((-v[0] if v[3] & 0x80 else v[0], -v[1] if v[3] & 0x40 else v[1], -v[2] if v[3] & 0x20 else v[2]))
    return pts


def transforms():
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product((1, -1), repeat=3):
            yield perm, sg


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
        if label not in HULL or HULL[label] is None:
            end = ends[label]
            blobs[label] = m[a:end] if end else m[a:a + 23]
            report.append(f"{label:24s} kept (stock bytes)")
            continue
        pts_a, facets = gen.parse(HULL[label])
        assert len(pts_a) <= 28, (label, len(pts_a))
        stock = stock_points(m, a)
        (perm, sg), err = best_axis(stock, pts_a, label)
        tp = [apply(p, perm, sg) for p in pts_a]
        k = radius(stock) / radius(tp)       # same bounding radius as the stock hull (rotation invariant, so a wrong axis map does not skew the size)
        q = [tuple(int(round(c * k)) for c in p) for p in tp]
        assert all(abs(c) <= 255 for p in q for c in p), label
        tris, ngroups = triangles(facets, tp)
        assert ngroups <= 31 and len(tris) < 256
        cols = sorted({t[3] for t in tris}, reverse=True)
        pat = {c: PATTERNS[i % len(PATTERNS)] for i, c in enumerate(cols)}
        hdr = bytearray(m[a:a + 23])
        hdr[3], hdr[4], hdr[5] = len(q), 0, 0
        vo = 23
        vert = b"".join(vertex_bytes(p) for p in q)
        end_off = vo + len(vert)
        hdr[12:14] = vo.to_bytes(2, "little")
        hdr[14:16] = end_off.to_bytes(2, "little")
        hdr[16:18] = end_off.to_bytes(2, "little")
        blobs[label] = bytes(hdr) + vert
        rec = bytes([len(tris), 1 if label in CONVEX else 0]) + b"".join(bytes([t[0], t[1], t[2], pat[t[3]] << 5 | t[4]]) for t in tris)
        fill[label] = rec
        pts_by[label] = q
        report.append(f"{label:24s} {HULL[label]:10s} axes {perm} signs {sg}  match error {err:.3f}  scale {k:.3f}  {len(q)} vertices {len(tris)} triangles {ngroups} groups  blueprint {len(blobs[label])} bytes (stock {ends[label] - a if ends[label] else '?'})")
    for stub, donor in STUB_OF.items():
        hdr = bytearray(m[sym[stub]:sym[stub] + 23])
        d = blobs[donor]
        hdr[3], hdr[4], hdr[5] = d[3], 0, 0
        hdr[12:14] = (23 + 23).to_bytes(2, "little")
        # the donor's header sits right after the stub (23 bytes) and its geometry follows it, so the stub's offsets are relative to the stub: 23 + len(donor)
        hdr[14:16] = (23 + len(d)).to_bytes(2, "little")
        hdr[16:18] = (23 + len(d)).to_bytes(2, "little")
        blobs[stub] = bytes(hdr)
        report.append(f"{stub:24s} stub of {donor}")
    # asm in the stock label order
    lines = ["; generated by tools/ship128.py from ArcElite hulls (third party data): do not commit"]
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
    body, offs = b"", []
    base = 1 + 2 * 20
    for t in range(20):
        lab = types[t] if t < 19 else None
        if lab in fill:
            offs.append(base + len(body))
            body += fill[lab]
        else:
            offs.append(0)
    import json
    (OUT / "ship128_points.json").write_text(json.dumps({str(t): {"name": types[t], "points": pts_by[types[t]]} for t in range(19) if types[t] in pts_by}))
    (OUT / "fill128.bin").write_bytes(bytes([20]) + b"".join(o.to_bytes(2, "little") for o in offs) + body)
    report.extend(report_note)
    report.append(f"fill128.bin: {1 + 40 + len(body)} bytes; blueprints replaced: {sum(len(b) for b in blobs.values())} bytes (stock region {sum((ends[n] or a + 23) - a for a, n in order)})")
    (OUT / "ship128_report.txt").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()

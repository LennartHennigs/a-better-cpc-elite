#!/usr/bin/env python3
"""Generate the data for the filled-ship prototypes (tools/proto_fill/fill.asm, flip.asm) from ArcElite's ship tables.

usage: python3 -I tools/proto_fill/gen.py [SHIP] [FRAMES]        (default COBRA, 24)       one ship, for fill.asm and the flip build's first version
       python3 -I tools/proto_fill/gen.py --ships                                       the CPC's ships, 16 frames each, in two bank files (flip.asm)
Reads work/arcelite/x_ships/B5052480.C (Ian Bell's table, third party, stays in work/) and writes into work/proto_fill/:
  facets.inc   db lines, 4 bytes per triangle: v0, v1, v2, pattern index
  frames.bin   per frame 104 bytes: x[32], y[32], draw order (face indices, far to near, 0xFF end), bounding box xmin xmax ymin ymax at +100
  rowtab.bin, rowtab_flip.bin   two 256-byte pages (low bytes, high bytes): screen address of each viewport line (base &C000 / &4000)
  winding.inc, tables.bin
  with --ships:  ships4.bin, ships5.bin (SHIPS4.BIN / SHIPS5.BIN on the disk: 8 ships per bank, 1824 bytes each = 160 bytes of triangles + 16 frames)
                 and names.inc
The ship turns about its y axis with a fixed tilt; the engine of the real game would deliver the projected vertices and the visible faces instead.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "work/arcelite/x_ships/B5052480.C"
OUT = ROOT / "work/proto_fill"
FIRST_LINE, LEFT_BYTE = 40, 8          # viewport placement on the 80-byte screen: lines 40..167, bytes 8..71
PATTERN_ORDER = [2, 3, 4, 1, 5, 0]     # brightest first (see PATS in fill.asm)
# the ships the CPC game has (docs/_architecture.md: 14 blueprints plus the splinter), in the order of the selection: (ArcElite name, shown name)
CPC_SHIPS = [("COBRA", "COBRA MK III"), ("VIPER", "VIPER"), ("SIDEWINDER", "SIDEWINDER"), ("PYTHON", "PYTHON"), ("ASP", "ASP MK II"),
             ("FERDELANCE", "FER-DE-LANCE"), ("KRAIT", "KRAIT"), ("THARGOID", "THARGOID"), ("THARGON", "THARGON"), ("CORIOLIS", "CORIOLIS STATION"),
             ("ESCAPEPOD", "ESCAPE POD"), ("CANNISTER", "CARGO CANISTER"), ("MISSILE", "MISSILE"), ("ASTEROID", "ASTEROID"), ("FRAGMENT", "SPLINTER")]


def parse(ship):
    s = re.sub(r"/\*.*?\*/", "", SRC.read_text(encoding="latin-1"), flags=re.S)
    objs = {}
    for m in re.finditer(r"static int (\w+?)(points|facets)\[\]\[\]\s*=\s*(\{.*?DATUM\s*\}\s*\})\s*;", s, flags=re.S):
        name, kind, body = m.groups()
        rows = [r for r in re.findall(r"\{\s*(-?\w+(?:\s*,\s*-?\w+)*)\s*\}", body[1:]) if "DATUM" not in r]
        objs.setdefault(name, {})[kind] = [[int(x) for x in r.split(",")] for r in rows]
    return objs[ship]["points"], objs[ship]["facets"]


def sub(a, b): return [a[i] - b[i] for i in range(3)]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def dot(a, b): return sum(x * y for x, y in zip(a, b))


def build_ship(ship, nframes):
    """-> (facet bytes: v0 v1 v2 pattern per triangle, frames bytes, screen winding of the visible triangles: True = clockwise)"""
    pts, facets = parse(ship)
    assert len(pts) <= 32 and len(facets) <= 40, (ship, len(pts), len(facets))
    cols = sorted({f[3] for f in facets}, reverse=True)
    pat = {c: PATTERN_ORDER[i % len(PATTERN_ORDER)] for i, c in enumerate(cols)}
    g = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    # winding: outward normal = cross(v1-v0, v2-v0) or its negative, whichever points away from the centre for most faces; ships wound the other
    # way get v1 and v2 swapped, so that every ship has the same winding on the screen and one pair of edge tables fits all
    signs = []
    for f in facets:
        a_, b_, c_ = (pts[i] for i in f[:3])
        n = cross(sub(b_, a_), sub(c_, a_))
        signs.append(1 if dot(n, sub([(a_[i] + b_[i] + c_[i]) / 3 for i in range(3)], g)) > 0 else -1)
    major = 1 if sum(signs) >= 0 else -1
    # facets wound against the majority (or concave spots where the centre test is wrong) are flipped one by one; the rest is wound the other way
    # round for some ships, then everything is swapped, so that every ship ends up with the same winding on the screen
    facets = [[f[0], f[2], f[1]] + f[3:] if (sg != major) != (major > 0) else f for f, sg in zip(facets, signs)]
    flipped = sum(1 for sg in signs if sg != major)
    wind = -1
    group_of, g0, i = {}, 0, 0
    while i < len(facets):                      # facets that share a plane: the fifth number counts the group members that follow (8,7,...,0)
        n = facets[i][4]
        for j in range(i, min(len(facets), i + n + 1)):
            group_of[j] = g0
        i += n + 1
        g0 += 1
    radius = max(math.dist(p, g) for p in pts)
    scale = 62 / radius
    dist = radius * 3.2
    frames = bytearray()
    orders, shots = [], []
    for k in range(nframes):
        ang = 2 * math.pi * k / nframes
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
            if dot(n, [-cen[0], -cen[1], -dist - cen[2]]) > 0:       # camera at (0, 0, -dist), looking along +z
                depth[i] = -(a[2] + b[2] + c[2]) / 3                   # far (large z) first
        gdepth = {}
        for i in depth:
            gdepth.setdefault(group_of[i], []).append(depth[i])
        vis = sorted((sum(gdepth[group_of[i]]) / len(gdepth[group_of[i]]), group_of[i], i) for i in depth)   # groups far to near, a group in list order
        order = []
        for _, _, i in vis:                                    # keep the sign of each visible triangle's screen winding; edge-on slivers are dropped below
            f = facets[i]
            cr = (xs[f[1]] - xs[f[0]]) * (ys[f[2]] - ys[f[0]]) - (xs[f[2]] - xs[f[0]]) * (ys[f[1]] - ys[f[0]])
            order.append((i, cr))
        orders.append(order)
        shots.append((xs, ys))
    # the winding that most visible triangles have on the screen is the one the edge tables are built for; the few that rounding turned the
    # other way (thin slivers seen almost edge-on) and the zero-area ones are dropped
    pos = sum(1 for o in orders for _, cr in o if cr > 0)
    neg = sum(1 for o in orders for _, cr in o if cr < 0)
    clockwise = pos >= neg
    dropped = min(pos, neg)
    total = pos + neg
    assert dropped * 10 <= total, f"{ship}: {dropped} of {total} visible triangles wound the other way on the screen"
    for (xs, ys), o in zip(shots, orders):
        order = [i for i, cr in o if cr != 0 and (cr > 0) == clockwise]
        assert len(order) <= 35
        used = {v for i in order for v in facets[i][:3]}
        bx = [xs[v] for v in used] or [0]
        by = [ys[v] for v in used] or [0]
        box = bytes([max(0, min(bx) - 1), min(255, max(bx) + 1), max(0, min(by) - 1), min(127, max(by) + 1)])   # what the next frame has to erase
        frames += bytes(xs + [0] * (32 - len(xs))) + bytes(ys + [0] * (32 - len(ys))) + bytes(order + [0xFF] * (36 - len(order))) + box
    fac = b"".join(bytes([f[0], f[1], f[2], pat[f[3]]]) for f in facets)
    return fac, bytes(frames), clockwise, len(pts), len(facets), flipped


def write_common(clockwise):
    # visible triangles all turn the same way on the screen; downward edges then all lie on one side
    (OUT / "winding.inc").write_text("DOWNPAGE equ %s\nUPPAGE equ %s\n" % (("XRP", "XLP") if clockwise else ("XLP", "XRP")))
    colt = bytes(x >> 2 for x in range(256))
    lm = bytes([0xFF, 0x77, 0x33, 0x11][x & 3] for x in range(256))
    rm = bytes([0x88, 0xCC, 0xEE, 0xFF][x & 3] for x in range(256))
    (OUT / "tables.bin").write_bytes(colt + lm + rm)
    for name, base in ("rowtab.bin", 0xC000), ("rowtab_flip.bin", 0x4000):      # the page flip build always draws at &4000
        lo, hi = bytearray(), bytearray()
        for y in range(128):
            line = FIRST_LINE + y
            addr = base + (line & 7) * 0x800 + (line >> 3) * 80 + LEFT_BYTE
            lo.append(addr & 255)
            hi.append(addr >> 8)
        (OUT / name).write_bytes(bytes(lo).ljust(256, b"\0") + bytes(hi).ljust(256, b"\0"))   # low bytes at &9500, high bytes at &9600


def main_one():
    ship = sys.argv[1].upper() if len(sys.argv) > 1 else "COBRA"
    nframes = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    OUT.mkdir(parents=True, exist_ok=True)
    fac, frames, clockwise, npts, ntri, _ = build_ship(ship, nframes)
    with open(OUT / "facets.inc", "w") as fh:
        fh.write(f"; {ship}: {npts} points, {ntri} triangles (v0, v1, v2, pattern)\n")
        for i in range(0, len(fac), 4):
            fh.write("    db %d,%d,%d,%d\n" % tuple(fac[i:i + 4]))
    (OUT / "frames.bin").write_bytes(frames)
    write_common(clockwise)
    print(f"{ship}: {npts} points, {ntri} triangles, {nframes} frames, {len(frames)} bytes of frames")


def main_ships():
    OUT.mkdir(parents=True, exist_ok=True)
    blocks, clock = [], set()
    names = []
    for arc, shown in CPC_SHIPS:
        fac, frames, clockwise, npts, ntri, flipped = build_ship(arc, 16)
        clock.add(clockwise)
        blocks.append(fac.ljust(160, b"\0") + frames)
        names.append(shown)
        print(f"{shown:18s} {npts:2d} points {ntri:2d} triangles" + (f", {flipped} wound against the rest and flipped" if flipped else ""))
    assert len(clock) == 1, "ships with different screen winding"
    write_common(clock.pop())
    assert all(len(b) == 160 + 16 * 104 for b in blocks)
    banks = [blocks[0:8], blocks[8:16]]
    for n, bl in enumerate(banks):
        (OUT / f"ships{4 + n}.bin").write_bytes(b"".join(bl))
    with open(OUT / "names.inc", "w") as fh:
        fh.write(f"NSHIPS equ {len(names)}\nnameTable:\n")
        for nm in names:
            fh.write('    db "%s"' % nm + ",0" + "\n    ds %d\n" % (17 - len(nm) - 1))     # 17 bytes per name, zero terminated
    print(len(blocks), "ships,", sum(len(b) for b in blocks), "bytes in", len(banks), "banks")


if __name__ == "__main__":
    if "--ships" in sys.argv:
        main_ships()
    else:
        main_one()

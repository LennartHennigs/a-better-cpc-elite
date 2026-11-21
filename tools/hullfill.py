#!/usr/bin/env python3
"""Filled ships for the 128K build from the CPC's own blueprints: triangles, dither patterns and a few hand-made details, no third-party data.

usage: python3 -I tools/hullfill.py [--report]        (the report lists every stock hull: outlines, triangles, brightness spread)
Used by tools/ship128.py when the hulls come from the stock blueprints (HULLS=stock, the default). The stock blueprints are read from the image of
src/elite/commonxx.asm; the Constrictor, which is based on Fessor's hull, from src/elite/missions_hull.asm.

How a hull becomes triangles (all of it from the blueprint's vertices, edges and face normals):
  - a face's outline is the loop of the edges that name that face (an edge names its two faces in its last byte); dangling edges (the Krait's wing-tip lines) are
    dropped, and a face whose edges do not form one clean loop gets the convex hull of its vertices; a loop is cut into triangles (ear clipping) wound
    counterclockwise seen from outside (cross product against the stock face normal);
  - further loops of the same face that lie inside its outline (the wireframe's exhaust ports and cockpit lines) become detail triangles in the accent
    colour, listed after the face so they are drawn on top (same group);
  - the dither pattern of a face comes from its brightness (a key light from the upper front left and a weak fill from below behind, baked into the hull's own axes);
    a hull whose faces differ very little (the Thargoid's rim facets) is stretched to use the whole ramp;
  - design(): a few details of our own: the Cobra's windscreen, the Sidewinder's canopy and wing trim, the Viper's canopy (extra vertices: the resident blueprint
    area is a fixed 1,781-byte slot, see HULL_REGION_SIZE in src/elite128/commonxx.asm: every new vertex costs 6 bytes of it).
Blueprint layout: header +3 vertices, +4 edges, +5 faces, +12/+14/+16 offsets of the three lists.
  vertex 6 bytes: |x| |y| |z|, signs (0x80 x, 0x40 y, 0x20 z) + visibility, face nibbles
  edge 4 bytes: visibility, v1, v2, faces (low nibble face 1, high nibble face 2)
  face 4 bytes: |nx| |ny| |nz|, signs (0x80 nx, 0x40 ny, 0x20 nz) + visibility   (the same shape as a vertex)
"""
import math

LIGHT = (-0.3, 0.75, 0.55)    # key light (y up, nose +z): top and front faces are lit
FILL = (0.5, -0.35, -0.3)      # weak fill from below and behind, so the underside differs from the shadow side
W_KEY, W_FILL = 0.75, 0.25
# Dither patterns of fill.asm (PATS): 0 solid pen 2 (the empty view: invisible), 1 solid pen 1 (accent colour), 2 solid pen 3 (the hull colour),
# 3 pen 2/pen 3 checker (hull colour dimmed), 4 pen 1/pen 3 checker (hull colour with the accent), 5 pen 1/pen 2 checker (accent dimmed)
BG, ACC, MAIN, DIM, MIX, ACCDIM = 0, 1, 2, 3, 4, 5
RAMP = [DIM, MIX, MAIN]        # face brightness, dark to bright: dim hull colour, hull colour with the accent, solid hull colour (tuned by eye, in the engine)
BINS = None                    # None = equal bins over -1..1


def parse_blueprint(m, a):
    """(vertices, edges, faces) of the blueprint at address a of the image m (bytes indexed by address); edges are (v1, v2, face1, face2)"""
    h = m[a:a + 23]
    nv, ne, nf = h[3], h[4], h[5]
    vo, eo, fo = (h[12] | h[13] << 8), (h[14] | h[15] << 8), (h[16] | h[17] << 8)
    verts, edges, faces = [], [], []
    for i in range(nv):
        v = m[a + vo + 6 * i:a + vo + 6 * i + 6]
        verts.append((-v[0] if v[3] & 0x80 else v[0], -v[1] if v[3] & 0x40 else v[1], -v[2] if v[3] & 0x20 else v[2]))
    for i in range(ne):
        e = m[a + eo + 4 * i:a + eo + 4 * i + 4]
        edges.append((e[1], e[2], e[3] & 15, e[3] >> 4))
    for i in range(nf):
        f = m[a + fo + 4 * i:a + fo + 4 * i + 4]
        faces.append(((-f[0] if f[3] & 0x80 else f[0]), (-f[1] if f[3] & 0x40 else f[1]), (-f[2] if f[3] & 0x20 else f[2])))
    return verts, edges, faces


def parse_asm_blueprint(path, name):
    """(vertices, edges, faces) of a blueprint written as `<name>Vertices:` / `<name>Edges:` / `<name>Faces:` lists of `db` lines (src/elite/missions_hull.asm)"""
    lines = [l.split(";")[0].strip() for l in open(path, encoding="latin1").read().splitlines()]
    sections, cur = {}, None
    for l in lines:
        for key in ("Vertices", "Edges", "Faces"):
            if l == f"{name}{key}:":
                cur = key
                sections[cur] = []
        if cur and l.lower().startswith("db"):
            sections[cur] += [int(x, 0) for x in l[2:].split(",") if x.strip()]
    v, e, f = sections["Vertices"], sections["Edges"], sections["Faces"]
    sg = lambda b, bit: -1 if b & bit else 1
    verts = [(sg(v[i + 3], 0x80) * v[i], sg(v[i + 3], 0x40) * v[i + 1], sg(v[i + 3], 0x20) * v[i + 2]) for i in range(0, len(v), 6)]
    edges = [(e[i + 1], e[i + 2], e[i + 3] & 15, e[i + 3] >> 4) for i in range(0, len(e), 4)]
    faces = [(sg(f[i + 3], 0x80) * f[i], sg(f[i + 3], 0x40) * f[i + 1], sg(f[i + 3], 0x20) * f[i + 2]) for i in range(0, len(f), 4)]
    return verts, edges, faces


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a):
    n = math.sqrt(dot(a, a)) or 1
    return (a[0] / n, a[1] / n, a[2] / n)


def loops(edge_pairs):
    """chain undirected edges into vertex loops; -> (closed loops, open chains, branching vertices)"""
    adj = {}
    for a, b in edge_pairs:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    branch = [v for v, n in adj.items() if len(n) > 2]
    seen_e, closed, opened = set(), [], []
    def walk(start, first):
        path, prev, cur = [start], None, start
        nxt = first
        while True:
            key = frozenset((cur, nxt)) if cur != nxt else None
            if key in seen_e:
                return path, False
            seen_e.add(key)
            prev, cur = cur, nxt
            if cur == start:
                return path, True
            path.append(cur)
            cand = [x for x in adj[cur] if x != prev and frozenset((cur, x)) not in seen_e]
            if not cand:
                return path, False
            nxt = cand[0]
    # open chains first (start at degree-1 vertices), then closed loops
    for v in [v for v, n in adj.items() if len(n) == 1]:
        if any(frozenset((v, x)) in seen_e for x in adj[v]):
            continue
        p, ok = walk(v, adj[v][0])
        opened.append(p)
    for v in list(adj):
        for x in adj[v]:
            if frozenset((v, x)) not in seen_e:
                p, ok = walk(v, x)
                (closed if ok else opened).append(p)
    return closed, opened, branch


def plane_axes(n):
    """drop the axis of the largest normal component: the 2D projection used for convexity and ear clipping"""
    i = max(range(3), key=lambda k: abs(n[k]))
    return [k for k in range(3) if k != i]


def area2(p2):
    return sum(p2[i][0] * p2[(i + 1) % len(p2)][1] - p2[(i + 1) % len(p2)][0] * p2[i][1] for i in range(len(p2)))


def triangulate(poly, verts, n):
    """ear clipping of a planar polygon (list of vertex indices) -> triangles wound counterclockwise seen from outside (cross . n > 0)"""
    ax = plane_axes(n)
    p2 = {v: (verts[v][ax[0]], verts[v][ax[1]]) for v in poly}
    idx = list(poly)
    if area2([p2[v] for v in idx]) < 0:
        idx.reverse()                                           # counterclockwise in the projection
    tris, guard = [], 0
    def cross2(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    while len(idx) > 3 and guard < 200:
        guard += 1
        for i in range(len(idx)):
            a, b, c = idx[i - 1], idx[i], idx[(i + 1) % len(idx)]
            if cross2(p2[a], p2[b], p2[c]) <= 0:
                continue
            if any(cross2(p2[a], p2[b], p2[v]) >= 0 and cross2(p2[b], p2[c], p2[v]) >= 0 and cross2(p2[c], p2[a], p2[v]) >= 0 for v in idx if v not in (a, b, c)):
                continue
            tris.append((a, b, c))
            idx.pop(i)
            break
        else:
            break
    if len(idx) == 3:
        tris.append(tuple(idx))
    out = []
    for a, b, c in tris:                                        # orient by the stock normal (outward), whatever the projection did
        if dot(cross(sub(verts[b], verts[a]), sub(verts[c], verts[a])), n) < 0:
            b, c = c, b
        out.append((a, b, c))
    return out


def components(pairs):
    """connected components of an undirected edge list -> list of (vertex set, edge list)"""
    par = {}
    def find(x):
        while par.setdefault(x, x) != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b in pairs:
        par[find(a)] = find(b)
    comps = {}
    for a, b in pairs:
        comps.setdefault(find(a), []).append((a, b))
    return [({x for e in es for x in e}, es) for es in comps.values()]


def prune(es):
    """remove dangling edges (a vertex used once: wing-tip spikes, detail lines) until only cycles and branches are left"""
    es = list(es)
    while True:
        deg = {}
        for a, b in es:
            deg[a] = deg.get(a, 0) + 1
            deg[b] = deg.get(b, 0) + 1
        leaves = {v for v, d in deg.items() if d == 1}
        if not leaves:
            return es
        es = [(a, b) for a, b in es if a not in leaves and b not in leaves]


def hull_outline(vs, verts, n):
    """convex hull (counterclockwise in the plane projection) of the vertices: the outline when the edges do not form one clean loop"""
    ax = plane_axes(n)
    pts = sorted(vs, key=lambda v: (verts[v][ax[0]], verts[v][ax[1]]))
    def c2(o, a, b): return (verts[a][ax[0]] - verts[o][ax[0]]) * (verts[b][ax[1]] - verts[o][ax[1]]) - (verts[a][ax[1]] - verts[o][ax[1]]) * (verts[b][ax[0]] - verts[o][ax[0]])
    lo, up = [], []
    for v in pts:
        while len(lo) >= 2 and c2(lo[-2], lo[-1], v) <= 0:
            lo.pop()
        lo.append(v)
    for v in reversed(pts):
        while len(up) >= 2 and c2(up[-2], up[-1], v) <= 0:
            up.pop()
        up.append(v)
    return lo[:-1] + up[:-1]


def poly2(poly, verts, n):
    ax = plane_axes(n)
    return [(verts[v][ax[0]], verts[v][ax[1]]) for v in poly]


def inside(pt, p2):
    x, y = pt
    c = False
    for i in range(len(p2)):
        (x1, y1), (x2, y2) = p2[i], p2[(i + 1) % len(p2)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def brightness(n):
    nn = norm(n)
    return W_KEY * dot(nn, norm(LIGHT)) + W_FILL * dot(nn, norm(FILL))


# Saucer hulls (the Thargoid and the Thargon): the ring of rim facets is lit from the front instead, so the facets that face the viewer in a front view are bright and
# the slanted ones next to them dark: a bright trapezoid, as on ArcElite's Thargoid. FRONT_BINS: below the first value dim, below the second mixed, above solid.
FRONT_LIT = {"shipdatThargoid", "shipdatThargon"}
FRONT_BINS = (0.3, 0.35)
SHIMMER = True                 # the second triangle of each bright rim facet gets the mixed pattern, so the trapezoid is not one flat slab


def pattern_of(n, label=None):
    if label in FRONT_LIT:
        b = dot(norm(n), (0, 0, 1))
        return DIM if b < FRONT_BINS[0] else (MIX if b < FRONT_BINS[1] else MAIN)
    b = brightness(n)
    if BINS:
        k = sum(1 for x in BINS if b >= x)
    else:
        k = int((b * 0.5 + 0.5) * len(RAMP))
    return RAMP[max(0, min(len(RAMP) - 1, k))]


def build_struct(verts, edges, faces, label=None):
    """-> dict: tris [(v0, v1, v2, tone, group)] (a face's base triangles first, its decals after: same group, drawn on top), stats"""
    st = {"faces": len(faces), "exact": 0, "hull": 0, "decals": 0, "skipped": 0, "nonplanar": 0, "unsupported": 0}
    tris = []
    for f, n in enumerate(faces):
        pairs = [(e[0], e[1]) for e in edges if f in (e[2], e[3])]
        polys = []
        for vs, es in components(pairs):
            es2 = prune(es)
            for vs2, es3 in components(es2):
                if len(vs2) < 3:
                    continue
                closed, opened, branch = loops(es3)
                if len(closed) == 1 and not opened and not branch and len(closed[0]) == len(vs2):
                    poly = closed[0]
                    st["exact"] += 1
                else:
                    poly = hull_outline(vs2, verts, n)
                    st["hull"] += 1
                if len(poly) >= 3:
                    polys.append(poly)
        if not polys:
            st["skipped"] += 1
            continue
        ax = plane_axes(n)
        areas = [abs(area2(poly2(p, verts, n))) for p in polys]
        bi = max(range(len(polys)), key=lambda k: areas[k])
        base2 = poly2(polys[bi], verts, n)
        tone = pattern_of(n, label)
        dtone = ACC
        order = [(bi, tone)]
        for k, p in enumerate(polys):
            if k == bi:
                continue
            p2 = poly2(p, verts, n)
            cx = (sum(x for x, y in p2) / len(p2), sum(y for x, y in p2) / len(p2))
            if inside(cx, base2):
                order.append((k, dtone))                 # a detail polygon inside the face: drawn after it, in a contrasting tone
                st["decals"] += 1
            else:
                order.insert(1, (k, tone))               # a second piece of the same face (left and right engine, ...)
        nn = norm(n)
        for k, tn in order:
            poly = polys[k]
            cen = [sum(verts[v][i] for v in poly) / len(poly) for i in range(3)]
            if max(abs(dot(sub(verts[v], cen), nn)) for v in poly) > 2.5:
                st["nonplanar"] += 1
            if k == bi and max(dot(nn, sub(v, verts[poly[0]])) for v in verts) > 1.5:
                st["unsupported"] += 1
            for t in triangulate(poly, verts, n):
                tris.append((t[0], t[1], t[2], tn, f))
    st["convex"] = st["unsupported"] == 0
    return {"verts": verts, "faces": faces, "edges": edges, "tris": tris, "stats": st}



# ---- hand-made details of our own (extra triangles drawn after the faces, recoloured ones) --------------------------------------------------------------

def inset(verts, tri, toward=None, scale=0.45, shift=0.0):
    """a smaller copy of a triangle of vertices, optionally slid toward a point; appended as new vertices (rounded to integers) -> their indices"""
    P = [verts[i] for i in tri]
    c0 = [sum(p[k] for p in P) / 3 for k in range(3)]
    c1 = c0 if toward is None else [c0[k] + shift * (toward[k] - c0[k]) for k in range(3)]
    out = []
    for p in P:
        verts.append(tuple(int(round(c1[k] + scale * (p[k] - c0[k]))) for k in range(3)))
        out.append(len(verts) - 1)
    return out


def add_tri(verts, tris, tri, n, pat, group):
    a, b, c = tri
    if dot(cross(sub(verts[b], verts[a]), sub(verts[c], verts[a])), n) < 0:
        b, c = c, b
    tris.append((a, b, c, pat, group))


def design(label, verts, faces, tris):
    """our own details: the Cobra's windscreen, the Sidewinder's canopy and panels, the Viper's canopy (see docs/_128k_version.md)"""
    if label == "shipdatCobraMk3Pirate":              # the windscreen triangle at the nose (vertices 1, 0, 2) in the accent colour
        for i, t in enumerate(tris):
            if {t[0], t[1], t[2]} == {0, 1, 2}:
                tris[i] = (t[0], t[1], t[2], ACC, t[4])
    elif label == "SHIPDATPIRATE1":                   # Sidewinder: a canopy on the top centre and an accent wedge (wing trim) along the rear edge of each top wing panel
        add_tri(verts, tris, inset(verts, (0, 1, 4), (0, 0, 36), 0.7, 0.3), faces[0], ACC, 0)      # canopy (3 new vertices)
        for face, (a, b, c), wing in ((1, (0, 3, 4), (3, 4)), (2, (1, 2, 4), (2, 4))):
            cen = tuple(int(round(sum(verts[i][k] for i in (a, b, c)) / 3)) for k in range(3))
            verts.append(cen)                                                                          # 1 new vertex per wing
            add_tri(verts, tris, (wing[0], wing[1], len(verts) - 1), faces[face], ACC, face)
    elif label in FRONT_LIT and SHIMMER:                # break up the bright rim facets: the second triangle of each gets the mixed pattern
        seen = set()
        for i, tr in enumerate(tris):
            if tr[3] == MAIN and tr[4] in seen:
                tris[i] = (tr[0], tr[1], tr[2], MIX, tr[4])
            seen.add(tr[4])
    elif label == "shipdatCoriolis":                  # the station is symmetric, the light is not: tones by face class (as ArcElite's), so the head-on view is four-fold symmetric
        cls = {0: MAIN, 13: MAIN, 5: DIM, 6: DIM, 7: DIM, 8: DIM}        # the two end faces solid, the four sides dim, the eight corner triangles (1-4, 9-12) mixed
        for i, t in enumerate(tris):
            if t[3] != ACC:
                tris[i] = (t[0], t[1], t[2], cls.get(t[4], MIX), t[4])
    elif label == "shipdatViper":                     # Viper: a canopy triangle on the ridge behind the nose
        ids = []
        for p in ((0, 4, 60), (-9, 13, 15), (9, 13, 15)):       # on the two front slopes (planes z = 72 -+ 2x - 3y), meeting on the ridge
            verts.append(p)
            ids.append(len(verts) - 1)
        add_tri(verts, tris, tuple(ids), (0, 66, 22), ACC, 1)


def build(verts, edges, faces, label=None):
    """-> dict: verts (the hull's, plus any the designs add), tris [(v0, v1, v2, pattern, group)], stats"""
    b = build_struct(verts, edges, faces, label)
    if label:
        design(label, b["verts"], faces, b["tris"])
    return b


def build_stock(m, a, label=None):
    return build(*parse_blueprint(m, a), label=label)


if __name__ == "__main__":
    import subprocess
    import tempfile
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as d:
        out, sym = Path(d) / "c.bin", Path(d) / "c.sym"
        subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), f"--raw={out}", f"--sym={sym}", str(root / "src/elite/commonxx.asm")], check=True, capture_output=True)
        img = bytes(0x1A40) + out.read_bytes()
        labels = {l.split()[0].rstrip(":"): int(l.split()[-1], 16) for l in sym.read_text().splitlines() if l.split() and l.split()[0].lower().startswith("shipdat")}
    print(f"{'hull':24} faces outlines exact/hull  details triangles spread")
    for name, a in sorted(labels.items(), key=lambda kv: kv[1]):
        v, e, f = parse_blueprint(img, a)
        if not f:
            continue
        b = build(v, e, f, name)
        s = b["stats"]
        bs = [brightness(n) for n in f]
        print(f"{name:24} {s['faces']:5} {s['exact']:8}/{s['hull']:<5} {s['decals']:7} {len(b['tris']):9} {max(bs) - min(bs):6.2f}")

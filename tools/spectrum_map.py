#!/usr/bin/env python3
"""Match routines of the stock CPC build (src/elite) to the ZX Spectrum SkoolKit disassembly by code shape.

usage: python3 -I tools/spectrum_map.py [OUTDIR]        (default work/spectrum_map)

Both games share their logic, so a routine often decodes to the same instruction skeleton on both
machines. A skeleton is the list of instructions with every immediate, address and relative offset
replaced by a placeholder. Routines are the blocks `c$XXXX` of the Spectrum `elite.skool`
(addresses decoded from `snapshot/elite-title-loop.sna`) and, on the CPC side, runs of code between
labels in the sjasmplus listing of each `src/elite/*.asm` (a routine starts at a label that follows a
terminator: ret, jp, unconditional jr, or data). Candidates are found through 3-gram overlap and
scored with difflib's ratio. Nothing is copied from the skool file except addresses and label names.

Writes OUTDIR/matches.tsv (cpc file, cpc address, cpc label, spectrum address, spectrum label, ratio,
second-best ratio, tokens) and prints a summary. Needs sjasmplus in ~/.local/bin and work/bin_stock.
"""
import difflib, os, re, subprocess, sys, tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import z80dis  # noqa: E402

SKOOL = ROOT / "work/ext_msx/skoolkit/src/elite.skool"
SNA = ROOT / "work/ext_msx/skoolkit/snapshot/elite-title-loop.sna"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "work/spectrum_map"
FILES = [("commonxx", "COMMONXX", 0x1A40), ("common2x", "COMMON2X", 0xC000),
         ("largeaxx", "LARGEAXX", 0x0840), ("musiquex", "MUSIQUEX", 0x6000)]
MINTOK = 8

HEXN = re.compile(r"\b0x[0-9A-Fa-f]+\b|\$[0-9A-Fa-f]+|\b\d+\b")


def norm(insn):
    t = insn.fmt.replace("{A}", "nn").replace("{R}", "r")
    t = HEXN.sub("n", t)
    return t


def decode_range(mem, start, end, base=0):
    out, pc = [], start
    while pc < end:
        i = z80dis.decode(mem, pc - base) if base else z80dis.decode(mem, pc)
        if not i.valid:
            return None
        out.append((pc, i))
        pc += i.length
    return out


def spectrum_routines():
    mem = bytes(0x4000) + SNA.read_bytes()[27:]
    lines = SKOOL.read_text(errors="replace").split("\n")
    blocks = []                       # (addr, kind, label, title, line_no)
    label, title, comment = None, None, []
    for n, l in enumerate(lines):
        if l.startswith("@label="):
            label = l[7:].strip()
        elif l.startswith(";"):
            comment.append(l)
        m = re.match(r"^([a-z])\$([0-9A-F]{4})", l)
        if m:
            t = ""
            for c in comment:
                s = c[1:].strip()
                if s and s != "." and not s.startswith("#"):
                    t = s
                    break
            blocks.append((int(m.group(2), 16), m.group(1), label, t))
            label, comment = None, []
        elif not l.startswith(";") and not l.startswith("@") and l.strip() == "":
            pass
        if l and not l.startswith((";", "@")) and not re.match(r"^[a-z*\s]", l) and False:
            pass
    routines = []
    for i, (a, k, lab, t) in enumerate(blocks):
        if k != "c":
            continue
        end = blocks[i + 1][0] if i + 1 < len(blocks) else 0x10000
        ins = decode_range(mem, a, end)
        if ins:
            routines.append({"addr": a, "label": lab, "title": t, "toks": [norm(x) for _, x in ins],
                             "calls": [x.addr for _, x in ins if x.flow == "call" and x.addr is not None]})
    return routines


def cpc_routines():
    routines = []
    env = dict(os.environ, PATH=os.path.expanduser("~/.local/bin") + ":" + os.environ["PATH"])
    for name, binf, load in FILES:
        raw = (ROOT / "work/bin_stock" / (binf + ".BIN")).read_bytes()
        mem = bytearray(65536)
        mem[load:load + len(raw)] = raw
        tmp = tempfile.mkdtemp()
        subprocess.run(["sjasmplus", f"--lst={tmp}/x.lst", f"--raw={tmp}/x.bin", str(ROOT / f"src/elite/{name}.asm")],
                       capture_output=True, env=env)
        code = []                     # (addr, label_at_start, is_term)
        pending = None
        for l in open(f"{tmp}/x.lst", errors="replace"):
            m = re.match(r"^\s*\d+\+?\s+([0-9A-F]{4})\s+(.*)$", l.rstrip("\n"))
            if not m:
                continue
            addr, rest = int(m.group(1), 16), m.group(2)
            lm = re.match(r"^(?:[0-9A-F]{2} ?)*\s*([A-Za-z_][A-Za-z_0-9.]*):", rest)
            if re.match(r"^\s*([A-Za-z_][A-Za-z_0-9.]*):\s*$", rest) or re.match(r"^\s{6,}([A-Za-z_][A-Za-z_0-9.]*):\s*$", rest):
                pending = rest.strip().rstrip(":")
                continue
            body = re.sub(r"^(?:[0-9A-F]{2} )+\s*", "", rest).strip()
            if not body or body.startswith(";"):
                continue
            isdata = re.match(r"(?i)(db|dw|ds|defb|defw|defs|dh|equ|org|align|ld sp,\s*$)", body) is not None
            code.append((addr, pending, isdata))
            pending = None
        # build instruction runs
        cur = None
        prev_term = True
        for addr, lab, isdata in code:
            if isdata:
                if cur:
                    routines.append(cur); cur = None
                prev_term = True
                continue
            ins = z80dis.decode(mem, addr) if addr >= load else None
            if ins is None or not ins.valid:
                if cur:
                    routines.append(cur); cur = None
                prev_term = True
                continue
            if cur is None or (lab and prev_term):
                if cur:
                    routines.append(cur)
                cur = {"file": name, "addr": addr, "label": lab, "toks": [], "calls": []}
            cur["toks"].append(norm(ins))
            if ins.flow == "call" and ins.addr is not None:
                cur["calls"].append(ins.addr)
            prev_term = ins.flow in ("ret", "stop") or (ins.flow == "jump")
        if cur:
            routines.append(cur)
    return routines


def ngrams(toks, n=3):
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    spec_all = spectrum_routines()
    cpc_all = cpc_routines()
    spec = [r for r in spec_all if len(r["toks"]) >= MINTOK]
    cpc = [r for r in cpc_all if len(r["toks"]) >= MINTOK]
    print(f"spectrum routines: {len(spec_all)} ({len(spec)} >= {MINTOK} instr); cpc routines: {len(cpc_all)} ({len(cpc)})", file=sys.stderr)
    idx = defaultdict(list)
    for si, s in enumerate(spec):
        for g in ngrams(s["toks"]):
            idx[g].append(si)
    rows = []
    for c in cpc:
        cnt = Counter()
        for g in ngrams(c["toks"]):
            for si in idx.get(g, ()):
                cnt[si] += 1
        cand = []
        for si, _ in cnt.most_common(8):
            s = spec[si]
            lr = len(s["toks"]) / len(c["toks"])
            if not 0.5 < lr < 2.0:
                continue
            r = difflib.SequenceMatcher(None, c["toks"], s["toks"], autojunk=False).ratio()
            cand.append((r, s["addr"]))
        cand.sort(reverse=True)
        if cand:
            r1, s1 = cand[0]
            r2 = cand[1][0] if len(cand) > 1 else 0.0
            c.update(best=s1, r1=r1, r2=r2, how="direct")
            rows.append(c)
    sbyaddr = {r["addr"]: r for r in spec_all}
    bests = {}
    for c in rows:
        if c["best"] not in bests or c["r1"] > bests[c["best"]]["r1"]:
            bests[c["best"]] = c
    pair = {}                      # (file, cpc addr) -> spectrum addr, confident ones
    for c in rows:
        if c["r1"] >= 0.85 and c["r1"] - c["r2"] >= 0.05 and bests[c["best"]] is c:
            pair[(c["file"], c["addr"])] = c
    cstart = {(r["file"], r["addr"]): r for r in cpc_all}
    cstart_addr = defaultdict(list)
    for (f, a), r in cstart.items():
        cstart_addr[a].append(r)
    taken_s = {c["best"] for c in pair.values()}
    changed = True
    rounds = 0
    while changed and rounds < 8:
        changed, rounds = False, rounds + 1
        for (f, a), c in list(pair.items()):
            s = sbyaddr[c["best"]]
            cc = [t for t in c["calls"] if len(cstart_addr.get(t, ())) == 1 and cstart_addr[t][0]["file"] in (f, "commonxx")]
            ss = [t for t in s["calls"] if t in sbyaddr]
            # same call sequence length: align in order
            cc2 = [t for t in c["calls"] if t in cstart_addr]
            if len(cc2) != len(ss):
                continue
            for ct, st in zip(cc2, ss):
                crt = cstart_addr[ct][0]
                key = (crt["file"], crt["addr"])
                if key in pair or st in taken_s:
                    continue
                s2 = sbyaddr[st]
                if min(len(crt["toks"]), len(s2["toks"])) < 3:
                    continue
                r = difflib.SequenceMatcher(None, crt["toks"], s2["toks"], autojunk=False).ratio()
                if r >= 0.70:
                    crt.update(best=st, r1=r, r2=0.0, how="prop")
                    pair[key] = crt
                    taken_s.add(st)
                    rows.append(crt)
                    changed = True
    with open(OUT / "matches.tsv", "w") as f:
        f.write("cpc_file\tcpc_addr\tcpc_label\tspec_addr\tspec_label\tspec_title\tratio\tsecond\ttokens\tmutual\thow\n")
        for c in sorted(rows, key=lambda x: -x["r1"]):
            s = sbyaddr[c["best"]]
            mutual = int(c["how"] == "prop" or bests.get(c["best"]) is c)
            f.write("\t".join(map(str, [c["file"], "%04X" % c["addr"], c["label"] or "", "%04X" % s["addr"], s["label"] or "",
                                        s["title"], "%.3f" % c["r1"], "%.3f" % c["r2"], len(c["toks"]), mutual, c["how"]])) + "\n")
    nd = sum(1 for c in pair.values() if c["how"] == "direct")
    npg = sum(1 for c in pair.values() if c["how"] == "prop")
    print(f"confident direct matches: {nd}; added by call-graph propagation: {npg} (rounds {rounds})", file=sys.stderr)


if __name__ == "__main__":
    main()

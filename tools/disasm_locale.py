#!/usr/bin/env python3
"""Disassemble the German or French build into sjasmplus source (src/elite_de, src/elite_fr) and verify the round trip.

usage: python3 -I tools/disasm_locale.py german|french [OUTDIR]   (wrappers: disasm_german.py, disasm_french.py)
       run tools/map_locale.py first (it writes work/<lang>_map.json); default OUTDIR is src/<SRCDIR> of that language

Names and comments come from the English source (src/elite): every English label whose code or data reference tools/map_locale.py
could pair with a target-language address is used for it, and the comment block above the English label is copied over (comments are
ours, so this is fine). Unmapped places get sub_/loc_/dat_ names. Each file is assembled with sjasmplus and compared byte for byte
with work/bin_<lang>; a mismatch is an error. MUSIQUEX is identical in both builds and is copied unchanged.
Like tools/disasm_stock.py, rerunning it into src/elite_de or src/elite_fr overwrites hand edits: use a scratch directory after editing.
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

# language -> (display name, binary dir under work/, source dir under src/, disk file name)
LOCALES = {
    "german": ("German", "bin_german", "elite_de", "Elite_DE_cracked.dsk"),
    "french": ("French", "bin_fr", "elite_fr", "Elite (1985)(Firebird Software)(fr).dsk"),
}
LANG = sys.argv.pop(1)          # first argument: german | french (the *_german.py / *_french.py wrappers pass it)
NAME, BINDIR, SRCDIR, DISK = LOCALES[LANG]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import disasm_stock as D  # noqa: E402

FILES = [("largeaxx", 0x0840, "LARGEAXX.BIN"), ("commonxx", 0x1A40, "COMMONXX.BIN"), ("common2x", 0xC000, "COMMON2X.BIN")]
GENERIC = re.compile(r"^(sub_|loc_|dat_)[0-9A-Fa-f]{4}$")


def english():
    """address -> [labels], set of instruction addresses, and label -> comment lines above it, per English file."""
    labels, insn, comments = {}, set(), {}
    env = dict(os.environ, PATH=os.path.expanduser("~/.local/bin") + ":" + os.environ["PATH"])
    for n in ("largeaxx", "commonxx", "common2x", "musiquex"):
        d = tempfile.mkdtemp()
        subprocess.run(["sjasmplus", f"--sym={d}/x.sym", f"--lst={d}/x.lst", f"--raw={d}/x.bin", str(ROOT / f"src/elite/{n}.asm")],
                       capture_output=True, env=env)
        for l in open(f"{d}/x.sym"):
            m = re.match(r"(\S+): EQU 0x([0-9A-Fa-f]+)", l)
            if m:
                labels.setdefault(int(m.group(2), 16), []).append(m.group(1))
        for l in open(f"{d}/x.lst", errors="replace"):
            m = re.match(r"^\s*\d+\+?\s+([0-9A-F]{4})\s+((?:[0-9A-F]{2} )+)\s*(\S+)", l)
            if m and m.group(3).lower() not in ("db", "dw", "ds", "dh", "defb", "defw", "defs", "org", "equ"):
                if n != "musiquex":
                    insn.add(int(m.group(1), 16))
        L = (ROOT / f"src/elite/{n}.asm").read_text().split("\n")
        for i, l in enumerate(L):
            m = re.match(r"^([A-Za-z_][A-Za-z_0-9.]*):", l)
            if m:
                j = i
                while j > 0 and L[j - 1].startswith(";"):
                    j -= 1
                if j < i:
                    comments[m.group(1)] = L[j:i]
    return labels, insn, comments


def main(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    mp = json.loads((ROOT / f"work/{LANG}_map.json").read_text())
    code = {int(a, 16): int(g, 16) for a, g in mp["code"].items()}
    data = {int(a, 16): [int(g, 16) for g in gs] for a, gs in mp["data"].items()}
    labels, einsn, comments = english()
    names, tags, kinds = {}, {}, {}
    taken = set()
    # decide the French address of each English label
    for ea in sorted(labels):
        ga = None
        if ea in code:
            ga = code[ea]
        elif ea in data and len(set(data[ea])) == 1:
            ga = data[ea][0]
        if ga is None or ga in names:
            continue
        nm = labels[ea][0]
        names[ga] = nm
        tags[ga] = "map"
        kinds[nm.lower()] = "code" if ea in einsn else "data"
    case_names = {n.lower(): n for n in names.values()}
    inline_g = {int(a, 16): 1 for a in mp[f"inline_{LANG}"]}
    inline_names = {"printstringfollowingbyte", "printfollowingtokenwithspace", "todo_printroutinew"}
    for a, n in names.items():
        if n.lower() in inline_names or kinds.get(n.lower()) == "code" and False:
            inline_g[a] = 1
    # english inline callees keep their names, so find their French addresses by name
    ok_all = True
    work = ROOT / "work"
    for fname, base, binf in FILES:
        data_b = (work / BINDIR / binf).read_bytes()
        end = base + len(data_b)
        seeds = [0x1C82] if fname == "commonxx" else []
        seeds += sorted(a for a, n in names.items() if base <= a < end and kinds.get(n.lower()) == "code")
        data_addrs = {a for a, n in names.items() if base <= a < end and kinds.get(n.lower()) == "data"}
        ext = {a: D.safe(n) for a, n in names.items() if not (base <= a < end)}
        fd = D.FileDis(fname, base, data_b, seeds, data_addrs)
        fd.run(inline_g)
        rounds = 0
        while True:
            new = {a for a in fd.scan() if a not in fd.insn}
            if not new or rounds > 20:
                break
            fd.work = sorted(new)
            fd.run(inline_g)
            rounds += 1
        path = D.generate(fd, names, tags, kinds, case_names, ext, outdir)
        text = path.read_text().split("\n")
        # header and the comment blocks of the English labels
        text[0] = f"; Elite (Amstrad CPC) {fname.upper()}.BIN, {NAME} build ({DISK}): generated by tools/disasm_{LANG}.py"
        text[1] = f"; load address 0x{base:04X}, {len(data_b)} bytes. Names and comments are transferred from src/elite (stock English)"
        text[2] = f"; where tools/map_{LANG}.py paired the code or data; otherwise sub_ (call target), loc_ (jump target), dat_ (data/variable reference)."
        out, nc = [], 0
        for l in text:
            m = re.match(r"^([A-Za-z_][A-Za-z_0-9.]*):\s*$", l)
            if m and m.group(1) in comments and not (out and out[-1].startswith(";")):
                out += comments[m.group(1)]
                nc += 1
            out.append(l)
        path.write_text("\n".join(out))
        same, errs = D.verify(path, data_b)
        code_b = sum(i.length for i in fd.insn.values())
        named = sum(1 for a in names if base <= a < end)
        print(f"{fname:9} {len(data_b):6} bytes  code {code_b:6} ({100 * code_b // len(data_b)}%)  insns {len(fd.insn):5}  "
              f"English names used {named:4}  comment blocks {nc:4}  scan rounds {rounds}  round trip {'IDENTICAL' if same else 'MISMATCH'}")
        for e in errs:
            print("    ", e)
        ok_all &= same
    shutil.copy(ROOT / "src/elite/musiquex.asm", outdir / "musiquex.asm")
    got = subprocess.run([str(D.SJASM), f"--raw={outdir}/m.tmp", str(outdir / "musiquex.asm")], capture_output=True)
    same = (outdir / "m.tmp").read_bytes() == (work / BINDIR / "MUSIQUEX.BIN").read_bytes()
    (outdir / "m.tmp").unlink(missing_ok=True)
    print(f"musiquex  copied from src/elite, round trip {'IDENTICAL' if same else 'MISMATCH'}")
    return 0 if ok_all and same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "src" / SRCDIR))

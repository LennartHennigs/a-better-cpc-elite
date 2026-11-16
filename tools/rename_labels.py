#!/usr/bin/env python3
"""Rename labels in src/elite, src/elite_de and src/elite_fr. usage: rename_labels.py [--en-only] [--no-check] MAPFILE
A label is renamed in each tree that defines it; the report says which trees did not (a dat_ name can stand for a different
thing in German or French: check those uses by hand). --en-only touches src/elite alone.
MAPFILE lines: old new [except=routine1,routine2] [hex=0xXXXX]   (# comments allowed)
References inside an `except` routine keep a numeric operand, for immediate constants that merely collide with the label's
address: 0xXXXX for a dat_XXXX label, else the hex= field (required then). Refuses a name that already exists.
Runs tools/check_src.sh for en, de and fr afterwards (--no-check skips it); exit 1 if one fails (the files stay written)."""
import re, sys, glob, subprocess

EN_ONLY = "--en-only" in sys.argv
NO_CHECK = "--no-check" in sys.argv
sys.argv = [a for a in sys.argv if a not in ("--en-only", "--no-check")]
pairs = []
for line in open(sys.argv[1]):
    line = line.split("#")[0].strip()
    if not line:
        continue
    f = line.split()
    opt = dict(x.split("=", 1) for x in f[2:])
    exc = set(opt["except"].split(",")) if "except" in opt else set()
    num = opt.get("hex") or ("0x" + f[0][4:] if f[0].startswith("dat_") else "")
    if exc and not num:
        sys.exit(f"{f[0]}: except= needs hex=0xXXXX for a label that is not dat_XXXX")
    pairs.append((f[0], f[1], exc, num))

trees = ["src/elite"] + ([] if EN_ONLY else ["src/elite_de", "src/elite_fr"])
files = {p: open(p).read().split("\n") for t in trees for p in sorted(glob.glob(t + "/*.asm"))}
alltext = {t: "\n".join("\n".join(v) for p, v in files.items() if p.startswith(t + "/")) for t in trees}
lab = re.compile(r"^([A-Za-z_][A-Za-z_0-9.]*):")
news = [new for _, new, _, _ in pairs]
dups = sorted({n for n in news if news.count(n) > 1})
if dups:
    sys.exit(f"the map gives the same new name twice: {', '.join(dups)}")
for old, new, exc, num in pairs:
    for t in trees:
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(new) + r"(?![A-Za-z0-9_])", alltext[t]):
            sys.exit(f"name {new} already used in {t} (for {old})")
    if not re.search(r"^" + old + ":", alltext["src/elite"], re.M):
        sys.exit(f"{old}: no definition")
defined = {(old, t): bool(re.search(r"^" + old + r"(:| equ)", alltext[t], re.M)) for old, _, _, _ in pairs for t in trees}
n = 0
for old, new, exc, num in pairs:
    skipped = [t for t in trees if not defined[old, t]]
    if skipped:
        print(f"{old} -> {new}: not defined in {', '.join(skipped)}, left alone there")
    rx = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
    for p, L in files.items():
        tree = p.rsplit("/", 1)[0]
        if not defined[old, tree]:
            continue
        enc = ""
        for i, l in enumerate(L):
            m = lab.match(l)
            if m and not m.group(1).startswith("dat_"):
                enc = m.group(1)
            if l.startswith(old + ":"):
                L[i] = l.replace(old, new, 1); n += 1
            elif rx.search(l):
                L[i] = rx.sub(num if enc in exc else new, l); n += 1
for p, L in files.items():
    open(p, "w").write("\n".join(L))
print(f"{len(pairs)} labels renamed, {n} lines changed")
if not NO_CHECK:
    bad = [loc or "en" for loc in ("", "de", "fr") if subprocess.run(["bash", "tools/check_src.sh"] + ([loc] if loc else []), stdout=subprocess.DEVNULL).returncode]
    if bad:
        sys.exit(f"check_src.sh FAILED for {', '.join(bad)}: run it by hand, or git checkout src/")
    print("check_src.sh ok for en, de, fr")

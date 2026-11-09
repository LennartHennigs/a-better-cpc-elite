#!/usr/bin/env python3
"""Rename dat_XXXX labels in src/elite/*.asm. usage: rename_dat.py [--all-trees] MAPFILE
--all-trees also renames the same label in src/elite_de and src/elite_fr, but only where it is defined (a dat_ name can stand
for a different thing there: check the German and French uses first).
MAPFILE lines: dat_XXXX newName [except=routine1,routine2]   (# comments allowed)
References inside an `except` routine keep a numeric operand (0xXXXX), for immediate constants that merely
collide with the label's address. Refuses a name that already exists. Check with tools/check_src.sh after."""
import re, sys, glob

ALL = "--all-trees" in sys.argv
argv = [a for a in sys.argv[1:] if a != "--all-trees"]
pairs = []
for line in open(argv[0]):
    line = line.split("#")[0].strip()
    if not line:
        continue
    f = line.split()
    exc = set(f[2].split("=", 1)[1].split(",")) if len(f) > 2 and f[2].startswith("except=") else set()
    pairs.append((f[0], f[1], exc))

trees = ["src/elite"] + (["src/elite_de", "src/elite_fr"] if ALL else [])
files = {p: open(p).read().split("\n") for t in trees for p in sorted(glob.glob(t + "/*.asm"))}
alltext = {t: "\n".join("\n".join(v) for p, v in files.items() if p.startswith(t + "/")) for t in trees}
def files_in(tree):
    return ["\n".join(v) for p, v in files.items() if p.startswith(tree + "/")]


lab = re.compile(r"^([A-Za-z_][A-Za-z_0-9.]*):")
news = [new for _, new, _ in pairs]
dups = sorted({n for n in news if news.count(n) > 1})
if dups:
    sys.exit(f"the map gives the same new name twice: {', '.join(dups)}")
for old, new, exc in pairs:
    for t in trees:
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(new) + r"(?![A-Za-z0-9_])", alltext[t]):
            sys.exit(f"name {new} already used in {t} (for {old})")
    if not re.search(r"^" + old + ":", alltext["src/elite"], re.M):
        sys.exit(f"{old}: no definition")
n = 0
for old, new, exc in pairs:
    rx = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
    for p, L in files.items():
        tree = p.rsplit("/", 1)[0]
        if tree != "src/elite" and not re.search(r"^" + old + r"(:| equ)", "\n".join(files_in(tree)), re.M):
            continue
        enc = ""
        for i, l in enumerate(L):
            m = lab.match(l)
            if m and not m.group(1).startswith("dat_"):
                enc = m.group(1)
            if l.startswith(old + ":"):
                L[i] = l.replace(old, new, 1); n += 1
            elif rx.search(l):
                L[i] = rx.sub("0x" + old[4:] if enc in exc else new, l); n += 1
for p, L in files.items():
    open(p, "w").write("\n".join(L))
print(f"{len(pairs)} labels renamed, {n} lines changed")

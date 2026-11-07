#!/usr/bin/env python3
"""Rename dat_XXXX labels in src/elite/*.asm. usage: rename_dat.py MAPFILE
MAPFILE lines: dat_XXXX newName [except=routine1,routine2]   (# comments allowed)
References inside an `except` routine keep a numeric operand (0xXXXX), for immediate constants that merely
collide with the label's address. Refuses a name that already exists. Check with tools/check_src.sh after."""
import re, sys, glob

pairs = []
for line in open(sys.argv[1]):
    line = line.split("#")[0].strip()
    if not line:
        continue
    f = line.split()
    exc = set(f[2].split("=", 1)[1].split(",")) if len(f) > 2 and f[2].startswith("except=") else set()
    pairs.append((f[0], f[1], exc))

files = {p: open(p).read().split("\n") for p in sorted(glob.glob("src/elite/*.asm"))}
alltext = "\n".join("\n".join(v) for v in files.values())
lab = re.compile(r"^([A-Za-z_][A-Za-z_0-9.]*):")
for old, new, exc in pairs:
    if re.search(r"(?<![A-Za-z0-9_])" + re.escape(new) + r"(?![A-Za-z0-9_])", alltext):
        sys.exit(f"name {new} already used (for {old})")
    if not re.search(r"^" + old + ":", alltext, re.M):
        sys.exit(f"{old}: no definition")
n = 0
for old, new, exc in pairs:
    rx = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
    for p, L in files.items():
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

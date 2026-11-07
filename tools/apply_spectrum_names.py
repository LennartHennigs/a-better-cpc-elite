#!/usr/bin/env python3
"""Seed src/elite with names from the ZX Spectrum disassembly, using work/spectrum_map/matches.tsv
(run tools/spectrum_map.py first).

usage: python3 -I tools/apply_spectrum_names.py [--dry]

1. Generic CPC labels (SUB_ram_*, LAB_ram_*, sub_*, loc_*) whose routine matches a Spectrum routine with an
   @label at ratio >= 0.90 (or >= 0.80 when found through the call graph), margin >= 0.05 over the runner-up and mutual best are renamed to that label
   (through tools/rename_dat.py, map kept in tools/rename_maps/2026-11-07-spectrum-names.txt).
2. Every match at ratio >= 0.85 (propagated: >= 0.70) gets one comment line above its label:
   `; ZX Spectrum: <label> (&ADDR) <ratio>`, so the Spectrum commentary can be read at that address. No
   commentary text is copied. Rerunning does not duplicate lines. Check with tools/check_src.sh afterwards.
"""
import csv, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
dry = "--dry" in sys.argv
rows = list(csv.DictReader(open(ROOT / "work/spectrum_map/matches.tsv"), delimiter="\t"))
GEN = re.compile(r"^(sub_|loc_|LAB_ram_|SUB_ram_)")
def good(r):
    if r.get("how") == "prop":
        return float(r["ratio"]) >= 0.70
    return float(r["ratio"]) >= 0.85 and float(r["ratio"]) - float(r["second"]) >= 0.05 and r["mutual"] == "1"
def strong(r):
    return float(r["ratio"]) >= (0.80 if r.get("how") == "prop" else 0.90)
ok = [r for r in rows if good(r)]
text = {p: p.read_text() for p in sorted((ROOT / "src/elite").glob("*.asm"))}
alltext = "\n".join(text.values())
used = set(re.findall(r"[A-Za-z_][A-Za-z_0-9.]*", alltext))
RESERVED = {"main", "end", "map", "page", "size", "high", "low", "abs", "module", "endmodule", "display", "assert", "struct", "device"}
rename, seen = [], set()
for r in ok:
    s = r["spec_label"]
    if (not strong(r) or not GEN.match(r["cpc_label"]) or not s or s in used or s in seen
            or s.lower() in RESERVED or not re.search(r"^" + re.escape(r["cpc_label"]) + ":", alltext, re.M)):
        continue
    seen.add(s)
    rename.append((r["cpc_label"], s))
mp = ROOT / "tools/rename_maps/2026-11-07-spectrum-names.txt"
print(f"{len(rename)} renames")
if dry:
    for o, n in rename[:200]: print(o, n)
    sys.exit()
mp.write_text("# names from the ZX Spectrum SkoolKit disassembly, matched by tools/spectrum_map.py (direct ratio >= 0.90, propagated >= 0.80)\n"
              + "\n".join(f"{o} {n}" for o, n in rename) + "\n")
subprocess.run([sys.executable, "-I", str(ROOT / "tools/rename_dat.py"), str(mp)], cwd=ROOT, check=True)
newname = dict(rename)
text = {p: p.read_text().split("\n") for p in sorted((ROOT / "src/elite").glob("*.asm"))}
fname = {"commonxx": ROOT / "src/elite/commonxx.asm", "common2x": ROOT / "src/elite/common2x.asm",
         "largeaxx": ROOT / "src/elite/largeaxx.asm", "musiquex": ROOT / "src/elite/musiquex.asm"}
n = 0
for r in ok:
    lab = newname.get(r["cpc_label"], r["cpc_label"])
    if not lab:
        continue
    L = text[fname[r["cpc_file"]]]
    idx = next((i for i, l in enumerate(L) if l.startswith(lab + ":")), None)
    if idx is None:
        continue
    mark = f"; ZX Spectrum: {r['spec_label'] or '-'} (&{r['spec_addr']}) {float(r['ratio']):.2f}"
    if idx > 0 and L[idx - 1].startswith("; ZX Spectrum:"):
        continue
    L.insert(idx, mark)
    n += 1
for p, L in text.items():
    p.write_text("\n".join(L))
print(f"{n} comment lines added")

#!/usr/bin/env python3
"""Find data tables that are byte-identical in the ZX Spectrum build and the CPC stock image.

usage: python3 -I tools/spectrum_data_map.py [OUT.tsv]        (default work/spectrum_map/data_matches.tsv)
Blocks come from the data blocks (b/w/t/s/u) of the Spectrum elite.skool (bytes from snapshot/elite-title-loop.sna);
each block of at least 12 bytes with at least 4 distinct values is searched in work/stock_mem_image.bin. Reports the
CPC address (and the label that src/elite has there, found in the sjasmplus symbol files) when the block occurs once.
"""
import re, subprocess, sys, os, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SK = (ROOT / "work/ext_msx/skoolkit/src/elite.skool").read_text(errors="replace").split("\n")
SNA = (ROOT / "work/ext_msx/skoolkit/snapshot/elite-title-loop.sna").read_bytes()[27:]
spec = bytes(0x4000) + SNA
cpc = (ROOT / "work/stock_mem_image.bin").read_bytes()
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "work/spectrum_map/data_matches.tsv"
env = dict(os.environ, PATH=os.path.expanduser("~/.local/bin") + ":" + os.environ["PATH"])
sym = {}
for n in ("commonxx", "common2x", "largeaxx", "musiquex"):
    d = tempfile.mkdtemp()
    subprocess.run(["sjasmplus", f"--sym={d}/x.sym", f"--raw={d}/x.bin", str(ROOT / f"src/elite/{n}.asm")], capture_output=True, env=env)
    for l in open(f"{d}/x.sym"):
        m = re.match(r"(\S+): EQU 0x([0-9A-Fa-f]+)", l)
        if m:
            sym.setdefault(int(m.group(2), 16), []).append((n, m.group(1)))
blocks, label, title = [], None, ""
for l in SK:
    if l.startswith("@label="):
        label = l[7:].strip()
    m = re.match(r"^([a-z])\$([0-9A-F]{4})", l)
    if m:
        blocks.append((int(m.group(2), 16), m.group(1), label)); label = None
rows = []
for i, (a, k, lab) in enumerate(blocks):
    if k == "c" or not lab:
        continue
    end = blocks[i + 1][0] if i + 1 < len(blocks) else 0x10000
    data = spec[a:end]
    if len(data) < 12 or len(set(data)) < 4:
        continue
    hits = [m.start() for m in re.finditer(re.escape(data), cpc, re.S)]
    if len(hits) == 1:
        rows.append((lab, a, len(data), hits[0], sym.get(hits[0], [])))
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w") as f:
    f.write("spec_label\tspec_addr\tlen\tcpc_addr\tcpc_labels\n")
    for lab, a, n, c, s in rows:
        f.write(f"{lab}\t{a:04X}\t{n}\t{c:04X}\t{' '.join(x[1] for x in s)}\n")
print(len(rows), "unique identical tables ->", out)

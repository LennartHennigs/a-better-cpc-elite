#!/usr/bin/env python3
"""List the byte ranges that a disassembled tree still holds as `db` data (candidates for hidden code), from the sjasmplus listing.

usage: python3 -I tools/db_ranges.py ASM [OUT.json]       e.g. work/elite128/dis_new/commonxx.asm
Assembles ASM with --lst into work/elite128/relo/, collects the address range of every `db` line, merges neighbours, and prints count and total bytes.
With OUT.json the merged ranges are written as [[start, end_inclusive], ...] for tools/exec_in_data.py.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
asm = Path(sys.argv[1])
work = ROOT / "work/elite128/relo"
work.mkdir(parents=True, exist_ok=True)
lst = work / (asm.stem + ".lst")
subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), f"--lst={lst}", f"--raw={work / (asm.stem + '.bin')}", str(asm)], capture_output=True, check=True)
BASES = {"commonxx": 0x1A40, "largeaxx": 0x0840, "common2x": 0xC000, "musiquex": 0x6000}
base = BASES[asm.stem]
binary = (work / (asm.stem + ".bin")).read_bytes()
covered = bytearray(len(binary))
for line in lst.read_text(errors="replace").splitlines():
    m = re.match(r"^\s*\d+\+*\s+([0-9A-F]{4})\s+((?:[0-9A-F]{2}\s?)+)\s+(\S.*)$", line)
    if not m or re.fullmatch(r"(?:[0-9A-F]{2}\s*)+", m.group(3).strip()):
        continue                                  # no match, or a continuation row of a long db (its last byte pair looks like source text)
    src = m.group(3).split(";")[0].strip().lower()
    if re.match(r"(db|dw|ds|defb|defw|defs|dup|edup|incbin|org|align|dd|dz)\b", src):
        continue
    a = int(m.group(1), 16) - base
    n = len(m.group(2).split())
    for i in range(a, min(a + n, len(binary))):
        covered[i] = 1
rows = []
i = 0
while i < len(binary):
    if covered[i]:
        i += 1
        continue
    j = i
    while j < len(binary) and not covered[j]:
        j += 1
    if any(binary[i:j]):                      # skip all-zero runs (buffers: an executed zero is a nop slide, not code)
        rows.append((base + i, base + j - 1))
    i = j
merged = [list(r) for r in rows]
print(f"{len(merged)} data ranges (not covered by an instruction, not all zero), {sum(b - a + 1 for a, b in merged)} bytes of {len(binary)}")
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(json.dumps(merged))

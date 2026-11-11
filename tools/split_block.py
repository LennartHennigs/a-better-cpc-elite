#!/usr/bin/env python3
"""Move the code block out of the &4000-&7FFF window and the screen-gap content into it (128K plan, phase 3). One-way text surgery on src/elite128.

usage: python3 -I tools/split_block.py DIR [--write]          DIR = src/elite128 (committed first: git is the undo)
Before: commonxx.asm holds the stock code from &1A40 to &9FFF (the window &4000-&7FFF is code); common2x.asm holds the screen-gap content, assembled at &C000.
After:
  commonxx.asm   head (up to &3FFD) | `ds` to the window | INCLUDE "gaps.asm" (the old common2x text, assembled at SCREEN = &4000) | `ds` to &8073 | tail (from shipEntityInitMatrixdata);
                 the bytes printCleartext..DistanceToPlanet (&3FDD-&4139) move to the resident glue area (before hullVertexBuf)
  common2x.asm   the block DistanceToPlanet..shipEntityInitMatrixdata (&413A-&8072, 16,185 bytes) at org &C000, padded to 16384 bytes
  gaps.asm       the old common2x text with org SCREEN
SCREEN becomes 0x4000 in every file. Cross-file names are fixed afterwards by tools/gen_equs.py. Not a byte-exact transformation: the layout is new.
"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1])
write = "--write" in sys.argv
cx = (d / "commonxx.asm").read_text().split("\n")
c2 = (d / "common2x.asm").read_text().split("\n")


def find(lines, label, start=0):
    for i in range(start, len(lines)):
        if lines[i].startswith(label + ":"):
            return i
    raise SystemExit(f"label {label} not found")


i_p0 = find(cx, "printCleartext")
i_b0 = find(cx, "DistanceToPlanet")
i_b1 = find(cx, "shipEntityInitMatrixdata")
i_glue = find(cx, "hullVertexBuf")
assert i_p0 < i_b0 < i_b1 < i_glue, (i_p0, i_b0, i_b1, i_glue)


def balanced(seg):
    depth = 0
    for l in seg:
        t = l.split(";")[0].strip().lower()
        if re.match(r"(if|ifdef|ifndef|ifn)\b", t):
            depth += 1
        elif t.startswith("endif"):
            depth -= 1
        if depth < 0:
            return False
    return depth == 0


P, B = cx[i_p0:i_b0], cx[i_b0:i_b1]
assert balanced(P) and balanced(B), "IF blocks cross a split point"
print(f"resident piece: lines {i_p0 + 1}-{i_b0}, block: lines {i_b0 + 1}-{i_b1}")
head, tail, glue_and_rest = cx[:i_p0], cx[i_b1:i_glue], cx[i_glue:]
new_cx = (head
          + ["; --- the &4000 window page: screen pixels (blank) and the code, tables and variables that used to hide in the gaps of the screen page at &C000 (COMMON2X in the 64K layout) ---",
             "    ds 0x4000 - $                       ; &3FFE-&3FFF: the two bytes of the old replacewithminus (moved to the resident glue)",
             '    INCLUDE "gaps.asm"',
             "    ds 0x8073 - $                       ; &8000-&8072: the end of the line drawing code moved to bank 7 with the block"]
          + tail
          + ["; --- moved here from &3FFE-&4139: small routines that LARGEAXX and the block call, now resident (the window is the screen) ---"] + P
          + glue_and_rest)
# gaps.asm: the old common2x text, assembled at SCREEN (&4000)
gaps = [l for l in c2]
# common2x.asm: the block at &C000
new_c2 = (["SCREEN equ 0x4000            ; the screen page (the 128K layout); the block below runs in RAM bank 7 at &C000",
           "    org 0xC000",
           "; Code block of the 128K build: DistanceToPlanet..end of the line drawing code (stock &413A-&8072), assembled for RAM bank 7 at &C000 (loaded there by the BASIC loader, as COMMON2X.BIN)."]
          + B
          + ["    ds 0xC000 + 16384 - $               ; the file is 16384 bytes (tools/build_dsk128.py keeps the AMSDOS header length)"])
# ---- post-processing (what was done by hand the first time) ----
import subprocess, tempfile
# mid-instruction equates: `name equ 0xADDR ; inside the instruction at 0xINSN` lines at the end of commonxx.asm whose instruction lies in the block become labels + expression equates in common2x.asm
mid = []
for k, l in enumerate(new_cx):
    m = re.match(r"(\w+) equ 0x([0-9A-Fa-f]+)\s*; inside the instruction at 0x([0-9A-Fa-f]+)", l)
    if m:
        mid.append((k, m.group(1), int(m.group(2), 16), int(m.group(3), 16)))
with tempfile.TemporaryDirectory() as tmp:
    lst = Path(tmp) / "o.lst"
    r = subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DENHANCED", "-DTITLESEL", "-DMISSIONS", f"--lst={lst}", f"--raw={Path(tmp) / 'o.bin'}", str(d / "commonxx.asm")], capture_output=True, text=True)
    addr_line = {}
    for l in lst.read_text(errors="replace").splitlines():
        m = re.match(r"^\s*(\d+)\s+([0-9A-F]{4})\s+(?:[0-9A-F]{2}\s?)+\s+\S", l)
        if m:
            addr_line.setdefault(int(m.group(2), 16), int(m.group(1)))
mid_equs, drop_idx = [], set()
for k, name, value, insn in mid:
    old_line = addr_line.get(insn)
    if old_line is None or not (i_b0 + 1 <= old_line <= i_b1):
        continue                                   # the instruction is not in the block (stays an equ of commonxx)
    pos = old_line - 1 - i_b0                      # index inside B
    lab = f"mi_{insn:04X}"
    if not B[pos - 1].startswith("mi_"):
        B.insert(pos, f"{lab}:")
        # later insertions shift positions: keep the table of insertions consistent by adjusting addr_line users below
        for kk in list(addr_line):
            if addr_line[kk] - 1 - i_b0 >= pos and addr_line[kk] > old_line:
                addr_line[kk] += 1
    mid_equs.append(f"{name} equ {lab}+{value - insn}   ; inside the instruction at {lab} (patched or jumped into)")
    drop_idx.add(k)
new_cx = [l for k, l in enumerate(new_cx) if k not in drop_idx]
flag_block = cx[next(i for i, l in enumerate(cx) if l.strip() == "IFNDEF STAR_OCCLUDE"):next(i for i, l in enumerate(cx) if l.strip() == "IFNDEF STAR_OCCLUDE") + 7]
assert flag_block[-1].strip() == "ENDIF", flag_block
new_c2 = (["SCREEN equ 0x4000            ; the screen page (the 128K layout); the block below runs in RAM bank 7 at &C000"] + flag_block
          + ["    IFDEF MISSIONS", "MISSIONS_POD equ STAR_OCCLUDE", "    ENDIF", "    org 0xC000"] + mid_equs
          + ["; Code block of the 128K build: DistanceToPlanet..end of the line drawing code (stock &413A-&8072), assembled for RAM bank 7 at &C000 (loaded there by the BASIC loader, as COMMON2X.BIN)."]
          + B + ["    ds 0xC000 + 16384 - $               ; the file is 16384 bytes (tools/build_dsk128.py keeps the AMSDOS header length)"])
# numeric relative jumps in the old COMMON2X text (data that the disassembler decoded as `jr c,0xBFD2`) cannot work at the new base: back to their bytes
with tempfile.TemporaryDirectory() as tmp:
    lst2 = Path(tmp) / "c2.lst"
    subprocess.run([str(Path.home() / ".local/bin/sjasmplus"), "-DENHANCED", f"--lst={lst2}", f"--raw={Path(tmp) / 'c2.bin'}", str(d / "common2x.asm")], capture_output=True, text=True)
    bytes_of_line, addr_of_line = {}, {}
    for l in lst2.read_text(errors="replace").splitlines():
        m = re.match(r"^\s*(\d+)\s+([0-9A-F]{4})\s+((?:[0-9A-F]{2}\s?)+)\s+\S", l)
        if m:
            bytes_of_line.setdefault(int(m.group(1)), m.group(3).split())
            addr_of_line.setdefault(int(m.group(1)), int(m.group(2), 16))
for k, l in enumerate(gaps):
    if re.match(r"\s*(jr|djnz)\s+(\w+,)?0x[0-9A-Fa-f]{4}\b", l.split(";")[0]):
        bs = bytes_of_line.get(k + 1)
        assert bs, (k, l)
        gaps[k] = "    db " + ",".join("0x" + b for b in bs) + "   ; was: " + l.strip()
# gaps.asm: drop the header equ lines (their names are now labels of the same assembly), the SCREEN line, the macro (commonxx.asm has it), the org line; keep mid-instruction equates in SCREEN terms
g2 = []
skip_macro = False
for l in gaps:
    t = l.strip()
    if t.startswith("macro circlePushRun"):
        skip_macro = True
    if skip_macro:
        if t.lower() == "endm":
            skip_macro = False
        continue
    m = re.match(r"\s*([A-Za-z_]\w*)\s+equ\s+(.*)$", l)
    if m:
        if "inside the instruction" in l:
            g2.append(re.sub(r"0x([0-9A-Fa-f]{4})", lambda x: "SCREEN+0x%04X" % (int(x.group(1), 16) - 0xC000) if int(x.group(1), 16) >= 0xC000 else x.group(0), l, count=1))
        continue
    if re.match(r"\s*org\b", l, re.I):
        g2.append("; (org removed: gaps.asm is INCLUDEd by commonxx.asm at &4000)")
        continue
    g2.append(l)
gaps = g2
# commonxx.asm: weird equ relative to a flight-tail label that names a COMMON2X routine (a label of gaps.asm now)
new_cx = [l for l in new_cx if not re.match(r"SUB_ram_e74c equ ", l)]
# hullQ (48 bytes of the deferred hull list) moves into the 115 free bytes at &8000-&8072
t = "\n".join(new_cx)
hq = "hullQ:\n    ds 8 * 6                            ; per entry: IX, IY (words), B, key (0xFF = drawn)\n"
assert t.count(hq) == 1
t = t.replace(hq, "")
end_ds = "    ds 0x8073 - $                       ; &8000-&8072: the end of the line drawing code moved to bank 7 with the block\n"
assert t.count(end_ds) == 1
t = t.replace(end_ds, "hullQ:                                  ; &8000-&8072 are free since the line drawing code moved to bank 7 with the block\n    ds 8 * 6                            ; per entry of the deferred hull list: IX, IY (words), B, key (0xFF = drawn)\n    ds 0x8073 - $\n")
# the TITLE_* jump table equates are labels of gaps.asm now
t = re.sub(r"^TITLE_(SCREEN2|NEXT|NAME) equ .*\n", "", t, flags=re.M)
# the music player (MUSIQUEX, an overlay at &6000) cannot run from the window: the 128K build has no music. flagMusicLoaded stays 0, so the ISR never jumps to &604A.
def cut(txt, old, new, count=1):
    assert txt.count(old) == count, (old[:60], txt.count(old))
    return txt.replace(old, new)
t = cut(t, "loadMusicnIndicator:\n    call bankMusic                      ; 128K build: MUSIQUEX from RAM bank 4\n    nop                                 ; the four inline argument bytes of the original `call loadFile`: same length, run as nops\n    nop\n    nop\n    nop\n    ld a,0x01\n    ld (flagMusicLoaded),a\n    ld hl,0x6170   ; a number, not an address: its bytes 70 61 are stored over code as instructions\n    ld (smcIndicatorPatch1),hl\n    ld (smcIndicatorPatch2),hl\n    call loadIndicator\n",
        "loadMusicnIndicator:\n    call loadIndicator                  ; 128K build: no music (the player is an overlay at &6000, which is the screen window now)\n")
t = cut(t, "    call bankNotMusic                   ; 128K build: NOTMUSIC from RAM bank 4\n    nop                                 ; the four inline argument bytes of the original `call loadFile`: same length, run as nops\n    nop\n    nop\n    nop\n", "")
a2 = t.index("    ld bc,0x7FC4                        ; MUSIQUEX (bank 4 window")
b2 = t.index("    call loadFile\n    dw 0x5000")
t = t[:a2] + "    ld bc,0x7FC5                        ; INDICATO (bank 5 window &5000) is read from the disk once, with the bank mapped: the firmware loads into it\n    out (c),c\n" + t[b2:]
a2 = t.index("    ld hl,0x6000                        ; NOTMUSIC is the COMMONXX slice")
b2 = t.index("    call bankChunk\n", a2) + len("    call bankChunk\n")
t = t[:a2] + t[b2:]
a2 = t.index("bankMusic:")
b2 = t.index("bankIndicator:")
t = t[:a2] + t[b2:]
t = cut(t, "bankBuf:\n    ds 256\n", "bankBuf:\n    ds 64\n")
t = cut(t, "    ld bc,0x0100\n    ldir\n    ld (bankSrc),hl\n", "    ld bc,0x0040\n    ldir\n    ld (bankSrc),hl\n")
t = cut(t, "    ld hl,bankBuf\n    ld de,(bankDst)\n    ld bc,0x0100\n    ldir\n", "    ld hl,bankBuf\n    ld de,(bankDst)\n    ld bc,0x0040\n    ldir\n")
t = cut(t, "    ld b,0x10                           ; 16 chunks of 256 bytes = 4096\n", "    ld b,0x40                           ; 64 chunks of 64 bytes = 4096\n")
t = cut(t, "; Copy 256-byte chunks", "; Copy 64-byte chunks")
t = cut(t, "bankIndicator:                          ; INDICATO, bank 5 window &5000 -> &0840 (loadIndicator swaps it into place)", "bankIndicator:                          ; INDICATO, bank 5 window &5000 -> &0840 (loadIndicator swaps it into place)")
new_cx = t.split("\n")
# title screen ship selection: the zero tail of MUSIQUEX (&6E21) cannot stay in the window as a RAM overlay; its code goes into the blank gap row of the screen page at SCREEN+0x1600 (read-only)
mq = (d / "musiquex.asm").read_text().split("\n")
a_ = next(i for i, l in enumerate(mq) if l.strip() == "ASSERT $ == 0x6E21")
b_ = next(i for i, l in enumerate(mq) if l.strip().startswith("ASSERT $ <= 0x7000"))
titles = {"jp titleScreen2": "TITLE_SCREEN2", "jp titleNext": "TITLE_NEXT", "jp titleName": "TITLE_NAME"}
T = []
for l in mq[a_ + 1:b_]:
    key = l.split(";")[0].strip()
    if key in titles:
        T.append(titles[key] + ":")
    T.append(l)
split_at = next(i for i, l in enumerate(T) if l.startswith("; spawnCommandParser actions"))
T_code, T_data = T[:split_at], T[split_at:]
# code: resident glue (before hullGlueEnd); data (ship list, names): end of the block
gi = next(i for i, l in enumerate(new_cx) if l.startswith("hullGlueEnd:"))
new_cx[gi:gi] = [" IFDEF TITLESEL", "; --- title screen ship selection: in the 64K layout the zero tail of MUSIQUEX at &6E21, an overlay in the window; resident code here, its two tables at the end of the bank 7 block ---"] + T_code + [" ENDIF"]
ci = next(i for i, l in enumerate(new_c2) if l.startswith("    ds 0xC000 + 16384 - $"))
new_c2[ci:ci] = [" IFDEF TITLESEL"] + T_data + [" ENDIF"]

if write:
    (d / "gaps.asm").write_text("\n".join(gaps))
    (d / "commonxx.asm").write_text("\n".join(new_cx))
    (d / "common2x.asm").write_text("\n".join(new_c2))
    for f in ("commonxx.asm", "largeaxx.asm", "gaps.asm"):
        p = d / f
        t = p.read_text()
        t = re.sub(r"^SCREEN equ 0xC000", "SCREEN equ 0x4000", t, flags=re.M)
        p.write_text(t)
    print("written")

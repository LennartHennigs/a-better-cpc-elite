#!/usr/bin/env python3
"""Map the stock English build onto the German or French build by walking both binaries in lockstep.

usage: python3 -I tools/map_locale.py german|french [OUT.json]   (wrappers: map_german.py, map_french.py; default OUT work/<lang>_map.json)

Both builds are the same program with different text, so from a common start the instruction streams are identical except for
their address operands. Starting at the entry point (and at every English code label of src/elite), both binaries are decoded
together; instructions must have the same shape and length. Jump, call and data operands give address pairs (English, target),
which seed further walking. Calls to the inline-byte routines skip their inline bytes on both sides.
Output: pairs of code addresses and data addresses per file, and the places where the two streams diverge.
Needs work/bin_stock, work/bin_<lang>, work/fessor_to_stock.sym (for the inline callees) and sjasmplus (for src/elite labels).
"""
import json, re, subprocess, tempfile, os
from collections import deque
from pathlib import Path

import sys
# language -> (display name, binary dir under work/, source dir under src/, disk file name)
LOCALES = {
    "german": ("German", "bin_german", "elite_de", "Elite_DE_cracked.dsk"),
    "french": ("French", "bin_fr", "elite_fr", "Elite (1985)(Firebird Software)(fr).dsk"),
}
LANG = sys.argv.pop(1)          # first argument: german | french (the *_german.py / *_french.py wrappers pass it)
NAME, BINDIR, SRCDIR, DISK = LOCALES[LANG]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import z80dis as Z  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / f"work/{LANG}_map.json"
FILES = [("largeaxx", 0x0840, "LARGEAXX"), ("commonxx", 0x1A40, "COMMONXX"), ("common2x", 0xC000, "COMMON2X")]   # MUSIQUEX (identical in both builds) overlays &6000 only while the music plays
INLINE = {"printstringfollowingbyte", "printfollowingtokenwithspace", "todo_printroutinew"}


def load():
    E, G = bytearray(65536 + 8), bytearray(65536 + 8)
    for _, base, f in FILES:
        for mem, d in ((E, "bin_stock"), (G, BINDIR)):
            b = (ROOT / "work" / d / (f + ".BIN")).read_bytes()
            if f == "MUSIQUEX" and mem is G:
                pass
            mem[base:base + len(b)] = b
    return E, G


def english_labels():
    """label -> address, and the set of instruction start addresses, from the current src/elite sources."""
    labels, insn = {}, set()
    env = dict(os.environ, PATH=os.path.expanduser("~/.local/bin") + ":" + os.environ["PATH"])
    for n, base, f in FILES:
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
                insn.add(int(m.group(1), 16))
    return labels, insn


NUM = re.compile(r"0x[0-9A-Fa-f]{1,2}\b")


def shape(i):
    """Instruction shape: 8-bit immediates are wildcards (the localized build changes key codes and token numbers), displacements kept."""
    f = i.fmt
    if f.startswith(("ld ", "cp ", "and ", "or ", "xor ", "add ", "sub ", "adc ", "sbc ")) and "(ix" not in f and "(iy" not in f:
        f = NUM.sub("n", f)
    return f


def main():
    E, G = load()
    labels, einsn = english_labels()
    fess = {}
    for l in (ROOT / "work/fessor_to_stock.sym").read_text().splitlines():
        m = re.match(r"(\w+) equ #([0-9A-Fa-f]+) ; (\S+)", l)
        if m and m.group(1).lower() in INLINE:
            fess[int(m.group(2), 16)] = 1
    inline_e, inline_g = dict(fess), {}
    ranges = [(b, b + (len(E) and (ROOT / "work/bin_stock" / (f + ".BIN")).stat().st_size)) for _, b, f in FILES]
    inr = lambda a: any(lo <= a < hi for lo, hi in ranges)
    code = {}          # english addr -> target addr
    inv = {}           # target addr -> english addr
    data = {}          # english data addr -> target addr (references)
    conflicts, diverge = [], []
    work = deque()

    def push(ea, ga, why):
        if not (inr(ea) and inr(ga)):
            return
        if ea in code:
            if code[ea] != ga:
                conflicts.append((ea, code[ea], ga, why))
            return
        work.append((ea, ga, why))

    start = [(0x1C82, 0x1C82, "entry")]
    for ea, ga, w in start:
        push(ea, ga, w)
    rounds = 0
    while True:
        while work:
            ea, ga, why = work.popleft()
            while inr(ea) and inr(ga):
                if ea in code:
                    if code[ea] != ga:
                        conflicts.append((ea, code[ea], ga, why))
                    break
                ie, ig = Z.decode(E, ea), Z.decode(G, ga)
                if not ie.valid or not ig.valid or ie.length != ig.length or shape(ie) != shape(ig) or ie.flow != ig.flow or ie.inline != ig.inline:
                    diverge.append((ea, ga, ie.fmt if ie.valid else "?", ig.fmt if ig.valid else "?", why))
                    break
                code[ea] = ga
                inv[ga] = ea
                nxe, nxg = ea + ie.length, ga + ig.length
                if ie.target is not None:
                    push(ie.target, ig.target, f"jr@{ea:04X}")
                elif ie.addr is not None:
                    if ie.addr_kind in ("call", "jp"):
                        push(ie.addr, ig.addr, f"{ie.addr_kind}@{ea:04X}")
                        if ie.addr_kind == "call" and ie.addr in inline_e:
                            inline_g[ig.addr] = inline_e[ie.addr]
                    elif ie.addr_kind == "ld":
                        data.setdefault(ie.addr, set()).add(ig.addr)
                if ie.inline:
                    nxe += ie.inline
                    nxg += ig.inline
                elif ie.addr_kind == "call" and ie.addr in inline_e:
                    nxe += inline_e[ie.addr]
                    nxg += inline_e[ie.addr]
                if ie.flow in ("jump", "stop"):
                    break
                ea, ga = nxe, nxg
        # seed unmapped English code labels by fingerprint search in the French binary
        rounds += 1
        added = 0
        ecode_labels = sorted(a for a in labels if a in einsn and a not in code and inr(a))
        for ea in ecode_labels:
            fp = []
            pc = ea
            for _ in range(10):
                i = Z.decode(E, pc)
                if not i.valid:
                    break
                fp.append((i.length, shape(i), i.flow))
                pc += i.length
                if i.flow in ("jump", "stop"):
                    break
            if len(fp) < 4:
                continue
            hits = []
            for lo, hi in ranges:
                if not lo <= ea < hi:
                    continue
                for ga in range(lo, hi):
                    if ga in inv:
                        continue
                    pc, ok = ga, True
                    for fl, ff, fw in fp:
                        i = Z.decode(G, pc)
                        if not i.valid or (i.length, shape(i), i.flow) != (fl, ff, fw):
                            ok = False
                            break
                        pc += i.length
                    if ok:
                        hits.append(ga)
                        if len(hits) > 1:
                            break
            if len(hits) == 1:
                push(ea, hits[0], f"fp@{ea:04X}")
                added += 1
        if not work or rounds > 6:
            break
    mapped = sum(Z.decode(E, a).length for a in code)
    total = sum(Z.decode(E, a).length for a in einsn if inr(a))
    print(f"mapped instructions {len(code)} ({mapped} bytes of {total} English code bytes); conflicts {len(conflicts)}; divergences {len(diverge)}; rounds {rounds}")
    unm = sorted(a for a in einsn if a not in code and inr(a))
    runs = []
    for a in unm:
        n = Z.decode(E, a).length
        if runs and a == runs[-1][1]:
            runs[-1][1] = a + n
        else:
            runs.append([a, a + n])
    print(f"unmapped English code: {len(runs)} runs, {sum(b - a for a, b in runs)} bytes")
    for a, b in sorted(runs, key=lambda r: r[0] - r[1])[:30]:
        print(f"   {a:04X}-{b:04X} {b - a:4}  {(labels.get(a) or [''])[0]}")
    OUT.write_text(json.dumps({"code": {f"{a:04X}": f"{g:04X}" for a, g in sorted(code.items())},
                               "data": {f"{a:04X}": sorted(f"{g:04X}" for g in s) for a, s in sorted(data.items())},
                               "diverge": [[f"{a:04X}", f"{b:04X}", c, d, e] for a, b, c, d, e in diverge],
                               "conflicts": [[f"{a:04X}", f"{b:04X}", f"{c:04X}", d] for a, b, c, d in conflicts],
                               f"inline_{LANG}": [f"{a:04X}" for a in sorted(inline_g)]}, indent=0))


main()

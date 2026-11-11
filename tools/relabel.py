#!/usr/bin/env python3
"""Turn `db` runs of a hand-edited source tree into labelled instructions, using a freshly regenerated reference (tools/disasm_stock.py, with the fixed decoder).

usage: python3 -I tools/relabel.py TARGET.asm REFERENCE.asm [--range LO HI] [--write]
  TARGET     the tree to improve (e.g. src/elite128/commonxx.asm); never regenerated, only edited here
  REFERENCE  a disassembly of the same stock bytes (work/elite128/dis_dyn/commonxx.asm); its addresses must equal the target's in the range
  --range    only runs inside LO..HI (hex) are touched (default 1A40 8FC6: the stock code, before the 128K blueprint data and glue)
Without --write the changes are only counted. The target must assemble with no flags and with -DENHANCED -DTITLESEL -DMISSIONS to the same bytes before and after; this script checks that
itself (it assembles both variants before editing and again after writing, and restores the original file when they differ).

What it does: a run of consecutive `db` lines outside any IF block whose bytes the reference decodes as a tiling of whole instructions is replaced by those instructions; operand
names are mapped by address to the target's own label names; addresses without a target label get one (a label line, a split db line, or `name equ instruction_label+k` when the
address falls inside an instruction, as the self-modified operands do). Everything else (data, runs the reference does not tile) stays as it is.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SJ = str(Path.home() / ".local/bin/sjasmplus")
VARIANTS = [[], ["-DENHANCED", "-DTITLESEL", "-DMISSIONS"]]


def assemble(path, flags, tmp):
    out, sym, lst = (Path(tmp) / n for n in ("o.bin", "o.sym", "o.lst"))
    r = subprocess.run([SJ, *flags, f"--raw={out}", f"--sym={sym}", f"--lst={lst}", str(path)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"assemble failed ({path} {flags}):\n{r.stdout[-900:]}{r.stderr[-300:]}")
    return out.read_bytes(), sym.read_text(), lst.read_text(errors="replace")


def parse_sym(text):
    d = {}
    for l in text.splitlines():
        p = l.split()
        if len(p) >= 3 and p[1] == "EQU":
            d.setdefault(p[0].rstrip(":"), int(p[2], 16))
    return d


ROW = re.compile(r"^\s*(\d+)(\+*)\s+([0-9A-F]{4})\s+((?:[0-9A-F]{2}\s?)+)\s+(\S.*)$")


def lst_rows(text, base_main=True):
    """(source line number, address, byte count shown, source text) for the main file's rows that emit bytes (byte lists are cut at 4 bytes by sjasmplus; used for the start address only)."""
    out = []
    for l in text.splitlines():
        m = ROW.match(l)
        if m and re.fullmatch(r"(?:[0-9A-F]{2}\s*)+", m.group(5).strip()):
            continue                              # a continuation row of a long db: the byte regex swallowed all but the last byte pair
        if m and (not m.group(2)):
            out.append((int(m.group(1)), int(m.group(3), 16), len(m.group(4).split()), m.group(5)))
    return out


def main():
    args = sys.argv[1:]
    target, reference = Path(args[0]), Path(args[1])
    lo, hi, write = 0x1A40, 0x8FC6, "--write" in args
    if "--range" in args:
        i = args.index("--range")
        lo, hi = int(args[i + 1], 16), int(args[i + 2], 16)
    src = target.read_text().split("\n")
    with tempfile.TemporaryDirectory() as tmp:
        t0 = [assemble(target, v, tmp)[0] for v in VARIANTS]
        tbin, tsym_text, tlst = assemble(target, [], tmp)
        rbin, rsym_text, rlst = assemble(reference, [], tmp)
    tsym, rsym = parse_sym(tsym_text), parse_sym(rsym_text)
    base = 0x1A40 if "commonxx" in target.name else 0x0840 if "largeaxx" in target.name else 0xC000 if "common2x" in target.name else 0x6000
    if rbin != tbin[:len(rbin)] and rbin[:0x7000] != tbin[:0x7000]:
        pass
    taddr_name = {}
    for n, a in tsym.items():
        taddr_name.setdefault(a, n)
    # reference instruction table: address -> (length, text)
    rrows = lst_rows(rlst)
    rins = {}
    for ln, a, n, text in rrows:
        t = text.split(";")[0].strip()
        if re.match(r"(db|dw|ds|dup|edup|org)\b", t.lower()) or t.endswith(":"):
            continue
        rins[a] = (None, t)
    # instruction lengths: next row start (rows are consecutive in the reference)
    addrs = sorted(rins)
    cover_end = {}
    for i, a in enumerate(addrs):
        nxt = addrs[i + 1] if i + 1 < len(addrs) else None
        cover_end[a] = nxt
    rlabels = {}                                   # address -> [reference label names]
    for n, a in rsym.items():
        rlabels.setdefault(a, []).append(n)

    # target db runs outside IF blocks
    trows = {ln: (a, n) for ln, a, n, text in lst_rows(tlst)}
    depth, runs, cur = 0, [], None
    for idx, line in enumerate(src):
        t = line.split(";")[0].strip().lower()
        if re.match(r"(if|ifdef|ifndef|ifn)\b", t):
            depth += 1
        elif t.startswith("endif"):
            depth -= 1
        if depth == 0 and re.match(r"db\b", t) and (idx + 1) in trows:
            a, n = trows[idx + 1]
            if cur and cur[2] == idx - 1 and True:
                cur[2] = idx
                cur[1] = a  # placeholder, fixed below
                cur[3].append((idx, a))
            else:
                if cur:
                    runs.append(cur)
                cur = [idx, a, idx, [(idx, a)]]
        else:
            if cur:
                runs.append(cur)
                cur = None
    if cur:
        runs.append(cur)
    # the byte length of a db line: from the next row's address inside the run, or the run's end = start of the following emitting row
    emit_rows = sorted(trows.values())
    start_after = {}
    for i, (a, n) in enumerate(emit_rows):
        pass
    all_addr = sorted(a for a, n in trows.values())

    def next_addr(a):
        import bisect
        i = bisect.bisect_right(all_addr, a)
        return all_addr[i] if i < len(all_addr) else None

    plans, skipped = [], 0
    for first, _, last, lines in runs:
        a = lines[0][1]
        end = next_addr(lines[-1][1])
        if end is None or a < lo or end - 1 > hi:
            continue
        # does the reference tile [a, end) with whole instructions?
        pos, seq = a, []
        while pos < end:
            if pos not in rins:
                break
            nxt = cover_end[pos]
            if nxt is None or nxt > end:
                break
            seq.append(pos)
            pos = nxt
        if not seq or pos != end:
            skipped += 1
            continue
        plans.append((first, last, a, end, seq))
    print(f"{len(runs)} db runs outside IF blocks in range, {len(plans)} tile as instructions in the reference, {skipped} do not")
    new_labels = {}
    out_src = list(src)
    repl = {}
    for first, last, a, end, seq in plans:
        lines = []
        for pos in seq:
            if pos != a:
                for name in rlabels.get(pos, [])[:1]:
                    if pos not in taddr_name:
                        lines.append(f"{name}:")
                        taddr_name[pos] = name
                        tsym[name] = pos
            text = rins[pos][1]

            def sub(m):
                tok = m.group(0)
                if tok in rsym:
                    ad = rsym[tok]
                    if ad in taddr_name:
                        return taddr_name[ad]
                    new_labels[ad] = tok
                    return tok
                return tok
            text = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", lambda m: sub(m) if m.group(0).lower() not in ("a", "b", "c", "d", "e", "h", "l", "af", "bc", "de", "hl", "sp", "ix", "iy", "ixh", "ixl", "iyh", "iyl", "nz", "z", "nc", "po", "pe", "p", "m", "r", "i", "af'") and not re.match(r"^(ld|add|adc|sub|sbc|and|or|xor|cp|inc|dec|jp|jr|call|djnz|ret|push|pop|ex|exx|bit|set|res|rl|rr|rlc|rrc|sla|sra|srl|rst|di|ei|nop|halt|neg|cpl|scf|ccf|daa|ldi|ldir|ldd|lddr|cpi|cpir|in|out|im|reti|retn|rld|rrd|rlca|rrca|rla|rra|outi|otir)$", m.group(0).lower()) else m.group(0), text)
            lines.append("    " + text)
        repl[first] = (last, lines)
    unresolved = {ad: n for ad, n in new_labels.items() if ad not in taddr_name}
    print(f"operands needing a label the target does not have: {len(unresolved)}")
    if not write:
        for ad, n in sorted(unresolved.items())[:20]:
            print(f"  &{ad:04X} {n}")
        return
    # labels for the unresolved operand addresses: before an instruction/db line that starts there, inside a db line by splitting it, or as an equate when inside an instruction
    line_start = {}                                  # source index -> address, for target lines that emit bytes
    for ln, (a, n) in trows.items():
        line_start[ln - 1] = a
    order = sorted(line_start)
    inserts = {}                                     # source index -> lines to put before it
    splits = {}                                      # source index -> (address, label): split the db line there
    for ad, name in sorted(unresolved.items()):
        cand = [i for i in order if line_start[i] <= ad]
        if not cand:
            raise SystemExit(f"no target line for &{ad:04X}")
        i = cand[-1]
        if i in repl or any(f <= i <= l for f, (l, _) in repl.items()):
            raise SystemExit(f"&{ad:04X} ({name}) falls into a replaced run: handle by hand")
        nxt = next_addr(line_start[i])
        text = src[i].split(";")[0].strip().lower()
        if line_start[i] == ad:
            inserts.setdefault(i, []).append(f"{name}:")
        elif re.match(r"db\b", text) and nxt and ad < nxt:
            splits.setdefault(i, []).append((ad, name))
        else:
            # inside an instruction: label at its start (if it has none) and an equate
            lab = taddr_name.get(line_start[i]) or f"loc_{line_start[i]:04X}"
            if line_start[i] not in taddr_name:
                inserts.setdefault(i, []).append(f"{lab}:")
            inserts.setdefault(i + 1, []).append(f"{name} equ {lab} + {ad - line_start[i]}   ; inside the instruction at &{line_start[i]:04X}")
    out = []
    i = 0
    while i < len(src):
        for l in inserts.get(i, []):
            out.append(l)
        if i in repl:
            last, lines = repl[i]
            out.extend(lines)
            i = last + 1
            continue
        if i in splits:
            a0 = line_start[i]
            n0 = next_addr(a0)
            cuts = sorted(splits[i])
            pos = a0
            for ad, name in cuts + [(n0, None)]:
                chunk = tbin[pos - base:ad - base]
                if chunk:
                    out.append("    db " + ",".join("0x%02X" % b for b in chunk))
                if name:
                    out.append(f"{name}:")
                pos = ad
            i += 1
            continue
        out.append(src[i])
        i += 1
    backup = target.with_suffix(target.suffix + ".relabel_bak")
    backup.write_text("\n".join(src))
    target.write_text("\n".join(out))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            t1 = [assemble(target, v, tmp)[0] for v in VARIANTS]
        except SystemExit as e:
            (ROOT / "work/elite128/relo/relabel_failed.asm").write_text("\n".join(out))
            target.write_text("\n".join(src))
            raise SystemExit(f"assembly failed after the edit, target restored (the edited text is in work/elite128/relo/relabel_failed.asm):\n{e}")
    if t1 != t0:
        target.write_text("\n".join(src))
        raise SystemExit("the edited tree no longer assembles to the same bytes: target restored")
    backup.unlink()
    print(f"written: {len(plans)} runs replaced, {len(unresolved)} labels added; both variants assemble to the same bytes as before")


if __name__ == "__main__":
    main()

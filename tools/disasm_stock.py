#!/usr/bin/env python3
"""Disassemble the stock Elite CPC binaries into sjasmplus source and verify the round trip.

usage: disasm_stock.py OUTDIR [--force]        (OUTDIR is required; src/ is refused without --force: src/elite is hand-edited)

Inputs (all produced earlier in this project):
  work/stock_bin/*.BIN, work/bin_stock/*.BIN   stock binaries, header stripped (tools/dskx.py)
  work/fessor_to_stock.sym                     Fessor's label names at stock addresses (tools/map_labels.py)
  work/build_fessor/EliteMasterSource.asm      only used to tell which labels sit on code and which on data
Method: recursive descent from labelled code and the game entry; calls to routines that take inline
bytes (printStringFollowingByte etc.) skip those bytes. Everything not reached is data. Every file is
assembled with sjasmplus and compared byte for byte with the original; a mismatch is an error.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import z80dis as Z   # noqa: E402

SJASM = Path.home() / ".local" / "bin" / "sjasmplus"
FILES = [  # name, load address, stock file, extra seeds
    ("largeaxx", 0x0840, "LARGEAXX.BIN", []),
    ("commonxx", 0x1A40, "COMMONXX.BIN", [0x1C82]),
    ("common2x", 0xC000, "COMMON2X.BIN", []),
    ("musiquex", 0x6000, "MUSIQUEX.BIN", [0x6000]),
]   # NOTMUSIC.BIN is byte-identical to commonxx 0x6000-0x6FFF, so it gets no file of its own
INLINE_CALLEES = {"printstringfollowingbyte", "printfollowingtokenwithspace", "todo_printroutinew"}
MNEM = set("ADC ADD AND BIT CALL CCF CP CPD CPDR CPI CPIR CPL DAA DEC DI DJNZ EI EX EXX HALT IM IN INC IND INDR "
           "INI INIR JP JR LD LDD LDDR LDI LDIR NEG NOP OR OTDR OTIR OUT OUTD OUTI POP PUSH RES RET RETI RETN RL "
           "RLA RLC RLCA RLD RR RRA RRC RRCA RRD RST SBC SCF SET SLA SRA SRL SUB XOR".split())
DIRS = {"DB", "DW", "DS", "DEFB", "DEFW", "DEFS", "DM", "BYTE", "WORD"}
SKIP = {"IF", "IFNOT", "ELSE", "ENDIF", "PRINT", "INCLUDE", "ORG", "SAVE", "PROTECT", "READ", "MACRO", "MEND",
        "NOLIST", "LIST", "ASSERT", "BANK", "LIMIT", "WRITE", "UNDEF", "IFDEF", "IFNDEF"}
RESERVED = {"a", "b", "c", "d", "e", "h", "l", "af", "bc", "de", "hl", "sp", "ix", "iy", "nz", "z", "nc", "po", "pe",
            "p", "m", "r", "i", "end", "map", "init", "page", "org", "equ", "struct", "module", "device", "align",
            "dup", "edup", "display", "define", "output", "if", "else", "endif", "macro", "endm", "include",
            "incbin", "block", "defs", "defb", "defw", "byte", "word", "ds", "db", "dw", "dm", "disp", "ent",
            "slot", "size", "export", "label", "dot", "text", "abyte", "dz", "lua", "endlua", "phase",
            "dephase", "unphase", "shellexec", "opt", "pop", "push", "rst", "ret", "set", "res", "sub", "and",
            "or", "xor", "cp", "in", "out", "ex", "jp", "jr", "ld", "inc", "dec", "add", "adc", "sbc", "bit",
            "halt", "nop", "im", "di", "ei", "neg", "cpl", "daa", "ccf", "scf", "call", "exx", "rl", "rr"}


def load_names(sym_path):
    names, tags = {}, {}
    for line in Path(sym_path).read_text().splitlines():
        m = re.match(r"(\w+) equ #([0-9A-Fa-f]+) ; (\S+)", line)
        if m and int(m.group(2), 16) not in names:
            a = int(m.group(2), 16)
            names[a], tags[a] = m.group(1), m.group(3)
    return names, tags


def fessor_kinds(path):
    """label (lowercase) -> 'code' | 'data' from how Fessor's source continues after the label."""
    kinds, pending = {}, []
    for raw in Path(path).read_text(encoding="latin1").splitlines():
        t = raw.split(";")[0].rstrip()
        if not t.strip():
            continue
        tok = t.strip().split()[0].rstrip(":")
        up = tok.upper()
        indented = raw[:1] in " \t"
        if up in SKIP or t.strip().startswith(("#", ".")) or "=" in t or " equ " in t.lower():
            continue
        if up in MNEM and (indented or t.strip().split()[0].upper() in MNEM):
            for l in pending:
                kinds[l.lower()] = "code"
            pending = []
        elif up in DIRS:
            for l in pending:
                kinds[l.lower()] = "data"
            pending = []
        elif re.fullmatch(r"[A-Za-z_]\w*", tok) and not indented:
            pending.append(tok)
    return kinds


class FileDis:
    def __init__(self, name, base, data, seeds, data_addrs=()):
        self.name, self.base, self.data = name, base, data
        self.data_addrs = set(data_addrs)      # labels that Fessor's source puts on data: never decode there
        self.end = base + len(data)
        self.mem = bytearray(65536 + 8)
        self.mem[base:self.end] = data
        self.insn = {}          # start address -> Insn
        self.inline = {}        # address of inline data -> byte count
        self.covered = {}       # address -> start of the item covering it
        self.jtargets, self.ctargets, self.drefs = set(), set(), set()
        self.seeds = set(seeds)
        self.work = [s for s in seeds if base <= s < self.end]

    def inrange(self, a):
        return self.base <= a < self.end

    def run(self, inline_callees):
        while self.work:
            pc = self.work.pop()
            while self.inrange(pc) and pc not in self.insn:
                if pc in self.covered:           # lands inside another instruction
                    break
                if pc in self.data_addrs and pc not in self.seeds:
                    break                        # ran into a data label
                i = Z.decode(self.mem, pc)
                if not i.valid or pc + i.length > self.end:
                    break
                if any(p in self.covered for p in range(pc, pc + i.length)):
                    break
                self.insn[pc] = i
                for p in range(pc, pc + i.length):
                    self.covered[p] = pc
                nxt = pc + i.length
                tgt = i.target if i.target is not None else (i.addr if i.addr_kind in ("call", "jp") else None)
                if tgt is not None and self.inrange(tgt):
                    (self.ctargets if i.flow == "call" or i.addr_kind == "call" else self.jtargets).add(tgt)
                    self.work.append(tgt)
                elif i.addr_kind == "ld" and i.addr is not None and self.inrange(i.addr):
                    self.drefs.add(i.addr)
                if i.inline:
                    for p in range(nxt, min(nxt + i.inline, self.end)):
                        self.covered[p] = nxt
                    self.inline[nxt] = i.inline
                    nxt += i.inline
                    if i.fmt in ("rst 0x08", "rst 0x28"):
                        break                   # LOW JUMP / FIRM JUMP never return
                elif i.addr_kind == "call" and i.addr in inline_callees:
                    n = inline_callees[i.addr]
                    for p in range(nxt, min(nxt + n, self.end)):
                        self.covered[p] = nxt
                    self.inline[nxt] = n
                    nxt += n
                if i.flow in ("jump", "stop"):
                    break
                pc = nxt


def _scan_methods():
    def clean_start(self, a, minimum=6):
        """True if a plausible instruction sequence starts at a (no data-looking opcodes)."""
        if a in self.data_addrs:
            return False
        seen, pc, nops = 0, a, 0
        while seen < 40:
            if not self.inrange(pc) or pc in self.covered or (seen and pc in self.data_addrs):
                return seen >= minimum
            i = Z.decode(self.mem, pc)
            if not i.valid or pc + i.length > self.end:
                return False
            if i.fmt in ("halt", "rst 0x38", "rst 0x30") or i.fmt.startswith(("ld b,b", "ld c,c")):
                return False
            nops = nops + 1 if i.fmt == "nop" else 0
            if nops >= 3:
                return False
            seen += 1
            if i.inline:
                pc += i.length + i.inline
            else:
                pc += i.length
            if i.flow in ("jump", "stop"):
                return seen >= minimum
        return True

    def scan(self):
        """New code seeds: ld-immediate addresses and runs of 3+ words that point at plausible code."""
        new = set()
        for a in self.drefs:
            if a not in self.covered and self.inrange(a) and self.clean_start(a):
                new.add(a)
        w = lambda p: self.mem[p] | self.mem[p + 1] << 8
        p = self.base
        while p < self.end - 1:
            if p in self.covered:
                p += 1
                continue
            run = []
            q = p
            while q < self.end - 1 and q not in self.covered and q + 1 not in self.covered:
                t = w(q)
                if self.inrange(t) and t not in self.covered and t not in self.insn and self.clean_start(t):
                    run.append(t)
                    q += 2
                else:
                    break
            if len(run) >= 3:
                new.update(run)
                p = q
            else:
                p += 1
        return new

    return clean_start, scan


FileDis.clean_start, FileDis.scan = _scan_methods()


def esc_data(bs):
    """db operands: runs of printable ASCII as strings, other bytes as hex."""
    parts, run = [], ""
    for v in bs:
        if 0x20 <= v < 0x7F and v not in (0x22, 0x5C):
            run += chr(v)
        else:
            if run:
                parts.append('"%s"' % run)
                run = ""
            parts.append("0x%02X" % v)
    if run:
        parts.append('"%s"' % run)
    return ",".join(parts)


def safe(n):
    n = re.sub(r"\W", "_", n)
    if n[0].isdigit():
        n = "_" + n
    return n + "_" if n.lower() in RESERVED else n


def generate(fd, names, tags, kinds, case_names, ext_names, outdir, variants=None):
    variants = variants or {}
    base, end = fd.base, fd.end
    # label table for this file: address -> name
    labels = {}
    used = set()

    def claim(a, nm):
        nm = safe(nm)
        k = nm
        i = 2
        while k.lower() in used:
            k = f"{nm}_{i}"
            i += 1
        used.add(k.lower())
        labels[a] = k

    for a in sorted(names):
        if fd.base <= a < fd.end and tags[a] != "delta" and a not in labels:
            claim(a, case_names.get(names[a].lower(), names[a]))
    # generated labels for referenced addresses
    for a in sorted(fd.ctargets):
        if a not in labels:
            claim(a, "sub_%04X" % a)
    for a in sorted(fd.jtargets):
        if a not in labels:
            claim(a, "loc_%04X" % a)
    data_at = lambda a: a not in fd.covered
    for a in sorted(fd.drefs):
        if a not in labels and (data_at(a) or a in fd.insn):
            claim(a, "dat_%04X" % a)
    # labels that fall inside an instruction become numeric equates (self-modifying code entry points)
    mid = {a: n for a, n in labels.items() if a in fd.covered and fd.covered[a] != a and a not in fd.inline}
    for a in mid:
        del labels[a]
    # labels at inline-data addresses stay (they split the data)
    lines = [f"; Elite (Amstrad CPC) {fd.name.upper()}.BIN, stock build: generated by tools/disasm_stock.py",
             f"; load address 0x{base:04X}, {len(fd.data)} bytes. Names come from Fessor's reconstruction where known,",
             "; otherwise sub_ (call target), loc_ (jump target), dat_ (data/variable reference).", ""]
    ext_used = {}

    def operand(i, kind):
        if kind == "R":
            return ref(i.target)
        a = i.addr
        if i.addr_kind in ("call", "jp"):
            return ref(a)
        if fd.inrange(a):
            if a in labels:
                return labels[a]
            if a in mid:
                return "0x%04X" % a
            return "0x%04X" % a
        nm = ext_names.get(a)
        if nm and "(" in i.fmt:             # memory operand outside the file: name it
            ext_used[a] = nm
            return nm
        return "0x%04X" % a

    def ref(t):
        if fd.inrange(t):
            return labels.get(t, "0x%04X" % t)
        nm = ext_names.get(t)
        if nm:
            ext_used[t] = nm
            return nm
        return "0x%04X" % t

    body = [f" org 0x{base:04X}", ""]
    pc = base
    while pc < end:
        if pc in labels:
            body.append(f"{labels[pc]}:")
        if pc in fd.insn:
            i = fd.insn[pc]
            t = i.fmt
            if "{A}" in t:
                t = t.replace("{A}", operand(i, "A"))
            if "{R}" in t:
                t = t.replace("{R}", operand(i, "R"))
            hit = [a for a in variants if pc <= a < pc + i.length]
            if hit:                     # the Firebird disk differs here: assemble either build
                alt = bytearray(fd.data[pc - base:pc - base + i.length])
                for a in hit:
                    alt[a - pc] = variants[a]
                body += ["    IFDEF FIREBIRD", f"    db {', '.join('0x%02X' % v for v in alt)}   ; {t} in the Gold build",
                         "    ELSE", f"    {t}", "    ENDIF"]
            else:
                body.append(f"    {t}")
            pc += i.length
            continue
        # data run up to the next label / code start
        stop = pc + 1
        n = fd.inline.get(pc)
        while stop < end and stop not in labels and stop not in fd.insn and stop - pc < (n or 16) \
                and stop not in fd.inline and not (n is None and stop in mid):
            stop += 1
        chunk = fd.data[pc - base:stop - base]
        assert not any(pc <= a < stop for a in variants), "Firebird difference inside data: handle it"
        # break text lines after a terminating zero so string tables stay one entry per line
        z = chunk.find(b"\x00")
        if 0 <= z < len(chunk) - 1 and any(0x30 <= c <= 0x5A for c in chunk[:z]):
            stop = pc + z + 1
            chunk = chunk[:z + 1]
        body.append(f"    db {esc_data(chunk)}")
        pc = stop
    for a, n in sorted(mid.items()):
        body.append(f"{safe(n)} equ 0x{a:04X}   ; inside the instruction at 0x{fd.covered[a]:04X} (patched or jumped into)")
    if ext_used:
        lines.append("; names of addresses in the other binaries")
        for a, n in sorted(ext_used.items()):
            lines.append(f"{n} equ 0x{a:04X}")
        lines.append("")
    path = Path(outdir) / f"{fd.name}.asm"
    path.write_text("\n".join(lines + body) + "\n")
    return path


def verify(path, expected, define=None):
    raw = path.with_suffix(".bin.tmp")
    cmd = [str(SJASM), f"--raw={raw}"] + ([f"-D{define}"] if define else []) + [str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    errs = [l for l in (r.stdout + r.stderr).splitlines() if "error" in l.lower() and "Errors:" not in l
            and "complete" not in l]
    got = raw.read_bytes() if raw.exists() else b""
    raw.unlink(missing_ok=True)
    return got == expected, errs[:5]


def main(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    work = ROOT / "work"
    names, tags = load_names(work / "fessor_to_stock.sym")
    main_src = work / "build_fessor" / "EliteMasterSource.asm"
    kinds = fessor_kinds(main_src)
    case_names = {}
    for src in (main_src, work / "build_fessor" / "musiquep.asm"):
        for raw in src.read_text(encoding="latin1").splitlines():
            m = re.match(r"([A-Za-z_]\w*)\s*$", raw.split(";")[0].rstrip())
            if m:
                case_names.setdefault(m.group(1).lower(), m.group(1))
    inline_callees = {a: 1 for a, n in names.items() if n.lower() in INLINE_CALLEES}
    code_names = {a for a, n in names.items() if kinds.get(n.lower()) == "code" and tags[a] != "delta"}
    ok_all = True
    for name, base, fname, extra in FILES:
        data = (work / "bin_stock" / fname).read_bytes()
        end = base + len(data)
        if name == "musiquex":
            nm, tg = load_names(work / "musiquex.sym")
            kd = {n.lower(): ("code" if n.upper().startswith(("SUB_", "LAB_")) or n.lower() == "musiceventroutine"
                              else "data") for n in nm.values()}
            seeds = list(extra) + [a for a, n in nm.items() if kd[n.lower()] == "code"]
            ext = {}
        else:
            nm, tg = names, tags
            seeds = list(extra) + sorted(a for a in code_names if base <= a < end)
            ext = {a: safe(case_names.get(n.lower(), n)) for a, n in names.items()
                   if not (base <= a < end) and tags[a] != "delta"}
        fb_path = work / "bin_fb_EliteFirebirdSoftwaredsk" / fname
        fb = fb_path.read_bytes() if fb_path.exists() else data
        variants = {base + k: fb[k] for k in range(len(data)) if fb[k] != data[k]} if len(fb) == len(data) else {}
        data_addrs = {a for a, n in nm.items() if base <= a < end and (kd if name == 'musiquex' else kinds).get(n.lower()) == 'data'}
        fd = FileDis(name, base, data, seeds, data_addrs)
        fd.run(inline_callees)
        rounds = 0
        while True:                         # pointer tables / ld-immediates that reveal more code
            new = {a for a in fd.scan() if a not in fd.insn}
            if not new or rounds > 20:
                break
            fd.work = sorted(new)
            fd.run(inline_callees)
            rounds += 1
        path = generate(fd, nm, tg, kinds, case_names, ext, outdir, variants)
        same, errs = verify(path, data)
        if variants:
            same_fb, errs_fb = verify(path, fb, "FIREBIRD")
            errs += errs_fb
            same = same and same_fb
        code = sum(i.length for i in fd.insn.values())
        print(f"{name:9} {len(data):6} bytes  code {code:6} ({100 * code // len(data)}%)  insns {len(fd.insn):5}  "
              f"labels {sum(1 for a in nm if base <= a < end):4}  scan rounds {rounds}  "
              f"round trip {'IDENTICAL' if same else 'MISMATCH'}"
              + (f" (Gold and Firebird, {len(variants)} byte differs)" if variants else ""))
        for e in errs:
            print("    ", e)
        ok_all &= same
    return 0 if ok_all else 1


def outdir_arg(usage):
    """The OUTDIR argument. It is required, and a directory inside src/ is refused unless --force is given: src/elite*
    are hand-edited, and a regeneration overwrites every name, comment and flag block in them."""
    args = [a for a in sys.argv[1:] if a != "--force"]
    if len(args) != 1:
        sys.exit(usage + "\nOUTDIR is required; use a scratch directory (src/elite* are hand-edited), or --force to write into src/")
    out = Path(args[0]).resolve()
    if (ROOT / "src") in (out, *out.parents) and "--force" not in sys.argv:
        sys.exit(f"{args[0]} is inside src/, which holds hand-edited sources; pass --force to overwrite them")
    return out


if __name__ == "__main__":
    sys.exit(main(outdir_arg("usage: disasm_stock.py OUTDIR [--force]")))

#!/usr/bin/env python3
"""Table-driven Z80 instruction decoder for sjasmplus-style source.

decode(mem, pc) -> Insn. Only standard encodings (plus IXH/IXL forms) are decoded; any other byte
sequence comes back with .valid False, so the caller can emit it as data. The source text is built
from .fmt, where {A} stands for a 16-bit address/immediate operand and {R} for a relative jump
target; both are filled in by the caller so that labels can replace numbers.
"""
from dataclasses import dataclass
from typing import Optional

R8 = ["b", "c", "d", "e", "h", "l", "(hl)", "a"]
RP = ["bc", "de", "hl", "sp"]
RP2 = ["bc", "de", "hl", "af"]
CC = ["nz", "z", "nc", "c", "po", "pe", "p", "m"]
ALU = ["add a,", "adc a,", "sub ", "sbc a,", "and ", "xor ", "or ", "cp "]
ROT = ["rlc", "rrc", "rl", "rr", "sla", "sra", "sll", "srl"]
BLI = [["ldi", "cpi", "ini", "outi"], ["ldd", "cpd", "ind", "outd"],
       ["ldir", "cpir", "inir", "otir"], ["lddr", "cpdr", "indr", "otdr"]]


@dataclass
class Insn:
    length: int
    fmt: str                      # text with optional {A} / {R} placeholders
    valid: bool = True
    addr: Optional[int] = None    # value of the {A} operand
    addr_kind: str = ""           # "call", "jp", "ld" (any other 16-bit operand)
    target: Optional[int] = None  # absolute target of a relative jump ({R})
    flow: str = "seq"             # seq, jump, cjump, call, ret, stop
    inline: int = 0               # bytes of inline data after a rst that takes a word


def _bad(n=1):
    return Insn(n, "", valid=False)


def _hex8(v):
    return "0x%02X" % (v & 0xFF)


def _disp(d):
    d = d - 256 if d > 127 else d
    return "+%d" % d if d >= 0 else "%d" % d


def decode(mem, pc):
    b = lambda i: mem[(pc + i) & 0xFFFF]
    op = b(0)
    if op == 0xCB:
        return _cb(b(1))
    if op == 0xED:
        return _ed(b, pc)
    if op in (0xDD, 0xFD):
        return _idx(b, pc, "ix" if op == 0xDD else "iy")
    return _base(b, pc, op)


def _base(b, pc, op, ix=None, extra=0):
    """Unprefixed opcode. With ix set, (hl) becomes (ix+d) and h/l become ixh/ixl where legal."""
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    p, q = y >> 1, y & 1

    def reg(i, mem_ok=True):
        if i == 6:
            return "(%s%s)" % (ix, _disp(b(1 + extra))) if ix else "(hl)"
        if ix and i in (4, 5):
            return ix + ("h" if i == 4 else "l")
        return R8[i]

    ln = 1 + extra          # prefix byte(s) already counted in extra
    # An index prefix only changes instructions that mention (hl), h, l or hl.
    uses_hl = False
    if x == 0:
        if z == 1:
            uses_hl = q == 1 or p == 2
        elif z in (2, 3):
            uses_hl = p == 2
        elif z in (4, 5, 6):
            uses_hl = y in (4, 5, 6)
    elif x == 1:
        uses_hl = (y in (4, 5, 6) or z in (4, 5, 6)) and not (y == 6 and z == 6)
    elif x == 2:
        uses_hl = z in (4, 5, 6)
    elif x == 3:
        if z == 1:
            uses_hl = (q == 0 and p == 2) or (q == 1 and p in (2, 3))
        elif z == 3:
            uses_hl = y in (4,)
        elif z == 5:
            uses_hl = q == 0 and p == 2     # push ix / push iy (this case was missing: every push ix/iy came back invalid and stayed a db run)
    if ix and not uses_hl:
        return _bad(1)          # prefix has no effect: caller emits the prefix as data

    if x == 0:
        if z == 0:
            if y == 0:
                return Insn(ln, "nop")
            if y == 1:
                return Insn(ln, "ex af,af'")
            tgt = (pc + extra + 2 + (b(1 + extra) - 256 if b(1 + extra) > 127 else b(1 + extra))) & 0xFFFF
            if y == 2:
                return Insn(ln + 1, "djnz {R}", target=tgt, flow="cjump")
            if y == 3:
                return Insn(ln + 1, "jr {R}", target=tgt, flow="jump")
            return Insn(ln + 1, "jr %s,{R}" % CC[y - 4], target=tgt, flow="cjump")
        if z == 1:
            rp = (ix or "hl") if p == 2 else RP[p]
            if q == 0:
                v = b(1 + extra) | b(2 + extra) << 8
                return Insn(ln + 2, "ld %s,{A}" % rp, addr=v, addr_kind="ld")
            return Insn(ln, "add %s,%s" % (ix or "hl", rp))
        if z == 2:
            if p < 2:
                s = "(%s)" % RP[p]
                return Insn(ln, ("ld %s,a" % s) if q == 0 else ("ld a,%s" % s))
            v = b(1 + extra) | b(2 + extra) << 8
            r = (ix or "hl") if p == 2 else "a"
            return Insn(ln + 2, ("ld ({A}),%s" % r) if q == 0 else ("ld %s,({A})" % r), addr=v, addr_kind="ld")
        if z == 3:
            rp = (ix or "hl") if p == 2 else RP[p]
            return Insn(ln, ("inc %s" if q == 0 else "dec %s") % rp)
        if z in (4, 5):
            n = ln + (1 if ix and y == 6 else 0)
            return Insn(n, ("inc %s" if z == 4 else "dec %s") % reg(y))
        if z == 6:
            if ix and y == 6:
                return Insn(ln + 2, "ld (%s%s),%s" % (ix, _disp(b(1 + extra)), _hex8(b(2 + extra))))
            n = ln + 1
            return Insn(n, "ld %s,%s" % (reg(y), _hex8(b(1 + extra))))
        return Insn(ln, ["rlca", "rrca", "rla", "rra", "daa", "cpl", "scf", "ccf"][y])
    if x == 1:
        if y == 6 and z == 6:
            return Insn(ln, "halt")
        n = ln + (1 if ix and (y == 6 or z == 6) else 0)
        # with (ix+d), the other operand is a real register, never ixh/ixl
        if ix and (y == 6 or z == 6):
            dd = _disp(b(1 + extra))
            if y == 6:
                return Insn(n, "ld (%s%s),%s" % (ix, dd, R8[z]))
            return Insn(n, "ld %s,(%s%s)" % (R8[y], ix, dd))
        return Insn(n, "ld %s,%s" % (reg(y), reg(z)))
    if x == 2:
        n = ln + (1 if ix and z == 6 else 0)
        return Insn(n, ALU[y] + reg(z))
    # x == 3
    if z == 0:
        return Insn(ln, "ret %s" % CC[y], flow="cjump")
    if z == 1:
        if q == 0:
            return Insn(ln, "pop %s" % ((ix or "hl") if p == 2 else RP2[p]))
        if p == 0:
            return Insn(ln, "ret", flow="stop")
        if p == 1:
            return Insn(ln, "exx")
        if p == 2:
            return Insn(ln, "jp (%s)" % (ix or "hl"), flow="stop")
        return Insn(ln, "ld sp,%s" % (ix or "hl"))
    if z == 2:
        v = b(1 + extra) | b(2 + extra) << 8
        return Insn(ln + 2, "jp %s,{A}" % CC[y], addr=v, addr_kind="jp", flow="cjump")
    if z == 3:
        if y == 0:
            v = b(1 + extra) | b(2 + extra) << 8
            return Insn(ln + 2, "jp {A}", addr=v, addr_kind="jp", flow="jump")
        if y == 1:
            return _bad()
        if y == 2:
            return Insn(ln + 1, "out (%s),a" % _hex8(b(1 + extra)))
        if y == 3:
            return Insn(ln + 1, "in a,(%s)" % _hex8(b(1 + extra)))
        if y == 4:
            return Insn(ln, "ex (sp),%s" % (ix or "hl"))
        if y == 5:
            return Insn(ln, "ex de,hl")
        return Insn(ln, "di" if y == 6 else "ei")
    if z == 4:
        v = b(1 + extra) | b(2 + extra) << 8
        return Insn(ln + 2, "call %s,{A}" % CC[y], addr=v, addr_kind="call", flow="cjump")
    if z == 5:
        if q == 0:
            return Insn(ln, "push %s" % ((ix or "hl") if p == 2 else RP2[p]))
        if p == 0:
            v = b(1 + extra) | b(2 + extra) << 8
            return Insn(ln + 2, "call {A}", addr=v, addr_kind="call", flow="call")
        return _bad()
    if z == 6:
        return Insn(ln + 1, ALU[y] + _hex8(b(1 + extra)))
    inl = 2 if y in (1, 2, 3, 5) else 0          # CPC firmware RST 1,2,3,5 take an inline word
    return Insn(ln, "rst %s" % _hex8(y * 8), inline=inl, flow="call")


def _cb(op):
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    if x == 0:
        if y == 6:
            return _bad(2)          # sll is undocumented
        return Insn(2, "%s %s" % (ROT[y], R8[z]))
    return Insn(2, "%s %d,%s" % (["", "bit", "res", "set"][x], y, R8[z]))


def _ed(b, pc):
    op = b(1)
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    p, q = y >> 1, y & 1
    if x == 1:
        if z == 0 and y != 6:
            return Insn(2, "in %s,(c)" % R8[y])
        if z == 1 and y != 6:
            return Insn(2, "out (c),%s" % R8[y])
        if z == 2:
            return Insn(2, "%s hl,%s" % ("sbc" if q == 0 else "adc", RP[p]))
        if z == 3:
            v = b(2) | b(3) << 8
            return Insn(4, ("ld ({A}),%s" if q == 0 else "ld %s,({A})") % RP[p], addr=v, addr_kind="ld")
        if z == 4 and y == 0:
            return Insn(2, "neg")
        if z == 5 and y in (0, 1):
            return Insn(2, "retn" if y == 0 else "reti", flow="stop")
        if z == 6 and y in (0, 2, 3):
            return Insn(2, "im %d" % {0: 0, 2: 1, 3: 2}[y])
        if z == 7 and y < 6:
            return Insn(2, ["ld i,a", "ld r,a", "ld a,i", "ld a,r", "rrd", "rld"][y])
        return _bad(2)
    if x == 2 and z < 4 and y >= 4:
        return Insn(2, BLI[y - 4][z])
    return _bad(2)


def _idx(b, pc, ix):
    op = b(1)
    if op == 0xCB:
        d, o = b(2), b(3)
        x, y, z = o >> 6, (o >> 3) & 7, o & 7
        if z != 6 or (x == 0 and y == 6):
            return _bad(4)
        m = "(%s%s)" % (ix, _disp(d))
        if x == 0:
            return Insn(4, "%s %s" % (ROT[y], m))
        return Insn(4, "%s %d,%s" % (["", "bit", "res", "set"][x], y, m))
    if op in (0xDD, 0xFD, 0xED):
        return _bad(1)
    r = _base(lambda i: b(i), pc, op, ix=ix, extra=1)
    if not r.valid:
        return _bad(1)
    return r


if __name__ == "__main__":      # tiny self-test against known encodings
    tests = [("3E05", "ld a,0x05"), ("CD3412", "call {A}"), ("DD7E05", "ld a,(ix+5)"), ("FD21FFFF", "ld iy,{A}"),
             ("DDCB06FE", "set 7,(ix+6)"), ("ED5B7201", "ld de,({A})"), ("1805", "jr {R}"), ("E9", "jp (hl)"),
             ("DD36020A", "ld (ix+2),0x0A"), ("DD84", "add a,ixh"), ("FD6E00", "ld l,(iy+0)"), ("EDB0", "ldir"),
             ("DDE5", "push ix"), ("FDE5", "push iy"), ("DDE1", "pop ix"), ("FDE1", "pop iy"), ("DDE3", "ex (sp),ix"), ("FDE3", "ex (sp),iy"), ("DDF9", "ld sp,ix")]
    for h, want in tests:
        m = bytearray.fromhex(h) + bytes(8)
        i = decode(m, 0)
        assert i.fmt == want and i.length == len(h) // 2, (h, i)
    print("ok")

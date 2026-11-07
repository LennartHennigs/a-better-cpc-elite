#!/usr/bin/env python3
"""Detokenize a Locomotive BASIC 1.1 program (the bytes after the AMSDOS header, or a memory dump from
&170) to text. Unknown tokens print as <hex>. usage: bastok.py FILE [--header]"""
import struct
import sys

T = ("AFTER AUTO BORDER CALL CAT CHAIN CLEAR CLG CLOSEIN CLOSEOUT CLS CONT DATA DEF DEFINT DEFREAL "
     "DEFSTR DEG DELETE DIM DRAW DRAWR EDIT ELSE END ENT ENV ERASE ERROR EVERY FOR GOSUB GOTO IF INK "
     "INPUT KEY LET LINE LIST LOAD LOCATE MEMORY MERGE MID$ MODE MOVE MOVER NEXT NEW ON ON_BREAK "
     "ON_ERROR_GOTO SQ OPENIN OPENOUT ORIGIN OUT PAPER PEN PLOT PLOTR POKE PRINT ' RAD RANDOMIZE READ "
     "RELEASE REM RENUM RESTORE RESUME RETURN RUN SAVE SOUND SPEED STOP SYMBOL TAG TAGOFF TROFF TRON "
     "WAIT WEND WHILE WIDTH WINDOW WRITE ZONE DI EI FILL GRAPHICS MASK FRAME CURSOR <E2> ERL FN SPC "
     "STEP SWAP <E8> <E9> TAB THEN TO USING > = >= < <> <= + - * / ^ \\ AND MOD OR XOR NOT").split()
OPS = {0x80 + i: w.replace("_", " ") for i, w in enumerate(T)}
FF = {0x00: "ABS", 1: "ASC", 2: "ATN", 3: "CHR$", 4: "CINT", 5: "COS", 6: "CREAL", 7: "EXP", 8: "FIX",
      9: "FRE", 10: "INKEY", 11: "INP", 12: "INT", 13: "JOY", 14: "LEN", 15: "LOG", 16: "LOG10",
      17: "LOWER$", 18: "PEEK", 19: "REMAIN", 20: "SGN", 21: "SIN", 22: "SPACE$", 23: "SQ", 24: "SQR",
      25: "STR$", 26: "TAN", 27: "UNT", 28: "UPPER$", 29: "VAL", 0x40: "EOF", 0x41: "ERR", 0x42: "HIMEM",
      0x43: "INKEY$", 0x44: "PI", 0x45: "RND", 0x46: "TIME", 0x47: "XPOS", 0x48: "YPOS", 0x49: "DERR",
      0x71: "BIN$", 0x72: "DEC$", 0x73: "HEX$", 0x74: "INSTR", 0x75: "LEFT$", 0x76: "MAX", 0x77: "MIN",
      0x78: "POS", 0x79: "RIGHT$", 0x7A: "ROUND", 0x7B: "STRING$", 0x7C: "TEST", 0x7D: "TESTR",
      0x7E: "COPYCHR$", 0x7F: "VPOS"}


def float5(b):
    m = int.from_bytes(b[:4], "little")
    e = b[4]
    if e == 0:
        return "0"
    sign = -1 if m & 0x80000000 else 1
    return repr(sign * ((m | 0x80000000) / 2**32) * 2 ** (e - 128))


def line_text(b, i, end):
    out = []
    while i < end:
        c = b[i]
        i += 1
        if 0x0E <= c <= 0x18:
            out.append(str(c - 0x0E))
        elif c == 0x01:
            out.append(":")
        elif c in (0x02, 0x03, 0x04, 0x0B, 0x0C, 0x0D):
            i += 2                                  # offset of the variable
            name = ""
            while i < end:
                ch = b[i]
                i += 1
                name += chr(ch & 0x7F)
                if ch & 0x80:
                    break
            out.append(name + {2: "%", 3: "$", 4: "!"}.get(c, ""))
        elif c == 0x19:
            out.append(str(b[i])); i += 1
        elif c == 0x1A:
            out.append(str(struct.unpack_from("<h", b, i)[0])); i += 2
        elif c == 0x1B:
            out.append("&X" + format(struct.unpack_from("<H", b, i)[0], "b")); i += 2
        elif c == 0x1C:
            out.append("&" + format(struct.unpack_from("<H", b, i)[0], "X")); i += 2
        elif c in (0x1D, 0x1E):
            out.append(str(struct.unpack_from("<H", b, i)[0])); i += 2   # 1D: pointer, 1E: line number
        elif c == 0x1F:
            out.append(float5(b[i:i + 5])); i += 5
        elif c == 0x22:
            j = b.find(b'"', i, end)
            j = end if j < 0 else j
            out.append('"' + b[i:j].decode("latin1") + ('"' if j < end else ""))
            i = j + 1
        elif c == 0x7C:
            out.append("|")
        elif c == 0xFF:
            out.append(FF.get(b[i], f"<FF{b[i]:02X}>")); i += 1
        elif c >= 0x80:
            out.append(OPS.get(c, f"<{c:02X}>"))
            if c in (0xC5, 0xC0, 0x8C):             # REM, ', DATA: rest of line is plain text
                out.append(b[i:end].decode("latin1")); i = end
        elif 0x20 <= c < 0x7C:
            out.append(chr(c))
        else:
            out.append(f"<{c:02X}>")
    return "".join(out)


def detokenize(b):
    i, lines = 0, []
    while i + 4 <= len(b):
        ln = b[i] | b[i + 1] << 8
        if ln == 0:
            break
        no = b[i + 2] | b[i + 3] << 8
        lines.append(f"{no} {line_text(b, i + 4, i + ln - 1)}")   # last byte of a line is 00
        i += ln
    return "\n".join(lines)


if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    print(detokenize(data[128:] if "--header" in sys.argv else data))

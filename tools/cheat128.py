#!/usr/bin/env python3
"""What the 128K build needs from the trainer and the save tools: its poke addresses and its commander-save key (both derived from src/elite128, never typed in).

The trainer (src/cheats/TRAINER.ASC + CHEATB.ASC) pokes the game after the files are loaded and before `CALL &1C82`. The UK row of its DATA table names 13 addresses of the
stock game; this module finds the same instructions in the 128K build (same label plus offset, in whichever of COMMONXX/COMMON2X the code now lives; the load address is the
run address, bank 7 shows the COMMON2X image at &C000) and checks that the byte there is the stock byte. The save key is the 104 bytes of code at EquipShip in LARGEAXX
(tools/elitekey.py finds it, exactly as for the 64K builds).

usage: python3 -I tools/cheat128.py            print the DATA row and the key
       python3 -I tools/cheat128.py --write    put the row into line 830 of src/cheats/CHEATB.ASC (the keys are in the BASIC tools: tools/mk_editsave.py, mk_listsave.py, mk_convsave.py, then bash tools/build_cheat.sh)
       python3 -I tools/cheat128.py --check    exit 1 when src/cheats/CHEATB.ASC (line 830) or the 128K key in EDITSAVE.ASC, LISTSAVE.ASC or CONVSAVE.ASC is stale
As a module: trainer_row() -> list of 13 addresses, save_key() -> 104 bytes, check() -> list of problems (empty = fine).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import elitekey  # noqa: E402
from symfile import read_sym  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SJASM = Path.home() / ".local/bin/sjasmplus"
CHEATB = ROOT / "src/cheats/CHEATB.ASC"
SAVE_TOOLS = [ROOT / "src/cheats" / f"{n}.ASC" for n in ("EDITSAVE", "LISTSAVE", "CONVSAVE")]      # the programs that carry the four build keys
ROW_LINE = 830


def assemble(src, tmp, name, flags=()):
    """sjasmplus SRC (extra flags such as -DFL_1) into TMP -> (labels, raw image)"""
    out, sym = Path(tmp) / f"{name}.bin", Path(tmp) / f"{name}.sym"
    r = subprocess.run([str(SJASM), "--nologo", *flags, f"--raw={out}", f"--sym={sym}", str(src)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{src}: assemble failed\n{r.stdout[-400:]}")
    return read_sym(sym), out.read_bytes()


def cheatb_line(number):
    """the text of `number DATA ...` in CHEATB.ASC (without the number), or None"""
    for line in CHEATB.read_text(encoding="latin-1").splitlines():
        if line.startswith(f"{number} DATA "):
            return line.split("DATA ", 1)[1].strip()
    return None


def uk_row():
    """The 13 UK addresses: DATA line 800 of CHEATB.ASC."""
    row = cheatb_line(800)
    if row is None:
        sys.exit("CHEATB.ASC has no line 800")
    return [int(x.strip().lstrip("&"), 16) for x in row.split(",")]


def trainer_row():
    with tempfile.TemporaryDirectory() as tmp:
        stock, stock_img = assemble(ROOT / "src/elite/commonxx.asm", tmp, "stock")
        files = {n: assemble(ROOT / f"src/elite128/{n}.asm", tmp, n) for n in ("commonxx", "common2x")}      # name -> (labels, image)
    # a label's real definition: COMMON2X holds what moved to bank 7 (&C000 and up), COMMONXX has an equ copy of it
    where = {}
    for n, (lab, _) in files.items():
        for k, v in lab.items():
            if (v >= 0xC000) == (n == "common2x"):
                where[k] = (n, v)
    by_addr = sorted((v, k) for k, v in stock.items() if 0x1A40 <= v < 0xA000 and k in where)
    row = []
    for a in uk_row():
        v, k = [x for x in by_addr if x[0] <= a][-1]      # the nearest label before the stock address, which the 128K tree also has
        n, base = where[k][0], 0xC000 if where[k][0] == "common2x" else 0x1A40
        addr = where[k][1] + (a - v)
        want, got = stock_img[a - 0x1A40], files[n][1][addr - base]
        if want != got:
            sys.exit(f"{a:04X} ({k}+{a - v}) -> {addr:04X}: the byte there is {got:02X}, stock has {want:02X}: look at it by hand")
        row.append(addr)
    return row


def save_key():
    with tempfile.TemporaryDirectory() as tmp:
        _, img = assemble(ROOT / "src/elite128/largeaxx.asm", tmp, "largeaxx")
    return elitekey.find_key(img)[1]


def row_text(row):
    return ",".join("&%04X" % a for a in row)


def check():
    problems = []
    want = row_text(trainer_row())
    if cheatb_line(ROW_LINE) != want:
        problems.append(f"{CHEATB.name}: line {ROW_LINE} is stale, it should be: {ROW_LINE} DATA {want} (python3 -I tools/cheat128.py --write)")
    key = save_key().hex().upper()
    for p in SAVE_TOOLS:
        if f"DATA 128K,{key}" not in p.read_text(encoding="latin-1"):
            problems.append(f"{p.name} does not carry the key of the 128K build: run tools/mk_{p.stem.lower()}.py, then bash tools/build_cheat.sh")
    return problems


def write_row():
    """replace line 830 of CHEATB.ASC (CRLF lines, the file ends with Ctrl-Z) or add it after line 820"""
    text = CHEATB.read_bytes().decode("latin-1")      # read_text would turn the CRLF into LF
    new = f"{ROW_LINE} DATA {row_text(trainer_row())}"
    lines = text.split("\r\n")
    if cheatb_line(ROW_LINE) is not None:
        lines = [new if l.startswith(f"{ROW_LINE} DATA ") else l for l in lines]
    else:
        i = max(k for k, l in enumerate(lines) if l.startswith("8") and " DATA " in l)
        lines.insert(i + 1, new)
    CHEATB.write_bytes("\r\n".join(lines).encode("latin-1"))
    print("wrote", new)


if __name__ == "__main__":
    if "--write" in sys.argv:
        write_row()
        sys.exit(0)
    if "--check" in sys.argv:
        probs = check()
        for p in probs:
            print("STALE:", p)
        sys.exit(1 if probs else 0)
    print(f"{ROW_LINE} DATA {row_text(trainer_row())}")
    print("key", save_key().hex(" "))

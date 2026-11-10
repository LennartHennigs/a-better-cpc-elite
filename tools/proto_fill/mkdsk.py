#!/usr/bin/env python3
"""Write work/proto_fill/proto.dsk: a blank disk with the two filled-ship prototypes, both with load and exec address &8000.
  PROTO.BIN  bounding-box erase, the ship is redrawn on the visible screen (fill.asm)
  FLIP.BIN   page flip, drawn off screen and flipped at vsync, with the CPC's ships to pick with the cursor keys (flip.asm); one 36 KB
             file from &1000 whose first 27 KB are the ship data (15 ships), which the program copies into RAM banks 4 and 5
Run tools/proto_fill/run.py and run.py --flip (or gen.py and sjasmplus) first so that work/proto_fill/proto.bin and flip.bin exist.
Start one on a 6128 with  RUN"PROTO.BIN  or  RUN"FLIP.BIN  (on a 464 or 664 they only draw a red bar: the RAM check finds no second 64 KB).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import dskx  # noqa: E402

OUT = ROOT / "work/proto_fill/proto.dsk"
OUT.unlink(missing_ok=True)
subprocess.run([str(Path.home() / ".local/bin/iDSK"), str(OUT), "-n"], check=True, capture_output=True)
d = bytearray(OUT.read_bytes())
secs = dskx.sector_offsets(d)
first = min(r for (t, r) in secs if t == 0)
# FLIP.BIN is one image from &1000 to &9DFF: the ship data (15 ships in ship order) at &1000, the program at &8000
ships = (ROOT / "work/proto_fill/ships4.bin").read_bytes() + (ROOT / "work/proto_fill/ships5.bin").read_bytes()
flip = ROOT / "work/proto_fill/flip.bin"
files = [("PROTO", (ROOT / "work/proto_fill/proto.bin").read_bytes(), 0x8000, 0x8000)]
if flip.exists():
    img = bytearray(0x9E00 - 0x1000)
    img[:len(ships)] = ships
    img[0x7000:0x7000 + len(flip.read_bytes())] = flip.read_bytes()
    (ROOT / "work/proto_fill/flip.img").write_bytes(img)
    files.append(("FLIP", bytes(img), 0x1000, 0x8000))
for name, data, load, exe in files:
    payload = dskx.make_header(name, "BIN", load, len(data), exe) + data
    dskx.add_payload(d, secs, first, name, "BIN", payload, -(-len(payload) // 128))
    print(f"{name}.BIN: {len(data)} bytes at &{load:04X}")
OUT.write_bytes(d)
print("wrote", OUT)

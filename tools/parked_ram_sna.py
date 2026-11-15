#!/usr/bin/env python3
"""Hand-flown test of the parked firmware RAM in any emulator that loads and saves .sna snapshots (see tools/test_parked_ram.py, TODO.md).

  python3 -I tools/parked_ram_sna.py markdocked IN.sna OUT.sna [MARK]  # IN = a docked snapshot: MARK in every zero run of the parked copy at &A600 (runs.txt is rewritten to match)
  python3 -I tools/parked_ram_sna.py make [MARK]        # work/parked_ram/flight_marked.sna: firebird_in_flight.sna with MARK (default AA) in every zero run of 16+ bytes of &0040-&1A3F
  python3 -I tools/parked_ram_sna.py check FILE.sna [MARK]  # count marker bytes that changed in a snapshot you saved afterwards
  python3 -I tools/parked_ram_sna.py markbin IN.bin OUT.bin [MARK]  # IN = 0x1A00 bytes dumped from &0040 (RVM debugger `save`); OUT = the same with MARK in its zero runs
  python3 -I tools/parked_ram_sna.py checkbin MARKED.bin NEW.bin [MARK]  # NEW = another 0x1A00-byte dump (from &0040 flying, or from &A600 docked)

`check` reads the markers at &0040 (flying) and, when low memory holds LARGEAXX (docked), also at &A600. The flat RAM starts at file offset 0x100 (a 64 KB or 128 KB .sna).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "work/xray/output/firebird_in_flight.sna"
OUT = ROOT / "work/parked_ram"
RUNS = OUT / "runs.txt"


def runs_of(ram):
    runs, i = [], 0x40
    while i < 0x1A40:
        if ram[i] == 0:
            j = i
            while j < 0x1A40 and ram[j] == 0:
                j += 1
            if j - i >= 16:
                runs.append((i, j - i))
            i = j
        else:
            i += 1
    return runs


def spans(bad):
    out, i = [], 0
    while i < len(bad):
        j = i
        while j + 1 < len(bad) and bad[j + 1] == bad[j] + 1:
            j += 1
        out.append(f"{bad[i]:04X}-{bad[j]:04X}")
        i = j + 1
    return out


mode = sys.argv[1]
if mode == "markbin":
    mark = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0xAA
    img = bytearray(Path(sys.argv[2]).read_bytes())
    assert len(img) == 0x1A00, len(img)
    runs, i = [], 0
    while i < len(img):
        if img[i] == 0:
            j = i
            while j < len(img) and img[j] == 0:
                j += 1
            if j - i >= 16:
                runs.append((i, j - i))
            i = j
        else:
            i += 1
    for a, l in runs:
        img[a:a + l] = bytes([mark]) * l
    Path(sys.argv[3]).write_bytes(img)
    Path(sys.argv[3] + ".runs").write_text("\n".join(f"{a:04X} {l}" for a, l in runs))
    print(f"{sys.argv[3]}: {len(runs)} runs, {sum(l for _, l in runs)} bytes set to {mark:02X}")
elif mode == "checkbin":
    mark = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0xAA
    new = Path(sys.argv[3]).read_bytes()
    runs = [(int(a, 16), int(l)) for a, l in (x.split() for x in Path(sys.argv[2] + ".runs").read_text().splitlines())]
    bad = [0x40 + k for a, l in runs for k in range(a, a + l) if new[k] != mark]
    print(f"{len(bad)} of {sum(l for _, l in runs)} marker bytes changed", " ".join(spans(bad)[:40]))
elif mode == "markdocked":
    # docked snapshot (low memory holds LARGEAXX, the parked copy is at &A600): put MARK in every zero run of 16+ bytes of &A600-&BFFF and write runs.txt in the
    # low-memory coordinates `check` expects (low address = &0040 + offset in the parked block)
    mark = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0xAA
    data = bytearray(Path(sys.argv[2]).read_bytes())
    img = data[0x100 + 0xA600:0x100 + 0xA600 + 0x1A00]
    runs, i = [], 0
    while i < len(img):
        if img[i] == 0:
            j = i
            while j < len(img) and img[j] == 0:
                j += 1
            if j - i >= 16:
                runs.append((0x40 + i, j - i))
            i = j
        else:
            i += 1
    for a, l in runs:
        data[0x100 + 0xA600 + a - 0x40:0x100 + 0xA600 + a - 0x40 + l] = bytes([mark]) * l
    OUT.mkdir(exist_ok=True)
    Path(sys.argv[3]).write_bytes(data)
    RUNS.write_text("\n".join(f"{a:04X} {l}" for a, l in runs))
    print(f"{sys.argv[3]}: {len(runs)} runs in the A600 copy, {sum(l for _, l in runs)} bytes set to {mark:02X}")
elif mode == "make":
    mark = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0xAA
    data = bytearray(SRC.read_bytes())
    runs = runs_of(data[0x100:0x100 + 65536])
    for a, l in runs:
        data[0x100 + a:0x100 + a + l] = bytes([mark]) * l
    OUT.mkdir(exist_ok=True)
    (OUT / "flight_marked.sna").write_bytes(data)
    RUNS.write_text("\n".join(f"{a:04X} {l}" for a, l in runs))
    print(f"{OUT / 'flight_marked.sna'}: {len(runs)} runs, {sum(l for _, l in runs)} bytes set to {mark:02X}")
else:
    data = Path(sys.argv[2]).read_bytes()
    mark = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0xAA
    ram = data[0x100:0x100 + 65536]
    runs = [(int(a, 16), int(l)) for a, l in (x.split() for x in RUNS.read_text().splitlines())]
    total = sum(l for _, l in runs)
    for base, tag in ((0x40, "low memory (&0040)"), (0xA600, "parked copy (&A600)")):
        bad = [k for a, l in runs for k in range(a, a + l) if ram[base + k - 0x40] != mark]
        print(f"{tag}: {len(bad)} of {total} changed", " ".join(spans(bad)[:40]))
    print("flying: read the first line; docked: read the second (low memory then holds LARGEAXX, so the first line is large)")

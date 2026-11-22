"""Shared by test_parked_ram.py, test_parked_save.py and test_parked_save128.py (the parked firmware RAM probes, docs/_memory_map.md): the build switch and the zero-run helpers.

BUILD=128 selects the 128K build (disk/elite128.dsk, output/flight128.sna from test_flight128.py 3); its addresses come from the symbols of src/elite128 (handleEntitys, and the
`xor a` after the loop of DockingSequence, +120, checked against the byte), so a layout change cannot leave a stale number here. The 64K ones are fixed: src/elite is byte-exact.
Import it from a test with  sys.path.insert(0, str(Path(__file__).resolve().parent))  (python -I does not put the script's folder on the path).
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cheat128  # noqa: E402

B128 = os.environ.get("BUILD") == "128"
SNA_FLIGHT = "output/flight128.sna" if B128 else "output/firebird_in_flight.sna"
DISK_BASE = "disk/elite128.dsk" if B128 else "disk/Elite_UK_Firebird_cracked_trainer.dsk"


def addresses():
    """-> (handleEntitys, the continue address after the docking loop: `xor a` after the djnz of todoDockingProcedure)"""
    if not B128:
        return 0x5066, 0x728D + 16
    with tempfile.TemporaryDirectory() as d:
        labels, img = cheat128.assemble(ROOT / "src/elite128/common2x.asm", d, "c2")
    dock = labels["DockingSequence"] + 120
    assert img[dock - 0xC000] == 0xAF, "DockingSequence + 120 is not the xor a after the loop any more"
    return labels["handleEntitys"], dock


HANDLE, DOCK_CONT = addresses()


def zero_runs(ram, lo=0x40, hi=0x1A40, minimum=16):
    """[(address, length)] of the runs of zero bytes in ram[lo:hi] that are at least `minimum` long"""
    runs, i = [], lo
    while i < hi:
        if ram[i] == 0:
            j = i
            while j < hi and ram[j] == 0:
                j += 1
            if j - i >= minimum:
                runs.append((i, j - i))
            i = j
        else:
            i += 1
    return runs


def marker(mark, length):
    """the hex string memory_write takes for `length` bytes of `mark`"""
    return (bytes([mark]) * length).hex(" ")

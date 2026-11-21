#!/usr/bin/env python3
"""The 128K port of test_ship_packs.py: the same script with BUILD=128 (src/elite128, output/flight128.sna, disk/elite128.dsk); see its header. Kept as its own name for run_all.py --emu128."""
import os
import runpy
from pathlib import Path

os.environ["BUILD"] = "128"
runpy.run_path(str(Path(__file__).resolve().parent / "test_ship_packs.py"), run_name="__main__")

#!/usr/bin/env python3
"""The laser position keys on the 64K mission disk: test_laserkeys.py with the argument 64 (run_all.py --emu; needs work/xray/disk/elite_missions.dsk)."""
import runpy
import sys
from pathlib import Path

sys.argv = [sys.argv[0], "64"]
runpy.run_path(str(Path(__file__).with_name("test_laserkeys.py")), run_name="__main__")

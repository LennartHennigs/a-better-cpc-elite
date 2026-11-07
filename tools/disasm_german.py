#!/usr/bin/env python3
"""Wrapper: disasm_locale.py for the german build (see tools/disasm_locale.py)."""
import runpy, sys
from pathlib import Path
sys.argv.insert(1, "german")
runpy.run_path(str(Path(__file__).with_name("disasm_locale.py")), run_name="__main__")

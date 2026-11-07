#!/usr/bin/env python3
"""Wrapper: map_locale.py for the french build (see tools/map_locale.py)."""
import runpy, sys
from pathlib import Path
sys.argv.insert(1, "french")
runpy.run_path(str(Path(__file__).with_name("map_locale.py")), run_name="__main__")

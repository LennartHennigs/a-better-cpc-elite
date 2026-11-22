"""Read a sjasmplus symbol file (`--sym=FILE`, lines `label: EQU 0x1234`) into {label: address}."""
import sys
from pathlib import Path


def read_sym(path, *wanted):
    """All labels of the symbol file as {name: address}. Exits naming the file when one of `wanted` is not in it."""
    labels = {}
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].endswith(":"):
            labels[parts[0][:-1]] = int(parts[2], 16)
    missing = [n for n in wanted if n not in labels]
    if missing:
        sys.exit(f"{Path(path).name}: label(s) not found: {', '.join(missing)}")
    return labels

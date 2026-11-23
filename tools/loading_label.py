"""Write "64" or "128" next to the ELITE logo of the loading picture (PICTURE.BIN on the disk), in the CPC's own font and red, like the signature at the lower left.

The picture is Mode 1 screen memory (16,384 bytes, 80 bytes per row, rows interleaved by &800). The digits come from the CPC 6128 lower ROM (character set at &3800), read at
build time from work/xray/roms/os6128.rom and never copied into the repo. They sit 5 pixels right of the logo (its right edge is x 205), bottom row on the bottom row of
"Bell & Braben" (y 197), over the orange beam. Used by tools/build_expanded.sh ("64") and tools/build_dsk128.py ("128").

usage (host check): python3 -I tools/loading_label.py PICTURE.BIN 128 OUT.BIN     (PICTURE.BIN = the file's 16,384 data bytes, without the AMSDOS header)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dskx  # noqa: E402

ROM = Path(__file__).resolve().parent.parent / "work" / "xray" / "roms" / "os6128.rom"
X0, Y0, PEN = 210, 191, 3      # glyph cell origin: its first lit column is X0 + 1 = 211 = logo edge 205 + 1 + 5 gap


def _addr(x, y):
    return (y // 8) * 80 + (y % 8) * 0x800 + x // 4


def _pen(buf, x, y):
    b, p = buf[_addr(x, y)], x % 4
    return (b >> (7 - p) & 1) | (b >> (3 - p) & 1) << 1


def label(picture, text):
    """the 16,384 picture bytes with `text` drawn in; stops if a target pixel is not black or orange (not the original picture)"""
    assert len(picture) == 0x4000, len(picture)
    font = ROM.read_bytes()[0x3800:0x4000]
    out = bytearray(picture)
    for k, ch in enumerate(text):
        for r in range(8):
            for c in range(8):
                if font[ord(ch) * 8 + r] >> (7 - c) & 1:
                    x, y = X0 + 8 * k + c, Y0 + r
                    if _pen(picture, x, y) not in (0, 2):
                        sys.exit(f"loading_label: pixel ({x},{y}) is pen {_pen(picture, x, y)}, not black or orange: this is not the original picture")
                    i, p = _addr(x, y), x % 4
                    out[i] = out[i] & ~((1 << (7 - p)) | (1 << (3 - p))) | (PEN & 1) << (7 - p) | (PEN >> 1 & 1) << (3 - p)
    return bytes(out)


def stamp(d, secs, first, disk, text):
    """patch PICTURE.BIN in the image bytes `d` in place (header, directory entry and hidden attribute stay); the picture is read from the disk file `disk`"""
    pic = dskx.read_files(dskx.load_sectors(disk))[(0, "PICTURE.BIN")]
    h = dskx.overwrite_file(d, secs, first, "PICTURE.BIN", label(pic[128:128 + 0x4000], text))
    print(f'PICTURE.BIN: "{text}" next to the ELITE logo (load {h["load"]:04X})')


if __name__ == "__main__":
    src, text, dst = sys.argv[1:4]
    Path(dst).write_bytes(label(Path(src).read_bytes(), text))

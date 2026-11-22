#!/usr/bin/env python3
"""Edit an Elite CPC commander save (104 bytes): the savegame counterpart of the interactive trainer (src/cheats/TRAINER.ASC).

usage:
  saveedit.py show   SAVE  [--key-disk GAME.dsk]
  saveedit.py edit   SAVE  [--key-disk GAME.dsk] [-o OUT] [options]
  saveedit.py roundtrip SAVE [--key-disk GAME.dsk]       decode, re-encode, compare with the input (self test)

SAVE is a raw 104-byte file, a file with its 128-byte AMSDOS header (a save on a DSK), or DISK.dsk:NAME for a file on a disk image
(for example work/some.dsk:PETER.BIN). The key (the 104 bytes of game code at EquipShip in LARGEAXX, one per build) is read from
--key-disk (default: the disk named in SAVE, otherwise Elite_UK_Firebird_cracked_trainer.dsk). Every build has its own key: use a disk of the
build the save belongs to (the saves on Elite_DE_savegames.dsk need Elite_DE_cracked.dsk). Both checksums are recomputed.
Writing: -o OUT.BIN writes a file with the AMSDOS header (kept from the input, or made); -o OUT.dsk:NAME replaces that file in a COPY of the
disk image (an existing file keeps its size; a missing file is added). Nothing is written without -o, and the original is never touched: to edit a disk save,
copy the disk into work/ first (CLAUDE.md: never modify the original disks).

options (all optional, each sets one thing; the numbers match the trainer; --to-key-disk GAME.dsk encrypts the result for another build, which converts a save between UK, French and German):
  --name NAME          commander name (up to 10 characters, upper case)
  --kills N            kill count 0-65535 (bytes &38D8/&38D9, the BBC TALLY: 256 = the Constrictor/plans gate "256 kill points"; the fraction byte is kept)
  --jumps N            jump counter 0-65535 (the stock missions start at 32, 128 and 254; counted from galaxy 2 on in the game)
  --cash CR            credits in Cr (0-65,535,999.9)
  --legal N            legal status (0 clean, 1-49 offender, 50+ fugitive on the status page)
  --fuel LY            fuel in light years (0-7.0)
  --stock 0-3          stock missions like the trainer: 1 supernova stage, 2 cloak stage (also bit 0), 3 invasion stage (bits 0 and 1): sets the jump counter 31, 127 or 253
  --cloak yes|no       own the cloaking device (Missionflag bit 6)
  --added 0-4          the added missions chain (docs/_missions.md section 11): 0 none (state 0, &38FE 0), 1 Trumbles offered next, then plans (Constrictor paid), 2 stolen police ship next
                       (plans delivered, offer at the next docking), 3 asteroids next (stolen ship paid), 4 all paid, asteroids state 3 (the Trumbles are no longer offered)
  --state HEX          missionState (&38FD) byte, raw
  --state2 HEX         the byte at &38FE, raw (asteroid counter / state)
  --trumbles N         Trumble count (&3905/&3906, 0-32767)
  --missionflag HEX    Missionflag (&3927) byte, raw
"""
import argparse
import struct
import sys
from functools import reduce
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dskx  # noqa: E402
import elitekey  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KEY_DISK = ROOT / "disks" / "Elite_UK_Firebird_cracked_trainer.dsk"
LEN = 0x68
O_NAME, O_LEGAL, O_KILLS, O_JUMPS, O_GALAXY, O_CASH, O_FUEL = 0x00, 0x0B, 0x0C, 0x0F, 0x11, 0x12, 0x2E
O_STATE, O_STATE2, O_TRUMBLES, O_EXTRA_UNIT, O_THARGON, O_MISSIONFLAG = 0x32, 0x33, 0x3A, 0x37, 0x5B, 0x5C
ADDED_STATE = {0: (0x00, 0x00), 1: (0x02, 0x00), 2: (0x2E, 0x00), 3: (0x5E, 0x00), 4: (0x5E, 0x03)}


def split_arg(spec):
    """'DISK.dsk:NAME' -> (disk, name); anything else -> (None, path)"""
    if ".dsk:" in spec.lower():
        i = spec.lower().index(".dsk:") + 4
        return Path(spec[:i]), spec[i + 1:]
    return None, Path(spec)


def read_save(spec):
    """returns (plain-save-bytes-as-stored (104 bytes encrypted), header bytes or None, key-disk hint)"""
    disk, name = split_arg(spec)
    if disk:
        files = dskx.read_files(dskx.load_sectors(disk))
        hits = [(k, v) for k, v in files.items() if k[1].upper() == str(name).upper()]
        if not hits:
            raise SystemExit(f"{disk}: no file {name}; files: {', '.join(k[1] for k in files)}")
        data = hits[0][1]
    else:
        data = Path(name).read_bytes()
    if len(data) >= 128 + LEN and dskx.amsdos_header(data):
        return data[128:128 + LEN], data[:128], disk
    if len(data) < LEN:
        raise SystemExit(f"{spec}: {len(data)} bytes, a save has {LEN}")
    return data[:LEN], None, disk


def decrypt(enc, key):
    return bytearray(a ^ b for a, b in zip(enc, key))


def checksums(p):
    p[0x66] = reduce(lambda a, b: a ^ b, p[:0x66])
    p[0x67] = sum(p[:0x67]) & 255


checks_ok = elitekey.checks_ok


def encrypt(p, key):
    return bytes(a ^ b for a, b in zip(p, key))


def show(p):
    le = lambda a, n: int.from_bytes(p[a:a + n], "little")
    print("checksums     ", "ok" if checks_ok(p) else "BAD (wrong key or edited without recomputing)")
    print("name          ", bytes(p[:11]).split(b"\0")[0].decode("latin1"))
    print("legal status  ", p[O_LEGAL])
    print("kills (&38D8) ", le(O_KILLS + 1, 2), "(24-bit score", le(O_KILLS, 3), ")")
    print("jump counter  ", le(O_JUMPS, 2))
    print("galaxy        ", p[O_GALAXY] + 1)
    print("credits       ", (le(O_CASH, 2) * 10000 + le(O_CASH + 2, 2)) / 10, "Cr")
    print("fuel          ", p[O_FUEL] / 10, "LY")
    print("missionState  ", "%02X" % p[O_STATE], "(&38FD: Constrictor bits 0-1 %d, plans 2-3 %d, stage 4-6 %d, Trumbles offered %d)" % (p[O_STATE] & 3, p[O_STATE] >> 2 & 3, p[O_STATE] >> 4 & 7, p[O_STATE] >> 7))
    print("&38FE         ", "%02X" % p[O_STATE2], "(asteroid state %d, asteroids to go %d)" % (p[O_STATE2] & 3, p[O_STATE2] >> 2))
    print("Trumbles      ", le(O_TRUMBLES, 2))
    print("Missionflag   ", "%02X" % p[O_MISSIONFLAG], "(&3927: bit 0 supernova, 1 cloak stage, 2 invasion, 3 done, 5 refugees, 6 cloak owned, 7 ECM jammer)")
    print("ThargonMission", p[O_THARGON])
    print("raw           ", bytes(p).hex(" "))


def apply(p, a):
    if a.name is not None:
        nm = a.name.upper()[:10].encode("latin1") + b"\0"
        p[0:len(nm)] = nm
    if a.legal is not None:
        p[O_LEGAL] = a.legal & 255
    if a.kills is not None:
        k = max(0, min(65535, a.kills))
        p[O_KILLS + 1], p[O_KILLS + 2] = k & 255, k >> 8
    if a.stock is not None:
        n = {0: None, 1: 31, 2: 127, 3: 253}[a.stock]
        if n is not None:
            p[O_JUMPS], p[O_JUMPS + 1] = n, 0
        p[O_MISSIONFLAG] = (p[O_MISSIONFLAG] & ~3) | (1 if a.stock == 2 else 3 if a.stock == 3 else 0)
    if a.jumps is not None:
        j = max(0, min(65535, a.jumps))
        p[O_JUMPS], p[O_JUMPS + 1] = j & 255, j >> 8
    if a.cash is not None:
        c = int(round(max(0.0, min(65535999.9, a.cash)) * 10))
        u, v = divmod(c, 10000)
        p[O_CASH:O_CASH + 4] = struct.pack("<HH", u, v)
    if a.fuel is not None:
        p[O_FUEL] = max(0, min(70, int(round(a.fuel * 10))))
    if a.cloak is not None:
        p[O_MISSIONFLAG] = (p[O_MISSIONFLAG] & ~0x40) | (0x40 if a.cloak == "yes" else 0)
    if a.added is not None:
        p[O_STATE], p[O_STATE2] = ADDED_STATE[a.added]
        if a.added >= 2:
            p[O_EXTRA_UNIT] = 0xFE        # the plans reward (Navy energy unit) is part of "plans delivered"
    if a.state is not None:
        p[O_STATE] = a.state & 255
    if a.state2 is not None:
        p[O_STATE2] = a.state2 & 255
    if a.trumbles is not None:
        t = max(0, min(32767, a.trumbles))
        p[O_TRUMBLES], p[O_TRUMBLES + 1] = t & 255, t >> 8
    if a.missionflag is not None:
        p[O_MISSIONFLAG] = a.missionflag & 255


def write_out(out_spec, data_with_header):
    disk, name = split_arg(out_spec)
    if not disk:
        Path(name).write_bytes(data_with_header)
        print("wrote", name, f"({len(data_with_header)} bytes with header)")
        return
    if dskx.is_original(disk):   # CLAUDE.md: never modify the original disks (disks/)
        raise SystemExit(f"{disk}: refusing to write into a disk in the project root or disks/; copy it to work/ first")
    d = bytearray(disk.read_bytes())
    secs = dskx.sector_offsets(d)
    first = min(r for (t, r) in secs if t == 0)
    extents = dskx.find_extents(d, secs, first, str(name))
    if not extents:
        stem, _, ext = str(name).upper().partition(".")
        dskx.add_payload(d, secs, first, stem[:8], (ext or "BIN")[:3], data_with_header, -(-len(data_with_header) // 128))
        dskx.write_atomic(disk, d)
        print("added", name, "to", disk)
        return
    records = -(-len(data_with_header) // 128)          # the directory keeps the size in 128-byte records, at most 128 per extent
    slots = []
    for k, (_, off, blocks) in enumerate(extents):
        d[off + 15] = max(0, min(128, records - 128 * k))
        slots += [secs[((blk * 2 + half) // 9, first + (blk * 2 + half) % 9)][0] for blk in blocks for half in (0, 1)]
    if len(data_with_header) > len(slots) * 512:
        raise SystemExit("the new file is larger than the old one")
    payload = data_with_header.ljust(len(slots) * 512, b"\xE5")    # the disk's filler byte, as add_payload pads
    for k, off in enumerate(slots):
        d[off:off + 512] = payload[k * 512:(k + 1) * 512]
    dskx.write_atomic(disk, d)
    print("replaced", name, "in", disk)


def main():
    ap = argparse.ArgumentParser(description="Edit an Elite CPC commander save", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("cmd", choices=["show", "edit", "roundtrip"])
    ap.add_argument("save")
    ap.add_argument("--key-disk")
    ap.add_argument("-o", "--out")
    ap.add_argument("--to-key-disk", help="encrypt the result for the build of this game disk (converts a save between the UK, French and German builds)")
    ap.add_argument("--name"); ap.add_argument("--kills", type=int); ap.add_argument("--jumps", type=int); ap.add_argument("--cash", type=float)
    ap.add_argument("--legal", type=int); ap.add_argument("--fuel", type=float); ap.add_argument("--stock", type=int, choices=range(4))
    ap.add_argument("--cloak", choices=["yes", "no"]); ap.add_argument("--added", type=int, choices=range(5))
    ap.add_argument("--state", type=lambda x: int(x, 16)); ap.add_argument("--state2", type=lambda x: int(x, 16))
    ap.add_argument("--trumbles", type=int); ap.add_argument("--missionflag", type=lambda x: int(x, 16))
    a = ap.parse_args()
    enc, header, disk = read_save(a.save)
    key_disk = Path(a.key_disk) if a.key_disk else (disk if disk and any(k[1].upper() == "LARGEAXX.BIN" for k in dskx.read_files(dskx.load_sectors(disk))) else DEFAULT_KEY_DISK)
    off, key = elitekey.key_from_disk(key_disk)
    p = decrypt(enc, key)
    if not checks_ok(p):
        print(f"warning: the checksums of {a.save} do not verify with the key of {key_disk} (another build?)", file=sys.stderr)
    if a.cmd == "show":
        return show(p)
    if a.cmd == "roundtrip":
        q = bytearray(p)
        checksums(q)
        same = encrypt(q, key) == enc
        print("roundtrip:", "identical" if same else "DIFFERENT (original checksums were not consistent)")
        return 0 if same else 1
    apply(p, a)
    checksums(p)
    show(p)
    if a.out:
        _, oname = split_arg(a.out)
        stem, _, ext = Path(str(oname)).name.upper().partition(".")
        hdr = header if header else dskx.make_header(stem[:8], (ext or "BIN")[:3], 0x39D2, LEN)
        if header:      # keep load/exec/length, but the file name inside the header follows the new name; recompute the header checksum
            stem, _, ext = Path(str(oname)).name.upper().partition(".")
            hb = bytearray(header)
            hb[1:9] = stem[:8].ljust(8).encode()
            hb[9:12] = (ext or "BIN")[:3].ljust(3).encode()
            hb[67:69] = struct.pack("<H", sum(hb[:67]) & 0xFFFF)
            hdr = bytes(hb)
        okey = elitekey.key_from_disk(a.to_key_disk)[1] if a.to_key_disk else key
        write_out(a.out, hdr + encrypt(p, okey))
    else:
        print("(nothing written: give -o OUT)")


if __name__ == "__main__":
    sys.exit(main() or 0)

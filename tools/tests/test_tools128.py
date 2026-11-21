#!/usr/bin/env python3
"""128K disk: the save converter (CONVSAVE, both directions against the 64K builds), the save editor and lister, and the trainer.

usage (from work/xray, after `python3 -I tools/build_dsk128.py` and cp build/elite128.dsk work/xray/disk/):
  PATH=$HOME/.local/bin:$PATH ~/.local/share/uv/tools/cpcxray/bin/python -I /ABSOLUTE/PATH/tools/tests/test_tools128.py
Works on copies of the disk (disk/tools128_w.dsk); prints ALL OK at the end.
 1. CONVSAVE UK -> 128K and 128K -> UK, compared byte for byte with the host (tools/elitekey.py keys; saveedit.py does the same conversion).
 2. LISTSAVE shows the builds of the saves on the disk; EDITSAVE edits kills in a 128K save (checked with the 128K key).
 3. TRAINER with every cheat on: at CALL &1C82 the 13 poke targets hold the poked bytes (tools/cheat128.py addresses), the commander block has the answers, and after the
    game has started the pokes are still there (bank 7 and main RAM from a snapshot).
"""
import asyncio
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cheat128  # noqa: E402
import elitekey  # noqa: E402
import saveedit  # noqa: E402

DISK = "disk/tools128_w.dsk"
KEY128 = elitekey.key_from_disk(ROOT / "build/elite128.dsk")[1]
KEY_UK = elitekey.key_from_disk(ROOT / "disks/Elite_UK_Firebird_cracked_trainer.dsk")[1]
G = 0x39C7      # default commander block (the trainer's g)
SAVE_OUT = "disk/tools128_out.dsk"      # the emulator's disk, saved after a BASIC program wrote to it


def rekey(enc, old, new):
    """what the host says CONVSAVE must write: the 104 bytes encrypted with another build's key"""
    return saveedit.encrypt(saveedit.decrypt(enc, old), new)


def bank_byte(snap, addr, bank=None):
    """a byte of a flat 128K snapshot (banks 0-7 from file offset 0x100): `bank` defaults to the CPU's own 16 KB block (configuration C0), 7 for code of the block at &C000"""
    return snap[0x100 + (addr >> 14 if bank is None else bank) * 0x4000 + (addr & 0x3FFF)]


async def main():
    shutil.copy("disk/elite128.dsk", DISK)
    # a UK save on the disk: LEN from the German saves disk, re-keyed for the UK game
    subprocess.run(["python3", "-I", str(ROOT / "tools/saveedit.py"), "edit", str(ROOT / "disks/Elite_DE_savegames.dsk") + ":LEN.BIN", "--key-disk", str(ROOT / "disks/Elite_DE_cracked.dsk"),
                    "--to-key-disk", str(ROOT / "disks/Elite_UK_Firebird_cracked_trainer.dsk"), "-o", str(Path(DISK).resolve()) + ":UK.BIN"], check=True, capture_output=True)
    uk_save, len_save = (saveedit.read_save(f"{DISK}:{n}")[0] for n in ("UK.BIN", "LEN.BIN"))
    ok = True
    async with stdio_client(StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def c(n, a=None):
                x = await s.call_tool(n, a or {})
                t = "".join(getattr(i, "text", "") for i in x.content)
                try:
                    return json.loads(t)
                except ValueError:
                    return t

            async def boot():
                await c("load_config", {"path": "config/cpc6128.toml"})
                await c("disk_insert", {"drive": "A", "path": DISK, "writable": True})
                await c("run", {"max_us": 4_000_000, "timeout_s": 60})

            async def typ(t, after=200_000):
                await c("type_text", {"text": t, "wait": True, "timeout_s": 60})
                await c("run", {"max_us": after, "timeout_s": 120})

            async def text():
                return "\n".join((await c("screen_text"))["lines"])

            async def until(want, limit_us=40_000_000):
                """run in 500 ms steps until the screen shows `want` (a text, or a list of regular expressions that must all match): a disk read or write takes several emulated seconds"""
                t = ""
                for _ in range(limit_us // 500_000):
                    await c("run", {"max_us": 500_000, "timeout_s": 60})
                    t = await text()
                    if all(re.search(x, t) for x in want) if isinstance(want, list) else want in t:
                        return t
                print("  not on the screen:", repr(want), "\n", t)
                return t

            async def disk_file(name):
                """the 104 encrypted bytes of a save the BASIC program wrote (the emulator's disk is not written back to the file)"""
                await c("disk_save", {"drive": "A", "path": SAVE_OUT})
                try:
                    return saveedit.read_save(f"{SAVE_OUT}:{name}")[0]
                except SystemExit:
                    return None

            async def convert(src, digit, dst, build, target, enc, old, new):
                """RUN"CONVSAVE with the dialogue of docs/_cheats.md; the file it writes must equal the host's conversion of `enc` from key `old` to key `new`"""
                await typ('RUN"CONVSAVE\r', 500_000)
                await until("press a key.")
                await typ(" ")
                await typ(src + "\r")
                t = await until("Convert to")
                await typ(digit + "\r")
                await typ(dst + "\r")
                await until("then press a key.")
                await typ(" ")
                t += await until(f"Saved {dst} as {target}")
                got = await disk_file(dst)
                good = f"Build:  {build}" in t and f"Saved {dst} as {target}" in t and got == rekey(enc, old, new)
                print(f"{build} -> {target} equals the host:", good)
                return good

            # ---- 1. the converter -------------------------------------------------------------------------------------------------------
            await boot()
            ok &= await convert("UK.BIN", "4", "C128.BIN", "UK", "128K", uk_save, KEY_UK, KEY128)
            ok &= elitekey.checks_ok(saveedit.decrypt((await disk_file("C128.BIN")) or bytes(104), KEY128))      # the converted save passes both checksums with the 128K key
            ok &= await convert("LEN.BIN", "1", "LENUK.BIN", "128K", "UK", len_save, KEY128, KEY_UK)

            # ---- 2. LISTSAVE and EDITSAVE -------------------------------------------------------------------------------------------------
            await boot()
            await typ('RUN"LISTSAVE\r', 500_000)
            t = await until([r"UK\.BIN\s+UK\b", r"LEN\.BIN\s+128K\b"], 120_000_000)      # a row needs a disk read
            print(t)
            good = bool(re.search(r"UK\.BIN\s+UK\b", t) and re.search(r"LEN\.BIN\s+128K\b", t))
            print("LISTSAVE names the builds:", good)
            ok &= good
            await boot()
            await typ('RUN"EDITSAVE\r', 500_000)
            await until("Save file")
            await typ("LEN.BIN\r")
            t = await until("Kills (<32768)")
            ok &= "128K" in t
            await typ("123\r")
            for _ in range(5):                      # jumps, cash, legal status, cloak and added missions keep their values
                await typ("\r")
            await until("Saved LEN.BIN")
            got = await disk_file("LEN.BIN")
            plain = saveedit.decrypt(got, KEY128) if got else bytes(104)
            kills = plain[13] + 256 * plain[14]
            print("EDITSAVE: kills", kills, "checksums", elitekey.checks_ok(plain))
            ok &= kills == 123 and elitekey.checks_ok(plain)

            # ---- 3. the trainer -----------------------------------------------------------------------------------------------------------
            await boot()
            await typ('RUN"TRAINER\r', 3_000_000)
            await typ("YYYYYYYYY", 300_000)      # nine cheats
            await typ("N", 300_000)              # unlimited hold: no -> POKE &998,25
            await typ("Y", 300_000)              # own cloak
            for ans in ("5000", "0", "300", "40", "0"):      # cash, mission, kills, jumps, added mission
                await typ(ans + "\r", 400_000)
            await c("breakpoint_add", {"kind": "pc", "address": 0x1C82})
            await c("run", {"max_us": 90_000_000, "timeout_s": 300})
            pc = (await c("registers_get")).get("pc")
            print("stopped at pc", pc)
            ok &= pc == 0x1C82
            await c("sna_save", {"path": "output/tools128_entry.sna"})
            snap = Path("output/tools128_entry.sna").read_bytes()
            row = cheat128.trainer_row()
            for j, a in enumerate(row[:11]):      # the nine groups poke 0, the pirate-boarding poke (the eleventh address) &C9
                want = 0xC9 if j == 10 else 0
                if bank_byte(snap, a) != want:
                    print(f"  poke {j} at {a:04X}: {bank_byte(snap, a):02X}, wanted {want:02X}")
                    ok = False
            hold = bank_byte(snap, 0x998)
            print("hold byte (N):", hold)
            ok &= hold == 25
            blk = lambda off: bank_byte(snap, G + off)
            print("block: cash", blk(18), blk(19), blk(20), blk(21), "jumps", blk(15), blk(16), "kills", blk(13), blk(14), "cloak byte", blk(92))
            ok &= (blk(18), blk(19), blk(20), blk(21)) == (5, 0, 0, 0) and (blk(15), blk(16)) == (40, 0) and (blk(13), blk(14)) == (44, 1) and blk(92) & 64 == 64
            ok &= bank_byte(snap, row[11]) == 0       # the galaxy-gate byte (jumps were asked for)
            # the game runs on: after the title is up the pokes are still in place (bank 7 holds the code block)
            await c("run", {"max_us": 40_000_000, "timeout_s": 300})
            await c("sna_save", {"path": "output/tools128_run.sna"})
            snap2 = Path("output/tools128_run.sna").read_bytes()
            moved = [bank_byte(snap2, a, 7 if a >= 0xC000 else None) for a in row[:10]]
            print("after the title:", [f"{m:02X}" for m in moved])
            ok &= all(m == 0 for m in moved)
            await c("screen_image", {"path": "output/tools128_title.png"})
            print("ALL OK" if ok else "FAIL")
            return ok


sys.exit(0 if asyncio.run(main()) else 1)

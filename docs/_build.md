# Building and checking

How to assemble the sources, what the switches do, what `check_src.sh` proves, and how to produce disks. The short version is in `README.md`; this is the full one.

## Requirements and inputs

- **Tools:** Python 3 (scripts run as `python3 -I`), [sjasmplus](https://github.com/z00m128/sjasmplus) 1.24.0 and iDSK, both built by `bash scripts/install-tools.sh` into `~/.local/bin` (pinned versions; not in Homebrew).
  `scripts/install-caprice32.sh` adds the Caprice32 emulator. cpcxray (via `uv tool`) runs the tests and the trainer tokeniser. RASM (`tools/bin/rasm`) is needed only for Fessor's source.
- **Disks:** the original `.dsk` images stay in the project root, untouched and untracked. The checker compares with files extracted from them:

  ```bash
  python3 -I tools/dskx.py Elite_UK_original_protected.dsk work/bin_stock      # English: .BIN files, AMSDOS header kept in .raw
  # German: work/bin_german, French: work/bin_fr (tools/dskx.py on Elite_DE_cracked.dsk and the French disk)
  ```
- Everything generated goes under `work/` (disks, snapshots, builds), `traces/` or `src/`; nothing is written to the project root.

## Source trees

| Tree | Build | Switches that apply |
|---|---|---|
| `src/elite/` | stock English (`LARGEAXX`, `COMMONXX`, `COMMON2X`, `MUSIQUEX`) | all |
| `src/elite_de/` | German | `ENHANCED`, `STAR_OCCLUDE`, `ESC_KEYCODE`, `TITLESEL` (its `musiquex.asm` differs only in six equates) |
| `src/elite_fr/` | French | `ENHANCED`, `STAR_OCCLUDE`, `ESC_KEYCODE`; no `TITLESEL`, no `MISSIONS` |

Each file starts with an `org` (`largeaxx` `&0840`, `commonxx` `&1A40`, `common2x` `&C000`, `musiquex` `&6000`) and assembles with plain `sjasmplus --raw=OUT.bin FILE.asm`. `INDICATO.BIN` and `PICTURE.BIN` are pixel data without source.

## Switches

A flag-less `sjasmplus` run gives the **original bytes** (plus the one-byte CPC+ keyboard fix in English and French; the German disk already has it). Everything else is a `-D` switch.

| Switch | Effect | Files |
|---|---|---|
| `ENHANCED` | `STAR_OCCLUDE` and `ESC_KEYCODE=0x7F` together; also the cash on the quantity line (English) | `commonxx.asm`, `largeaxx.asm` |
| `STAR_OCCLUDE` (`=1`/`=0`) | stars stay behind planet and sun; overrides `ENHANCED` | `commonxx.asm` |
| `ESC_KEYCODE` (`=0x7F`/`0xFF`) | key code of ESC in the keyboard table; `0x7F` leaves the buy, sell and equipment prompts | `commonxx.asm` |
| `TITLESEL` | choose the demo ship on the title screens | `commonxx.asm`, `musiquex.asm` |
| `MISSIONS` | added missions: stub, hooks, vector table, default flight image | `largeaxx.asm`, `commonxx.asm` |
| `FL_C` `FL_P` `FL_T` `FL_S` `FL_R` | with `MISSIONS`: which flight image goes in the `COMMONXX` tail (default image if none) | `commonxx.asm` |
| `OVL_C` `OVL_P` `OVL_T` `OVL_R` | with `MISSIONS`: which docked overlay goes after the stub | `largeaxx.asm` |
| `FIREBIRD` | the Firebird disk's `LARGEAXX` (`&0998`: `38 19` -> `38 00`, no hold-capacity test) | `largeaxx.asm` |

What each change does in the game: `_my_changes.md`.

## `make`

```bash
make stock            # work/build/stock/{en,de,fr}/      original bytes   (LOC=de or LOC=fr)
make enhanced         # work/build/enhanced/{...}/        -DENHANCED, plus -DTITLESEL except French
make missions         # python3 -I tools/build_dsk.py --missions work/elite_missions.dsk
make check            # check_src.sh for en, de, fr
```

`SJASM` overrides the sjasmplus path (default `~/.local/bin/sjasmplus`). `make stock` and `make enhanced` write the four `.bin` files only; they do not touch a disk.

## `tools/check_src.sh [de|fr]`

Assembles the four files of one tree and compares with `work/bin_stock` / `bin_german` / `bin_fr`. It exits 0 only if all of this holds:

1. `largeaxx`, `common2x`, `musiquex` are byte-identical to the originals.
2. `commonxx` without flags equals the original, with the CPC+ byte (`getPPI_Input` + 20 = `ED 49`) applied to the reference (not for German).
3. `commonxx -DENHANCED` differs from it only in the ESC byte (`tblKeyboardmatrix` + 66: `&7F` instead of `&FF`), the star-occlusion slots (`dustPlotPixel`'s space up to `ClearBitmap`, 16 bytes of the dust loop `dust70`), the English status/title labels and tabs, `cashHome` and the start operand of the escape-pod cargo clear (`podCleanOperand`, all three trees); `largeaxx -DENHANCED` (English) differs only in the 16-byte `clrLineCash` slot (`&08E7`), the operands of its two call sites and the status label, and its 104-byte save-key window (`EquipShip`) must equal the stock bytes. `-DENHANCED` without `STAR_OCCLUDE` is refused by an `ASSERT` (`cashHome` lives in the block it frees).
4. English: `-DMISSIONS` and `-DENHANCED -DMISSIONS` (the disk build) keep the lengths of `LARGEAXX` and `COMMONXX`.
5. English and German: `-DTITLESEL` (English also with `-DMISSIONS` and `-DENHANCED -DMISSIONS`) keeps the lengths, and the six `COMMONXX` addresses that `musiquex.asm` hard-codes (`setCommandsCPL`, `setCommandsNOP`, `transferBuffertoScreen`, `spawnCommandParser`, `dataFromPPI`, `splash2Shipnr`) are the real ones (English also with `-DMISSIONS`).
6. The three trees agree on the `ESC_KEYCODE` value.

It does **not** catch a rename that matched nothing; confirm with a grep count. Run it after every batch of edits, and `check_src.sh de` / `fr` after any rename that is applied to the other trees.

## Disks

All disk builders start from a **copy** of a base disk and refuse to modify the originals.

| Command | Base disk | Output | Notes |
|---|---|---|---|
| `python3 -I tools/build_dsk.py` | `Elite_UK_Firebird_cracked_trainer.dsk` | `work/elite_rebuilt.dsk` | the four files with `-DENHANCED -DTITLESEL` (LARGEAXX with `-DFIREBIRD`), AMSDOS headers kept, sizes must not change |
| `... --missions` | same | `work/elite_missions.dsk` | adds the mission overlays and flight images (assembled per tag), `README.TXT` |
| `... --de` | `Elite_DE_cracked.dsk` | `work/elite_de_rebuilt.dsk` | `--de --missions` is refused; there is no `--fr` |
| `bash tools/build_cheat.sh` | Firebird disk, mission disk | `work/firebird_cheat.dsk`, `work/missions_cheat.dsk` | tokenises `src/cheats/*.ASC` with the CPC's own BASIC (headless cpcxray), adds `CHEAT`, `SHOWSAVE`, `EDITSAVE`; `TRUMBLE.BAS` is built but not put on the disks |
| `python3 -I tools/hide_files.py DISK` | | in place | refuses a disk in the project root |

Every built disk shows only `.BAS` and `.TXT` files in `CAT`; all other files get the System attribute (`hide_entries` in `tools/hide_files.py`, called by `build_dsk.py`). iDSK adds files unhidden, so hide again after any
`iDSK -i` or `-r`. Check with `CAT` or the directory bytes, not `iDSK -l` (it lists hidden files). The disk README is `src/disk/README.TXT` (ASCII, CRLF, Ctrl-Z). A built disk's boot test: `RUN"ELITE`.

Raw build of the mission game without `build_dsk.py` (to look at bytes only, the overlays and images are missing):

```bash
sjasmplus -DENHANCED -DTITLESEL -DMISSIONS -DFIREBIRD --raw=out/LARGEAXX.BIN src/elite/largeaxx.asm
sjasmplus -DENHANCED -DTITLESEL -DMISSIONS            --raw=out/COMMONXX.BIN src/elite/commonxx.asm
sjasmplus                                             --raw=out/COMMON2X.BIN src/elite/common2x.asm
sjasmplus -DTITLESEL                                  --raw=out/MUSIQUEX.BIN src/elite/musiquex.asm
```

## Editing the source safely

- `src/elite/` is hand-edited. **Never rerun `tools/disasm_stock.py` into it** (it overwrites); use a scratch directory (`python3 -I tools/disasm_stock.py /tmp/x`). Same for `src/elite_de/` (`map_german.py` + `disasm_german.py`) and `src/elite_fr/`.
- Renames: for `dat_` labels use `tools/rename_dat.py` with a map in `tools/rename_maps/` (`--all-trees` applies it to German and French too; it refuses a name used twice). Otherwise `perl -pi -e 's/\bold\b/new/g'`
  (BSD `sed` has no `\b` and silently changes nothing), then a grep count, then `check_src.sh` for all three trees.
- Keep the mission tails honest: the stub plus the Constrictor overlay fill `&1714-&1A3F` exactly, the largest flight image is 608 of 610 bytes, and `ASSERT`s guard the fixed addresses (`&1714`, `&9D9E`, `&9FFE`). See `_memory_map.md`.
- A new language: extract the disk with `tools/dskx.py` into `work/bin_X/`, add it to `LOCALES` in `tools/map_locale.py` and `tools/disasm_locale.py`, run both, add a branch to `check_src.sh`, and check `getPPI_Input` for the CPC+ fix (`out (c),c` = fixed).

## Tests and the emulator

The tests in `tools/test_*.py` run in cpcxray from `work/xray/` with cpcxray's own Python, after a disk build and a copy of the disk to `work/xray/disk/`:

```bash
export PATH="$HOME/.local/bin:$PATH"
cd work/xray && ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_launch.py
```

Suites: `test_mission_hook`, `test_launch`, `test_mission_flight`, `test_plans`, `test_stolen_ship`, `test_rocks`, `test_trumbles`, `test_trumble_sprites`, `test_flight_hull`, `test_title_ships` (`[de]`), `test_star_occlusion`.
Run long sweeps in the background (`nohup ... &`, one output file each); the foreground limit is 2 minutes. They force game states and call routines directly; they do not replace a real playthrough.

**Driving cpcxray from a script.** Start `cpcxray mcp --config config/cpc6128.toml` with `mcp.client.stdio.stdio_client(StdioServerParameters(command="cpcxray", args=["mcp", "--config", "config/cpc6128.toml"]))` (paths like `config/` and `disk/` are relative to `work/xray/`);
`streamable_http_client("http://127.0.0.1:8765/mcp")` attaches to a running GUI instead. Wrap `session.call_tool(name, args)` in a small helper. Tools used: `disk_insert`, `type_text`, `run`, `run_until`, `sna_load`, `sna_save`,
`memory_read`/`memory_write`/`memory_view`/`memory_save`, `registers_set`, `breakpoint_add`/`breakpoint_list`, `key_press`/`key_release`, `screen_image`.

| Topic | Rule |
|---|---|
| Disks | `disk_insert` takes `drive` (`"A"`) and `path`, read-only by default; insert **before** `sna_load`, or the game stops at "Drive A: disc missing" |
| Start states | `output/firebird_in_flight.sna` is the game just launched: use it for flight routines. `output/firebird_at_entry.sna` is the docked layout at `&1C82` (its `&0038` interrupt still jumps into the bitmap), so it is the wrong state for flight code |
| Booting from the disk | wait about 4 s for BASIC, `type_text('RUN"ELITE\n', wait=False)`, then `run`; the title screen appears after about 19 s of emulated time |
| Time | `run(max_us=..., timeout_s=...)` reports `time_limit`, not a breakpoint stop; count breakpoint hits with `breakpoint_list`. The interrupt phase is not deterministic, so compare runs with interrupts off (`registers_set iff1=0`) |
| Keys | the game polls the keyboard: hold a key 1.2-1.5 s of emulated time (`key_press`, `run`, `key_release`); shorter holds are missed. Names are `cursor_left`, `cursor_up`, `space`, `return`, `f1`, `a`... (not `left`/`up`); text prompts need taps of about 0.33 s (0.25 s misses, longer types twice) |
| Reading memory | `memory_view` and `memory_read` show ROM under the lower ROM and `view="ram"` returns zeros. Use `view="ram:0"` for RAM below `&4000` (the `:N` is a 16 KB block with offset `address & &3FFF`, so `ram:0` is wrong above `&4000`) and `view="cpu"` above. For a whole-RAM comparison use `sna_save` and read the 64 KB after the 256-byte header (a 128 KB snapshot starts with the same flat 64 KB) |
| Stop points | stop at `handleEntitys` (`&5066`) before injecting calls and restore all registers afterwards; stopping elsewhere (the fill routines use SP as a write pointer inside the bitmap) corrupts the run. `run_until` an address below `&4000` can stop early inside the OS ROM |
| Writes | `memory_write(address, data="3E 05")`; `registers_set(values={"pc": 0x9000})`; `breakpoint_add(address, kind="pc"|"write")`; `bus_trace_read` returns the last 100 records unless `last=` (max 2000) |
| Looking | the GUI flickers (it draws unsynced); use `screen_image` for screenshots (`output/*.png`) and cpcxray for tracing, a real emulator (Virtual Retro) to play |
| In-game steps | `5` galactic chart, `6` short range chart, `7` data on present system, `h` hyperspace to the system nearest the chart cursor (needs fuel; keep the cursor within about 7 LY, e.g. a 0.2 s `cursor_left` tap from Lave reaches Diso); the cursor lives at `PresentPlanetX/Y` `&3934/&3935`; the planet is `posDataPlanet` `&1C2F`, the sun `posDataSun` `&1C26` |
| Symbols | `sjasmplus --raw=o.bin --lst=x.lst --sym=x.sym src/elite/commonxx.asm` into a scratch directory gives addresses; grep the `.lst` for an address |

Test patterns that work: start from the in-flight snapshot, stop at `handleEntitys`, write the freshly assembled patches, set variables, call a vector with a trap return address, restore registers. Missions mostly use forced state values
(`_missions_built.md` section 5 and 7).

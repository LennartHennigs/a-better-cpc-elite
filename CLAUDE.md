# CPC Elite

Goal: disassemble and edit an old abandonware Amstrad CPC game (Elite) from `Elite_UK_original_protected.dsk`, then
write the modified build back to a DSK image that runs on a CPC emulator.

## Rules

- **Never modify the original disks in the project root** (`Elite_UK_original_protected.dsk`,
  `Elite_DE_cracked.dsk`, `Elite_UK_Firebird_cracked_trainer.dsk`, `Elite_DE_savegames.dsk`). Work on copies.
- Keep generated output (extracted binaries, disassembly, snapshots, traces) out of the project root:
  `work/` for disks, snapshots and extracted files, `src/` for annotated assembly, `traces/` for traces.
- Target is Z80 on a CPC 464/6128. Write assembly in sjasmplus syntax (cpcxray generates it and uses it for
  its round-trip check). RASM stays an option for writing DSKs.
- Keep AMSDOS headers intact when writing binaries back to disk (load address, exec address, length, checksum).
- On every disk we build, `CAT` shows only `.BAS` and `.TXT` files (`ELITE.BAS`, our `CHEAT/EDITSAVE.BAS`, `README.TXT`); every other file (`.BIN` code,
  mission overlays, flight images) gets the System attribute. `tools/build_dsk.py` does it for all its variants, `tools/hide_files.py DISK` for finished images
  (`tools/build_cheat.sh` calls it); iDSK adds files unhidden, so hide again after any `iDSK -i` or `-r`. Check with `CAT` or by reading the directory, not `iDSK -l` (it lists hidden files).
- Keep the save-game XOR key intact: the 104 bytes at `EquipShip` (`LARGEAXX` file offset `&2BE` stock, `&2C2` German) decode every commander save, so plans should leave them as they are. If a plan would change or move them (a tweak in that code, a shifted table before it, a different build flag), tell the user before doing it.
- Fessor's material stays out of the repo and is not re-uploaded; see `extended/CLAUDE.md`. Exception, by his private mail and the user's later go-ahead (2026-11-14): the Constrictor hull (`src/elite/missions_hull.asm`), the ship hulls in `src/elite/missions_ships.asm` (made by `tools/fessor_ships.py`, ship packs, `docs/_ship_packs.md`) and the use of his names and findings in the source, credited in `README.md`.
- `scripts/build-fessor.sh` builds Fessor's source in `work/build_fessor_run/` and compares with the beta disk (user runs it).
- Building downloaded source in Bash is blocked by the permission classifier. Put it in a script under
  `scripts/` and ask the user to run it (`! bash scripts/…`); do not try to work around the block.

## Layout

- `extended/` Fessor's downloaded archives, source, symbols and saved forum pages (read-only, do not re-upload; see `extended/CLAUDE.md`).
- `tools/` helper scripts; `tools/bin/rasm` is the locally built RASM. `scripts/` installers, run by the user.
- `work/bin_stock/` stock files from `Elite_UK_original_protected.dsk` (`.raw` keeps the AMSDOS header); `work/stock_bin/` the
  three code files for `tools/map_labels.py`; `work/bin_ext/` Fessor's beta; `work/build_fessor/` his source
  plus build output (do not run `rasm` on its other `.asm` files: it overwrites `rasmoutput.sym`); `work/prot/` protection
  dumps; `work/xray/` the cpcxray project; `work/stock_mem_image.bin` the three code files laid out in a 64K image;
  `work/musiquex.sym` the music player's labels at stock addresses.
- `magazines/` period scans plus extracted text (Amstrad Action 3, Amtix 13); `docs/` notes by topic (canonical and tracked; start with `_build.md`, `_my_changes.md`, `_memory_map.md`, `_open_questions.md`; `_missions_built.md` the implemented missions; there is no `docs/notes.md`, the topic files are the index); `docs_other/` untracked internal notes (Fessor, history, plans, Spectrum map, third-party text); `CHANGELOG.md` and `TODO.md` track changes and open work; the root is a git repo (`.gitignore` keeps `extended/`, `work/`, disks and scans out).
- `src/cheats/` tracked: `CHEAT.ASC` (source of our interactive trainer, stage one), `CHEATB.ASC` (stage two: loads the game, detects the UK, German or French build, pokes; on the disks as hidden `CHEATB.BIN`), `CHEAT.BAS` (its tokenised file) with its listing `CHEAT.BAS.txt`, and `CHEAT_ORIGINAL.BAS.txt` (listing of the CHEAT.BAS on the Firebird disk); `tools/build_cheat.sh` rebuilds the `.BAS` and `work/firebird_cheat.dsk`, `work/de_cheat.dsk`, `work/fr_cheat.dsk`. `SHOWSHIP.BAS` (ship viewer, `src/cheats/showship.asm` is its Z80 frame routine, made by `tools/mk_showship.py`, built by `tools/build_showship.sh` into `work/showship.dsk`; `build_dsk.py --missions` adds it and our `CHEAT.BAS` to the mission disk; `docs/_cheats.md`). Add files to the Firebird-based disks with `dskx` (as `build_dsk.py` does), not iDSK: iDSK may fill the two odd-sector tracks, which AMSDOS cannot read (`Drive A: read fail`); the viewer data must also stay below `&A67B` while loading.
- `tools/proto_fill/` filled-ship prototype for a 6128 (`docs/_filled_ships.md`): `python3 -I tools/proto_fill/gen.py [--ships]`, `run.py [--flip]` (from `work/xray`, cpcxray interpreter), `mkdsk.py` -> `work/proto_fill/proto.dsk`. It uses ArcElite's ship table (`work/arcelite/`, third party: never copy it into the repo; everything derived stays in `work/proto_fill/`).
- `README.md` project overview (spoiler-free on the missions). `src/disk/README.TXT` is the short text written onto the mission disk, where the build also hides every file that is not `.BAS` or `.TXT` (rule under Rules). `src/cheats/` also has `EDITSAVE.BAS` and `LISTSAVE.BAS` (generated by `tools/mk_editsave.py` and `tools/mk_listsave.py`, which share `tools/savekeys.py`; built by `tools/build_cheat.sh`, which also writes `work/missions_cheat.dsk`); `LISTSAVE.BAS` (from `tools/mk_listsave.py`, on `work/de_savegames.dsk`, whose saves stay visible so `CAT` shows them); `tools/saveedit.py` edits saves on the host; `docs/img/` holds screenshots.
- `work/ext_elitea/` (Elite-A, markmoxon/elite-a-source-code-bbc-micro), `work/arcelite/` (ArcElite unpacked, `docs/_arcelite.md`), `work/ext_st/`, `work/ext_nes/`, `work/ext_msx/` shallow clones of the Atari ST (`ataribaby42/elite-source-code-atarist`), NES (`markmoxon/nes-elite-beebasm`) and
  TI-99/4A-from-MSX (`Rasmus-M/elite-ti994a`) sources, plus in `work/ext_msx/` the ZX Spectrum SkoolKit disassembly (`skoolkit/`, the closest annotated relative of the CPC code) and the MSX one (`ricbit/`), read-only references for the missions (links in `docs/_references.md`); copyrighted, do not copy them into the project or build them.
- `src/elite/` reassemblable source of the stock English build (see its README); `traces/` holds the `tools/dead_trace.py` results (`dead_run*.json`).
- `src/elite_de/` reassemblable source of the German build (`bash tools/check_src.sh de`; names and comments transferred from `src/elite` by `tools/map_german.py` + `tools/disasm_german.py`, see its README).
- `src/elite_fr/` reassemblable source of the French build (`bash tools/check_src.sh fr`; `tools/map_french.py` + `tools/disasm_french.py`, files in `work/bin_fr/`; `[a]` repack in `work/bin_fr_a/`). The two French disks are in the project root next to the others; never modify them.
- Another localized build (French done): extract the disk with `tools/dskx.py` into `work/bin_X/`, add an entry to `LOCALES` in `tools/map_locale.py` and `tools/disasm_locale.py` (`map_german.py`/`map_french.py` are thin wrappers; copy one), run both, then add a branch to `tools/check_src.sh`. Check `getPPI_Input` for the CPC+ fix (`out (c),c` = fixed).
- Third-party disk images belong in `work/` (e.g. `work/plus_patch/`), never `tools/` or the root.
- `work/elite plus/` PC Elite Plus (`ELITE.EXE`, EXEPACK, a hacked build); `extracted/` has the unpacked image and strings. Unpack with `python3 -I tools/unexepack.py IN OUT.EXE OUT.IMG`. Its mission logic is in `docs/_missions.md` section 4 ("Elite Plus code"); no source exists, only this EXE and [rembish/elite-plus-revamp](https://github.com/rembish/elite-plus-revamp) (decompilation in progress).

## Disks (details and hashes in `docs/_disks.md`)

- Disks were renamed 2026-11-07 (old names in `docs/_disks.md`): `Elite_UK_original_protected.dsk`, `Elite_UK_Firebird_cracked_trainer.dsk`, `Elite_DE_cracked.dsk`, `Elite_DE_savegames.dsk`.
- `Elite_UK_original_protected.dsk` is the UK original ("Version GOLD", CPC Power #1): 41-track extended DSK, all files carry the
  System attribute so `CAT` shows nothing, with decoy directory entries and a protected `ELITE.BAS`.
  SHA-256: `e50a6627d98da88f74d3207fc953c3c4d9960b1f190aedc0a5c695d3e9de1b76`.
- `Elite_UK_Firebird_cracked_trainer.dsk` is the same English game, unprotected, plus `CHEAT.BAS`. Start here.
  The original `CHEAT.BAS` on this disk has a wrong cloak entry. Our interactive trainer is also called `CHEAT.BAS` (`src/cheats/CHEAT.ASC`); on `work/firebird_cheat.dsk` it replaces the original (`RUN"CHEAT`, see `docs/_cheats.md`). Cloak key is `Y`.
- `Elite_DE_cracked.dsk` is the German build (same program, German text; already has the CPC+ keyboard fix; source in `src/elite_de/`).
- `Elite_DE_savegames.dsk` holds four 104-byte commander saves.
- Tracks 1 and 40 of the 41-track disks use odd sector IDs but hold only `0xE5` filler: not a loader.

## Game facts

- Load sequence (plain `ELITE.BAS`): picture to `&C000`, `largeaxx` to `&840`, `commonxx` to `&1A40`,
  `common2x` to `&C000`, then `CALL &1C82`. `&1C82` is the entry point.
- `CHEAT.BAS` gives poke addresses in the English build (see `docs/_cheats.md`); they anchor routine names.
- The CPC port is a Spectrum port, not a BBC port. Use the annotated 6502 sources only for naming and logic.
- Fessor's RASM reconstruction of the game and his beta are in `extended/` (downloaded 2026-11-07, do not
  re-upload). `extended/reference/symbolsEnglishVersion.asm` holds 157 symbols that are correct for the stock game.
  His source builds the patched game only; switching all patch flags off does not give the stock bytes.
  The `.rar` files are RAR5: use `bsdtar`, not `7z` (17.05).
- CPC tokenised BASIC: constants `0x0E–0x18` are 0–10, `0x19` is a byte, `0x1A` an int16, `0x1C` hex,
  `0x1F` a 5-byte real, `0x01` is `:`, `0xFF` prefixes functions. `CAT` on `Elite_UK_original_protected.dsk` shows only `0K free`
  (a decoy entry; the real files are System-hidden); use `iDSK x.dsk -l` or `tools/dskx.py` instead.
- `Elite_UK_original_protected.dsk` is protected by ARMOURLOC v1.1. `LOAD"ELITE.BAS` is wiped by BASIC on return to the prompt
  (flag `&AE2C`); to read it, stop at `&C06A` and write `0` to `&AE2C`. Details in `docs/_disks.md`. `RUN` is fine.

## Toolchain (macOS, Apple Silicon)

| Purpose | Tool | Status |
|---|---|---|
| Analysis emulator | **cpcxray** 0.9.4 (traces, disassembly, sjasmplus output, MCP server) | Installed with `uv tool`; `~/.local/bin/cpcxray` (not on PATH). Project folder `work/xray/`. Headless MCP and GUI both work. |
| Other emulators | RVM 2.1 (play and compare; installed in `/Applications`, no remote interface: its debugger has only PC `break`, `poke`, `load`/`save`), MAME (traces, not installed), **konCePCja** (sector editor; see below) | konCePCja: source only in `work/ext_koncepcja/` (v6.6.0, not built, not installed) |
| konCePCja for live memory tracking | Unlike RVM it has a TCP text protocol on `localhost:6543` (`docs/ipc-protocol.md` in its clone: `wp add <addr> [len] [r\|w\|rw]` watchpoints, memory read and search, breakpoints, `step`, `wait pc`), so Claude can drive it like cpcxray without the cpcxray GUI's keyboard problem. Needs a build (macOS, see its `AGENTS.md`/`CMakeLists.txt`; building downloaded source in Bash is blocked, so put it in a script under `scripts/` and ask the user to run it). Used once for the parked-RAM check (`TODO.md`); the build script and the watcher were deleted 2026-11-15 (never committed), so a new use needs both rewritten | Not built here |
| DSK read and write | iDSK | Installed at `~/.local/bin/iDSK` (built by `scripts/install-tools.sh`). `iDSK x.dsk -l` lists, including hidden System files. |
| Tape images | **CDTconvert** 1.0 (CDT/TZX to WAV, `-l` lists blocks) | `~/.local/bin/CDTconvert` (installed by `scripts/install-cdtconvert.sh`); `tools/cdt_direct_decode.py` decodes the English tape's direct-recording block (`docs_other/_tapes.md`) |
| Disassembly | cpcxray first; z80dismblr (unmaintained but works); Ghidra if cross-references are needed | z80dismblr and Ghidra not installed |
| Assembler | **sjasmplus** (needed by cpcxray's `source-verify`), RASM as optional | sjasmplus 1.24.0 installed at `~/.local/bin/sjasmplus` (built by `scripts/install-tools.sh`; not in Homebrew). RASM 3.3.2 is built locally at `tools/bin/rasm` (needed for Fessor's source; not in Homebrew; rebuild with
`cc -O2 -DNO_3RD_PARTIES -DNOAPI -o rasm rasm.c -lm -lpthread`, the repo's makefile fails to link) |
| Project scripts | `scripts/` has installers (run by the user); `tools/` has the helpers, each with a header docstring: `dskx.py` (list and extract AMSDOS files), `build_dsk.py`, `build_cheat.sh`, `check_src.sh`, `saveedit.py`/`savedec.py`/`elitekey.py` (saves), `bastok.py` (detokenize BASIC), `elitetext.py`, `map_labels.py`, `map_german.py`/`map_french.py` + `disasm_*.py` (regenerate `src/elite_de/`, `src/elite_fr/`), `z80dis.py` + `disasm_stock.py` (verify `src/elite/`), `deadcode.py`/`dead_trace.py`/`dbcode.py` (dead-code checks; all candidates turned out live, `docs/_architecture.md`), `spectrum_map.py` + `apply_spectrum_names.py` (`docs_other/_spectrum_map.md`), `circle_sweep.py`, `test_*.py` (cpcxray tests) | Plain Python 3, run with `python3 -I` |

```bash
make original [LOC=de|fr]                              # stock bytes on a disk -> work/elite_original*.dsk
make expanded                                                # viewer, trainers, missions, ship packs on one disk -> work/elite_expanded.dsk (English only)
bash tools/check_src.sh [de]                                 # assemble src/elite (or src/elite_de) and compare with the original binaries
python3 -I tools/dskx.py Elite_UK_original_protected.dsk work/bin_stock          # list and extract (AMSDOS headers kept in .raw)
python3 -I tools/map_labels.py work/build_fessor work/build_fessor/rasmoutput.sym work/stock_bin \
    work/fessor_to_stock.sym extended/reference/symbolsEnglishVersion.asm        # add --eval to score the method
cd work/build_fessor && ../../tools/bin/rasm EliteMasterSource.asm -s -sq   # patched build + symbols
python3 -I tools/bastok.py FILE                              # detokenize BASIC (--header if AMSDOS header)
```

16-bit x86 (Elite Plus): no `ndisasm` or `objdump`; use capstone in a scratch venv (`Cs(CS_ARCH_X86, CS_MODE_16)`). `ELITE.img` has DS base `0xB000` (data offset = file offset - `0xB000`). Mission text is script-like (x/y bytes), so find logic through variables (`DS:83A0` mission, `83A2` state, `83A3` target system, `836B` legal status) by searching for their little-endian bytes.

Shell gotcha (zsh): `echo =====` fails (`= expansion`); use `printf -- '---\n'` for separators, and quote or `${=VAR}` variables you want word-split.

Run cpcxray with `export PATH="$HOME/.local/bin:$PATH"`, then `cd work/xray && cpcxray gui --config
config/cpc6128.toml` (its MCP server listens on `127.0.0.1:8765`). Mount disks read-only
(`disk_insert` defaults to read-only).

Scripting cpcxray: use its own interpreter, `~/.local/share/uv/tools/cpcxray/bin/python -I script.py`, with
`mcp.client.stdio.stdio_client(StdioServerParameters(command="cpcxray", args=["mcp"]))`. Run from
`work/xray/` (paths like `config/cpc6128.toml` and `disk/x.dsk` are relative). Attaching to the running GUI
uses `streamable_http_client("http://127.0.0.1:8765/mcp")`, which yields two streams, not three.
Useful tools: `disk_insert`, `type_text`, `run_until`, `sna_load`/`sna_save`, `memory_save`, `disassemble`.
Gotchas: `memory_view` and `memory_read` show ROM under the lower ROM, and `view="ram"` returns zeros. Use
`view="ram:0"` (or `ram:N`) for RAM, or `view="cpu"` after paging. Argument names: `memory_write(address, data="3E 05")`,
`registers_set(values={"pc": 0x9000})`, `breakpoint_add(address, kind="pc"|"write")`. For boot-time work use
`type_text(text, wait=False)` then `run(max_us=...)`. Plain stdlib JSON-RPC over `cpcxray mcp --config config/cpc6128.toml` also works.
Test routines in flight, not from `firebird_at_entry.sna` (its memory is the docked layout: the ISR at `&0038` still jumps into the bitmap); `output/firebird_in_flight.sna` is the game just launched (`docs/_architecture.md`). cpcxray quirks: `bus_trace_read` returns the last 100 records unless `last=` (max 2000); a non-deterministic interrupt phase makes single runs differ, so compare with interrupts off (`registers_set iff1=0`). Driving the game: `disk_insert disk/Elite_UK_Firebird_cracked_trainer.dsk` BEFORE `sna_load output/firebird_at_entry.sna` (else "Drive A: disc missing"),
run ~8 s, then hold `n` and `space` 1.2 to 1.5 s each (`key_press`, `run`, `key_release`); shorter holds are missed. `run` reports
`time_limit`, not a breakpoint stop: count hits with `breakpoint_list`. The GUI flickers constantly (draws unsynced to the emulated
frame); play and test visually in Virtual Retro, use cpcxray for tracing. Label addresses: `sjasmplus --raw=o.bin --lst=x.lst --sym=x.sym
src/elite/commonxx.asm` into a scratch dir. Key to flag mapping: `tblKeyboardMatrix2` (`&8D37`, line*8+bit; code>>3 is the `&8D87` byte, code&7 == 0 is bit 7).

## Workflow

1. Boot the Firebird disk in cpcxray. Snapshot at `&1C82`: `work/xray/output/firebird_at_entry.sna`
   (reload with `sna_load`); the image and disassembly of `&0840-&9FFF` are beside it.
2. Disassembly is done for the stock English build (`src/elite/`, byte-exact). Cheat addresses, missions and known
   variables are tracked in `docs/_cheats.md` and `docs/_gameplay.md`.
3. Improve `src/elite/` (names, `dw` tables, comments). Once you hand-edit the `.asm` files, **never rerun
   `tools/disasm_stock.py` into `src/elite`** (it overwrites them); give it a scratch directory instead
   (`python3 -I tools/disasm_stock.py /tmp/x`). After every change assemble with sjasmplus and compare with `work/bin_stock/*.BIN` (the README shows how)
   before changing any behaviour.
4. Write rebuilt binaries into a copy of the DSK (keep the AMSDOS headers) and test.
5. Diff against other builds (German `[G]`, CPC+ patch) once the English code is understood.
6. After a big rename or comment batch in `src/elite/`, regenerate the German names into a scratch dir first (`python3 -I tools/map_german.py && python3 -I tools/disasm_german.py /tmp/de`) and diff against `src/elite_de/`; never write over `src/elite_de/` once it is hand-edited.

Gotchas:
- Docs: `docs/_*.md` (architecture, build, my_changes, cheats, cpcplus, disks, gameplay, memory_map, missions, missions_built, open_questions, references, savegame, ship_occlusion, filled_ships) are canonical and tracked; `docs_other/` (untracked: fessor, history, mission_build_plan, spectrum_map, the GameFAQs guide copy) holds internal notes, split by topic; there is no `notes.md`. Edit the `docs/` file when you change a fact.
- Source comments and `TODO.md` cite doc sections (`docs/_missions.md section 3`); after moving or renumbering docs, grep `src/`, `TODO.md` and `docs/` for the old name or section.
- Whole-RAM compare in cpcxray: `sna_save`, then read 64 KB at offset `0x100` of the .sna (flat RAM layout, also for 128 KB snapshots). Memory layout and the `&0040-&1A3F` / `&A600-&BFFF` swap: `docs/_memory_map.md`.
- Double-buffer experiment on Fessor's source (the scripts and tests are on branch `double-buffer`, not on `addon-missions`; untracked write-up `docs_other/_double_buffer_experiment.md`): the user runs `bash scripts/build-fessor-dbuf.sh [adresschange|mylinedraw|banks]` (building his source is blocked for you; it patches a copy in `work/dbuf`), then `bash tools/dbuf_disk.sh`, then from `work/xray` the cpcxray python runs `tools/test_dbuf.py` (title) or `tools/test_dbuf_flight.py` (title to flight, saves `output/dbflight_state.sna`). Check `work/dbuf/EliteMasterSource.asm` for the flags and patch markers to see whether the user's build really ran.
- cpcxray scripting: `breakpoint_add(address, end=, kind="pc"|"write")` takes a range; `breakpoint_remove` wants `breakpoint_id`; time with `machine_status["clock_us"]` (`emulated_us` in `run` results is per call); `trace_read` returns at most 1000 lines; `step` single-steps; `sna_load` restores a saved scenario (128K .sna: the first flat 64 KB are banks 0-3).
- Runs longer than about 100 s: start them detached with `python3 -c "subprocess.Popen([...], start_new_session=True, stdout=open(f,'w'), stdin=subprocess.DEVNULL)"` and poll the output file (macOS has no `setsid`; a plain `nohup ... &` dies when the call ends). Save a snapshot at the interesting state instead of rerunning the whole boot.
- Web pages behind Cloudflare (GameFAQs, CPCWiki and similar) return 403 to `curl` and WebFetch. Use Claude in Chrome: `navigate`, then `javascript_tool` with `document.querySelector('#faqwrap').innerText` (or `get_page_text`). Save third-party text under `docs/` with its source URL in the header.
- `rtk` truncates long Bash output ("+N more … see log"). For big greps or counts use the Read tool or a `python3 -I` script. In zsh an unmatched glob such as `--include=*.asm` aborts the command: drop the flag or quote it.
- Best annotated relative of the CPC code: `work/ext_msx/skoolkit/src/elite.skool` (ZX Spectrum, per-line comments). It uses the same `Missionflag` byte, Asp spawn and shared state byte (`aspMissionState` = Spectrum `$9CB2`). `ricbit/` is the MSX disassembly (one-line comments only). In `work/ext_st/repo`, read `src_orig/` for the original logic; `src_atari/` is a modified build.
- In docs, cite CPC routines by label (`spawnCommand0`, `targetisKilled`) unless you checked the address in the listing or a trace. Label names in `src/elite/` are stable; guessed `&xxxx` values are not.
- Spectrum map workflow: `python3 -I tools/spectrum_map.py && python3 -I tools/spectrum_data_map.py && python3 -I tools/gen_spectrum_map_doc.py` regenerates `work/spectrum_map/` and `docs_other/_spectrum_map.md`; renames go through `tools/rename_dat.py` with a map in `tools/rename_maps/` (it refuses a name already used). From the Spectrum disassembly take only names and addresses; write comments in our own words from the code and mark matches `; ZX Spectrum: name (&ADDR)`.
- `tools/z80dis.py` decodes `push/pop ix/iy` and `ex (sp),ix` since 2026-11-11 (the `uses_hl` check lacked `push`); `tools/relabel.py TARGET REFERENCE --write` folded 33 `db` runs of `src/elite` into labelled instructions on 2026-11-11 (`check_src.sh` still byte-exact); `src/elite_de`/`src/elite_fr` still have them.
  Never regenerate the hand-edited trees: `tools/disasm_stock.py OUTDIR` into a scratch dir gives the fixed reference (`traces/dyn_seeds.json` adds code seeds found by running the game with `tools/exec_in_data.py`; data ranges from
  `tools/db_ranges.py`), then run `relabel.py` (it restores the file unless both flag variants assemble to the same bytes). Back up `src/elite/` before bulk edits (`work/backup_src_pre_spectrum/` is the pre-Spectrum copy) and run `bash tools/check_src.sh` after each batch.
- Foreground Bash stops at 2 minutes: run long cpcxray sweeps in the background (`nohup ... &`, one output file each) and check the logs; `tools/circle_sweep.py` takes about 5 ms per call.
- `MUSIQUEX.BIN` loads at `&6000` over `COMMONXX`'s `&6000-&6FFF` (while the music plays; `NOTMUSIC.BIN` is that slice of `COMMONXX`). Never lay both into one image when decoding or comparing code: use `COMMONXX` alone, as `tools/map_german.py` does.
- Scans of raw disk images can double-count: `Elite_DE_cracked.dsk` holds `COMMONXX` twice (tracks 7 and 27). Its AMSDOS headers have load address 0 except `COMMONXX.BIN` (`&1A40`); set the others when writing a DSK.
- To find every use of a variable, grep all of `src/elite/*.asm` for both the label and the number (`0x38E1`): `largeaxx.asm` and `common2x.asm` use raw addresses for variables that `commonxx.asm` labels.
- Fessor-vs-stock comparisons by label anchors (`work/fessor_to_stock.sym`) give false "changed" reports when an anchor is a few bytes off; read the routine in both builds before reporting a change. `extended/FESSOR_VS_STOCK.md` marks which findings are unverified.
- zsh does not word-split unquoted variables: `set -- $p` leaves one argument. Use `${=p}` or a plain loop over explicit names.
- Renames and deletes of ignored files (`work/`, `extended/`, disks) have no undo, since git does not track them. Check each reference first (`grep -rn OLDNAME CLAUDE.md docs src tools scripts extended/*.md`) and update docs in the same step.
- RASM `SAVE ...,AMSDOS` output has a 128-byte header; strip it (`[128:]`) before comparing with `work/bin_*/*.BIN`.
- Commander saves: 104 bytes at `&38CB`, XORed with the code at `EquipShip` (`LARGEAXX` file offset `&2BE` stock,
  `&2C2` German). A save only decodes with its own build's key; the `Elite_DE_savegames.dsk` saves are German.
  Use `tools/savedec.py SAVE DISK.dsk` (the key is read from the disk by `tools/elitekey.py`); the field map is in `docs/_savegame.md`.
  Credits are a word pair (high word counts 1,000 Cr, low word the decicredits below 10,000), not a 32-bit number.
- To find which build a blob belongs to, XOR-scan it against every `work/bin_*/*.BIN` for known plaintext.
- `Elite - Gold.dsk` was deleted (it was `Elite_UK_original_protected.dsk` plus a stray `TES.BIN`). `extended/` has its own `CLAUDE.md`.

Watch for self-modifying code (the line plotters are self-patched): confirm static results with traces.
Elite swaps `&0040-&1A3F` with `&A600-&BFFF` at runtime, so the BASIC program at `&170` is destroyed once
the game runs. Dump it early (a write breakpoint on `&840` fires just after the loader starts).

Poke and patch addresses are often operand bytes. Disassemble from `addr-1` to `addr-4` and keep the start
that lands on `addr` as a boundary and decodes sensibly; do not trust a decode that begins at `addr`.

## Open items

- Star occlusion (`STAR_OCCLUDE`, on with `-DENHANCED`, off = stock bytes by default, all three trees; `ESC_KEYCODE` likewise): `dustPlotPixel` lives in the dead `unusedViewBorderFill` (`&1FD2-&1FF0`, 3 bytes left; `cashHome` takes `&1FEA-&1FF0` for the cash on the quantity line (`clrLineCash` in `LARGEAXX` `&08E7`, `-DENHANCED`, English)) and is
  called from the dust loop `dust70`. `check_src.sh` proves it (default = original bytes; `-DENHANCED` differs only in those two slots and the ESC byte). Ship hulls stay
  see-through: `docs/_ship_occlusion.md` (options A/B/C, not built).
- Screens of a planet and sun: `tools/test_star_occlusion.py [off] [far] [sun]` (run from `work/xray`, PNGs in `output/stars_*.png` via cpcxray `screen_image`). In flight
  the planet is `posDataPlanet` `&1C2F` and the sun `posDataSun` `&1C26` (x, y, z, 3 bytes each); `&1A40+7` is not the planet.
- `tools/build_dsk.py` builds English, `--missions`, `--de` and `--fr` disks (the French one boots with `RUN"EL`).
- Free flight-time space is only the 610 zero bytes at `&9D9E-&9FFF` (top bytes carry stack pushes at `&A000`) plus 10 bytes of `unusedGet*` (`unusedViewBorderFill` is now used); the "130-155 bytes of dead code in db runs" were live (`docs/_architecture.md`, with the list of dynamic labels). Mission idea: load missions one at a time as overlay files, order per commander (`docs/_missions.md`).
- Ship packs and traffic (`docs/_ship_packs.md`): `-DMISSIONS` flight images `MFLIGHT1-7` carry Fessor's extra hulls (`src/elite/missions_ships.asm`, `missions_flight_k.asm`, picker in `mxLaunchEntry`: `(jumpCounter + presentSystemSeed) & 7`, 0 = default image), the Trumbles image is at 607 of 608 bytes; `-DTRAFFIC` (all three trees, on in `build_dsk.py`) names the spawn roll constants. Tests: `tools/test_ship_packs.py`, `tools/test_launch.py`. Open: play it through, hide the pack load (`TODO.md`).
- Missions: six added missions (Constrictor, Thargoid plans, stolen police ship, asteroid bombardment, Trumbles; Elite Plus 4 and 6) are built on branch `addon-missions` (`main` is its ancestor; the former feature branches are merged and deleted). Overview, order, triggers, sizes and tests: `docs/_missions_built.md`; research: `docs/_missions.md`. `-DMISSIONS` builds put the code in the free tails (`src/elite/missions_*.asm`: stub and overlays in the LARGEAXX tail, vector table and one flight image in the COMMONXX tail). Test disk: `python3 -I tools/build_dsk.py --missions` (copy to `work/xray/disk/`); the cpcxray tests are `tools/test_*.py` (stop at `handleEntitys` `&5066` and restore registers when injecting calls). Test helpers: `CHEAT.BAS`, `tools/saveedit.py`, `LISTSAVE.BAS` (`docs/_cheats.md`). Limits: the stub plus Constrictor overlay has 3 bytes spare, the Constrictor flight image 11 and the Trumbles image 1 (`docs/_missions_built.md`). Open: a real playthrough, tuning, merge into `main`.
- Improve `src/elite/`: 7 `dat_` labels left (`TODO.md`), about 640 `LAB_ram_`; `smc_` = self-patched, `buf_` = runtime buffer (README of `src/elite`); long unrolled runs use sjasmplus `DUP`; `tools/trace_unknowns.py` finds who touches a variable; turn pointer tables into `dw`; annotate the 25 Spectrum matches that still lack a comment (`docs_other/_spectrum_map.md`). 
- Save key: the 104 bytes at `EquipShip` must stay the stock bytes (`check_src.sh` checks it); do not touch them (an equipment-list column tweak changed the key once and was removed). `-DENHANCED` needs `STAR_OCCLUDE` (an `ASSERT`). The disk and disassembly scripts refuse the project root and `src/` (`build_dsk.py`, `saveedit.py`, `disasm_stock.py`/`disasm_locale.py` need an OUTDIR). A save on a write-protected disk resets to BASIC (not yet confirmed whether the stock game does the same).
- Menu and disk tests (disk menu, save, load) need a clean boot, not `firebird_at_entry.sna` (half-initialised, it corrupts the screen); in `type_text` the quote in `RUN"ELITE` came out garbled, so check the first screenshot. Timing one routine: `tools/test_keydelay.py` (stop at `handleEntitys` `&5066`, push a trap address, compare `machine_status["clock_us"]`).
- `halt` resumes on every interrupt: 6 per frame, 300 per second, so `djnz` + `halt` delays are B/300 s, not B frames.
- 128K tests: `sna_save` then read bank n at file offset `0x100 + n*0x4000` (the file is flat, banks 0-7); `memory_read` shows only the CPU's current map (a mapped bank hides what is under it), and `view="ram:N"` returned the same bytes for every N. Disc loads from the emulated drive take several emulated seconds: run 10-15 s before reading results. After boot wait about 4 s before `type_text`, or the first characters are lost.
- A binary started with `RUN"X.BIN` finds the cassette vectors selected (`CAS_IN_OPEN` asks "Press PLAY"; seen in cpcxray) and the lower ROM off (read the font ROM only after `KL L ROM ENABLE` `&B906`). Put everything a RUN'd program needs into its own file (several extents work: `tools/dskx.py add_payload`); only a BASIC loader (`ELITE.BAS`) still has the disc routines.
- macOS: `sed -i ''` (empty suffix) edits in place; for multi-line edits use a `python3 -I` script with exact-match asserts instead of `sed`.
- Before committing, check `git status`: if every file shows `D ` (staged) plus `??`, the index was emptied; `git reset -q` restores it without touching the working tree.
- The user edits files while you work: commit with explicit paths (`git add FILE...`) unless told to commit everything, and run `git status` first to see what is not yours.
- `posDataPlanet` (`&1C2F`) and `posDataSun` (`&1C26`): x, y, z as lo, hi, sign bytes each. Planet far to the left: `00 FF 80 00 00 00 B6 7C 01`.
- New `-DENHANCED` byte change: label the operand (`name equ $ - 1`), add `X=$(off name)` plus `o==x` to the awk filter in `check_src.sh` (a tree without the label gets -99999), and do all three trees. Slots so far: `podCleanOperand`, `predelayOperand`, `hyperCountPos`, `cashHome`, `laserSightsJp` (3 bytes) and `laserSightsBlock` (128 bytes, `LASER_SIGHTS_SIZE`; the laser sights of `lasersights.asm`, on with `-DENHANCED` unless `-DMISSIONS` in English).
- Escape-pod cargo clear is off by one (confirmed: starts at the market byte `&38E1`, keeps alien items `&38F2`; `docs/_missions.md` section 3); fixed with `-DENHANCED` in all three trees (`podCleanOperand`, `ld hl,cargoHold`), the default build keeps the original bytes.
- Spectrum names were seeded 2026-11-07 (`docs_other/_spectrum_map.md`); `work/fessor_to_stock.sym` is exhausted (its useful names are in `src/elite/` already); the remaining labels need naming from callers.
  Check each name against callers before trusting it; see `docs_other/_fessor.md` for how it was made and checked.
- macOS BSD `sed` has no `\b` and silently changes nothing: for word-boundary renames in `src/` use `perl -pi -e 's/\bold\b/new/g'`, then confirm with a grep count. `tools/rename_dat.py` only handles `dat_` labels. `check_src.sh` also passes on an unchanged tree, so it does not catch a rename that matched nothing.
- `sjasmplus` is on PATH only inside `tools/check_src.sh`; for listings/symbols run `export PATH="$HOME/.local/bin:$PATH"` first, then `--lst` and grep the `.lst` for the address.
- Renaming a label in `src/elite/`: apply it to `src/elite_de/` and `src/elite_fr/` too. For many labels, regenerate into a scratch dir (`map_german.py`, then `disasm_german.py work/de_scratch`) and diff with difflib; if only renames/comments differ, copying `commonxx.asm` over is safe. For one label, `perl` on both trees plus `check_src.sh` and `check_src.sh de`.
- Asp mission state byte is `aspMissionState` (Spectrum `$9CB2`; 0-3, see its comment in `commonxx.asm`); escort pack is `spawnEscortPack` (`$BCAB`). Both builds are named.
- In-game keys (cpcxray `key_press`, hold 1.2-1.4 s): `5` galactic chart, `6` short range chart, `7` data on present system, `h` hyperspace to the system nearest the chart cursor (needs fuel; keep the cursor within ~7 LY, e.g. a 0.2 s `cursor_left` tap from Lave reaches Diso). `cursor_*` move the chart cursor (`PresentPlanetX/Y` `&3934/&3935`, about 22 steps per second). Load `output/firebird_in_flight.sna` directly, or `disk_insert(drive="A", path=...)` BEFORE `sna_load`. Key names are `cursor_left`, `space`, `f1` (not `left`/`up`). Full cpcxray rules: `docs/_build.md` "Tests and the emulator". Helper pattern: `call_tool(name, dict)` over `stdio_client`, `key_press`, `run(max_us=…)`, `key_release`.
- The `rtk` hook rewrites Bash commands (`grep`, `ls`, `diff`, `cat`) and auto mode may refuse the first attempt ("a hook changed this call's input"); reissue the call unchanged. `rtk diff` prints nothing useful for file-vs-file diffs, so use `python3 -I` with `difflib`. `rtk grep` can truncate large results.

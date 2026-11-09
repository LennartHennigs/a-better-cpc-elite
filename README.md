# Elite for the Amstrad CPC, taken apart and given more to do

This project takes the Amstrad CPC version of *Elite* (Firebird, 1985, a Z80 port of the Spectrum game), disassembles it into readable, commented, reassemblable source, and uses that source to build a **richer Elite**:
a version with the missions the other versions of the game had, and a few they did not.

## Secret Missions

The CPC game shipped with **three** scripted missions. This build adds **five** more, **eight in total**. They come from three places:

| Source | Missions taken |
|---|---|
| the BBC Micro disc version (and its relatives: Master, Apple II, Atari ST, MSX, C64, NES) | 2 |
| the C64 and NES versions | 1 |
| *Elite Plus* for the PC | 2 |

What they are, where they start and what they pay is the point of finding out: **it is not written here**. Play it. (The research notes in `docs/` do spoil everything, so read those afterwards.)

The repository contains no game binaries, disk images or third-party source: the original disks, scans and reference sources are listed in `.gitignore` and stay on the author's machine. You need your own copy of the game to build and test anything. The assembly source is a disassembly of the original game's code and stays subject to its copyright; it is here for study and preservation.

## What is in here

| Part | What it is |
|---|---|
| `src/elite/` | the stock English game as **commented source in sjasmplus syntax** that assembles to the original bytes (`LARGEAXX`, `COMMONXX`, `COMMON2X`, `MUSIQUEX`, about 20,000 lines) |
| `src/elite_de/`, `src/elite_fr/` | the German and French builds, same names and comments carried over, also byte-exact |
| `src/elite/missions_*.asm` | the added missions: code, text and one ship model, assembled only with `-DMISSIONS` so the stock build stays untouched |
| `src/cheats/` | a trainer, a save viewer and a save editor, all written in CPC BASIC |
| `tools/` | Python helpers: disassembler and verifier, disk reader and writer, text compressor, sprite converter, savegame decoder and editor, emulator tests |
| `docs/` | notes by topic: architecture, game facts, save format, cheats, the other versions' missions (research), and the implemented missions |

## Small improvements

Besides the missions, the build has a few changes that make the game nicer to play. The first is always on; the others are switches in the source (see *Build switches* below), and `tools/check_src.sh` proves that without the switches the original bytes come back.

- **The keyboard works on a CPC464+/6128+.** The original game's keyboard is dead on a Plus machine; one byte in the keyboard scan (`getPPI_Input`, `ED 79` -> `ED 49`, found by diffing Redbox's patched disk) fixes it. It is not a switch, and the German stock disk already has it. Not tried on real Plus hardware; details in `docs/_cpcplus.md`.
- **Escape leaves the buy, sell and equipment prompts.** Escape now backs out of them (switch `ESC_KEYCODE`; the stock game ignores that key there).
- **Stars stay behind the planet and sun.** The stars used to be drawn over the planet and sun discs, so they shone through them. Now they only appear against empty space (switch `STAR_OCCLUDE`, in all three languages). Ships are still wireframes, so you see stars between their edges, as in the original.
- **Choose the ship on the title screen.** Cursor left and right, or the joystick, step the demo ship through eight hulls (Viper, Asp, Cobra Mk III, Fer-de-Lance, Sidewinder, Krait, Rock Hermit, Thargoid), so you can look at all of them (switch `TITLESEL`, English and German; the disks from `tools/build_dsk.py` include it).

## The commented code

`src/elite/` is not a raw disassembly dump. It was built in steps and every step is checked against the original bytes:

1. **Code and data found by following the program.** Recursive descent from the entry point (`&1C82`), the labelled routines and the address tables finds the routines; what is never reached stays `db` (strings, ship blueprints, graphics, tables). Self-modifying code, which Elite uses heavily in its line plotters, is written as `name equ` labels that point into an instruction's operand.
2. **Names.** Routines and variables carry real names (`spawnShip`, `applyLaserDamagetoEntity`, `setShipvarsAtArrival`, `killScoreHigh`, `jumpCounter`, `Missionflag` ...), taken from earlier reconstruction work, from the annotated 6502 versions and from matching routines against the **ZX Spectrum disassembly** (the CPC game is a Spectrum port, not a BBC port). A line `; ZX Spectrum: name (&ADDR)` marks a routine that matches one there. What could not be named stays `sub_`, `loc_` or `dat_` plus its address; the work to replace those goes on.
3. **Comments in plain words.** Each routine says what it does, what goes in and out, and what the surprising parts are. Examples: the double-buffered view is drawn into a bitmap at `&A000` that is wiped and copied to the screen every frame; the game swaps `&0040-&1A3F` with `&A600-&BFFF` at runtime; the savegame is XORed with the game's own code, which is why any code change breaks old saves (and how the tools here read the key from the disk).
4. **Proof that nothing was lost.** `bash tools/check_src.sh` assembles all four files and compares them with the original disk bytes (`... de` and `... fr` for the other builds); it fails on any difference. Two one-byte fixes are expected and documented in the script: the CPC+ keyboard bug and the Escape key in the buy menus.
5. **Strings.** The game's text uses its own token scheme (digrams, references to other strings); `tools/elitetext.py` expands it and `tools/textenc.py` encodes new text with the same scheme.

Free space and hooks: the original is full, so the added missions use two zero-filled tails (610 bytes at the end of `COMMONXX`, 812 bytes at the end of `LARGEAXX`), 3-byte call replacements at a handful of hook sites, and small **overlay files** loaded from the disk only when something can happen. Only one mission's code is in memory at a time. `docs/_missions_built.md` explains the mechanism, sizes and tests.

## Build and run

Requirements: Python 3, [sjasmplus](https://github.com/z00m128/sjasmplus), iDSK for the trainer disks, and an emulator for the disks (RVM, MAME or the analysis emulator cpcxray, which the tests use).

```bash
bash tools/check_src.sh              # stock English source == original bytes, -DENHANCED differs only where documented (also: de, fr)
python3 -I tools/build_dsk.py --missions     # combined build: work/elite_missions.dsk (from the Firebird disk)
bash tools/build_cheat.sh            # trainer and save tools onto work/firebird_cheat.dsk and work/missions_cheat.dsk
```

Boot the disk and `RUN"ELITE`. `RUN"CHEAT.BAS` starts the trainer (it has prompts for kills, jumps and mission presets, so the added missions can be reached without hours of play); `RUN"SHOWSAVE.BAS` shows the build (UK, French or German), kills and jumps of a save; `RUN"EDITSAVE.BAS` edits one. On the host, `tools/saveedit.py` does the same and can convert a save between the three builds.

## Build switches

The easy way is `make`:

```bash
make stock          # original bytes -> work/build/stock/       (LOC=de or LOC=fr for German / French)
make enhanced       # the improvements -> work/build/enhanced/
make missions       # enhanced + added missions, bootable disk -> work/elite_missions.dsk
make check          # check_src.sh for en, de, fr
```

Underneath, a plain `sjasmplus` run gives the **stock** game (`bash tools/check_src.sh` proves it), and our changes are assembler switches (`-D` flags):

| Switch | What it does | Files |
|---|---|---|
| `ENHANCED` | turns on `STAR_OCCLUDE` and `ESC_KEYCODE=0x7F` together (the "small improvements" above) | `commonxx.asm` |
| `STAR_OCCLUDE` | stars stay behind planet and sun (`=1`/`=0`, overrides `ENHANCED`) | `commonxx.asm` |
| `ESC_KEYCODE` | key code of Escape in the keyboard table (`0x7F` = Escape leaves the prompts, `0xFF` = stock) | `commonxx.asm` |
| `TITLESEL` | choose the demo ship on the title screen | `commonxx.asm`, `musiquex.asm` |
| `MISSIONS` | the added missions (`missions_*.asm`, overlay stub, hooks) | `largeaxx.asm`, `commonxx.asm` |
| `FIREBIRD` | the Firebird trainer variant of `LARGEAXX` (one byte, no hold-capacity test) | `largeaxx.asm` |

**CPC+ keyboard fix.** The original game's keyboard is dead on a real CPC464+/6128+: the scan routine `getPPI_Input` touches the PPI in an order the Plus ASIC does not tolerate. The English and French sources carry a one-byte fix found by diffing Redbox's patched disk (`ED 79` -> `ED 49`); it is always on, not a switch, and the German stock disk already has it. I have not tried it on real Plus hardware. Details: `docs/_cpcplus.md`. So "stock" here means the original game plus this one byte, and `check_src.sh` expects it.

**How the free space is used.** The original is full: no byte of it can simply be given up, and no address may move (saves are XORed with the game's own code, so any shift breaks them). The additions therefore go into space the game does not use:

| Where | Size | What lives there | Left |
|---|---|---|---|
| zero tail of `LARGEAXX` (`&1714-&1A3F`, reloaded from disk at every docking) | 812 | resident mission stub (251) plus the one docked overlay that is loaded on demand (largest: Constrictor, 561) | **0** |
| zero tail of `COMMONXX` (`&9D9E-&9FFF`) | 610 | vector table, launch hook and one flight image, picked at every launch (largest: 608; the image must end at `&9FFE` or below, because an interrupt can push at `&9FFE-&9FFF`, which an `ASSERT` checks) | **0** |
| dead `unusedViewBorderFill` (`&1FD2-&1FF0`) | 31 | `dustPlotPixel` for star occlusion (11 bytes) and `mxPodHook`, which zeroes the Trumble count when an escape pod is used (10 bytes) | 10 |

Changes to existing stock bytes are small: the CPC+ keyboard fix and the Escape key code (one byte each), 16 bytes of the dust loop for star occlusion, and a handful of 3-byte call replacements at the mission hook sites. Nothing else moves. With the switches off only the CPC+ byte differs from the original, and `tools/check_src.sh` checks every one of these claims. So there are 0 spare bytes in each of the two tails: a further mission or change to the largest ones has to trim something first (sizes per mission in `docs/_missions_built.md`).

Example: assemble the four files with the mods (English, with missions) into a scratch directory, then put them on a disk:

```bash
mkdir -p out
sjasmplus -DENHANCED -DTITLESEL -DMISSIONS -DFIREBIRD --raw=out/LARGEAXX.BIN src/elite/largeaxx.asm
sjasmplus -DENHANCED -DTITLESEL -DMISSIONS            --raw=out/COMMONXX.BIN src/elite/commonxx.asm
sjasmplus                                             --raw=out/COMMON2X.BIN src/elite/common2x.asm
sjasmplus -DTITLESEL                                  --raw=out/MUSIQUEX.BIN src/elite/musiquex.asm

python3 -I tools/build_dsk.py --missions             # does all of the above and writes work/elite_missions.dsk
```

Without `-DMISSIONS` you get the improvements only; without any flag, the original. The missions also need the overlay and flight-image files, which `build_dsk.py` builds and writes, so use it for a bootable disk; the raw `sjasmplus` lines are for looking at the bytes. The German and French trees take the same `ENHANCED` switch (`src/elite_de/`, `src/elite_fr/`; `TITLESEL` in German, `MISSIONS` English only).

## Tests

The missions are tested in an emulator driven from Python (`tools/test_*.py`): the docked stub and overlays, the launch image picker, the spawn and kill hooks of every mission, the Trumble sprites and the save tools. The tests force game states and call routines directly. They do not replace playing through the whole game with save and load, which is still open.

## More

The notes live in `docs/`, one file per topic (`docs/_*.md`); the main ones:

- `docs/_build.md` building, switches and what the checker proves, `docs/_my_changes.md` every change we made to the game, `docs/_memory_map.md` memory map, swapping and free space
- `docs/_architecture.md` design, dead code and the dynamic labels
- `docs/_missions_built.md` the implemented missions (spoilers), `docs/_missions.md` the research on the other versions (spoilers)
- `docs/_savegame.md` the save format, `docs/_cheats.md` the trainer and save tools
- `docs/_open_questions.md` what is unverified, with how to settle it
- `CHANGELOG.md` what changed and why, `TODO.md` what is open, `CLAUDE.md` working notes for the tooling

## Credits and sources

*Elite* is by David Braben and Ian Bell; the CPC version is the Firebird port. Mark Moxon's annotated BBC Micro, C64 and NES sources (elite.bbcelite.com) and Andy McFadden's Apple II disassembly were read for behaviour only; the Z80 here is written fresh. The Atari ST source, the MSX and ZX Spectrum (SkoolKit) disassemblies, the *Elite Plus* decompilation work by rembish and the CPC reconstruction by Fessor were used as references; Fessor asked that his material not be redistributed, so it is not part of this repository. Details and links are in `docs/_references.md`.

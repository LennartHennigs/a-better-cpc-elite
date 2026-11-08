# Elite for the Amstrad CPC, taken apart and given more to do

This project takes the Amstrad CPC version of *Elite* (Firebird, 1985, a Z80 port of the Spectrum game), disassembles it into readable, commented, reassemblable source, and uses that source to build a **richer Elite**:
a version with the missions the other versions of the game had, and a few they did not.

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

Besides the missions, the build has a few changes that make the game nicer to play. None of them touches the stock bytes: each is a switch in the source, and `tools/check_src.sh` proves that with the switch off the original comes back.

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
bash tools/check_src.sh              # stock English source == original bytes (also: de, fr)
python3 -I tools/build_dsk.py --missions     # combined build: work/elite_missions.dsk (from the Firebird disk)
bash tools/build_cheat.sh            # trainer and save tools onto work/firebird_cheat.dsk and work/missions_cheat.dsk
```

Boot the disk and `RUN"ELITE`. `RUN"CHEAT.BAS` starts the trainer (it has prompts for kills, jumps and mission presets, so the added missions can be reached without hours of play); `RUN"SHOWSAVE.BAS` shows the build (UK, French or German), kills and jumps of a save; `RUN"EDITSAVE.BAS` edits one. On the host, `tools/saveedit.py` does the same and can convert a save between the three builds.

## Tests

The missions are tested in an emulator driven from Python (`tools/test_*.py`): the docked stub and overlays, the launch image picker, the spawn and kill hooks of every mission, the Trumble sprites and the save tools. The tests force game states and call routines directly. They do not replace playing through the whole game with save and load, which is still open.

## More

- `docs/_architecture.md` memory map, load sequence, free space and the dynamic labels
- `docs/_missions_built.md` the implemented missions (spoilers), `docs/_missions.md` the research on the other versions (spoilers)
- `docs/_savegame.md` the save format, `docs/_cheats.md` the trainer and save tools
- `CHANGELOG.md` what changed and why, `TODO.md` what is open, `CLAUDE.md` working notes for the tooling

## Credits and sources

*Elite* is by David Braben and Ian Bell; the CPC version is the Firebird port. Mark Moxon's annotated BBC Micro, C64 and NES sources (elite.bbcelite.com) and Andy McFadden's Apple II disassembly were read for behaviour only; the Z80 here is written fresh. The Atari ST source, the MSX and ZX Spectrum (SkoolKit) disassemblies, the *Elite Plus* decompilation work by rembish and the CPC reconstruction by Fessor were used as references; Fessor asked that his material not be redistributed, so it is not part of this repository. Details and links are in `docs/_references.md`.

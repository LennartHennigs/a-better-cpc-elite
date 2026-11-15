# Elite for the Amstrad CPC, taken apart and given more to do

This project takes the Amstrad CPC version of *Elite* (Firebird, 1985, a Z80 port of the Spectrum game), disassembles it into readable, commented, reassemblable source, and uses that source to build a **richer Elite**:
a version with the missions the other versions of the game had, and a few they did not, plus a few quality-of-life improvements (see *Small improvements* below).

## Secret Missions

The CPC game shipped with **three** scripted missions. This build adds **five** more, **eight in total**. They come from three places:

| Source | Missions taken |
|---|---|
| the BBC Micro disc version (and its relatives: Master, Apple II, Atari ST, MSX, C64, NES) | 2 |
| the C64 and NES versions | 1 |
| *Elite Plus* for the PC | 2 |

The missions are for the **English build only**: the German and French builds have too little free space for them (the tail of `COMMONXX` holds 282 bytes in German and 195 in French against 610 in English, and the English missions, their texts and the flight images already fill it), so the localized ports keep the stock missions. What they are, where they start and what they pay is the point of finding out: **it is not written here**. Play it. (The research notes in `docs/` do spoil everything, so read those afterwards.)

The repository contains no game binaries, disk images or third-party source: the original disks, scans and reference sources are listed in `.gitignore` and stay on the author's machine. You need your own copy of the game to build and test anything. The assembly source is a disassembly of the original game's code and stays subject to its copyright; it is here for study and preservation.

## Fuller Skies

The stock game has few ship types and a quiet sky. This build fills it up, in three ways:

- **More ships in space.** The stock game has 19 ship types. Ten more (Gecko, Cobra Mk I, Worm, Moray, Mamba, Adder, Boa, Anaconda, Shuttle, Boulder, hulls by Fessor) come in seven small "ship packs" on the disk. With no mission active, one pack is chosen for each system visit and loaded at the first launch (about 2 s, only when the pack changes); in it the new ships replace some Sidewinders, Kraits and traders at random, and the stock ships stay. Missions in progress use their own images, so no extras then (`-DMISSIONS`, English only, for the same lack of space in the German and French builds; `docs/_ship_packs.md`).
- **Busier space, like the C64.** The spawn roll is named and tuned towards the C64 version: more hostiles per check, about 3.5 times the asteroids, escort packs of one to four (`-DTRAFFIC`, all three languages, on in the disks; the stock values stay in comments; `docs/_ship_packs.md`).
- **A viewer for ships and objects.** `RUN"SHOWSHIP` shows all 30 models of the game as a rotating hidden-line wireframe with name, kills, bounty, speed and energy: 21 ships (the 11 stock ones, the 9 new ones and the Constrictor) and 9 objects that are not ships (the Coriolis station, missile, escape pod, cargo canister, alloy plate, splinter, asteroid, rock hermit and the new Boulder). The arrow keys step through them, "Q" quits. It runs on the mission disk and on its own blank disk (`tools/build_showship.sh`, about 8 frames a second).

## What is in here

| Part | What it is |
|---|---|
| `src/elite/` | the stock English game as **commented source in sjasmplus syntax** that assembles to the original bytes (`LARGEAXX`, `COMMONXX`, `COMMON2X`, `MUSIQUEX`, about 20,000 lines) |
| `src/elite_de/`, `src/elite_fr/` | the German and French builds, same names and comments carried over, also byte-exact; without the missions and ship packs, which do not fit their smaller free tails |
| `src/elite/missions_*.asm` | the added missions: code, text and one ship model, assembled only with `-DMISSIONS` so the stock build stays untouched; also the extra ship hulls and the ship packs (`missions_ships.asm`, `missions_flight_k.asm`) |
| `src/*/lasersights.asm`, `src/elite/killcount.asm` | the per-laser sights (the same file in all three trees) and the kill count of the status page (English), included into the free tail of `COMMONXX` (`-DENHANCED`) |
| `src/cheats/` | a trainer, a save viewer and a save editor, all written in CPC BASIC, and `SHOWSHIP.BAS`, a viewer for all the ships (BASIC plus a small Z80 routine) |
| `tools/` | Python helpers: disassembler and verifier, disk reader and writer, text compressor, sprite converter, savegame decoder and editor, emulator tests |
| `docs/` | notes by topic: building and the switches, what we changed in the game, memory map, architecture, save format, cheats, disks, the other versions' missions (research), the implemented missions, and open questions |

## Small improvements

Besides the missions, the build has a few changes that make the game nicer to play. The first is always on; the others are switches in the source (see *Build switches* below), and `tools/check_src.sh` proves that without the switches the original bytes come back.

- **The keyboard works on a CPC464+/6128+.** The original game's keyboard is dead on a Plus machine; one byte in the keyboard scan (`getPPI_Input`, `ED 79` -> `ED 49`, found by diffing Redbox's patched disk) fixes it. It is not a switch, and the German stock disk already has it. Not tried on real Plus hardware; details in `docs/_cpcplus.md`.
- **The keyboard reacts faster.** Before every key read the game waited 128 interrupts, which is 0.43 s on the CPC (the interrupt fires six times per frame, so the "128 frames" in the old comment were never frames). With `-DENHANCED` it waits 48, about 0.16 s (one operand byte in `sub_403E`, measured in the emulator: 425 ms against 160 ms), so menus, quantity prompts and Press Space feel quicker.
- **Browse the ships on the "Press Space" screen.** "Cursor Left" and "Cursor Right", or the joystick, step the demo ship through eight hulls (Viper, Asp, Cobra Mk III, Fer-de-Lance, Sidewinder, Krait, Rock Hermit, Thargoid), so you can look at all of them (it only changes the demo ship, not the one you fly) (switch `TITLESEL`, English and German; the disks from `tools/build_dsk.py` include it). In the English build the press-space screen shows the ship's name, in the ship colour, where the ELITE title stood.
- **"Escape" leaves the buy, sell and equipment prompts.** "Escape" now backs out of them (switch `ESC_KEYCODE`; the stock game ignores that key there).
- **"A" sells the whole hold.** In the sell menu, "A" at any quantity prompt sells every good you carry at once (with the trade sound) and returns to the inventory screen; the other keys still just leave the menu (`-DENHANCED`, English only so far; `src/elite/sell_all.asm`).
- **Improved readability.** The station screens line up: every headline starts in column 2, the status screen reads "System:", "Target:", "Fuel:", "Cash:", "Status:" and "Rating:" with the values in one column ("Legal Status" is now just "Status"), and the hyperspace countdown moved to column 6 so it no longer covers the headline (`-DENHANCED`, English only so far).
- **Cash on the quantity line.** The buy, sell and equipment prompts show your credits at the bottom right, on the row where you type the quantity, and refresh after every purchase (`-DENHANCED`, English only so far).
- **Kill count on the status page.** "Rating: Competent - 300": the rank is followed by your kills (`-DENHANCED`, English, in the mission build too: `killcount.asm`, 26 bytes in every flight image).
- **A sight for each laser.** The pulse laser keeps the cross; the beam, military and mining lasers get their own sights (two bracketed bars, four diagonals, bars with a dot), as on the C64 and Atari ST, and there is no sight without a laser (`-DENHANCED`, `lasersights.asm`, all three languages). Not on the mission disk: the missions fill the free flight memory it would need (English only without `-DMISSIONS`).
- **Stars stay behind the planet and sun.** The stars used to be drawn over the planet and sun discs, so they shone through them. Now they only appear against empty space (switch `STAR_OCCLUDE`, in all three languages). Ships are still wireframes, so you see stars between their edges, as in the original.

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
make original                        # the original game, stock bytes: work/elite_original.dsk (LOC=de or LOC=fr for German / French)
make expanded                        # everything on one disk: work/elite_expanded.dsk = enhancements, all missions and ship packs, CHEAT, EDITSAVE, LISTSAVE, SHOWSHIP (English only for now)
```

Boot the disk and `RUN"ELITE`. `RUN"SHOWSHIP` starts the ship viewer. `RUN"TRAINER.BAS` starts the trainer (ours, which replaces Firebird's `CHEAT.BAS` on the mission and expanded disks) (it has prompts for kills, jumps and mission presets, so the added missions can be reached without hours of play); `RUN"EDITSAVE.BAS` edits a save; `RUN"LISTSAVE.BAS` (on the mission, expanded and German saves disks) lists the saves on a disk with build, kills and cash. On the host, `tools/saveedit.py` does the same and can convert a save between the three builds.

## Build switches

The easy way is `make`:

```bash
make original       # the original game on a disk -> work/elite_original.dsk
make expanded       # the full build on one disk -> work/elite_expanded.dsk (runs tools/build_showship.sh and tools/build_cheat.sh in the right order)
make stock          # original bytes -> work/build/stock/       (LOC=de or LOC=fr for German / French)
make enhanced       # the improvements -> work/build/enhanced/
make missions       # enhanced + added missions, bootable disk -> work/elite_missions.dsk
make check          # check_src.sh for en, de, fr
```

Underneath, a plain `sjasmplus` run gives the **stock** game (`bash tools/check_src.sh` proves it), and our changes are assembler switches (`-D` flags):

| Switch | What it does | Files |
|---|---|---|
| `ENHANCED` | turns on `STAR_OCCLUDE` and `ESC_KEYCODE=0x7F` together, and the cash display, the A key of the sell menu, the readability tabs, the shorter key delay, the escape-pod cargo fix, the kill count on the status page (English) and the laser sights (not together with `MISSIONS`) (the "small improvements" above) | `commonxx.asm`, `largeaxx.asm` |
| `STAR_OCCLUDE` | stars stay behind planet and sun (`=1`/`=0`, overrides `ENHANCED`) | `commonxx.asm` |
| `ESC_KEYCODE` | key code of Escape in the keyboard table (`0x7F` = Escape leaves the prompts, `0xFF` = stock) | `commonxx.asm` |
| `TITLESEL` | choose the demo ship on the title screen | `commonxx.asm`, `musiquex.asm` |
| `TRAFFIC` | C64-like spawn odds: hostile limit, asteroid width, escort pack size (named constants, stock values in comments) | `commonxx.asm` (all three trees) |
| `MISSIONS` | the added missions (`missions_*.asm`, overlay stub, hooks) | `largeaxx.asm`, `commonxx.asm` |
| `FIREBIRD` | the Firebird trainer variant of `LARGEAXX` (one byte, no hold-capacity test) | `largeaxx.asm` |

**CPC+ keyboard fix.** The original game's keyboard is dead on a real CPC464+/6128+: the scan routine `getPPI_Input` touches the PPI in an order the Plus ASIC does not tolerate. The English and French sources carry a one-byte fix found by diffing Redbox's patched disk (`ED 79` -> `ED 49`); it is always on, not a switch, and the German stock disk already has it. I have not tried it on real Plus hardware. Details: `docs/_cpcplus.md`. So "stock" here means the original game plus this one byte, and `check_src.sh` expects it.

**How the free space is used.** The original is full: no byte of it can simply be given up, and no address may move (saves are XORed with the game's own code, so any shift breaks them). The additions therefore go into space the game does not use:

| Where | Size | What lives there | Left |
|---|---|---|---|
| zero tail of `LARGEAXX` (`&1714-&1A3F`, reloaded from disk at every docking) | 812 | resident mission stub (251) and the sell-all key (48) plus the one docked overlay that is loaded on demand (largest: Constrictor, 511) | **3** |
| zero tail of `COMMONXX` (`&9D9E-&9FFF`) | 610 | vector table, launch hook, the 26-byte kill count routine and one flight image, picked at every launch (largest: Trumbles, 608, and pack 1 and the Constrictor, 606; the image must end at `&9FFE` or below, because an interrupt can push at `&9FFE-&9FFF`, which an `ASSERT` checks). Without `MISSIONS` the tail holds the laser sights (128 bytes) and the kill count instead, with about 450 bytes free | **0** |
| dead `unusedViewBorderFill` (`&1FD2-&1FF0`) | 31 | `dustPlotPixel` for star occlusion (11 bytes), `mxPodHook`, which zeroes the Trumble count when an escape pod is used (10 bytes), and `cashHome` for the cash display (7 bytes) | 3 |
| dead `unusedGetFlightMode` and `unusedGetCloakFlag` (`&204E-&2057`) | 10 | `killSpace`, the helper of the kill count that prints one space before the dash (10 bytes) | 0 |

Changes to existing stock bytes are small: the CPC+ keyboard fix and the Escape key code (one byte each), 16 bytes of the dust loop for star occlusion, and a handful of 3-byte call replacements at the mission hook sites. Nothing else moves. With the switches off only the CPC+ byte differs from the original, and `tools/check_src.sh` checks every one of these claims. So the two tails have 3 and 0 spare bytes (the Trumbles image is exactly 608 of 608): a further mission or change to the largest ones has to trim something first (sizes per mission in `docs/_missions_built.md`).

Example: assemble the four files with the mods (English, with missions) into a scratch directory, then put them on a disk:

```bash
mkdir -p out
sjasmplus -DENHANCED -DTITLESEL -DMISSIONS -DFIREBIRD --raw=out/LARGEAXX.BIN src/elite/largeaxx.asm
sjasmplus -DENHANCED -DTITLESEL -DMISSIONS            --raw=out/COMMONXX.BIN src/elite/commonxx.asm
sjasmplus                                             --raw=out/COMMON2X.BIN src/elite/common2x.asm
sjasmplus -DTITLESEL                                  --raw=out/MUSIQUEX.BIN src/elite/musiquex.asm

python3 -I tools/build_dsk.py --missions             # does all of the above and writes work/elite_missions.dsk
```

Without `-DMISSIONS` you get the improvements only; without any flag, the original. The missions also need the overlay and flight-image files, which `build_dsk.py` builds and writes, so use it for a bootable disk; the raw `sjasmplus` lines are for looking at the bytes. The German and French trees take the same `ENHANCED` switch (`src/elite_de/`, `src/elite_fr/`; `TITLESEL` in German, `MISSIONS` English only: the German and French free tails are 384 and 493 bytes in `LARGEAXX` and 282 and 195 in `COMMONXX`, against 812 and 610 in English, too small for the stub, the overlays and the flight images; `TRAFFIC` and the improvements work in all three).

## Tests

The missions are tested in an emulator driven from Python (`tools/test_*.py`): the docked stub and overlays, the launch image picker (mission images and ship packs), the ship pack hooks, the spawn and kill hooks of every mission, the Trumble sprites and the save tools. The tests force game states and call routines directly. They do not replace playing through the whole game with save and load, which is still open.

## More

The notes live in `docs/`, one file per topic (`docs/_*.md`); the main ones:

- `docs/_build.md` building, switches and what the checker proves, `docs/_my_changes.md` every change we made to the game, `docs/_memory_map.md` memory map, swapping and free space
- `docs/_architecture.md` design, dead code and the dynamic labels
- `docs/_ship_packs.md` the extra ships, the ship packs, the traffic constants and how they are tested
- `docs/_missions_built.md` the implemented missions (spoilers), `docs/_missions.md` the research on the other versions (spoilers)
- `docs/_savegame.md` the save format, `docs/_cheats.md` the trainer, save tools and the ship viewer
- `docs/_open_questions.md` what is unverified, with how to settle it
- `CHANGELOG.md` what changed and why, `TODO.md` what is open, `CLAUDE.md` working notes for the tooling

## Credits and sources

*Elite* is by David Braben and Ian Bell; the CPC version is the Firebird port. Mark Moxon's annotated BBC Micro, C64 and NES sources (elite.bbcelite.com) and Andy McFadden's Apple II disassembly were read for behaviour only; the Z80 here is written fresh. The Atari ST source, the MSX and ZX Spectrum (SkoolKit) disassemblies, the *Elite Plus* decompilation work by rembish and the CPC reconstruction by Fessor were used as references. **Fessor** (CPCWiki, thread "Expanding Elite") disassembled the CPC game first: the Constrictor hull in `src/elite/missions_hull.asm` and the extra ship hulls in `src/elite/missions_ships.asm` (Gecko, Cobra Mk I, Worm, Moray, Mamba, Adder, Boa, Anaconda, Shuttle, Boulder) are his, and many routine and variable names, the ship layout and the symbol list come from his work. The rest of his source, beta disk and forum pages are not part of this repository (he asked that they not be redistributed); they are in his thread, linked in `docs/_references.md`.

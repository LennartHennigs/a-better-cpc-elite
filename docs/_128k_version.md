# Elite 128K (Amstrad CPC 6128): what it is and how it differs

Branch `elite128` (worktree `work/wt_elite128`), source tree `src/elite128/`. Written 2026-11-20 from `src/elite128/README.md`, the memory map (now `docs/_memory_map_128k.md`) and a comparison with `main`; reviewed and updated 2026-11-21 against the tree, the build and the tests of that day (numbers marked "measured" come from `work/elite128/c128.sym`). Details and measurements stay in the README; this page is the overview.
Diary: `CHANGELOG_128K.md`. Open work, including what `main` did since the fork: `TODO_128K.md`.

## Where it stands

- Forked from `main` at `d6b6ed0` (2026-11-11). `main` was merged into the branch on 2026-11-20 (`957072a`, `main` at `0b257db`): the branch is `main` plus the 128K work, and the features `main` got since the fork (ship packs and traffic, laser sights, sell-all, kill count, Esc at the second digit, `elite64.dsk`) are ported (`TODO_128K.md` *Done*).
- Works in the emulator (cpcxray): boots, title with the ship selector (29 ships), docking, launch, flight, hyperspace, charts, save and load, missions, ship packs. `python3 -I tools/tests/run_all.py --emu128` runs the four tests with a pass/fail result (packs, sell-all, Esc digit, file menu: all pass 2026-11-21); the other 128K tests are screenshots, probes and soaks (soaks of 5 and 10 minutes ran without a reset). Not played through by hand.
- **Music:** on the title screens only (2026-11-21), as in the 64K game (checked on `elite64.dsk`: the docked pages have the flight code in the music slot). It plays from RAM bank 7 and is tick-skipped while the ship fill hides that bank, so the notes come in bursts (`TODO_128K.md` "Title music": listen to it).
- 128K only. The 64K game on `main` is untouched: `src/elite` stays byte-exact. `src/elite128` may differ from the stock bytes; the save key is the build's own (decided 2026-11-21): the 128K build relocates the code the key is read from, so a save of a 64K disk does not load as it is, and the 64K rule that the 104 bytes at `EquipShip` stay stock does not apply here. `RUN"CONVSAVE` (on this disk and on `elite64.dsk`) converts a save either way between the UK, French, German and 128K builds; on the host `tools/saveedit.py ... --to-key-disk build/elite128.dsk` does the same. `tools/tests/test_disks.py` skips the key-equals-stock check for `elite128.dsk`; `tools/cheat128.py --check` (run by `build_dsk128.py` and `check_src128.sh`) stops the build when the key or the trainer addresses in `src/cheats` no longer match the source.
- The plan (phases, risks, the language and particle-explosion ideas) lives outside the repo in `~/.claude/plans/delegated-seeking-aho.md`.

## What is different from the 64K game

| Area | 64K (`main`) | 128K (`elite128`) |
|---|---|---|
| Ships | wireframe | **filled, dithered polygons**, from one of two sources (`HULLS`): `stock` (the default) builds the triangles from the stock blueprints (`tools/hullfill.py`: face outlines from the edges, five-tone shading, a few details of our own); `arcelite` uses ArcElite's shapes (Ian Bell's ship table), the original look. All 19 ship types, the alloy plate and the Constrictor (based on Fessor's hull) |
| Drawing | one bitmap, copied to the screen | **double buffered**: the view is drawn at `&4000` (RAM banks 1 and 3) and shown by switching CRTC R12; the cockpit is kept in sync zone by zone |
| Title screens | single buffered | double buffered with a cached text overlay (frame 320 to 255 ms) and a key latch for short taps |
| Draw order | entity order | far to near, through a deferred queue sorted on the 16-bit depth |
| Disk use | loads `LARGEAXX`, music, progress bar, mission files from disk | everything is copied into RAM banks at start (`bankInit`); only saves and the catalogue read the disk |
| Music | the Blue Danube on the title screens | title screens only: the player overlays 4 KB of flight-only code in bank 7 (`&DF02`) from the interrupt, `NOTMUSIC.BIN` restores it at the title exit (`src/elite128/musiquex.asm`) |
| Ship packs, traffic | 7 packs of Fessor's hulls, C64-like traffic (`-DTRAFFIC`) | the same, all filled (hull types 20-28); the pack is drawn at random at every launch from 13 flight images in bank 5 |
| Spawning | hostile ships start in one of four fixed diagonal corners ahead | hostile ships start at a random distance and direction from the front 270 degrees (compile switch `SPAWN_VARIANCE` in `config.inc`); escort packs keep together, asteroids start anywhere around the player with a heading towards the player, the Thargoid group, the plans pair and the Constrictor keep a z sign of 0 (never behind); traders unchanged so far (`docs/_ship_spawning.md`) |
| Ship viewer | `RUN"SHOWSHPS`, wireframe, 30 models | `RUN"SHOWSHPS` shows the same 29 ships as the title selector, filled (page flip prototype, banks 4-6), with the 64K viewer's layout: name and counter in yellow, a sky blue frame, "KILLS, BOUNTY, SPD, EN" from the blueprint header, the key hint (the 64K viewer's Boulder is not a 128K hull) |
| Disk | `elite64.dsk` (expanded): `ELITE64.BAS`, trainer, save tools | `build/elite128.dsk`: `RUN"ELITE128` (Firebird's `ELITE.BAS` renamed), `README.TXT`, `SHOWSHPS.BAS`, the trainer `RUN"TRAINER` (128K addresses, `tools/cheat128.py`), `EDITSAVE`, `LISTSAVE`, `CONVSAVE` and a ready commander `LEN.BIN` |
| Memory | 64 KB, about 610 free bytes in flight | 128 KB, about 27.5 KB free but only in banks 4-6 (data); resident code space is **0 + 13 + 15 bytes** (measured 2026-11-21 after the title music: the glue ends at `&9C7D`, the fixed mission table starts at `&9C80`; `docs/_memory_map_128k.md` has the table). New resident code goes into the overlay on `bankInit` (`lasersights128.asm`, 6 of its 248 bytes are free, the stage slot allows 256) or into a far-call module |
| Build flags | `-DENHANCED -DMISSIONS -DTRAFFIC -DTITLESEL` per disk | one variant (`src/elite128/config.inc`): enhanced UI, missions, title ship selection, Firebird loader |
| Machines | 464, 664, 6128 | 6128 only; a 464/664 shows "128K CPC REQUIRED" |
| Languages | English, German, French | English only |

## How it is laid out

- **RAM banks** (`docs/_memory_map_128k.md`): bank 6 holds the fill module and the hull records (mapped at `&4000` with config `&C6`); bank 4 holds a copy of `LARGEAXX` and the mission overlays; bank 5 holds the progress bar data (`INDICATO.BIN`) and the 13 flight images (default, packs 1-7, mission images); bank 7 holds the code block that used to live at `&3F60-&7D5D`, shown at `&C000` in configs C1/C3, so it stays visible while the CPU draws at `&4000`.
- **Screen page**: the stock screen page content (3,163 bytes of `COMMON2X`) moved into the `&4000` window (`gaps.asm`, labels as `SCREEN+offset`); the flip alternates bank 1 and bank 3.
- **Glue in the resident part**: `hullDraw`, the deferred queue, `bankInit`, the flip stubs, the disc trampolines (the firmware reads the disc on its own stack, because the game stack sits in the window).
- **Build**: `bash tools/check_src128.sh` (generates the hull data into `work/elite128/` and assembles everything; the generated files are never committed). After ANY size change also run `python3 -I tools/gen_equs.py src/elite128 --write` and `sync_equs.py ... --write` (cross-file `equ` lines go stale) and `python3 -I tools/check_moved_labels.py` (raw numbers that still point at a stock address whose label moved). `check_src128.sh` itself fails on a stale `equ` (`sync_equs.py --check`). Then `python3 -I tools/build_dsk128.py` (or `make disk6128`; `--missions` is accepted and ignored: the one variant always carries the missions) gives `build/elite128.dsk`, which is copied to `work/xray/disk/` for tests; boot with `RUN"ELITE128`. A 128K RVM state is converted with `python3 -I tools/rvmstate.py STATE --sna OUT.sna --curcfg`.
- **Readable listing:** `make listing6128` (`tools/listing6128.sh`) writes `build/listing6128/elite6128.lst`, every module in one file with its includes expanded, address and bytes beside each source line and a label table per module (about 32,000 lines); the same flags as the real build. It is generated output, not source: it contains the generated ArcElite-derived hull data, so it stays in the ignored `build/`.
- **Tests** are `tools/tests/test_*128.py` in cpcxray (`test_boot128`, `test_flight128`, `test_hulls128`, `test_flip128`, `test_mission128`, `test_launch128`, `test_packs128`, `test_sellall128`, `test_filemenu128`, `test_soak128`, ...; index in `tools/tests/README.md`). The 128K disk is one variant with the missions, so symbols and glue labels match it; `snap_docked128.py` must regenerate `output/docked128.sna` after code changes, or `test_launch128.py` silently runs the old code.

## Cost

Measured 2026-11-21 with `tools/tests/test_frametime.py` (milliseconds between two stops at `handleEntitys`, once per frame; `--phases` adds marks): the launch scene of a new commander (planet filling the view and inside scanner range, ship slots cleared), the same scene on all builds. The older figures ("232 ms wireframe against 254 ms filled", "6 frames per second before the flip") came from a script whose fixed addresses had gone stale and from different scenes: do not quote them.

| Scene | 64K stock | 64K `elite64.dsk` | 128K before the copy change | 128K now |
|---|---|---|---|---|
| planet in scanner range (after a launch) | 201 ms (5.0 fps) | 202 ms | 276 ms (3.6 fps) | 240 ms (4.2 fps) |
| planet out of scanner range | | 178 ms | 215 ms | 200 ms |
| Cobra straight ahead (fastest of 16 frames; the first frames with a close ship are much slower) | 201 ms | | 279 ms | 252 ms |

Where the 128K frame goes in the first row (before the change, against `elite64.dsk`; the buffer-to-screen transfer is the same 55 ms in both):

| Phase | 64K | 128K before | 128K now |
|---|---|---|---|
| `handleEntitys` (entity loop, planet only) | 7.6 | 14.7 | same |
| `handleLaser` (crosshair) | 3.4 | 10.5 | same |
| `transferBuffertoScreen` | 54.4 | 55.1 | same |
| page flip: wait for the vertical sync | | 6 to 13 (depends on the phase) | 6 to 8 |
| page flip: cockpit copy (scanner zone, 1,792 bytes) | | 47.1 | 17.9 |
| `UpdateIndicatorBars` | 24.5 | 27.1 | same |
| everything else (dust, planet, dashboard, scanner draw) | | | within 1 ms of 64K, per routine |

- The page flip was 79% of the 128K overhead. The scanner copy runs every frame while any slot is inside scanner range, and slot 0 (the planet) counts: after a launch it is in range for as long as the ship stays near it (`UpdateScanner` draws it as a blip, as in the stock game). Moving the planet out of range (`--poke 1A47=50`) drops the copy from 47 to 7 ms.
- The copy used to keep interrupts off per chunk, so it was paced (160 bytes per interrupt, then `halt`), and a chunk that outlasted the 3.3 ms gap cost a whole further period. Since 2026-11-21 `dbCopy` has no `di`/`ei` and the pacing is deleted: the interrupt handlers are in banks 0 and 2 and touch nothing in `&4000-&7FFF` or `&C000+`, so `ldir` may be interrupted anywhere. Interrupt entry jitter (`tools/tests/test_isrjitter128.py`): worst 5 us (was 221 us; the stock game 5 us).
- Method, pitfalls and the list of next steps: `docs/_128k_speedup.md`.
- Not yet cut: the vertical-sync wait before the CRTC switch (6 to 12 ms; R12 only takes effect at the next frame start, so the wait may be unnecessary, untested on hardware), the remaining 18 ms of the scanner copy (per-strip overhead: a dirty rectangle or fewer, longer strips), the entity loop (+7 ms against 64K with only the planet in it, not yet traced) and the laser sights (10.5 ms against the stock crosshair's 3.4). Direct drawing into the back screen (no transfer copy) is not needed for the copy: the transfer costs the same as in the 64K game.

## Things to know before touching it

- Pointer tables and self-patch targets must be labels, not numbers. Resident `commonxx` labels from `&293F` up must stay at their stock addresses (the sources use raw numbers for variables). Constants that only look like screen addresses stay literal (`0xC624`, the bitmap-end clamp). The pitfalls list is in the README ("Relocated layout").
- **Title music:** the slot, the hook and the stop order are described in the header of `musiquex.asm` and `CHANGELOG_128K.md` (the open listening test is in `TODO_128K.md`); the order in `loadNotMusique` matters (`musicState` = 0, `mute`, `loadLARGEAXX`, then the disc read).
- `&0040-&1A3F` is not free memory at any time: in flight and on the title it holds the firmware's parked RAM (`loadIndicator` swaps it with `&A600-&BFFF`; the first docking puts it back), docked it holds `LARGEAXX`. The interrupt can only call code in banks 0 and 2: bank 7 at `&C000` is hidden while a far call (config C6) is active.
- The fill module file (`fill.bin`) must stay within `&600` bytes; it rides in blank screen pixels of the window page.
- ArcElite source only: hull axis maps and convexity flags in `tools/ship128.py` are plausible, not proven for every hull (`AXIS_OVERRIDE`). The stock source has no axis map (the blueprints are already in the engine's axes); its convexity is measured.
- **Hull source switch:** `make disk6128` (`HULLS=arcelite DSK128=build/elite128_arcelite.dsk make disk6128` leaves the stock-hull disk alone; or `HULLS=stock|arcelite bash tools/check_src128.sh`, then `python3 -I tools/build_dsk128.py [OUT.dsk]`) builds with the stock-based hulls by default; `HULLS=arcelite` needs the ArcElite files in `work/arcelite/`. Both fill the same fixed slot of the resident area (`HULL_REGION_SIZE` = 1,781 bytes in `commonxx.asm`, padded with zeros), so every address stays the same and switching needs no `sync_equs`; the stock-based set uses 1,763 bytes of it (each new vertex of a design costs 6). `work/elite128/hulls_source.txt` records which source made the generated files. ArcElite data is third party: it stays in `work/` and never goes into git. Licence terms: `NOTICE` items 6 to 10.

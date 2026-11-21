# Elite 128K (Amstrad CPC 6128): what it is and how it differs

Branch `elite128` (worktree `work/wt_elite128`), source tree `src/elite128/`. Written 2026-11-20 from `src/elite128/README.md`, `docs/_memory_map.md` and a comparison with `main`; reviewed and updated 2026-11-21 against the tree, the build and the tests of that day (numbers marked "measured" come from `work/elite128/c128.sym`). Details and measurements stay in the README; this page is the overview.
Diary: `CHANGELOG_128K.md`. Open work, including what `main` did since the fork: `TODO_128K.md`.

## Where it stands

- Forked from `main` at `d6b6ed0` (2026-11-11). `main` was merged into the branch on 2026-11-20 (`957072a`, `main` at `0b257db`): the branch is `main` plus the 128K work, and the features `main` got since the fork (ship packs and traffic, laser sights, sell-all, kill count, Esc at the second digit, `elite64.dsk`) are ported (`TODO_128K.md` section 2).
- Works in the emulator (cpcxray): boots, title with the ship selector (29 ships), docking, launch, flight, hyperspace, charts, save and load, missions, ship packs. `python3 -I tools/tests/run_all.py --emu128` runs the four tests with a pass/fail result (packs, sell-all, Esc digit, file menu: all pass 2026-11-21); the other 128K tests are screenshots, probes and soaks (soaks of 5 and 10 minutes ran without a reset). Not played through by hand.
- **Music:** on the title screens only (2026-11-21), as in the 64K game (checked on `elite64.dsk`: the docked pages have the flight code in the music slot). It plays from RAM bank 7 and is tick-skipped while the ship fill hides that bank, so the notes come in bursts (`TODO_128K.md` "Title music": listen to it).
- 128K only. The 64K game on `main` is untouched: `src/elite` stays byte-exact. `src/elite128` may differ from the stock bytes; the README and the plan say save-key compatibility is not required, but the branch's `CLAUDE.md` still carries the 64K rule that the 104 bytes at `EquipShip` stay stock. The 128K build relocates the code the key is read from, so saves of the 64K disks do not load: `tools/tests/test_disks.py` skips the key check for `elite128.dsk`, and a BASIC save converter is a TODO (`TODO_128K.md`).
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
| Ship viewer | `RUN"SHOWSHPS`, wireframe | `RUN"SHOWSHPS` shows 26 ships filled (page flip prototype, banks 4-6); the title screen's ship selector (N, then the cursor keys) shows all 29 |
| Disk | `elite64.dsk` (expanded): `ELITE64.BAS`, trainer, save tools | `build/elite128.dsk`: `RUN"ELITE128` (Firebird's `ELITE.BAS` renamed), `README.TXT`, `SHOWSHPS.BAS`; no trainer (it pokes 64K addresses) |
| Memory | 64 KB, about 610 free bytes in flight | 128 KB, about 27.5 KB free but only in banks 4-6 (data); resident code space is **3 + 13 + 15 bytes** (measured 2026-11-21 after the title music: the glue ends at `&9C7D`, the fixed mission table starts at `&9C80`; `docs/_memory_map.md` still says 172, see the TODO to split it). New resident code goes into the overlay on `bankInit` (`lasersights128.asm`, 4 of its 160 bytes are free) or into a far-call module |
| Build flags | `-DENHANCED -DMISSIONS -DTRAFFIC -DTITLESEL` per disk | one variant (`src/elite128/config.inc`): enhanced UI, missions, title ship selection, Firebird loader |
| Machines | 464, 664, 6128 | 6128 only; a 464/664 shows "128K CPC REQUIRED" |
| Languages | English, German, French | English only |

## How it is laid out

- **RAM banks** (`docs/_memory_map.md`, "128K layout"): bank 6 holds the fill module and the hull records (mapped at `&4000` with config `&C6`); bank 4 holds a copy of `LARGEAXX` and the mission overlays; bank 5 holds the progress bar data (`INDICATO.BIN`) and the 13 flight images (default, packs 1-7, mission images); bank 7 holds the code block that used to live at `&3F60-&7D5D`, shown at `&C000` in configs C1/C3, so it stays visible while the CPU draws at `&4000`.
- **Screen page**: the stock screen page content (3,163 bytes of `COMMON2X`) moved into the `&4000` window (`gaps.asm`, labels as `SCREEN+offset`); the flip alternates bank 1 and bank 3.
- **Glue in the resident part**: `hullDraw`, the deferred queue, `bankInit`, the flip stubs, the disc trampolines (the firmware reads the disc on its own stack, because the game stack sits in the window).
- **Build**: `bash tools/check_src128.sh` (generates the hull data into `work/elite128/` and assembles everything; the generated files are never committed). After ANY size change also run `python3 -I tools/gen_equs.py src/elite128 --write` and `sync_equs.py ... --write` (cross-file `equ` lines go stale) and `python3 -I tools/check_moved_labels.py` (raw numbers that still point at a stock address whose label moved). `check_src128.sh` itself fails on a stale `equ` (`sync_equs.py --check`). Then `python3 -I tools/build_dsk128.py` (or `make disk6128`; `--missions` is accepted and ignored: the one variant always carries the missions) gives `build/elite128.dsk`, which is copied to `work/xray/disk/` for tests; boot with `RUN"ELITE128`. A 128K RVM state is converted with `python3 -I tools/rvmstate.py STATE --sna OUT.sna --curcfg`.
- **Readable listing:** `make listing6128` (`tools/listing6128.sh`) writes `build/listing6128/elite6128.lst`, every module in one file with its includes expanded, address and bytes beside each source line and a label table per module (about 32,000 lines); the same flags as the real build. It is generated output, not source: it contains the generated ArcElite-derived hull data, so it stays in the ignored `build/`.
- **Tests** are `tools/tests/test_*128.py` in cpcxray (`test_boot128`, `test_flight128`, `test_hulls128`, `test_flip128`, `test_mission128`, `test_launch128`, `test_packs128`, `test_sellall128`, `test_filemenu128`, `test_soak128`, ...; index in `tools/tests/README.md`). The 128K disk is one variant with the missions, so symbols and glue labels match it; `snap_docked128.py` must regenerate `output/docked128.sna` after code changes, or `test_launch128.py` silently runs the old code.

## Cost

- Frame time with one Cobra ahead: 232 ms (wireframe) against 254 ms (filled), +9.5%.
- The page flip costs about 21 ms of copying per frame plus the wait for the vertical sync: about 4.5 flight frames per second with a planet filling the view (6 before the flip).
- The interrupt-timed colour split stays on time: the copy is paced by `halt` in chunks of at most 160 bytes (`tools/tests/test_isrjitter128.py`).

## Things to know before touching it

- Pointer tables and self-patch targets must be labels, not numbers. Resident `commonxx` labels from `&293F` up must stay at their stock addresses (the sources use raw numbers for variables). Constants that only look like screen addresses stay literal (`0xC624`, the bitmap-end clamp). The pitfalls list is in the README ("Relocated layout").
- **Title music:** the slot, the hook and the stop order are described in `TODO_128K.md` ("Title music") and the header of `musiquex.asm`; the order in `loadNotMusique` matters (`musicState` = 0, `mute`, `loadLARGEAXX`, then the disc read).
- `&0040-&1A3F` is not free memory at any time: in flight and on the title it holds the firmware's parked RAM (`loadIndicator` swaps it with `&A600-&BFFF`; the first docking puts it back), docked it holds `LARGEAXX`. The interrupt can only call code in banks 0 and 2: bank 7 at `&C000` is hidden while a far call (config C6) is active.
- The fill module file (`fill.bin`) must stay within `&600` bytes; it rides in blank screen pixels of the window page.
- ArcElite source only: hull axis maps and convexity flags in `tools/ship128.py` are plausible, not proven for every hull (`AXIS_OVERRIDE`). The stock source has no axis map (the blueprints are already in the engine's axes); its convexity is measured.
- **Hull source switch:** `make disk6128` (or `HULLS=stock|arcelite bash tools/check_src128.sh`, then `python3 -I tools/build_dsk128.py`) builds with the stock-based hulls by default; `HULLS=arcelite` needs the ArcElite files in `work/arcelite/`. Both fill the same fixed slot of the resident area (`HULL_REGION_SIZE` = 1,781 bytes in `commonxx.asm`, padded with zeros), so every address stays the same and switching needs no `sync_equs`; the stock-based set uses 1,763 bytes of it (each new vertex of a design costs 6). `work/elite128/hulls_source.txt` records which source made the generated files. ArcElite data is third party: it stays in `work/` and never goes into git. Licence terms: `NOTICE_128K.md` (an addendum to `NOTICE` on `main`).

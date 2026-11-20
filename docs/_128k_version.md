# Elite 128K (Amstrad CPC 6128): what it is and how it differs

Branch `elite128` (worktree `work/wt_elite128`), source tree `src/elite128/`. Written 2026-11-20 from `src/elite128/README.md`, `docs/_memory_map.md`, the branch's 50 commits and a comparison with `main`; nothing here was re-run today. Details and measurements stay in the README; this page is the overview.
Diary: `CHANGELOG_128K.md`. Open work, including what `main` did since the fork: `TODO_128K.md`.

## Where it stands

- Forked from `main` at `d6b6ed0` (2026-11-11); last commit `0cde05d` (2026-11-13). `main` has moved 41 commits since (to `0b257db`, 2026-11-20), the branch is 50 commits ahead.
- Works in the emulator (cpcxray): boots, title, docking, launch, flight, hyperspace, charts, save and load, missions. Soaks of 5 and 10 minutes ran without a reset. Not played through by hand.
- 128K only. The 64K game on `main` is untouched: `src/elite` stays byte-exact. `src/elite128` may differ from the stock bytes; the README and the plan say save-key compatibility is not required, but the branch's `CLAUDE.md` still carries the 64K rule that the 104 bytes at `EquipShip` stay stock. Whether the 128K build keeps the key has not been checked (`TODO_128K.md`).
- The plan (phases, risks, the language and particle-explosion ideas) lives outside the repo in `~/.claude/plans/delegated-seeking-aho.md`.

## What is different from the 64K game

| Area | 64K (`main`) | 128K (`elite128`) |
|---|---|---|
| Ships | wireframe | **filled, dithered polygons**, from one of two sources (`HULLS`): `stock` (the default) builds the triangles from the stock blueprints (`tools/hullfill.py`: face outlines from the edges, five-tone shading, a few details of our own); `arcelite` uses ArcElite's shapes (Ian Bell's ship table), the original look. All 19 ship types, the alloy plate and the Constrictor (based on Fessor's hull) |
| Drawing | one bitmap, copied to the screen | **double buffered**: the view is drawn at `&4000` (RAM banks 1 and 3) and shown by switching CRTC R12; the cockpit is kept in sync zone by zone |
| Title screens | single buffered | double buffered with a cached text overlay (frame 320 to 255 ms) and a key latch for short taps |
| Draw order | entity order | far to near, through a deferred queue sorted on the 16-bit depth |
| Disk use | loads `LARGEAXX`, music, progress bar, mission files from disk | everything is copied into RAM banks at start (`bankInit`); only saves and the catalogue read the disk |
| Memory | 64 KB, about 610 free bytes in flight | 128 KB, about 27.5 KB free but only in banks 4-6 (data); resident code space is 172 + 16 + 15 bytes |
| Build flags | `-DENHANCED -DMISSIONS -DTRAFFIC -DTITLESEL` per disk | one variant (`src/elite128/config.inc`): enhanced UI, missions, title ship selection, Firebird loader |
| Machines | 464, 664, 6128 | 6128 only; a 464/664 shows "128K CPC (6128) REQUIRED" |
| Languages | English, German, French | English only |

## How it is laid out

- **RAM banks** (`docs/_memory_map.md`, "128K layout"): bank 6 holds the fill module and the hull records (mapped at `&4000` with config `&C6`); bank 4 holds a copy of `LARGEAXX`, the mission overlays and the music; bank 5 holds the mission flight images and the progress bar data; bank 7 holds the code block that used to live at `&3F60-&7D5D`, shown at `&C000` in configs C1/C3, so it stays visible while the CPU draws at `&4000`.
- **Screen page**: the stock screen page content (3,163 bytes of `COMMON2X`) moved into the `&4000` window (`gaps.asm`, labels as `SCREEN+offset`); the flip alternates bank 1 and bank 3.
- **Glue in the resident part**: `hullDraw`, the deferred queue, `bankInit`, the flip stubs, the disc trampolines (the firmware reads the disc on its own stack, because the game stack sits in the window).
- **Build**: `bash tools/check_src128.sh` (generates the hull data into `work/elite128/` and assembles everything; the generated files are never committed). After ANY size change also run `python3 -I tools/gen_equs.py src/elite128 --write` and `sync_equs.py ... --write` (cross-file `equ` lines go stale) and `python3 -I tools/check_moved_labels.py` (raw numbers that still point at a stock address whose label moved). Then `python3 -I tools/build_dsk128.py [--missions]` gives `work/elite128.dsk`, which is copied to `work/xray/disk/` for tests; boot with `RUN"ELITE`.
- **Readable listing:** `make listing6128` (`tools/listing6128.sh`) writes `build/listing6128/elite6128.lst`, every module in one file with its includes expanded, address and bytes beside each source line and a label table per module (about 32,000 lines); the same flags as the real build. It is generated output, not source: it contains the generated ArcElite-derived hull data, so it stays in the ignored `build/`.
- **Tests** are `tools/test_*128.py` in cpcxray (`test_boot128`, `test_flight128`, `test_hulls128`, `test_flip128`, `test_mission128`, `test_launch128`, `test_filemenu128`, `test_soak128`, ...). Use the missions disk, because symbols and glue labels depend on the flags; `snap_docked128.py` must regenerate `output/docked128.sna` after code changes, or `test_launch128.py` silently runs the old code.

## Cost

- Frame time with one Cobra ahead: 232 ms (wireframe) against 254 ms (filled), +9.5%.
- The page flip costs about 21 ms of copying per frame plus the wait for the vertical sync: about 4.5 flight frames per second with a planet filling the view (6 before the flip).
- The interrupt-timed colour split stays on time: the copy is paced by `halt` in chunks of at most 160 bytes (`tools/test_isrjitter128.py`).

## Things to know before touching it

- Pointer tables and self-patch targets must be labels, not numbers. Resident `commonxx` labels from `&293F` up must stay at their stock addresses (the sources use raw numbers for variables). Constants that only look like screen addresses stay literal (`0xC624`, the bitmap-end clamp). The pitfalls list is in the README ("Relocated layout").
- The fill module file (`fill.bin`) must stay within `&600` bytes; it rides in blank screen pixels of the window page.
- ArcElite source only: hull axis maps and convexity flags in `tools/ship128.py` are plausible, not proven for every hull (`AXIS_OVERRIDE`). The stock source has no axis map (the blueprints are already in the engine's axes); its convexity is measured.
- **Hull source switch:** `make disk6128` (or `HULLS=stock|arcelite bash tools/check_src128.sh`, then `python3 -I tools/build_dsk128.py`) builds with the stock-based hulls by default; `HULLS=arcelite` needs the ArcElite files in `work/arcelite/`. Both fill the same fixed slot of the resident area (`HULL_REGION_SIZE` = 1,781 bytes in `commonxx.asm`, padded with zeros), so every address stays the same and switching needs no `sync_equs`; the stock-based set uses 1,763 bytes of it (each new vertex of a design costs 6). `work/elite128/hulls_source.txt` records which source made the generated files. ArcElite data is third party: it stays in `work/` and never goes into git. Licence terms: `NOTICE_128K.md` (an addendum to `NOTICE` on `main`).

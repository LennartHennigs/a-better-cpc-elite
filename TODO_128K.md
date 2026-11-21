# TODO: Elite 128K (branch `elite128`)

Open work for the 128K build, cleaned up 2026-11-21 (first written 2026-11-20 by comparing the branch with `main`; `main` has not moved since the merge at `0b257db`). Finished items are in *Done* at the bottom. Overview: `docs/_128k_version.md`; diary: `CHANGELOG_128K.md`; the plan is outside the repo (`~/.claude/plans/delegated-seeking-aho.md`). Git is slow in this repo (iCloud, full disk) and the index has emptied itself before: run it in the background, one command at a time, and check `git status` for `D ` plus `??` before any commit.

## Open

### Parity with `main`

- [ ] **German and French:** the 128K build is English only (the biggest gap). Tied to "one codebase for all languages" under *Later*.
- [ ] **464/664:** only a "128K CPC REQUIRED" message today (checked on cpcxray's 664 config); no fallback.
- [ ] **Cheats in play:** the trainer's effects (shields, hyperjump, one-hit kills, ...) are untested on the 128K build, as on the 64K disks; French and German saves converted by `CONVSAVE` load in the game's menu but have not been played.

### Gameplay and content

- [ ] **Spawn variance, phase 2:** hostiles are done (`SPAWN_VARIANCE`, see *Done*). Open: asteroids and traders (they need a heading first), packs staying together (`spawnEscortPack`), a play test (does a ship from the side or behind feel right?), the default for the 128K disk and whether `main` gets the switch. Design notes: `docs/_ship_spawning.md` "Open: asteroids, traders and packs".
- [ ] **Boulder in the 128K ship packs and the viewer:** the 64K game leaves Fessor's Boulder out of every pack (165 bytes; with the Boa the flight image is 9 bytes over, `docs/_ship_packs.md`); the 128K build inherited the nine pack hulls (types 20-28), so it never spawns a Boulder and `RUN"SHOWSHPS` shows 29 ships against the 64K viewer's 30. The hull records live in bank 6 (about 9 KB free), so the image limit may not bind here (not checked): add `Boulder` to `PACK_HULLS` in `tools/ship128.py` (type 29), give it a pack slot (a flight image in bank 5, or a place in an existing pack) and a `mxHullType` entry, then add it to `PACK_NAMES`/`STOCK` in `tools/mk_viewer128.py` (3 banks hold 33 ships). `spawnVariance` is no problem (checked 2026-11-21: the slot flag byte `+33` is blueprint byte `+18` AND `&6F`; every pack hull that replaces a Sidewinder or Krait has bit 2 set, the trader replacements and the Boulder `&00` have it clear and are left alone on purpose). Still to check: a hard limit of 29 types in the glue and the type chain, the pick odds of the packs, `test_packs128.py`. Afterwards reword "not a 128K hull" in `docs/_128k_version.md` and `README.md` (now it should say "not in any pack").
- [ ] **Hulls:** (ArcElite source only) confirm each hull's axis map (`AXIS_OVERRIDE` in `tools/ship128.py`: plausible, not proven). Stock source: the lighting and tones were tuned by eye on two palettes; look at the ships from other angles than the rear view, per-hull tone tweaks (the Thargoid needed one), more hand-made details for the most-seen ships (each vertex costs 6 of the 18 spare bytes of the hull slot; the Cobra is at the 28-vertex limit).
- [ ] **Clipping v2:** hulls with a vertex behind the viewer are skipped; replace with proper clipping (Sutherland-Hodgman) and LOD twins by distance (plan, phase 5).
- [ ] **Title name band:** a tall filled hull under the ship name (text row 1) spoils the text: the name is printed into the same off-screen bitmap after the ship and the recolouring pass in `titleName` assumes a plain background (seen with the Thargoid in Virtual Retro, 2026-11-20). Worked around by distance (Thargoid 5, Cobra Mk III 3 in `tools/ship128.py` `VIEW`). Proper fix: clear text row 1, columns 1-30 of the bitmap to the background before printing the name (about 15 bytes: the glue has about 9 free, the `bankInit` overlay can grow a little); then the distances need no tuning.
- [ ] **Title music:** listen to it (Virtual Retro). While a far call hides bank 7 (the ship fill, most of each title frame) the ticks are owed and run in bursts afterwards (at most 24 at once), so the tempo holds but the notes come in clumps; if that sounds bad, shorten the fill windows or make the player independent of bank 7. Not checked: the docked screens after docking back from flight. The title exit reads `NOTMUSIC.BIN` from disk (about a second, as in the 64K game); a bank copy needs resident bytes that do not exist.

### Speed

- [ ] **Investigate a speedup:** a title frame takes 254 ms against 232 ms in the 64K build (`tools/tests/test_frametime.py`); flight is about 4.5 frames per second with a planet filling the view (6 before the page flip), which should feel slower than the 64K build, but nobody has measured the 64K figure in the same situation. First measure both builds (same view, planet and ship count; frames per second from the screen or the interrupt counter), then profile the 128K cost (the flip copy of about 21 ms, the fill, the scanner sync; `docs/_128k_version.md` "Cost") and decide what to cut: direct drawing into the back screen (plan, phase 4; only if the copy dominates), a finer scanner rectangle (a ship-position bounding box would cut the scanner-busy cost, 21 ms with a ship in range against 3 ms without; `tools/cockpit_rects.py` was planned, not written), fewer fill spans. Also open in the page flip: docking from flight.

### Verification

- [ ] **Verification pass** (plan, last step): 10-minute soak with key events, `test_flip128.py`, one hull per run, launch and mission tests, before/after screenshots; `test_order128.py` and `test_frametime.py` on the final layout.
- [ ] **Played by hand:** the branch was tested with cpcxray scripts and soaks only; play it in an emulator that shows real timing (Virtual Retro) before calling it done.
- [ ] **Coverage:** `tools/exec_in_data.py` has not been run from the title screen and the chart views as start states (old TODO item).

### Tooling cleanups (from the /simplify pass, 2026-11-21)

- [ ] `tools/check_moved_labels.py` only finds raw numbers that equal a moved stock address; add the opposite pass (a label used as a number, `ld bc,LABEL`, which turned `buf_7406` into `0xF30A`), filtering the real pointer families (`Colors*`, tables, buffers, `gfx*`), and drop the one-off note in `src/elite128/CLAUDE.md`.
- [ ] One shared `tools/sjasm.py` (assemble to a temp dir, return labels and bytes) instead of the six copies of the assemble-and-parse-`.sym` code (`cheat128.py`, `mk_viewer128.py`, `build_dsk128.py`, `check_moved_labels.py`, `relo_numbers.py`, `mk_showship.py`, `hullfill.py`).
- [ ] Guard `main()` in `tools/mk_showship.py` with `__main__` so `mk_viewer128.py` can reuse its ship lists and `blueprint()`.
- [ ] `tools/cheat128.py --check` assembles four files per run, once from `check_src128.sh` and once from `build_dsk128.py` (a few seconds): take the stock symbols from `ship128.stock_image()` if it gets annoying.
- [ ] Test speed (from the second /simplify pass): `test_ship_packs.py` makes about six MCP calls per hook call (a Z80 loop that appends the record addresses to a buffer would need 3 calls per type), reloads the snapshot and reassembles for every pack (load once, assemble the seven images in parallel), and `test_parked_save128.py` saves a 128K snapshot per step to look at 3 KB (`memory_read` of `&A600-&BFFF` is enough). The shared cpcxray harness item above covers the copied `c()`, `call()`, `snap()`, `key()` and `typ()` helpers.
- [ ] Generate the 128K address row and the keys into the tokenised programs at build time instead of pasting and checking (`cheat128.py --write` already makes the paste one command).

### Constraints (facts, not tasks)

- Free space (measured 2026-11-21): resident glue 0 + 13 + 15 bytes, 6 bytes in the `bankInit` overlay (slot of 256, 242 used), bank 7 has 1 byte. Code can only live in bank 2, bank 7, the overlay or a far-call module like the fill (`docs/_memory_map_128k.md`); about 27.5 KB are free in banks 4-6, data only.

## Later, from the plan (outside the repo)

- [ ] **One codebase for all languages** (`lang/<xx>/strings.txt`, a build-time tokenizer, byte-exact gates for English, German and French; 128K per language from banks 4-6). Large.
- [ ] **Particle explosions** (`-DPARTICLE_EXPLOSION`, compile switch, off = today's behaviour; plan only) and **the 11 original BBC ships** as optional flags. Today (`todoDrawExplosions`, `common2x.asm`): a sound and 15 expanding rings (`drawradius` + 2 per ring, `SUB_ram_e74c`) at the screen position cached for the exploding slot (`cache_explosion_screen_pos`, flag bits 4 and 5), `sfxFlags2Bitmap` bit 6 for the sound. The C64 and BBC (`DOEXP`/`PTCLS` in `work/ext_c64`, `ext_bbc`): at each of the first n projected vertices (n from the blueprint's explosion-count byte) a cloud of 1 to 8 particles, offsets = random x cloud size, size = 8 x counter / distance, the counter starting at 18 and rising by 4 per frame; the random numbers come from four seed bytes kept per ship, XORed with the vertex index, so the cloud is the same every frame; points are clipped and plotted with a size from the distance; the C64 adds a sprite flash on the first frame. How it fits here:
  - Keep the sound and the ring flash as the first frame; the particles take over after it. No erase pass (the off-screen bitmap is wiped every frame; the per-ship seed keeps the cloud coherent).
  - Code in a bank 6 module, not in the glue: replace the ring code in bank 7 by a far-call stub (the `hullDraw` pattern: resident stack, config C6, call, `mapMain`, stack back), the particle code (150-250 bytes) in bank 6 with its own pixel plot (bank 7 is hidden in C6), a new stage chunk in the blank bytes of `COMMON2X` (check blankness in `build_dsk128.py`) and a vector next to `fillHullEntry`; per-slot state (cloud counter, 4 seed bytes, 8 slots) in a bank 6 table, reset when a slot starts to explode.
  - Phase 1: one cloud at the cached screen centre, radius from the counter and the distance. Phase 2: clouds at the vertices (`hullVertexBuf` already holds the projected ones for the fill), n capped at about 12; check that the explosion-count byte of the CPC blueprint is where the 6502 header has it.
  - The counter step must be larger than the 6502's 4 (the CPC draws 5 to 6 frames per second), or an explosion would last 10 seconds. Cost: up to about 28 x 8 = 220 dots a frame, roughly 10 ms; clip to the 256 x 128 viewport and skip vertices behind the viewer.
  - Checks: screenshots at several distances and counter values, frame time with several exploding ships, the special explosions (Constrictor, station, escape pod), the pens used by the flight view.
- [ ] **Bigger view and newer cockpit UI** (320 px, 25 rows): deferred, because it needs 9-bit x everywhere and direct drawing.

## Done

### Bringing `main` into the branch (2026-11-20)

- Merged `main` (`957072a`; dry run with `git merge-tree` found 8 conflicts, all resolved); `check_src.sh` en, de, fr stayed byte-exact, `check_src128.sh`, `--emu128` and `make test` passed afterwards.
- Worktree set up (`work/elite128/` a real folder; `work/arcelite`, `work/xray`, `work/stock_mem_image.bin` and the Firebird disk are symlinks into the main checkout, all gitignored). Gotcha: from `work/xray` a relative `../../tools/...` resolves to the main checkout, so run the 128K tests with absolute script paths.
- Scripts follow `main`'s layout (`disks/`, `build/elite128.dsk`, `dskx.is_original`, `make disk6128` / `listing6128`); one `CLAUDE.md` (the 128K notes live in `src/elite128/CLAUDE.md`); one `rvmstate.py` (`--sna OUT --curcfg`); `check_src128.sh` fails on a stale `equ`; Firebird's `CHEAT.BAS` taken off the 128K disk (then replaced by our trainer, below); `docs/_filled_ships.md` untracked as on `main` (it lives in `docs_other/` of the main checkout).
- Checked 2026-11-21: `main` defines its own `add_file` in `tools/build_dsk.py`, so the "`make expanded` fails on `main`" note of 2026-11-20 does not apply to `main` (the branch calls `dskx.add_file`).

### Features `main` got since the fork (all ported, 2026-11-20 unless noted)

- Trumbles aboard block the other added missions (6 bytes at the start of the docked stub; `TR=5 test_mission128.py` loads no overlay).
- A sells the whole hold (`src/elite128/sell_all.asm`, `test_sellall128.py`).
- Ship packs (13 flight images in bank 5, a random pack at every launch, nine hulls as types 20-28 generated by `tools/ship128.py`, `hullFindType` via `mxHullType`; `test_packs128.py`) and C64-like traffic (hostile limit `0x5A`, junk width 35, escort pack 1-4).
- Laser sights as an overlay on `bankInit` (`lasersights128.asm`; `test_sights128.py`).
- Kill count on the status page (own `killHook` in the glue, same page text as `main`; `test_killcount128.py`).
- Esc at the second digit of a quantity (`test_escdigit128.py`).
- Trainer, save editor, save lister and the ship viewer (2026-11-21, below).
- German and French trees changed on `main`: nothing to do for 128K (English only).

### Pirates in the top right (closed 2026-11-21, on the user's word)

- Reported as "pirates always appear in the top right". Disproved as a spawn bias: `spawnShip` is byte-identical in the 64K and 128K sources, 80 spawns per type land in all four quadrants (z always `&3200`), and a Cobra Mk III at (+1500, +1000) and (-1500, -1000) draws at the upper right and lower left, so neither the spawn nor the projection is biased. The hostile start was replaced anyway by the spawn variance (`SPAWN_VARIANCE`). Closed because it was proven wrong and fixed; I did not re-test the symptom myself. If it ever comes back: an RVM state or screenshot at the moment it happens (`tools/rvmstate.py --sna`, slots with `--slots`), compare the sign bytes, look at the later movement and the other callers (`spawnCommand0`, `spawnEscortPack`, the missions, `-DTRAFFIC`'s pack code). Comparison with the other versions: `docs/_ship_spawning.md`.

### Licence, parked RAM and pack test (2026-11-21)

- **Licence files:** `NOTICE_128K.md` is folded into `NOTICE` as items 6 to 10 ("Not in this repository" extends item 5) and removed; `LICENSE` lists `src/elite128/` under "no licence granted", `src/viewer128/` under MIT and the 128K docs under CC BY. Nothing to decide about ArcElite for the default build (own hulls from the game's blueprints; Fessor's hulls with his permission; only `HULLS=arcelite` reads ArcElite data, kept in `work/`).
- **Parked-RAM rule re-verified on the relocated layout** (`BUILD=128` for `test_parked_ram.py` and `test_parked_save.py`, new menu-driven `test_parked_save128.py`): over flight, two dock and launch cycles and a hyperspace jump 0 of 3100 marker bytes in the 34 zero runs changed; the docked save works without markers, and marking a single run (`&B819`, 22 bytes, `&1259` in low memory) is enough to break it, so the firmware's disk code reads zero runs of the docked copy as state. The old probe's forced-PC save does not complete on the 128K build. The rule stands: no code in the zero runs of the parked block.
- **Ship pack hook test:** `tools/tests/test_ship_packs128.py` (in `run_all.py --emu128`): each pack's flight image at `&9D9E`, `mxShipTable` hands out the extra hull about half the time, never touches types 8, 15 and 18, keeps A, B and DE; all seven packs pass.

### 2026-11-21

- **Trainer and save tools on the 128K disk:** `TRAINER`, `EDITSAVE`, `LISTSAVE`, `CONVSAVE` and a ready commander `LEN.BIN`; fourth address row in `CHEATB.ASC` (line 830) derived by `tools/cheat128.py`, which `check_src128.sh` and `build_dsk128.py` run as a stale check (`--write` fixes the row). `tools/tests/test_tools128.py` (in `run_all.py --emu128`): pokes at `CALL &1C82` and after the title, `EDITSAVE`, `LISTSAVE`. Details: `docs/_cheats.md` "The 128K build".
- **Save key decided:** the 128K build has its own key (the relocated `EquipShip` code), compatibility comes from the converter; `test_saves.py` pins the four keys.
- **`CONVSAVE`:** converts a save between the UK, French, German and 128K builds, either way, equal to `saveedit.py --to-key-disk` byte for byte; on the 128K disk and `elite64.dsk` (the French and German 64K disks have no room for it).
- **Ship viewer:** `RUN"SHOWSHPS` shows the same 29 ships as the title selector with the 64K viewer's layout (yellow name and counter, sky blue frame and labels, kills/bounty/speed/energy from the blueprint header; `tools/mk_viewer128.py`, `src/viewer128/viewer.asm`, `test_viewer128.py`).
- **`buf_7406` bug:** the galactic hyperdrive start loaded `0xF30A` instead of `0x7406` after the relocation (a number labelled as an address); now a literal.
- **Title music** on the title screens only, as in the 64K game (`musiquex.asm`, the player overlays 4 KB of flight-only code in bank 7, `NOTMUSIC.BIN` restores it; `test_music128.py`). Checked on `elite64.dsk`: the 64K game has it on the title only too.
- **Spawn variance, phase 1** (`SPAWN_VARIANCE` in `config.inc`, on): hostile types start at a random distance and direction from the front 270 degrees (`spawnVariance` in the overlay on `bankInit`, 59 bytes, called at the end of `spawnShip`); measured over 80 spawns per type, none in the rear cone; the five emulator tests, flight and `make test` pass.
- **`docs/_memory_map.md` split:** the 64K map stays there, the 128K banks, the Gate Array notes and the layout table are in `docs/_memory_map_128k.md`.
- **Title:** the Cobra over the prompt text is fixed (text printed after the ship, double-buffered title with a text cache); checked after the merge.

# TODO

Open work first, finished items at the bottom (section *Done*). `CLAUDE.md` keeps the short list; details live in `docs/`. Things we do not know yet are in `docs/_open_questions.md`.

## Open

### Game and build

- [ ] Ship packs (`docs/_ship_packs.md`): play through jumps and launches; try hiding the pack load; Boulder and Transporter do not fit yet; check role flags and kill values against the C64 table. [full text](docs/_todo_notes.md#ship-packs)
- [ ] Added missions are English only (no translated texts; the mission disk is built from `src/elite` only). Suggested: German first, then French. [full text](docs/_todo_notes.md#added-missions-english-only)
- [ ] French "Statut Legal" is still long: it needs 4 padding bytes that print nothing, and no code in the French message table does (`docs/_my_changes.md`).
- [ ] ships are still see-through (stars between the edges): options in `docs/_ship_occlusion.md`; try the bounding box (B) first, after measuring the free bytes in the `-DMISSIONS` build
- [ ] Optional speed: `drawViewportFrame` redraws a constant frame each frame (about 1.5% of the frame); unroll or draw the edge bytes once. Needs free bytes in flight, so low priority.
- [ ] Save on a write-protected disk resets to BASIC. Suggested: catch the AMSDOS error in `checkMedia`, return to the menu; measure the bytes first. [full text](docs/_todo_notes.md#write-protected-save)
- [ ] (deferred 2026-11-16, no room with `-DMISSIONS`) Legal status number on the status line, about 14 bytes per flight image; kill count and status number in German and French. [full text](docs/_todo_notes.md#legal-status-number)
- [ ] Laser sights on the English mission disk: 108 bytes, about 13 short in the `COMMONXX` tail; French sights untested in an emulator. Suggested: an overlay, or one hull less in packs 1 and 2. [full text](docs/_todo_notes.md#laser-sights-on-the-mission-disk)

### Missions

- [ ] Real playthrough of the whole chain with save and load; no real docking has triggered each offer yet. Suggested: script it with cpcxray from `firebird_in_flight.sna`. [full text](docs/_todo_notes.md#real-playthrough)
- [ ] Trumbles: a second end condition besides a sun or an escape pod (aboard they block every other added mission since 2026-11-13, so a player who never meets either stalls the chain), interplay with selling, the sprite-count thresholds.
- [ ] More than six Trumbles drawn (a fuller screen at big counts): blocked, the Trumbles flight image is full (608 of 608); 12 sprites need about 25 bytes (state array and counter mask), only the sprite trim below frees some (`docs/_missions_built.md` section 6).
- [ ] Tune the added missions (20 asteroids, 50% and 22% spawn rates, Birera as the police target); optionally the Cobra Mk III that Elite Plus adds to the asteroid mission.
- [ ] A per-commander random mission order (not built: no room in the stub plus Constrictor overlay).
- [ ] Space: the stub plus Constrictor overlay (3 spare since 2026-11-13, with the sell-all key resident) have a little room; the flight images are full since the kill count (2026-11-15): Trumbles 608 of 608, pack 1 and the Constrictor 606, pack 2 604 (`docs/_missions_built.md`).
- [ ] Optional: furs (4 t) and a death sound when the Trumbles die in a sun; about 24 bytes, so the sprite must lose 4 rows. [full text](docs/_todo_notes.md#furs-when-the-trumbles-die-in-a-sun)
- [ ] A CPC colour option for the Trumble fur.
- [ ] Test `CHEAT` stock mission stages 2 and 3 (rows not run, `docs/_missions_built.md` section 7), the pirate-boarding poke and the unlimited-hold toggle in play.

### Space and speed

- [ ] Cheap flight-space savings (2026-11-13; each is small, so do them together and measure the tail with `-DMISSIONS`):
  - [ ] Hull dedup behind `-DENHANCED`/`-DMISSIONS`: point the Splinter edge offset at the Capsule's block, drop 24 duplicate bytes. [full text](docs/_todo_notes.md#hull-dedup)
  - [ ] String tables: re-encoding saves only about 48 bytes (`docs/_memory_map.md`); skip unless a mission needs exactly that.
- [ ] Peephole pass in a separate variant build, not in the byte-exact `src/elite/`: in `commonxx` 28 unconditional and 28 conditional `jp` within
      +-127 bytes can be `jr` (56 bytes), 24 `call X` + `ret` can be `jp X` (24 bytes, only if nothing jumps to the `ret`), up to 19 `ld a,0`
      to `xor a` (only where flags are unused) and 7 `cp 0` to `or a`: about 100 bytes. Everything after a shrunk routine moves, so cheat
      pokes, the save key offset (`&2BE`), pointer tables kept as `db` and self-patched code need rechecking. Low value for the effort.
- [ ] Write a script that lists each peephole candidate with address and references, to check them by hand.
- [ ] Measure the ISR's worst-case stack depth at `&A000` (the top of the free tail), then fix the safe size of the tail.

### Disassembly and research

- [ ] `tools/relabel.py` for `src/elite_de` and `src/elite_fr`, if wanted (needs `disasm_german.py`/`disasm_french.py` into a scratch dir; `src/elite` is done).
- [ ] Coverage of the data ranges so far: flight only (`firebird_in_flight.sna`); run `exec_in_data.py` from the entry snapshot, the docked state and the chart views too (`--sna`).
- [ ] Name the last `dat_` variables by tracing (`tools/trace_unknowns.py`; `dat_2F36` and `dat_38E1` were not hit, need a run with a real galactic jump and the inventory screen); the seed byte `dat_3D2D` is rewritten by `waggle_galaxy`.
- [ ] The remaining 7 `dat_` labels in `src/elite/` (counted with `grep -c "^dat_"`), checked 2026-11-09 (23 before this pass). Done: 16 address/message-id immediates
  (`&2000 &4000 &3FC0 &7F00 &7F01 &7F03 &7F10 &7F89 &640A &7B05 &6170 &7EFD &80FF &C03F &C040 &CE00`) are numeric operands in
  `src/elite`, `elite_de` and `elite_fr`; `dat_6161`/`dat_6163` are `smcIndicatorPatch1/2`; 2026-11-09: `&2710 &5B4E &5C4C &58C1 &FFFF` also numeric, and renamed
  `saveChk0..3` (`&0F5B-&0F5E`), `edgeVecX/Y/Z` (`&5921-&5925`), `catalogBuf`, `tempString1End`, `casOutAddr`, `keybFlags0` (`&8E23`, a flag byte decoded as `adc a,h`).
  `dat_2F36` is now `fuelPriceByte`, `dat_38DE` is byte 2 of the credits high word. Left: `dat_0F01` (code label whose address is loaded), `dat_38DE`, `dat_38E1`
  (cargo/market bytes, see `docs/_savegame.md`), `dat_3D2D` (planet-type byte after the target seed), `dat_8427` (return-address stub), `dat_90A2` (inside ship data).
  - **Variables with an unknown role**: `&1B2A-&1B73` (entity slot workspace), `&38DE`/`&38E1` (block pointers; `&38E1` is the
    market byte, see `docs/_missions.md` section 3), `&3B3F-&3B69` (galactic chart buffers), `&3D2D` (7 bytes after the target
    seed), `&5921-&5925` (three words in the ship-edge drawing code), `&1BE3`, `&2F36`, `&864B`, `&C083`, `&FFFF`, and `largeaxx`
    `&0F01-&0F5E` (save menu; `&0F01` is a code label whose address is loaded).
  - **Labels inside or between instructions** (dead code or operand bytes, name or fold into the neighbour): `&2710`, `&3A6C`,
    `&5860`, `&58C1`, `&5B4E`, `&5C4C`, `&7406`, `&8427`, `&8E23`, `&90A2` (label inside ship data; the end sequence clears 5 bytes from it).
  Method that worked: align the declaration order of Fessor's variable blocks (`extended/source/EliteMasterSource.asm`) with
  the stock block by count of bytes, check one anchor (`work/fessor_to_stock.sym`) and the initial data value, then read the uses.
- [ ] Optional: comments for `chardefs1-7` (`common2x`, never referenced by label) and `sEntityunknown` as a named field of the ship record (byte `+0x26`).
- [ ] Optional: strip the screen-address remarks from the German and French copies of the scanner and alert icon comments (not checked there).
- [ ] CPC+: check the other PSG/PPI port users for the same ordering problem (`MUSIQUEX`, joystick reads; grep `0xF4`/`0xF6` writes in `src/elite/`).
- [ ] Cleanups skipped in the /simplify pass: one shared cpcxray test harness (`tools/tests/test_*.py` copy about 500 lines), shared test snapshots, deriving the per-build patch addresses in `check_src.sh` from symbols, state-mask equates shared by the stub, picker and images.
- [ ] Share the listing parser between `tools/deadcode.py` and `tools/dbcode.py` (both define their own `parse()`).

### Housekeeping

- [ ] Update `work/xray/` disk copies and snapshots if they still use the old disk names.
- [ ] `.claude/` (holds only `scheduled_tasks.lock`): add it to `.gitignore` or leave it untracked.

## Done

### General

- [x] allow Escape to exit the buy menu (goods): done (one byte, `docs/changelog_archive.md`)
- [x] Escape at the second digit of a buy or sell quantity undid nothing: fixed 2026-11-16 under `-DENHANCED` (`escQtyOperand`, same size, save key untouched).
- [x] Key pre-delay 0.43 s -> 0.16 s (`sub_403E`, `-DENHANCED`, 2026-11-10); play-tested by the user, feels faster.
- [x] `tools/z80dis.py` decoded no `push ix/iy` (missing case in `uses_hl`); fixed 2026-11-11, round trip of a fresh disassembly still byte-identical (49 instructions where 38 `db` runs were).
- [x] Fold the fixed decoder into the hand-edited trees without regenerating them: `tools/relabel.py` (done 2026-11-11 for `src/elite`: 33 `db` runs in `commonxx.asm`, 1 in `musiquex.asm`, 4 labels added; `check_src.sh` byte-exact).
- [x] Status screen tidy-up in German and French (2026-11-10, `docs/_my_changes.md`).
- [x] Station headlines in column 2 in German and French (2026-11-10).
- [x] Cash on the quantity line in German and French (2026-11-10).
- [x] stars no longer shine through the planet and sun (`STAR_OCCLUDE`, `docs/changelog_archive.md`)
- [x] star patch checked on the German and French builds by the user, 2026-11-16.
- [x] `tools/build_dsk.py --fr` builds `work/elite_fr_rebuilt.dsk` from the French Firebird disk (2026-11-10)
- [x] show different ships on load, arrow keys left/right for next (`TITLESEL`, all three builds, with the ship name; the press-space screen opens on the Cobra Mk III)

### Missions (build)

- [x] Trumble squeak: keep effect 13 (flags2 bit 5), chosen by ear with `RUN"TRUMBLE` on 2026-11-09.
- [x] Trumbles gate: offered once in the gap between the Constrictor reward and the plans offer (2026-11-09).
  - [x] Correct `docs/_memory_map.md`: the "`&9751-&97A0`, 80 bytes, filler" row is the Python/Big Trader edge block (live hull data), not free space. Doc-only, no bytes. Done 2026-11-16.
  - [x] Dead 10 bytes at `unusedGetFlightMode`/`unusedGetCloakFlag` (`&204E`, `&2053`): used by `killSpace` (kill count, 2026-11-15). Open: the 3 spare bytes of `unusedViewBorderFill`.
- [x] Fessor's Constrictor hull: he confirmed by private mail that the hull and his names and findings may be used; credited in `missions_hull.asm`, `README.md` and `docs/_references.md` (his source and beta stay out of the repo).
- [x] (done 2026-11-15) Kill count on the status page, "Rating: Harmless - 12": `src/elite/killcount.asm`, English only; German and French still need it (translated spacing, width check of the longer labels, and room: the French tail has about 65 bytes left after the laser sights).
- [x] Merge `addon-missions` into `main` (fast-forward 2026-11-16; `check_src.sh`, `de` and `fr` pass).
- [x] Macros: only `DUP` for the long runs (done); the short idioms and inline-argument calls stay as they are.
- [x] Built: Constrictor, Thargoid plans, stolen police ship (Elite Plus 4), asteroid bombardment (Elite Plus 6), Trumbles with sprites and squeak; trainer prompts, `saveedit.py`, `SHOWSAVE.BAS`, `EDITSAVE.BAS`; README and hidden files on the mission disk.

### Disassembly

- [x] Name the `dat_` variables: 109 of 176 named on 2026-11-07 (`tools/rename_labels.py`, then called `rename_dat.py`; map in `tools/rename_maps/`); `tools/check_src.sh` still byte-exact.
- [x] (done 2026-11-07: 8 tables, byte-exact) Turn pointer tables into `dw` and annotate; never rerun `tools/disasm_stock.py` into `src/elite`.
- [x] (done 2026-11-07: searched by use, `ld hl,<table>` followed by a word fetch; only `CircleParmTable` was new) Look for more pointer tables hiding behind unlabeled targets. `dustParticleAdrTable` is a runtime buffer in the code area, not a table.
- [x] (done 2026-11-07) Seed names from `work/fessor_to_stock.sym`: 1,471 of 1,581 descriptive names were already in `src/elite/`; the rest are Fessor-only code or weak `delta` matches. Last two (`cloakTick`, `commandsPatchTable`) named from callers. Remaining `LAB_ram_`/`dat_` labels need naming from callers or the Spectrum map.
- [x] Name the equipment bytes in the commander save (done 2026-11-07, see `docs/_savegame.md`). `&38E1` is the market random byte; the escape pod clears from it and so keeps alien items (`&38F2`): a confirmed off-by-one bug (`docs/_missions.md` section 3), fixed under `-DENHANCED` in all three trees (`podCleanOperand`); the default build keeps the original bytes.
- [x] (done 2026-11-07, `src/elite_de/`, `bash tools/check_src.sh de`) Do the German build (`Elite_DE_cracked.dsk`). Open: the 140 generic `sub_`/`loc_`/`dat_` labels there, the German-only routines (system data text, token printing in `COMMON2X`), `dw` tables, and a German text table decoder.

### Research

- [x] Obtain the CPC+ patch disk (UK) and diff it against the UK disk (done 2026-11-07: a one-byte patch, `&8DA0` `ED 79` -> `ED 49`, see `docs/_cpcplus.md`).
- [x] (done 2026-11-07, byte-exact vs Redbox patch, `check_src.sh` expects it) CPC+: apply the one-byte fix to `src/elite/commonxx.asm` (`getPPI_Input`, second `out (c),a` after `or 0xC0` -> `out (c),c`), assemble with `tools/check_src.sh`, and check that `COMMONXX` differs from stock in exactly that byte and equals `work/plus_patch/x/COMMONXX.BIN` (`docs/_cpcplus.md`).
- [x] (done 2026-11-07, byte-exact: one differing byte at `&8F3F`, `check_src.sh fr` expects it) CPC+: apply the fix to the French build. German needs nothing (the disk has it).
- [x] (done 2026-11-07: `work/elite_plus.dsk`; passes in Caprice32 on 6128 and 6128+, which does not reproduce the bug) CPC+: build a patched DSK from the Firebird disk and test. Still open: test in an emulator that models the Plus port order (WinAPE with Plus PPI emulation on), or on real hardware.
- [x] (done 2026-11-07: `Elite_DE_cracked.dsk` already has the fix, see `docs/_cpcplus.md`) CPC+: find the German patched disk (`Elite (G) ... Gepatcht Tastatur fur Plus.dsk`; forum attachment is gone) or apply the same one-byte change to the German routine (relocated, different address) once the German build is disassembled.
- [x] (done 2026-11-07, `docs/_missions.md`: the station takeover is the Thargoid invasion, system 0's station) Match the four missions Amtix lists (supernova, pirates take over Space Station 1, cloaking device, ECM jammer)
      to the code; the station-takeover one is not yet found. The ST and MSX sources have the Thargoid base invasion as mission 5;
      check whether Amtix's "pirates take over" is the same mission described loosely.
- [x] (done 2026-11-07, `docs/_architecture.md`) Find where the disk-drawing routine can crash when a planet leaves the screen. Open: sweep radii under 9, the screen-memory fill path (`ce2func46`) and a finer edge grid with `tools/circle_sweep.py`.
- [x] (done 2026-11-07) Verify Fessor-vs-stock findings in `extended/FESSOR_VS_STOCK.md`: nearly all flags were false positives (variables, or dead code Fessor drops). Open from it: name the stock dead blocks (`buf_5860`, `Filemenuloop` tail, `&B1/&A9` pair, `jp` stubs after `msgSupernovaMission`) and `buf_3A6C` as a data buffer.
- [x] (done 2026-11-07, `docs/_architecture.md`) Check whether `Elite_UK_original_protected.dsk` ships the Anaconda and Transporter after all: it does not. The German disk's second set of 14 blueprints is a second copy of `COMMONXX` in the raw image (tracks 7 and 27; all 17 sampled windows occur twice), not a new ship set; why the copy is there is unknown (`iDSK -l` lists only one `COMMONXX.BIN`).

### Missions (plan and phases)

- [x] Phase 0: no fixed-table save key needed (2026-11-08), DSK writer is `tools/build_dsk.py` (the dead-code reclaim is cancelled: there is none).
- [x] Phase 1-3: mission state byte, text compressor (`tools/textenc.py`), hull converter (`tools/fessor_hull.py`), Constrictor mission: built.
- [x] Phase 4: Thargoid plans and the Navy energy unit: built.
- [x] Read the Trumbles code in the C64 source (done, in `docs/_missions.md`). Still unread: `TRIBTA`/`TRIBMA` sprite count, inventory print, escape pod.
- [x] Decided: Trumbles are ported, with sprites (270 bytes) and squeak (`docs/_missions_built.md`).
- [x] (done 2026-11-07, `docs/_missions.md` "Colours") Check which of the two-colour sprite pens exist in every view (`setInks`) before drawing anything into the off-screen bitmap: only pen 2 (ink 20, black) is fixed in views 0-3; pens 0/1/3 vary by system, supernova mode and cloak. Confirmed in cpcxray (all 8 systems, supernova mode, cloak, energy-bomb flash); explosion flicker of pen 3 is listing-only.
- [x] (done 2026-11-07, `docs/_missions.md` section 3) Check the ten system names of the Constrictor and Plans chains against the CPC name generator: all ten exist once, in the right galaxy.
- [x] Decided the mission order and trigger: fixed chain Constrictor -> plans -> stolen ship -> asteroids after the stock missions, Trumbles independent (`docs/_missions_built.md` section 1).
- [x] Read the ST Cougar mission (`$40-$41`) and compare with the CPC Asp code (done 2026-11-07, table in `docs/_missions.md` section 1).
      "elite-msx-skoolkit" does not exist online; `elite-skoolkit` is the Spectrum one and `ricbit/elite` the MSX one (cloned, `docs/_references.md`).
- [x] Read the CPC's laser-only Asp draw test and the non-laser gate reset (done 2026-11-07, source only, not yet traced in cpcxray): `todoWorkVariable` -> `aspMissionState`, `LAB_ram_5755` -> `drawShipDistanceCheck`, `LAB_ram_5175` -> `aspGateClearIfBlueprint1E`, `LAB_ram_517c` -> `aspGateReset`. 
- [x] (first pass done 2026-11-07, `docs_other/_spectrum_map.md`) Mine `work/ext_msx/skoolkit/src/elite.skool` (Spectrum) to seed `src/elite/`: 43 names, ~140 cross-reference comments. Maths, circle, text, chart, trade, movement and spawn routines now commented (about 170); open: the 25 matched routines still without a comment, the unmatched rest; match the rest (routines the CPC splits differently); label `sqr_table` (`&C600`) and the default commander (`&39D1`).
- [x] Stolen police ship: built from the Elite Plus logic (`docs/_missions_built.md`).
- [x] Settled the two save-format disagreements with the type-in (2026-11-07, in-game jump): `&48` is the tech level minus 1 (`presentTechLevel`), and y is at `&43`, x at `&45`; see `docs/_savegame.md`.
- [x] Scan the `db` runs of `COMMONXX` for unreferenced code (`tools/dbcode.py`): about 130-155 bytes in six routines, plus 28 bytes of labelled
      dead code (`tools/deadcode.py`). See `docs/_architecture.md`.
- [x] (done 2026-11-08, `tools/dead_trace.py`, two 700-key runs; static check too) Those six chains are live code or a buffer, not dead (`docs/_architecture.md`). Free space is the 610-byte tail only.
- [x] (done 2026-11-09) Dynamic labels share prefixes in all three trees: `smc_` for the 59 self-patched code/operand labels (`smc_patchInk0`, `smc_PatchAND_1`, ...; `smcIndicatorPatch1/2` kept), `buf_` for 14 runtime buffers (`buf_5860`, `buf_3A6C`, `buf_3B3F..3B69`, `buf_1B2A..1B73`, `buf_7406`). Left alone: `altJrPoint*` (jump targets), `commandsPatchTable` (a table), the `equ` aliases and the operand labels without `patch` in the name (`dvRotatePixmask`, `irds22`, ...). `check_src.sh`, `de`, `fr` pass.
- [x] (2026-11-08, branch `missions-foundation`) `tools/textenc.py` and `tools/size_report.py`; open there: fixed-table save key, state bytes in `&38FD/&38FE/&3905/&3906`, string-table entry point, `chkMissions` dispatch, `-DMISSIONS` variant.
- [x] (2026-11-08) No fixed-table save key needed while the `EquipShip` window stays unchanged (`tools/size_report.py` checks it).
- [x] (2026-11-08) `-DMISSIONS` scaffold in `src/elite` (tails as conditional includes, `missionOrder` 21 bytes); next: string-table entry point, `chkMissions` dispatch, state-byte accessors, then mirror to `elite_de`/`elite_fr` if the missions are kept.
- [x] (2026-11-08) Docking hook, string-table entry (`missionShow`) and `missionState` byte `&38FD` working in cpcxray; next: accessors for the other state bytes, a real docked mission (Constrictor briefing), custom-token text measurement.
- [x] (2026-11-08) Constrictor docked part built and tested (offer, hints, reward; 772 bytes of the 812-byte docked tail). Open: flight part (hull, spawn at Orarra, kill hook setting state 3), shrinking the text (galaxy-1/2 briefings share most words; custom tokens; system names from the seed), Plans/Trumbles.
- [x] (2026-11-08, branch `mission-constrictor`) Hull in the flight tail (261 bytes) and ship type 19 via `mxShipTable`; flight tail 280/610 used. Wireframe close-up done (`work/xray/output/missions_constrictor_closeup.png`). Spawn at Orarra and the kill hook are built and tested (flight tail 441/610). Special behaviour built (only military lasers or better hurt it; flight tail 477/610). Open: play the whole chain through once in a real game (galaxy change, Orarra spawn, real kill, reward); check its ECM and missiles from the hull header; then Plans.
- [x] (2026-11-08, branch `mission-plans`) Thargoid plans built and tested: docked 402 bytes, flight +98 (575/610 with the Constrictor). Constrictor + Plans docked do not fit together (802 + 402 > 812): overlay or shared code/text needed. Open: real playthrough, Trumbles branch.
- [x] (2026-11-08) Overlay scheme built and tested (stub 97 + MISSIONC 711 / MISSIONP 362; docked tail 808/812; flight tail 575/610 with both missions). Open: the flight side is still resident (Trumbles needs room: shrink or overlay the flight code), name-hash order when Trumbles exists, shrinking the Constrictor text (the two briefings share most words), a real playthrough.
- [x] (2026-11-08, branch `mission-trumbles`) Trumbles built and tested; flight code is now overlaid too (images 125/587/223/286 bytes, vectors + launch hook); docked max 787/812.
- [x] Trumble sprites built (up to six, pen 3, `missions_trumble_art.txt`); count thresholds are in.
- [x] Constrictor flight image: now 609 of 610 bytes; trimming is tracked under Missions above ("Space").
- [x] Trumbles sound done (effect 13).
- [x] Branches are merged into one: `addon-missions` contains all of them; only its merge into `main` is open (see Missions above).

### Build and test

- [x] (done: `tools/saveedit.py`, `EDITSAVE.BAS`, `SHOWSAVE.BAS`) Build a commander save editor (`tools/`): show every field of a save (name, cash, kills and rank, legal status, galaxy,
      fuel, missiles, lasers, equipment, cargo, market stock, mission variables and flags such as the cloak and jammer bits)
      and let the user edit them, then write a valid save: re-encrypt with the right build's key (English `&2BE`, German
      `&2C2` in `LARGEAXX`) and recompute both checksums. Cash is a word pair (thousands of Cr plus decicredits), see
      `docs/_savegame.md`. Nicer than patching the default commander in `CHEAT`; `tools/savedec.py` already decodes, and `tools/elitekey.py` reads the key straight from a game disk.

### Housekeeping

- [x] Removed the redundant extractions in `work/` (done 2026-11-07: `ext_EliteSource`, `ext_EliteMasterSource`, `ext_ELITE_EXT_DISK`, `build_fessor_run`; each checked byte-for-byte against an archive that stays). `ext_st`, `ext_nes`, `ext_msx` are reference clones in use (tools read `ext_msx/skoolkit`), so they stay.

# TODO

Open work, most useful first. `CLAUDE.md` keeps the short list; details live in `docs/` (there is no `notes.md`). Things we do not know yet are in `docs/_open_questions.md`.

- [x] allow Escape to exit the buy menu (goods): done (one byte, `CHANGELOG.md`)
- [ ] Escape at the second digit of a buy or sell quantity leaves the first digit's trade applied (`todoInputNumber0to9`, `largeaxx.asm` ~line 205: ESC takes `jr nc,LAB_ram_095f` without `restore_trade_state`; DEL undoes it correctly). Review 2026-11-10, not fixed.
- [ ] Save on a write-protected disk resets to BASIC (seen in RVM on the mission disk). The game's own hook only catches AMSDOS's "Retry, Ignore or Cancel?" message (`LAB_ram_855e`, `checkMedia`); whether the stock game behaves the same, and what a graceful handler would cost in bytes, is untested (needs a clean boot in cpcxray on a read-only disk; `firebird_at_entry.sna` is not valid for disk-menu tests).
- [x] Key pre-delay 0.43 s -> 0.16 s (`sub_403E`, `-DENHANCED`, 2026-11-10); play-tested by the user, feels faster.
- [ ] Optional speed: `drawViewportFrame` redraws a constant frame each frame (about 1.5% of the frame); unroll or draw the edge bytes once. Needs free bytes in flight, so low priority.
- [ ] Filled ships on a 6128 (polygons in RAM bank 7, `-DHULLFILL`-style switch, 464 falls back to lines): prototype in `tools/proto_fill/`, findings and the integration analysis in `docs/_filled_ships.md`. First step: a tool that turns the CPC blueprint edges into face loops.
- [x] `tools/z80dis.py` decoded no `push ix/iy` (missing case in `uses_hl`); fixed 2026-11-11, round trip of a fresh disassembly still byte-identical (49 instructions where 38 `db` runs were).
- [x] Fold the fixed decoder into the hand-edited trees without regenerating them: `tools/relabel.py` (done 2026-11-11 for `src/elite`: 33 `db` runs in `commonxx.asm`, 1 in `musiquex.asm`, 4 labels added; `check_src.sh` byte-exact). [ ] Same for `src/elite_de`/`src/elite_fr`, if wanted (their references need `disasm_german.py`/`disasm_french.py` into a scratch dir).
- [ ] Coverage of the data ranges so far: flight only (`firebird_in_flight.sna`); run `exec_in_data.py` from the entry snapshot, the docked state and the chart views too (`--sna`).
- [ ] radar (scanner) flicker. Measured 2026-11-09 (cpcxray, in flight): a game frame is about 200 ms; `UpdateScanner` takes about 24 ms, of which `cleanScanner` (blank the area, rebuild the background from `gfxdataScanner` with `exx`-heavy loops, drawn straight on the visible screen) is about 21.7 ms and the ship dots about 2 ms. That is longer than one video frame, so the beam always crosses a half-drawn scanner. Ruled out: a hidden-row off-screen copy (rows 24-31 of the screen RAM, `&C600-&C7FF` etc., hold the square and other lookup tables) and an erase list for the dots (an `or`-plotted pixel cannot be restored without saved bytes, up to about 650). Free space: 20 bytes in the dead block, 10 in `unusedGet*`; the Constrictor and Trumble flight images leave 1 byte in the tail. Left: rewrite `cleanScanner` in place to about 14 ms (tight nibble-split loop) and sync `UpdateScanner` to just after the beam has passed the scanner (ISR counter), so the blank period (about 16 ms) falls between two passes; cannot be verified in cpcxray (no beam), only by eye.
- [ ] Added missions (Constrictor, plans, stolen ship, asteroids, Trumbles) are English only: no translated texts, and the mission disk and hooks are built only from `src/elite` (`build_dsk.py --missions` refuses `--de`/`--fr`). The biggest gap between the builds.
- [x] Status screen tidy-up in German and French (2026-11-10, `docs/_my_changes.md`). [ ] French "Statut Legal" is still long: it needs 4 padding bytes that print nothing, and no code in the French message table does (details in `docs/_my_changes.md`).
- [x] Station headlines in column 2 in German and French (2026-11-10).
- [x] Cash on the quantity line in German and French (2026-11-10).
- [x] stars no longer shine through the planet and sun (`STAR_OCCLUDE`, `CHANGELOG.md`)
- [ ] ships are still see-through (stars between the edges): options in `docs/_ship_occlusion.md`; try the bounding box (B) first, after measuring the free bytes in the `-DMISSIONS` build
- [ ] test the star patch in cpcxray on the German disk (`work/elite_de_rebuilt.dsk`) and the French build (only the English snapshot was shown so far)
- [x] `tools/build_dsk.py --fr` builds `work/elite_fr_rebuilt.dsk` from the French Firebird disk (2026-11-10)
- [ ] more than one color for moving stars?
- [ ] or other color for asteroids?
- [x] show different ships on load, arrow keys left/right for next (`TITLESEL`, all three builds, with the ship name; the press-space screen opens on the Cobra Mk III)
  
## Missions (branch `addon-missions`, overview in `docs/_missions_built.md`)
- [ ] Real playthrough of the whole chain with save and load (so far only forced states, direct calls, the trainer pokes and a booted disk). A real docking triggering each offer has not been seen in the running game.
- [x] Trumble squeak: keep effect 13 (flags2 bit 5), chosen by ear with `RUN"TRUMBLE` on 2026-11-09. [ ] Still open: decide a Trumble end condition other than a sun (the chain waits on them since 2026-11-13) and the sprite-count thresholds.
- [ ] Tune the added missions (20 asteroids, 50% and 22% spawn rates, Birera as the police target); optionally the Cobra Mk III that Elite Plus adds to the asteroid mission.
- [x] Trumbles gate: offered once in the gap between the Constrictor reward and the plans offer (2026-11-09). [ ] A per-commander random order (not built, no room in the stub plus Constrictor overlay).
- [ ] Space: the stub plus Constrictor overlay (now 0 spare) and the Constrictor flight image (now ends at &9FFE, the limit set by an ASSERT for the interrupt push at &9FFE-&9FFF; 0 spare) need trimming before any further change there.
- [ ] Investigate hull compression for flight space (2026-11-13, analysis only, nothing built). The 19 blueprints take about 3.8 KB (`shipdatAspMk2` `&8FC7` to the tail at `&9D9E`). Already shared by the stock game: Rock Hermit/Asteroid, Single Trader/Cobra Mk3, Big Trader/Python (header-only entries pointing into the other ship's blocks). A general compressor (zlib 36%, about 1.3 KB) does not pay: hulls are read in place through the entity's pointer every frame, so an unpacker would need a RAM buffer per ship type on screen (the Cobra Mk3 alone is 395 bytes, up to 6 types at once) plus its own code, and the only free flight RAM is the 610-byte tail. Packing the fixed strides (vertex 6, edge/face 4, header 23 bytes) means patching every indexing site in the draw code, which costs bytes and speed.
  **Cheap approach:** only de-duplicate and re-point, no format change. Today only the Capsule/Splinter edge blocks (24 bytes) are identical, so the gain is about 25-50 bytes. It is contiguous because the hulls sit directly before the free tail and only `shipGFXdataTable`, `mxShipTable` and `ld hl,dat_90A2` (inside the Asp Mk2 block) refer to them: point the Splinter header's edge offset at the Capsule's block, close the gap, and the tail starts 24 bytes lower. Next step: check the other sub-blocks and the face bytes for partial overlaps (the 171-byte Cargo/Pirate1/Thargon are not equal), and correct the `&9751-&97A0` "filler" row in `docs/_memory_map.md` (it is the Python/Big Trader edge block, not free).
  **Risk of the non-default build:** the default build must keep the original bytes (`check_src.sh`), so the change has to sit behind `-DENHANCED` or `-DMISSIONS`. Then (1) that build no longer matches the stock binaries, and every address after the moved hulls shifts (the tail, `mxFlightId` `&9DB6`, the vector table, the Constrictor image limit and its `ASSERT`); (2) a new marker is needed in `check_src.sh` and the change must be done in all three trees (`elite`, `elite_de`, `elite_fr`); (3) it is only as tested as the missions are (no real playthrough yet), and a wrong offset shows up as a broken ship (wireframe garbage or a crash on spawn) only when that ship appears, so each hull needs a flight check (`tools/test_flight_hull.py`); (4) the save key sits in `LARGEAXX` (`EquipShip`), so saves are not affected, but the disk loaders and tests that assume `&9D9E` must be rechecked.
- [ ] Parked firmware RAM: check in cpcxray that the zero bytes in `&0040-&1A3F` (the parked copy of `&A600-&BFFF` in flight) are really never read or written, in flight and across a dock, save, load and launch cycle (2026-11-13: 3 s in `firebird_in_flight.sna`, 0 read and 0 write hits on the whole range; `tools/test_parked_ram.py` fills the 36 zero runs of 16+ bytes (3169 bytes, largest 513 at `&08AE`, 480 at `&0CF6`, 284 at `&18C0`) with a marker and runs flight with chart keys, the docking tail, the docked screens, F1 launch and 5 s flight: 0 marker bytes changed in flight, after launch and after the second flight, 1 changed (`&0224`, in the parked copy while docked, back after launch); a longer run added a hyperspace attempt (`6`, cursor tap, `h`; the jump itself was not confirmed on screen), more chart keys and a second dock and launch: the same result, 0 changed in flight, 1 changed (`&0224`) in each docked phase; not yet covered: save and load, the disk menu, a real docking, the mission overlays). Needs: a long flight session with keys, then the docked period with breakpoints on `&A600-&BFFF`, since the firmware's disc routines write there while docked and anything placed in those bytes would be overwritten before the launch swap brings it back. Only then could flight code live there.
- [x] Fessor's Constrictor hull: he confirmed by private mail that the hull and his names and findings may be used; credited in `missions_hull.asm`, `README.md` and `docs/_references.md` (his source and beta stay out of the repo).
- [ ] Optional: furs when the Trumbles die in a sun. Idea: when the sun brings the count to 0, add a fixed 4 t of furs (good 11, `cargoHold+11`), capped by `cargoSpaceFree`. Costs about 24 bytes in `mxSunImpl` (Trumbles image has 8 spare, limit `&9FFE`), so 16 bytes must be freed: cutting the sprite from 14 to 10 rows does it (drop rows 0, 6, 12, 13 of `missions_trumble_art.txt`, `ld c,10` in `mxBlit`). Once per commander (the offer is made once), so no trading exploit. A scaled amount (peak count) needs a stored byte and more space. Also a death sound for the sun: reuse an existing effect via a bit in `sfxFlags2Bitmap` (about 5 bytes), pick by ear with `TRUMBLE.BAS`.
- [ ] Merge `addon-missions` into `main`; check `check_src.sh de` and `fr`.
- [ ] Name the last `dat_` variables by tracing (`tools/trace_unknowns.py`; `dat_2F36` and `dat_38E1` were not hit, need a run with a real galactic jump and the inventory screen); the seed byte `dat_3D2D` is rewritten by `waggle_galaxy`.
- [ ] Optional: comments for `chardefs1-7` (`common2x`, never referenced by label) and `sEntityunknown` as a named field of the ship record (byte `+0x26`).
- [ ] Optional: strip the screen-address remarks from the German and French copies of the scanner and alert icon comments (not checked there).
- [x] Macros: only `DUP` for the long runs (done); the short idioms and inline-argument calls stay as they are.
- [ ] Cleanups skipped in the /simplify pass: one shared cpcxray test harness (`tools/test_*.py` copy about 500 lines), shared test snapshots, deriving the per-build patch addresses in `check_src.sh` from symbols, state-mask equates shared by the stub, picker and images.
- [x] Built: Constrictor, Thargoid plans, stolen police ship (Elite Plus 4), asteroid bombardment (Elite Plus 6), Trumbles with sprites and squeak; trainer prompts, `saveedit.py`, `SHOWSAVE.BAS`, `EDITSAVE.BAS`; README and hidden files on the mission disk.

## Disassembly (`src/elite/`)
- [x] Name the `dat_` variables: 109 of 176 named on 2026-11-07 (`tools/rename_dat.py`, map in `tools/rename_maps/`); `tools/check_src.sh` still byte-exact.
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
- [x] (done 2026-11-07: 8 tables, byte-exact) Turn pointer tables into `dw` and annotate; never rerun `tools/disasm_stock.py` into `src/elite`.
- [x] (done 2026-11-07: searched by use, `ld hl,<table>` followed by a word fetch; only `CircleParmTable` was new) Look for more pointer tables hiding behind unlabeled targets. `dustParticleAdrTable` is a runtime buffer in the code area, not a table.
- [x] (done 2026-11-07) Seed names from `work/fessor_to_stock.sym`: 1,471 of 1,581 descriptive names were already in `src/elite/`; the rest are Fessor-only code or weak `delta` matches. Last two (`cloakTick`, `commandsPatchTable`) named from callers. Remaining `LAB_ram_`/`dat_` labels need naming from callers or the Spectrum map.
- [x] Name the equipment bytes in the commander save (done 2026-11-07, see `docs/_savegame.md`). `&38E1` is the market random byte; the escape pod clears from it and so keeps alien items (`&38F2`): a confirmed off-by-one bug (`docs/_missions.md` section 3), fixed under `-DENHANCED` in all three trees (`podCleanOperand`); the default build keeps the original bytes.
- [x] (done 2026-11-07, `src/elite_de/`, `bash tools/check_src.sh de`) Do the German build (`Elite_DE_cracked.dsk`). Open: the 140 generic `sub_`/`loc_`/`dat_` labels there, the German-only routines (system data text, token printing in `COMMON2X`), `dw` tables, and a German text table decoder.

## Research
- [x] Obtain the CPC+ patch disk (UK) and diff it against the UK disk (done 2026-11-07: a one-byte patch, `&8DA0` `ED 79` -> `ED 49`, see `docs/_cpcplus.md`).
- [x] (done 2026-11-07, byte-exact vs Redbox patch, `check_src.sh` expects it) CPC+: apply the one-byte fix to `src/elite/commonxx.asm` (`getPPI_Input`, second `out (c),a` after `or 0xC0` -> `out (c),c`), assemble with `tools/check_src.sh`, and check that `COMMONXX` differs from stock in exactly that byte and equals `work/plus_patch/x/COMMONXX.BIN` (`docs/_cpcplus.md`).
- [x] (done 2026-11-07, byte-exact: one differing byte at `&8F3F`, `check_src.sh fr` expects it) CPC+: apply the fix to the French build. German needs nothing (the disk has it).
- [x] (done 2026-11-07: `work/elite_plus.dsk`; passes in Caprice32 on 6128 and 6128+, which does not reproduce the bug) CPC+: build a patched DSK from the Firebird disk and test. Still open: test in an emulator that models the Plus port order (WinAPE with Plus PPI emulation on), or on real hardware.
- [x] (done 2026-11-07: `Elite_DE_cracked.dsk` already has the fix, see `docs/_cpcplus.md`) CPC+: find the German patched disk (`Elite (G) ... Gepatcht Tastatur fur Plus.dsk`; forum attachment is gone) or apply the same one-byte change to the German routine (relocated, different address) once the German build is disassembled.
- [ ] CPC+: check the other PSG/PPI port users for the same ordering problem (`MUSIQUEX`, joystick reads; grep `0xF4`/`0xF6` writes in `src/elite/`).
- [x] (done 2026-11-07, `docs/_missions.md`: the station takeover is the Thargoid invasion, system 0's station) Match the four missions Amtix lists (supernova, pirates take over Space Station 1, cloaking device, ECM jammer)
      to the code; the station-takeover one is not yet found. The ST and MSX sources have the Thargoid base invasion as mission 5;
      check whether Amtix's "pirates take over" is the same mission described loosely.
- [x] (done 2026-11-07, `docs/_architecture.md`) Find where the disk-drawing routine can crash when a planet leaves the screen. Open: sweep radii under 9, the screen-memory fill path (`ce2func46`) and a finer edge grid with `tools/circle_sweep.py`.
- [x] (done 2026-11-07) Verify Fessor-vs-stock findings in `extended/FESSOR_VS_STOCK.md`: nearly all flags were false positives (variables, or dead code Fessor drops). Open from it: name the stock dead blocks (`buf_5860`, `Filemenuloop` tail, `&B1/&A9` pair, `jp` stubs after `msgSupernovaMission`) and `buf_3A6C` as a data buffer.
- [x] (done 2026-11-07, `docs/_architecture.md`) Check whether `Elite_UK_original_protected.dsk` ships the Anaconda and Transporter after all: it does not. The German disk's second set of 14 blueprints is a second copy of `COMMONXX` in the raw image (tracks 7 and 27; all 17 sampled windows occur twice), not a new ship set; why the copy is there is unknown (`iDSK -l` lists only one `COMMONXX.BIN`).

## Missions (plan in `docs/_missions.md`)
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
- [ ] Test `CHEAT` stock mission stages 2 and 3 (rows not run, `docs/_missions_built.md` section 7), the pirate-boarding poke and the unlimited-hold toggle in play.

- [x] Scan the `db` runs of `COMMONXX` for unreferenced code (`tools/dbcode.py`): about 130-155 bytes in six routines, plus 28 bytes of labelled
      dead code (`tools/deadcode.py`). See `docs/_architecture.md`.
- [x] (done 2026-11-08, `tools/dead_trace.py`, two 700-key runs; static check too) Those six chains are live code or a buffer, not dead (`docs/_architecture.md`). Free space is the 610-byte tail only.
- [ ] Measure the ISR's worst-case stack depth at `&A000` (the top of the free tail), then fix the safe size of the tail.
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
- [x] Trumble sprites built (up to six, pen 3, `missions_trumble_art.txt`); count thresholds are in. [ ] Still open: a CPC colour option for the fur.
- [x] Constrictor flight image: now 609 of 610 bytes; trimming is tracked under Missions above ("Space").
- [x] Trumbles sound done (effect 13). [ ] Open: an end condition other than the sun, interplay with selling. The escape pod ends them (2026-11-09). Since 2026-11-13 Trumbles aboard also block every other added mission (docked stub), so a player who never meets a sun or a pod stalls the chain: a second end condition matters more now.
- [x] Branches are merged into one: `addon-missions` contains all of them; only its merge into `main` is open (see Missions above).
- [ ] (superseded) Evaluate the mission overlay scheme (load missions one at a time, random order per commander): loader size, disk space, save-load restore.

## Space savings (review 2026-11-07)
- [ ] Peephole pass in a separate variant build, not in the byte-exact `src/elite/`: in `commonxx` 28 unconditional and 28 conditional `jp` within
      +-127 bytes can be `jr` (56 bytes), 24 `call X` + `ret` can be `jp X` (24 bytes, only if nothing jumps to the `ret`), up to 19 `ld a,0`
      to `xor a` (only where flags are unused) and 7 `cp 0` to `or a`: about 100 bytes. Everything after a shrunk routine moves, so cheat
      pokes, the save key offset (`&2BE`), pointer tables kept as `db` and self-patched code need rechecking. Low value for the effort.
- [ ] Write a script that lists each peephole candidate with address and references, to check them by hand.
- [ ] Share the listing parser between `tools/deadcode.py` and `tools/dbcode.py` (both define their own `parse()`).

## Build and test
- [x] (done: `tools/saveedit.py`, `EDITSAVE.BAS`, `SHOWSAVE.BAS`) Build a commander save editor (`tools/`): show every field of a save (name, cash, kills and rank, legal status, galaxy,
      fuel, missiles, lasers, equipment, cargo, market stock, mission variables and flags such as the cloak and jammer bits)
      and let the user edit them, then write a valid save: re-encrypt with the right build's key (English `&2BE`, German
      `&2C2` in `LARGEAXX`) and recompute both checksums. Cash is a word pair (thousands of Cr plus decicredits), see
      `docs/_savegame.md`. Nicer than patching the default commander in `CHEAT`; `tools/savedec.py` already decodes, and `tools/elitekey.py` reads the key straight from a game disk.
- [ ] Write the rebuilt binaries into a copy of the DSK (keep AMSDOS headers) and boot it in cpcxray.
- [ ] A script that does the sjasmplus build and byte compare for all four `src/elite/` files in one step.
- [ ] Try one small gameplay change end to end (for example the hold size) to prove the pipeline.

## Housekeeping
- [x] Removed the redundant extractions in `work/` (done 2026-11-07: `ext_EliteSource`, `ext_EliteMasterSource`, `ext_ELITE_EXT_DISK`, `build_fessor_run`; each checked byte-for-byte against an archive that stays). `ext_st`, `ext_nes`, `ext_msx` are reference clones in use (tools read `ext_msx/skoolkit`), so they stay.
- [ ] Update `work/xray/` disk copies and snapshots if they still use the old disk names.

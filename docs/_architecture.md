# Architecture of the CPC port and what we learned from disassembling it

## The disassembly (`src/elite/`, 2026-11-07)

`src/elite/` is sjasmplus source for `LARGEAXX`, `COMMONXX`, `COMMON2X` and `MUSIQUEX`, regenerated and verified by
`python3 -I tools/disasm_stock.py` (never into `src/elite` once hand-edited; see `CLAUDE.md`). Details: `src/elite/README.md`.

- Method: own Z80 decoder (`tools/z80dis.py`, round-trip checked on all five binaries), recursive descent from Fessor's code labels, the
  entry `&1C82`, `ld`-loaded addresses and runs of 3+ words pointing at plausible code. Inline data after `printStringFollowingByte`,
  `printFollowingTokenWithSpace`, `todo_printroutinew` (1 byte each) and after `rst 1,2,3,5` (a word) is skipped. Unreached bytes are `db`;
  text runs are strings. `tools/z80dis.py` cannot decode `push ix`/`push iy`, so such routines stay `db`.
- All four files assemble to the original bytes. Code share: `commonxx` 69%, `largeaxx` 39%, `common2x` 13% (blank hidden-screen bytes and the
  character set), `musiquex` 7% (score data). `NOTMUSIC.BIN` equals `COMMONXX` `&6000-&6FFF`; `MUSIQUEX` labels come from Fessor's `musiquep.asm`
  (patched build = stock - `&363`), saved as `work/musiquex.sym`.
- Gold vs Firebird: the code is identical except `&0998` in `LARGEAXX` (see `_disks.md`); `largeaxx.asm -DFIREBIRD` gives the Firebird bytes.
- cpcxray's own source export was not used (trace-based coverage looked unreliable with overlaid files and self-patching plotters; untested).
- Open: about 430 Fessor labels are unplaced; several variables are still `dat_XXXX`; most `dw` pointer tables are converted.

### Naming variables

109 of 176 `dat_` labels were renamed with `tools/rename_dat.py` (maps in `tools/rename_maps/`); batch 2 named the data tables and turned two
immediates into numeric operands. Evidence, in order of strength: Fessor's variable blocks in the same byte order as the stock block (anchored by a
named neighbour such as `dustViewDirection` at `&6BF7` or `charXY` at `&38C4`, and matching initial values such as `0x55` at `&6BFD`); then the
uses (`cargoHold` indexed by good number in `storeScoopedGood`; illegal goods 3, 6, 10 in `chkForIllegalGoods`); then save files (a 34 t cargo with
1 t free and the large-cargo-bay byte `0xFF` in `LEN.BIN`). A `ld hl,dat_XXXX` that is really an immediate (`ld hl,0x3900` in `copyCharset`, a ROM
character address) keeps a numeric operand. Run `bash tools/check_src.sh` after every rename.

### Other builds

- **German** (`src/elite_de/`, 2026-11-07, `bash tools/check_src.sh de`): the same program with German text, not relocated code. Token tables have other
  lengths, so data between routines moves (10 bytes in `LARGEAXX`, `&114` or `&148` in `COMMONXX` regions) and instruction addresses change; the instruction
  stream is the same apart from a few German-only places (`src/elite_de/README.md`). `COMMON2X` differs in 270 bytes; `MUSIQUEX`, `INDICATO`, `PICTURE`
  and `ELITE.BAS` are identical to English. Method: `tools/map_german.py` walks both binaries in lockstep from `&1C82` (same-shape instructions, 8-bit
  immediates ignored), pairs operands and re-seeds from English labels by instruction fingerprint (81% of English code bytes paired);
  `tools/disasm_german.py` then runs the stock disassembler with the paired names. Its free tail is smaller (282 vs 610 zero bytes). Disk headers have
  load address 0 except `COMMONXX.BIN`; `ELITE.BAS` is the English unprotected loader.
- **French** (`src/elite_fr/`, `bash tools/check_src.sh fr`, `tools/map_french.py` + `disasm_french.py`): four extra text functions for accents and shifted
  string numbers; no CPC+ fix.

## Overall design

- A Spectrum port, not BBC. It draws into a linear off-screen bitmap at `&A000-&BFFF` (Mode 1, 4 px/byte, 64 bytes per line) and copies it to screen
  RAM at `&C000`; the copy is the main speed brake (Fessor: in `ELITE.BAS` before `CALL &1C82` do `POKE &1EDF,8` to copy half the buffer and see the fps jump).
- Colour split is interrupt-driven (`doColorSplit`; 300 Hz, counter 1-5 per frame, SFX and keyboard at counter 3, dashboard colours at 4).
- Routines are swapped in and out of the same address ranges at takeoff and docking (`&0040-&1A3F` with `&A600-&BFFF`, so the BASIC program at `&170` is
  destroyed once the game runs). Memory is very tight; the music player and some code overwrite unused routines.
- Line drawing: two self-patched Bresenham plotters at `&800D` and `&8025`. The patcher at `&7CE5` (`manipulate_drawroutine1/2`) rewrites `RRC C`/`RLC C` and
  `INC L`/`DEC L` per octant. Pixel address at `&7EFC` (`H=2`, `L=y`, shifts to land at `&A000`).
- Circles: the chart-view circle writes straight to screen RAM, unclipped; the in-flight planet/sun circle uses the off-screen bitmap and builds lines with a
  PUSH loop (63 pushes plus an IX store, with a private stack) to stay safe from the interrupt.
- Maths: square tables at `&4600`/`&4700` (low/high bytes, quadratic) and `&5600-&57FF`. Fessor never identified most maths routines; the Spectrum
  disassembly names them (`mult_b_c`, `mult_b_c_msb`, `div_de_h`, `divide_signed` = DVID3B2, `approx_sqrt_16bit`, `diff_of_products`, ...), now renamed in `src/elite/`.
- Ship blueprint header is **23 bytes** on the Z80 versions, 20 on the 6502 ones, fields in a different order.
- "Boarded by Pirates" game over on docking exists. Savegame encryption exists in the stock game (Fessor disabled it in his beta). CubeMDOS crashes Elite
  because Elite copies the firmware area with the floppy routines.
- Missions in stock: the Asp/cloaking-device mission and the supernova mission only; the BBC's Constrictor and Thargoid plans are missing (we add them: `_missions_built.md`).

### Entry point `&1C82` (read from the first boot in cpcxray, interpretation of the loop unconfirmed)

Calls `&4F22` and `&877C` (setup), programs the CRTC (R7=`&1D`, R1=`&20`, R2=`&2A`, R6=`&18`), calls `&1EC7` with A=`&14`, sets `SP=&7497` (stored at `&1C7F`), more
init (`&7369`, `&4A9E`, `&8745`). The main loop starts near `&1CD9`: `&4531`, `&1FF1`, `&1D73`, `&5624`, `&1ED1`, `&4535`, then tests `(&8E22)`: `&FF` loops, `&5A` takes a
special path (`&875E`, `&0D28`, `&4646`, `&1F89`). `&1DA8` is incremented once per pass (frame counter). Reaching `&1C82` takes about 13.7 s of emulated time.

### Ships

The CPC has 19 ship-table entries and 14 full blueprints; the 6502 versions' Boa, Anaconda, Transporter, Mamba, Adder, Gecko, Cobra Mk I, Worm, Moray, Shuttle,
Constrictor and Dodecahedron station are absent. Checked 2026-11-07: `shipGFXdataTable` (`&1B..`, 19 four-byte entries `C3 lo hi n`) is entry for entry the ZX
Spectrum table (Coriolis, missile, escape pod, splinter, canister, boulder, two asteroids, Viper, two Cobra Mk III, two Pythons, Asp, Fer-de-Lance, Thargoid,
Sidewinder, Krait, Thargon; `n` values 0,0,1,1,1,1,1,2,2,2,2,3,3,3,3,3,4,4,4), and each blueprint has its Spectrum size (Coriolis 287, Cobra 395, Asp 297 bytes). A
signature scan (23-byte header with vertex offset `17 00`) over every file and the raw 199,680-byte disk image finds only those 14 blueprints (the other 5 entries
are 23-byte stubs): no hidden Anaconda, Transporter, Boa, Mamba or Constrictor in code, data or unused sectors. Ship names are not in the string tables (the CPC never
prints them). The Boulder is present (entry 6, 87 bytes). The German disk gives 28 hits because its raw image holds `COMMONXX` twice (tracks 7 and 27).

## Hazard

A `PUSH` to addresses near `&5800` with interrupts on can be hit by an interrupt writing its return address. Fessor's double-buffer attempt corrupted the
square tables at `&57FE-&57FF` this way (flattened station every 90 degrees). Relevant if screen RAM or tables move.

## Dead code and free space (2026-11-07/08)

Goal: find bytes a mission port can reclaim. **Conclusion: there is no reclaimable dead code in the `db` runs.** Reliable free space is the 610-byte tail of
`COMMONXX` (`&9D9E-&9FFF`) minus the top bytes the stack uses, plus 10 bytes of `unusedGetFlightMode` (`&204E`) and `unusedGetCloakFlag` (`&2053`).
`unusedViewBorderFill` (`&1FD2-&1FF0`, 31 bytes, no references) now holds `dustPlotPixel` under `STAR_OCCLUDE`.

1. **Fessor's switches** (`extended/source/EliteMasterSource.asm`): `defdeactivate`, `defdeactivate1-13`, `defdeactivatereal` and `defdeactivatechar` (all on in the
   beta) switch off 17 blocks, about **450 bytes** (the character-set copy at source line 11270 is 206 of them; the rest 2-49 bytes: a screen fill, a 16-byte routine
   at `&5800`, `enableROM`/`disableROM`). His "735 bytes saved, 1,034 left" (`COMMONXX` ends at `&9BF6`) also counts moved tables. `defdeactivatesfx`, `defallowfullstop`
   and `defcheat` are off in the beta. Finding the same blocks in the stock binary by byte pattern **does not work** (unique hits landed in live routines `sub_1FCC`,
   `chkCloak`, `loc_5072`, `Filemenuloop`); do not use such a list.
2. **Reachability** (`tools/deadcode.py` on the sjasmplus listings): from `&1C82`, treating all `db` blocks as live, it finds only 28 bytes in two regions
   (`altJrPoint3` and neighbours `&7198-&71AE`, 23 bytes; `LAB_ram_8aaa` `&8AAA-&8AAE`, 5), both live by design (see Dynamic labels). The rest is in `db` runs.
3. **Known free space**: the 610 zero bytes above; 812 zero bytes at the end of `LARGEAXX` (`&1714-&1A3F`; the file is reloaded at every docking, written 952 times by
   `loadLARGEAXX` and by nothing else in the trace, so the mission stub uses it); the firmware copy area `&0040-&083F` while docked.
4. **Code-shaped chains in `db` runs** (`tools/dbcode.py`: chains of at least 12 bytes ending in `ret`/`jp`/`jr` that call only source labels; 17 chains, 846 bytes).
   *Not code:* the zero entity area `&1A40-&1B7A`, variable blocks `&38C1-&3929`/`&392A-&3937`, tables `&1B81-&1B9A` and `&939D-&93A8`, tails of live routines
   (`&2997`, `&3D7B`, `&522A`, `&6BEB`, `&838B`). *Live (static check and cpcxray, 2026-11-08), not the "130-155 bytes of dead code" first claimed:* each is the tail of a routine
   starting with `push ix`/`push iy`: `&53D7` in `LAB_ram_53cf` (`move_ship_forward` three times), `&5DD2` in `SUB_ram_5dcf` (called from `&51CC`, `&563C`), `&8243` in
   `execSpawncmd4`, `&8365` in `spawnAtEntityCoordinates`, `&89F5` in `LAB_ram_89f4`/`LAB_ram_8a10`; `&6C0A` is in the runtime buffer `dustParticleAdrTable`; `&9751-&97A0` is filler.
5. **Trace** (`tools/dead_trace.py`, two runs of 700 random 1.3 s key presses from `firebird_in_flight.sna`, docking and cloak/Thargoid states forced every 25 presses;
   `traces/dead_run1.json`, `dead_run2.json`): the positive controls all fired (`LAB_ram_53cf`, `SUB_ram_5dcf`, `execSpawncmd4`, `LAB_ram_89f4`, `LAB_ram_8a10`, `chkCloak`,
   `handleEntitys`, `spawnCommand0` or `loadLARGEAXX`); `spawnAtEntityCoordinates` (`&8364`) did not (rare spawn command). `alt_animated_effect_reset` (`&719D`) fired;
   `altJrPoint3` and `LAB_ram_8aaa` did not but are jump targets (below, and three `jr`s in the `&89F4` chain at `&8A70`, `&8A78`, `&8A80`). Only `unusedGetFlightMode` and
   `unusedGetCloakFlag` (10 bytes) never fired. Other writes to the free tail were the BASIC ROM's memory clear (`ldir` at `&C154`) after a key sequence left the game.

### Stack in the free tail

With SP at `&A000` an interrupt pushes at `&9FFE-&9FFF` (seen at the first interrupt after key `4`, PC `&0038`, SP `&9FFE`). Nothing may sit there: the mission flight
images end at or below `&9FFE` (an `ASSERT` checks it), and the ISR's worst-case depth is unmeasured, so keep clear of more if in doubt.

## Dynamic labels (found 2026-11-08)

Labels whose bytes change at runtime or sit inside an instruction. Patched operands carry the prefix `smc_`, runtime buffers `buf_` (since 2026-11-09). Static
dead-code or free-space claims must not touch them. Sources: `equ` aliases at the end of `src/elite/*.asm`, patch-named labels, and a diff of `&1A40-&9FFF` after
700 random presses (`changed_ranges` in `traces/dead_run*.json`; rarely used patches are missing from the "seen" list). Method for more: assemble into a scratch dir
with `--lst`, run `tools/dead_trace.py`, map each changed range to the nearest label with the `.sym` file.

- **Labels inside instructions** (`equ` aliases, patched or jumped into): `ce2func63` `&25D6`, `ce2func74` `&2688`, `loc_3A88`, `loc_5958`, `sub_61B5`, `sub_6953`,
  `sub_71CB`, `loc_7873`, `loc_86F7` (`commonxx`); `LAB_ram_f638`, `LAB_ram_f6ea` (`common2x`).
- **Self-modified operands seen changing in flight:** circle masks `smc_ce2func64patchmask7` `&2603`, `...65patchmask8` `&2606`, `...75patchmask9` `&26B5`, `...76patchmask10` `&26B8`;
  viewport inks `smc_patchInk0` `&28E3`, `smc_patchInk1` `&28EC`, `smc_patchInk3` `&28F5`, `smc_patchInk2` `&28FE`, `smc_patchSecondInk3` `&2911`, `smc_patchAnotherInk1` `&2953`,
  `smc_patchAnotherInk1_2` `&2993`; line plotters `smc_PatchAND_1` `&33E1`, `smc_PatchAND_2` `&33E8`, `smc_PatchOR_2` `&3469`, `smc_PatchOR_4` `&34AD`; `smc_isPatchStrlen` `&40F2`,
  `smc_patch1` `&4AAA`, `smcIndicatorPatch1` `&6161`; `dvRotatePixmask` `&8018`, `dh2RotatePixmask` `&804B`, `dh1nextPixelline` `&8030` and the other `dh*`/`dv*` operands
  `&801B-&806B`; operands `&3B08-&3B1C` (`LAB_ram_3b07 .. SUB_ram_3b1a`), `LAB_ram_3bae` `&3BAF`; `CallHL` `&2AEA`; `irds22` `&2CCD`, `irds_dat7/9` `&2DB4/&2DB7`.
- **Self-modified, not seen changing:** `smc_PatchA_1`, `smc_PatchAND_3`, `smc_PatchOR_1`, `smc_PatchOR_3`, `smc_dcPatchAdr1..4`, `commandsPatchTable` targets, `smc_patch3`,
  `smc_charPatchD628/D650/D6D8/D700/D7D8`, `smcIndicatorPatch2`, `smc_md1_patchcommands`, `smc_md2_patchcommands`, `smc_dvpatchadr5/7`, `smc_dhpatchadr6`, `smc_patchFWTextfunctions`,
  `smc_patchmask1..6`, `smc_patchmask11..16`, `smc_patchJr`, `smc_patchJr1`, `smc_dfcPatchpos` (`common2x`), `smc_cpatchloop`, `smc_patchViewPortInk0/1`, `smc_patchviewPortInk3`.
- **Self-patched jumps:** `smc_PatchJRZat714b` and `smc_PatchJRat715e` (hyperspace tunnel) choose among `altJrPoint1-3` and `LAB_ram_7192`; `smc_PatchORat7159` patches the
  compare value. So `altJrPoint*` look unreferenced statically but are live.
- **Runtime buffers inside the code image:** entity slots `&1A40-&1B01` (zero area to `&1B7A`), `&1C02-&1C39` flight state, `tblDustCoordinates` `&34F4-&3544`, `buf_3A6C`
  `&3A6C-&3A83`, `buf_3B3F/3B49/3B61` chart buffers, `qq3`..`travelDistance` `&3D22-&3D63`, `buf_5860` `&5860-&589B` (60 bytes, written at runtime), `todo_tableforedges`/
  `tableUnkownFacedata` `&58EA-&592D`, dust tables `&6BED-&6C2D`, `dataShortTunnle` `&721D-&7224`, `buf_7406` `&7407-&7496` (about 140 bytes, `loc_745B`), `LAB_ram_7734+10`
  `&773E-&7749`, sound tables `&2D6C-&2DC9`, `FilenameNOTMUSIC` `&8830`, `dataFromPPI`/`keybFlags*` `&8D34-&8D8B`, `irki2_dat2/3` `&8F5C`, private stacks `ce2stack4` `&2727`,
  `stack5` `&2997-&29FD`, `stack1` `&4644`, and the variable block `&38C1-&3949`.

## The disc-drawing routine and Amtix's "infamous bug" (2026-11-07)

Amtix 13 (Pinto): the cassette release crashed intermittently ("hours, or a couple of minutes") when a planet drifted off screen; the "disk drawing routine" was shared with
*Gyron* and Spectrum Elite.

- Entry `todoDrawFilledCircle` `&E787` / `clearCircle` `&E795` (`common2x.asm`), called from `drawPlanetnSun` and `drawPlanet`. Parameters: `circleOffsetY` `&20C7`,
  `circleOffsetXlo` `&20C8`, flags `circleOffsetXhi` `&20C9` (bit 0 x sign, bit 1 y sign, bit 2 x overflow, bit 3 y overflow; set by `calcSunPlanetCoordinates`/`SUB_ram_6aa6`),
  `drawradius` `&20CA`. `smc_dfcPatchpos` `&E7AE` is `ret c` (in flight, discs under radius 9 are skipped), a `nop` during launch and docking.
- `CircleEntrypoint2` (`&20FB`) is a case tree on the centre being on or off screen (`ce2func1`..`ce2func33`). Edge cases fill whole lines through `ce2func43FillCompleteLinesinBM`
  (`&243A`): `ld sp,hl` at a bitmap line, then `push de` 32 times (one 64-byte line) per `djnz LineFillLoop`. Partial lines and the interior use a private stack at `&F72E`
  (`CircleParm0x11Mask`) and self-patched `jr` into a run of `push af` (`&CE50` onwards).
- **The guard:** at `&245B`, `cp b / jr nc,ce2func44 / ld b,a / inc b` clamps the line count in B to the lines left above the bitmap start. Without it the loop keeps pushing below `&A000`.
- **Test** (`tools/circle_sweep.py`, cpcxray, game in flight so the real ISR at `&2811` and layout apply; the snapshot at `&1C82` is the wrong state, as `&0038` still jumps to `&B941`
  inside the bitmap): stock build, 131,072 inputs (all 16 flag combinations, x and y in steps of 8, radii 9, 24, 48, 80, 120, 160, 200, 255): every call returns with SP restored and
  writes nothing outside the bitmap except the stack and the circle's own variables. With the clamp disabled (`&245C` `jr` instead of `30`), 20,480 inputs: 88 never return or return
  with a wrong SP, 107 write garbage (`F0F0`...) over `&7A9x`, `&81Ex`, `&29E7` and other code below the bitmap, all with flags 12-15 (a big, close planet with centre off screen) and
  radius 120 or more, plus deeper stack use of flags 6 and 7. That is the "planet moved off the screen" crash; the clamp is the fix and the cassette release presumably lacked it (not available to check).
- **Why intermittent:** with SP inside the bitmap, each 300 Hz interrupt pushes its return address there. Harmless inside the picture and harmless at `&A000`, because `COMMONXX` ends in unused
  zero bytes (`&9D9E-&9FFF`, 610 bytes UK, 282 German) that absorb the push (the CPU pushed `&2483`/`&2485` at `&9FFE-&9FFF` when an interrupt hit right after the last `push de` of `ce2func45`).
  Without the clamp the runaway overwrites live code, and what it hits depends on timing. Why Spectrum and *Gyron* did not show it: unconfirmed (on the Spectrum the memory below the screen is ROM).
- **Not covered:** the unclamped screen path (`ce2func46`, charts, `cirGetScrAddr`), radii under 9, a finer grid at the screen edges, writes at `&C000`+, real hardware; the ISR's worst-case depth.

## Title screen ship selection (`-DTITLESEL`, 2026-11-08)

Cursor and joystick left/right step the demo ship on both title screens. The code sits in the zero tail of `MUSIQUEX.BIN` (`&6E21-&6FFF`, about 120 bytes used; the file is
resident only while the title screens run, and a failed load is retried by `loadFile`, so the hooks cannot meet `NOTMUSIC`). A jump table at `&6E21` (`TITLE_SCREEN1`,
`TITLE_SCREEN2`, `TITLE_NEXT`, `TITLE_SHOW`) is called from four places in `COMMONXX` that keep their byte length. `splash2Shipnr` (`&1DA8`) holds the ship index in bits 0-2 and
"direction key already down" in bit 7; the eight hulls are in `titleShips` (spawn actions, high nibble = ship type - 2). The raw PPI rows (`dataFromPPI`) are read because `irki2`
rewrites `keybFlags2` into roll values. `tools/check_src.sh` checks the six `COMMONXX` addresses `musiquex.asm` hard-codes (plain and `-DMISSIONS`); test `tools/test_title_ships.py`.
The automatic pick on the press-space screen follows this list. English and German (the German `musiquex.asm` differs only in the six equates); French is not done.

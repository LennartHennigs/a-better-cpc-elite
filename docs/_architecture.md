## Disassembly of the stock build (2026-11-07)

`src/elite/` holds sjasmplus source for `LARGEAXX`, `COMMONXX`, `COMMON2X` and `MUSIQUEX`, regenerated and verified by
`python3 -I tools/disasm_stock.py`. Details are in `src/elite/README.md`. Summary:

- Method: own Z80 decoder (`tools/z80dis.py`, checked by linear-sweep round trip of all five binaries), recursive
  descent from Fessor's code labels (kind taken from how his source continues after each label), the entry
  `&1C82`, `ld`-loaded addresses and runs of 3+ words pointing at plausible code. Inline data after calls to
  `printStringFollowingByte`, `printFollowingTokenWithSpace`, `todo_printroutinew` (1 byte each) and after
  `rst 1,2,3,5` (a word) is skipped. Everything unreached is `db`; text runs are written as strings.
- Result: all four files assemble to the exact original bytes. Code share: `commonxx` 69%, `largeaxx` 39%,
  `common2x` 13% (mostly blank hidden-screen bytes and the character set), `musiquex` 7% (score data).
- `NOTMUSIC.BIN` is byte-identical to `COMMONXX` at `&6000-&6FFF`. `MUSIQUEX` labels come from Fessor's
  `musiquep.asm` (Ghidra names carry the stock address; patched build = stock - `&363`), saved as `work/musiquex.sym`.
- Gold vs Firebird: `Elite_UK_original_protected.dsk` and the since-deleted `Elite - Gold.dsk` had identical code. The Firebird disk differs only at
  `&0998` in `LARGEAXX` (`jr c,errorforNotEnoughCapacity` `38 19` -> `38 00`: buying goods ignores the hold-capacity
  test). `largeaxx.asm -DFIREBIRD` gives the Firebird bytes.
- cpcxray's own source export was not used. I expected trace-based coverage to be unreliable here (overlaid
  files sharing addresses, self-patching plotters, only executed code is classified), but I did not test it.
- Open: about 430 Fessor labels are unplaced (variables and rewritten code), so many variables are still `dat_XXXX`;
  most `dw` pointer tables are converted (the rest are `db`, see `src/elite/README.md`); the German `[G]` build is in `src/elite_de/` (see "German build" below).

## Disassembly findings (English build, booted in cpcxray)

Booted `Elite_UK_Firebird_cracked_trainer.dsk` on a CPC 6128 in cpcxray (`RUN"ELITE`), ran to `&1C82`, saved
`work/xray/output/firebird_at_entry.sna`, the image `firebird_0840_9fff.bin` (`&0840-&9FFF`), a screenshot, and
`firebird_disasm.txt`. Disk mounted read-only; originals unchanged. Reaching `&1C82` took about 13.7 s of
emulated time.

### Entry point `&1C82`

- Calls `&4F22` and `&877C` (setup), then programs the CRTC (R7=`&1D`, R1=`&20`, R2=`&2A`, R6=`&18`), calls
  `&1EC7` with A=`&14`, sets `SP=&7497` and stores it at `&1C7F`, then more init (`&7369`, `&4A9E`, `&8745`).
- Main loop starts around `&1CD9`: calls `&4531`, `&1FF1`, `&1D73`, `&5624`, `&1ED1`, `&4535`, then tests
  `(&8E22)`: `&FF` loops back, `&5A` goes to a special path (`&875E`, `&0D28`, `&4646`, `&1F89`).
  `&1DA8` is incremented once per pass (a frame counter).
- Interpretation of the loop is not confirmed.

## Architecture of the CPC port (as Fessor found it)

- It is a Spectrum port, not a BBC port. It draws into a linear offscreen bitmap at `0xA000-0xBFFF`
  (Mode 1, 4 px/byte, 64 bytes per line) and copies it to screen RAM at `0xC000`.
  The framebuffer copy is the main speed brake. Fessor's experiment: in the English `ELITE.BAS`,
  before `CALL &1C82` do `POKE &1EDF,8` to copy half the buffer and see the fps jump.
- Colour split is driven by the interrupt (`doColorSplit`; 300 Hz, counter 1-5 per frame, SFX and
  keyboard at counter 3, dashboard colours at 4). Palette and mode changes happen there.
- Routines are swapped in and out of the same address ranges at takeoff and docking. Memory is very
  tight; the music player and some code overwrite unused routines.
- Line drawing: two self-patched Bresenham plotters at `0x800D` and `0x8025`. The patcher is at
  `0x7CE5` (`manipulate_drawroutine1/2`), which rewrites `RRC C`/`RLC C` and `INC L`/`DEC L` per octant.
  Pixel address calc is at `0x7EFC` (`H=2`, `L=y`, shifts to land at `0xA000`).
- Circle routine for the chart view writes directly to screen RAM and has no clipping. The in-flight
  planet/sun circle uses the offscreen bitmap. Circle code builds lines with a PUSH loop (63 pushes plus
  an IX store with a private stack) to stay safe from the interrupt.
- Maths: square tables at `0x4600`/`0x4700` (low/high bytes, quadratic) and `0x5600-0x57FF`.
  Fessor never identified most of the maths routines; the Spectrum disassembly names them (mult_b_c, mult_b_c_msb, div_de_h, divide_signed = DVID3B2, approx_sqrt_16bit, diff_of_products, ...), they are renamed and commented in `src/elite/` (`docs/_spectrum_map.md`, 2026-11-07).
- Ship blueprint header is **23 bytes** on the Z80 versions, 20 bytes on the 6502 ones. Fields differ in
  order. Fessor decoded enough to show the Constrictor (2021-07-31) and later every BBC ship.
- Ships missing from the CPC (13 items): Boulder, Shuttle, Transporter, Boa, Anaconda, Mamba, Adder,
  Gecko, Cobra Mk I, Worm, Moray, Constrictor, Dodecahedron station. (We saw earlier that the Anaconda
  and Transporter are missing; this list is longer.) **Checked 2026-11-07 on `Elite_UK_original_protected.dsk`: the ship lookup
  table `shipGFXdataTable` (`&1B..`, 19 four-byte entries `C3 lo hi n`) is entry for entry the ZX Spectrum table (Coriolis, missile,
  escape pod, splinter, canister, boulder, two asteroids, Viper, two Cobra Mk III, two Pythons, Asp, Fer-de-Lance, Thargoid, Sidewinder,
  Krait, Thargon: same `n` values 0,0,1,1,1,1,1,2,2,2,2,3,3,3,3,3,4,4,4), and each blueprint has exactly the size of its Spectrum
  counterpart (e.g. Coriolis 287, Cobra 395, Asp 297 bytes), so no extra blueprint is hiding between them. A signature scan (23-byte
  header with the vertex offset `17 00`) over every file and over the raw 199,680-byte disk image finds only these 14 full blueprints
  (the other 5 table entries are 23-byte stubs) and no further header: no Anaconda, Transporter, Boa, Mamba or Constrictor on the
  disk, in code, data, or unused sectors. The ship names are not in the string tables either (no Anaconda or Transporter string; the CPC
  never prints ship names). The Boulder is present (entry 6, 87 bytes), so "Boulder" in the list above is wrong. The German disk gives 28
  hits for the same scan: the raw image holds `COMMONXX` twice (tracks 7 and 27 at the same sector index; all 17 sampled 64-byte windows occur twice), so those are two copies of the same 14.**
- Missions in the CPC version: the Asp/cloaking-device mission and the supernova mission. Missing
  compared with BBC: Hunting the Constrictor, Thargoid plans.
- "Boarded by Pirates" game over on docking exists; Fessor wanted it off.
- The French build has four extra text functions for accents and shifted string numbers; the German one
  differs more. Fessor replaced hard-coded token numbers with equates (`db token03`).
- Savegame encryption exists in the stock game (Fessor disabled it in the beta).
- CubeMDOS crashes Elite because Elite copies the firmware area with the floppy routines (stock too).

## Hazard worth remembering

Anything that stores to `0x5800`-ish addresses via PUSH while interrupts are on can be hit by an
interrupt call writing a return address. Fessor's double-buffer attempt corrupted the square tables at
`0x57FE-0x57FF` this way (flattened station every 90 degrees). Relevant if we move screen RAM or tables.

## Naming variables (2026-11-07)

109 of the 176 `dat_` labels were renamed with `tools/rename_dat.py` (map: `tools/rename_maps/2026-11-07-dat-batch1.txt`); batch 2 (`...-dat-batch2.txt`) named the data tables and turned two immediates into numeric operands, leaving 58.
Evidence, in order of strength: Fessor's variable blocks in the same byte order as the stock block (anchored by a
named neighbour such as `dustViewDirection` at `&6BF7` or `charXY` at `&38C4`, and by matching initial values
such as `0x55` at `&6BFD` and `0x1E32` at `&2D6A`); then the uses (for example `cargoHold` indexed by the good number
in `storeScoopedGood`, and the illegal goods 3, 6 and 10 in `chkForIllegalGoods`); then the save files (a 34 t cargo
with 1 t free and the large-cargo-bay byte `0xFF` in `LEN.BIN`). A `ld hl,dat_XXXX` that is really an immediate constant
(for example `ld hl,0x3900` in `copyCharset`, a ROM character address) keeps a numeric operand. Run
`bash tools/check_src.sh` after every rename; it must report four `ok`.

## Dead code and free space (analysis 2026-11-07)

Goal: find bytes a mission port can reclaim (the plan in `docs/_missions.md`, section 3, needed the dead code). Three views.

**1. Fessor's switches** (`extended/source/EliteMasterSource.asm`, read only). The `defdeactivate`, `defdeactivate1` to
`defdeactivate13`, `defdeactivatereal` and `defdeactivatechar` flags (all on in the beta) switch off 17 blocks of code. Assembling each
block gives about **450 bytes** in total (one block, the character-set copy at source line 11270, is 206 of them; the others are 2 to 49
bytes: a screen fill, a 16-byte routine at `&5800`, the obsolete `enableROM`/`disableROM`, and similar). His comment "735 bytes saved,
1,034 left" (`COMMONXX` ends at `&9BF6`) is larger because it also counts tables he moved. `defdeactivatesfx`, `defallowfullstop` and
`defcheat` are off in the beta, so sound and the full-stop code were kept. Finding the same blocks in the stock binary by byte pattern
(operands wildcarded) was tried and **does not work**: the unique hits landed inside live routines (`sub_1FCC`, `chkCloak`,
`loc_5072`, `Filemenuloop`), so no stock address list from this method is trustworthy. Do not use one.

**2. Reachability over our source** (`tools/deadcode.py`, run on the sjasmplus listings; instructions in its header). It builds a graph
of labelled blocks (name references, fall-through, address words in code and data, `address-1` push/ret tables) from the entry point
`&1C82`, treats all `db` blocks as live, and reports code nothing reaches. Result: **28 bytes in two regions**: `altJrPoint3` and its
neighbours (`&7198-&71AE`, 23 bytes) and `LAB_ram_8aaa` (`&8AAA-&8AAE`, 5 bytes). Every other labelled routine is reached. So dead code is
not in the labelled code. It sits in the `db` runs, because `tools/disasm_stock.py` only follows reachable code and writes the rest as
bytes.

**3. Known free space** (from `docs/_missions.md`, section 3): 610 zero bytes at the end of `COMMONXX` (`&9D9E-&9FFF`); 812 zero bytes at the end of
`LARGEAXX` (`&1714-&1A3F`, whether free at runtime is unchecked, but the file is reloaded from disk at every docking); the firmware copy
area `&0040-&083F` while docked.

**4. Code hiding in the `db` runs** (`tools/dbcode.py`, same listings). It decodes every `db` run of `COMMONXX` with `tools/z80dis.py`
and keeps chains that end in `ret`/`jp`/`jr`, are at least 12 bytes long, and only call or jump to labels of the source. That is a strict
filter, so the result is a lower bound. 17 chains (846 bytes) pass; reading them:
- *Not code:* `&1A40-&1B7A` is the zero-filled entity area (zeros decode as `nop`), `&38C1-&3929` and `&392A-&3937` are variables, `&1B81-&1B9A`
  and `&939D-&93A8` are tables (`01 C3 lo hi` jump-table rows, 4-byte rows). `&2997`, `&3D7B`, `&522A`, `&6BEB` and `&838B` are pointed at by
  other words, so they are tails of live routines.
- *Code-shaped chains: all LIVE (checked 2026-11-08, static and in cpcxray).* The earlier reading ("130 to 155 bytes of unreferenced
  code") was wrong. Each chain is the tail of a live routine that starts with `push ix`/`push iy`, which `tools/z80dis.py` cannot decode,
  so the routine stayed `db` and its inner entry points looked unreferenced: `&53D7` is inside `LAB_ram_53cf` (reached by fall-through
  from `LAB_ram_53cc`: `move_ship_forward` three times), `&5DD2` inside `SUB_ram_5dcf` (called from `&51CC` and `&563C`), `&8243` inside
  `execSpawncmd4` (`&8242`, `jr z` targets), `&8365` inside `spawnAtEntityCoordinates` (`&8364`, `jr z`), `&89F5` inside `LAB_ram_89f4`
  and `LAB_ram_8a10` (`jr` targets); `&6C0A` is inside `dustParticleAdrTable`, a runtime buffer. `&9751-&97A0` (80 bytes) is filler.
- *Trace (2026-11-08, `tools/dead_trace.py`, two runs of 700 random key presses of 1.3 s each from `firebird_in_flight.sna`, docking and
  the cloak/Thargoid-variable states forced every 25 presses; results in `traces/dead_run1.json` and `dead_run2.json`):* positive controls
  `LAB_ram_53cf`, `SUB_ram_5dcf`, `execSpawncmd4` (`&8242`), `LAB_ram_89f4`, `LAB_ram_8a10`, `chkCloak`, `handleEntitys`, and
  `spawnCommand0` or `loadLARGEAXX` (one run each) all fired; `spawnAtEntityCoordinates` (`&8364`) did not (rare spawn command). Candidates:
  `alt_animated_effect_reset` (`&719D`) fired (hyperspace tunnel, key `e`); `altJrPoint3` (`&7198`) did not, but it is one of three
  targets of the self-patched `jr` at `PatchJRat715e`/`PatchJRZat714b` (see "Dynamic labels"), so it is live by design; `LAB_ram_8aaa`
  (`&8AAA`) did not fire, but three `jr` instructions inside the `&89F4` chain target it (`&8A70`, `&8A78`, `&8A80`). Only
  `unusedGetFlightMode` (`&204E`) and `unusedGetCloakFlag` (`&2053`) (10 bytes, no references of any kind) never fired.
  A write breakpoint on the free tail showed the stack at `&A000` pushing an interrupt return at `&9FFE-&9FFF` (as described below);
  the other tail writes in the harness were the BASIC ROM's memory clear (`ldir` at `&C154`) after a key sequence left the game.
  The `LARGEAXX` tail `&1714-&1A3F` was written 952 times by `loadLARGEAXX` (file reload), nothing else.

Conclusion (corrected 2026-11-08): **there is no reclaimable dead code in the `db` runs.** The reliable free space is the 610-byte
tail of `COMMONXX` (minus the few top bytes the stack uses at `&A000`; the ISR's worst-case depth is still unmeasured) plus about 10 bytes
of `unusedGet*`. Fessor's 450 bytes of switched-off blocks could not be placed in stock and stay unverified.

## Dynamic labels (found 2026-11-08, for later reference)

Labels whose bytes change at runtime, or that sit inside an instruction. Static dead-code and free-space claims must not touch them.
Sources: the `equ` aliases at the end of `src/elite/*.asm`, the patch-named labels, and a diff of `&1A40-&9FFF` after 700 random key
presses in cpcxray (`changed_ranges` in `traces/dead_run*.json`; the diff shows only bytes that changed in that run, so rarely used
patches are missing from the "seen" lists).
- **Labels inside instructions** (`equ` aliases, patched or jumped into): `ce2func63` `&25D6`, `ce2func74` `&2688`, `loc_3A88`,
  `loc_5958`, `sub_61B5`, `sub_6953`, `sub_71CB`, `loc_7873`, `loc_86F7` in `commonxx`; `LAB_ram_f638`, `LAB_ram_f6ea` in `common2x`.
- **Self-modified operands seen changing in flight:** circle-drawing masks `ce2func64patchmask7` `&2603`, `ce2func65patchmask8`
  `&2606`, `ce2func75patchmask9` `&26B5`, `ce2func76patchmask10` `&26B8`; viewport inks `patchInk0` `&28E3`, `patchInk1` `&28EC`,
  `patchInk3` `&28F5`, `patchInk2` `&28FE`, `patchSecondInk3` `&2911`, `patchAnotherInk1` `&2953`, `patchAnotherInk1_2` `&2993`;
  line plotters `PatchAND_1` `&33E1`, `PatchAND_2` `&33E8`, `PatchOR_2` `&3469`, `PatchOR_4` `&34AD`; `isPatchStrlen` `&40F2`, `patch1`
  `&4AAA`, `smcIndicatorPatch1` `&6161`; `dvRotatePixmask` `&8018`, `dh2RotatePixmask` `&804B`, `dh1nextPixelline` `&8030` and the
  other `dh*`/`dv*` operands `&801B-&806B`; `LAB_ram_3b07 .. SUB_ram_3b1a` operands `&3B08-&3B1C`; `LAB_ram_3bae` `&3BAF`; `CallHL` `&2AEA`;
  `irds22` `&2CCD`, `irds_dat7/9` `&2DB4/&2DB7`.
- **Self-modified, not seen changing in 700 presses (patch-named, listing only):** `PatchA_1`, `PatchAND_3`, `PatchOR_1`, `PatchOR_3`,
  `dcPatchAdr1..4`, `commandsPatchTable` targets, `patch3`, `charPatchD628/D650/D6D8/D700/D7D8`, `smcIndicatorPatch2`, `md1_patchcommands`,
  `md2_patchcommands`, `dvpatchadr5/7`, `dhpatchadr6`, `patchFWTextfunctions`, `patchmask1..6`, `patchmask11..16`, `patchJr`, `patchJr1`,
  `dfcPatchpos` (`common2x`), `cpatchloop`, `patchViewPortInk0/1`, `patchviewPortInk3`.
- **Self-patched jumps:** `PatchJRZat714b` and `PatchJRat715e` (hyperspace tunnel) choose among `altJrPoint1`, `altJrPoint2`, `altJrPoint3`
  and `LAB_ram_7192`; `PatchORat7159` patches the compare value. So `altJrPoint*` look unreferenced statically but are live.
- **Runtime buffers inside the code image:** entity slots `&1A40-&1B01` (and the zero area to `&1B7A`), `&1C02-&1C39` flight state,
  `tblDustCoordinates` `&34F4-&3544`, `dat_3A6C` `&3A6C-&3A83` (24), `dat_3B3F/3B49/3B61` chart buffers, `qq3`..`travelDistance`
  `&3D22-&3D63`, `dat_5860` `&5860-&589B` (60 bytes; written at runtime, so it is a buffer, not the dead block the TODO suspected),
  `todo_tableforedges`/`tableUnkownFacedata` `&58EA-&592D`, dust tables `&6BED-&6C2D`, `dataShortTunnle` `&721D-&7224`, `dat_7406`
  `&7407-&7496` (about 140 bytes, `loc_745B`), `LAB_ram_7734+10` `&773E-&7749`, sound tables `&2D6C-&2DC9`, `FilenameNOTMUSIC` `&8830`,
  `dataFromPPI`/`keybFlags*` `&8D34-&8D8B`, `irki2_dat2/3` `&8F5C`, private stacks `ce2stack4` `&2727`, `stack5` `&2997-&29FD`, `stack1`
  `&4644`, and the variable block `&38C1-&3949`.
- **Stack in the free tail:** with SP at `&A000` an interrupt pushes at `&9FFE-&9FFF` (seen at the first interrupt after key `4`, PC `&0038`,
  SP `&9FFE`). The top bytes of the `&9D9E-&9FFF` tail are therefore not free; a mission patch must stay clear of at least `&9F00-&9FFF`
  until the depth is measured.
- Method for finding more: assemble `src/elite` into a scratch dir with `--lst`, run `tools/dead_trace.py` (it diffs the code image), map
  each changed range to the nearest label with the `.sym` file.

## The disc-drawing routine and Amtix's "infamous bug" (investigated 2026-11-07)

Amtix 13 (Pinto): the cassette release crashed, intermittently ("hours, or a couple of minutes"), when a planet drifted off the
screen; it was the "disk drawing routine" shared with *Gyron* and Spectrum Elite. Where it is in the stock build:

- Entry `todoDrawFilledCircle` `&E787` / `clearCircle` `&E795` (`common2x.asm`), called from `drawPlanetnSun` and `drawPlanet`.
  Parameters: `circleOffsetY` `&20C7`, `circleOffsetXlo` `&20C8`, flags `circleOffsetXhi` `&20C9` (bit 0 x sign, bit 1 y sign,
  bit 2 x overflow, bit 3 y overflow; set by `calcSunPlanetCoordinates`/`SUB_ram_6aa6`), `drawradius` `&20CA`.
  `dfcPatchpos` `&E7AE` is `ret c`: in flight discs of radius under 9 are skipped; it is a `nop` during launch and docking.
- `CircleEntrypoint2` (`&20FB`) is a case tree on the centre being on or off screen (`ce2func1`..`ce2func33`); the edge cases fill whole
  lines through `ce2func43FillCompleteLinesinBM` (`&243A`): it points SP at a bitmap line (`ld sp,hl`) and runs `push de` 32 times (64
  bytes, one line of the off-screen bitmap `&A000-&BFFF`, 64 bytes per line) per `djnz LineFillLoop`, with SP as the write pointer.
  The partial lines and the interior use the same trick with a private stack at `&F72E` (`CircleParm0x11Mask`) and self-patched
  `jr` into a run of `push af` (`&CE50` onwards).
- **The guard:** at `&245B`, `cp b / jr nc,ce2func44 / ld b,a / inc b` clamps the line count in B to the lines left above the bitmap
  start. Without it the loop keeps pushing below `&A000`.

Test (`tools/circle_sweep.py`, cpcxray, the game in flight so the real ISR at `&2811` and memory layout apply; the stock disk's
snapshot at `&1C82` is the wrong state: there `&0038` still jumps to `&B941`, inside the bitmap):
- Stock build, 131,072 inputs (all 16 flag combinations, x and y in steps of 8, radii 9, 24, 48, 80, 120, 160, 200, 255): every call
  returns with SP restored and writes nothing outside the bitmap except the stack and the circle's own variables and patch bytes.
- Same sweep with the clamp disabled (`&245C` changed to `jr`, `18` instead of `30`), 20,480 inputs: 88 inputs never return or
  return with a wrong SP, 107 write garbage (the fill pattern `F0F0`...) over `&7A9x`, `&81Ex`, `&29E7` and other code and data
  below the bitmap. All of them are flags 12-15 (both coordinates beyond the limit: a big, close planet whose centre is off screen)
  with radius 120 or more, plus the deeper stack use of flags 6 and 7. That is the "planet moved off the screen" crash: the clamp
  is the fix, and the cassette release presumably lacked it (a cassette copy of the first release was not available to check).
- Why intermittent: with SP inside the bitmap, any of the 300 Hz interrupts pushes its return address and the ISR's registers there.
  Harmless inside the picture (a glitch pixel pair), and harmless when SP is at `&A000`, because `COMMONXX` ends in unused zero bytes
  (`&9D9E`-`&9FFF`, 610 bytes in the UK build, 282 in the German) which absorb the push below the buffer; observed: the CPU pushes
  `&2483`/`&2485` at `&9FFE-&9FFF` when an interrupt lands right after the last `push de` of the last line (`ce2func45`). With a
  clamp-less fill the runaway overwrites live code, and what it hits depends on timing: hours or minutes.
- Why Spectrum and *Gyron* did not show it: unconfirmed; on the Spectrum the memory below the screen is ROM (writes are ignored).

What the test does not cover: the unclamped path to the screen (`ce2func46`, used for the charts, `cirGetScrAddr`), radii under 9
(launch and docking, when `dfcPatchpos` is a `nop`), a finer grid at the screen edges, writes at `&C000` and above, and an
independent check on real hardware. The ISR's worst-case stack depth was not measured (one invocation wrote nothing below `&A000`).

## German build (`src/elite_de/`, done 2026-11-07)

`Elite_DE_cracked.dsk` is disassembled into `src/elite_de/` (byte-exact, `bash tools/check_src.sh de`), with names and comments transferred
from `src/elite`. Facts found on the way:
- It is not relocated code. It is the same program with German text: the token tables have other lengths, so the data between the routines
  moves (by 10 bytes in `LARGEAXX`, `&114` or `&148` in `COMMONXX` regions), and addresses in the instructions change with it. The instruction
  stream is the same, apart from a few German-only places (see `src/elite_de/README.md`). `COMMON2X` differs in only 270 bytes (call targets
  and the text routines); `MUSIQUEX`, `INDICATO`, `PICTURE` and `ELITE.BAS` are identical to the English files, `NOTMUSIC` is `COMMONXX` `&6000-&6FFF`.
- Method: `tools/map_german.py` walks the two binaries in lockstep from `&1C82` (same-shape instructions, 8-bit immediates ignored), pairs jump,
  call and data operands, and re-seeds from English code labels by instruction fingerprint; 81% of the English code bytes are paired.
  `tools/disasm_german.py` then runs the stock disassembler (`tools/disasm_stock.py`) on the German files with the paired English names.
- The German `COMMONXX` has the same trailing free area as the English one, only smaller (282 against 610 zero bytes at the end).
- The headers of the German disk's files have load address 0 except `COMMONXX.BIN`; `ELITE.BAS` is the English unprotected loader.

## Title screen ship selection (`-DTITLESEL`, 2026-11-08)

Cursor and joystick left/right step the demo ship on both title screens. The code is in the zero tail of `MUSIQUEX.BIN` (`&6E21-&6FFF`, about 120 bytes used; the file is resident only while the title screens run, and a failed load is retried by `loadFile` so the hooks cannot meet `NOTMUSIC`). A jump table at `&6E21` (`TITLE_SCREEN1`, `TITLE_SCREEN2`, `TITLE_NEXT`, `TITLE_SHOW`) is called from four places in `COMMONXX` that keep their byte length. `splash2Shipnr` (`&1DA8`) holds the ship index in bits 0-2 and "a direction key was already down" in bit 7; the eight hulls are in `titleShips` (spawn actions, high nibble = ship type - 2). The raw PPI rows (`dataFromPPI`) are read because `irki2` rewrites `keybFlags2` into roll values. The six `COMMONXX` addresses `musiquex.asm` hard-codes are checked by `tools/check_src.sh` (plain and `-DMISSIONS`); test `tools/test_title_ships.py`. The automatic pick on the press-space screen now follows this list instead of the stock order. English only.

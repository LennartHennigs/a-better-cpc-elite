# Open items, full text

The one-line items in `TODO.md` link here. Moved unchanged; edit both when the status changes.

## Ship packs

Ship packs (`docs/_ship_packs.md`): play through a few jumps and launches (pack mix, 2 s load after a jump, asteroid crowding with `-DTRAFFIC`); try hiding the pack load (load at the end of `DockingSequence`, or chunked during the launch tunnel); Boulder and Transporter do not fit yet; check the new hulls' role flags and kill values against the C64 table.

## Added missions, English only

Added missions (Constrictor, plans, stolen ship, asteroids, Trumbles) are English only: no translated texts, and the mission disk and hooks are built only from `src/elite` (`build_dsk.py --missions` refuses `--de`/`--fr`). The biggest gap between the builds. Suggested: port the texts to German first, then French (same free-space limit as the flight images; the overlays carry the text).

## Write-protected save

Save on a write-protected disk resets to BASIC (seen in RVM on the mission disk). The game's own hook only catches AMSDOS's "Retry, Ignore or Cancel?" message (`LAB_ram_855e`, `checkMedia`); whether the stock game behaves the same, and what a graceful handler would cost in bytes, is untested (needs a clean boot in cpcxray on a read-only disk; `firebird_at_entry.sna` is not valid for disk-menu tests). Suggested: catch the AMSDOS error in `checkMedia` and return to the menu; measure the byte cost in the flight image first.

## Legal status number

(deferred 2026-11-16: no room in the mission build, left for now) Legal status number on the status line ("Status: Offender - 25"): a shared printing routine plus two small entries, about 14 bytes more in the head of every flight image; the images have 0 to 2 bytes left (2026-11-15), so it fits only without `-DMISSIONS` (about 450 bytes free in the tail) or after dropping the Trumble squeak (17 bytes, Trumbles only) and more in the packs. Also open: the kill count and the status number in German and French (spacing, width of the longer labels).

## Laser sights on the mission disk

Laser sights on the English mission disk: `-DENHANCED -DMISSIONS` keeps the stock cross because the sights (108 bytes) do not fit beside the flight images (about 13 bytes short after the cuts that keep the missions as they are; measured launch-table cut: 2 bytes per image; see `docs/_my_changes.md` "Laser sights"). Needs space in the `COMMONXX` tail (images T 608, packs 1/2 606/604, C 606 of 608 since the kill count) or a hull less in packs 1 and 2. The French sights are untested in an emulator (the German ones were played by hand). Suggested: move the sights into an overlay, or drop a hull from packs 1 and 2 to make the 108 bytes.

## Real playthrough

Real playthrough of the whole chain with save and load (so far only forced states, direct calls, the trainer pokes and a booted disk). A real docking triggering each offer has not been seen in the running game. Suggested: script it with cpcxray from `firebird_in_flight.sna`, forcing each offer by docking, saving a snapshot at each step.

## Furs when the Trumbles die in a sun

Optional: furs when the Trumbles die in a sun. Idea: when the sun brings the count to 0, add a fixed 4 t of furs (good 11, `cargoHold+11`), capped by `cargoSpaceFree`. Costs about 24 bytes in `mxSunImpl` (Trumbles image has 8 spare, limit `&9FFE`), so 16 bytes must be freed: cutting the sprite from 14 to 10 rows does it (drop rows 0, 6, 12, 13 of `missions_trumble_art.txt`, `ld c,10` in `mxBlit`). Once per commander (the offer is made once), so no trading exploit. A scaled amount (peak count) needs a stored byte and more space. Also a death sound for the sun: reuse an existing effect via a bit in `sfxFlags2Bitmap` (about 5 bytes), pick by ear with `TRUMBLE.BAS`.

## Hull dedup

Hull dedup behind `-DENHANCED`/`-DMISSIONS` (default keeps the original bytes): point the Splinter header's edge offset (`shipdatSplinter` +14) at `shipdatCapsule`'s edge block and drop the duplicate 24 bytes; move the later hulls down so the free tail grows by the same amount. Check the Splinter and Capsule faces and all other sub-blocks for partial overlaps first (only whole equal blocks were compared; Cargo/Pirate1/Thargon differ). Risks as in the hull compression item: shifted tail addresses, `check_src.sh` marker, all three trees, `tools/tests/test_flight_hull.py` per ship.

## Spawn variance in the 64K build

**Built 2026-11-21 for the English `-DMISSIONS` builds (hostiles only; see `docs/_ship_spawning.md`); the plan below is kept for the German and French builds and for what differs.** Plan, 2026-11-21. The 128K build has `SPAWN_VARIANCE` (commit `ff0a988`, `spawnVariance` in `src/elite128/lasersights128.asm`, 59 bytes, `docs/_ship_spawning.md`): a hostile (bit 2 of the ship's byte `+33`) starts at x_hi, y_hi random 0 to 63, z_hi 32 to 63, random z sign, and a ship behind the player inside the rear cone is put in front (front 270 degrees). Port it to `src/elite` behind `-DSPAWN_VARIANCE` (default build keeps the original bytes; `check_src.sh` en, de, fr).

**Why it does not fit today.** With `-DMISSIONS` the routine has to be in every flight image, about 62 bytes each (59 + the call). Images against the 608-byte limit: default 182, packs 3 to 7 448 to 508, mission images P, S, R 284, 379, 303 (all fit); pack 1 606, pack 2 604, Constrictor 606, Trumbles 608 (do not). The main binary has no spare bytes either. Dropping a whole pack frees nothing for the others: each image is separate.

**Decisions (2026-11-21).**
- Packs 1 and 2 lose one hull each: drop the **Cobra Mk I** and the **Worm**, keep the Gecko (replaces the Sidewinder) and the Moray (replaces the Krait). Images become about 405 and 425 bytes (467 and 487 with the routine). Both packs then use the single-type test of packs 3 and 4 (`cp 16 / ret nz`, `cp 17 / ret nz`) and the `ASSERT` on adjacent records goes. All seven packs stay in the picker; the 64K build has 7 of the 9 pack hulls, the 128K build keeps all 9 (so README, `_ship_packs.md`, `_my_changes.md` counts differ between the two).
- The Constrictor and Trumbles images do not carry the routine: a `ret` at its entry, so spawns during those two missions keep the stock corner start. The Trumbles image has 0 to 1 spare bytes: find the byte (or use an 11th vector in the table) before relying on it.
- The pack hulls are no catch: the role bytes ANDed with `&6F` have bit 2 set for Gecko, Cobra Mk I, Worm, Moray, Mamba and Adder (the Sidewinder and Krait stand-ins, so they get the variance) and clear for Boa, Anaconda, Shuttle and Boulder (traders and rocks, left alone). Checked statically in `src/elite/missions_ships.asm` and in the 128K flight images. `docs/_ship_spawning.md` line 29 says the opposite for the pack hulls: fix it.

**Steps.**
1. Cut packs 1 and 2 in `missions_flight_k.asm` (`FL_1`: Gecko only, `FL_2`: Moray only), `tools/fessor_ships.py` and the build lists, the 64K ship viewer data if it lists the two hulls, `tools/tests/test_ship_packs.py` (packs 1 and 2 expectations). Build; read the real image sizes (`mxFlightEnd`, `ASSERT <= &9FFE`). `check_src.sh` en, de, fr.
2. The 3-byte `call` at the end of `spawnShip` (`src/elite/commonxx.asm`, before `xor a / ret`; the routine must not leave A changed: the 128K call sits before `xor a`). The main binary has no spare bytes: the 18-byte pirate block (`jr nz,spwnIsNoPirate` to the two `and 7` stores) may be merged or shortened to make 3. If not, a `jp` in place of `xor a / ret` costs 2.
3. The routine (port of `spawnVariance`, `getRandomNumber` instead of `GETRND`, no bank handling) at a fixed entry label at the start of the flight tail in the default and pack images, so the call in `spawnShip` needs no vector; the opt-out images put a `ret` there. Non-missions builds (`make original`, enhanced, de, fr): the routine goes into the free tail of `COMMONXX` (610 bytes, 128 for the laser sights, about 480 left; check each locale).
4. Tests: sample `spawnShip` 80 times per hostile type (Sidewinder, Krait, a pack hull, a Python pirate) as in the 128K check (ranges, none in the rear cone, 12 to 25 of 80 behind); types 8, 15, 18, traders, asteroids unchanged; the Constrictor and Trumbles images spawn as stock; `test_ship_packs.py`, `test_launch.py`, `make test`, `make test-emu`. Play test: does a ship from the side or behind feel right?
5. Docs: `_ship_spawning.md` (64K section, fix line 29), `_ship_packs.md` (table, hull count, limits), `_missions_built.md` (image sizes), `_my_changes.md` (new switch and slot), `README.md` (counts only, no mission names), `src/disk/README.TXT` (one short line), `CHANGELOG.md`, `NOTICE`/credits unchanged. Note the port in `TODO_128K.md` ("the same switch in the 64K build").

**Not in this item:** asteroids and traders. Packs staying together (`spawnEscortPack`) was added on 2026-11-22 inside `mxSpawnVar` (the stack-peek design, 63 bytes; not the bank 6 module of the 128K build): `docs/_ship_spawning.md` "The 64K build". Image sizes with it: default 309, packs 1 and 2 525 and 545, pack 5 575, pack 6 587 (room 21), P 414, S 506, R 430; packs 3, 4 and 7 (568 to 572) skip it (`NO_PACKCOH`).

## Remaining dat labels

The remaining 7 `dat_` labels in `src/elite/` (counted with `grep -c "^dat_"`), checked 2026-11-09 (23 before this pass). Done: 16 address/message-id immediates
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

## Particle explosions

Particle explosions (`-DPARTICLE_EXPLOSION`, compile switch, off = today's behaviour; plan only) and **the 11 original BBC ships** as optional flags. Today (`todoDrawExplosions`, `common2x.asm`): a sound and 15 expanding rings (`drawradius` + 2 per ring, `SUB_ram_e74c`) at the screen position cached for the exploding slot (`cache_explosion_screen_pos`, flag bits 4 and 5), `sfxFlags2Bitmap` bit 6 for the sound. The C64 and BBC (`DOEXP`/`PTCLS` in `work/ext_c64`, `ext_bbc`): at each of the first n projected vertices (n from the blueprint's explosion-count byte) a cloud of 1 to 8 particles, offsets = random x cloud size, size = 8 x counter / distance, the counter starting at 18 and rising by 4 per frame; the random numbers come from four seed bytes kept per ship, XORed with the vertex index, so the cloud is the same every frame; points are clipped and plotted with a size from the distance; the C64 adds a sprite flash on the first frame. How it fits here:
  - Keep the sound and the ring flash as the first frame; the particles take over after it. No erase pass (the off-screen bitmap is wiped every frame; the per-ship seed keeps the cloud coherent).
  - Code in a bank 6 module, not in the glue: replace the ring code in bank 7 by a far-call stub (the `hullDraw` pattern: resident stack, config C6, call, `mapMain`, stack back), the particle code (150-250 bytes) in bank 6 with its own pixel plot (bank 7 is hidden in C6), a new stage chunk in the blank bytes of `COMMON2X` (check blankness in `build_dsk128.py`) and a vector next to `fillHullEntry`; per-slot state (cloud counter, 4 seed bytes, 8 slots) in a bank 6 table, reset when a slot starts to explode.
  - Phase 1: one cloud at the cached screen centre, radius from the counter and the distance. Phase 2: clouds at the vertices (`hullVertexBuf` already holds the projected ones for the fill), n capped at about 12; check that the explosion-count byte of the CPC blueprint is where the 6502 header has it.
  - The counter step must be larger than the 6502's 4 (the CPC draws 5 to 6 frames per second), or an explosion would last 10 seconds. Cost: up to about 28 x 8 = 220 dots a frame, roughly 10 ms; clip to the 256 x 128 viewport and skip vertices behind the viewer.
  - Checks: screenshots at several distances and counter values, frame time with several exploding ships, the special explosions (Constrictor, station, escape pod), the pens used by the flight view.

## Clipping v2

Plan and estimate, 2026-11-21. Trigger: a thin stray triangle when flying close to the station (RVM state `Untitled.rvmstate`, screenshots 21:08; `TODO_128K.md`).

**What goes wrong.** `getVertex` (`fill.asm`) turns the engine's projected vertex (x magnitude, y magnitude, flag) into absolute 8-bit coordinates and CLAMPS it into the viewport (`VIEW_X0..X1`, `VIEW_Y0..Y1`). A vertex that is outside the view but not flagged off (`bit 7`) therefore moves to the border, which bends the edges of every triangle that touches it (the sliver) and also feeds wrong coordinates to `cull`, so a face can be culled or kept wrongly. In the saved state vertices 0, 2, 5, 7 of the Coriolis were at y = 147, -10, 168, -25 (view 0..127). Vertices flagged off view (`bit 7`: the engine's own limit, magnitude over 255 or behind the viewer) still drop their triangle; the engine keeps no 16-bit projection, so those cannot be recovered (a hull right in front of the slot will still lose triangles; the plan fixes the "a few pixels outside" range, which is what the screenshots show).

**Design.** Keep the fast path as it is (all three vertices inside the view: `getVertex` -> `cull` -> `fillTri` with 8-bit coordinates). Add a slow path for triangles with a vertex outside the view:
1. `getVertexWide`: the same vertex as signed 16-bit x, y (x = 127 -/+ xmag, y = 63 +/- ymag; range -128..382 and -192..318) into a small buffer; a flag `V_CLIPF` says that a vertex is outside (set where `getVertex` now clamps).
2. Trivial reject: all three vertices beyond the same side of the view -> drop (cheap, and the common case for the big side faces).
3. `cullWide`: the sign of the cross product with 9-bit signed differences (one shift-and-add 9 x 9 multiply, used twice), instead of the clamped 8-bit `cull`.
4. Sutherland-Hodgman against the four view sides on the 16-bit triangle (a polygon of at most 7 vertices; one generic pass routine run four times, intersection = interpolation by a 9-bit multiply and an 18 / 9-bit divide, shared with `cullWide`).
5. Fan-triangulate the clipped polygon (all vertices are inside the view now) and call `fillTri` for each triangle with the same pattern.

**Where it lives (no resident bytes).** A new block `fillclip.asm` at `&4840` in bank 6 (free: `&4834-&4EFF`, 1,740 B; `docs/_memory_map_128k.md`), assembled separately with the fill symbols (`fillTri`, `V_*`, `VIEW_*`, `PATS`) like `spawnmod.asm`. The fill region has 5 spare bytes (`fillEnd` `&43CB`, limit `&43D0`), so `getVertex` and `cull` (about 100 bytes) move into the new block, which frees that room for the dispatch in `fhLoop` (a flag test after the third vertex and a `jp` to the slow path). The boot copy costs nothing: stage the block directly behind the spawn module (`STAGE+0x3240`, if the 960 bytes there are blank pixel bytes: check with the blank-block assertion in `build_dsk128.py`) and raise the immediate `ld bc,0x0240` of the existing module `ldir` in `bankInit` (no new instruction); if that area is not blank, restage both at `STAGE+0x3800` (`ld hl` immediate changes, still no new bytes). Variables (two 7-vertex 16-bit buffers, about 60 bytes) go into the new block or the free end of the `&4F00` page.

**Size.** About 320 to 380 bytes of code (wide vertex 30, `cullWide` 70, multiply and divide 60, clip passes 100 to 130, fan and dispatch 40, glue 20) plus 60 bytes of variables: fits the 1,740 free bytes with room. `ASSERT`s: block end `<= &4EFF`, `bankInit` copy length equals the staged length, fill code `<= &43D0`.

**Speed.** Only triangles with an outside vertex take the slow path. A clip is about 15 to 25 thousand T-states (4 to 7 ms) per triangle, so a station filling the view (10 to 20 such triangles) adds roughly 50 to 120 ms to those frames, on top of the fill itself (a close hull already costs about 250 ms); the trivial reject removes the faces that are entirely outside. Frames with no clipped triangle are unchanged (one flag test per triangle, about 1 us).

**Tests.** (a) Load the saved state in cpcxray (`tools/rvmstate.py --sna ... --curcfg`): the sliver must be gone and the face edges straight. (b) `test_hulls128.py` with `POS=0,0,z` for the station and a few big hulls at 4 to 5 distances plus a roll (set `ix+9..` orientation words), screenshots before and after. (c) A Python reference: take `VBUF` and the triangle records from a snapshot, clip and rasterise in Python, compare with the game bitmap at `&A000` (the prototype in `tools/proto_fill/` has the fill) and require over 99% of the pixels equal. (d) Frame time with `test_frametime.py --ship 0,2` before and after (fast path unchanged, slow path as estimated). (e) `run_all.py --emu128`, `test_flip128.py`, the title ship viewer (it draws every hull at a set distance: no change expected).

**Effort.** About 3 to 4 hours of work in four steps: (1) move `getVertex` and `cull` into the new block, the staging and the `bankInit` immediate, byte-identical output on the fast path (45 min); (2) `getVertexWide`, trivial reject, `cullWide` (60 min); (3) the clip passes, fan and fill, first against the saved state (75 to 90 min); (4) tests, timing, docs (45 min). Risks: 16-bit arithmetic slips (the reference rasteriser in test (c) is the safety net), the unverified blankness of `STAGE+0x3240`, and the remaining holes for engine-flagged vertices (documented limit).

**Not covered.** Vertices flagged off view by the engine (magnitude over 255 or behind the viewer) still drop their triangle. Fixing that needs the engine to keep 16-bit projected coordinates (the 6502 original does; this port stores 8-bit magnitudes in `buf_5860`) or a clip against the near plane in 3D before projection: a separate, much larger change in code that has no free bytes.

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

**Not in this item:** asteroids and traders, packs staying together (`spawnEscortPack`): they wait for the 128K work (`TODO_128K.md`).

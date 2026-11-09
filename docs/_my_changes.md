# What we changed in the game

Every difference between our builds and the original game, with why it exists, where it lives, what it costs and how it is proven. Without any switch only the CPC+ byte differs from the original
(`_build.md`); everything else is behind a `-D` flag. Source-only work (names, comments, `smc_`/`buf_` prefixes, `dw` tables) changes no byte and is not listed. The dated history is in `CHANGELOG.md`.

## At a glance

| Change | Switch | Languages | Stock bytes touched | Extra space used |
|---|---|---|---|---|
| CPC+ keyboard fix | none (always on) | English, French (German disk already has it) | 1 (`ED 79` -> `ED 49` in `getPPI_Input`) | 0 |
| Escape leaves buy, sell and equipment prompts | `ESC_KEYCODE` / `ENHANCED` | all three | 1 (`FF` -> `7F` in `tblKeyboardmatrix`) | 0 |
| Stars stay behind planet and sun | `STAR_OCCLUDE` / `ENHANCED` | all three | 16 bytes of the dust loop | 11 bytes in dead `unusedViewBorderFill` |
| Cash on the quantity line of buy, sell and equip | `ENHANCED` | English | two 3-byte call operands (`clrLine0x15` -> `clrLineCash`) | 16 dead bytes in `LARGEAXX` (`&08E7`) and 7 in the dead block of `COMMONXX` (`cashHome`, `&1FEA`) |
| Title screen ship choice | `TITLESEL` | English, German | four call operands in `COMMONXX` (same length) | about 120 bytes in the tail of `MUSIQUEX` |
| Added missions | `MISSIONS` (+ `FL_*`, `OVL_*`) | English | about a dozen 3-byte call replacements (hook sites) | both zero tails, plus overlay and image files on disk |
| Trainer and save tools | none (BASIC programs, host scripts) | UK, French, German saves | none | none |

## CPC+ keyboard fix

The keyboard scan `getPPI_Input` writes the PSG select value twice; the second `out (c),a` becomes `out (c),c`, which releases the PSG before the PPI's port A turns to input. That is the port order a CPC464+/6128+ ASIC tolerates.
One byte, length unchanged. Found by diffing Redbox's patched disk; the mechanism is inferred, and it is untested on real Plus hardware and in Caprice32 (which does not reproduce the bug). Full story: `_cpcplus.md`.
`check_src.sh` expects the patched byte, so "stock" in this project means the original plus this byte.

## Escape in the prompts (`ESC_KEYCODE`)

In the original, ESC maps to `&FF` ("no key") in the ASCII keyboard table (`tblKeyboardmatrix`, row 8 bit 2), so the prompts never see it. We return `&7F`. `getInputForFunctionHL` already treats any code of `&3A` or more as
"leave" (that is why any letter leaves too), so Escape backs out of buy, sell (to the inventory) and equipment (to the status screen) with no new code. Side effects, all harmless: `InputString` ignores codes above `&5A`, so names are unaffected;
pause mode compares specific letters; on the title screen ESC now counts as "any key" (starts a new commander; the "press space" loop still needs space). Runtime address of the byte: English `&8C98`, German `&8DE0`, French `&8E37`.
Tested live in cpcxray at Lave (key 2, Esc). The built disk was not booted for this.

## Stars behind planet and sun (`STAR_OCCLUDE`)

The dust loop (`dust70`) plots each star with `AND NOT mask` over whatever is in the off-screen bitmap, and the dust is drawn after the planet and sun discs, so stars shone through them. It now calls `dustPlotPixel`, which plots only while the
pixel is still background (`(byte XOR &0F) AND mask` is zero, the background being `&0F`): disc, tunnel and ship-edge pixels are left alone. The 11 bytes of code sit in the dead block `unusedViewBorderFill` (`&1FD2-&1FF0`, padded up to
`ClearBitmap`), the dust loop keeps its length, and nothing moves. Ships stay see-through wireframes (as on the BBC); the options for hiding stars behind hulls are in `_ship_occlusion.md`. Proof: `check_src.sh` requires
the default build to equal the original and the `-DENHANCED` build to differ only inside those two slots (plus the ESC byte). Test: `tools/test_star_occlusion.py [off] [far] [sun]` writes screenshots to `work/xray/output/stars_*.png`.

## Title screen ship choice (`TITLESEL`)

Cursor left/right and joystick left/right step the demo ship on both title screens (Y/N and press-space) through eight hulls: Viper, Asp, Cobra Mk III, Fer-de-Lance, Sidewinder, Krait, Rock Hermit, Thargoid (the Python, big trader and Coriolis do
not fit the window). The code, about 120 bytes with its table, lives in the zero tail of `MUSIQUEX.BIN` (`&6E21-&6FFF`), which is resident only while the title screens run. `COMMONXX` reaches it through four hooks of unchanged byte length:
`TITLE_SHOW` replaces the fixed Cobra spawn, `TITLE_SCREEN1` and `TITLE_SCREEN2` replace the `setCommandsNOP` / `transferBuffertoScreen` calls in the two loops, `TITLE_NEXT` replaces the automatic pick before the press-space screen. `splash2Shipnr` (`&1DA8`) holds
the ship index (bits 0-2) and "a key was already down" (bit 7), so a held key steps once and the choice carries over between screens and restarts. The raw PPI rows (`dataFromPPI`) are read because `irki2` rewrites `keybFlags2` into roll values.
The six `COMMONXX` addresses `musiquex.asm` hard-codes are checked by `check_src.sh`. Test: `tools/test_title_ships.py [de]`.

## The added missions (`MISSIONS`)

Five missions on top of the three stock ones: Constrictor, Thargoid plans, Trumbles, and the two Elite Plus missions (stolen police ship, asteroid bombardment). How they work, their order and triggers: `_missions_built.md`; the research: `_missions.md`.
What they change in the stock game:

- **Credit:** the Constrictor hull (`src/elite/missions_hull.asm`) is by Fessor, used with his permission (post: <https://www.cpcwiki.eu/forum/programming/expanding-elite/msg205425/#msg205425>).
- **Hook sites** (each a 3-byte `call` replacement, so no stock routine moves): `spawnShip` (`mxShipTable`, ship type 19), `spawnCommand0` (`mxSpawnCheck`), `todo_killedsomeone` (`mxKillHook`, replaces `call getBounty`),
  `applyLaserDamagetoEntity` (`mxLaserHook`), `RechargeEnergy` (`mxRecharge`), the docking sequence (`&1714` replaces `chkMissions`), `launchSequence` (`mxLaunchEntry`), `setShipvarsAtArrival` (`mxArrive`), `todoOverheating` (`mxSun`),
  the Inventory loop (`mxInvHook`), the `call transferBuffertoScreen` in `Spaceflight` at `&1E4D` (`mxFlightDraw`, the Trumble sprites) and the escape-pod launch (`mxPodHook`).
- **Unused save bytes** carry the state (`&38FD`, `&38FE`, `&3905-&3906`), so the save layout and the code-keyed encryption are unchanged and old saves still load.
- **Free space:** the 812-byte tail of `LARGEAXX` and the 610-byte tail of `COMMONXX` (`_memory_map.md`); the missions load their code from overlay and image files, one at a time.
- **Behaviour you can notice outside the missions:** an escape pod now ends the Trumbles quest (the original leaves 1-7 aboard); a docking costs nothing extra unless a mission can act (an overlay load is about 2 s of disk time); a launch swaps the
  flight image only when it differs (about 2 s more).
- Disk files: `MISSIONC/P/T/R.BIN` (overlays), `MFLIGHT0/C/P/T/S/R.BIN` (flight images), `README.TXT`; all but the `.BAS`/`.TXT` files are hidden.

## Trainer, save tools and disks

- `CHEAT.BAS` (ours, replaces the Firebird disk's): interactive trainer with prompts for each of the original pokes plus no pirate boarding, unlimited hold, own cloak, cash, stock mission stage, kills, jumps and added-mission presets;
  `SHOWSAVE.BAS` / `EDITSAVE.BAS` show and edit a commander save on the CPC; `tools/saveedit.py` does the same on the host and converts saves between UK, French and German builds. `_cheats.md`, `_savegame.md`.
- The original `CHEAT.BAS` has a wrong cloak entry (it only lists the device; `POKE &202B,0` makes the cloak work); ours sets the ownership bit instead.
- Built disks show only `.BAS` and `.TXT` files in `CAT`, like the original protected disk; `RUN`, `LOAD` and the game's own loads still find the hidden files.

## Stock bugs we found and did not fix

| Bug | Where | Status |
|---|---|---|
| Escape-pod cargo clear starts at `&38E1` (the market random byte) and keeps alien items (`&38F2`); `cargoSpaceFree` is reset to full capacity | `mleCleanInvLoop`; fix: start the loop at `&38E2` | not applied; no reward depends on it (`_missions.md` section 3) |
| The random witchspace mis-jump looks unreachable (the seed byte is compared with `0x40` then `0x20`) | `someHyperSpaceFunctions`; only the pause-menu toggle (bit 6 of `keybFlags0`) forces it | not applied (`_gameplay.md`) |
| The station-kill code does `SET 3,(HL)` on `&3926` instead of `Missionflag` | invasion mission | left as is |
| Large planets off screen can overwrite memory below the bitmap if the line-count clamp at `&245B` is missing | disc fill | stock build is safe (131,072-input sweep); the cassette release presumably lacked the clamp (`_architecture.md`) |

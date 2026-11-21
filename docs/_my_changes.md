# What we changed in the game

This file covers the 64K builds. The differences of the 128K build (`src/elite128`, branch `elite128`) are in `_128k_version.md` and `src/elite128/README.md`.

Every difference between our builds and the original game, with why it exists, where it lives, what it costs and how it is proven. Without any switch only the CPC+ byte differs from the original
(`_build.md`); everything else is behind a `-D` flag. Source-only work (names, comments, `smc_`/`buf_` prefixes, `dw` tables) changes no byte and is not listed. The dated history is in `CHANGELOG.md` (up to 2026-11-11: `changelog_archive.md`).

## At a glance

| Change | Switch | Languages | Stock bytes touched | Extra space used |
|---|---|---|---|---|
| CPC+ keyboard fix | none (always on) | English, French (German disk already has it) | 1 (`ED 79` -> `ED 49` in `getPPI_Input`) | 0 |
| Escape leaves buy, sell and equipment prompts | `ESC_KEYCODE` / `ENHANCED` | all three | 1 (`FF` -> `7F` in `tblKeyboardmatrix`) | 0 |
| Stars stay behind planet and sun | `STAR_OCCLUDE` / `ENHANCED` | all three | 16 bytes of the dust loop | 11 bytes in dead `unusedViewBorderFill` |
| Station-screen headlines in column 2 | `ENHANCED` | all three | 4 operand bytes, no new code | 0 |
| Key pre-delay 0.43 s -> 0.16 s (`sub_403E`, 1 operand byte) | `ENHANCED` | all | 1 byte, no new code | 0 |
| Status screen: short labels, values and fuel number in column 9 | `ENHANCED` | English, German (new labels), French (all but the "Statut Legal" label) | the label strings in both string tables (same length), 4 bytes in `COMMON2X`, two bytes in `COMMONXX` | 0 |
| Cash on the quantity line of buy, sell and equip | `ENHANCED` | all three | two 3-byte call operands (`clrLine0x15` -> `clrLineCash`) | 16 dead bytes in `LARGEAXX` (`&08E7`) and 7 in the dead block of `COMMONXX` (`cashHome`, `&1FEA`) |
| Kill count after the rank on the status page ("Harmless - 12") | `ENHANCED` | English (also with `MISSIONS`) | the 2-byte operand of the `call anotherPrintwithTokeninA` after `getRank` (`killHookSite`) | 26 bytes: in the shared head of every flight image with `MISSIONS`, in the zero tail without; plus a 10-byte helper in the dead bytes at `&204E` |
| A sight per laser type (pulse cross, beam, military, mining), none without a laser | `ENHANCED` (not with `MISSIONS`) | all three; English only without `-DMISSIONS` | the first instruction of `LaserSights` (3 bytes, `jp`) | 108 of the 128 first bytes of the zero tail of `COMMONXX` (`laserSightsBlock`) |
| Title screen ship choice, ship name on the press-space screen | `TITLESEL` | English, German, French (ship names are English in all three) | three call operands (two in German and French) plus one `call printELITE` in `COMMONXX` (same length) | about 280 bytes in the tail of `MUSIQUEX` |
| A sells the whole hold in the sell menu | `ENHANCED` | English | the 3-byte operand of the `jp Inventory` at the end of the sell menu (`sellAllOperand`) | 48 bytes in the `LARGEAXX` tail (`sell_all.asm`; in the missions build inside the resident stub) |
| Ten more ships in flight (ship packs) | `MISSIONS` (`FL_1`-`FL_7`) | English | none beyond the missions' hooks (`mxShipTable`, `mxLaunchEntry`) | seven flight images on disk; 9 bytes more in every image for the picker |
| C64-like traffic | `TRAFFIC` | all three | 5 bytes (two roll operands, the 3-byte escort pack size) | 0 |
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

Second digit (`-DENHANCED`, all three trees, 2026-11-16): the stock jump for "leave" after the first digit of a quantity skipped `restore_trade_state`, so Esc (or a letter) left that digit's trade applied while the caller took it as cancelled. The `jr nc` at that point now targets the DEL path (`LAB_ram_08f7`), which undoes the trade and re-prompts; a second Esc then leaves. Same instruction size, so nothing moves and the save key at `EquipShip` is untouched (marker `escQtyOperand`, allowed in `check_src.sh`). Checked by assembling only; not played.

## Stars behind planet and sun (`STAR_OCCLUDE`)

The dust loop (`dust70`) plots each star with `AND NOT mask` over whatever is in the off-screen bitmap, and the dust is drawn after the planet and sun discs, so stars shone through them. It now calls `dustPlotPixel`, which plots only while the
pixel is still background (`(byte XOR &0F) AND mask` is zero, the background being `&0F`): disc, tunnel and ship-edge pixels are left alone. The 11 bytes of code sit in the dead block `unusedViewBorderFill` (`&1FD2-&1FF0`, padded up to
`ClearBitmap`), the dust loop keeps its length, and nothing moves. Ships stay see-through wireframes (as on the BBC); the options for hiding stars behind hulls are in `_ship_occlusion.md`. Proof: `check_src.sh` requires
the default build to equal the original and the `-DENHANCED` build to differ only inside those two slots (plus the ESC byte). Test: `tools/tests/test_star_occlusion.py [off] [far] [sun]` writes screenshots to `work/xray/output/stars_*.png`.

## Title screen ship choice (`TITLESEL`)

Cursor left/right and joystick left/right step the demo ship on the press-space screen (the first screen keeps the fixed Cobra Mk III and ignores the arrows) through eight hulls: Viper, Asp, Cobra Mk III, Fer-de-Lance, Sidewinder, Krait, Rock Hermit, Thargoid (the Python, big trader and Coriolis do
not fit the window). The code, about 120 bytes with its table, lives in the zero tail of `MUSIQUEX.BIN` (`&6E21-&6FFF`), which is resident only while the title screens run. `COMMONXX` reaches it through hooks of unchanged byte length:
`TITLE_SCREEN2` replaces the `transferBuffertoScreen` call in the press-space loop, `TITLE_NEXT` replaces the automatic pick before that screen (it now selects the Cobra Mk III) (English also `TITLE_NAME`, below). `splash2Shipnr` (`&1DA8`) holds
the ship index (bits 0-2) and "a key was already down" (bit 7), so a held key steps once and the choice carries over between screens and restarts. The raw PPI rows (`dataFromPPI`) are read because `irki2` rewrites `keybFlags2` into roll values.
The eleven `COMMONXX` addresses `musiquex.asm` hard-codes are checked by `check_src.sh`. Test: `tools/tests/test_title_ships.py [de]`.

**Ship name.** A fifth hook, `TITLE_NAME` (`&6E27`), replaces `call printELITE` in `printPressSpace`: `titleName` prints the name of the ship on show (table `titleNames`, 16 bytes per name, in `titleShips` order) centred on text row 1 in capitals (`todoPrintFlag3948` forced to 1 while printing). It then recolours that row of the off-screen bitmap from pen 0 to pen 3, the pen of the ship lines and frame: the background byte is `&0F`, text pixels have both planes clear, so `byte := &0F | (~byte & &0F) << 4`.

## Cash on the quantity line (`ENHANCED`)

The buy, sell and equipment prompts show the balance at the right end of text row `&16`, the row below the prompt where the typed quantity appears (8 characters ending at column 30, one decimal, space-padded by `printDeciCredit`). `clrLineCash` replaces `clrLine0x15` at two sites (`printInputQuestionforQuantity`, used by buy and sell, and `eqShoppingloop`): it clears the two rows, prints `getMoneyinHLDE` at `(22, &16)` and jumps to `cashHome`, which puts `charXY` back on `&1500` so the prompt prints as before. Because the prompt runs before every row, the balance is fresh after each purchase.
`clrLineCash` sits in 16 dead bytes of `LARGEAXX` (`&08E7`, a ZX Spectrum attribute fill nothing calls), `cashHome` (7 bytes, `&1FEA`) at the end of the star-occlusion dead block in `COMMONXX`; `largeaxx.asm` calls it by address and `commonxx.asm` asserts it. `check_src.sh` requires the default `LARGEAXX` to equal the original and the `-DENHANCED` one to differ only in that slot and the two call operands. 

## Kill count on the status page (`ENHANCED`)

The status page printed the rank only. `killcount.asm` (English) prints the rank, " - " and the number of kills, the whole-kill word at `killScore+1` (the low byte of the 24-bit score is a fraction): `call printString` for the rank (no new line), three `printStringFollowingByte` characters, `todo_SomethingwithDigits`, then `jp CurHomeinFrame` for the two new lines `anotherPrintwithTokeninA` gave the rank. 26 bytes, resident in flight and docked, plus `killSpace` (10 bytes) in the 10 dead bytes of `unusedGetFlightMode` and `unusedGetCloakFlag`: it prints the one space before the dash unless the rank string already ends in one. With `-DMISSIONS` it sits in the shared head of every flight image right after the file name (`killCountHook`, asserted at `&9E1A`: every image must have it at the same address); without, after the laser sights block in the zero tail. Tested in cpcxray at 0 to 3000 kills (every rank) and by hand in RVM (commander LEN: "Rating: Poor  - 31"). The ranks Poor, Average and Above Average (tokens `&17`-`&19`) end in a space in the stock text (the same tokens give "Poor Agricultural" on the system-data screen, so the strings cannot be shortened); `killSpace` skips the extra space for them, so every rank reads "Name - kills".

The room for it in the mission build came from cuts that keep every mission as it was (`CHANGELOG.md`): direct vectors for hooks an image does not use, the 12 x 12 Trumble sprite, one type-range test in packs 1 and 2 and no `push bc` in the packs, one state test in the Constrictor image, and a (mask, value, image) table in `mxLaunchEntry`. German and French do not have it yet.

## Laser sights (`ENHANCED`)

The stock game draws one cross for every laser; the C64, Atari ST and Amiga draw a different sight per laser. `lasersights.asm` (the same file in `src/elite`, `src/elite_de` and `src/elite_fr`) draws one per laser type, read from `laserTypes` for the current view (front, rear, left, right): pulse the stock cross, beam two bars with a centre tick and short ends, military four double diagonals, mining the same bars without the ends plus a dot in the centre. With no laser in the view there is no sight (the ST shows none). Each sight is three lines for one quadrant (x1, y1, x2, y2, 12 bytes), drawn with `drawLaserLine` four times, mirrored through the quadrant bits of `C` (`0x0F`, `0x0A`, `0x05`, `0x00`), so the data is 48 bytes and the routine 60. Previews: `docs_other/laser_sights/cpc_laser_sights.png` (`cpc_sights.py`, untracked).

Place: the routine takes the first 128 bytes of the free zero tail of `COMMONXX` (`laserSightsBlock`, `LASER_SIGHTS_SIZE`) and `LaserSights` starts with a `jp` to it (3 bytes, `laserSightsJp`; the rest of the cross is dead then). **English with `-DMISSIONS` keeps the cross**: the flight images fill the tail there (610 bytes, 608 usable) and about 13 bytes were missing after every cut that kept the missions intact (measured: the launch-table cut saves 2 bytes per image, not the 12 first estimated). The parked firmware RAM in low memory was tried as flight-time space and rejected (`TODO.md`). `check_src.sh` proves the default is the original and `-DENHANCED` differs in these two slots only, in all three trees. Tested in cpcxray on the English build (patched into `firebird_in_flight.sna`, laser type 0-4, screenshots); the German build was played by hand (the sights work; disk `work/elite_de_sights.dsk`); the French build assembles and passes the checks but has not run in an emulator.

## A key of the sell menu (`ENHANCED`)

In the sell menu, A at a quantity prompt sells every good in the hold (the same row handler as typing the quantity, `sellQuantityofGood`) and leaves for the inventory screen. The old exit for any other key stays. `sell_all.asm` (48 bytes, one trade sound for the whole hold, no delay) sits in the free `LARGEAXX` tail
(with `-DMISSIONS` inside the resident stub, before the overlay); the only changed stock bytes are the operand of the `jp Inventory` at `csGotoInventoryScreen`, which now reads `jp sellAllEntry`. Nothing before `EquipShip` moves, so the save key is untouched.
`reAskifNotAllSold` counts the key down twice on its way there, so the routine compares with `"A"-2`; the other way in, the end of the menu loop, arrives with A = `0x11`. `check_src.sh` allows exactly the operand and the routine (`sellAllOperand`, `sellAllEntry..sellAllEnd`) as differences of `-DENHANCED`.
Test: `tools/tests/test_sellall.py` (boot, fill the hold, key 3, key A). English only so far; German and French need the hook and a localised key.

## The added missions (`MISSIONS`)

Five missions on top of the three stock ones: Constrictor, Thargoid plans, Trumbles, and the two Elite Plus missions (stolen police ship, asteroid bombardment). How they work, their order and triggers: `_missions_built.md`; the research: `_missions.md`.
What they change in the stock game:

- **Credit:** the Constrictor hull (`src/elite/missions_hull.asm`) is by Fessor, used with his permission (post: <https://www.cpcwiki.eu/forum/programming/expanding-elite/msg205425/#msg205425>).
- **Hook sites** (each a 3-byte `call` replacement, so no stock routine moves): `spawnShip` (`mxShipTable`, ship type 19), `spawnCommand0` (`mxSpawnCheck`), `todo_killedsomeone` (`mxKillHook`, replaces `call getBounty`),
  `applyLaserDamagetoEntity` (`mxLaserHook`), `RechargeEnergy` (`mxRecharge`), the docking sequence (`&1714` replaces `chkMissions`), `launchSequence` (`mxLaunchEntry`), `setShipvarsAtArrival` (`mxArrive`), `todoOverheating` (`mxSun`),
  the Inventory loop (`mxInvHook`), the `call transferBuffertoScreen` in `Spaceflight` at `&1E4D` (`mxFlightDraw`, the Trumble sprites) and the escape-pod launch (`mxPodHook`).
- **Unused save bytes** carry the state (`&38FD`, `&38FE`, `&3905-&3906`), so the save layout and the code-keyed encryption are unchanged and old saves still load (`check_src.sh` checks the key window).
- **Free space:** the 812-byte tail of `LARGEAXX` and the 610-byte tail of `COMMONXX` (`_memory_map.md`); the missions load their code from overlay and image files, one at a time.
- **Behaviour you can notice outside the missions:** an escape pod now ends the Trumbles quest (the original leaves 1-7 aboard); a docking costs nothing extra unless a mission can act (an overlay load is about 2 s of disk time); a launch swaps the
  flight image only when it differs (about 2 s more).
- Disk files: `MISSIONC/P/T/R.BIN` (overlays), `MFLIGHT0/C/P/T/S/R.BIN` (flight images), `README.TXT`; all but the `.BAS`/`.TXT` files are hidden.

## Ship packs and traffic (`MISSIONS`, `TRAFFIC`)

Ten more hulls (Fessor's; `src/elite/missions_ships.asm`) in seven flight images `MFLIGHT1-7`, picked per system visit by `(jumpCounter + presentSystemSeed) & 7`; the pack hook redirects some Sidewinder, Krait and trader spawns to them. The spawn roll constants are named (`SPAWN_HOSTILE_LIMIT` 0x5A, `SPAWN_JUNK_WIDTH` 35, escort packs of one to four) with the stock values in comments. Design, sizes, load times, tests and what was left out: `_ship_packs.md`.

## Trainer, save tools and disks

- `TRAINER.BAS` (ours, replaces the Firebird disk's `CHEAT.BAS`, which is deleted on our disks; renamed from `CHEAT.BAS` on 2026-11-15): interactive trainer with prompts for each of the original pokes plus no pirate boarding, unlimited hold, own cloak, cash, stock mission stage, kills, jumps and added-mission presets;
  `EDITSAVE.BAS` edits and `LISTSAVE.BAS` lists commander saves on the CPC; `tools/saveedit.py` does the same on the host and converts saves between UK, French and German builds. `_cheats.md`, `_savegame.md`.
- The original `CHEAT.BAS` has a wrong cloak entry (it only lists the device; `POKE &202B,0` makes the cloak work); ours sets the ownership bit instead.
- The mission disk (`build_dsk.py --missions`) now carries our `TRAINER.BAS` (+ hidden `CHEATB.BIN`) instead of Firebird's, and `SHOWSHPS.BAS` + hidden `SHIPS.BIN`, the ship viewer (`_cheats.md`).
- Built disks show only `.BAS` and `.TXT` files in `CAT`, like the original protected disk; `RUN`, `LOAD` and the game's own loads still find the hidden files.

## Stock bugs we found and did not fix

| Bug | Where | Status |
|---|---|---|
| Escape-pod cargo clear starts at `&38E1` (the market random byte) and keeps alien items (`&38F2`); `cargoSpaceFree` is reset to full capacity | `mleCleanInvLoop`; fixed with `-DENHANCED` (`podCleanOperand`: the loop starts at `cargoHold`, `&38E2`) | no reward depends on it (`_missions.md` section 3) |
| The random witchspace mis-jump looks unreachable (the seed byte is compared with `0x40` then `0x20`) | `someHyperSpaceFunctions`; only the pause-menu toggle (bit 6 of `keybFlags0`) forces it | not applied (`_gameplay.md`) |
| The station-kill code does `SET 3,(HL)` on `&3926` instead of `Missionflag` | invasion mission | left as is |
| Large planets off screen can overwrite memory below the bitmap if the line-count clamp at `&245B` is missing | disc fill | stock build is safe (131,072-input sweep); the cassette release presumably lacked the clamp (`_architecture.md`) |

## Status screen labels in German and French (`ENHANCED`)

The English tidy-up shortens the labels so that every value starts in column 9. The same needs shorter words in the other languages; the byte length of each token string must stay, and the padding must be a token that prints nothing.
German: "System:", "Ziel:" (were "Derzeitiges System", "Hyperraum-Ziel"), "Tank:" (the main-table token `&69`, was "Treibstoff"; it also names the fuel item in the equipment list), "Status:" (was "Strafregister") and "Klasse:" (was "Einstufung"), padded with code `&14` in the
message table and token `&68` in the main table. Konto stays, so the balance starts one column further right than the other values. French: "Syst.:" and "Cible:" (were "Systeme Present" and "Systeme Hyperespace"); "Fuel", "Argent" and "Niveau" already fit.
**French "Statut Legal" is unchanged**: it needs four padding bytes, and every candidate code in the French message table prints something (`&14` an e-acute, `&0C` line breaks, `&11`-`&17` variables such as the planet name, `&06` flips a print flag and corrupts the screen), so its value stays in column 15.
All three trees share the labels `statusLabels`/`statusLabelsEnd`, `statusColon`, `statusColonPrint`, `statusTitleCol`, `chartTitleCol`, `titleTab`, `fuelTab` (and `statusToken`/`statusTokenEnd`, `fuelToken`/`fuelTokenEnd` where a longer slot exists); `check_src.sh` takes the slot lengths from them.
Screenshots: `tools/tests/test_station_screens.py en|de|fr` writes `work/xray/output/station_<loc>_{status,chart,inventory,buy}.png` (the commander status page is key `9`, the market `8`).

# Changelog

Newest first. Entries up to 2026-11-11 are in `docs/changelog_archive.md`. The project root is a git repository from 2026-11-07; before that, the archive is the only history. Dates are ISO.

- **Trainer no longer corrupts the Asp (2026-11-20).** `TRAINER.BAS` kept its answers as strings across the `CHAIN`, and BASIC copied them over the Asp's vertex data (`&8FED-&9000`) once the game was loaded, so Asps were drawn as fans of long lines; line 164 now empties the strings and collects them before the `CHAIN` (`docs/_cheats.md`).

- **Folders and cleanup (2026-11-16).** Original disks and tapes moved to `disks/` and `make` targets deliver to `build/` (both gitignored; `build/README.md` explains the contents); the tools that guard the originals refuse `disks/`. `SHOWSHIP.BAS` renamed `SHOWSHPS.BAS`. `LICENSE` (MIT for tools, CC BY 4.0 for docs) and `NOTICE` added. Removed: the Spectrum/ArcElite one-offs (`arc_*.py`, `armdis.py`, `adfs_e.py`), `parked_ram_*.py`, three installer scripts, three `showsave_*` screenshots. `docs/_arcelite.md` and `docs/_filled_ships.md` moved to `docs_other/`; `TODO.md` and this file shortened (older wording is in git history).

- **Esc at the second digit of a quantity (2026-11-16, `-DENHANCED`, all three trees).** Esc (or any non-digit) after the first digit of a buy or sell quantity left that digit's trade applied; it now undoes it like DEL (`jr nc,LAB_ram_095f` became `jr nc,LAB_ram_08f7`, same size, so the save key does not move; marker `escQtyOperand`, `check_src.sh` allows it).

- **Kill count on the status page (2026-11-15).** "Rating: Harmless - 12" (`src/elite/killcount.asm`, `-DENHANCED`, English): the routine replaces `call anotherPrintwithTokeninA` after `getRank` (slot `killHookSite` in `check_src.sh`), 26 bytes in the shared head of every flight image (`-DMISSIONS`, address asserted) or in the zero tail without missions, plus a 10-byte helper `killSpace` in the dead bytes of `unusedGetFlightMode` / `unusedGetCloakFlag` (one space before the dash for every rank: Poor, Average and Above Average already end in a space in the stock text, which the economy line needs).

- **`CHEAT.BAS` renamed `TRAINER.BAS` (2026-11-15).** Our interactive trainer is `src/cheats/TRAINER.ASC` / `TRAINER.BAS` / `TRAINER.BAS.txt` (stage two stays `CHEATB`), `RUN"TRAINER`.

- **Laser sights (2026-11-15).** One sight per laser type instead of the cross for all of them: pulse the cross, beam two bracketed bars with a tick, military four diagonals, mining the bars plus a centre dot; no sight without a laser (`-DENHANCED`, `src/*/lasersights.asm`, all three trees, English only without `-DMISSIONS`: the mission flight images leave no room in the `COMMONXX` tail).

- **Two builds, `make original` and `make expanded` (2026-11-15).** `original` writes the stock bytes (CPC+ fix included) into a copy of the Firebird disk (`tools/build_dsk.py --stock`, `tools/build_original.sh`; `LOC=de|fr` for the German and French disks); `expanded` runs `tools/build_expanded.sh`: ship viewer, then `build_cheat.sh` (trainers, `build_dsk.py --missions`, EDITSAVE and LISTSAVE added), giving `work/elite_expanded.dsk` (English only until the missions are ported).

- **Ship viewer (2026-11-15).** `SHOWSHPS.BAS` on `work/showship.dsk` (`tools/build_showship.sh`, `tools/mk_showship.py`, `src/cheats/showship.asm`) and on the mission disk: all 30 models (21 ships and 9 objects such as the station, missile, canister and asteroids: 19 stock, 10 extras, Constrictor) with name, rotating hidden-line wireframe and kills, bounty, speed, energy; arrow keys step, `Q` quits.

- **Ship packs and C64-like traffic (2026-11-14, `-DMISSIONS` and `-DTRAFFIC`).** Seven flight images `MFLIGHT1-7` carry one or two of Fessor's hulls (Gecko, Cobra Mk I, Worm, Moray, Mamba, Adder, Boa, Anaconda, Shuttle; `src/elite/missions_ships.asm` from `tools/fessor_ships.py`, `missions_flight_k.asm`) and swap them in for a stock type on half the spawns through the `mxShipTable` hook.

- **A sells the whole hold in the sell menu; Constrictor trimmed (2026-11-13, `-DENHANCED`, English).** `src/elite/sell_all.asm` (48 bytes, plays the trade sound once): A at a quantity prompt sells every good and returns to the inventory; the hook is the operand of the `jp Inventory` after the prompt loop, so nothing before `EquipShip` moves.

- **Trumbles block the chain (2026-11-13, `-DMISSIONS`).** The docked stub (`missions_docked.asm`) returns right after the stock-mission check while the Trumble count is nonzero, so no chain mission is offered, paid or running while the Trumbles image (which has none of the mission hooks) is loaded.

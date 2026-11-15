# Implemented missions (combined build, 2026-11-08)

What is built, how it works, what it costs and how it is tested. The research behind each mission (other versions, source reading, Elite Plus code) is in `docs/_missions.md`.
Everything lives on branch `addon-missions` (the former branches `missions-foundation`, `mission-constrictor`, `mission-plans`, `mission-trumbles`, `escape-menus` are merged into it and deleted; `main` is its ancestor).
`python3 -I tools/build_dsk.py --missions` writes `work/elite_missions.dsk`: the four code files plus the overlay and image files below. The stock build stays byte-exact (`bash tools/check_src.sh`, also `de` and `fr`).
**Status:** booted from the DSK with `RUN"ELITE` in cpcxray; every mission is tested with forced states and direct calls, none has been played through.

## 1. Missions, order, triggers

The three stock missions (S1 to S3: supernova rescue, cloaking device, Thargon invasion) run first and unchanged: the docked stub hands over to the original `chkMissions` whenever `ThargonMissionVar` is not 0.
The added chain is fixed: **Constrictor -> Thargoid plans -> stolen police ship -> asteroid bombardment**. The Trumbles are offered once, in the gap after the Constrictor is paid and before the plans are offered, so they never interrupt a running hunt; while Trumbles are aboard the docked stub starts nothing else (it returns right after the stock-mission check), so no chain mission can be running when the Trumbles image is loaded. A sun ends them, as in the original, or an escape pod; until then the chain waits.

Global prerequisites for every added mission: the files on the disk; for the chain at least 256 kill points (`killScoreHigh` >= 1; below that the stub returns without touching the disk; the Trumbles offer has no kill gate); no stock mission offer or reward pending.

| # | Mission | Prerequisites | Offer trigger | Hunt / flight part | Completion and reward | State | Code |
|---|---|---|---|---|---|---|---|
| S1 | Supernova rescue (stock) | none; jumps counted from galaxy 2 on | arrival hook: low byte of `jumpCounter` reaches 32 (stage 1, `Missionflag` bit 0); the briefing replaces the Buy Cargo screen at a docking | the sun goes nova (`FlightMode` 1), every hyperspace key is a free galactic jump | refugees sold at `SellGoods`: rank +1 and gems | `Missionflag` bits 0, 5 | stock |
| S2 | Cloaking device / Cougar (stock) | supernova stage done (bit 0) | `jumpCounter` reaches 128 (stage 2, bit 1) | random encounters (30/256 per spawn check) spawn a marked Asp Mk II with 2-4 escorts (1-4 with `-DTRAFFIC`, which the disks use) | kill it with a laser, scoop the canister: cloak (`Y`, bit 6), rank +1 | `Missionflag` bits 1, 6, `aspMissionState` | stock |
| S3 | Thargon invasion (stock) | cloak stage reached (bit 1) | `jumpCounter` reaches 254 (stage 3, sets bit 2 and `ThargonMissionVar` 1) | the Thargons take the station of system 0 of the galaxy, it launches Thargoids; docking there in state 4 is game over | kill the station: rank +1, ECM jammer (bit 7), name FLORENCE | `Missionflag` bits 2, 3, 7, `ThargonMissionVar` | stock |
| T | Trumbles | 5,000 Cr or more (thousands word >= 5); offer not made before (`missionState` bit 7); no kill-score gate | the first docking after the Constrictor is paid (`missionState & 0x8F` = 2: bits 0-1 = 2, plans not offered, bit 7 clear), in any galaxy, once whatever the answer, so a "no" is final | breed on every arrival (eat food and narcotics), slow breeding from 256, squeak, sprites, heat halves them | none; Y pays 5,000 Cr for one Trumble; only a sun kills them | `&3905` count, bit 7 | MISSIONT, MFLIGHTT |
| 1 | Constrictor | none | docking in galaxy 1 or 2 | seven hints, each shown only when docked at that stage's system (Reesdice, Arexe, Cearso, Errius, Inbibe, Ausar, Usleri; galaxy 2 starts at Cearso); the Constrictor spawns at Orarra (galaxy 2, 144/33); only a military laser hurts it | kill it; the next docking pays 5,000 Cr and one rank step | bits 0-1 (0 none, 1 hunting, 3 killed, 2 paid), 4-6 hint stage | MISSIONC, MFLIGHTC |
| 2 | Thargoid plans | Constrictor paid; 1280 kill points (`killScoreHigh` >= 5) | docking in galaxy 3 | plans at Ceerdi (215/84), deliver at Birera (63/72); 22% of spawn checks add a Thargoid and a Thargon while aboard | delivery: Navy energy unit (3 recharge steps) and a rank step | bits 2-3 (0 none, 1 briefed, 2 aboard, 3 done) | MISSIONP, MFLIGHTP |
| 3 | Stolen police ship (Elite Plus 4) | plans delivered | waits 5 to 12 hyperspace arrivals, then offered at the next docking anywhere | at Birera (galaxy 3, 63/72) one non-police hostile Viper (energy `&C8`), 22% of spawn checks, never two | kill it: the next docking pays 4,000 Cr; the kill is no offence | bits 4-6 (1 waiting, 2 ready, 3 hunting, 4 killed, 5 paid); `&38FE` counts the jumps | MISSIONP, MFLIGHTS |
| 4 | Asteroid bombardment (Elite Plus 6) | stolen ship paid | the next docking anywhere | at Ceerdi (galaxy 3, 215/84) an asteroid on 50% of spawn checks; 20 to destroy there | at 0 the next docking pays 6,000 Cr; no failure path | `&38FE`: asteroids to go in bits 2-7, state in bits 0-1 (0 offer, 1 clearing, 2 cleared, 3 paid) | MISSIONR, MFLIGHTR |

Galaxy numbers are the game's 1-based galaxies (code index 0-7).

## 2. Architecture

Missions run one at a time, so their code is loaded when needed instead of being resident (overlays).
- **Docked part.** The 812-byte zero tail of `LARGEAXX` (`&1714-&1A3F`; `loadLARGEAXX` reloads the file from disk at every docking, so the tail is fresh each time and unused by the game) holds a resident **stub** (251 bytes) and one **overlay** loaded behind it
  with the game's own `loadFile`. The docking sequence calls `&1714` in place of `chkMissions`. The stub tests the trigger first (state bytes, galaxy, system table `mxStageTable`, cash) and loads an overlay only where something can happen,
  about 2 s of emulated disk time; a docking with nothing to do costs nothing. Overlay layout: `jp entry`, `dw textTable`, code, strings; a module ends with `jp mxShowEnd` (message box, back to the docking code) or `ret`.
- **Flight part.** The last 610 bytes of `COMMONXX` (`&9D9E-&9FFF`) hold a table of nine 3-byte `jp` vectors, an id byte and the launch hook, then at most one **flight image** (a mission image, or with no mission one of the seven ship packs `MFLIGHT1-7`, `_ship_packs.md`). At every launch `mxLaunchEntry` picks the image for the state
  (letter T Trumbles, C Constrictor, P plans, S stolen ship, R asteroids, 0 none; T is tested first, which is safe because the docked stub lets no chain mission run while Trumbles are aboard, but a poked state or an old save can have both, see `elite128` commit `52573a7` for the reorder: mission image first, T only when none is wanted) and loads `MFLIGHT?.BIN` only when it differs from the one in RAM. Every image has stubs for the vectors it does not use.
- **Hook sites in stock code** (each a 3-byte `call` replacement, so no stock routine moves): `spawnShip` (`mxShipTable`, serves ship type 19), `spawnCommand0` (`mxSpawnCheck`), `todo_killedsomeone` (`mxKillHook`, replaces `call getBounty`),
  `applyLaserDamagetoEntity` (`mxLaserHook`), `RechargeEnergy` (`mxRecharge`), the docking sequence (`&1714`), `launchSequence` (`mxLaunchEntry`), `setShipvarsAtArrival` (`mxArrive`), `todoOverheating` (`mxSun`), the Inventory loop
  (`mxInvHook`) and the `call transferBuffertoScreen` in `Spaceflight` at `&1E4D` (`mxFlightDraw`, the sprites).
- **Build.** `-DMISSIONS` selects the hooks and tails; `-DFL_C/P/T/S/R` pick the flight image and `-DOVL_C/P/T/R` the overlay; `tools/build_dsk.py` slices each by labels (`mxFlightBase..mxFlightEnd`, `mxOverlayBase..mxOverlayEnd`) and adds the files with AMSDOS headers, then adds `README.TXT` and hides every file that is not `.BAS` or `.TXT` (System attribute, as on the original disk; `tools/hide_files.py`).
- **Save bytes used** (all unused by the stock game, no key change): `&38FD` mission state (bits 0-1 Constrictor, 2-3 plans, 4-6 stage of the first added mission, 7 Trumbles offered), `&38FE` (jump counter of the stolen ship, then the asteroids' state and count),
  `&3905-&3906` Trumble count (at most `&7FFF`). `docs/_savegame.md` has the layout.

## 3. How each mission works (insights)

- **Constrictor.** The CPC hull is Fessor's (his post: <https://www.cpcwiki.eu/forum/programming/expanding-elite/msg205425/#msg205425>, used with his permission), converted by `tools/fessor_hull.py` (only this one ship is used; the rest of `extended/` stays out of git). Ship type 19 is served from a one-entry table (`cp 19` in `mxShipTable`, only our spawn passes 19).
  Spawn at Orarra in stage 7 (all hints), one at a time; the laser hook makes any hit whose laser power lacks bit 4 do nothing (pulse and beam are 15, military 23, mining 50), so only a military laser or better hurts it. The kill hook sets state 3; the reward is paid at the next docking.
  The stub loads the overlay only at the system of the current hint stage, so hunts cost no disk time elsewhere.
- **Plans.** The 22% Thargoid + Thargon spawn mirrors the BBC; the Navy energy unit is `extraEnergyUnit` `&FE`, one more `SUB_ram_3693` recharge step (3 per call). Delivery also schedules the stolen ship.
- **Stolen police ship.** Elite Plus spawns the same Viper blueprint as the police with aggression 5, energy `&C8` and a marker byte. The CPC has no spare ship-record byte, so the marker is a flag pattern: police Vipers have bits 1 and 6 of `(ix+33)` set
  (blueprint byte 18), the stolen one has both cleared. That also makes its kill harmless to legal status (the kill code tests bits 5 and 6 of `ix+33` for the fugitive rule) and keeps the cop AI (bit 1) away from it.
- **Asteroids.** The game already has the asteroid hull (type 6), so the image only reuses the stock asteroid spawn of `spawnCommand0` and counts asteroid kills at Ceerdi; no marker is needed. State and count share `&38FE`: the offer writes `&51` (20 << 2 | 1), a kill subtracts 4.
- **Trumbles.** Arrival hook breeds (`2 * ((count + 0..15) OR 4)`; a sum of `&4000` or more before the doubling is held at `&7FFF`) and eats the hold's food and narcotics; with 256 or more, slow breeding in the spawn check and a squeak (bit 5 of `sfxFlags2Bitmap`, chance high byte / 64); the sun halves them; the inventory
  shows a line. **Sprites:** up to six 16 x 14 round, fluffy blobs (pen 3, one shape, `missions_trumble_art.txt` via `tools/sprite_enc.py`) OR-ed into the off-screen bitmap `&A000` just before it is copied to the screen, so nothing needs erasing; one
  Trumble moves per frame (counter mod 8) with an 8% chance of a new direction. Cost 270 bytes (code about 210, shape 56, state 28).
- **Escape key.** Separate from the missions: ESC is key code `&7F` instead of `&FF` in the ASCII keyboard table, so the buy, sell and equipment prompts leave on Escape (`-DENHANCED`; `docs/_cpcplus.md`).

## 4. Sizes (bytes, from the assembled files)

| Part | Constrictor | Plans | Stolen ship | Asteroids | Trumbles |
|---|---|---|---|---|---|
| Docked overlay file | `MISSIONC.BIN` 561 | `MISSIONP.BIN` 506 (also the stolen ship) | in `MISSIONP` | `MISSIONR.BIN` 170 | `MISSIONT.BIN` 178 |
| Flight image file | `MFLIGHTC.BIN` 597 | `MFLIGHTP.BIN` 269 | `MFLIGHTS.BIN` 361 | `MFLIGHTR.BIN` 285 | `MFLIGHTT.BIN` 607 |

Default image `MFLIGHT0.BIN` 167 (what `COMMONXX.BIN` carries; 9 bytes more than before for the ship pack picker, which every image carries). **Limits:** docked stub (with the sell-all key, 48 bytes) plus largest overlay (Constrictor, trimmed 2026-11-13) ends at `&1A3C`, 3 bytes short of the end of the tail (`&1A3F`); the Constrictor flight image is 597 of 608 (11 spare), the Trumbles image 607 (1 spare), so any further change there
needs trimming first. Every image carries the launch picker and the recharge hook. Text is tokenised with the game's own digrams and string references (`tools/textenc.py`), 25-31% smaller than raw text. Mission text is in the default capitalised-words
style (all caps): the stock mission screens use `{0D}`/`{13}` sentence case instead, which would cost about 38 docked bytes in the Constrictor overlay, so it stays as is for now.
**Time (emulated):** an overlay load about 1.9-2.1 s; a launch with an image swap about 3.9 s against 2.0 s for `loadIndicator` alone; nothing extra when nothing is active or the right image is in RAM.

## 5. Tests and tools

All run in cpcxray (`work/xray`, `~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/NAME.py`) after `python3 -I tools/build_dsk.py --missions` and a copy of the disk to `work/xray/disk/`.
- `test_mission_hook.py` (docked stub and overlays, about 30 scenarios, the fast ones assert that no overlay is loaded), `test_launch.py` (image picker, about 20 scenarios), `test_mission_flight.py` (Constrictor spawn, kill, laser), `test_plans.py`, `test_stolen_ship.py`,
  `test_rocks.py` (spawn, kill, arrival, a live loop with the station-near test patched out), `test_trumbles.py`, `test_trumble_sprites.py` (draw, stray-byte regression, live screenshot), `test_flight_hull.py`.
- Method: start from `output/firebird_in_flight.sna`, stop at `handleEntitys` (`&5066`, a safe point), write the freshly assembled `COMMONXX` patches, set variables, call a vector with a trap return address and restore registers when injecting calls.
- Helpers: `tools/size_report.py`, `tools/textenc.py`, `tools/sprite_enc.py`, `tools/fessor_hull.py`, `tools/build_dsk.py` (shared DSK code in `tools/dskx.py`). Testing aids: the trainer `CHEAT.BAS` (kills, jumps, added-mission presets), `tools/saveedit.py` and `SHOWSAVE.BAS` (`docs/_cheats.md`).

## 6. Limits and open items

**Known limits** (code review, 2026-11-08):
- While Trumbles are aboard the chain waits: the docked stub returns when the Trumble count is nonzero (6 bytes at its start, 2026-11-13), so no mission is offered, paid or running with the Trumbles image loaded (that image has none of the hooks). A player who accepts them and never meets a sun or a pod stalls the chain. The original has no end for Trumbles other than a sun; ours also ends them with an escape pod (`mxPodHook` in the dead block at `&1FDD` zeroes the count; the original leaves 1-7).
- A launch needs the game disk in the drive for the flight image (`loadFile` shows the firmware disk error and retries like every other game load; no mission-specific fallback).
- The vector table and the stub sit at fixed addresses (`&9D9E`, `&1714`), guarded by `ASSERT`s; flight images must end at or below `&9FFE`.

**Open:**
- A real playthrough of the whole chain with save and load.
- Tuning: 20 asteroids, 50% and 22% spawn rates, Birera as the police target. The Trumble squeak is settled (effect 13, chosen with `TRUMBLE.BAS`).
- A Trumbles end condition other than a sun; the Cobra Mk III that Elite Plus adds to the asteroid mission; the Constrictor's ECM and missiles (from the hull header, unchecked).
- A random per-commander order is not built: the last two missions are encoded differently and the stub plus Constrictor overlay has no room.
- Merging `addon-missions` into `main`.

## 7. Pokes to start each mission (for testing)

Two ways to set the state. **Trainer:** `RUN"CHEAT.BAS` on `work/missions_cheat.dsk` has the prompts Kills, Jumps and Added mission 1-4 (and Mission 0-3 for the stock missions); the table gives the answers. **Raw pokes:** the same values as plain `POKE`s in a loader
(lines between the `LOAD` of `common2x` and `CALL &1C82`, as `CHEAT.ASC` does): while the loader runs the save block sits `&FC` higher than in the running game, so the runtime address `&38FD` is `&39F9` there. The runtime addresses
are for `memory_write` in an emulator, or a monitor on a running game. Kill points are the BBC-style count at `&38D8/&38D9` (`&39D4/&39D5` in the loader): `POKE &39D5,n` sets `n x 256`. All presets leave the other save bytes alone.

| Mission | Trainer answers | Loader pokes | Runtime (running game) | Then |
|---|---|---|---|---|
| Constrictor | Kills 256 | `POKE &39D5,1` | `&38D9` = 1 | start in galaxy 1 (Lave), launch and dock again: the offer comes at the docking. For the Orarra fight: state `&39F9` = `&71` (hunting, all hints given) and go to Orarra in galaxy 2 |
| Thargoid plans | Kills 1280, Added mission 1 | `POKE &39D5,5:POKE &39F9,2` | `&38D9` = 5, `&38FD` = `&02` | needs a galaxy 3 docking (use "Free gal jump" in the trainer and a galactic hyperdrive); the offer comes at the docking there, then Ceerdi and Birera |
| Stolen police ship | Kills 256, Added mission 2 | `POKE &39D5,1:POKE &39F9,&2E` | `&38D9` = 1, `&38FD` = `&2E` | the offer comes at the next docking in any galaxy; the hunt is at Birera in galaxy 3. To test the jump wait instead: `POKE &39F9,&1E:POKE &39FA,5` (five hyperspace arrivals, then the next docking offers it) |
| Asteroid bombardment | Kills 256, Added mission 3 | `POKE &39D5,1:POKE &39F9,&5E:POKE &39FA,0` | `&38D9` = 1, `&38FD` = `&5E`, `&38FE` = 0 | the offer comes at the next docking in any galaxy; the rocks are at Ceerdi in galaxy 3. To start already clearing: `POKE &39FA,&51` (20 to go) |
| Trumbles | Kills 256, Cash 6000, Added mission 1 | `POKE &39D5,1:POKE &39D9,6:POKE &39DA,0:POKE &39F9,2` | `&38D9` = 1, `&38DD/&38DE` = 6 (thousands), `&38FD` = `&02` | the offer comes at the next docking, once, in the gap after the Constrictor reward and before the plans offer (state 0 offers the Constrictor first). To have them aboard at once: `POKE &3A01,3:POKE &3A02,0` (runtime `&3905/&3906` = 3) |
| Supernova (stock) | Mission 1 | `POKE &4E5D,0:POKE &39D6,31` | `&38DA` = 31 | the next hyperspace arrival starts it (the `&4E5D` patch makes jumps count in galaxy 1) |
| Cloaking device (stock) | Mission 2 | `POKE &4E5D,0:POKE &39D6,127:POKE &3A23,1` | `&38DA` = 127, `&3927` = 1 | the next arrival starts it |
| Thargon invasion (stock) | Mission 3 | `POKE &4E5D,0:POKE &39D6,253:POKE &3A23,3` | `&38DA` = 253, `&3927` = 3 | the next arrival starts it |

Notes. The added-mission presets keep the earlier stages consistent: preset 2 and up also fit the Navy energy unit (`&3902` / loader `&39FE` = `&FE`), which `saveedit.py --added` and `EDITSAVE.BAS` write (the trainer presets do not); with raw pokes add `POKE &39FE,&FE` if you care. Galaxy cannot be poked
(the seeds define it): reach galaxy 3 by two galactic jumps, with the trainer's free galactic jump, or load a save whose galaxy is already 3. The host save editor does the same presets on a save file (`tools/saveedit.py edit SAVE --kills 256 --added 2 -o ...`),
and `EDITSAVE.BAS` on the CPC.

Checked 2026-11-08 in cpcxray: for the Constrictor, plans, stolen ship, asteroids and Trumbles rows the trainer answers started the real game with exactly these values in memory (kills 256 or 1280, `&38FD/E` = `0000`, `0200`, `2E00`, `5E00`, `0000`, cash 6 thousand for the Trumbles); the status screen showed the rating Competent for 256 kills. That the offers then appear at a docking is covered by the docked tests with the same state values (`tools/test_mission_hook.py`), not by a real docking in the running game. The stock rows were not run.

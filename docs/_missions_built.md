# Implemented missions (combined build, 2026-11-08)

What is built, how it works, what it costs and how it is tested. The research behind each mission (other versions, source reading, Elite Plus code) is in `docs/_missions.md`.
Everything lives on one branch, `addon-missions` (it contains `missions-foundation`, `mission-constrictor`, `mission-plans`, `mission-trumbles`, `escape-menus`; `master` is its ancestor).
`python3 -I tools/build_dsk.py --missions` writes `work/elite_missions.dsk`: the four code files plus the overlay and image files below. The stock build stays byte-exact (`bash tools/check_src.sh`, also `de` and `fr`).
**Status:** booted from the DSK with `RUN"ELITE` in cpcxray; every mission is tested with forced states and direct calls, none has been played through.

## 1. Missions, order, triggers

The three stock missions (S1 to S3: supernova rescue, cloaking device, Thargon invasion) run first and unchanged: the docked stub hands over to the original `chkMissions` whenever `ThargonMissionVar` is not 0.
The added chain is fixed: **Constrictor -> Thargoid plans -> stolen police ship -> asteroid bombardment**. The Trumbles are independent: offered at any docking.

Global prerequisites for every added mission: the files on the disk; at least 256 kill points (`killScoreHigh` >= 1; below that the stub returns without touching the disk); no Trumbles aboard (while they are aboard nothing
else is offered and the Trumbles flight image replaces the others, so a running mission pauses until a sun kills them); no stock mission offer or reward pending.

| # | Mission | Prerequisites | Offer trigger | Hunt / flight part | Completion and reward | State | Code |
|---|---|---|---|---|---|---|---|
| S1 | Supernova rescue (stock) | none; jumps counted from galaxy 2 on | arrival hook: low byte of `jumpCounter` reaches 32 (stage 1, `Missionflag` bit 0); the briefing replaces the Buy Cargo screen at a docking | the sun goes nova (`FlightMode` 1), every hyperspace key is a free galactic jump | refugees sold at `SellGoods`: rank +1 and gems | `Missionflag` bits 0, 5 | stock |
| S2 | Cloaking device / Cougar (stock) | supernova stage done (bit 0) | `jumpCounter` reaches 128 (stage 2, bit 1) | random encounters (30/256 per spawn check) spawn a marked Asp Mk II with 2-3 escorts | kill it with a laser, scoop the canister: cloak (`Y`, bit 6), rank +1 | `Missionflag` bits 1, 6, `aspMissionState` | stock |
| S3 | Thargon invasion (stock) | cloak stage reached (bit 1) | `jumpCounter` reaches 254 (stage 3, sets bit 2 and `ThargonMissionVar` 1) | the Thargons take the station of system 0 of the galaxy, it launches Thargoids; docking there in state 4 is game over | kill the station: rank +1, ECM jammer (bit 7), name FLORENCE | `Missionflag` bits 2, 3, 7, `ThargonMissionVar` | stock |
| T | Trumbles | 5,000 Cr or more (thousands word >= 5); offer not made before (`missionState` bit 7) | the first docking in any galaxy (galaxy 1 included: no galaxy test), once whatever the answer, so a "no" is final | breed on every arrival (eat food and narcotics), slow breeding from 256, squeak, sprites, heat halves them | none; Y pays 5,000 Cr for one Trumble; only a sun kills them | `&3905` count, bit 7 | MISSIONT, MFLIGHTT |
| 1 | Constrictor | none | docking in galaxy 1 or 2 | seven hints, each shown only when docked at that stage's system (Reesdice, Arexe, Cearso, Errius, Inbibe, Ausar, Usleri; galaxy 2 starts at Cearso); the Constrictor spawns at Orarra (galaxy 2, 144/33); only a military laser hurts it | kill it; the next docking pays 5,000 Cr and one rank step | bits 0-1 (0 none, 1 hunting, 3 killed, 2 paid), 4-6 hint stage | MISSIONC, MFLIGHTC |
| 2 | Thargoid plans | Constrictor paid; 1280 kill points (`killScoreHigh` >= 5) | docking in galaxy 3 | plans at Ceerdi (215/84), deliver at Birera (63/72); 22% of spawn checks add a Thargoid and a Thargon while aboard | delivery: Navy energy unit (3 recharge steps) and a rank step | bits 2-3 (0 none, 1 briefed, 2 aboard, 3 done) | MISSIONP, MFLIGHTP |
| 3 | Stolen police ship (Elite Plus 4) | plans delivered | waits 5 to 12 hyperspace arrivals, then offered at the next docking anywhere | at Birera (galaxy 3, 63/72) one non-police hostile Viper (energy `&C8`), 22% of spawn checks, never two | kill it: the next docking pays 4,000 Cr; the kill is no offence | bits 4-6 (1 waiting, 2 ready, 3 hunting, 4 killed, 5 paid); `&38FE` counts the jumps | MISSIONP, MFLIGHTS |
| 4 | Asteroid bombardment (Elite Plus 6) | stolen ship paid | the next docking anywhere | at Ceerdi (galaxy 3, 215/84) an asteroid on 50% of spawn checks; 20 to destroy there | at 0 the next docking pays 6,000 Cr; no failure path | `&38FE`: asteroids to go in bits 2-7, state in bits 0-1 (0 offer, 1 clearing, 2 cleared, 3 paid) | MISSIONR, MFLIGHTR |

Galaxy numbers are the game's 1-based galaxies (code index 0-7).

## 2. Architecture

Missions run one at a time, so their code is loaded when needed instead of being resident (overlays).
- **Docked part.** The 812-byte zero tail of `LARGEAXX` (`&1714-&1A3F`; `loadLARGEAXX` reloads the file from disk at every docking, so the tail is fresh each time and unused by the game) holds a resident **stub** (249 bytes) and one **overlay** loaded behind it
  with the game's own `loadFile`. The docking sequence calls `&1714` in place of `chkMissions`. The stub tests the trigger first (state bytes, galaxy, system table `mxStageTable`, cash) and loads an overlay only where something can happen,
  about 2 s of emulated disk time; a docking with nothing to do costs nothing. Overlay layout: `jp entry`, `dw textTable`, code, strings; a module ends with `jp mxShowEnd` (message box, back to the docking code) or `ret`.
- **Flight part.** The last 610 bytes of `COMMONXX` (`&9D9E-&9FFF`) hold a table of ten 3-byte `jp` vectors, an id byte and the launch hook, then at most one **flight image**. At every launch `mxLaunchEntry` picks the image for the state
  (letter T Trumbles, C Constrictor, P plans, S stolen ship, R asteroids, 0 none) and loads `MFLIGHT?.BIN` only when it differs from the one in RAM. Every image has stubs for the vectors it does not use.
- **Hook sites in stock code** (each a 3-byte `call` replacement, so no stock routine moves): `spawnShip` (`mxShipTable`, serves ship type 19), `spawnCommand0` (`mxSpawnCheck`), `todo_killedsomeone` (`mxKillHook`, replaces `call getBounty`),
  `applyLaserDamagetoEntity` (`mxLaserHook`), `RechargeEnergy` (`mxRecharge`), the docking sequence (`&1714`), `launchSequence` (`mxLaunchEntry`), `setShipvarsAtArrival` (`mxArrive`), `todoOverheating` (`mxSun`), the Inventory loop
  (`mxInvHook`) and the `call transferBuffertoScreen` in `Spaceflight` at `&1E4D` (`mxFlightDraw`, the sprites).
- **Build.** `-DMISSIONS` selects the hooks and tails; `-DFL_C/P/T/S/R` pick the flight image and `-DOVL_C/P/T/R` the overlay; `tools/build_dsk.py` slices each by labels (`mxFlightBase..mxFlightEnd`, `mxOverlayBase..mxOverlayEnd`) and adds the files with AMSDOS headers.
- **Save bytes used** (all unused by the stock game, no key change): `&38FD` mission state (bits 0-1 Constrictor, 2-3 plans, 4-6 stage of the first added mission, 7 Trumbles offered), `&38FE` (jump counter of the stolen ship, then the asteroids' state and count),
  `&3905-&3906` Trumble count (at most `&7FFF`). `docs/_savegame.md` has the layout.

## 3. How each mission works (insights)

- **Constrictor.** The CPC hull is Fessor's converted by `tools/fessor_hull.py` (only this one ship is used; the rest of `extended/` stays out of git). Ship type 19 is served from a one-entry table (`cp 19` in `mxShipTable`, only our spawn passes 19).
  Spawn at Orarra in stage 7 (all hints), one at a time; the laser hook makes any hit with power below 23 (military) do nothing, so only a military laser or better hurts it. The kill hook sets state 3; the reward is paid at the next docking.
  The stub loads the overlay only at the system of the current hint stage, so hunts cost no disk time elsewhere.
- **Plans.** The 22% Thargoid + Thargon spawn mirrors the BBC; the Navy energy unit is `extraEnergyUnit` `&FE`, one more `SUB_ram_3693` recharge step (3 per call). Delivery also schedules the stolen ship.
- **Stolen police ship.** Elite Plus spawns the same Viper blueprint as the police with aggression 5, energy `&C8` and a marker byte. The CPC has no spare ship-record byte, so the marker is a flag pattern: police Vipers have bits 1 and 6 of `(ix+33)` set
  (blueprint byte 18), the stolen one has both cleared. That also makes its kill harmless to legal status (the kill code tests bits 5 and 6 of `ix+33` for the fugitive rule) and keeps the cop AI (bit 1) away from it.
- **Asteroids.** The game already has the asteroid hull (type 6), so the image only reuses the stock asteroid spawn of `spawnCommand0` and counts asteroid kills at Ceerdi; no marker is needed. State and count share `&38FE`: the offer writes `&51` (20 << 2 | 1), a kill subtracts 4.
- **Trumbles.** Arrival hook breeds (`2 * ((count + 0..15) OR 4)`, capped `&7FFF`) and eats the hold's food and narcotics; with 256 or more, slow breeding in the spawn check and a squeak (bit 5 of `sfxFlags2Bitmap`, chance high byte / 64); the sun halves them; the inventory
  shows a line. **Sprites:** up to six 16 x 14 round, fluffy blobs (pen 3, one shape, `missions_trumble_art.txt` via `tools/sprite_enc.py`) OR-ed into the off-screen bitmap `&A000` just before it is copied to the screen, so nothing needs erasing; one
  Trumble moves per frame (counter mod 8) with an 8% chance of a new direction. Cost 270 bytes (code about 210, shape 56, state 28).
- **Escape key.** Separate from the missions: ESC is key code `&7F` instead of `&FF` in the ASCII keyboard table, so the buy, sell and equipment prompts leave on Escape (`docs/_cheats.md` and `CHANGELOG.md`).

## 4. Sizes (bytes, from the assembled files)

| Part | Constrictor | Plans | Stolen ship | Asteroids | Trumbles |
|---|---|---|---|---|---|
| Docked overlay file | `MISSIONC.BIN` 561 | `MISSIONP.BIN` 506 (also the stolen ship) | in `MISSIONP` | `MISSIONR.BIN` 170 | `MISSIONT.BIN` 178 |
| Flight image file | `MFLIGHTC.BIN` 609 | `MFLIGHTP.BIN` 256 | `MFLIGHTS.BIN` 352 | `MFLIGHTR.BIN` 276 | `MFLIGHTT.BIN` 606 |

Default image `MFLIGHT0.BIN` 158 (what `COMMONXX.BIN` carries). Resident stub 249. **Limits:** docked stub plus largest overlay (Constrictor) ends at `&1A3E` of `&1A40` (2 spare); the Constrictor flight image is 609 of 610 (1 spare), so any further change there
needs trimming first. Every image carries the launch picker and the recharge hook. Text is tokenised with the game's own digrams and string references (`tools/textenc.py`), 25-31% smaller than raw text. Mission text is in the default capitalised-words
style (all caps): the stock mission screens use `{0D}`/`{13}` sentence case instead, which would cost about 38 docked bytes in the Constrictor overlay, so it stays as is for now.
**Time (emulated):** an overlay load about 1.9-2.1 s; a launch with an image swap about 3.9 s against 2.0 s for `loadIndicator` alone; nothing extra when nothing is active or the right image is in RAM.

## 5. Tests and tools

All run in cpcxray (`work/xray`, `~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/NAME.py`) after `python3 -I tools/build_dsk.py --missions` and a copy of the disk to `work/xray/disk/`.
- `test_mission_hook.py` (docked stub and overlays, about 30 scenarios, the fast ones assert that no overlay is loaded), `test_launch.py` (image picker, about 20 scenarios), `test_mission_flight.py` (Constrictor spawn, kill, laser), `test_plans.py`, `test_stolen_ship.py`,
  `test_rocks.py` (spawn, kill, arrival, a live loop with the station-near test patched out), `test_trumbles.py`, `test_trumble_sprites.py` (draw, stray-byte regression, live screenshot), `test_flight_hull.py`.
- Method: start from `output/firebird_in_flight.sna`, stop at `handleEntitys` (`&5066`, a safe point), write the freshly assembled `COMMONXX` patches, set variables, call a vector with a trap return address and restore registers when injecting calls.
- Helpers: `tools/size_report.py`, `tools/textenc.py`, `tools/sprite_enc.py`, `tools/fessor_hull.py`, `tools/build_dsk.py` (shared DSK code in `tools/dskx.py`). Testing aids: the trainer `CHEAT.BAS` (kills, jumps, added-mission presets), `tools/saveedit.py` and `SHOWSAVE.BAS` (`docs/_cheats.md`).

## 6. Open items

A real playthrough of the whole chain with save and load; listening to the squeak (other effects: flags2 bit 7 the lock blip, flags1 bit 7 the key click); tuning (20 asteroids, 50% and 22% spawn rates, Birera as the police target); a Trumbles end condition other than a sun;
the Cobra Mk III that Elite Plus adds to the asteroid mission; a random per-commander order (not built: the two last missions are encoded differently and the stub plus Constrictor overlay has no room); optionally a Trumbles gate after a stock mission or outside galaxy 1;
the Constrictor's ECM and missiles come from the hull header and were not checked; merging `addon-missions` into `master` (the repo still has `master`, not `main`).

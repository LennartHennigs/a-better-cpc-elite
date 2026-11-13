# Missions: research notes

All eight missions below now exist in the combined build; what was built (order, triggers, sizes, tests) is in `docs/_missions_built.md`.
This file keeps the research behind them: what other versions do, what the CPC already had, source readings (BBC, C64, Apple II, Atari ST, MSX,
Elite Plus) and the questions that were answered. CPC facts come from `docs/_gameplay.md`, `docs/_savegame.md` and `src/elite/`; 6502 facts
from Mark Moxon's annotated BBC code (https://elite.bbcelite.com/deep_dives/: Constrictor, Thargoid Plans, Trumbles; fetched 2026-11-07) and
Andy McFadden's Apple II disassembly. Links: `docs/_references.md`. Unverified claims are marked *estimate* or *to check*.

## 1. What the other versions have

Basis: BBC cassette and Electron from Moxon's Constrictor page ("no missions"); BBC disc, Apple II, C64 and NES from annotated source (the NES `TP` byte
has exactly three fields); Atari ST from `missions.m68`; MSX from the TI-99/4A conversion of the MSX code, whose comments document the five mission
states. "wiki" means only a forum or wiki list, not code.

| Mission | BBC cassette, Electron | BBC disc, 6502SP, Master | Apple II | C64 | NES | Atari ST, Amiga | MSX | CPC stock | Elite Plus (PC) |
|---|---|---|---|---|---|---|---|---|---|
| Constrictor hunt | no | yes | yes | yes | yes | yes (#1) | yes (#1) | no | wiki: replaced in some lists |
| Thargoid plans / documents | no | yes | yes | yes | yes | yes (#2) | yes (#2) | no | wiki: yes |
| Trumbles | no | no | no | yes | yes | no | no | no | wiki: yes |
| Supernova (refugees) | no | no | no | no | no | yes (#3) | yes (#3, "Fuel Leak", sun approaches) | **yes** | wiki: yes |
| Cloaking device (Cougar, Asp escorts) | no | no | no | no | no | yes (#4) | yes (#4) | **yes** (special Asp) | wiki: yes (masking device) |
| Thargoid invasion (ECM jammer) | no | no | no | no | no | yes (#5) | yes (#5) | **yes** | wiki: yes |
| Stolen police ship | no | no | no | no | no | no | no | no | wiki: yes (4,000 Cr) |
| Asteroid bombardment | no | no | no | no | no | no | no | no | wiki: yes (6,000 Cr) |

ArcElite (Archimedes) has a different set of four (section 5). The Apple II is a BBC-disc derivative (same two missions, same `TP` bit layout). Elite-A's generated delivery missions are out of scope.

**MSX state table** (TI-99/4A source `src/main-code.a99`): five missions run in order via `next_mission` (1-5, 6 = done) when `jumps_to_next_mission` reaches 0;
it counts down on every hyperspace jump **outside the first galaxy** while no mission is under way, reset to 64. The state byte's high nibble is the mission,
the low nibble the progress: `$10-$19` Constrictor (a five-system trail, reward on docking), `$20-$21` documents (Thargoids replace pirates), `$30-$34`
supernova ("Fuel Leak", refugees, the sun approaches by an offset growing 100 per frame, cabin temperature rises), `$40-$41` Cougar with Asp Mk II escorts,
`$50-$53` Thargoid base briefing, invasion, reward. The ST source has the same design ("adapted from the MSX version"). The CPC's three missions are MSX/ST
missions 3 to 5 with different triggers (counter thresholds, not a queue). A wiki page quotes MSX triggers as kill scores (Constrictor at 175,455) and
rewards (500 Cr and a cloaking device for the Cougar) but says its FAQ numbers did not match experience, so the code is the better source.

### The eight missions

1-3 were in the CPC; 4-8 were candidates and are all built.

**1. Supernova rescue** (CPC, ST #3, MSX #3). Arrival hook `&4E58` (stage 1: low byte of `jumpCounter` >= 32, galaxy 2+); `Missionflag` bit 0 (stage) and 5
(refugees); `FlightMode` 1; `removeFuel` `&4EF4`; the Buy Cargo screen `&0840` replaced by the offer; every hyperspace key becomes a free galactic jump (`&4C6A`);
`SellGoods` `&0A40` pays; the escape pod clears the refugees; messages "FUEL LEAK!" and "MAYDAY! CORIOLIS IN DANGER!". Differences: the MSX makes the sun approach and
heats the cabin; the ST pays 1 kg of gems, the CPC rank +1 and gems.

**2. Cloaking device** (CPC, ST #4, MSX #4). Arrival hook stage 2 (>= 128, needs bit 0, sets bit 1); random encounters (`&8404`: random byte below 30/256 and
`Missionflag & &42 == 2`) spawn a special Asp Mk II with a marker flag; scooping cargo type `&FF` (`&3961`) sets bit 6, rank +1; `chkCloak` `&2017` and the `Y` key;
enemy aiming returns early; shut-off when energy bank 3 is below `&28`. The ST and MSX use a Cougar (own hull, 5,000 bounty = 500 Cr) with two Asp escorts; the CPC and
Spectrum use a marked Asp Mk II with 2-3 Sidewinder/Krait escorts and no bounty.

*Cougar and cloak compared (read 2026-11-07; ST = `work/ext_st/repo/src_orig/asm`; Spectrum = `work/ext_msx/skoolkit/src/elite.skool`; CPC = `src/elite/commonxx.asm`):*

| Step | Atari ST (states `$40`/`$41`) | CPC (and Spectrum) |
|---|---|---|
| Start | `new_mission` (`missions.m68:64`): galaxy 2+, no mission, `jump_count` (64 per mission) hits 0, `next_mission` 4 gives `$40` | `Missionflag` stage 2 on the 128th jump (`&4EDB`), no state byte |
| Briefing | next docking, `dock_check` at `$40` runs `warning4` (text21 "Warning to all Traders"); state `$41` | none |
| Spawn | `create_pirates` (deep space, fewer than 2 pirates) calls `pirate_attack`; at `$41`, only if no Cougar exists, creates a Cougar plus exactly 2 Asps | `spawnCommand0`: random below 30/256, `Missionflag & &42 == 2`, gate byte `aspMissionState` zero; gate := 1, spawns ship `&0D` (Asp), patch `dat_8427` sets bit 6 of `(ix+38)` (marker) and bit 2 of `(ix+32)`, then `jp &84E0` = `spawnEscortPack` (2-3 escorts; Spectrum `$BCAB`) |
| Hidden? | Cougar blinks invisible half the time (`vector.m68:151`), always ECMs missiles, ignores the energy bomb, cannot be collided with | while the gate is 1 the marked Asp is drawn as its laser only (Spectrum `$A7D9`; CPC `drawShipDistanceCheck`, the test just before it) |
| Gate states | none (state `$41` is the gate) | `aspMissionState` (Spectrum `$9CB2`): 1 spawned, 2 it has you lined up with the cloak off (`loc_884A`, back to 1 when the bearing grows), 3 shot down by the player's laser (`targetisKilled`), canister pending; 0 on hyperspace, ramming, or death by another route |
| Kill | `explode_object`, `release_cargo` (`orbit.m68:504`): blueprint `cargo_type` -1 releases one canister with cargo -1 | `targetisKilled`: marked Asp with gate 1 or 2 sets the gate to 3 and ejects a canister (action 6); cargo is not a blueprint field |
| Scoop | `salvage` (`flight.m68:1261`): scoop fitted, object ahead and below, negative cargo: `equip+cloaking_device`++, no rank change | `TryScoopGood`: scoop fitted; a plain canister with the gate at exactly 3 zeroes it and passes `&FF` to `storeScoopedGood` -> `chkCloakingDeviceScooped` (bit 6, rank +1, status shows "}" = Cloaking Device) |
| End | `remove_object` (`main.m68:405`) clears `mission` when a Cougar record is removed, scooped or not; `clear_objects` on hyperspace skips that hook, so `$41` survives a jump | bit 6 of `Missionflag` ends it: stage 2 fires once and spawning stops when bit 6 is set (the `&42` mask) |
| Use | `Y` (`action.m68:83`), `cloaking_toggle` (`main.m68:1044`); AI stops shooting (`combat.m68:1330`) | `Y`; `chkCloak` (`&2017`); aiming code returns early while active |

- The ST data is explicit (Cougar: 6 faces, 19 nodes, energy 1024, speed 30, 7 missiles, ECM, cargo -1, bounty 5000, kill rating 1000). The CPC and Spectrum reuse
  one shared byte as a state machine and mark the Asp by a flag; that byte also steers the Spectrum's energy-regeneration throttle (`$A2D8`) and the spawn throttle,
  so resetting it is a side effect of other code (which is why a scooped random canister at state 3 also gives the cloak).
- The CPC can lose the cloak by ramming or a non-laser kill (gate back to 0, spawns again later); the ST ends the mission at the first removal of the Cougar.
- Traced 2026-11-10 (`tools/test_cloak_asp.py`, stock code, Asp spawned ahead with the marker bit and `aspMissionState` = 1): the wireframe is not drawn in the front view, but the scanner still shows its blip, because `UpdateScanner` plots every slot in range with no marker test. So the Asp is hidden from the view, not from the radar.
- Read from source, not traced: the laser-only draw test and the "other route" reset (`aspGateClearIfBlueprint1E` guards state 3, `aspGateReset` clears 1/2).
- The MSX (`main-code.a99`, ricbit's `code.asm`) matches the ST: Cougar type `$1E`, flickering draw, `SCOOP_CLOAK_REWARD` (`$8BA6`) sets `CLOAK_FITTED`, `Y` toggles `CLOAK_ACTIVE`.

**Amtix's four missions** (Amtix 13, Pinto: "Supernova rescue, pirates taking over Space Station 1, the cloaking device and the ECM jammer which you use in the
Thargoid invasion bit"), matched to the code 2026-11-07: supernova = stage 1 (certain); "pirates taking over Space Station 1" = the Thargon invasion, stage 3 (likely);
cloaking device = stage 2, bit 6 (certain); ECM jammer = bit 7, given in the invasion briefing (certain). Why the takeover is the invasion and not a fifth mission:
no other mission exists in the CPC code (`Missionflag` bit 4 never touched, `ThargonMissionVar` holds 0-5, no extra story strings, nothing in Fessor's source); the
invasion target is the station of **system 0 of the current galaxy** ("Space Station 1"), and in the ST text it "has been captured"; the jammer is the invasion's tool,
so the scripted missions are three against the BBC disc's two; "SHIP BOARDED BY PIRATES" (`punishCheater`) fires at random stations with no story text and looks like a
leftover of the title/game-over path. A mission Torus switched off cannot be excluded; the dead-code survey (`_architecture.md`) did not look for a takeover state.

**3. Thargon invasion** (CPC, ST #5, MSX #5). Arrival hook stage 3 (>= 254, needs bit 1, sets bit 2 and `ThargonMissionVar` 1); `chkMissions` `&2063` states 1-5; planet
description override `&DE`; the station spawns Thargoids (state 4); the station kill adds `&FFFF` kill points and sets the station flag; `ThargonMissionFinished` `&49DB`
(rank +1, `Missionflag` bit 3, name FLORENCE); ECM jammer bit 7; game over on docking in state 4; target = system 0 of the galaxy. Oddity: the station-kill code does
`SET 3,(HL)` on `&3926` instead of `Missionflag`.

**4. Constrictor hunt** (BBC disc/Master/6502SP, Apple II, C64, NES, ST #1, MSX #1). Needs: docking hook, a mission state (the CPC had one free `Missionflag` bit; the chain needs about 4 bits plus a hint index), rank test (`killScoreHigh` is
the BBC `TALLY+1`) and galaxy 1 or 2, a docked description override for the hint chain, a galactic-hyperdrive check, ship table entry 19 and a blueprint (BBC-to-CPC hull
conversion), a spawn command with marker flag, tough-ship AI (only military lasers hurt it, ECM), kill hook, reward 5,000 Cr + `inc (killScoreHigh)`, about ten strings, a save byte. Any code
change breaks saves (`encryptSAV` keys on code), hence the unused save bytes. The ST/MSX variant visits five planets in turn, then attacks in deep space, reward 10,000 Cr.

**5. Thargoid plans / documents** (BBC disc family, Apple II, C64, NES; ST #2 and MSX #2 as "documents"). Needs mission 4's machinery (or the ST variant, which does not need the Constrictor):
rank test (>= 5), destinations (BBC: Ceerdi (215,84) then Birera (63,72); ST: the furthest planet found with `search`), a carried item (BBC plans, ST documents; the CPC hold has no
slot), the spawn rule (BBC: 22% of checks add a Thargoid and a Thargon; ST/MSX: Thargoids replace pirates), reward (BBC Navy Extra Energy Unit and 256 kill points; ST/MSX the military
energy unit): `extraEnergyUnit` `&3902`, `RechargeEnergy` `&3608`.

**6. Trumbles** (C64, NES only). Docking offer at enough cash; a 16-bit count in the save; breeding on arrival (`setShipvarsAtArrival`) and slowly in the main loop; the sun and
cabin-temperature code (heat kills them); the hold (they eat food, good 0, and narcotics, good 6); a sound; an inventory line; optionally software sprites in the off-screen bitmap.
No reward: a joke mission.

**7. Stolen police ship** (Elite Plus only). Offer at docking; `Missionflag` bit 4 or a state byte; target system by seed compare; one hostile Viper on arrival; kill hook;
reward 4,000 Cr; the legal-status code and `punishCheater`.

**8. Asteroid bombardment** (Elite Plus only). Offer at docking; a named system; asteroid spawning (`spawnCommand0` already spawns asteroids); reward 6,000 Cr.

**Order and trigger.** The ST/MSX start one mission per 64 jumps from a queue; the CPC fires its three at counter thresholds 32, 128, 254. The choice for the added missions is in
`docs/_missions_built.md`.

### Constrictor (BBC disc; Apple II the same)

- State is `TP` bits 0-1: `%00` not started, `%01` in progress (`BRIEF`), `%11` killed (`KILLSHP`), `%10` finished (`DEBRIEF`, which clears bit 0 and unlocks the next mission).
- Checked at every docking (`DOENTRY`): `TP` bits 0-1 `%00`, `TALLY+1 > 0` (256 kill points, rank Competent), galaxy **1 or 2**. Briefing: Captain Carruthers in galaxy 1,
  Fosdyke Smythe in galaxy 2.
- A chain of docked hints (capitalised overrides of the system description, shown only while in progress): Reesdice, Arexe (a galactic hyperdrive fitted and used), a galactic jump to
  galaxy 2, Cearso, Errius, Inbibe, Ausar, Usleri, and finally the ship waits in deep space at Orarra (near Usleri).
- Tough ship: only military lasers hurt it, it has an ECM. Reward 5,000 Cr and 256 kill points ("Right On Commander"). The blueprint lives in one data file (`D.MOG`) that `LOMOD` loads for the fight.

### Thargoid plans (BBC disc; Apple II the same)

- Needs the Constrictor finished (`TP` bits 0-3 `%0010`), galaxy **3**, `TALLY+1 >= 5` (3/8 of the way from Dangerous to Deadly).
- Stages: `%0110` briefed (Captain Fortesque: go to Ceerdi (215,84)); `%1010` plans on board (Agent Blake of Naval Intelligence at Ceerdi); `%1110` delivered at Birera (63,72).
- While the plans are on board, 22% of spawn checks add a Thargoid and a Thargon. Reward: a Navy Extra Energy Unit (recharges 3 per use instead of 2) and 256 kill points. On disc the
  Thargoid and Thargon blueprint files load while the plans are carried.

### Trumbles (C64 and NES), read from the C64 source (2026-11-07)

Source: Mark Moxon's annotated C64 code, https://github.com/markmoxon/elite-source-code-commodore-64 (`elite-source.asm`, `elite-data.asm`), browsable at https://elite.bbcelite.com/c64/;
copyrighted, read only. Pages read: `doentry`, `tbrief`, `solar`, `main_game_loop_part_5_of_6`, `main_flight_loop_part_15_of_16`, `mvtribs` and the sprite code. Behaviour only.

- Offered once cash is at least 5,017.6 Cr (the code tests `CASH+2 >= $C4`; the deep-dive page also says "`CASH+1 > 0`" and "6553.6", which disagree with the code: trust the code). The
  Merchant Prince of Thrun sells one Trumble for 5,000 Cr; `TP` bit 4 records the offer. They breed on every jump and slowly in flight, eat food (C64: and narcotics), die in the sun. The
  escape pod does not clear them: the original sets the count to a random 1-7 (NES source, `ESCAPE` part, "not a solution to the trouble with Trumbles"); our build zeroes it (`mxPodHook`).

| Piece | What the C64 does |
|---|---|
| Order in `DOENTRY` | Constrictor first (`TP` bits 0-1), then Plans (galaxy index 2, three stages), Trumbles last and only when nothing else fired: "first match wins" |
| Offer | `CASH+2 >= $C4` and `TP` bit 4 clear, then `TBRIEF`: set the bit, show token 199, Y/N; on Y pay 50,000 decicredits and set the count to 1 |
| Count | `TRIBBLE`, 16 bits kept positive (high byte clamped to `$7F`), saved with the commander |
| Breeding on arrival (`SOLAR`) | count not zero: zero the hold's food and narcotics; new count about `2 * ((count + random 0-15) OR 4)`, roughly doubling per jump up to the cap |
| Breeding in flight | only at 256 or more: 14% of passes (`random >= 220`) add one |
| Noise | at 256 or more, chance proportional to the high byte (halved when the cabin is cooler than 224), sound 14; pitch and length depend on cabin temperature |
| Sun | cabin temperature 240 or more: hide sprites 2-7 and halve the count (decays to zero); 224 or more still scoops fuel |
| Sprites (`MVTRIBS`) | once per main-loop pass one of up to six sprites moves (pass counter mod 8; none if at or above `TRIBCT`, 0-6); 8% chance (random >= 235) of a new velocity from a four-entry table (0, +1, -1, 0, separately for x and y); y wraps at 8 bits, x is 9 bits with carry in `VIC+$10`; a sprite leaving one side reappears on the other |
| Count to sprites | bits 4-6 of the count's high byte through the 8-entry `TRIBTA` (0-6; the first sprite shows at 4,096 Trumbles, the sixth at 20,480), `TRIBMA` gives the VIC enable mask |
| Shapes | `SPRITE.bin` 448 bytes = seven 64-byte hardware sprites (24 x 21 px): four laser sights, one explosion, two Trumble shapes (facing left/right, alternating); drawn double size, single colour, six different pen colours |
| Cost | the VIC draws them: no CPU cost; `MVTRIBS` is about 110 instructions; state is `TRIBCT` plus three 16-byte tables |

CPC consequences: the logic is small; hooks exist for each part (`chkMissions` offer, `setShipvarsAtArrival` breeding, main loop for slow breeding and noise, the sun code, `cargoHold` for eating,
the credits words for payment); the save block needed free bytes (`&38FD`, `&38FE`, `&3905`, `&3906`, see the built doc). The CPC has no hardware sprites (only the CPC+ ASIC: 16 of 16 x 16 pixels,
about 100 bytes of detection and unlock code, not worth it), so the sprites are software.

**Software sprites on the CPC.** The flight view is drawn into the linear off-screen bitmap `&A000-&BFFF` (Mode 1, 4 pixels per byte, 64 bytes per line, 256 pixels wide), which `ClearBitmap`
(`&1FF1`) wipes every frame and `transferBuffertoScreen` (`&1ED1`) copies to `&C000`. Drawing into it just before the single end-of-frame call needs **no erase and no screen-address maths**
(address = `&A000 + y*64 + x`). They appear only inside the 3D view (the dashboard is outside the bitmap). Six 16 x 12 blits cost about 10,000 T-states (2.5 ms of a 20 ms frame).

**Colours in the flight view** (read from the listing and checked in cpcxray 2026-11-07). Everything drawn through the off-screen bitmap (`Spaceflight`, title screen, hyperspace and witchspace
tunnel, docking, launch) runs with `Viewdirection` 0-3; views 4+ (charts, market, status) draw straight to the screen. In views 0-3 the ISR (`doColorSplit` -> `setDashboardInks`) sets the viewport pens at
the start of every frame. Hardware ink numbers (gate-array value minus `&40`):

| Case | pen 0 (background) | pen 1 | pen 2 | pen 3 |
|---|---|---|---|---|
| System, `presentSystemX & 7` = 0 | 3 | 4 | 20 | 23 |
| 1 | 10 | 22 | 20 | 12 |
| 2 | 12 | 24 | 20 | 29 |
| 3 | 7 | 0 | 20 | 11 |
| 4 | 3 | 28 | 20 | 21 |
| 5 | 19 | 21 | 20 | 14 |
| 6 | 11 | 23 | 20 | 12 |
| 7 | 10 | 30 | 20 | 2 |
| Supernova rescue (`FlightMode` 1) | 12 | 28 | 20 | 14 |
| Cloak active (wins over the two above) | 0 | 24 | 20 | 31 |

Check: from `firebird_in_flight.sna`, for each `presentSystemX & 7` I ran `setViewColors` (`&4D2B`), stopped at `&28B4` (end of the viewport ink setting) and read the gate-array palette: all eight rows
match, as do `FlightMode` 1, the cloak flag (also with `FlightMode` 1) and `Viewdirection` 1-3; `Viewdirection` 4 gives 4/31/18/14. With `counter_colorsetting` (`&2854`) at `&18`, pen 2 alternates 20 and 13
each frame (read at `&28D8`). Not tested: the pen 3 flicker during explosions. The per-system row comes from `tableSystemColors` (three bytes per system: pen 3, pen 0, pen 1), copied by
`setViewColors` into `smc_patchviewPortInk3/0/1`; it runs in `setupNewGame` and `generateTargetSystemParAtHyperjump`.
- **Pen 2 is the only fixed pen**: `&54` = ink 20 (black) in views 0-3. Exception: the energy bomb flashes it between `&54` and `&4D` (ink 13) for `&18` frames (`counter_colorsetting`,
  `flag_color0alternating`; it flashes the border too). `changeInks2and3` runs only for views 4+.
- Pens 0, 1, 3 change with the system, supernova mode and cloak. Pen 3 is set to `&4E` (ink 14) while explosions are drawn (`todoDrawExplosions` saves the old value in `CirclePixelMask`), so a pen-3
  sprite can flicker orange.
- In every case the four pens are four different inks, and black never appears as pen 0. So a body in pen 2 (black) plus an eye in pen 1 or 3 is the safe two-pen design; check the eye's contrast on a few systems.

## 2. What the CPC already had that the port reuses

| Need | CPC mechanism |
|---|---|
| Docking hook (`DOENTRY` equivalent) | `chkMissions` at `&2063`, called from the docking code |
| Arrival hook | `&4E58` after every hyperspace arrival; counts jumps in `jumpCounter` (`&38DA`) from galaxy 2 on |
| Rank tests | `killScoreHigh` (`&38D9`) **is** the BBC `TALLY+1` (the rank table `RankingBytes2` = `02,0A,19,FF` is the BBC high-byte table, Elite at `&19`); `killScore` low bytes are `TALLY` (`getRank`) |
| "256 kill points" reward | `inc (killScoreHigh)`, as the supernova and cloak rewards do (`AddDEtoKillScore`) |
| Credits reward | `getMoney` / `getBounty` |
| Story screens | `drawFlipChart` full-screen text, flight messages, `stringsTable2` (`&0FCA`, indexes to `&E0`) |
| Docked description override | the invasion replaces a planet description with `<planet> IS RESISTING A THARGON INVASION` (`&DE`) |
| Thargoid and Thargon models, spawn commands | ship table entries 15, 16; `spawnCommand1` (up to four Thargoids), `spawnCommand4` |
| Special ship with marker flag | the cloaking-device Asp (`&8404`) |
| Equipment flag for the reward | `extraEnergyUnit` (`&3902`), `RechargeEnergy` (`&3608`) |

## 3. Findings kept from the planning

- **Free space (measured 2026-11-07, cpcxray):** `loadLARGEAXX` (called at every docking just before `chkMissions`) parks `&0040-&1A3F` at `&A600` and reloads `LARGEAXX.BIN` (`&0840`, `&1200` bytes), so the zero tail
  `&1714-&1A3F` (812 bytes) is fresh at each docking and nothing in the sources addresses it. In flight the range holds the parked data (not a disk file, see `_memory_map.md`) (0 reads and writes in 30 s); the docked copy is swapped out to `&A600` at launch and lost to the bitmap (`_memory_map.md`). At the title screen `LARGEAXX`
  is already parked, so docked-only code is valid only after `loadLARGEAXX`. `chkMissions` has a single call site, the docking sequence. Flight-time parts need the 610 bytes at the end of `COMMONXX`
  (its top bytes carry stack pushes at `&A000`); `&A000-&A5FF` is the off-screen buffer in flight, not free. Dead code gives only about 10 bytes (`_architecture.md`).
- **Strings:** `printStringA` takes an 8-bit index and `stringsTable2` already has 254 strings, so a small entry point sets `HL` to a table of our own and reuses the token loop; tokens may still reference
  `stringsTable2` strings `&81-&D6` and the digrams. Re-encoding both stock tables optimally saves only 48 of 2,822 bytes (`tools/textcomp.py`).
- **Gating and slots.** CPC missions run on `jumpCounter`, counted only from galaxy 2 on; the BBC Constrictor is offered in galaxy 1 or 2 and the plans need galaxy 3. The invasion is offered at jump 254 in any galaxy 2-8, so the
  stub lets the stock offers go first. The supernova and invasion react to galactic jumps, so added state stays out of `ThargonMissionVar`. The CPC has 6 entity slots (3 reserved): spawn special ships alone. The invasion gives rank +1 and
  the title ARCHANGEL (`Missionflag` bit 3); new rewards use `inc (killScoreHigh)`. Saves are XORed with the game's code at `EquipShip`, so changing that code invalidates old saves; the added missions use only unused save bytes.
- **The ten system names (answered 2026-11-07):** generated from the CPC's digram table (`DockedDigrams`, index 0 skipped, `?` drops the second letter) and the BBC seed twist (`waggle_galaxy`, four twists per name; a galaxy hop rotates
  every seed byte left by one), after checking it reproduces Tibedied (galaxy 1 system 0), Lave (7) and Diso (147). All ten exist exactly once, in the galaxy the chain needs: galaxy 1 Arexe (system 28, x/y 164,89) and Reesdice (36; 149,101);
  galaxy 2 Ausar (53; 146,102), Cearso (68; 87,109), Inbibe (79; 152,146), Usleri (118; 148,68), Orarra (193; 144,33), Errius (253; 184,149); galaxy 3 Birera (36; 63,72), Ceerdi (83; 215,84). Ceerdi and Birera match the BBC coordinates;
  Orarra is about 7 LY from Usleri.
- **The spawn rule (answered 2026-11-07):** the CPC counterpart of the BBC main-loop spawn is `handleEntitys`: every frame it counts down `todoLaserVar2`; at 0, with no station near, no launch running and fewer than 4
  station-launched ships, it calls `spawnCommandParser` with action 0 = `spawnCommand0`. That rolls a random byte minus the contraband weight C: below zero picks a hostile (`cmd0ChkSendHostileAfterUs`), `&50-&59` an asteroid, `&5A`+ nothing.
  The mission spawn checks hook in at its top. The invasion already forces a Thargoid there when `ThargonMissionVar` is 4.
- **The escape pod (answered 2026-11-07):** a bug that affects no reward. `cargoHold` is `&38E2-&38F2` (17 goods), but the pod clear (`mleCleanInvLoop`) clears 17 bytes from `&38E1`, wiping `&38E1` (the market random byte) and goods 0-15
  and **keeping alien items (good 16, `&38F2`)**; `cargoSpaceFree` is reset to the full capacity, so a pilot who ejects with alien items can hold more than the capacity. Fix: start the loop at `&38E2` (`ld hl,cargoHold`); applied under `-DENHANCED` in all three trees (`podCleanOperand`), the default build keeps the original bytes.
- Not planned: Elite-A delivery missions, the Apple II's graphics, music. The BBC code is under Mark Moxon's annotations: behaviour only, the Z80 is written fresh. Builds start from the Firebird or German cracked disks, not the protected original.

## 4. Elite Plus

The ST source (adapted from the MSX version) has five missions in a fixed order every 64 jumps: Constrictor, Thargoid documents, refugees, the Cougar, the invasion. Only Elite Plus (PC) adds **Stolen Police Ship** (4,000 Cr) and
Asteroid Bombardment (6,000 Cr); no code for either is in the ST or NES source. Player reports are thin: a stolen police Viper with a new paint job, hunted in a named system, offered on docking, one mission at a time, players disagree on
whether it is fully implemented ([AFE FAQ2](https://wiki.alioth.net/index.php/AFE_FAQ2), [guide](https://www.tales-from-darkenedroom.com/post/elite-plus-missions-galaxy-9)). No public Elite Plus source exists (Chris Sawyer's PC assembly); the
[Frontier thread](https://forums.frontier.co.uk/threads/elite-plus.70102/) and savegame-editor notes list the mission as code 04. Triggered by a hyperspace counter after leaving galaxy 1, one at a time, the Viper gives no bounty and shooting it
may count as an offence. So the EXE was unpacked and read.

### Elite Plus code (disassembled 2026-11-07)

Source: `work/elite plus/ELITE.EXE` (EXEPACK, "hacked version of PC Elite +"; `tools/unexepack.py`; 16-bit x86, DS base = image `0xB000`). Addresses are image offsets, data is `DS:off`. Read statically with capstone, nothing was run;
the mission code looks original, but the hack is unexamined.

- **Variables:** `DS:83A0` mission number (0 none, 1-6), `83A2` state, `83A3` target system (seed byte, compared with `8329` = current system), `839E` jump counter (saturates at 255), `83B0`/`83B1` offer-pending flags, `836B` legal status, `836C` kill counter.
- **Trigger (`0x7595`):** every jump increments `839E`; at `0x20, 0x38, 0x50, 0x6E, 0x8C, 0xA0` (32, 56, 80, 110, 140, 160) the mission number becomes 1-6 and the state is cleared, but only while no mission runs. **Number 4 (110 jumps) is the stolen
  police ship, 5 (140) the Thargoid plans (debrief pays 5,000 Cr), 6 (160) the asteroid bombardment (6,000 Cr)**; see the table below. This is the ST rule with a one-byte counter.
- **Offer (`0x99DC`, at docking):** twists the galaxy seed (`0x205-0x20B`) until the system byte differs from the current one, stores it in `83A3`, sets state 1, prints the text with the system name. Mission 4 has **no Y/N prompt**, only "press any key".
- **Arrival (`0x7543`):** states 1/2 are re-evaluated each jump: 2 if the new system's byte equals `83A3`, else 1.
- **Spawn (`0x7AD3`):** state 2 only. Needs free ship slots, scans for an existing ship with id `0x39` and `[+0x25]==1` (only one), then a roll (`rand <= 400` of 65536 per check), and spawns blueprint entry `DS:87C5`, **the same entry the police
  spawn uses** (`0x7A50`, from the wanted-level code at `0x8416`): the police Viper. Differences: aggression `[+0x33]` = 5 instead of 4 (that 5 means "hostile" is inferred), energy `[+0x30]` = `0xC8` instead of `0x64`, marker `[+0x25]` = 1.
- **Kill (`0xAD4F`):** state 2 and `[+0x25]==1`: state := 3, flash "Stolen Viper Destroyed!" (`DS:AED8`), bump the kill counter.
- **Reward (`0x9C4A`, next docking):** state 3 shows the debrief and adds `0x9C40` = 40000 decicredits = **4,000 Cr** (call `0x8E3C`), clears `83A0` and `83B0`. A failed hunt just waits: leaving the system drops state 2 back to 1.

**Legal status, Elite Plus vs the CPC** (static):
- CPC: any destroyed ship whose flag byte `ix+33` has bit 5 or 6 set (innocent or police) does `legalStatus |= 0x40`, fugitive at once (after `AddDEtoKillScore`); the stolen Viper would trigger it unless its flags are cleared.
- Plus: no OR with 64. A kill adds to `DS:836B` only in `0xAE08`: +4 for a police Viper (blueprint `87C5`, id `0x1C`) whose word `[+0x3A]` is 1, +2 for any other ship when `DS:7680` bit 0 is set, otherwise nothing. The marked Viper has bounty byte
  `0xFF` (variable) and only id `0x16` pays (500 = 50 Cr, `0xADEC`), so it pays nothing: the forum's "no bounty". Other offences: +40 for a missile hitting a station or planet (`0xACA6`), +5 for lasers on a station (`0x83B1`), +10 or +40 when a police
  Viper (`[+0x3A]==1`, `0x827E`) witnesses an attack (`0x84B0`).
- The police Viper spawn sets `[+0x3A]=1` (`0x7A5C`); the mission spawn (`0x7B1B`) does not, and skips the slot-clearing routine `0x81B7`, so whether the marked Viper counts as police for witnesses depends on stale slot data (unresolved).
- For the CPC: give the marked Viper flag bits that make `ix+33 & 0x60` zero (neither innocent nor police), so the kill costs nothing.

**Online (2026-11-07):** [rembish/elite-plus-revamp](https://github.com/rembish/elite-plus-revamp) is a work-in-progress decompilation ("V3.1 August 1990"); no official source. The Frontier thread has an EXE hex patch (`3D 2C 01` -> `90 90 F9`), an "Archangel"
difficulty mode and a lower Elite kill count, and lists a masking device and a stolen-plans mission. The [VOGONS savegame thread](https://www.vogons.org/viewtopic.php?t=64736) lists a savegame flag that activates special missions and a Thargoid Base mission
(not checked). `3D 2C 01` occurs three times (`0x7455`, `0x7B51`, `0x82DF`, all `cmp ax,0x12C` after a random call, 300/65536): `0x7455` is the galactic jump (after galaxy 8 a 300/65536 roll keeps the ninth galaxy, otherwise it wraps to 0; `stc` makes it
certain; likely, not proven, to be the patched one), `0x7B51` the mission-6 Viper spawn roll, `0x82DF` a per-tick Cobra-class roll.

### Unconfirmed features, checked (2026-11-10)

Source of the claims: [AFE FAQ2](https://wiki.alioth.net/index.php/AFE_FAQ2) (sections 2.1, 2.2.2, 2.2.3, 2.4).

- **9th galaxy in Elite Plus: confirmed in the EXE, and it is reachable.** The string `Welcome to the 9th Galaxy!` is at `DS:829D` and is chosen at `0x73DD` when the galaxy byte `DS:8315` is 8 (after a galactic jump, flag `DS:AE24`).
  The jump routine `0x7439`: at 8 it wraps to 0; otherwise it increments, and when the new value is 8 it calls the random routine and keeps 8 only if `ax < 0x12C` (300 of 65536, about 0.46 % per jump from galaxy 8), else wraps to 0.
  The wiki's "no-one has found a way" is therefore a probability, not a missing path, unless the hacked EXE differs from the original (unexamined); the forum hex patch `3D 2C 01` -> `90 90 F9` (carry set) makes it certain. The digit shown is `'1' + galaxy`, so a '9' is printed.
- **ArcElite also has nine galaxy names** (index 8 "Trojane"; `docs/_arcelite.md`); how that index is reached was not found.
- **Generation ships, dredgers:** the wiki gives the Space Trader's manual (p. 30, "more than seventy thousand") and a rumour that Ian Bell said none were ever implemented; for dredgers "no confirmed sightings". Our check: no string `generation`, `dredger`, `carrier` or `destroyer` in the CPC
  binaries (English, German), the Elite Plus image (its ship list: Dodo, Coriolis, Boa, Anaconda, Cobra Mk I, Asteroid, Boulder, Thargon, Shuttle, Transporter, Worm, Splinter, Plate, Gecko, Moray, Adder, Mamba, Cargo Canister, Constrictor,
  Cougar, Missile, Escape Pod, Thargoid, Ferdelance, Asp, Sidewinder, Cobra Mk III, Krait, Viper, Python) or ArcElite, and none in the cloned ST/Amiga, NES, MSX and C64 trees. So the claim holds for those builds; it says nothing about builds we do not have. The wiki's ArcElite "mystery ship" is held to be the Urutu (not checked).
- **Elite A destroyer and battle carrier:** Mark Moxon's annotated Elite-A source ([repo](https://github.com/markmoxon/elite-a-source-code-bbc-micro), cloned to `work/ext_elitea/repo`) has no string or blueprint named destroyer or carrier. Its 37 ship blueprints (plus the missile) are the classic ones plus Adder, Bushmaster, Chameleon, Dragon,
  Ghavial, Iguana, Monitor, Ophidian, Rattler, Shuttle Mk II and Asp Mk II (no Dredger, no generation ship). So the "destroyer under test" and "battle carrier" are hints in the printed documentation only, not ships in the code; the wiki guesses the destroyer is the Constrictor.

### Elite Plus missions 4, 5 and 6, read again (2026-11-08, static)

Method: capstone on `work/elite plus/extracted/ELITE.img`, every `cmp byte [0x83A0],n` site, offer (`0x98EB`), debrief (`0x9AC4`), spawn (`0x7A66-0x7C8F`), kill (`0xAD4F`). Offer texts: 4 "stolen by Thargoid infiltrators", 5 "plans for a new Thargoid invasion
ship", 6 "bombarded by large rocks and asteroids". `83B0` = 1 once the offer is shown (it runs when `83B0` is 0 at docking, `0x8C17-0x8C1E`) and returns to 0 with `83A0` when the debrief is paid.

| | 4 Stolen police ship | 5 Thargoid plans | 6 Asteroid bombardment |
|---|---|---|---|
| Jump counter | 110 | 140 | 160 |
| Target `83A3` | seed twist, must differ from here | same | same |
| State `83A2` | 1 hunting, 2 in target system, 3 killed | not used | counter, set to `0x32` (50) at the offer |
| In flight | one marked police Viper (above) | `0x7A66`: `83B0` = 1, 60/65536 per check, only with no hostile around (`0x8736` = 0): a Thargoid (type `0x16`, row `0x8847`), aggression 5, an ambush not tied to a system | `0x7B32`: only in the target system, state above 1: 5000/65536 per check spawns an **Asteroid** (type 5, row `0x876B`; aggression 3, marker `[+0x25]` = 2, placed by `0x7E32`); with a roll of 300 or less a **Cobra Mk III** (type `0x1A`, row `0x8815`; aggression 5, `0x7C59`) |
| Kill (`0xAD4F`) | marked ship: state 3, "Stolen Viper Destroyed!" | none | marked ship (`[+0x25]` = 2): state minus 1, down to 1 |
| End | dock anywhere: 4,000 Cr | dock **in the target system**: 5,000 Cr (`0xC350`) | state equals 1, dock anywhere: 6,000 Cr (`0xEA60`) |

Notes: (a) the Plus missions not in any other port are 4 and 6; 5 is the BBC plans mission with an ambush. (b) No failure path for 6: leaving the system just stops the spawning, the counter stays. (c) The Plus "masking device" mission is the cloaking-device
mission the CPC already has. (d) Blueprint rows are 10 bytes; byte 0 is the ship type indexing the name list at `DS:80E9` (0 Dodo, 1 Coriolis, 2 Boa, 3 Anaconda, 4 Cobra Mk I, 5 Asteroid, 6 Boulder, 7 Thargon, 8 Shuttle, ... `0x11` Cargo Canister, `0x12` Constrictor,
`0x13` Cougar, `0x14` Missile, `0x15` Escape Pod, `0x16` Thargoid, `0x17` Fer-de-lance, `0x18` Asp, `0x19` Sidewinder, `0x1A` Cobra Mk III, `0x1B` Krait, `0x1C` Viper, `0x1D` Python): the stolen ship is a Viper (row `0x87C5`, the police Viper; only aggression 5, energy
`0xC8` and the marker change), the rocks are Asteroids with an occasional Cobra Mk III, mission 5's ambush is a Thargoid. (e) The `[+0x25]` marker byte does not exist in the CPC ship record; the build uses a flag pattern instead (a police Viper has bits 1 and 6 of `(ix+33)` set from
blueprint byte 18, the stolen one has both clear, which also answers the legal-status question: the CPC kill code only tests bits 5 and 6 of `ix+33`). The asteroid mission counts asteroid kills at the target with no marker.

CPC consequence (built, `docs/_missions_built.md`): a state byte instead of a `Missionflag` bit, no Y/N prompt, a flag-pattern marker for the Viper, the jump wait before the offer.

## 5. ArcElite (Acorn Archimedes, 1991)

The Archimedes version has four missions of its own: none is a Constrictor, plans (as in the 6502 versions), Trumbles, supernova or Elite Plus mission, and no other port has them. No source is public; the game was unpacked and read in 2026-11
(method, files and global variables: `docs/_arcelite.md`). Values are from the code, checked against the [wiki](https://wiki.alioth.net/index.php/ArcElite_missions) (one difference: mission 1 starts at 450 kills, not 550).

| ArcElite | Start | Reward |
|---|---|---|
| Genesis capsule: Razaar (167), Ordima (236), drop low over Xeaan (80) | galaxy 1, kills > 450, cash > 1200 Cr | 500 Cr |
| Zartid (MTA) hunt ("running plans to Thargoids"): system 116, Mamba convoy, fails after about 20 docks | kills > 1450, cash > 4000 Cr | yaw boosters, offences cleared |
| Zurid Pino: stolen MisLoc and stealth Cobra, ten taunts | kills > 2600 (second message > 2650) | MisLoc missile system |
| Groigan disease: four compounds from systems 170-173, mix at 174 | galaxy index > 4 (galaxies 6-9), kills > 4600, offences < 1000, system mod 3 = 1 | 2000 Cr |

Design points: mission state is one word per mission (`88888` failed, `99999` done, -999..-995 pending outcome codes written by the destroy handler or the jettison code, small positive values as progress bits); a single scheduler runs on
every dock and returns 1 when it showed a message; chatter lines are random per dock and shown once each (a separate bit array); the kill thresholds sit in the rating bands. The Zartid mission is the nearest relative of the 6502 plans mission
(a despot flying plans to the Thargoids), and the Pino hunt of the CPC stolen police ship (a marked ship that must be killed). ArcElite has nine galaxy names (index 8, "Trojane"); see `docs/_arcelite.md`. The ArcElite set is unrelated to the set built here (`docs/_missions_built.md`).

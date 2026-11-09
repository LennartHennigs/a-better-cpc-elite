# Missions: research notes

**Status (2026-11-08):** the Constrictor, the Thargoid plans, the Trumbles and the two Elite Plus missions (stolen police ship, asteroid bombardment) are implemented; what was built, its order, triggers, sizes and tests are in `docs/_missions_built.md`.
This file keeps the research behind them: what the other versions do, what the CPC already had, source readings (BBC, C64, Apple II, Atari ST, MSX, Elite Plus), findings from the planning and the open questions that were answered. Facts about the
CPC come from `docs/_gameplay.md`, `docs/_savegame.md` and `src/elite/`; facts about the 6502 versions come from Mark Moxon's annotated BBC code (https://elite.bbcelite.com/deep_dives/, pages "The Constrictor mission", "The Thargoid Plans mission",
"The Trumbles mission", fetched 2026-11-07) and Andy McFadden's Apple II disassembly (https://6502disassembly.com/a2-elite/Elite.html). Anything marked *estimate* or *to check* is not verified.

## 1. What the other versions have

How each row was established: BBC cassette and Electron from Moxon's Constrictor page ("no missions"); BBC disc, Apple II, C64 and NES
from annotated source (the NES `TP` byte has exactly three fields); Atari ST from `missions.m68`; MSX from the TI-99/4A conversion of
the MSX code, whose comments document the five mission states; Elite Plus and the CPC rows as noted. "wiki" means only a forum or wiki
list, not code. Links in `docs/_references.md`.

| Mission | BBC cassette, Electron | BBC disc, 6502SP, Master | Apple II | C64 | NES | Atari ST, Amiga | MSX | CPC today | Elite Plus (PC) |
|---|---|---|---|---|---|---|---|---|---|
| Constrictor hunt | no | yes | yes (hint text and hull present) | yes | yes | yes (#1) | yes (#1) | no | wiki: replaced by others in some lists |
| Thargoid plans / documents | no | yes | yes (briefing text present) | yes | yes | yes (#2) | yes (#2) | no | wiki: yes |
| Trumbles | no | no | no | yes | yes | no | no | no | wiki: yes |
| Supernova (refugees) | no | no | no | no | no | yes (#3) | yes (#3, "Fuel Leak", sun approaches) | **yes** | wiki: yes |
| Cloaking device (Cougar, Asp Mk II escorts) | no | no | no | no | no | yes (#4, Cougar warning) | yes (#4, Cougar with Asp escorts) | **yes** (special Asp) | wiki: yes (masking device) |
| Thargoid invasion (ECM jammer) | no | no | no | no | no | yes (#5) | yes (#5) | **yes** | wiki: yes |
| Stolen police ship | no | no | no | no | no | no | no | no | wiki: yes (4,000 Cr) |
| Asteroid bombardment | no | no | no | no | no | no | no | no | wiki: yes (6,000 Cr) |

MSX details (state table in the TI-99/4A source, `src/main-code.a99`, from the MSX disassembly): five missions, started in order by
`next_mission` (1-5, 6 = all done), when `jumps_to_next_mission` reaches 0; it is counted down on every hyperspace jump **outside the
first galaxy** while no mission is under way, and reset to 64. The state byte's high nibble is the mission, the low nibble the
progress: `$10-$19` Constrictor (a five-system trail, reward on docking), `$20-$21` documents (Thargoids replace pirates on the way),
`$30-$34` supernova ("Fuel Leak" on arrival, refugees, the sun approaches by an offset growing 100 per frame, cabin temperature
rises), `$40-$41` the Cougar with Asp Mk II escorts, `$50-$53` Thargoid base briefing, invasion, reward. The ST source is the same
design (it says "adapted from the MSX version"). So the CPC's three missions are the MSX/ST missions 3 to 5, with a different
trigger (counter thresholds, not a queue). A wiki page quotes MSX trigger values as kill scores (for example the Constrictor at 175,455
points) and rewards (500 c and a cloaking device for the Cougar); the same page says the FAQ's numbers did not match its author's
experience, so the code is the better source.

The Apple II is a BBC-disc derivative: same two missions, same `TP` bit layout, no extras. So there are three
candidate missions, and only two come from both 6502 families. Elite-A's generated delivery missions are a
different game and out of scope.

### The missions, numbered, with systems and changes

Eight missions exist across the versions. 1 to 3 were already in the CPC; 4 to 8 were candidates and are all built now except where noted (`docs/_missions_built.md`). "Systems" are the parts of the
game a mission touches (CPC names and addresses from `docs/_gameplay.md`, `docs/_savegame.md` and `src/elite/`); "Changes" is what
the CPC code or data needs. Byte counts are *estimates* unless stated. The subsections after this list hold the source reading.

**1. Supernova rescue** (CPC, Atari ST #3, MSX #3)
- *Systems:* arrival hook `&4E58` (stage 1, low byte of `jumpCounter` `>= 32`, galaxy 2 and later); `Missionflag` bit 0 (stage) and
  bit 5 (refugees); `FlightMode` 1; `removeFuel` `&4EF4`; the Buy Cargo screen `&0840` replaced by the offer; every hyperspace key
  becomes a free galactic jump (`&4C6A`); `SellGoods` `&0A40` pays; the escape pod clears the refugees; the in-flight messages "FUEL
  LEAK!" and "MAYDAY! CORIOLIS IN DANGER!".
- *Changes:* none, it works. Differences to copy if wanted: the MSX makes the sun approach (an offset that grows by 100 per frame) and
  heats the cabin while the state lasts; the ST pays 1 kg of gem-stones, the CPC rank +1 and gems.

**2. Cloaking device** (CPC, Atari ST #4, MSX #4)
- *Systems:* arrival hook stage 2 (`>= 128`, needs bit 0, sets bit 1); random encounters (`&8404`, a random byte below 30 of 256 and
  `Missionflag & &42 == 2`) spawn a special Asp Mk II with a marker flag; scooping cargo type `&FF` (`&3961`) sets bit 6, rank +1;
  `chkCloak` `&2017` and the `Y` key; enemy aiming returns early; dashboard colours; shut-off when energy bank 3 is below `&28`.
- *Changes:* none to the CPC mechanism (read in detail below). The ST and MSX use a Cougar (its own hull, 5,000 bounty = 500 Cr) with
  two Asp escorts; the CPC and the Spectrum use a marked Asp Mk II with 2 or 3 Sidewinder/Krait escorts and no bounty. `CHEAT` can
  start with the device owned.

*Cougar and cloaking device, compared (read 2026-11-07; ST = `work/ext_st/repo/src_orig/asm`, the preserved original, `src_atari` is a
modified build; Spectrum = `work/ext_msx/skoolkit/src/elite.skool`; CPC = `src/elite/commonxx.asm`):*

| Step | Atari ST (states `$40`/`$41`) | CPC (and Spectrum) |
|---|---|---|
| Start | `new_mission` (`missions.m68:64`): galaxy 2+, no mission, `jump_count` (64 per mission) hits 0, `next_mission` 4 gives state `$40` | `Missionflag` stage 2 on the 128th jump (`&4EDB`), no state byte |
| Briefing | next docking, `dock_check` at `$40` runs `warning4`: text21 "Warning to all Traders", unknown hostile ship with a device that makes on-board computers malfunction; state becomes `$41` | none |
| Spawn | `create_pirates` (deep space only, fewer than 2 pirates, the pirate counter) calls `pirate_attack`; at `$41`, and only if no Cougar exists, it creates a Cougar plus exactly 2 Asps in the squadron positions | `spawnCommand0`: random below 30/256, `Missionflag & &42 == 2`, gate byte `aspMissionState` zero; sets the gate to 1, spawns ship `&0D` (Asp), patch `dat_8427` sets bit 6 of `(ix+38)` (marker) and bit 2 of `(ix+32)`, then `jp &84E0` = `spawnEscortPack`, the 2-3 escort pack (Sidewinder or Krait, per the Spectrum disassembly `$BCAB`) |
| Hidden? | Cougar blinks invisible half the time (`vector.m68:151`) and is not drawn on radar then; always ECMs missiles; ignores the energy bomb; the player cannot collide with it | while the gate byte is 1 the marked Asp is drawn as its laser only, not the wireframe (Spectrum comment at `$A7D9`; CPC `drawShipDistanceCheck`, the test just before it); ordinary Asp otherwise |
| Gate states | none (the mission state `$41` is the gate) | `aspMissionState` = Spectrum `$9CB2`: 1 spawned, 2 it has you lined up with the cloak off (set in the aiming code at `loc_884A`, back to 1 when the bearing grows), 3 the marked Asp was shot down by the player's laser (`targetisKilled`) and a canister is pending, 0 reset on hyperspace arrival/jump, on ramming it, or when it dies by another route |
| Kill | `explode_object`, `release_cargo` (`orbit.m68:504`): blueprint `cargo_type` is -1, so exactly one canister is released whose cargo is -1 (not the random 0-7) | `targetisKilled`: marked Asp with gate 1 or 2 sets the gate to 3 and ejects a canister (action 6); the cargo is *not* a blueprint field |
| Scoop | `salvage` (`flight.m68:1261`): fuel scoop fitted, object ahead and below, `cargo_type` negative: `equip+cloaking_device` incremented, no rank change | `TryScoopGood` (`fsGetRandomGood`): fuel scoop fitted; a plain canister (blueprint nibble 0) with the gate at exactly 3 zeroes the gate and passes `&FF` to `storeScoopedGood`, which calls `chkCloakingDeviceScooped` (`Missionflag` bit 6, rank +1, status shows "}" = Cloaking Device) |
| End | `remove_object` (`main.m68:405`): whenever a record of type Cougar is removed (killed, then cleaned up), `mission` is cleared, whether or not the canister is scooped. `clear_objects` on hyperspace zeroes the records without that hook, so `$41` survives a jump and a new Cougar can appear in the next system | bit 6 of `Missionflag` is the end: the 128-th-jump stage fires once, and spawning stops when bit 6 is set (the `&42` mask) |
| Use | `Y` (`action.m68:83`), `cloaking_toggle` (`main.m68:1044`): needs the device, flips `cloaking_on`; AI stops shooting at you (`combat.m68:1330`) | `Y`; `chkCloak` (`&2017`); aiming code returns early while active |

Reading notes:
- The ST data is explicit (Cougar blueprint line in `objects.dat`: 6 faces, 19 nodes, energy 1024, speed 30, 7 missiles, ECM, cargo -1,
  1 canister, bounty 5000, kill rating 1000); the CPC and Spectrum reuse one shared byte as a state machine and mark the Asp by a flag, so
  that byte also steers the Spectrum's energy regeneration throttle (`$A2D8`, 2/1 hysteresis) and the spawn throttle. Resetting it is a
  side effect of other code, which is why a scooped random canister at state 3 also gives the cloak.
- The CPC differs from the ST in that the cloak can be lost by ramming or by a non-laser kill (gate back to 0, spawn again later) and
  it needs bit 6 clear to keep spawning; the ST ends the mission on the first removal of the Cougar.
- Read from source, not yet traced in an emulator: the laser-only draw test (the 5 instructions before `drawShipDistanceCheck`) and the reset on the "other route" (`aspGateClearIfBlueprint1E` guards state 3, `aspGateReset` clears 1/2).
- The MSX (TI-99 `main-code.a99`, ricbit's `code.asm`) matches the ST: Cougar ship type `$1E`, flickering draw, `SCOOP_CLOAK_REWARD`
  (`$8BA6`) sets `CLOAK_FITTED` when the canister's cargo byte is negative, `Y` toggles `CLOAK_ACTIVE`.

**Amtix's four missions matched to the code** (Amtix 13, Ricardo Pinto: "Supernova rescue, pirates taking over Space Station 1, the cloaking device and the ECM jammer which you use in the Thargoid invasion bit"; checked 2026-11-07):

| Amtix | Code | Confidence |
|---|---|---|
| Supernova rescue | stage 1, `Missionflag` bits 0 and 5, `FlightMode` 1 | certain |
| "Pirates taking over Space Station 1" | the Thargon invasion (stage 3, `ThargonMissionVar` 1-5): the Thargons take over a station; it turns hostile and launches Thargoids | likely, see below |
| Cloaking device | stage 2, bit 6 | certain |
| ECM jammer | bit 7, given in the invasion briefing and used there | certain |

Why the station takeover is the invasion and not a fifth mission:
- No other mission exists in the CPC code: `Missionflag` bit 4 is never touched, `ThargonMissionVar` only holds 0-5, no extra story strings
  (every `drawFlipChart` caller is accounted for, `docs/_gameplay.md`), and no mission wording in Fessor's source either (grep for
  takeover, hijack, occupied finds nothing).
- The invasion target is the station of **system 0 of the current galaxy**, the first system the galaxy generator makes: "Space
  Station 1" fits the station of the first system. In the ST text (`missions.m68`, text13) the station "has been captured" and becomes
  the Thargoid headquarters, so a loose "taking over a station" is a fair description; "pirates" is Pinto's shorthand for hostile
  invaders, or a slip, as Amtix's wording is from memory in an interview.
- The count of four is two missions plus gadgets: the jammer is the invasion's reward/tool (Pinto says so himself), so the shipped
  scripted missions are three (supernova, cloaking device, invasion), against the BBC disc's two. The ST and MSX add two more
  (Constrictor, documents) that the CPC lacks.
- Not the same thing: the hidden "SHIP BOARDED BY PIRATES" hazard (`punishCheater`, `docs/_gameplay.md`). It fires after docking at
  random stations, not at a named one, and has no story text; the Spectrum disassembly calls the flag it tests the "demo ship" bit, so it
  looks like a leftover of the title/game-over path rather than a mission.
- Still open: a mission that Torus planned and switched off (Pinto: "huge chunks of the program just sitting there unused") cannot be
  excluded, but the dead-code survey in `docs/_architecture.md` (about 0.15 KB of unreachable code) did not look for one specifically; I have not checked it for a station-takeover state.

**3. Thargon invasion** (CPC, Atari ST #5, MSX #5)
- *Systems:* arrival hook stage 3 (`>= 254`, needs bit 1, sets bit 2 and `ThargonMissionVar` 1); `chkMissions` `&2063` states 1 to 5;
  the planet description override `&DE`; station spawns Thargoids (state 4); station kill adds `&FFFF` kill points and sets the
  station flag; `ThargonMissionFinished` `&49DB` (rank +1, `Missionflag` bit 3, name overwritten with FLORENCE); ECM jammer bit 7;
  game over on docking in state 4; target = system 0 of the current galaxy.
- *Changes:* none. Known oddity to leave or fix: the station-kill code does `SET 3,(HL)` on `&3926` instead of `Missionflag`.

**4. Constrictor hunt** (BBC disc, Master, 6502SP, Apple II, C64, NES, Atari ST #1, MSX #1; **not** the CPC)
- *Systems:* docking hook (offer, briefing); a new mission state byte (the CPC has 1 free `Missionflag` bit, the chain needs about 4
  bits plus a hint index); rank test (`killScoreHigh` is the BBC `TALLY+1`) and galaxy 1 or 2; the docked system-description override
  for the eight-system hint chain; a galactic-hyperdrive check and the galactic jump; the ship table (entry 19) and a blueprint; a spawn
  command with a marker flag (as the cloak Asp); tough-ship AI (only military lasers hurt it, ECM); kill hook; reward 5,000 Cr and
  `inc (killScoreHigh)`; about ten strings in `stringsTable2`; the save block (new byte); free space (610 bytes at the end of `COMMONXX`).
- *Changes:* write a BBC-to-CPC hull converter (the CPC blueprint layout differs); add ship table entry 19; add the mission byte and a
  `chkMissions` branch; grow the string table (needs a compressor); add the hint chain, spawn and kill hooks and the payout; re-key
  `encryptSAV` (any code change breaks saves). About 0.8-1.1 KB for the Constrictor alone. The ST and MSX version differs: after the
  offer you visit five planets in turn (each docking picks the next), then it attacks in deep space, reward 10,000 Cr.

**5. Thargoid plans / documents** (BBC disc, Master, 6502SP, Apple II, C64, NES; Atari ST #2 and MSX #2 as "documents"; **not** the CPC)
- *Systems:* docking hook; mission state (the BBC needs the Constrictor finished and galaxy 3); rank test (`>= 5`); a destination
  planet (BBC: Ceerdi (215,84) then Birera (63,72); ST: the furthest planet found with `search`); a "carried item" (BBC plans, ST
  documents in the hold: the CPC hold has no slot, only the unnamed save byte `&38E1`); the spawn rule (BBC: 22% of checks add a
  Thargoid and a Thargon; ST and MSX: Thargoids replace pirates); reward (BBC Navy Extra Energy Unit and 256 kill points; ST and MSX the
  military energy unit); `extraEnergyUnit` `&3902` and `RechargeEnergy` `&3608`.
- *Changes:* needs mission 4's state machinery first (or the ST variant, which does not need the Constrictor). New: carried-item
  flag, destination logic, the changed spawn rule (find the CPC equivalent of the BBC main loop spawn; `spawnCommand0` picks asteroids
  or pirates today), recharge rate 3 instead of 2, text. About 0.5-0.7 KB on top of mission 4 (the plan's earlier estimate for both: 1.4-1.8 KB).

**6. Trumbles** (C64, NES only; **not** the CPC)
- *Systems:* docking offer once cash is high enough (`chkMissions`); the credits words; a 16-bit Trumble count in the save (the CPC
  has only the unnamed bytes `&38FD`, `&38FE`, `&3905`, `&3906`); breeding on arrival (`setShipvarsAtArrival`) and slowly in the main
  loop; the sun and cabin-temperature code (heat kills them); the hold (they eat food, goods 0, and narcotics, good 6); a sound; an
  inventory or status line; optionally software sprites in the off-screen bitmap.
- *Changes:* about 150-250 bytes of code and 100 bytes of text for the text-only version; sprites add 300-450 bytes (see the Trumbles
  analysis below). No reward, so it is a joke mission.

**7. Stolen police ship** (Elite Plus only; built)
- *Systems:* offer at docking (`chkMissions`); `Missionflag` bit 4 (unused) as the state; a target system chosen by seed compare (as
  the Thargon target); a spawn on arrival of one hostile Viper (the Viper is in the ship table; police AI replaced by hostile AI); kill
  hook; reward 4,000 Cr (add 4 to the high credits word); strings from index `&E1`; the legal-status code and `punishCheater`.
- *Changes:* a new spawn command, the state bit and a done-flag, the offer and reward text, and a trigger that the CPC thresholds do not
  provide (a separate counter or the ST queue). The Elite Plus code is in section 4 below.

**8. Asteroid bombardment** (Elite Plus only; built)
- *Systems:* offer at docking; a named system; asteroid spawning (CPC `spawnCommand0` already spawns asteroids); some rule for a
  "threat" to a planet; reward 6,000 Cr.
- *Changes:* the Elite Plus EXE shows how it works (section 4 below); built.

**Order and trigger.** The ST and MSX start one mission per 64 jumps from a queue (1 to 5). The CPC fires its three at counter
thresholds 32, 128, 254. Adding missions 4 and 5 means choosing between the two schemes; see `docs/_missions_built.md`.

### Constrictor (BBC disc; Apple II the same logic)
- State is `TP` bits 0-1: `%00` not started, `%01` in progress (set by `BRIEF`), `%11` Constrictor killed (set by
  `KILLSHP`), `%10` finished (set by `DEBRIEF`, which clears bit 0 and unlocks the next mission).
- Trigger, checked at every docking (`DOENTRY`): `TP` bits 0-1 are `%00`, `TALLY+1 > 0` (at least 256 kill points,
  rank Competent), and the galaxy is **1 or 2**. Then the briefing runs (Captain Carruthers in galaxy 1, Fosdyke
  Smythe in galaxy 2).
- A chain of docked hints, each a capitalised override of the system description, shown only while in progress:
  Reesdice, then Arexe (a galactic hyperdrive was fitted and used), then a galactic jump to galaxy 2, then Cearso,
  Errius, Inbibe, Ausar, Usleri, and finally the ship waits in deep space at Orarra (near Usleri).
- The Constrictor is a tough ship: only military lasers hurt it, it has an ECM. Reward 5,000 credits and 256 kill
  points (one "Right On Commander").
- Disc cost: the blueprint lives only in one data file (`D.MOG`) that `LOMOD` loads for the fight.

### Thargoid plans (BBC disc; Apple II the same logic)
- Needs the Constrictor finished (`TP` bits 0-3 `%0010`), galaxy **3**, and `TALLY+1 >= 5` (3/8 of the way from
  Dangerous to Deadly).
- Stages: `%0110` briefed (Captain Fortesque: go to Ceerdi (215,84)); `%1010` plans on board (Agent Blake of Naval
  Intelligence at Ceerdi); `%1110` delivered at Birera (63,72).
- While the plans are on board, 22% of spawn checks add a Thargoid and a Thargon: the extra danger.
- Reward: a Navy Extra Energy Unit (recharges 3 per use instead of 2) and 256 kill points.
- Disc cost: forces the Thargoid and Thargon blueprint files to load while the plans are carried.

### Trumbles (C64 and NES only)
- Offered at the dock once cash is at least 5,017.6 Cr (the C64 code tests `CASH+2 >= $C4`; the deep-dive page also says
  "`CASH+1 > 0`" and "6553.6", which disagree with the code, so trust the code); the Merchant Prince of Thrun sells one Trumble for
  5,000 credits; bit 4 of `TP` records the offer. Trumbles breed on every jump and slowly in flight, eat food (and on the C64
  narcotics), and die in the sun. The C64 draws them as sprites over the cockpit. Code-level reading is below.
- **Where the C64 source is** (found 2026-11-07): Mark Moxon's annotated C64 source,
  https://github.com/markmoxon/elite-source-code-commodore-64 (files `1-source-files/main-sources/elite-source.asm`,
  `elite-data.asm`, and the sprite data), browsable at https://elite.bbcelite.com/c64/. It is the original Bell and
  Braben code with Moxon's commentary, so it is copyrighted: read it, do not copy it into this project. The pieces:
  - `DOENTRY` holds the offer; `TBRIEF` (https://elite.bbcelite.com/c64/main/subroutine/tbrief.html) makes it; `SOLAR`, main
    loop part 5 and main flight loop part 15 hold the breeding, noise and sun death; `TRIBBLE` is the 16-bit count in the save
    block. The details are in the table in the next subsection. They survive the escape pod (stated by the deep dive, not read).
  - `MVTRIBS` (https://elite.bbcelite.com/c64/main/subroutine/mvtribs.html): once per main-loop pass it moves one of the
    sprites (the pass counter mod 8 selects it; none moves if that is at or above `TRIBCT`, the count shown, 0 to 6). An 8%
    chance picks a new direction from a four-entry table (`TRIBDIR`/`TRIBDIRH`: still or one step each way), the y position
    wraps at 8 bits, x is 9 bits with the carry kept in `VIC+$10`, and a sprite leaving one side reappears on the other.
  - `TRIBTA` converts the count in the hold to a sprite count (0-6) and `TRIBMA` to the VIC sprite-enable mask; `spritp`
    holds the sprite shapes (laser sights, explosion, two Trumbles).
  - Port cost estimate for the CPC: see "Trumbles, read from the C64 source" below.
- (Planning note, now built: it adds no reward and needs a 16-bit save variable, an arrival hook, a main-loop hook and a
  sun hook; with no sprites on the CPC it would be text-only (the NES shows none on screen). Parked as optional (phase 5),
  but it is the smallest of the three.)

### Trumbles, read from the C64 source (2026-11-07)

Read in the annotated pages `doentry`, `tbrief`, `solar`, `main_game_loop_part_5_of_6`, `main_flight_loop_part_15_of_16` and
`mvtribs` of https://elite.bbcelite.com/c64/. Behaviour only; the code is not copied here. Not read: the code that turns
the count into sprites (`TRIBTA`, `TRIBMA`, `TRIBCT`), the inventory printing, and the escape-pod path.

| Piece | What the C64 does | Size of the idea |
|---|---|---|
| Order in `DOENTRY` | Constrictor is tested first (`TP` bits 0-1), then Plans (galaxy index 2 = galaxy 3, three stages), and Trumbles last, only when none of those fired | `chkMissions` needs the same "first match wins" rule |
| Offer | cash byte `CASH+2 >= $C4` and `TP` bit 4 clear, then `TBRIEF`: set the bit, show token 199, Y/N, on Y pay 50,000 decicredits and set the count to 1, on N nothing | about 25 bytes |
| Count | `TRIBBLE` is 16 bits, kept positive (high byte clamped to `$7F`), saved in the commander file | 2 save bytes |
| Breeding on arrival (`SOLAR`) | if the count is not zero: zero the food and narcotics in the hold; new count is about `2 * ((count + random 0-15) OR 4)`, so it roughly doubles per jump and soon runs into the 16-bit cap | about 30 bytes |
| Breeding in flight (main loop part 5) | only when the high byte is not zero (256 or more): 14% of passes (`random >= 220`) add one | about 15 bytes |
| Noise (main loop part 5) | when the high byte is not zero, chance proportional to it (halved when the cabin is cooler than 224), plays sound 14; pitch and length depend on cabin temperature | about 40 bytes plus one sound entry |
| Sun (main flight loop part 15) | when the cabin temperature is 240 or more: hide sprites 2-7 and halve the count (so it decays to zero); 224 or more still scoops fuel | about 15 bytes |
| Sprites (`MVTRIBS`) | one of up to six sprites moves per main-loop pass (pass counter mod 8), 8% chance to pick a new direction from a four-entry table, 9-bit x with wrap | C64 only |

What this means for the CPC:
- The logic is small: about 150 bytes of Z80, one 16-bit save variable, one briefing string, one sound, and an inventory line.
- The CPC has the matching hooks: `chkMissions` for the offer, `setShipvarsAtArrival` for breeding on arrival, the main loop for
  slow breeding and noise, the sun and cabin-temperature code (`ScoopFuel` and `chkAltitude` area) for the heat death, and
  `cargoHold` (food is good 0, narcotics good 6) for the eating. Payment uses the credits words.
- The breeding arithmetic needs 16 bits; the C64 caps at 32,767. On the CPC the save block has only unnamed bytes
  (`&38FD`, `&38FE`, `&3905`, `&3906`) to spare: find which are really free.
- No sprites: show the count as a text line on the status or inventory screen (the NES approach) and drop `MVTRIBS`,
  `TRIBTA`, `TRIBMA`, `spritp`. Estimate for the whole text-only mission: 150-250 bytes of code and 100 bytes of text.
- One thing to decide: the C64 mission has no end other than the Trumbles dying out, and in the C64 they eat the hold's food, so the
  main effect on play is lost food and narcotics trading; there is no reward. Keep it as a joke, or tie it to something
  (for example a rank bonus for getting rid of them).

### Trumbles crowding the screen: what it would cost on the CPC (analysis, 2026-11-07)

On the C64 the crowding is hardware sprites: up to six, picked from the count by `TRIBTA`, moved one per pass by `MVTRIBS`, drawn
by the VIC over the view, the margins and the dashboard at no CPU cost. The CPC has no sprites (only the CPC+ ASIC does), so they
would be software sprites, and the game's structure makes that fairly cheap:

- The flight view is drawn into a linear off-screen bitmap at `&A000-&BFFF` (Mode 1, 4 pixels per byte, 64 bytes per line, so 256 pixels
  wide), which `ClearBitmap` (`&1FF1`, a push loop) wipes every frame and `transferBuffertoScreen` (`&1ED1`) copies to `&C000`.
  Drawing the Trumbles into that bitmap just before the single end-of-frame call (`jp transferBuffertoScreen` at the end of the
  flight loop) needs **no erase and no screen-address maths** (address = `&A000 + y*64 + x`).
- They would only ever appear inside the 3D view; the dashboard is outside the bitmap. The C64 sprites spill over everything, so
  this is tidier but less crowded.

| Part | Estimate |
|---|---|
| Sprite shapes: 16 x 12 pixels is 4 bytes x 12 rows = 48 bytes; with a mask 96 bytes; two animation frames about 190 bytes | 100-200 bytes data |
| Draw routine: per-sprite masked blit into the bitmap, clipped by keeping positions inside the view, plus a loop over the count | 60-100 bytes |
| State: x, y, vx, vy for six Trumbles | 24 bytes RAM (not in the save) |
| Movement: port of `MVTRIBS` (one sprite per pass, 8% chance of a new direction from a four-entry table, wrap at the edges); x moves in 4-pixel steps so no pixel shifting is needed | 60-80 bytes plus 8 for the table |
| Count to sprite number (`TRIBTA`: 0-6) and the hook before the transfer | 20-30 bytes |
| **Sprites in total** | **about 300-450 bytes**, on top of the 150-250 bytes of code and 100 bytes of text for the text-only mission: **about 0.6-0.9 KB for the whole mission** |

Speed: six 16 x 12 blits is about 290 byte operations, roughly 10,000 T-states or 2.5 ms; a 50 Hz frame is 20 ms and the copy to the screen
already costs more than a frame, so this adds only a few percent, and movement of one sprite per pass is negligible.

Problems to solve:
- **Colours** (read from the listing and checked in cpcxray 2026-11-07). Everything drawn through the off-screen bitmap
  (`Spaceflight`, title screen, hyperspace and witchspace tunnel, docking, launch; the only callers of `ClearBitmap` and
  `transferBuffertoScreen`) runs with `Viewdirection` 0-3. Views 4 and up (charts, market, status) are drawn straight to the screen,
  so they do not matter for sprites. In views 0-3 the ISR (`doColorSplit` -> `setDashboardInks`) sets the viewport pens at the start of
  every frame, and the dashboard inks only after the fourth interrupt. Hardware ink numbers (gate-array value minus `&40`):

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
  | Cloaking device active (wins over the two above) | 0 | 24 | 20 | 31 |

  cpcxray check: from `firebird_in_flight.sna`, for each `presentSystemX & 7` I ran `setViewColors` (`&4D2B`), stopped at `&28B4` (end of the
  viewport ink setting) and read the gate-array palette: all eight rows match, as do `FlightMode` 1 (12/28/20/14), the cloak flag (0/24/20/31,
  also with `FlightMode` 1) and `Viewdirection` 1-3 (same as 0). `Viewdirection` 4 gives 4/31/18/14, so views 4 and up really differ (pen 2 is 18).
  With `counter_colorsetting` (`&2854`) set to `&18`, pen 2 alternates 20 and 13 every frame, read at `&28D8`. Not tested: the pen 3 flicker during explosions
  (listing only).

  The per-system row comes from `tableSystemColors` (three bytes per system: pen 3, pen 0, pen 1), copied by `setViewColors` into the
  operands of `smc_patchviewPortInk3/0/1`; it runs in `setupNewGame` and in `generateTargetSystemParAtHyperjump`.
  - **Pen 2 is the only fixed pen**: always `&54` = ink 20 (black) in views 0-3. Two exceptions: the energy bomb flashes it between `&54`
    and `&4D` (ink 13) for `&18` frames (`counter_colorsetting`, `flag_color0alternating`, it flashes the border too).
    The colour-split code leaves pen 2 alone in views 0-3 (`changeInks2and3` runs only for views 4 and up).
  - Pens 0, 1 and 3 change with the system, the supernova mode and the cloak. Pen 3 is also set to `&4E` (ink 14) while explosions are drawn
    (`todoDrawExplosions` saves the old value in `CirclePixelMask` and restores it afterwards), so a sprite in pen 3 can flicker orange for a moment.
  - In every case above the four pens are four different inks, and ink 20 (black) never appears as pen 0. So pen 2 is always distinct from the
    background and from pens 1 and 3, and pen 1 or 3 is too. Body in pen 2 (black, fixed) plus an eye in pen 1 or 3 is the safe two-pen design;
    the eye's actual colour depends on the system, so check its contrast against pen 0 on a few systems before fixing the choice.
- **Space.** 0.6-0.9 KB is more than the 610 free bytes, so it needs the reclaimed dead code (735 bytes) and competes with the
  Constrictor for it. The mission works without sprites; the sprites are the part to drop first if space runs out.
- **CPC+.** The ASIC has 16 hardware sprites of 16 x 16 pixels (256 bytes each in ASIC RAM). Using them would crowd the whole screen like the
  C64 but only on a Plus, needs detection and the unlock sequence (about 100 bytes) and is not worth it for the original CPC.
- **Crowding level.** To look as crowded as the C64 (six large sprites on a 320 x 200 view) on a 256 x 128 bitmap, use 12-pixel-wide shapes.

## 2. What the CPC already has that the port can reuse

| Need | CPC mechanism | Source |
|---|---|---|
| Docking hook (the `DOENTRY` equivalent) | `chkMissions` at `&2063`, called from the docking code | `commonxx.asm` |
| Arrival hook | `&4E58` after every hyperspace arrival; counts jumps in `jumpCounter` (`&38DA`) from galaxy 2 on | `docs/_gameplay.md` |
| Rank tests | `killScoreHigh` (`&38D9`) **is** the BBC `TALLY+1` (the CPC rank table `RankingBytes2` = `02,0A,19,FF` is the BBC high-byte table, Elite at `&19`); `killScore` low bytes are `TALLY` | `getRank` |
| "256 kill points" reward | `inc (killScoreHigh)`, as the supernova and cloak rewards already do | `AddDEtoKillScore` |
| Credits reward | `getMoney` / `getBounty` | `commonxx.asm` |
| Story screens | `drawFlipChart` full-screen text, flight messages, `stringsTable2` (`&0FCA`, indexes to `&E0`) | `docs/_gameplay.md` |
| Docked description override | the invasion already replaces a planet description with `<planet> IS RESISTING A THARGON INVASION` (`&DE`) | `docs/_gameplay.md` |
| Thargoid and Thargon models, spawn commands | ship table entries 15 and 16, `spawnCommand1` (up to four Thargoids), `spawnCommand4` | `shipGFXdataTable` |
| Special ship with a marker flag | the cloaking-device Asp is spawned this way (`&8404`) | `docs/_gameplay.md` |
| Equipment flag for the reward | `extraEnergyUnit` (`&3902`), `RechargeEnergy` (`&3608`) | `commonxx.asm` |

## 3. Findings kept from the planning

- **Free space (measured 2026-11-07, cpcxray):** `loadLARGEAXX` (called at every docking just before `chkMissions`) parks `&0040-&1A3F` at `&A600` and reloads `LARGEAXX.BIN` (`&0840`, `&1200` bytes) from disk, so the zero tail
  `&1714-&1A3F` (812 bytes) is fresh at each docking and nothing in the sources addresses it. Docked, `LARGEAXX` is resident and the tail is all zero; in flight `LARGEAXX` is parked and the range holds flight-side content with 0 reads and 0 writes in 30 s
  of flight. At the title screen `LARGEAXX` is already parked, so docked-only code is only valid after `loadLARGEAXX`. `chkMissions` has a single call site, the docking sequence. The tail is usable for docked-only code and data; flight-time parts
  need the 610 bytes at the end of `COMMONXX`. New strings can sit in a table of their own: `printStringA` takes an 8-bit index and `stringsTable2` already has 254 strings, so a small entry point sets `HL` to the new table and reuses the token loop;
  tokens may still reference `stringsTable2` strings `&81-&D6` and the digrams. Re-encoding both stock string tables optimally saves only 48 bytes of 2,822 (`tools/textcomp.py`), so recompressing old text is not a space source.
- **Dead code (2026-11-08):** the code-shaped chains in `db` runs are live (tails of `push ix` routines), `altJrPoint*` are self-patched jump targets; only `unusedGetFlightMode` and `unusedGetCloakFlag` are unreferenced, about 10 bytes. Fessor's "450-735 bytes" could not be placed in stock
  (`docs/_architecture.md`, "Dead code and free space"). The flight-time budget is the 610-byte tail only (its top bytes also carry stack pushes at `&A000`). `&A000-&A5FF` is the off-screen buffer in flight, not free.
- **Gating and slots.** CPC missions run on `jumpCounter`, counted only from galaxy 2 on; the BBC Constrictor is offered in galaxy 1 or 2 at a docking and the plans need galaxy 3. The invasion is offered at jump 254 in any galaxy 2-8, so the stub lets the stock
  offers go first. The supernova and invasion react to galactic jumps, so the added state stays out of `ThargonMissionVar`. The CPC has 6 entity slots (3 reserved): spawn the special ships alone. The invasion gives rank +1 and the title ARCHANGEL
  (`Missionflag` bit 3); new rewards use `inc (killScoreHigh)` and need no title. Saves are XORed with the game's own code at `EquipShip`, so any change to that code invalidates old saves; the added missions only use unused save bytes and keep the code.
- **The ten system names (answered 2026-11-07):** generated from the CPC's own digram table (`DockedDigrams`, index 0 skipped, `?` drops the second letter) and the BBC seed twist (`waggle_galaxy`, four twists per name; a galaxy hop rotates every seed byte left by one),
  after checking it reproduces Tibedied (galaxy 1 system 0), Lave (7) and Diso (147). All ten exist exactly once, in the galaxy the chain needs: galaxy 1 Arexe (system 28, x/y 164,89) and Reesdice (36; 149,101); galaxy 2 Ausar (53; 146,102), Cearso (68; 87,109),
  Inbibe (79; 152,146), Usleri (118; 148,68), Orarra (193; 144,33) and Errius (253; 184,149); galaxy 3 Birera (36; 63,72) and Ceerdi (83; 215,84). Ceerdi and Birera match the BBC coordinates. Orarra is about 7 LY from Usleri.
- **The spawn rule (answered 2026-11-07):** the CPC equivalent of the BBC main-loop spawn is `handleEntitys`: every frame it counts down `todoLaserVar2`; when that reaches 0 and no station is near, no launch is running and fewer than 4 station-launched ships exist,
  it calls `spawnCommandParser` with action 0 = `spawnCommand0`. `spawnCommand0` rolls a random byte minus the contraband weight C: below zero picks a hostile (`cmd0ChkSendHostileAfterUs`), `&50-&59` an asteroid, `&5A` and up nothing. The mission spawn checks hook in at the top
  of `spawnCommand0`. The existing invasion already forces a Thargoid there when `ThargonMissionVar` is 4.
- **The escape pod (answered 2026-11-07):** a bug, but it affects no reward. `cargoHold` is `&38E2-&38F2` (17 goods), but the pod clear (`mleCleanInvLoop`) clears 17 bytes from `&38E1`, so it wipes `&38E1` (the market random byte) and goods 0-15 and **keeps alien items (good 16, `&38F2`)**;
  `cargoSpaceFree` is reset to the full capacity, so a pilot who ejects with alien items can hold more than the capacity. Fix: start the loop at `&38E2` (`ld hl,cargoHold`); not applied.
- Not planned: Elite-A delivery missions, the Apple II's graphics, music. The BBC code is under Mark Moxon's annotations: behaviour only, the Z80 is written fresh. The disc `Elite_UK_original_protected.dsk` carries ARMOURLOC and decoys, so builds start from the Firebird or German cracked disks.

## 4. More missions: Elite Plus

What exists elsewhere (details and links in `docs/_gameplay.md`, "Atari ST source and the NES source"): the Atari ST source
(adapted from the MSX version, which shares the Torus lineage) has five missions in a fixed order triggered every 64 jumps:
Constrictor, Thargoid documents, refugees, the Cougar, the Thargoid invasion. Only Elite Plus (PC) adds **Stolen Police Ship**
(4,000 Cr) and Asteroid Bombardment (6,000 Cr); no code for either was found in the ST or NES source. Reports on how the police
ship works are thin: a stolen police Viper with a new paint job, hunted in a named system, reward 4,000 Cr, offered on docking; one
mission at a time; players disagree on whether it is fully implemented ([AFE FAQ2](https://wiki.alioth.net/index.php/AFE_FAQ2),
[Elite Plus missions guide](https://www.tales-from-darkenedroom.com/post/elite-plus-missions-galaxy-9)).

Source search (2026-11-07): no Elite Plus source or disassembly exists publicly (Chris Sawyer's PC assembly; only player guides, the
[Frontier forum thread](https://forums.frontier.co.uk/threads/elite-plus.70102/) and savegame-editor notes, where the mission is code 04). Extra details
from those: triggered by a hyperspace counter after leaving galaxy 1, offered at docking, one mission at a time, the Viper gives no bounty and
shooting it may count as an offence. Update: the Elite Plus EXE was then unpacked and disassembled (next section), so there is now a reference.

### Elite Plus code (disassembled 2026-11-07)

Source: `work/elite plus/ELITE.EXE` (EXEPACK, README says "hacked version of PC Elite +"; unpacked with `tools/unexepack.py`, 16-bit
x86, DS base = image `0xB000`). Addresses are image offsets; data is `DS:off`. Read with capstone, nothing was run, so every line below is
from static reading. The mission code looks original, but the hack is unexamined.

- **Variables:** `DS:83A0` mission number (0 none, 1-6), `83A2` mission state, `83A3` target system (seed byte, compared with `8329` = current
  system), `839E` jump counter (saturates at 255), `83B0`/`83B1` offer-pending flags, `836B` legal status, `836C` kill counter.
- **Trigger (`0x7595`):** every jump increments `839E`; when it reaches `0x20, 0x38, 0x50, 0x6E, 0x8C, 0xA0` (32, 56, 80, 110, 140, 160) the
  mission number becomes 1 to 6 and the state is cleared, but only while no mission is running. **Stolen police ship is number 4 (110 jumps).
  Corrected 2026-11-08: number 5 (140 jumps) is the Thargoid plans (a debrief pays 5,000 Cr) and number 6 (160 jumps) is the asteroid
  bombardment (pays 6,000 Cr); see "Elite Plus missions 4, 5 and 6" below.** This is the ST rule with a one-byte counter, so the CPC Thargon thresholds are not needed.
- **Offer (`0x99DC`, run at docking):** twists the galaxy seed (`0x205-0x20B`) until the system byte differs from the current one, stores it in
  `83A3`, sets state 1 and prints the text with the system name. Mission 4 has **no Y/N prompt**, only "press any key".
- **Arrival (`0x7543`):** states 1/2 are re-evaluated at each jump: state 2 if the new system's byte equals `83A3`, else 1.
- **Spawn (`0x7AD3`):** state 2 only. Requires free ship slots, scans the slots for an existing ship with id `0x39` and `[+0x25]==1` (so only
  one), then a random roll (`rand <= 400` of 65536 per check) and spawns blueprint entry `DS:87C5`. That entry is the **same one the police
  spawn uses** (`0x7A50`, reached from the wanted-level encounter code at `0x8416`): the police Viper. Differences: aggression byte `[+0x33]`
  = 5 instead of 4, energy `[+0x30]` = `0xC8` instead of `0x64`, and the marker `[+0x25]` = 1. (That `[+0x33]` 5 means "hostile" is inferred.)
- **Kill (`0xAD4F`):** state 2 and `[+0x25]==1` on the dying ship: state := 3, flash "Stolen Viper Destroyed!" (`DS:AED8`) and bump the kill counter.
- **Reward (`0x9C4A`, next docking):** state 3 shows the debrief page and adds `0x9C40` = 40000 decicredits = **4,000 Cr** (call `0x8E3C`), then
  clears `83A0` and `83B0`. A failed hunt just waits: leaving the system drops state 2 back to 1.
- Not checked: whether killing the marked Viper changes legal status (the forum "no bounty" claim), and the hack's changes.

- **Legal status, Elite Plus vs the CPC (static reading, not run):**
  - CPC: any destroyed ship whose flag byte `ix+33` has bit 5 or 6 set (innocent or police) does `legalStatus |= 0x40`, i.e. fugitive at once
    (`commonxx.asm`, after `AddDEtoKillScore`). Our stolen Viper would trigger it unless its flags are cleared.
  - Plus: no OR with 64. A kill adds to `DS:836B` only in `0xAE08`: +4 for a police Viper (blueprint `87C5`, id `0x1C`) whose word `[+0x3A]` is 1,
    +2 for any other ship when `DS:7680` bit 0 is set, otherwise nothing. The marked Viper has bounty byte `0xFF` (variable), and only id `0x16`
    pays (500 = 50 Cr in the `0xADEC` path), so it pays nothing: this is the forum's "no bounty".
  - Plus fugitive-sized hits are separate: +40 for a missile hitting a station or planet (`0xACA6`), +5 for lasers on a station (`0x83B1`), +10 or +40
    when a police Viper (`[+0x3A]==1`, tested by `0x827E`) witnesses an attack (`0x84B0`).
  - The police Viper spawn sets `[+0x3A]=1` (`0x7A5C`); the mission spawn (`0x7B1B`) does not and does not call the slot-clearing routine
    `0x81B7` that the normal spawn uses, so whether the marked Viper counts as police for witnesses depends on stale slot data. Unresolved.
  - For the CPC build: give the marked Viper flag bits that make `ix+33 & 0x60` zero (not innocent, not police) and treat it as a pirate, so the
    kill costs nothing; check what police do when they see you attack it.
- **Online (2026-11-07):** [rembish/elite-plus-revamp](https://github.com/rembish/elite-plus-revamp) is a work-in-progress decompilation of
  Elite Plus (EXEPACK unpack, control flow, Ghidra, galaxy generator verified for all 8 x 256 systems; it names the build "V3.1 August 1990"). No
  official source. The [Frontier thread](https://forums.frontier.co.uk/threads/elite-plus.70102/) has an EXE hex patch (`3D 2C 01` -> `90 90 F9`),
  an "Archangel" difficulty mode and a lower kill count for Elite rank; its mission list also has a masking device and a stolen-plans mission.
  The [VOGONS savegame thread](https://www.vogons.org/viewtopic.php?t=64736) lists a savegame flag that activates special missions and a Thargoid
  Base mission. The `3D 2C 01` bytes occur three times in the EXE (`0x7455`, `0x7B51`, `0x82DF`; all `cmp ax,0x12C` after a random call, a 300/65536 chance). The
  one that fits a useful patch is `0x7455`, the galactic jump: after the counter reaches galaxy 8 (the ninth) a 300/65536 roll keeps it, otherwise it wraps
  to galaxy 0; `stc` makes `jb` always taken, so the ninth galaxy is guaranteed. The Frontier post does not say which occurrence, so this is a likely match, not
  proven. The other two are the mission-6 Viper spawn roll (`0x7B51`) and a per-tick Cobra-class roll (`0x82DF`). The savegame flag and the Base mission are not checked.

### Elite Plus missions 4, 5 and 6, read again (2026-11-08, static, nothing run)

Method: capstone on `work/elite plus/extracted/ELITE.img`, every `cmp byte [0x83A0],n` site, offer (`0x98EB`), debrief (`0x9AC4`), spawn (`0x7A66-0x7C8F`) and kill (`0xAD4F`).
The offer pointers give the texts: 4 -> "stolen by Thargoid infiltrators", 5 -> "plans for a new Thargoid invasion ship", 6 -> "bombarded by large rocks and asteroids".
Common to all: `83B0` = 1 once the offer is shown (the offer runs when `83B0` is 0 at docking, `0x8C17-0x8C1E`); `83B0` goes back to 0 with `83A0` when the debrief is paid.

| | 4 Stolen police ship | 5 Thargoid plans | 6 Asteroid bombardment |
|---|---|---|---|
| Jump counter | 110 | 140 | 160 |
| Target `83A3` | seed twist, must differ from here | same | same |
| State `83A2` | 1 hunting, 2 in target system, 3 killed | not used | counter, set to `0x32` (50) at the offer |
| In flight | one marked police Viper (above) | `0x7A66`: `83B0` = 1, 60/65536 per check, only with no hostile around (`0x8736` = 0), spawns a Thargoid (type `0x16`, row `0x8847`) with aggression 5, an ambush (not tied to a system) | `0x7B32`: only in the target system, state above 1: 5000/65536 per check spawns an **Asteroid** (type 5, row `0x876B`; aggression 3, marker `[+0x25]` = 2, placed by `0x7E32`); with a roll of 300 or less one more ship, a **Cobra Mk III** (type `0x1A`, row `0x8815`; aggression 5, `0x7C59`) |
| Kill (`0xAD4F`) | marked ship: state 3, flash "Stolen Viper Destroyed!" | none | marked ship (`[+0x25]` = 2): state minus 1, down to 1 |
| End | dock anywhere: 4,000 Cr | dock **in the target system**: 5,000 Cr (`0xC350` decicredits) | state equals 1, dock anywhere: 6,000 Cr (`0xEA60`) |

Notes: (a) so "the two Elite Plus missions" that are not in any other port are 4 and 6; 5 is the BBC plans mission with an ambush; (b) no failure path was found for 6
(the asteroids never "reach the planet"; leaving the system just stops the spawning, the counter stays); (c) the "masking device" mission of the Plus texts (find the invisible-ship system, retrieve the device, "Use ... to activate it") is the cloaking device mission that the CPC already has (Cougar with Asp escorts, `aspMissionState`, `Y` key; section 2 above), so it is not missing: the only Plus missions the CPC lacks are 4 and 6 (6 is built on branch `addon-missions`);
(d) blueprint rows identified (2026-11-08): each row is 10 bytes, byte 0 is the ship type and indexes the name list at `DS:80E9` (0 Dodo, 1 Coriolis, 2 Boa, 3 Anaconda, 4 Cobra Mk I, 5 Asteroid, 6 Boulder, 7 Thargon, 8 Shuttle, ... `0x11` Cargo Canister, `0x12` Constrictor, `0x13` Cougar, `0x14` Missile, `0x15` Escape Pod, `0x16` Thargoid, `0x17` Fer-de-lance, `0x18` Asp, `0x19` Sidewinder, `0x1A` Cobra Mk III, `0x1B` Krait, `0x1C` Viper, `0x1D` Python). So the **stolen ship is a Viper** (row `0x87C5`, the police Viper row, type `0x1C`; the mission only changes aggression 5, energy `0xC8` and the marker), the **asteroid mission's rocks are type 5 Asteroid** (row `0x876B`) with an occasional Cobra Mk III, and mission 5's ambush is a **Thargoid**; the CPC build can therefore count asteroid kills with no marker (as built on `addon-missions`); (e) the `[+0x25]` marker byte
is a ship-record byte the CPC does not have; built (2026-11-08) without one: a police Viper has bits 1 and 6 of `(ix+33)` set (from blueprint byte 18), the stolen one has both cleared, which also answers the legal-status question (the CPC kill code only tests bits 5 and 6 of `ix+33`).

CPC consequence (built, `docs/_missions_built.md`): a state byte instead of a `Missionflag` bit, no Y/N prompt, a flag-pattern marker for the Viper, the jump wait before the offer; the asteroid mission counts asteroid kills at the target with no marker.

## 5. What the C64 does for its Trumble sprites


Files read: `elite-source.asm` (`MVTRIBS`, `TRIBDIR`, `TRIBDIRH`, `SPMASK`, `TRIBTA`, `TRIBMA`, the `TRIBCT`/`TRIBVX`/`TRIBVXH`/`TRIBXH` workspace, the count-to-sprites code in the sight routine) and `elite-loader.asm` (VIC setup, sprite pointers).
- **Shapes:** `SPRITE.bin` is 448 bytes = seven 64-byte hardware sprites (24 x 21 px, 3 bytes per row): four laser sights, one explosion and **two Trumble shapes** (one looks right, one looks left). Sprites 2, 4, 6 use the right-facing
  shape and 3, 5, 7 the left-facing one, so the six Trumbles alternate facing. All sprites are drawn double width and double height (48 x 42 px on a 320 x 200 screen, about 15% x 21% of it), single colour.
- **Colours:** six different pen colours (brown, grey, blue, white, green, brown); the CPC has no spare pens in the flight view (only pen 2, black, is fixed), so that cannot be copied.
- **Drawing cost on the C64: none.** The VIC-II draws the sprites; the code only changes registers. `MVTRIBS` is about 110 instructions, most of them the 9-bit x-coordinate and the I/O-banking switches. Its logic: one Trumble per main-loop pass
  (loop counter mod 8, only those below the shown count), an 8% chance (random >= 235) of a new velocity from the table 0, +1, -1, 0 separately for x and y (so half of the picks mean no movement), then x and y are advanced by that velocity and wrap
  around the edges (x past the right edge returns at the left and the other way round; y just wraps at 8 bits).
- **State:** `TRIBCT` (1 byte, the number of sprites 0-6), and three 16-byte tables of which 12 bytes each are used (x velocity low and y velocity interleaved, x velocity high, bit 8 of x): 49 bytes of RAM. Position lives in the VIC registers.
- **Count to sprites:** bits 4-6 of the high byte of the 16-bit count (0-7) go through the 8-entry `TRIBTA` to 0-6 sprites, so the first sprite appears at 4,096 Trumbles and the sixth at 20,480 or more. The count is only a few hundred
  for a long time, so the sprites show up late; on the CPC the thresholds are a free choice (our count roughly doubles per jump).

**What this changes in the estimate above.** The C64 uses two facing shapes, which is design B1 (two frames, no mask: 96 bytes of data at 16 x 12 px) and not the masked B2. Per-Trumble state on the CPC would be x, y, vx, vy: 24 bytes for six, instead of 18.
Movement is simpler on the CPC (x in 4-pixel byte units, 0-63, plain 8-bit wrap), so the 45 bytes stand; the draw routine (about 70 bytes) is the part the C64 gets for free. Expected Trumbles image with the two facing shapes: about
560 of 610 bytes (about 50 free). A C64-sized sprite (a third of the flight view) is out of reach: 38 x 27 px would be about 270 bytes per shape.

**Built (2026-11-08):** one 16 x 14 shape instead of the two facing shapes, 270 bytes in the Trumbles image; see `docs/_missions_built.md` section 3.

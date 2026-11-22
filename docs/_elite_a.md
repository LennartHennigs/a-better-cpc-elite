# Elite-A (Angus Duggan, BBC Micro) analysed for the CPC port

Sources read (reference only, nothing copied into the repo): the annotated source `work/ext_elitea/` (https://github.com/markmoxon/elite-a-source-code-bbc-micro, every change marked `Mod:`: 226 markers in the docked file, 183 in the flight file, 98 in the encyclopedia), Angus Duggan's manual page (http://knackered.org/angus/beeb/elite.html), and the deep dives https://elite.bbcelite.com/deep_dives/elite-a_buying_and_flying_ships.html and https://elite.bbcelite.com/deep_dives/elite-a_making_room_for_the_modifications.html. Elite-A is the BBC disc Elite plus the extras below; the extra code is Angus Duggan's, so this is analysis, not a code source for us.

## 1. Feature list (from the manual)

| Area | What Elite-A adds or changes |
|---|---|
| Player ships | Start in an Adder, buy and fly 15 ships (Adder, Gecko, Moray, Cobra Mk I, Iguana, Ophidian, Chameleon, Cobra Mk III, Fer-de-Lance, Ghavial, Monitor, Python, Boa, Asp Mk II, Anaconda, ordered by price). Ships differ in speed, turn rate, missile pylons (1 to 12), laser mounts (1, 2 or 4), cargo (up to 250 t), shields, hyperspace range and equipment prices. |
| Shipyard | CTRL-f3 buys a ship, CTRL-f2 sells equipment at half price. Ships on offer = 15 - 2 x economy (0-7): poor agricultural systems sell only the Adder, rich industrial ones all 15. Part exchange refunds the old ship; equipment and cargo are lost, legal status resets to clean. |
| New hulls | Bushmaster, Chameleon, Ghavial, Iguana, Monitor, Ophidian (and Adder, Gecko, Moray, Cobra Mk I, Boa, Anaconda, Transporter, Shuttle, Worm as in the BBC original); the 6502 second processor build shows more varied ship combinations. |
| Equipment | Energy bomb and large cargo bay removed; Hyperspace Unit (instant jump to a random system, single use) and I.F.F. system (colours the scanner bars: white station, blue clean, blue and red offender, blue and white debris, white and red missile) added. Missiles no longer kill outright but do heavy damage. |
| Missions | Special cargo delivery (documents, medical supplies, passengers, illegal goods): one at a time, time limited, reward falls with delay. |
| Encyclopedia | CTRL-f6: ship cards with stats around the edge and a rotating 3D wireframe in the middle, controls and equipment pages; a third program loaded on demand. |
| Combat and law | Damage by ramming scales with relative size and counts as aggression; shooting innocent traders hurts legal status; "most wanted" gets police attacks at stations; Thargoids much harder; encounters appear at random positions in the forward quadrant and further away, with asteroid showers, trader convoys, police squadrons and pirate clans. |
| Interface | Docking fee (50 Cr) to stay docked and let prices change; hyperspace countdown locks the controls; "Are you sure (y/n)" on save and load; status screen shows the ship type; "missiles low" display; Delta 14B joystick support; incompatible save format (ship type byte added). |
| Variants | Released version, source disc version (lower ship prices), bug fix version (splinter bug fixed, Master support). |

## 2. How buying and selling ships works (the part worth copying)

Data (all in the docked program):
- `new_ships`: 15 entries of 9 bytes name + 4 bytes price (13 B each, 195 B).
- `new_details`: 13 bytes per ship (195 B): pulse, beam, military and mining laser power, laser mounts (1, 2, 4), maximum missiles + 1, shields, energy recharge rate, maximum speed, hold capacity + 1, hyperspace range (LY x 10), offset into the equipment price table `PRXS`, maximum roll/pitch rate (the minimum is 255 minus it). Example: Adder 14/142/146/25 lasers, 2 mounts, 1 missile, shields 4, speed 36, hold 8 t, range 6.0 LY, roll rate 223; Cobra Mk I: 4 mounts, 3 missiles, shields 5, speed 39, hold 14 t.
- `PRXS`: equipment prices in blocks of 26 bytes (13 two-byte prices, one block per ship family; `new_costs` selects the block), so newer and rarer ships pay different prices for the same equipment.
- Player state: one byte `cmdr_type` (the ship type, in a byte the original left over from dropped up/down lasers) is the only thing saved; `n_load` re-expands the 13 flight bytes from `new_details` into a workspace block and patches the ship name text token whenever a ship is bought or a commander is loaded. The flight code reads that block instead of constants (speed limit, roll/pitch rate, shield level, laser power, missile limit, hyperspace range).
- `n_buyship` (called from `EQSHP` when CTRL is held): price list for the system, part exchange, zeroes the equipment block (`LASER` to `LASER+36`) and the legal status, sets fuel to the new range, resets the missile indicators.
- Space tricks (Angus's "making room" article): docked, flight and encyclopedia are three separate programs; about 60 docked and 14 flight routines were removed (dashboard code from the docked program, energy bomb from the flight program), repeated code turned into subroutines (a few bytes each), the disc catalogue routine replaced; the only hook into the docked code for the encyclopedia is a check in the trade menu. Everything is paid for in bytes of a 64 KB machine, which is the same fight as ours.

## 3. What would it take on the CPC build (128K, `src/elite128`)

| Piece | Size | Where it fits | Effort and risk |
|---|---|---|---|
| Ship tables (15 x 13 B names/prices, 15 x 13 B details, price blocks) | about 0.5 KB | bank 4 (9.4 KB free), copied to a 13 byte resident block when a ship is bought or a commander is loaded | low |
| Shipyard screen and `n_buyship`/sell logic, in Z80 | about 0.5-0.8 KB | a docked overlay like the mission overlays, loaded from bank 4 on demand; the existing overlay window `&17FD-&1A3F` is 578 B and has 0 spare, but the unused bitmap `&A000-&A5FF` (1.5 KB) is free while docked | medium |
| Flight code reads the ship block (speed limit, roll and pitch rate, shield maximum, laser power, missile limit, fuel range) instead of constants | about 15-25 sites, +2-3 bytes each | bank 7 has **1 byte** spare: first free about 300 B there (the title selection tables at the end of the block are only used at the title and can move to a bank) | medium-high: it touches the flight loop, the save key and the savegame layout |
| Player ship types as hulls | the 15 ships | the 128K build already has Cobra III, Python, Fer-de-Lance, Asp, Viper, Sidewinder, Krait, Thargoid; Adder, Gecko, Moray, Cobra Mk I, Boa and Anaconda are in the BBC-ships plan; Iguana, Ophidian, Chameleon, Ghavial, Monitor exist only in Elite-A's own blueprints (6502 format: vertices, edges, faces; our `ship128.py` needs triangle lists, which would have to be derived from faces and edges) | medium-high |
| Savegame | one byte for the ship type (the CPC save has 104 bytes and a code-derived XOR key) | an unused byte | low, but saves become incompatible with the stock game (already true for the mission bytes) |
| Equipment changes (Hyperspace Unit, I.F.F., half price selling, docking fee) | small | overlay + flight hooks | low-medium each |
| Special cargo missions | similar to our mission overlays | bank 4 overlays | medium (text per language) |
| Encyclopedia | ship cards use a rotating wireframe: we already have a filled hull renderer and the title ship display | a docked overlay program of 2-4 KB in a bank, using the hull fill | medium, nice with the filled ships |

## 4. Other key changes worth considering (cheapest value first)

1. **I.F.F. scanner colours** (the scanner draws with one pen today; mode 1 gives four pens: bars could use pen 1/2/3 by object type): small, needs the pen set of the cockpit.
2. **Missile damage instead of instant kill, ramming damage by size, legal status for shooting traders**: balance changes in the kill and damage code, no new memory.
3. **Docking fee / hyperspace countdown lock / Are-you-sure prompts**: tiny.
4. **Random encounter variety** (convoys, police squadrons, pirate packs): spawn table work, ties in with the BBC ships plan.
5. **Hyperspace Unit and Delta-14B**: only the unit is relevant (CPC has no Delta 14B).
6. **Ship purchase** (this report, section 3): the largest piece and the one that changes the game most.

## 5. Recommendation

Keep Elite-A as a **later, optional phase** (`-DELITE_A`), after the language work and the BBC ships: the shipyard needs the same resident-byte discipline as the BBC ships, plus about 300 B freed in bank 7, plus parametrising the flight constants. If we want it, split it: (a) ship block in a resident variable + flight code reading it, with only the Cobra Mk III (no visible change, proves the mechanism); (b) shipyard overlay with the six ships we get from the BBC-ships plan; (c) the remaining Elite-A hulls and the encyclopedia. The cheap items in section 4 can go in anytime.

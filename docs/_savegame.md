# Commander save format (decoded 2026-11-07)

A save is 104 bytes (`&68`), the RAM block `&38CB-&3932`, written by `saveGame` in `LARGEAXX`. Load address `&39D2` on the
save disk (`&38CB` for `1.BIN`). `tools/savedec.py` decodes one; `tools/saveedit.py` edits one.

- **Encryption**: `encryptSAV` XORs the block with the `&68` bytes of code at `EquipShip` (file offset `&2BE` in stock
  `LARGEAXX`, `&2C2` in the German one). A save only decodes with the same build's code, which is why Fessor's patched builds
  re-key it. `tools/elitekey.py DISK.dsk` reads the key from the disk. The saves on `Elite_DE_savegames.dsk` are German;
  `1.BIN` on `Elite_UK_original_protected.dsk` is stock English.
- **Checksums** (plain data): byte `&66` = XOR of bytes 0-`&65` (`CryptRun1`), byte `&67` = sum of bytes 0-`&66` mod 256
  (`getChecksum`). Loading checks the sum; the XOR sets the "modified" flag (bit 5 of the file-menu checksum).
- The default commander is at `&39C7` (name JAMESON) and is copied to `&38CB` on a new game.

## Field map

| Offset (RAM) | Meaning |
|---|---|
| 0-10 (`&38CB`) | name, up to 10 characters plus NUL; bytes after the NUL are leftovers of "JAMESON". The disk file name uses the first 8 |
| 11 (`&38D6`) | `legalStatus` (status page: 0 clean, 1-49 offender, 50-255 fugitive: `cp &32` in the status code; the game halves it at every jump; the cops are said to turn hostile from about 40, not checked) |
| 12-14 (`&38D7-&38D9`) | `killScore`, 24 bits: `&38D7`/`&38D8` low word, `&38D9` `killScoreHigh` (a carry into it prints "RIGHT ON COMMANDER"; the cloaking-device and supernova rewards add 1); `getRank` reads them |
| 15-16 (`&38DA`) | `jumpCounter` (missions) |
| 17 (`&38DC`) | `currentGalaxy`, 0-7 |
| 18-21 (`&38DD-&38E0`) | credits as a word pair: `creditsHighWord` (`&38DD`, high byte `creditsHighWordHi` `&38DE`) counts 1,000 Cr (10,000 decicredits), `creditsLowWord` (`&38DF`) holds the decicredits below 10,000; default `E8 03` = 100.0 Cr. **Not** a 32-bit number (tested: high 2, low 2500 shows 2250.0 Cr; high 65000 gives 65,000,000 Cr). Maximum 65,535,999.9 Cr |
| 22 (`&38E1`) | market random byte: `GenPriceAndStockEntry1` stores the RNG byte here and `GeneratePricesAndStock` masks it into every price and stock. The escape-pod code clears 17 bytes from here (this byte and goods 0-15), so it misses alien items (`&38F2`) |
| 23-39 (`&38E2`) | `cargoHold`, one byte per good (0 food ... 16 alien items). `cargoSlaves` (`&38E5`), `cargoNarcotics` (`&38E8`), `cargoFirearms` (`&38EC`) are goods 3, 6, 10, the illegal ones in `chkForIllegalGoods` |
| 40 (`&38F3`) | `cargoSpaceFree` in tonnes (scooping decrements it); 20 by default, 35 with the large cargo bay |
| 41-44 (`&38F4`) | `laserTypes`, one per view (front, rear, left, right): 0 none, 1 pulse, 2 beam, 3 military, 4 mining |
| 45 (`&38F8`) | `FlightMode` |
| 46 (`&38F9`) | `fuel` in 0.1 LY, max 70 |
| 47 (`&38FA`) | `missileCount` (3 by default) |
| 48 (`&38FB`) | `largeCargoBay` (selects 35 t instead of 20 t) |
| 49 (`&38FC`) | `ecmEquipped` (bit 7 is cleared when docking) |
| 50-51 (`&38FD`, `&38FE`) | `equipSlotPulseLaser`, `equipSlotBeamLaser`: never read or written. Equipment bytes are indexed from `&38F8` by shop item number (`selectEquipmentOfShip`: item 3 is `&38FB`, 4 is `&38FC`, 7-12 are `&38FF-&3904`); items 5 and 6 are lasers, which live in `laserTypes` |
| 52-57 (`&38FF-&3904`) | equipment flags, `&FF` when fitted: `fuelScoops`, `escapePod`, `energyBomb`, `extraEnergyUnit`, `dockingComputer`, `galacticHyperdrive` (shop items 7-12) |
| 58-59 (`&3905`, `&3906`) | `equipSlotMilitaryLaser`, `equipSlotMiningLaser`: unused, same reason (items 13, 14) |
| 60-65 (`&3907`) | `galaxySeed`, default `4A 5A 48 02 53 B7` (the BBC Jameson seed) |
| 66-71 (`&390D`) | `presentSystemSeed`; `presentSystemY` is byte 1 (`&390E`), `presentSystemX` byte 3 (`&3910`) |
| 72 (`&3913`) | `presentTechLevel`: tech level of the present system minus 1 (the data screen prints value + 1); copied from `techLevel` at each arrival and used by `EquipShip` (+2, capped) as the equipment limit. After a jump to Diso the data screen showed 8 and the byte held 7. The default block holds 5 (Lave shows 5), so a fresh game is not value-1 until the first arrival. (Formerly misnamed `marketRandomByte`; that is `&38E1`) |
| 73-89 (`&3914`) | `marketStock`, 17 entries |
| 90 (`&3925`) | `AlienItemsForSale` (likely) |
| 91-92 (`&3926-&3927`) | `ThargonMissionVar`, `Missionflag` |
| 93-101 (`&3928-&3930`) | `savedSunPosX/Y/Z` (3 bytes each: low, high, sign): `saveGame` copies the 9 bytes of `posDataSun` (`&1C26`) here, `setupNewGame` copies them back from `storedPlanet3dcoords`. Sign bytes at +2, +5, +8 are tested at `chalt` (likely) |
| 102, 103 | checksums |

Offsets 41-44, 48, 49, 52-57 and 90 are inferred rather than traced ("likely"); the rest is confirmed. The layout differs from
the BBC one. `LEN` and `LEN.BAK` are played commanders with edited-looking values (legal 25-43, cargo bytes 248/18/16, 441 Cr),
so use `PETER`, `PETE` and `1.BIN` as clean references.

## Cross-check with the CPC International type-in

*ELITE: Commander nach Wunsch*, Schneider CPC International Sonderheft 3/86, pp. 67-68 (Thomas Kochmann; `magazines/elite-commander.pdf`,
text in `magazines/text/elite-commander.txt`). A BASIC program builds a commander at `&A000` (offset 0 = `&38CB`) and `SAVE`s the
104 bytes to tape. It was written against an earlier German build, but its offsets match the table with two exceptions, settled on
2026-11-07 by running the game in cpcxray (launch, short range chart, move the cursor, `h`, data screen):

- `&48` **is the tech level minus 1**, as the type-in says (our table had called it `marketRandomByte`).
- The game keeps **y at `&43` and x at `&45`** (`presentSystemY` `&390E`, `presentSystemX` `&3910`); the type-in's x and y are swapped,
  or its build used the other order. Evidence: the chart cursor X (`PresentPlanetX`, `&3934`) changes with cursor left/right and the
  galactic chart puts Lave (`14 AD` = 20, 173) at the far left; after a jump the cursor read `0B AE` and `&390D-&3912` read
  `98 AE 34 0B CD 8D`, so `&390E` = `AE` (y), `&3910` = `0B` (x). Its galaxy table lists the two centre bytes in the type-in's order, i.e. (y, x) in ours.

Other details it confirms: `Missionflag` (`&5C`) **`&40` = cloaking device, `&80` = E.C.M. jammer**; equipment `&FF` when fitted
(`&30` large cargo bay, `&31` E.C.M., `&34` scoops, `&35` escape pod, `&36` energy bomb, `&37` extra energy unit, `&38` docking
computer, `&39` galactic hyperdrive). Cargo `&17-&26` is 16 goods (tonnes; gold and platinum in kg, gems in g): food, textiles,
radioactives, slaves, liquor/wines, luxuries, narcotics, computers, machinery, alloys, firearms, furs, minerals, gold, platinum,
gems (our table adds a 17th, alien items). Market stock `&4A-&59` uses the same order.

Rank thresholds (kill score): Harmless 0-2303, Mostly Harmless 2304-4351, Poor 4352-8447, Average 8448-16639, Above Average
16640-33023, Competent 33024-196607, Dangerous 196608-720895, Deadly 720896-1703935, Elite from 1703936.

Galaxy table (hex; each seed is the previous one with every byte rotated left once, as used for the mission target names):

| Galaxy | Seed | Centre (y, x in our order) | Last byte (stored at `&48`) |
|---|---|---|---|
| 1 | `4A 5A 48 02 53 B7` | `79 85` | `09` |
| 2 | `94 B4 90 04 A6 6F` | `83 84` | `06` |
| 3 | `29 69 21 08 4D DE` | `78 82` | `0C` |
| 4 | `52 D2 42 10 9A BD` | `7A 86` | `07` |
| 5 | `A4 A5 84 20 35 7B` | `90 80` | `05` |
| 6 | `49 4B 09 40 6A F6` | `75 82` | `07` |
| 7 | `92 96 12 80 D4 ED` | `7C 7F` | `09` |
| 8 | `25 2D 24 01 A9 DB` | `7B 80` | `07` |

The type-in's own encryption data (104 hex bytes, lines 1650-1770, XORed over `&A000-&A067`) is the key of that earlier build
(it starts `21 16 4F CD C3 6B ...`, a `ld hl,&4F16 / call &6BC3` sequence). It matches none of our binaries (101 of 104 bytes
differ from the stock English key, likewise from the German), so type-in saves load only on that earlier build.

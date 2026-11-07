## Commander save format (decoded 2026-11-07)

A save is 104 bytes (`&68`), the RAM block `&38CB-&3932`, written by `saveGame` in `LARGEAXX`. Load address
`&39D2` on the save disk (`&38CB` for `1.BIN`). `tools/savedec.py` decodes one.

- **Encryption**: `encryptSAV` XORs the block with the `&68` bytes of code at `EquipShip` (file offset `&2BE` in
  stock `LARGEAXX`, `&2C2` in the German one). So a save only decodes with the same build's code, which is why
  Fessor's patched builds re-key it. `tools/elitekey.py DISK.dsk` reads the key from the disk itself, so nothing needs extracting. The saves on `Elite_DE_savegames.dsk` are from the **German** build; `1.BIN` on
  `Elite_UK_original_protected.dsk` is from the stock English one.
- **Checksums** (plain data): byte `&66` = XOR of bytes 0-`&65` (`CryptRun1`), byte `&67` = sum of bytes
  0-`&66` mod 256 (`getChecksum`). Loading checks the sum, and the XOR sets the "modified" flag (bit 5 of the
  file-menu checksum). All five saves verify.
- The default commander is at `&39C7` (name JAMESON) and is copied to `&38CB` on a new game.

| Offset (RAM) | Meaning | Confidence |
|---|---|---|
| 0-10 (`&38CB`) | name, up to 10 characters plus NUL (the type-in below truncates to 10); characters after the NUL are leftovers of "JAMESON". The file name on disk uses the first 8 | sure |
| 11 (`&38D6`) | `legalStatus` (0 clean, 25 offender, 40+ fugitive, hostile cops) | sure |
| 12-14 (`&38D7-&38D9`) | `killScore`, 24 bits: `&38D7`/`&38D8` low word, `&38D9` `killScoreHigh` (a carry into it prints "RIGHT ON COMMANDER"; the cloaking-device and supernova rewards add 1 to it); `getRank` reads them | sure |
| 15-16 (`&38DA`) | `jumpCounter` (missions) | sure |
| 17 (`&38DC`) | `currentGalaxy`, 0-7 | sure |
| 18-21 (`&38DD-&38E0`) | credits as a word pair: `creditsHighWord` at `&38DD` counts 1,000 Cr (10,000 decicredits), `creditsLowWord` at `&38DF` holds the decicredits below 10,000; default `E8 03` = 100.0 Cr. **Not** a 32-bit number: tested in the game, high 2 and low 2500 shows 2250.0 Cr; the CPC International type-in and a 65,000,000 Cr test (high 65000) agree. Maximum 65,535,999.9 Cr | sure |
| 22 (`&38E1`) | the market random byte: `GenPriceAndStockEntry1` stores the RNG byte here and `GeneratePricesAndStock` masks it into every price and stock. The escape-pod code clears 17 bytes from here, i.e. this byte and goods 0-15, which misses alien items (`&38F2`) | likely |
| 23-39 (`&38E2`) | `cargoHold`, one byte per good (0 food ... 16 alien items). `cargoSlaves` (`&38E5`), `cargoNarcotics` (`&38E8`), `cargoFirearms` (`&38EC`) are goods 3, 6 and 10, the illegal ones in `chkForIllegalGoods` | sure |
| 40 (`&38F3`) | `cargoSpaceFree` in tonnes (scooping decrements it); 20 by default, 35 with the large cargo bay | sure |
| 41-44 (`&38F4`) | `laserTypes`, one per view | likely |
| 45 (`&38F8`) | `FlightMode` | sure |
| 46 (`&38F9`) | `fuel` in 0.1 LY, max 70 | sure |
| 47 (`&38FA`) | `missileCount` (3 by default) | sure |
| 48 (`&38FB`) | `largeCargoBay` (selects 35 t instead of 20 t) | likely |
| 49 (`&38FC`) | `ecmEquipped` (bit 7 is cleared when docking) | likely |
| 50-51 (`&38FD`, `&38FE`) | `equipSlotPulseLaser`, `equipSlotBeamLaser`: never read or written. The equipment bytes are indexed from `&38F8` by shop item number (`selectEquipmentOfShip`: item 3 is `&38FB`, 4 is `&38FC`, 7-12 are `&38FF-&3904`), and items 5 and 6 are lasers, which live in `laserTypes` | sure (by index) |
| 52-57 (`&38FF-&3904`) | equipment flags, `&FF` when fitted: `fuelScoops`, `escapePod`, `energyBomb`, `extraEnergyUnit`, `dockingComputer`, `galacticHyperdrive` (shop items 7-12) | likely |
| 58-59 (`&3905`, `&3906`) | `equipSlotMilitaryLaser`, `equipSlotMiningLaser`: unused, same reason (items 13 and 14) | sure (by index) |
| 60-65 (`&3907`) | `galaxySeed`, default `4A 5A 48 02 53 B7` (the BBC Jameson seed) | sure |
| 66-71 (`&390D`) | `presentSystemSeed`, the seed of the system you are in; `presentSystemY` is byte 1 (`&390E`), `presentSystemX` byte 3 (`&3910`) | sure |
| 72 (`&3913`) | `presentTechLevel`: tech level of the system you are in, minus 1 (the data screen prints value + 1); copied from `techLevel` at each arrival, and `EquipShip` uses it (+2, capped) as the equipment tech limit. Formerly named `marketRandomByte`, wrong: that is `&38E1`. Measured 2026-11-07: after a jump to Diso the data screen showed 8 and the byte held 7. The default commander block holds 5 here (Lave shows 5), so a fresh game is not yet value-1 until the first arrival | sure |
| 73-89 (`&3914`) | `marketStock`, 17 entries, varies per save | sure |
| 90 (`&3925`) | `AlienItemsForSale` | likely |
| 91-92 (`&3926-&3927`) | `ThargonMissionVar`, `Missionflag` | sure |
| 93-101 (`&3928-&3930`) | `savedSunPosX`, `savedSunPosY`, `savedSunPosZ` (3 bytes each: low, high, sign): `saveGame` copies the 9 bytes of `posDataSun` (`&1C26`) here, and `setupNewGame` copies them back from `storedPlanet3dcoords`. Fessor's name was `SGstoreSystem3DCoordinates`. Sign bytes at +2, +5, +8 are tested in the code at `chalt` | likely |
| 102, 103 | checksums | sure |

The layout differs from the BBC one (name, mission, position, seeds, cash ...). `LEN` and `LEN.BAK` are played
commanders (legal status 25-43, kills, 441 Cr, cargo bytes of 248/18/16 look edited), so use `PETER`, `PETE`
and `1.BIN` as the clean references.

### Cross-check with the CPC International type-in (`magazines/elite-commander.pdf`)

*ELITE: Commander nach Wunsch*, Schneider CPC International Sonderheft 3/86, pages 67-68 (Thomas Kochmann; text in
`magazines/text/elite-commander.txt`). A BASIC program builds a commander in RAM at `&A000` (the save block, offset 0 =
`&38CB`) and `SAVE`s the 104 bytes to tape. It was written against an earlier German build, but every offset it pokes
matches the table above except the two noted below:

- Name `0-9` plus NUL (10 characters); legal status `&0B`; kill score `&0C-&0E` (low, mid, high); galaxy `&11` (0-7);
  credits `&12/&13` = thousands of Cr and `&14/&15` = remaining decicredits (it computes `INT(x/1000)` and `(x mod 1000)*10`);
  fuel `&2E` = 10 x light years; missiles `&2F`; free hold `&28`; galaxy seed `&3C-&41`; checksums `&66` (XOR) and `&67` (sum).
- Lasers `&29-&2C` (front, rear, left, right): 0 none, 1 pulse, 2 beam, 3 military, 4 mining.
- Equipment, `&FF` when fitted: `&30` large cargo bay, `&31` E.C.M., `&34` fuel scoops, `&35` escape pod, `&36` energy bomb,
  `&37` extra energy unit, `&38` docking computer, `&39` galactic hyperdrive. `&32` and `&33` are not touched by it.
- `Missionflag` `&5C`: **`&40` = cloaking device, `&80` = E.C.M. jammer**. This confirms the bits found in the code.
- Cargo `&17-&26`, 16 goods in this order (tonnes; gold and platinum in kg, gems in g): food, textiles, radioactives, slaves,
  liquor/wines, luxuries, narcotics, computers, machinery, alloys, firearms, furs, minerals, gold, platinum, gems.
  Market stock of the present system `&4A-&59`, same order. (Our table counts 17 goods because of the alien-items slot.)
- Sets `&65` to `&FF` (last of the nine bytes copied from `&1C26`).
- The two disagreements are settled (2026-11-07, game run in cpcxray: launch, short range chart, move the cursor, `h`, then the data screen):
  - `&48` **is the tech level minus 1**, as the type-in says. Our table had called it `marketRandomByte`, which was wrong (now `presentTechLevel`).
  - Planet order: the game keeps **y at `&43` and x at `&45`** (`presentSystemY` `&390E`, `presentSystemX` `&3910`). The type-in's "x" and "y"
    are swapped, or its earlier build used the other order. Evidence: the chart cursor X (`PresentPlanetX`, `&3934`) changes with cursor left/right and
    the galactic chart puts Lave (`14 AD` = 20, 173) at the far left and lower half; after the jump the cursor read `0B AE` and `&390D-&3912` read
    `98 AE 34 0B CD 8D`, so `&390E` = `AE` (y) and `&3910` = `0B` (x). Its galaxy table below lists the two centre bytes in the type-in's order, i.e. (y, x) in ours.

Rank thresholds from its menu (kill score; the score counts kills): Harmless 0-2303, Mostly Harmless 2304-4351, Poor
4352-8447, Average 8448-16639, Above Average 16640-33023, Competent 33024-196607, Dangerous 196608-720895, Deadly
720896-1703935, Elite from 1703936.

Its galaxy table (hex, nine bytes per galaxy: the 6-byte seed, then the centre system's two coordinates and one more
byte it stores at `&48`); each seed is the previous one with every byte rotated left once, as already used for the
mission target names:

| Galaxy | Seed | Centre x, y | Last byte |
|---|---|---|---|
| 1 | `4A 5A 48 02 53 B7` | `79 85` | `09` |
| 2 | `94 B4 90 04 A6 6F` | `83 84` | `06` |
| 3 | `29 69 21 08 4D DE` | `78 82` | `0C` |
| 4 | `52 D2 42 10 9A BD` | `7A 86` | `07` |
| 5 | `A4 A5 84 20 35 7B` | `90 80` | `05` |
| 6 | `49 4B 09 40 6A F6` | `75 82` | `07` |
| 7 | `92 96 12 80 D4 ED` | `7C 7F` | `09` |
| 8 | `25 2D 24 01 A9 DB` | `7B 80` | `07` |

Its encryption data (104 hex bytes, lines 1650-1770, XORed over `&A000-&A067`) is the key of that earlier build, the code
at its `EquipShip` (it starts `21 16 4F CD C3 6B ...`, a `ld hl,&4F16 / call &6BC3 ...` sequence). Those bytes are not in
any of our binaries (they differ from the stock English key in 101 of 104 bytes and from the German key likewise), so
saves made by the type-in load only on that earlier build, not on ours.


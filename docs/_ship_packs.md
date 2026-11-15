# Ship packs and traffic (`-DMISSIONS`, English; `-DTRAFFIC` in all three trees)

The stock CPC game has 19 ship types, like the Spectrum. The BBC, C64 and Fessor's beta also have Mamba, Adder, Gecko, Cobra Mk I, Worm, Moray, Boa, Anaconda, Shuttle, Transporter, Boulder (and Cougar, Dodecahedron on the C64). Written 2026-11-14; the hook and the picker are tested in cpcxray (`tools/test_ship_packs.py`, `tools/test_launch.py`), nothing is played through yet.

## Packs

A **pack** is a flight image `MFLIGHT1..7.BIN` (the tail `&9D9E-&9FFD`, see `_missions_built.md`): the default image plus one or two extra hulls and a `mxShipTableImpl` (`src/elite/missions_flight_k.asm`) that swaps them in for a stock type, on half the spawns (bit 0 of `getRandomNumber`), so the stock ships stay. Hulls are Fessor's (`src/elite/missions_ships.asm`, made by `tools/fessor_ships.py` from `extended/source/`, used with his permission and credited in `README.md`); the blueprint layout is the CPC one, so no other table needs an entry.

| Pack | Hulls (bytes) | Replaces (stock type) | Image |
|---|---|---|---|
| 1 | Gecko 199, Cobra Mk I 201 | 16 Sidewinder, 17 Krait | 606 |
| 2 | Worm 179, Moray 219 | 16 Sidewinder, 17 Krait | 604 |
| 3 | Mamba 305 | 16 Sidewinder | 504 |
| 4 | Adder 307 | 17 Krait | 506 |
| 5 | Boa 249 | 10 Python trader | 448 |
| 6 | Anaconda 261 | 10 Python trader | 460 |
| 7 | Shuttle 309 | 9 Cobra Mk III trader | 508 |

The image limit is 608 bytes (`ASSERT mxFlightEnd <= &9FFE`); the default image is 182 (sizes as of 2026-11-15, with the kill count routine every image carries). Never redirected: 8 (police Viper), 15 (Thargoid), 18 (Thargon): the Thargoid and plans missions need them. Not included: Boulder (165 bytes; with the Boa the image is 9 bytes over), Transporter (485) and the Dodecahedron (do not fit). Role flags, bounty, missiles and kill value come from Fessor's headers (a Gecko is worth 0.5 kills, a Mamba 0.75, an Anaconda 1.5; see `_gameplay.md`).

## Which pack, and when it loads

`mxLaunchEntry` (`missions_flight.asm`) keeps its mission priority (Trumbles, Constrictor, plans, stolen ship, asteroids). With no mission it asks for pack `(jumpCounter + presentSystemSeed) & 7`: `0` is the default image (no extras), `1` to `7` a pack. `jumpCounter` (`&38DA`) goes up at every arrival and `presentSystemSeed` changes with the system, so the pack changes from visit to visit but is the same for every launch from one station. The hook compares with `mxFlightId` (`&9DB9`) and loads only when the pack differs. No save byte is used. Cost: the picker is 9 bytes in every image (the Trumbles image saved 2 with `set 2,l`, so it is at 607 of 608).

Measured in cpcxray (`tools/test_launch.py`): a launch that keeps the image in RAM takes 2.06 s (the `INDICATO` load alone), one that loads a pack or mission image 4.0 s. So the first launch after a jump pays about 2 s more in 7 of 8 visits; relaunching from the same station does not. During the load the docked screen stays frozen with the game's interrupt handler off; nothing is drawn.

Ideas to hide that load, not built: (1) load the pack at the end of `DockingSequence`, over the last tunnel frame that is already frozen for the `LARGEAXX` load; (2) read it in chunks with `CAS_IN_CHAR` during the launch tunnel (needs a 2 KB buffer that survives the tunnel: `&0040` is in use after the swap, `&A000` is cleared every frame, so probably not); appending a pack to `INDICATO.BIN` leaves room for one pack only (about 512 bytes).

## Traffic (`-DTRAFFIC`)

One spawn check per 256 passes on the CPC and the C64 alike; what differs is what a check produces. The C64 gives about 1.4 times the hostiles per check (up to 1.9 in anarchy), 3.5 times the junk, and has 8 ship slots against 6 (counted from the source, not measured). `-DTRAFFIC` moves two roll operands and the escort pack size towards the C64; the default build keeps the stock bytes, the disk build (`tools/build_dsk.py`) turns it on. The named values are in `commonxx.asm` before `chkSpawnAsteroid`, with the stock value in the comment:

| Name | Stock | `-DTRAFFIC` | C64 |
|---|---|---|---|
| `SPAWN_HOSTILE_LIMIT` (roll below it lets a hostile through, 256 = 100%) | `0x50` (31%) | `0x5A` (35%) | `CMP #90` |
| `SPAWN_JUNK_WIDTH` (the next values make an asteroid) | 10 (3.9%) | 35 (13.7%) | `CMP #35` |
| escort pack size (`spawnPackSlot`) | 2 to 4 (mean 3.0) | 1 to 4 (mean 2.5) | `(rnd & 3) + 1` |

The pack size matches the C64's range but not its effect on the average: the stock roll gives 2,3,3,4 ships, `(rnd & 3) + 1` gives 1,2,3,4, so packs get a little smaller and 1-ship packs appear.

Not changed: the slot count (the slot area is fixed in `_memory_map.md`), the C64's junk cap of 3 and the 4-ship gate (no spare bytes in the main binary), and the share of packs against lone hunters (C64 61%, CPC about 25%; set by a bit test, not an operand). With 6 slots and no cap, 13.7% junk may crowd out hostiles: if so lower `SPAWN_JUNK_WIDTH` (try 20). `check_src.sh` proves the default is the original and `-DTRAFFIC` differs only in those five bytes, in all three trees.

## Tests

- `tools/test_ship_packs.py [PACK ...]` (from `work/xray`): for each pack, calls `mxShipTable` 60 times per redirected type and checks the extra hull comes up about half the time, the stock one otherwise, types 8, 15, 18 are never redirected, and A, BC, DE survive.
- `tools/test_launch.py`: picker scenarios (`pack_*`, mission and Trumbles priority) and the image bytes against the disk files.
- `tools/test_flight_hull.py 16 --fl 3 --extra shipdatMamba`: spawns the pack's hull and writes `output/missions_ship.png`.

# How pirates are spawned: CPC, BBC, C64 and Atari ST

Why this note exists: pirates seem to appear in the top right of the view in the 128K build (`TODO_128K.md`). It compares the CPC code (`src/elite/commonxx.asm`, the same in `src/elite128/`) with the 6502 versions (BBC and C64, the commented sources in `work/ext_bbc` and `work/ext_c64`) and the Atari ST original (`work/ext_st/repo/src_orig/asm/combat.m68`). The third-party sources are read-only references: nothing here is copied from them. Findings on the CPC marked "measured" come from calling `spawnShip` in cpcxray on the 128K build (2026-11-21).

## The short version

| | BBC / C64 | CPC (stock and 128K) | Atari ST |
|---|---|---|---|
| Where a ship starts | one of the four diagonal corners ahead: x, y and z each 8,192 (BBC) or 6,400 (C64) | ahead, z = 12,800; x and y of about 12,800 (the corner of the view) or, for pirate types, within about 2,300 of the centre | a random point on a sphere of radius 16,384 to 24,576 around the player, so also behind |
| Left/right, up/down | from bit 7 of two consecutive random numbers (the second is the first one's predecessor, so not fully independent) | from two bits of one random number | two random angles, 0 to 360 |
| A group | 1 to 4 ships added from one workspace: they all start at the same spot | each ship through `spawnShip`: its own random position | a leader plus wingmen in formation (offsets along its own x and y axes) |
| Where it can happen | anywhere in flight | anywhere in flight | deep space only, and only while fewer than 2 pirates are around |
| How often | 35% per attempt, only if the random 0 to 7 is not below the government number (anarchy always) | one roll per 256 passes of the main loop, hostile below 80/256 (stock) or 90/256 (`-DTRAFFIC`, the C64 value) | a counter reloaded with (government + 2) x 512: lawless systems wait longer |

No version has a fixed top-right start. **In all three 8-bit versions a new ship always starts in front of the player** (the sign of z is never set): pirates only come from the front, and in the rear and side views they show up after they have flown past or turned. Only the Atari ST spawns all around.

## BBC and C64 (6502)

Main loop part 4. An "extra vessels" counter delays the checks. When it runs out: a 35% chance (random below 90), then the government filter (a random 0 to 7 below the system's government number means no spawn; anarchy skips it, so lawless systems spawn more). The routine `Ze` clears the ship workspace and sets x, y and z to the same distance, with the signs of x and y taken from bit 7 of two random numbers; the comments in both sources point out that the location is therefore not totally random.

A further roll chooses between a group and a lone ship: BBC 13% group (random 200 or more), otherwise a lone Mamba, Python or Cobra Mk III, or a Thargoid; C64 61% group (random 100 or more), otherwise a lone bounty hunter. A group is 1 to 4 ships (the pirate counter counts down to minus one), each added with the same workspace, so the whole group sits on one point. BBC types: Sidewinder or Mamba. C64 types: one of eight blueprints from the Sidewinder up (Mamba, Krait, Adder, Gecko, Cobra Mk I, Worm, Cobra Mk III pirate), small numbers more likely (two random numbers ANDed).

## CPC (stock, same in the 128K build)

`spawnShip` copies an initial block in which x, y and z are all `&3200` (12,800), then: the low bytes of x and y are random; for the types whose blueprint byte has bit 2 clear (the pirate-like ones; measured: types `&06` and `&0A`) the high bytes of x and y become a random 0 to 7, so those ships start within about 23 px of the view centre; the other types (measured: `&10`) keep `&32xx`, the corner. The signs of x and y are two bits of one random number. z is always ahead. Measured over 80 calls per type: the four quadrants come out about equally (e.g. 24/13/20/23), the 128K build changes nothing here.

The pick itself (`spawnCommand0`): a roll below `SPAWN_HOSTILE_LIMIT` (`&50`, `&5A` with `-DTRAFFIC`) lets a hostile through, the next `SPAWN_JUNK_WIDTH` values (10, 35 with `-DTRAFFIC`) make an asteroid; the type comes from further rolls, the marked Asp and the mission states have their own paths. `spawnEscortPack` makes 2 to 4 (1 to 4 with `-DTRAFFIC`) Sidewinders or Kraits, each through `spawnShip`.

## Atari ST

`create_pirates` runs only in deep space (not near a planet or station) and only while fewer than 2 pirates exist. A counter reloaded with (the planet's government + 2) x 512 decides when; then `pirate_attack` (also called for the missions) prints "Condition RED!", stops the torus drive and restores the speed. The leader is put on a random sphere around the player (radius 16,384 plus a random up to 8,192; two random angles through a sine table), pointed at the player and sent in at full speed. The number of wingmen is a random up to (rating + 3) / 2, so better pilots meet bigger squads; each is a copy of the leader moved along its own x or y axis by a table of offsets (`squadron_positions`: plus and minus along x, plus and minus along y). The types come from `random_pirate`; the missions force a Thargoid, a Constrictor, or two Asps.

## What this means for the 128K build

The spawn and the projection are not the cause of a top-right bias (the spawn is uniform, a hull at each quadrant draws in that quadrant). If a bias is real, look at later movement (ships turn towards the player), the other callers of `spawnShip` and the same situation on `elite64.dsk`; the plan is in `TODO_128K.md` (pirates). To make pirates come from all around (a random sign for z as well, or the ST model), the ST's random direction on a sphere (including behind the player) is the model, but it needs trigonometry that the CPC code does not have.

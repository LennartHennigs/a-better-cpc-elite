# How ships are spawned: pirates and asteroids on the CPC, BBC, C64 and Atari ST

Why this note exists: pirates seemed to appear in the top right of the view in the 128K build (disproved as a spawn bias and closed, see `TODO_128K.md` *Done*). It compares the CPC code (`src/elite/commonxx.asm`, the same in `src/elite128/`) with the 6502 versions (BBC and C64, the commented sources in `work/ext_bbc` and `work/ext_c64`) and the Atari ST original (`work/ext_st/repo/src_orig/asm/combat.m68`). The third-party sources are read-only references: nothing here is copied from them. Findings on the CPC marked "measured" come from calling `spawnShip` in cpcxray on the 128K build (2026-11-21).

## The short version

| | BBC / C64 | CPC (stock and 128K) | Atari ST |
|---|---|---|---|
| Where a hostile ship (pirate, Thargoid) starts | one of the four diagonal corners ahead: x, y and z each 8,192 (BBC) or 6,400 (C64) | ahead, z = 12,800; x and y of about 12,800: the same diagonal corner | a random point on a sphere of radius 16,384 to 24,576 around the player, so also behind |
| Where an asteroid starts | far ahead (z 9,728), almost on the centre line: x within about 770, y within about 260 | ahead, z = 12,800, within about 2,300 of the centre line in x and y | the same random sphere as the pirates |
| Left/right, up/down | from bit 7 of two consecutive random numbers (not fully independent) | from two bits of one random number | two random angles, 0 to 360 |
| A pirate group | 1 to 4 ships added from one workspace: they all start at the same spot | each ship through `spawnShip`: its own random position | a leader plus wingmen in formation (offsets along its own x and y axes) |
| Where it can happen | anywhere in flight (asteroids: not in a witchspace mis-jump) | anywhere in flight | deep space only; pirates while fewer than 2 are around, an asteroid only if none exists |
| How often: pirates | 35% per attempt, only if the random 0 to 7 is not below the government number (anarchy always) | one roll per 256 passes of the main loop, hostile below 80/256 (stock) or 90/256 (`-DTRAFFIC`, the C64 value) | a counter reloaded with (government + 2) x 512: lawless systems wait longer |
| How often: asteroids | every 256 passes, 13% (random below 35), at most 3 in the bubble | in the same roll, a band of 10 values (3.9%; 35 values = 13.7% with `-DTRAFFIC`) | a counter of 512 |

No version has a fixed top-right start. **In all three 8-bit versions a new ship always starts in front of the player** (the sign of z is never set): pirates and asteroids only come from the front, and in the rear and side views they show up after they have flown past or turned. Only the Atari ST spawns all around.

## BBC and C64 (6502)

Main loop. Every 256 passes (a counter `MCNT`) the loop considers new ships; an "extra vessels" counter delays the pirate checks.

**Asteroids and traders (part 2).** Not in a witchspace mis-jump, a 13% chance (random below 35), and only if fewer than 3 asteroids are around. The ship gets z_hi = 38 (9,728, far away), random low bytes for x and y, and signs from bit 7 of those low bytes; x is moved off-centre by 0 or 512 through a random carry, y_hi stays 0, so the rock appears almost on the centre line. Half of these spawns are a trader instead (an asteroid 98.5%, a cargo canister 1.5% of the rest). The ship also gets a random roll (and with luck a random pitch or speed), and an asteroid or cargo canister is not spawned inside the station's safe zone (the trader branch is taken before that check). The C64 source has the same structure (the CPC `-DTRAFFIC` comment cites its value 35).

**Cops (part 3)**, then **pirates (part 4):** a 35% chance (random below 90), then the government filter (a random 0 to 7 below the system's government number means no spawn; anarchy skips it, so lawless systems spawn more). The routine `Ze` clears the ship workspace and sets x, y and z to the same distance, with the signs of x and y taken from bit 7 of two random numbers; the comments in both sources point out that the location is therefore not totally random. A further roll chooses between a group and a lone ship: BBC 13% group (random 200 or more), otherwise a lone Mamba, Python or Cobra Mk III, or a Thargoid; C64 61% group (random 100 or more), otherwise a lone bounty hunter. A group is 1 to 4 ships (the pirate counter counts down to minus one), each added with the same workspace, so the whole group sits on one point. BBC types: Sidewinder or Mamba. C64 types: one of eight blueprints from the Sidewinder up (Mamba, Krait, Adder, Gecko, Cobra Mk I, Worm, Cobra Mk III pirate), small numbers more likely (two random numbers ANDed).

## CPC (stock, same in the 128K build)

`spawnShip` copies an initial block in which x, y and z are all `&3200` (12,800), then: the low bytes of x and y are random; for the types whose blueprint flag byte (`+33`) has bit 2 **clear** the high bytes of x and y become a random 0 to 7, so those ships start within about 23 px of the view centre; the types with bit 2 **set** keep `&32xx`, the corner. Measured over all 29 types (6 calls each): bit 2 is set for exactly the hostile ones (Python pirate, Cobra Mk III pirate, Asp Mk II, Thargoid, Sidewinder, Krait, Thargon), which start in the diagonal corner like the 6502 pirates; every other type (asteroid, cargo, traders, the Viper, and the ship-pack hulls Gecko to Shuttle, the 6502's pirate types) starts near the centre line. The signs of x and y are two bits of one random number. z is always ahead. Measured over 80 calls for three types: the four quadrants come out about equally (e.g. 24/13/20/23); the 128K build changes nothing here.

A corner start is a long way off the visible view: x/z and y/z are both about 1, so the ship is at the very edge horizontally and above or below the 64-line half height of the viewport, and appears only after it has flown in.

The pick itself (`spawnCommand0`): a roll below `SPAWN_HOSTILE_LIMIT` (`&50`, `&5A` with `-DTRAFFIC`) lets a hostile through, the next `SPAWN_JUNK_WIDTH` values (10, 35 with `-DTRAFFIC`) make an **asteroid**: a free slot (1 to 6), `spawnShip` type 6, then the AI and aggression bits cleared and the roll counter set to `&C0`; there is no count limit like the 6502's 3 and no random speed or pitch. The type of a hostile comes from further rolls, the marked Asp and the mission states have their own paths. `spawnEscortPack` makes 2 to 4 (1 to 4 with `-DTRAFFIC`) Sidewinders or Kraits, each through `spawnShip`.

## Atari ST

**Pirates.** `create_pirates` runs only in deep space (not near a planet or station) and only while fewer than 2 pirates exist. A counter reloaded with (the planet's government + 2) x 512 decides when; then `pirate_attack` (also called for the missions) prints "Condition RED!", stops the torus drive and restores the speed. The leader is put on a random sphere around the player (radius 16,384 plus a random up to 8,192; two random angles through a sine table), pointed at the player and sent in at full speed. The number of wingmen is a random up to (rating + 3) / 2, so better pilots meet bigger squads; each is a copy of the leader moved along its own x or y axis by a table of offsets (`squadron_positions`: plus and minus along x, plus and minus along y). The types come from `random_pirate`; the missions force a Thargoid, a Constrictor, or two Asps.

**Asteroids.** `create_asteroid`: deep space only, only if no asteroid exists, a counter of 512 passes; the asteroid is put on the same random sphere, pointed at the player, cruising at full speed, and with about a 10% chance (random below 26 of 256) it carries 1 to 4 platelets that it releases when shot.

## The 128K build: spawn variance (2026-11-21)

With `SPAWN_VARIANCE` (on in `src/elite128/config.inc`) the hostile types (blueprint byte `+33` bit 2: Sidewinder, Krait, the pirates, the Asp, the Thargoid) no longer start in one of four fixed corners: x_hi and y_hi are random 0 to 63, z_hi 32 to 63 (8,000 to 16,000 units), the z sign is random, and a ship that would land behind the player inside the rear cone (x_hi and y_hi both below z_hi) is put in front instead. That leaves the front 180 degrees plus the two side wedges behind the lateral axis, 270 degrees; the ship turns towards the player through its tactics. Asteroids, traders and the rest keep the stock start for now (they need a heading, see "Open: asteroids, traders and packs" below). The code is `spawnVariance` in the overlay on `bankInit`, called at the end of `spawnShip`.

### Open: asteroids, traders and packs (design notes, 2026-11-21)

Wanted: a random distance and direction for asteroids too, with the 128K rules switchable (`SPAWN_VARIANCE`; `src/elite` stays byte-exact, decide whether `main` gets the switch).

- **Position without trigonometry:** random high bytes (x_hi, y_hi 0 to `&3F`, z_hi `&20`-`&3F`) and random signs; the rear cone is spared with one comparison (z negative and both x_hi and y_hi below z_hi: flip the z sign). Asteroids may start anywhere around the player, so they skip the test.
- **Heading:** asteroids have no AI (`spawnCommand0` clears it) and keep the identity orientation, so they all fly along +z. For a random heading `setDirectionofEntity` (`&82B8`) builds the matrix from a direction vector (no normalising needed if the routine copes). Fully random headings would send most rocks away for good, so aim at the player plus a random offset of a few thousand units per axis (decided 2026-11-21): most pass through or near the player's area, some hit, as the ST's asteroids do.
- **Packs:** `spawnEscortPack` calls `spawnShip` per ship, so with variance the wingmen scatter over the sky: spawn the leader with the variance and put the others at its position plus a small random offset.
- **Where the code goes:** the glue has no byte left; the hostile rules live in the overlay on `bankInit` (6 bytes left of 248). An asteroid heading routine needs a far-call module (bank 6 has about 2.3 KB of code space) or a second overlay region.
- **Checks:** the spawn-sampling script (call `spawnShip` 80 times per type, histogram of signs and distance), a test that no spawn lands in the back cone, screenshots in the front, side and rear views; the missions (Constrictor, Thargoid, the marked Asp, Trumbles) and the safe zone behave as before; frame time with ships at the sides.

## What this means for the 128K build

The spawn and the projection are not the cause of a top-right bias (the spawn is uniform, a hull at each quadrant draws in that quadrant); the report was closed. If it comes back, look at later movement (ships turn towards the player), the other callers of `spawnShip` and the same situation on `elite64.dsk` (`TODO_128K.md` *Done*). To make ships come from all around (a random sign for z as well, or the ST model), the ST's random direction on a sphere (including behind the player) is the model, but it needs trigonometry that the CPC code does not have.

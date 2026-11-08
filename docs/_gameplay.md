# Gameplay events

## Witchspace mis-jump (read from the code 2026-11-08, not yet traced in cpcxray)

A mis-jump drops the player into witchspace between two systems: no planet, no sun, almost no stars, and
Thargoids. Entry point is `someHyperSpaceFunctions` (`commonxx.asm`), reached after the jump countdown.

**Sequence on the CPC**
1. Fuel for the jump is deducted, the fuel price and the legal status (halved) are updated.
2. If bit 6 of `dat_8E23` (pause-mode option flags) is set, the code takes `todoMisJump`.
3. `todoMisJump` sets `todoLaunchFlag` (nonzero = in witchspace), replaces the present system and the chart
   cursor coordinates with their midpoint (per axis: add, `rr a`), clears `FlagStationNear` and both planet
   name buffers, and continues at `setShipvarsAtArrival`.
4. `Spaceflight` skips `drawPlanetnSun` while the flag is set.
5. `Witchspace` (the tunnel entry) calls `spawnCommandParser` with A=1 when the flag is set, then runs the
   usual tunnel effect. How many Thargoids this spawns is not checked yet.
6. `dust2` sets the particle count `dustVar5` to 4 instead of 16, so the screen is almost starless.
7. A normal jump (`generateTargetSystemparAtHyperjump`) clears `todoLaunchFlag`.

**Open: the random mis-jump looks unreachable.** The other versions mis-jump at random, about 1 in 256 per
jump. The CPC code compares the low byte of the random seed (`todo_varEscapepod`, which is the seed, not an
escape pod) with `0x40` and then with `0x20` and branches away on not-equal both times. After the first match
A is `0x40`, so the second compare always fails: the path is never taken. The Spectrum has `CP $F9` there
(`work/ext_msx/skoolkit/src/elite.skool`, around line 22105). So on the CPC only the pause-menu toggle
(bit 6 of `dat_8E23`) triggers a mis-jump, unless a trace shows otherwise.

**Other versions**

| | C64 (`work/ext_c64`, `elite-source.asm`, routines `ee5`, `MJP`) | Spectrum | CPC |
|---|---|---|---|
| Random trigger | `DORND`, `CMP #253`, about 0.78% | seed byte `== $F9`, about 1 in 256 | seed compare that cannot match (see above) |
| Manual trigger | CTRL after enabling author names ("X") when paused | bit 6 of the control options ("F" toggle) | bit 6 of `dat_8E23` |
| Position | y-coordinate XOR `%00011111` | midpoint | midpoint |
| Spawned | 4 Thargoids, each with a Thargon (`GTHG` loop) | not checked | `spawnCommandParser`, count not checked |
| Stars | 3 (`NOSTM`; normal 18) | not checked | 4 (normal 16) |
| Planet and sun | none | none | none |

Escape pods are fatal in witchspace on the C64; whether the CPC does the same is not checked.

**Names to fix when `src/` is next edited:** `todoLaunchFlag` means "in witchspace"; `todo_varEscapepod`
is the random seed.

Flicker-free C64 patch (`work/ext_c64_flicker`): it interleaves erase and redraw of ship lines to cure 6502
flicker. Its author states it does not apply to the Z80 ports, which draw the frame off-screen and copy it
(`Spaceflight` -> `transferBuffertoScreen`), so nothing to port. Useful only as a model for finding space in
a packed binary (unused sprite data, NOP runs, slack after a shortened routine).

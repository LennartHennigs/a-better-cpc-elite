# Gameplay events

## Witchspace mis-jump (read from the code 2026-11-08; the branch logic is deterministic, so no trace is needed)

A mis-jump drops the player into witchspace between two systems: no planet, no sun, almost no stars, and Thargoids.
Entry point is `someHyperSpaceFunctions` (`commonxx.asm`), reached after the jump countdown.

1. Jump fuel is deducted; fuel price and legal status (halved) are updated.
2. If bit 6 of `keybFlags0` (pause-mode option flags) is set, the code takes `todoMisJump`.
3. `todoMisJump` sets `todoLaunchFlag` (nonzero = in witchspace), replaces the present system and the chart cursor with
   their midpoint (per axis: add, `rr a`), clears `FlagStationNear` and both planet name buffers, and continues at
   `setShipvarsAtArrival`.
4. `Spaceflight` skips `drawPlanetnSun` while the flag is set.
5. `Witchspace` (the tunnel entry) calls `spawnCommandParser` with A=1 when the flag is set, then runs the usual tunnel
   effect. Action 1 is `spawnCommand1`: 3 or 4 Thargoids (ship type `0x0F`; `3 + (random & 1)`), fewer if the slots run out; no Thargons (the C64 gives each Thargoid one).
6. `dust2` sets the particle count `dustVar5` to 4 instead of 16.
7. A normal jump (`generateTargetSystemparAtHyperjump`) clears `todoLaunchFlag`.

**The random mis-jump is unreachable (`someHyperSpaceFunctions`).** Other versions mis-jump at random, about 1 in 256 per jump. Here the code is `ld a,(todo_varEscapepod)` (the low byte of the random seed, not an escape pod), `cp 0x40`, `jr nz,normal`, `cp 0x20`, `jr nz,normal`:
only A = `0x40` passes the first test, and A is still `0x40` at the second, which therefore always branches away. The Spectrum has `CP $F9` there (`work/ext_msx/skoolkit/src/elite.skool`, around line 22105). So the only way into `todoMisJump` is bit 6 of `keybFlags0` (the pause-menu
toggle). On that path `todoLaunchFlag` is set to `keybFlags0 + 1`, which is nonzero unless `keybFlags0` is `&FF`.

| | C64 (`work/ext_c64`, `elite-source.asm`, `ee5`, `MJP`) | Spectrum | CPC |
|---|---|---|---|
| Random trigger | `DORND`, `CMP #253`, about 0.78% | seed byte `== $F9`, about 1 in 256 | seed compare that cannot match |
| Manual trigger | CTRL after enabling author names ("X") when paused | bit 6 of the control options ("F" toggle) | bit 6 of `keybFlags0` |
| Position | y-coordinate XOR `%00011111` | midpoint | midpoint |
| Spawned | 4 Thargoids, each with a Thargon (`GTHG` loop) | not checked | 3 or 4 Thargoids (`spawnCommand1`), no Thargons |
| Stars | 3 (`NOSTM`; normal 18) | not checked | 4 (normal 16) |
| Planet and sun | none | none | none |

Escape pods: fatal in witchspace on the C64. On the CPC the pod cannot be launched there at all: `meLaunchEscapePod` (`commonxx.asm`; Spectrum `launch_escape_pod`) returns without effect when `todoLaunchFlag` is nonzero, after the checks for the key and for a fitted pod. So the key does nothing in witchspace (static reading, not traced).

Name fixes for the next `src/` edit: `todoLaunchFlag` means "in witchspace"; `todo_varEscapepod` is the random seed.

**Flicker-free C64 patch** (`work/ext_c64_flicker`): interleaves erase and redraw of ship lines to cure 6502 flicker. Its
author says it does not apply to the Z80 ports, which draw off-screen and copy (`Spaceflight` -> `transferBuffertoScreen`),
so there is nothing to port. It is only a model for finding space in a packed binary (unused sprite data, NOP runs).

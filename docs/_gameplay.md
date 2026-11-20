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

## Kill score per ship (read from the code 2026-11-14; not yet confirmed in a run)

`todo_killedsomeone` adds half of the dead ship's blueprint word (bytes +21/+22) to `killScore`, a 3-byte value: byte 0 is 1/256 kill, byte 1 the low and byte 2 the high byte of the kill count. The rank tables (`getRank`) count whole kills: Harmless below 8, then 16, 32, 64, 128, 256 (Competent), 512, 2560, 6400 (Elite). Asteroids and every other ship type with a non-zero word count. The bounty (blueprint +8/+9) is separate.

Kills per ship (word / 512), with the C64 value (`KWL%`/`KWH%`, `work/ext_c64`) and the BBC (`EXNO2` in `work/ext_bbc`: `INC TALLY`, 1 kill for everything, asteroids too):

| CPC ship | CPC | C64 |
|---|---|---|
| Thargoid | 4 | 2.66 |
| Constrictor (our hull, `missions_hull.asm`) | 8 | 5.33, plus 256 kills |
| Cobra Mk III pirate / Python pirate | 1.75 | 1.16 |
| Asp Mk II | 1.63 | 1.08 |
| Fer-de-lance | 1.5 | 1.25 |
| Cobra Mk III trader / Python trader | 1 | 0.91 / 0.66 |
| Missile | 0.88 | 0.58 |
| Sidewinder (`SHIPDATPIRATE1`), Krait (`SHIPDATPIRATE2`), rock hermit | 0.5 | 0.33 each |
| Thargon | 0.2 | 0.13 |
| Viper | 0.16 | 0.10 |
| Escape pod | 0.1 | 0.06 |
| Alloy, cargo canister, splinter | 0.06 | 0.04 |
| Asteroid | 0.05 | 0.03 |
| Coriolis | 0 | 0 |

The CPC has the same 19 ship types as the Spectrum (`shipGFXdataTable`; `SHIPDATPIRATE1/2` match the Spectrum's Sidewinder and Krait blueprints byte for byte). The C64 and BBC also have Boulder, Shuttle, Transporter, Boa, Anaconda, Mamba, Adder, Gecko, Cobra Mk I, Worm, Moray, Cougar and the Dodecahedron station, which the CPC lacks. The CPC missions add no scoring: `mxKillHook` only wraps `getBounty`. The Constrictor and plans missions pay a rank step (`inc killScoreHigh`, +256 kills), like the C64's flat +256 for the Constrictor kill and mission 2.

## Legal status (read from the code 2026-11-16; not yet confirmed in a run)

`legalStatus` (`&38D6`, one byte in the save) is 0 clean, 1-49 offender, 50-255 fugitive (`cp &32` in the status page code).

Raised by:
- **Illegal goods**, in `chkForIllegalGoods` (a purchase, with B = the quantity bought, or a scooped canister, B = 1): the byte gets B added, saturating at 255. Slaves (good 3) and narcotics (6) count B x 4, firearms (10) B x 2.
- **A kill**, in `todo_killedsomeone`: if the dead ship's flag byte `ix+33` has bit 5 or 6 set (police or innocent), `legalStatus |= &40`, so the commander is a fugitive at once. Missed shots and hits that do not kill change nothing: no other code writes the byte, which differs from the BBC.

Lowered by:
- every hyperspace jump halves it (`srl`);
- a galactic jump sets it to 0;
- the escape pod sets it to 0 (the same routine that clears the cargo).

Effect in flight: `chkCopHuntergettingHostile` sets the hostile flag (`ix+33` bit 2) on a ship with bit 1 set (the cop AI) once the byte is 40 or more, so police turn on the commander before the status page says Fugitive.

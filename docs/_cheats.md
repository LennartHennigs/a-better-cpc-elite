## CHEAT.BAS (Firebird disk): poke targets in the English build

File: the original is on `Elite_UK_Firebird_cracked_trainer.dsk` (`python3 -I tools/dskx.py` extracts it). The extracted binary
was deleted; the plain-text listing is kept, tracked, at `src/cheats/CHEAT_ORIGINAL.BAS.txt`. Type 0 (tokenised BASIC), load `&0170`,
length `&0235` (565 bytes), no exec address. SHA-256 of the data file:
`f8d6ca248c4f9098bbacd852e64edd971a044aa2d8c51f6c12efb0c6517805b9`. `Elite_UK_original_protected.dsk` has no such file.
Run it with `RUN"CHEAT.BAS` instead of `RUN"ELITE.BAS`. Structure (line numbers from the listing):
10-100 loader (the Firebird `ELITE.BAS` loader minus the `picture` load and the ink changes; all four inks are black from line 30), 110-280 nine
`REM` + `POKE` groups, 290 `CALL &1C82`. `ON ERROR GOTO 100` (line 20) jumps straight to the `common2x` load, so a
failed `OPENOUT`/`LOAD` earlier still reaches the pokes. The original comment text spells "SHEILDS" wrongly.

Decoded with a proper CPC BASIC detokenizer (an earlier quick decode garbled the values). It uses the same
load sequence as `ELITE.BAS` (inks set to black, `MEMORY &83F`, load the three files), then pokes after
`common2x` is loaded and before `CALL &1C82`:

| Cheat (comment in file) | Pokes |
|---|---|
| Infinite shields and fuel | `&4F02`=0, `&35CB`=0 |
| Infinite missiles | `&382D`=0 |
| No hyperspace limit | `&4C08`=0, `&4C12`=0 |
| Missiles destroy space stations | `&8A8F`=0 |
| No laser temperature | `&7A4F`=0 |
| Constant galactic hyperjump | `&4BFA`=0 |
| One hit to destroy | `&7AA8`=0 |
| Cloaking device | `&4902`=`&21`, `&4096`=`&F6`, `&4908`=0 |
| Constant energy bomb | `&2F6A`=0 |

Most cheats write 0 (a Z80 `NOP`), so each is probably a one-byte instruction being removed, such as a
decrement or a check. That is a guess until we disassemble those addresses. The cloaking patch differs: it
writes `&21` (`ld hl,nn`) and `&F6` (`or n`), which looks like a code change, not a NOP.

Other facts from the decode: `ELITE.BAS` sets inks `0,0 / 1,24 / 2,15 / 3,6` for the loading picture, then
blanks all four inks before loading `common2x`. The `OPENOUT "d"` / `MEMORY &83F` / `CLOSEOUT` sequence looks
like a disc-buffer trick to protect memory from `&840` up while loading (unverified). `ON ERROR GOTO 90` skips
to the `common2x` load if the earlier steps fail.

## Cheat addresses, aligned to real instruction boundaries

Disassembling from the poke address often lands mid-instruction, because most pokes hit an operand byte.
After re-aligning:

| Poke | Real instruction | Effect of the cheat |
|---|---|---|
| `&4F02`=0 | operand of `jr c,&4F05` (after `cp &47`) | the clamp `ld a,&46` always runs, so `(&38F9)` is always set to 70: **`&38F9` is the fuel variable** |
| `&35CB`=0 | `cp (hl)` becomes `nop` in `xor a / cp (hl) / ret z` | the routine always returns early (shield damage skipped) |
| `&382D`=0 | `dec (hl)` becomes `nop` | missile count is not decremented |
| `&4C08`=0 | operand of `jr nz,&4C2A` after `ld a,h / and a` | removes the "distance too large" test (hyperspace distance is `(&3D5C)`) |
| `&4C12`=0 | operand of `jr c,&4C2A` after `ld a,(&38F9) / sub b` | removes the "not enough fuel" test |
| `&7A4F`=0 | `add a,b` becomes `nop` before `cp &A0` | laser temperature (stored at `(&1C0F)`, capped at `&A0`) stops rising |
| `&7AA8`=0 | operand of `jr nc,&7AF1` | damage check skipped, so the ship always takes the destroyed path (`set 4,(ix+&20)`) |
| `&8A8F`=0 | operand of `jr nz,&8AA3` after `cp &04` | removes a ship-type check, so missiles always take the destroy path |
| `&4BFA`=0 | opcode of `ld bc,&7406` becomes `nop` | C is no longer set to 6; B still set to `&74`; then `jr &4C1B` (meaning unclear) |
| `&2F6A`=0 | `ret z` becomes `nop` before `xor a / ld (hl),a` | energy bomb path always runs (unclear) |
| `&4902`=`&21`, `&4908`=0 | `ld a,(Missionflag)` becomes `ld hl,&3927`; the `jr z,+4` after `bit 6,a` becomes `jr z,+0` | equipment screen always prints "CLOAKING DEVICE" (token `&7D`), owned or not; see "Cloaking cheat" below |
| `&4096`=`&F6` | not code: the inline token byte `&08` after `call printStringFollowingByte` in `FindPlanet`'s not-found path | prints token `&F6` ("BIRD") instead of control code `&08`; looks like a stray address |

Known variable addresses so far: fuel `&38F9` (max 70), laser temperature `&1C0F`, frame counter `&1DA8`,
hyperspace distance `&3D5C`, `&3927` (a flag byte tested at bit 6 in the cloak code).

## Cloaking cheat (`CHEAT.BAS`) analysed

Corrects the earlier guess that it patches code: only `&4902` and `&4908` are code bytes, and `&4096` is data.

- `Missionflag` (`&3927`) bit 6 means "cloaking device owned". Only scooping cargo type `&FF` sets it
  (`chkCloakingDeviceScooped`, `&3961`). Readers: `&2029` (`bit 6,(hl) / ret z` at the start of the in-flight cloak code,
  so without the bit the cloak never works), `&4902` (equipment screen prints token `&7D`, "CLOAKING DEVICE"), and
  `&840B` (Asp spawn test `and &42 / cp &02`: bit 1 set, bit 6 clear).
- `&4902`=`&21` turns `ld a,(&3927)` (`3A 27 39`) into `ld hl,&3927`, so `bit 6,a` tests whatever `A` held. `&4908`=0
  makes the `jr z` fall through either way. Net effect: the equipment list always shows CLOAKING DEVICE. Nothing sets
  bit 6, so the cloak does not work in flight.
- `&4096`=`&F6` changes the inline byte of a string call. No code or pointer refers to `&4096` or `&4097` (searched all
  three binaries). An unknown planet name on the chart should print "BIRD" (token `&F6`) before " NOT FOUND".
- **Emulator test (cpcxray, Firebird disk, 2026-11-07):** all three cases boot via the entry snapshot with the pokes
  applied, answer `N` to "Load New Commander" and press Space for the status page.

  | Case | Status page lists "Cloaking Device" | `chkCloak` passes the ownership test (`&2030` reached) |
  |---|---|---|
  | Stock | no | no (0 hits in about 35 calls) |
  | Original cheat (`&4902`, `&4096`, `&4908`) | **yes** (cosmetic) | no (0 hits in about 70 calls) |
  | Fixed cheat (`&4902`, `&4908`, `&202B`=0) | yes | **yes** (34 hits) |

  So the original cheat only changes the equipment list, as predicted. The "BIRD" side effect of `&4096` was not run.
- **Fix:** `POKE &202B,0` turns the `ret z` after `bit 6,(hl)` in `chkCloak` into a `nop`, so the cloak code runs
  whether or not you own the device (same style as the other zero pokes). Keep `&4902`/`&4908` if you want the device
  listed, and drop `&4096`. Fixed line 260: `POKE &4902,&21:POKE &202B,0:POKE &4908,0`.
- The cloak key is `Y` (see "German keycard" in `_gameplay.md`); with the fixed cheat the cloak works in flight, confirmed by hand.
- The first fixed file was a copy of the original `CHEAT.BAS` with only line 260 changed. It is superseded by our interactive trainer, also named `CHEAT.BAS`, below.
- cpcxray notes from this test: the game polls the keyboard, so hold keys about 1.2 to 1.5 s of emulated time
  (`key_press`, `run`, `key_release`); `run` reports `time_limit` instead of stopping at a PC breakpoint, so count
  hits with `breakpoint_list`. Load `output/firebird_at_entry.sna` after `disk_insert disk/Elite_UK_Firebird_cracked_trainer.dsk`, or the
  game stops at "Drive A: disc missing".
- Launching with `f1` twice from the status page got `chkCloak` running; `FlightMode` (`&38F8`) stayed 0 in all runs,
  so do not read it as docked/flying.

## Our interactive trainer (`CHEAT.BAS`, built from `src/cheats/CHEAT.ASC`)

`RUN"CHEAT` on `work/firebird_cheat.dsk` (a copy of the Firebird disk plus this file; the disk is built, not
shipped). It asks, then loads the game and applies only what you chose. Source: `src/cheats/CHEAT.ASC`
(ASCII, edit this); `CHEAT.BAS` is the tokenised file with AMSDOS header and `CHEAT.BAS.txt` its listing.
Rebuild both and the disk with `bash tools/build_cheat.sh` (the CPC's own BASIC tokenises, via cpcxray headless).

Prompts (Y or ENTER = yes, N = no):

| Prompt | What it does |
|---|---|
| Inf shield+fuel, Inf missiles, Free hyperjump, Missile v station, No laser heat, Free gal jump, One-hit kills, Inf energy bomb | the original pokes of `CHEAT.BAS`, one prompt each (addresses above) |
| No pirate board | `POKE &207D,&C9`: `punishCheater`'s `ret nz` becomes `ret`, so the "SHIP BOARDED BY PIRATES" game over never fires |
| Unlimited hold | `POKE &0998,0` (yes) or `&19` (no): the hold-capacity test; the Firebird disk's `LARGEAXX` already has the trainer value `0` |
| Own cloak | sets bit 6 of the default commander's `Missionflag` (`&3A23`), so the device is listed and `Y` cloaks; replaces the old `&4902`/`&4908`/`&202B` pokes |
| Cash Cr (default 100) | default commander block at `&39C7`: cash high word `&39D9`, low word `&39DB` (pair of words: high word counts 1,000 Cr, low word the remaining decicredits below 10,000, see `docs/_savegame.md`; up to 65,000,000 Cr) |
| Mission 0-3 | 0 normal; 1 supernova on the first jump, 2 cloak Asp on the first jump, 3 Thargon invasion on the first jump. Sets the jump counter (`&39D6`) to 31/127/253, the earlier stage bits in `Missionflag` (1 for stage 2, 3 for stage 3), and removes the galaxy-0 gate (`POKE &4E5D,0`) so arrivals count in the first galaxy |

Why the default block: the game copies `&39C7` (104 bytes, same layout as a save, see `docs/_savegame.md`) to the live
commander on "N" at "Load New Commander", so pokes there act as starting values and survive the game's own init.
The stage thresholds are `cp` on the counter's low byte (`>= 32`, `>= 128`, `>= 254`, at `&4EC8`, `&4EDC`, `&4EE6`), so the
counter only has to reach them. Stage 2 needs the cloak not owned for the Asp to appear (`Missionflag & &42 == 2`).

Checked in cpcxray (2026-11-07): with a STOP in place of the `CALL`, all pokes land at the expected addresses and an N skips
exactly its own pokes; the full file boots to the status page with the chosen cash and the Cloaking Device listed; running
the arrival routine `&4E58` with stage 1 turns counter 31 into 32, sets `Missionflag` bit 0 and `FlightMode` 1 in galaxy 0.
Cash 65,000,000 Cr shows correctly on the status page. Not checked: stages 2 and 3 end to end, the pirate-boarding poke in play.

BASIC pitfalls met while writing it (Locomotive BASIC 1.1):
- The program, its variables and strings must fit in `&170-&83E` (about 1.7 KB) because `MEMORY &83F` protects the game
  area; the file is 1.3 KB. Questions come first, loads later; keep all prompts short.
- `MEMORY &A000` (kept from the original loaders) always fails with "Memory full"; the `ON ERROR GOTO` handler is what
  continues to the `common2x` load. Do not put `ON ERROR GOTO 0` in the handler: it re-raises the pending error and stops.
- Strings are not safe after `MEMORY &A000`; the poke phase uses only numbers (the choices live in `DIM f(9)`).
- `f AND b` with a bit mask `b` of 256 and up silently failed inside `IF` here; per-cheat array flags fixed it.
  `x MOD 256` overflows above 32767 (use `x-256*INT(x/256)`), and `IF ... THEN a:NEXT` skips the `NEXT` when false.
- Reading results back in cpcxray: below `&4000` use `memory_view` with `view="ram:0"` (the CPU view shows the lower ROM);
  above, use `view="cpu"`. `ram:N` is a 16 KB RAM block with offset `address & &3FFF`, so `ram:0` is wrong for `&4902`.
  `run_until` an address below `&4000` can stop early inside the OS ROM (BASIC passes `&1C82` there); use a STOP in the
  BASIC program instead and read memory at the prompt.

## Interactive trainer additions for testing the added missions (2026-11-08)

`src/cheats/CHEAT.ASC` (`RUN"CHEAT`, build with `bash tools/build_cheat.sh`) has three more prompts after Cash and Mission: **Kills** (0-32767, pokes the BBC-style kill count at `&38D8/&38D9`; 256 is the gate of
the Constrictor and plans missions), **Jumps** (0-255, pokes the low byte of `jumpCounter`; also patches `&4E5D` so jumps are counted in galaxy 1) and **Added mission 1-4** (presets for the chain of
`docs/_missions_built.md` section 1: 1 plans next, 2 stolen police ship next, 3 asteroids next, 4 Trumbles open). All addresses are the save-block addresses plus `&FC` (the block sits there while the loader pokes:
`&39D4` kills, `&39D6` jumps, `&39F9/&39FA` the two mission bytes). The program must stay under about 1.7 KB (BASIC memory below `&840`): it is 1,536 bytes, so
new prompts need shortening elsewhere. `build_cheat.sh` also writes `work/missions_cheat.dsk`: the combined mission build plus `CHEAT.BAS` and `SHOWSAVE.BAS`.
Galaxy cannot be poked (the system seeds define the galaxy): use the "Free gal jump" cheat and the galactic hyperdrive.

## Save editor and save viewer

- `tools/saveedit.py show|edit|roundtrip SAVE` edits a 104-byte commander save on the host: kills, jumps, cash, legal status, fuel, name, stock mission stage, cloak, the added-mission chain
  (`--added 0-4`), raw mission bytes, Trumbles. It reads the key from a game disk, recomputes both checksums, never writes without `-o` and replaces a file in a copy of a disk image (or adds
  it). `--to-key-disk` converts a save between the UK, French and German builds. Round trip is byte-identical on `PETER`, `PETE`, `LEN` (German) and `1.BIN` (UK).
- `src/cheats/SHOWSAVE.BAS` (generated by `tools/mk_showsave.py`, 1.5 KB) runs on the CPC: `RUN"SHOWSAVE.BAS`, type the save file name; it prints origin (UK, FRENCH, GERMAN: the key whose checksums verify),
  name, kills, jumps, cash and galaxy. Tested in cpcxray on one save per build.
- Not tested: loading an edited save through the game's own disk menu (typing the name with `key_press` repeats keys in cpcxray); the checksums verify with the same code as the game.


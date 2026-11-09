# Cheats, trainer and save tools

## The original CHEAT.BAS (Firebird disk): poke targets in the English build

The original is on `Elite_UK_Firebird_cracked_trainer.dsk` (`python3 -I tools/dskx.py` extracts it); the tracked listing is
`src/cheats/CHEAT_ORIGINAL.BAS.txt`. Type 0 (tokenised BASIC), load `&0170`, length `&0235` (565 bytes), no exec address, SHA-256
`f8d6ca248c4f9098bbacd852e64edd971a044aa2d8c51f6c12efb0c6517805b9`. `Elite_UK_original_protected.dsk` has no such file. Run it with
`RUN"CHEAT.BAS` instead of `RUN"ELITE.BAS`.

Structure: lines 10-100 are the Firebird loader (minus the `picture` load; all four inks black from line 30), 110-280 nine `REM` + `POKE`
groups, 290 `CALL &1C82`. The pokes land after `common2x` is loaded. `ON ERROR GOTO 100` (line 20) jumps to the `common2x` load, so a
failed `OPENOUT`/`LOAD` earlier still reaches the pokes. (`OPENOUT "d"` / `MEMORY &83F` / `CLOSEOUT` looks like a disc-buffer trick
protecting memory from `&840`; unverified.) The comment text spells "SHEILDS".

Most cheats write 0, i.e. a Z80 `NOP`, or zero an operand. Disassembling from a poke address often lands mid-instruction, so the table
gives the re-aligned instruction:

| Cheat | Poke | Real instruction | Effect |
|---|---|---|---|
| Infinite shields and fuel | `&4F02`=0 | operand of `jr c,&4F05` after `cp &47` | the clamp `ld a,&46` always runs, so `(&38F9)` is always 70: **`&38F9` is fuel** |
| | `&35CB`=0 | `cp (hl)` becomes `nop` in `xor a / cp (hl) / ret z` | routine always returns early (shield damage skipped) |
| Infinite missiles | `&382D`=0 | `dec (hl)` becomes `nop` | missile count not decremented |
| No hyperspace limit | `&4C08`=0 | operand of `jr nz,&4C2A` after `ld a,h / and a` | removes the "distance too large" test (distance is `(&3D5C)`) |
| | `&4C12`=0 | operand of `jr c,&4C2A` after `ld a,(&38F9) / sub b` | removes the "not enough fuel" test |
| Missiles destroy stations | `&8A8F`=0 | operand of `jr nz,&8AA3` after `cp &04` | removes a ship-type check; missiles always take the destroy path |
| No laser temperature | `&7A4F`=0 | `add a,b` becomes `nop` before `cp &A0` | temperature (`(&1C0F)`, capped `&A0`) stops rising |
| Constant galactic hyperjump | `&4BFA`=0 | opcode of `ld bc,&7406` becomes `nop` | C no longer set to 6, B still `&74`, then `jr &4C1B` (meaning unclear) |
| One hit to destroy | `&7AA8`=0 | operand of `jr nc,&7AF1` | damage check skipped; ship always takes the destroyed path (`set 4,(ix+&20)`) |
| Cloaking device | `&4902`=`&21`, `&4908`=0 | `ld a,(Missionflag)` becomes `ld hl,&3927`; `jr z,+4` after `bit 6,a` becomes `jr z,+0` | equipment screen always lists "CLOAKING DEVICE" (token `&7D`); cosmetic, see below |
| | `&4096`=`&F6` | not code: the inline token byte `&08` after `call printStringFollowingByte` in `FindPlanet`'s not-found path | would print token `&F6` ("BIRD") instead of control code `&08`; looks like a stray address (nothing refers to `&4096`/`&4097`) |
| Constant energy bomb | `&2F6A`=0 | `ret z` becomes `nop` before `xor a / ld (hl),a` | energy-bomb path always runs (unclear) |

Other known variables: laser temperature `&1C0F`, frame counter `&1DA8`, hyperspace distance `&3D5C`.

### The cloak cheat does not make the cloak work

- `Missionflag` (`&3927`) bit 6 = "cloaking device owned"; only scooping cargo type `&FF` sets it (`chkCloakingDeviceScooped`, `&3961`).
  Readers: `&2029` (`bit 6,(hl) / ret z` at the start of the in-flight cloak code, so the cloak never works without the bit), `&4902`
  (equipment screen) and `&840B` (Asp spawn test `and &42 / cp &02`: bit 1 set, bit 6 clear).
- The original cheat only changes the equipment list. cpcxray test (2026-11-07, three cases, status page after answering `N` to "Load New Commander"):

  | Case | Status page lists the device | `chkCloak` ownership test passes (`&2030` reached) |
  |---|---|---|
  | Stock | no | no |
  | Original cheat | yes (cosmetic) | no (0 hits in about 70 calls) |
  | Fixed cheat | yes | yes (34 hits) |

- **Fix:** `POKE &202B,0` turns the `ret z` after `bit 6,(hl)` in `chkCloak` into a `nop`. Fixed line 260:
  `POKE &4902,&21:POKE &202B,0:POKE &4908,0` (drop `&4096`). With it the cloak, key `Y`, works in flight (confirmed by hand). Our trainer
  supersedes this (it sets the ownership bit instead).
- Notes: `FlightMode` (`&38F8`) stayed 0 in all runs, so do not read it as docked/flying. cpcxray tips are in `CLAUDE.md`.

## Our interactive trainer (`CHEAT.BAS`, from `src/cheats/CHEAT.ASC`)

`RUN"CHEAT` on `work/firebird_cheat.dsk` (the Firebird disk plus this file; built, not shipped). It asks, loads the game and applies only
what you chose. Edit `src/cheats/CHEAT.ASC` (ASCII); `CHEAT.BAS` is the tokenised file with AMSDOS header, `CHEAT.BAS.txt` its listing.
`bash tools/build_cheat.sh` rebuilds them and the disks (the CPC's own BASIC tokenises, via headless cpcxray), and also writes
`work/missions_cheat.dsk` (the mission build plus `CHEAT.BAS` and `SHOWSAVE.BAS`).

Prompts (Y or ENTER = yes, N = no):

| Prompt | What it does |
|---|---|
| Inf shield+fuel, Inf missiles, Free hyperjump, Missile v station, No laser heat, Free gal jump, One-hit kills, Inf energy bomb | the original pokes above, one prompt each |
| No pirate board | `POKE &207D,&C9`: `punishCheater`'s `ret nz` becomes `ret`, so "SHIP BOARDED BY PIRATES" never fires |
| Unlimited hold | `POKE &0998,0` (yes) or `&19` (no): the hold-capacity test (the Firebird `LARGEAXX` already has `0`) |
| Own cloak | sets bit 6 of the default commander's `Missionflag` (`&3A23`): device listed, `Y` cloaks |
| Cash Cr (default 100) | default commander block `&39C7`: high word `&39D9`, low word `&39DB` (see `_savegame.md`; up to 65,000,000 Cr) |
| Mission 0-3 | 0 normal; 1 supernova, 2 cloak Asp, 3 Thargon invasion, each on the first jump. Sets the jump counter (`&39D6`) to 31/127/253, the earlier stage bits in `Missionflag` (1 for stage 2, 3 for stage 3) and removes the galaxy-0 gate (`POKE &4E5D,0`) |
| Kills | 0-32767, pokes the kill count at `&38D8/&38D9` (256 gates the Constrictor and plans missions) |
| Jumps | 0-65535, both bytes of `jumpCounter`; also patches `&4E5D` so jumps count in galaxy 1 |
| Added mission 1-4 | presets for the chain in `_missions_built.md`: 1 Trumbles offered next, then plans; 2 stolen police ship next; 3 asteroids next; 4 all paid, asteroids state 3 |

Why the default block: the game copies `&39C7` (104 bytes, save layout) to the live commander on `N` at "Load New Commander", so pokes
there act as starting values and survive the game's init. Addresses are the save-block addresses plus `&FC` (`&39D4` kills, `&39D6`
jumps, `&39F9/&39FA` mission bytes). Stage thresholds are `cp` on the counter's low byte (`>= 32`, `>= 128`, `>= 254` at `&4EC8`,
`&4EDC`, `&4EE6`); stage 2 needs the cloak not owned for the Asp to appear (`Missionflag & &42 == 2`). Galaxy cannot be poked
(the seeds define it): use "Free gal jump" and the galactic hyperdrive.

Checked in cpcxray (2026-11-07): pokes land at the expected addresses, `N` skips exactly its own pokes, the file boots to the status
page with the chosen cash and the device listed; the arrival routine `&4E58` at stage 1 turns counter 31 into 32, sets `Missionflag`
bit 0 and `FlightMode` 1 in galaxy 0; 65,000,000 Cr shows correctly. Not checked: stages 2 and 3 end to end, the pirate-boarding poke.

BASIC pitfalls (Locomotive BASIC 1.1):
- Program, variables and strings must fit in `&170-&83E` (about 1.7 KB) because `MEMORY &83F` protects the game area; the file is
  1,536 bytes, so new prompts need shortening elsewhere. Questions come first, loads later.
- `MEMORY &A000` (kept from the original loaders) always fails with "Memory full"; the `ON ERROR GOTO` handler continues to the
  `common2x` load. Do not put `ON ERROR GOTO 0` in the handler: it re-raises the pending error.
- Strings are not safe after `MEMORY &A000`; the poke phase uses only numbers (choices in `DIM f(9)`).
- `f AND b` with a mask of 256 or more silently failed inside `IF`; per-cheat array flags fixed it. `x MOD 256` overflows above 32767
  (use `x-256*INT(x/256)`); `IF ... THEN a:NEXT` skips the `NEXT` when false.
- Reading results in cpcxray: below `&4000` use `memory_view` with `view="ram:0"`, above use `view="cpu"` (`ram:N` is a 16 KB block with offset
  `address & &3FFF`). `run_until` an address below `&4000` can stop early inside the OS ROM; use a STOP in the BASIC program instead.

## Save editor and viewer

- `tools/saveedit.py show|edit|roundtrip SAVE` edits a 104-byte save on the host: kills, jumps, cash, legal status, fuel, name, stock mission
  stage, cloak, the added-mission chain (`--added 0-4`), raw mission bytes, Trumbles. It reads the key from a game disk, recomputes both
  checksums, never writes without `-o`, and replaces a file in a copy of a disk image (or adds it). `--to-key-disk` converts a save between
  UK, French and German. The round trip is byte-identical on `PETER`, `PETE`, `LEN` (German) and `1.BIN` (UK).
- `src/cheats/SHOWSAVE.BAS` (from `tools/mk_showsave.py`, 1.5 KB): `RUN"SHOWSAVE.BAS`, type the save name; prints origin (UK, FRENCH,
  GERMAN: the key whose checksums verify), name, kills, jumps, cash, galaxy. Tested on one save per build.
- `src/cheats/EDITSAVE.BAS` (from `tools/mk_editsave.py`, about 2.8 KB): `RUN"EDITSAVE.BAS`, type the save name. It detects the build,
  shows name, kills, jumps, cash, legal status and both mission bytes, asks for new values (Enter keeps one; cloak y/n, added-mission preset
  0-4), recomputes checksums, encrypts and `SAVE`s. **Use a copy of the disk**: AMSDOS keeps the old file as `NAME.BAK`, and the new header
  has load address `&6000` and exec 0; the game does not care, since `loadFile` reads with `CAS_IN_DIRECT` to a caller address and uses only the
  length. Tested on a UK and a French save; the game's disk menu loads a file it wrote (kills 500, cash 3,000 Cr, mission byte `2E`, name EDSAVE).
- Loading through the game's menu is tested (2026-11-08): the English game on the mission disk answered "FOUND COMMANDER Tester." for a save
  from `saveedit.py` and loaded kills, cash, mission byte and name. cpcxray key timing: title-screen `y` held 1.4 s, `1` held 1.4 s (it also
  types a `1` into the name prompt: delete it with two `del` taps), then each letter and `return` tapped 0.33 s (longer types it twice, 0.25 s misses).

Screenshots (cpcxray, Mode 1): `docs/img/trainer_prompts.png`, `showsave_uk.png`, `showsave_fr.png`, `showsave_de.png`, `editsave_fr.png`.

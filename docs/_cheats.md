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

`RUN"CHEAT` on `work/firebird_cheat.dsk` (the Firebird disk plus this file; built, not shipped), `work/de_cheat.dsk` (German) or
`work/fr_cheat.dsk` (French): the same file runs on the UK, German and French builds (and on the mission build). It asks, loads the game
and applies only what you chose.

Two stages (the BASIC program and its variables must fit under `&83F`, one program with the three address tables did not): `CHEAT.BAS`
asks and converts the answers to numbers, then `CHAIN"cheatb.bin"`. `CHEATB.BAS` (disk file `CHEATB.BIN`, so it stays hidden; built from
`src/cheats/CHEATB.ASC`) loads the game, finds the build and pokes. CHAIN keeps the variables but puts HIMEM back to `&A000`, so stage two
repeats `OPENOUT"d":MEMORY &83F:CLOSEOUT` before the `LOAD`s (without it: "Memory full in 2"). Build detection: the byte pattern around the
shield-clamp operand (`cp &47 / jr c,+2` at `setFuel`+1) and the missile-v-station operand (`cp 4 / jr nz,&13`), looked up at each build's
address; nothing matches = no pokes, the game just starts. The per-build addresses (13 per build, `DATA` lines 800-820 of `CHEATB.ASC`) are
the nine patch groups, the galaxy-gate byte (`&4E5D` in UK) and the start of the default commander block (`&39C7` in UK), found as
label + offset in the three source trees (`sjasmplus --sym`) and checked byte by byte:

| | UK | German | French |
|---|---|---|---|
| default commander block (kills at +13, jumps +15, cash +18, mission bytes +50, flags +92) | `&39C7` | `&3ACE` | `&3A98` |
| galaxy-gate byte | `&4E5D` | `&4F71` | `&4FAF` |
| `setFuel` operand | `&4F02` | `&5016` | `&5054` |

`work/de_savegames.dsk` (built by the same script) is `work/de_cheat.dsk` (German game, `CHEAT.BAS`, `EDITSAVE.BAS`) plus `LISTSAVE.BAS` and the four saves of `Elite_DE_savegames.dsk`; all find the build from the save's key, so they work on any of the three builds' saves. The saves stay visible on this disk: `LISTSAVE` lists them by running `CAT` into a hidden screen buffer and reading it back, and `CAT` does not show System files. It only loads files `CAT` shows as 1K (a save is 232 bytes with its header), so large `.BIN` files are skipped; the key and checksum test still decides what is a save.

Tested in cpcxray on all three disks with every cheat on, cash 5000, mission 2, kills 300, jumps 40: all pokes landed, the title screen came
up. The added-mission pokes (`+50`, `+51`) only mean something in the English `-DMISSIONS` build.
 Edit `src/cheats/CHEAT.ASC` (ASCII); `CHEAT.BAS` is the tokenised file with AMSDOS header, `CHEAT.BAS.txt` its listing.
`bash tools/build_cheat.sh` rebuilds them and the disks (the CPC's own BASIC tokenises, via headless cpcxray), and also writes
`work/missions_cheat.dsk` (the mission build plus `CHEAT.BAS` and `EDITSAVE.BAS`).

Prompts (Y or ENTER = yes, N = no):

| Prompt | What it does |
|---|---|
| Inf shield+fuel, Inf missiles, Free hyperjump, Missile v station, No laser heat, Free gal jump, One-hit kills, Inf energy bomb | the original pokes above, one prompt each |
| No pirate board | `POKE &207D,&C9`: `punishCheater`'s `ret nz` becomes `ret`, so "SHIP BOARDED BY PIRATES" never fires |
| Unlimited hold | `POKE &0998,0` (yes) or `&19` (no): the hold-capacity test (the Firebird `LARGEAXX` already has `0`) |
| Own cloak | sets bit 6 of the default commander's `Missionflag` (`&3A23`): device listed, `Y` cloaks |
| Cash Cr (default 100) | default commander block `&39C7`: high word `&39D9`, low word `&39DB` (see `_savegame.md`; up to 65,000,000 Cr) |
| Mission 0-3 | 0 normal; 1, 2 or 3 starts that stock mission (S1 to S3 in `_missions_built.md`) on the first jump. Sets the jump counter (`&39D6`) to 31/127/253, the earlier stage bits in `Missionflag` (1 for stage 2, 3 for stage 3) and removes the galaxy-0 gate (`POKE &4E5D,0`) |
| Kills | 0-32767, pokes the kill count at `&38D8/&38D9` (256 gates added mission 1, 1280 added mission 2) |
| Jumps | 0-65535, both bytes of `jumpCounter`; also patches `&4E5D` so jumps count in galaxy 1 |
| Added mission 1-4 | presets for the chain in `_missions_built.md`: 1 T offered next, then mission 2; 2 mission 3 next; 3 mission 4 next; 4 all paid, mission 4 in state 3 |

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
  1,536 bytes, so new prompts need shortening elsewhere. That is why the trainer is split in two stages (see above). Questions come first, loads later.
- `MEMORY &A000` (kept from the original loaders) always fails with "Memory full"; the `ON ERROR GOTO` handler continues to the
  `common2x` load. Do not put `ON ERROR GOTO 0` in the handler: it re-raises the pending error.
- Strings are not safe after `MEMORY &A000`; the poke phase uses only numbers (choices in `DIM f(9)`).
- `f AND b` with a mask of 256 or more silently failed inside `IF`; per-cheat array flags fixed it. `x MOD 256` overflows above 32767
  (use `x-256*INT(x/256)`); `IF ... THEN a:NEXT` skips the `NEXT` when false.
- Reading results in cpcxray: below `&4000` use `memory_view` with `view="ram:0"`, above use `view="cpu"` (`ram:N` is a 16 KB block with offset
  `address & &3FFF`). `run_until` an address below `&4000` can stop early inside the OS ROM; use a STOP in the BASIC program instead.

## Save editor and viewer

- `tools/saveedit.py show|edit|roundtrip SAVE` edits a 104-byte save on the host: kills, jumps, cash, legal status, fuel, name, stock mission
  stage, cloak, the added-mission chain (`--added 0-4`), raw mission bytes, T. It reads the key from a game disk, recomputes both
  checksums, never writes without `-o`, and replaces a file in a copy of a disk image (or adds it). `--to-key-disk` converts a save between
  UK, French and German. The round trip is byte-identical on `PETER`, `PETE`, `LEN` (German) and `1.BIN` (UK).
- `src/cheats/LISTSAVE.BAS` (from `tools/mk_listsave.py`, 2.1 KB): `RUN"LISTSAVE.BAS` lists every save on the disk in drive A (File, Build = UK, FRENCH or GERMAN: the key whose checksums
  verify, Kills, Cash Cr). One page, no `CLS`, no colour changes, no catalogue on screen. BASIC cannot read the directory any other way than `CAT`, so the program prints it into
  a hidden screen buffer: `MEMORY &3FFF` frees `&4000-&7FFF`, a 6-byte stub (`ld a,&40 / call &BC08` = SCR SET BASE `/ ret`, `&9000`; the same with `&C0` at `&9006`) points the
  firmware's text output there, two `OUT`s keep the CRTC displaying `&C000`, `CAT` runs, `COPYCHR$` reads the rows back and the second stub switches back. Only files `CAT`
  shows as 1K are loaded (to `&9100`, keys at `&9200`). `SHOWSAVE.BAS` (one save by name) was removed: the saves are not the files one sees in `CAT`.
- `src/cheats/EDITSAVE.BAS` (from `tools/mk_editsave.py`, about 2.8 KB): `RUN"EDITSAVE.BAS`, type the save name. It detects the build,
  shows name, kills, jumps, cash, legal status and both mission bytes, asks for new values (Enter keeps one; cloak y/n, added-mission preset
  0-4), recomputes checksums, encrypts and `SAVE`s. **Use a copy of the disk**: AMSDOS keeps the old file as `NAME.BAK`, and the new header
  has load address `&6000` and exec 0; the game does not care, since `loadFile` reads with `CAS_IN_DIRECT` to a caller address and uses only the
  length. Tested on a UK and a French save; the game's disk menu loads a file it wrote (kills 500, cash 3,000 Cr, mission byte `2E`, name EDSAVE).
- Loading through the game's menu is tested (2026-11-08): the English game on the mission disk answered "FOUND COMMANDER Tester." for a save
  from `saveedit.py` and loaded kills, cash, mission byte and name. cpcxray key timing: title-screen `y` held 1.4 s, `1` held 1.4 s (it also
  types a `1` into the name prompt: delete it with two `del` taps), then each letter and `return` tapped 0.33 s (longer types it twice, 0.25 s misses).

Screenshots (cpcxray, Mode 1): `docs/img/trainer_prompts.png`, `showsave_uk.png`, `showsave_fr.png`, `showsave_de.png` (from the removed `SHOWSAVE`), `editsave_fr.png`.

## Ship viewer (`SHOWSHIP.BAS`, `work/showship.dsk`)

`bash tools/build_showship.sh` builds a blank data disk with `SHOWSHIP.BAS` (visible) and `SHIPS.BIN` (System-hidden); `RUN"SHOWSHIP` shows every model with its name (21 ships and 9 other objects: station, missile, escape pod, cargo canister, alloy plate, splinter, asteroid, rock hermit, Boulder), a rotating wireframe with the game's hidden-line test, and the numbers that matter (kills, bounty in Cr, speed, energy, vertices, edges, faces). Left and right arrows (or `,` and `.`) step through the 30 models (19 stock, 10 extras from `src/elite/missions_ships.asm`, the Constrictor), `Q` quits. The colours follow the game: black background, sky blue frame and lines (firmware ink 11, the game's `(0,128,255)`), pastel yellow text (ink 25).

How it works: `tools/mk_showship.py` cuts every blueprint out of `work/bin_stock/COMMONXX.BIN` and the extra hull sources, scales the vertices to +-125 and the face normals to +-64, and packs them with the Z80 routine of `src/cheats/showship.asm` into `SHIPS.BIN` (loaded to `&4000`, ships from `&5000`; everything stays under `&A67B`, where AMSDOS keeps its work area, or the load fails with "read fail"). BASIC only handles keys and text and POKEs the sine and cosine of the spin angle (6 degrees a frame); `CALL &4000` rotates (spin about the ship's y axis, then a fixed 20 degree tilt, orthographic) and redraws every edge whose face points at the viewer, erasing the edge's segment of the previous frame first. The lines come from the routine's own DDA (8-bit slope fraction, XOR into the mode 1 screen at `&C000`, pen 2): the firmware's `GRA LINE` gave about 3 frames a second, this gives about 8 (Coriolis, counted with a breakpoint on `&4000`). The alternate registers are not used (the firmware's interrupt routine owns them). `CALL &4003` copies a ship's packed record into the tables. Shared line ends toggle twice in XOR, so a vertex pixel can flicker.

The mission disk (`python3 -I tools/build_dsk.py --missions`, `work/elite_missions.dsk`) carries it too: `SHOWSHIP.BAS` visible in `CAT`, `SHIPS.BIN` hidden, added with `dskx` (`add_showship` in `tools/build_dsk.py`; run `tools/build_showship.sh` first, otherwise the build skips it). `RUN"SHOWSHIP` there works as on the blank disk (checked in cpcxray); `src/disk/README.TXT` mentions it. The same build now **replaces Firebird's own `CHEAT.BAS` on that disk with ours** (`replace_trainer`: the original is deleted, `src/cheats/CHEAT.BAS` and the hidden `CHEATB.BIN` are added; checked: `RUN"CHEAT` asks "ELITE CHEATS"). The old file only held nine poke groups with a wrong cloak entry; its addresses are still right in our build (all in `COMMONXX`, bytes unchanged there).

The standalone disk is a blank one because the Firebird disk has two tracks with odd sector ids that iDSK may fill; AMSDOS cannot read them (`Drive A: read fail`).

# Changelog

- **Asteroid bombardment mission (Elite Plus mission 6, branch `mission-asteroids`).** Delivering the plans (the P module) also offers it in the same box: destroy 20 asteroids at Ceerdi (galaxy 3, 215/84), 6,000 Cr. State: `missionState` bits 4-6 (free once the Constrictor is paid: 0 none, 1 clearing, 2 cleared, 3 paid) and the counter `&38FE`. New flight image `MFLIGHTA.BIN` (251 bytes): at Ceerdi while clearing the spawn check adds the stock asteroid (50% of checks), the kill hook counts asteroid kills down, at 0 the stage becomes 2; the P module pays at the next docking, then the Trumbles are offered (asteroids come first). The game already has the asteroid hull, so no hull was needed. Costs: stub 242 -> 254 bytes, Constrictor overlay still the largest (stub + overlay = 1A36, 10 spare); every flight image +9 bytes (launch picks "A"), Constrictor image 602 of 610. To fit, the Trumbles offer now starts at 5,000 Cr (the price) instead of 5,017.6 Cr. Tests: `tools/test_asteroids.py` (new: spawn places, kill counts, live loop with the spawn timer forced), test_launch (+4), test_mission_hook (+3, p_birera now ends in 0x1E). Not played through; the number 20 and the 50% spawn rate are guesses.

- **Trumble squeak.** With 256 or more Trumbles aboard, `mxSpawnCheckImpl` sets bit 5 of `sfxFlags2Bitmap` (the game's own short decaying tone, the engine plays it) with chance high byte / 64 per check, as the C64 scales its noise with the count. Trumbles flight image 562 -> 579 of 610 bytes (31 free). Test added to `tools/test_trumbles.py` (flag set / silent). Not listened to yet; which effect sounds best is a taste choice (other candidates: flags2 bit 7 the missile-lock blip, flags1 bit 7 the key click).

Changes to the project, newest first. The project root is a git repository from 2026-11-07; before that, this
file is the only history. Dates are ISO.

## 2026-11-08

- `docs/_gameplay.md` (was empty): the witchspace mis-jump on the CPC compared with the C64 and Spectrum. Found by reading, not traced: the random mis-jump roll looks unreachable (the seed byte is compared with `0x40` then `0x20`); only the bit-6 pause toggle forces it. `work/ext_c64/` (C64 source) and `work/ext_c64_flicker/` cloned as references.
- Trumble sprites, draft (branch `mission-trumbles`): up to six furry blobs drawn into the off-screen bitmap each frame by `mxFlightDraw`, a ninth vector in the flight table (+3 bytes there, +3 for the default stub: default image
  125 -> 131 bytes, Constrictor image 587 -> 593, plans 223 -> 229). **Hook site corrected: it is the `call transferBuffertoScreen` in `Spaceflight` (`&1E4D`), not `drawViewPorttoScreen` (that is only the hyperspace tunnel path; the earlier
  "single jp" claim in `docs/_missions.md` section 11 was wrong).** One 16 x 14 pixel shape (`src/elite/missions_trumble_art.txt` -> `tools/sprite_enc.py` -> `missions_trumble_data.asm`: a lumpy, slightly off-round body with irregular stubby spikes
  like the Claude Code asterisk, no eyes, pen 3), OR-blitted; positions in bytes/lines kept inside the frame, velocities 0/+1/-1 as on the C64, one Trumble moved per call, shown = one per Trumble up to six. **Measured: Trumbles image 562 of 610
  bytes (48 free); the sprites cost 270 bytes (code about 210, shape 56, state 28).** Bug found and fixed on the way: `mxMoveSprite` clobbered `C`, the number of sprites, so after a move the draw loop ran off the 6-entry state array and drew about 100
  garbage sprites, some into the dashboard rows of screen memory (the live game showed a garbled dashboard). The unit tests missed it because they only looked at the first six records; `tools/test_trumble_sprites.py` now has a regression case
  (a call that moves a Trumble must leave no stray bitmap bytes outside the sprites and the frame) and a live-loop screenshot. All suites pass again (launch 12, trumbles 7, flight 14, plans 5, docked 25, sprites 9).
- No needless overlay loads (branch `mission-trumbles`): the docked stub now tests the trigger before it touches the disk. A 9-row system table (`mxStageTable`, galaxy/x/y: the seven
  Constrictor hint systems, Ceerdi, Birera) and the stage in the state byte tell it whether the player is at the system the current stage wants; the offers need galaxy 1-2 (Constrictor), rank 5 and
  galaxy 3 (plans), cash (Trumbles). The overlays dropped their own tables and place checks (they only advance the stage and show the text). **Result: a docking that has nothing to do takes 0 ms
  extra (was about 1,750 ms for every docking during a hunt or while the plans are aboard); only a docking at the right system, an offer or a reward loads a module (about 1,900-2,100 ms).**
  Sizes now: stub 242, `MISSIONC.BIN` 565, `MISSIONP.BIN` 326, `MISSIONT.BIN` 178; **largest docked need 242 + 565 = 807 of 812 bytes (5 spare)**. Two Constrictor hints were shortened to fit.
  `tools/test_mission_hook.py`: 25 scenarios, nine of them assert the load is skipped (under 300 ms), all pass.
- Trumbles, flight overlays, final layout (branch `mission-trumbles`). **Flight tail** (COMMONXX `&9D9E-&9FFF`) is now a vector table (8 jp entries at fixed addresses: ship table, spawn check, kill, laser,
  recharge, arrival, sun, inventory), an id byte (`mxFlightId` `&9DB6`), the launch hook `mxLaunchEntry` and one mission image. The image files `MFLIGHT0/C/P/T.BIN` are cut from builds with
  `-DFL_C/-DFL_P/-DFL_T` (the default image `0` is what COMMONXX.BIN carries). `mxLaunchEntry` replaces the first call of `launchSequence`; it loads the image the state asks for ("T" Trumbles aboard,
  "C" Constrictor state 1 or 3, "P" plans aboard, else "0") unless it is already there, then `loadIndicator`. It lives in the base part that is identical in every image, so the load can overwrite
  it while it waits. **Measured image sizes: default 125 bytes, Constrictor 587 (23 free, tight), plans 223, Trumbles 286 (161 beyond the default).** Cost: a launch with an image swap takes
  about 3.9 s of emulated time against 2.0 s without (`loadIndicator` alone).
  **Docked:** the stub is 135 bytes (it no longer holds the launch code; it picks C, then P, then T, blocks everything while Trumbles are aboard, and checks the cash for the offer); overlays
  `MISSIONC.BIN` 652 (the two briefings now share a head and tail: 472 bytes of text instead of 552), `MISSIONP.BIN` 362, `MISSIONT.BIN` 178. **Largest docked need: 135 + 652 = 787 of 812 bytes.**
  **Trumbles** (text only): offer once the Constrictor and the plans are finished and cash is 5,017.6 Cr or more (state bit 7 records it, whatever the answer; Y pays 5,000 Cr and gives one Trumble);
  count = word at `&3905` (at most `&7FFF`); on every arrival with Trumbles the food and narcotics are eaten (the tonnes return to the free hold) and count = 2 * ((count + 0..15) OR 4);
  with 256 or more, 14% of the spawn checks add one; at cabin temperature 240 or more the sun halves the count each call; the inventory shows a "Trumbles n" line before the goods. While Trumbles are aboard no
  other mission is offered. No sound, no sprites, no name-hash order (Trumbles are simply last). Tests (cpcxray, all pass): `test_mission_hook.py` 22 docked scenarios (through the real overlay load,
  including offer Y/N, cash 5,017.6 and 5,017.5, Trumbles aboard), `test_launch.py` 12, `test_mission_flight.py` 14, `test_plans.py` 5, `test_trumbles.py` 7 plus a screenshot of the inventory line.
- Overlays (branch `mission-plans`): the docked modules are now separate files loaded at docking. A 97-byte resident stub in the LARGEAXX tail (`src/elite/missions_docked.asm`:
  it hands over to `chkMissions` while an old mission is pending, returns when `killScoreHigh` is 0 (no disk access under 256 points), picks the module from the state byte, patches the
  last letter of the name `MISSION?`, loads the file with the game's `loadFile` at `mxOverlayBase` (`&1775`) and jumps there; it also holds the shared box printer `missionShow`). Overlay
  layout: `jp moduleEntry`, `dw missionTextTable`, module. Overlays: `MISSIONC.BIN` (Constrictor, `missions_overlay_c.asm`, **711 bytes**) and `MISSIONP.BIN` (Thargoid plans,
  `missions_overlay_p.asm`, **362 bytes**), cut from `-DOVL_C` / `-DOVL_P` builds by label. **Docked tail needed: 97 + 711 = 808 of 812 bytes (4 spare) instead of about 1,170 resident.**
  `tools/build_dsk.py --missions` now adds the two files to the DSK (new AMSDOS header, directory entry and block allocation; `--plans` is gone, the flight hooks of both missions are always in
  `-DMISSIONS`; flight tail 575 of 610). The test string is gone (Constrictor strings are 1-10) and `missionOrder` was dropped until Trumbles needs it (code in `docs/_mission_build_plan.md`).
  Tested in cpcxray (`tools/test_mission_hook.py`, 15 scenarios through the real overlay load, `tools/test_plans.py` flight side): all pass. **Cost: about 1.75 s of emulated time per docking
  that loads a module, 0 when all missions are done or `killScoreHigh` is 0.**
- Thargoid plans (branch `mission-plans`, built with `-DMISSIONS -DPLANS`, `tools/build_dsk.py --plans`): docked module `missions_docked_plans.asm` (shared definitions and
  the box printer moved to `missions_docked_defs.asm` and `missions_docked_show.asm`): offer with the Constrictor finished, `killScoreHigh >= 5`, galaxy 3 (bits 2-3 of `&38FD` = 1);
  Ceerdi (215,84) hands over the plans (2); Birera (63,72) pays the Navy energy unit (`extraEnergyUnit` = `&FE`) and +1 rank (3). Flight: while the plans are aboard `mxSpawnCheck` adds a
  Thargoid plus a Thargon on a roll of 200 or more (22%) via `mxSpawnThargoidPair`; `mxRecharge` (replaces `call nz,SUB_ram_3693` in `RechargeEnergy`) gives the Navy unit 3 recharge steps
  per call (ordinary unit 2, none 1). **Measured: docked module 402 of 812 bytes (text 248, code and table 154); flight tail +98 bytes (spawn branch, pair routine, recharge hook), 575 of 610
  used, 35 free.** The Constrictor docked module is 802, so both together (about 1,170) do not fit the 812-byte tail: they need overlays or shared text and code. `tools/test_plans.py`
  (cpcxray, 14 scenarios) passes: docked stages and rewards, spawn pairs only while the plans are aboard, recharge 1/2/3 steps.
- Constrictor special behaviour: `mxLaserHook` (replaces the `ld (ix+34),a` after `sub c` in `applyLaserDamagetoEntity`, same 3 bytes) makes the Constrictor ignore lasers weaker than
  military: the laser power per hit is in C (pulse and beam 15, military 23, mining 50, as in the BBC), a hit below 23 leaves the energy unchanged and returns NZ/NC so nothing counts. Other ships keep the
  original store. **Measured: 36 bytes; flight tail now 477 of 610 (133 free).** `tools/test_mission_flight.py` has five laser scenarios (all 14 pass). Missiles and collisions still hurt it; its ECM and
  missiles come from the hull header and were not checked.
- Constrictor flight part complete (branch `mission-constrictor`): `mxSpawnCheck` (replaces the first instruction of `spawnCommand0` with a 3-byte call, ends with that
  instruction) spawns the Constrictor when the hunt is on, all seven hints are given (stage 7) and the player is in Orarra (galaxy 2, x 144, y 33), unless one is already alive;
  `mxKillHook` (replaces `call getBounty` in `todo_killedsomeone`, where both laser and missile kills are paid, IY = the dead ship's blueprint) sets state 3 when the dead
  ship is the Constrictor and the hunt is on; the docking code then pays 5,000 Cr and +1 `killScoreHigh`. **Measured, whole Constrictor mission: flight tail 441 of 610 bytes
  (lookup helper 15 + table entry 4 + spawn check 128 + kill hook 33 + hull 261), 169 free; docked tail about 772 of 812.** `tools/test_mission_flight.py` (cpcxray, 9 scenarios) passes:
  spawn only at Orarra at stage 7 and never twice; the kill hook marks only a hunted Constrictor. The hooks were called directly, not through a real kill. Nothing wrote into
  `&9E00-&9FFF` in 2.6 minutes of random play, so `tools/size_report.py` now reserves 32 bytes for the stack (placeholder, worst case still unmeasured).
- Constrictor flight part, first step (branch `mission-constrictor`): `src/elite/missions_hull.asm` (261-byte hull, generated by `tools/fessor_hull.py` from the one file
  `Constrictor.asm`, with the owner's permission for that single ship; attribution in the file header) and `mxShipTable` in the COMMONXX tail: `spawnShip`'s
  `ld hl,shipGFXdataTable` becomes a 3-byte `call mxShipTable` in `-DMISSIONS` builds, which serves ship type 19 from a one-entry table, so no stock table moves.
  **Measured: flight tail 280 of 610 bytes used (helper 15, table entry 4, hull 261), 330 free**; COMMONXX changes outside the tail are 3 bytes (`&80CD`) and 2 bytes (`&72A8`).
  `tools/test_flight_hull.py` (cpcxray) spawns type 19: the slot gets blueprint `&9DB1` and the hull's energy `&FC`; a stock Viper spawns the same way. **Correction (same day):** the broken screens
  (horizontal lines at the bottom, a field of red text, a runaway stack) came from the test harness, not the game: it injected calls at an arbitrary stop (the fill routines use SP as a write pointer inside the
  bitmap) and then resumed at the trap address, running the zeroed tail and the bitmap as code. The script now stops at `handleEntitys` (`&5066`) and restores all registers after the calls; the screen is
  then clean, the Constrictor slot is processed (its position changes) and it is drawn (a red dot in the view and on the scanner, it flies off quickly). The snapshot is still undocking at start: run 4 s first.
  Close-up (`work/xray/output/missions_constrictor_closeup.png`): with speed 0 and `res 6,(ix+32)` (spawnShip sets bit 6 and the game re-places such ships; the stock `loc_83AA` clears it) the hull is drawn as a red wireframe wedge at z 342. Hull and ship type 19 work.
- Constrictor hull size measured: 261 bytes (Fessor's `Constrictor.asm`, CPC layout, read only; not committed because `extended/CLAUDE.md` forbids it). The MSX disassembly has the same geometry decoded (`work/ext_msx/ricbit/shapes.asm`), so our own hull can be generated from that.
- Constrictor, docked part (in the `-DMISSIONS` build, `src/elite/missions_docked.asm`, text in `missions_text.txt`): offer at docking with 256 kill points
  in galaxy 1 or 2 (galaxy 2 starts the trail at Cearso), seven system hints (Reesdice, Arexe, Cearso, Errius, Inbibe, Ausar, Usleri; table of galaxy/x/y/string),
  reward of 5,000 Cr and +1 `killScoreHigh` when the state is "killed", all in the state byte `&38FD` (bits 0-1 Constrictor, 4-6 stage). The flight part (hull,
  spawn at Orarra, kill hook that sets state 3) is not built. **Measured: the docked tail is 802 of 812 bytes used, of which 30 are the test string and 21 the
  order routine, so the Constrictor's docked part is about 772 bytes (text 552, code and tables 220).** Plans' docked part will not fit beside it, which is the case for
  overlays. `tools/test_mission_hook.py` runs eight scenarios in cpcxray (all pass, screenshots in `work/xray/output/missions_*.png`). `tools/textenc.py` takes `{0C}` byte escapes.
- Branch `missions-foundation`: docking hook and string table. In `-DMISSIONS` builds the docking sequence calls `missionsDockedEntry` (`&1714`, first byte of
  the LARGEAXX tail) instead of `chkMissions`; it tail-calls `chkMissions` while `ThargonMissionVar` is non-zero, otherwise looks at `missionState` (`&38FD`,
  a save byte the stock game never uses). `missionShow` draws the mission box like `drawFlipChart` but prints from `missionTextTable`, reusing the scan
  loop inside `printStringA` (`&442C`). Measured: the docked tail uses 112 bytes (entry, `missionShow`, `missionOrder` 21, one test string 30) and the
  COMMONXX change is 2 bytes (the call operand at `&72A8`); the flight tail is untouched. Tested in cpcxray (`tools/test_mission_hook.py`,
  screenshot shows the box). `tools/build_dsk.py --missions` writes `work/elite_missions.dsk`; `tools/textenc.py --asm` emits string tables.
- Branch `missions-foundation`: both free tails are now `IFDEF MISSIONS` includes (`src/elite/missions_flight.asm`, `missions_docked.asm`)
  followed by `DS` padding, so stock stays byte-exact and `-DMISSIONS` keeps the file lengths (checked by `tools/check_src.sh`). The first
  content is `missionOrder` (21 bytes, rotate-xor hash of the commander name, mod 3). Only `src/elite` has the scaffold so far; `elite_de` and
  `elite_fr` do not.
- Branch `missions-foundation`: `tools/textenc.py` (optimal encoder for new docked-table text with the existing 214 string refs and digrams;
  `--selftest` round-trips all 254 existing strings; prose compresses only about 26% with the existing tokens: 163 characters -> 121
  bytes, so a mission-specific dictionary is worth measuring) and `tools/size_report.py` (tail usage and footprint of a build against
  stock: COMMONXX tail 610 free, 354 after a 256-byte stack reserve; LARGEAXX tail 812 free).
- Checked the dead-code claims statically and in cpcxray (`tools/dead_trace.py`, new; two runs of 700 random key presses, results in
  `traces/`). The six code-shaped chains in `db` runs are live (tails of `push ix` routines, or a runtime buffer); `altJrPoint*` are
  self-patched jump targets; only `unusedGetFlightMode` and `unusedGetCloakFlag` (10 bytes) are unreferenced. `docs/_architecture.md`
  corrected and gained a "Dynamic labels" section; `docs/_missions.md`, `TODO.md` and `CLAUDE.md` updated (free flight space is the
  610-byte tail only; overlay idea recorded).

## 2026-11-07

- Applied the CPC+ fix to `src/elite_fr/commonxx.asm` too (`getPPI_Input` at `&8F2B`, patched byte `&8F3F`, `ED 79` -> `ED 49`): the assembled `COMMONXX` differs from `work/bin_fr` in exactly that byte. `tools/check_src.sh` expects the patched byte for `src/elite` (`&8DA0`) and `src/elite_fr` (`&8F3F`); German (disk already patched) needs no exception. All three checks pass. Not tested in an emulator (Caprice32 does not reproduce the Plus bug anyway); a patched French disk is not built.
- Applied the CPC+ keyboard fix to `src/elite/commonxx.asm` (`getPPI_Input`, second `out (c),a` -> `out (c),c`, `&8DA0` `ED 79` -> `ED 49`). The assembled `COMMONXX` differs from stock in exactly that byte and equals `work/plus_patch/x/COMMONXX.BIN`; no length change, so no address moves (the `CHEAT.ASC` pokes are unaffected, none lies near `&8DA0`). `tools/check_src.sh` now expects the patched byte for `src/elite`. Built `work/elite_plus.dsk` and tested it in Caprice32 (new `scripts/install-caprice32.sh`): works on a classic 6128 and a 6128+; Caprice32 does not reproduce the Plus keyboard bug (the unpatched disk also works there), so the fix itself is untested on a bug-reproducing Plus emulator (`docs/_cpcplus.md`).
- Found one more pointer table by searching for table use instead of table shape: `CircleParmTable` (20 patch addresses read by `prepareCircleFillMask`; the addresses jump between `&26xx`, `&CExx` and `&F6xx-&F7xx`, which is why the shape scan missed it). Now `dw` in `src/elite`, `src/elite_de` and `src/elite_fr`; all three `check_src.sh` byte-exact.
- Turned the pointer tables of `src/elite/` into `dw`/`jp` with comments: `sfxTableOfFunctions`, `sfxTableRegSettingFunctions` (16 words each), `commandsPatchTable`, `DockedFuncJumptable` (16 `jp`), `shipGFXdataTable` (19 records of `jp` + byte; the `jp` is filler, `spawnShip` reads the address word), `Jumptokens1` (14) and `Jumptokens2` (30 + 4 odd bytes) in `COMMON2X`. Found by a scan for runs of in-range words in `db` lines; `tools/check_src.sh` byte-exact. `disasm_stock.py` was not rerun (edited with a script on the existing files). Same conversion applied to `src/elite_de/` and `src/elite_fr/` (values and sizes read from each build's binary; the French `Jumptokens1` has 17 words, the others 14); `check_src.sh de` and `fr` byte-exact.
- Added the French disks (`Elite (1985)(Firebird Software)(fr).dsk` and `[a]`). Extracted to `work/bin_fr/` and `work/bin_fr_a/`. The code is the English program with French text (no encryption); `tools/map_french.py` + `tools/disasm_french.py` (copies of the German tools) produce `src/elite_fr/`, byte-exact (`bash tools/check_src.sh fr`, now supported). Findings in `src/elite_fr/README.md`: no CPC+ fix, `[a]` is a renamed repack with identical payloads.
- Cleaned `work/`: deleted `ext_EliteSource/`, `ext_EliteMasterSource/`, `ext_ELITE_EXT_DISK/` (each identical to a kept archive: `work/EliteSource.rar`, `work/EliteMasterSource.rar`, `extended/archives/ELITE_EXT_DISK.zip`; `ext_EliteSource` also to `extended/source/`) and `build_fessor_run/` (wiped and rebuilt by `scripts/build-fessor.sh`). Renamed the disk copies in `work/xray/disk/` to the current names (`ELITE.DSK` -> `Elite_UK_original_protected.dsk`, `firebird.dsk` -> `Elite_UK_Firebird_cracked_trainer.dsk`; hashes match the root disks) and updated `CLAUDE.md`, `docs/_cheats.md`, `docs/_missions.md`, `tools/circle_sweep.py`. Snapshots hold no disk name, so they needed no change.
- Settled the save-format disagreements with the CPC International type-in by launching the game in cpcxray and jumping Lave -> Diso: `&3913` is the present system's tech level minus 1 (renamed `marketRandomByte` -> `presentTechLevel` in `src/elite/` and `src/elite_de/`; the market random byte is `&38E1`), and the game stores y at `&43`, x at `&45` (the type-in's names are swapped). `docs/_savegame.md` updated; `check_src.sh` and `check_src.sh de` byte-exact.
- Renamed the Asp mission state byte `todoWorkVariable` -> `aspMissionState` and its branch labels (`drawShipDistanceCheck`, `aspGateClearIfBlueprint1E`, `aspGateReset`) in `src/elite/commonxx.asm`, with Spectrum cross-reference comments (`&A7D9`, `&A7E6`, `&9DD6`, `&9DDD`); docs updated. `tools/check_src.sh` byte-exact. Backup: `work/backup_src_pre_asp/`.
- Answered two mission-plan questions (`docs/_missions.md` section 7): the CPC's main-loop spawn is `handleEntitys` -> `spawnCommand0` (hook point for a 22% Thargoid rule), and the escape-pod clear is off by one (starts at the market byte `&38E1`, keeps alien items `&38F2`). `&38E1` identified as the market random byte in `docs/_savegame.md`.
- Disassembled the German build into `src/elite_de/` (byte-exact, `tools/check_src.sh de`): `tools/map_german.py` pairs the German code with the English by lockstep walking (81% of English code bytes), `tools/disasm_german.py` transfers names and comments and verifies by assembling. Findings: not relocated code but the same program with German text; the German disk already contains the CPC+ keyboard fix; `NOTMUSIC` is `COMMONXX` `&6000-&6FFF`; `COMMON2X` differs in 270 bytes.
- Unpacked `work/elite plus/ELITE.EXE` (EXEPACK, a hacked PC Elite Plus) with the new `tools/unexepack.py`; output in `work/elite plus/extracted/` (`ELITE_unpacked.EXE`, raw `ELITE.img`, `strings.txt`). The mission texts (stolen police ship, asteroids) are in the image, so the logic can now be disassembled.
- Three more passes on the Spectrum map: own comments for the disc/circle code (with a header block for the whole routine), six more unmatched maths routines named and commented (`normalize_position_vector`, `square_position_component`, `rotate_vertex_axis`, `add_sign_mag_bytes`, `de_plus_hl_div_2`, `minus_de_plus_hl_div_2`), ten Fessor `todo_*` placeholders renamed from exact matches, and about 70 comments for text, charts, trade, ship movement and spawning. `tools/gen_spectrum_map_doc.py` regenerates `docs/_spectrum_map.md`. `tools/check_src.sh` byte-exact.
- Wrote our own comments for the maths routines Fessor had not identified (27 routines: squares-table multiply, the two divides, DVID3B2 projection divide, square root, cross-product helpers, face visibility); renamed three more from the Spectrum map (`div_hl_a_de`, `add_scaled_nosev_to_roofv`, `line_of_sight_vector_component`). `tools/check_src.sh` still byte-exact.
- Seeded `src/elite/` from the ZX Spectrum disassembly: `tools/spectrum_map.py` (routine matching by instruction skeleton plus call-graph propagation), `tools/spectrum_data_map.py`, `tools/apply_spectrum_names.py`; 43 generic labels renamed, about 140 `; ZX Spectrum: name (&ADDR)` comment lines, `docs/_spectrum_map.md`. `tools/check_src.sh` still byte-exact.
- Confirmed the UK disk has no Anaconda or Transporter: the ship table and blueprint sizes equal the ZX Spectrum's, and a header scan of the raw disk finds only the 14 known blueprints (`docs/_architecture.md`). Boulder is present.
- Found Amtix's "infamous bug": the disc fill (`ce2func43FillCompleteLinesinBM`, `&243A`) uses SP as a write pointer and relies on a line-count clamp at `&245B`; without it, big off-centre planets overwrite memory below the bitmap. The stock build survives a 131k-input sweep (`tools/circle_sweep.py`, `docs/_architecture.md`).
- Matched Amtix's four missions to the code (`docs/_missions.md`): "pirates taking over Space Station 1" is the Thargoid invasion of system 0's station; the jammer is its tool. Gave the probability of the hidden "boarded by pirates" hazard (about 1.8% per arrival).
- Diffed Redbox's UK CPC+ patch disk (`work/plus_patch/`): the whole fix is one byte in `COMMONXX` (`&8DA0`, second `out (c),a` -> `out (c),c` in `getPPI_Input`), no length change. Documented in `docs/_cpcplus.md`.
- Compared the Atari ST Cougar mission with the CPC cloak-Asp (`docs/_missions.md`, section 2): the CPC does spawn escorts, `todoWorkVariable` is a 0-3 state byte, the canister is ordinary. Cloned `Rasmus-M/elite-skoolkit` (ZX Spectrum) and `ricbit/elite` (MSX) into `work/ext_msx/`; `elite-msx-skoolkit` does not exist online.
- Added `docs/_cpcplus.md` (CPC+ keyboard bug from the CPCWiki thread, Redbox's patch, plan for our own fix) and `docs/gamefaqs_player_guide_nemrac.md` (saved GameFAQs guide, third-party).
- Named the equipment bytes of the commander save: `&38FD`/`&38FE`/`&3905`/`&3906` are unused laser slots (the equipment block is indexed from `&38F8` by shop item number), `&3928-&3930` is the sun position (`savedSunPos{X,Y,Z}`). Named data tables `charPatchD628`..`charPatchD7D8`, `dustParticleAdrTable`, `tblKeyFlagOffsetMask`; turned `dat_5F55` and `dat_1600` (immediates) into numeric operands (`tools/rename_maps/2026-11-07-dat-batch2.txt`). `tools/check_src.sh` still byte-exact.
- Added `tools/textcomp.py`: optimal re-tokenisation of `stringsTable2` (`&0FCA`, 254 strings) and the in-flight
  `stringsTable` (`&2FAF`, 145 strings) with the existing refs and digrams, expansion checked identical. Result: the
  original token choice is already near optimal, only 48 bytes saved (36 + 12, about 1.7%). Not applied to `src/elite/`.
  Found that `LARGEAXX` ends in 812 zero bytes (`&1714-&1A3F`); whether they are free at runtime is unchecked
  (see `docs/_missions.md` section 4). Confirmed in cpcxray: reloaded from disk at every docking (zero tail when docked, unused flight-side bytes when flying), so safe for docked-only code and mission text.

### Added
- `tools/dbcode.py`: finds code-shaped, unreferenced chains in the `db` runs of `COMMONXX`: six routines, about 130-155 bytes; a short trace
  was inconclusive (`docs/_architecture.md`, point 4).
- `tools/deadcode.py`: reachability analysis of `src/elite/` (needs sjasmplus listings, see its header). Finds 28 bytes of labelled dead
  code; most dead code is in `db` runs. Dead-code findings and a failed attempt to locate Fessor's switched-off blocks by byte pattern
  are in `docs/_architecture.md`.
- `docs/_missions.md`: a numbered list of the eight missions (1 to 3 in the CPC, 4 to 8 candidates) with the game systems each touches and the
  changes the CPC needs, and a table now covering BBC, Apple II, C64, NES, Atari ST, MSX, CPC and Elite Plus.
- Shallow clones of the Atari ST, NES and TI-99/4A-from-MSX sources in `work/ext_st`, `work/ext_nes`, `work/ext_msx` (untracked, read-only).
- Found the C64 Trumbles source (Mark Moxon's annotated repo) and read its offer, breeding, noise and sun-death code; behaviour table, a CPC hook map and an analysis of drawing crowding Trumbles as software sprites (about 300-450 bytes, no erase needed because the off-screen bitmap is cleared every frame) are in `docs/_missions.md`; links in `docs/_references.md`.
- `tools/elitekey.py`: reads the save key from a game disk (finds `EquipShip` in `LARGEAXX` by its code signature, same result
  as the fixed offsets 0x2BE English and 0x2C2 German); `tools/savedec.py SAVE DISK.dsk` uses it, no extracted files needed.
- `docs/_missions.md`: plan (only) for porting the BBC and Apple II missions to the CPC.
- `magazines/elite-commander.pdf` (CPC International 3/86 commander type-in) and its extracted text.
- 109 `dat_` labels in `src/elite/` renamed to real names (save block, equipment, dust, circle, sound, entity workspace, planet data); still byte-exact. `tools/rename_dat.py`, `tools/check_src.sh`, `tools/rename_maps/`.
- `CHEAT.BAS` (ours, source `src/cheats/CHEAT.ASC`; it replaces the original on `work/firebird_cheat.dsk`), an interactive trainer: asks Y/N per cheat plus start cash, own-cloak and a mission stage; adds pirate-boarding
  removal, unlimited-hold toggle and mission fast-forward (`tools/build_cheat.sh`, `tools/cheat_tokenise.py`; sources and listings in `src/cheats/`, tracked; see `docs/_cheats.md`).
- `src/elite/`: reassemblable, byte-exact source of the stock English build (four files; see its README).
- `tools/savedec.py`: decodes a commander save (XOR with the code at `EquipShip`, plus both checksums).
- `scripts/build-fessor.sh`: rebuilds Fessor's patched source in `work/build_fessor_run/` and compares it with
  the beta disk. Run by the user; all five files matched.
- `extended/source/` (Fessor's source extracted), `extended/FESSOR_VS_STOCK.md` (changes vs stock),
  `extended/CLAUDE.md` (what each file is and the no-re-upload rule).
- `magazines/` with the Amstrad Action 3 and Amtix 13 scans, extracted text and an index.
- `docs/` (notes split by topic), `TODO.md`, this file.

### Found
- The Atari ST source's reward routines are swapped in their comments: by `dock_check` the Constrictor pays 10,000 Cr and the Thargoid
  documents give the military energy unit (matches the MSX wiki). `docs/_gameplay.md` had them the other way and is corrected.
- MSX Elite (Rob Nicholson, Mr. Micro) has the same five missions as the Atari ST, one per 64 jumps outside the first galaxy (read in
  the TI-99/4A conversion of the MSX code, `Rasmus-M/elite-ti994a`). The mission table in `docs/_missions.md` now covers BBC, Apple II, C64,
  NES, ST, MSX, CPC and Elite Plus.
- The Atari ST source (Mr. Micro 1988, adapted from MSX) runs five missions in a fixed order every 64 jumps and contains the supernova,
  Cougar and Thargon-invasion missions, so those are not CPC-only. The NES source has three missions (Constrictor, Thargoid plans,
  Trumbles). No source has the Stolen Police Ship (Elite Plus only). Links in `docs/_gameplay.md` and `docs/_references.md`.
- Commander cash is a word pair, not a 32-bit number: the high word counts 1,000 Cr, the low word the decicredits below
  10,000 (tested: high 2, low 2500 shows 2250.0 Cr). `tools/savedec.py` and `CHEAT` corrected. Source: the CPC
  International type-in `magazines/elite-commander.pdf`, which also confirms the laser, equipment and mission-flag bytes
  (see `docs/_savegame.md`).
- The 23,835-line `EliteMasterSource.asm` is the beta disk's source: it builds byte-identical `LARGEAXP`,
  `COMMONXP`, `COMMON2P`, `NOTMUSIP` and `SHIPSETB`. The second, 28,615-line version is an older fork.
- Commander save format decoded (104 bytes at `&38CB`, field map in `docs/_savegame.md`). `Elite Savegame.dsk` holds
  **German**-build saves; `1.BIN` is a stock-key save named `1`.
- `Elite - Gold.dsk` was `ELITE.DSK` plus a stray `TES.BIN`.
- Amtix 1986: the four special missions, the unused-code statement and the "planet drifts off screen" crash.

### Changed
- `docs/_gameplay.md`: the BBC Constrictor mission is offered in galaxies 1 and 2 (it said galaxy 1 only); `docs/_missions.md` notes the Trumbles trigger is cash of 5,017.6 Cr in the code, not the figures on the deep-dive page.
- `docs/_savegame.md` field map rewritten from the code: cargo table starts at `&38E2`, kill score is 24 bits, `&38F3` is free hold space, `&38FB` the large cargo bay, `&390D` the present system's seed, `&3914` market stock. `tools/savedec.py` prints these.
- Disks renamed: `ELITE.DSK` to `Elite_UK_original_protected.dsk`, `Elite_1985_Firebird_Software.dsk` to
  `Elite_UK_Firebird_cracked_trainer.dsk`, `Elite - Gold [G].dsk` to `Elite_DE_cracked.dsk`,
  `Elite Savegame.dsk` to `Elite_DE_savegames.dsk`; `IMG_9858.JPG` to `Elite_DE_controls_card.jpg`.
- `extended/` reorganised into `archives/`, `forum/`, `reference/`, `source/`.
- `notes.md` corrected: the beta build is byte-identical to the source (it said "not identical", which came
  from comparing files with and without the AMSDOS header).

### Removed
- `Elite - Gold.dsk` (duplicate of the UK original), `extended/archives/EliteSource.rar` (kept extracted in
  `extended/source/`), `extended/archives/EliteMasterSource.rar` (older fork; extracted copy remains in
  `work/ext_EliteMasterSource/`).

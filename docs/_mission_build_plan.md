# Plan (stored copy; status notes in the headings): dead-code check, then measurement branches for Constrictor, Thargoid plans, Trumbles

## Context
Goal of the branches (user, 2026-11-08): **get a precise size measurement** of each mission, not (yet) a polished
release. So each branch is a measurement prototype: implement the mission's real code and text, assemble, and report
exact bytes used in each memory region. The decision inputs are the free-space figures, so those are checked first.
Earlier decisions: missions = Constrictor, Thargoid plans, text-only Trumbles; foundation branch, constrictor ->
plans stacked on it, trumbles off the foundation; BBC-style gates for triggers. Plans are also stored in the repo as
`docs/_mission_build_plan.md` (user: "store the plans here").

## Step 1: dead-code assumptions (DONE 2026-11-08; results in `docs/_architecture.md`)
Assembled `src/elite/commonxx.asm` into the scratchpad listing and checked each candidate from `docs/_architecture.md`
("Code hiding in the db runs") for labels, source references and little-endian address words in the image:
- `&53D7`: middle of `LAB_ram_53cf`, which the previous routine falls into (`push ix/iy`, `move_ship_forward` x3). **Live.**
- `&5DD2`: inside `SUB_ram_5dcf`, called from `&51CC` and `&563C`. **Live.**
- `&8243`: inside `execSpawncmd4` (`&8242`), targeted by `jr z`. **Live.**
- `&8365`: inside `spawnAtEntityCoordinates` (`&8364`), targeted by `jr z`. **Live.**
- `&89F5`: inside `LAB_ram_89f4`/`LAB_ram_8a10`, targeted by `jr`. **Live.**
- `&6C0A`: inside `dustParticleAdrTable`, a runtime buffer, not code.
Cause: these routines start with `push ix`/`push iy`, which `tools/z80dis.py` cannot decode, so they stayed `db` and
`tools/dbcode.py` saw their tails as unreferenced. **The claimed 130-155 bytes of dead code in db runs is about 0.**
What is left statically unreachable: `altJrPoint3` + `alt_animated_effect_reset` (`&7198-&71AE`, 23 bytes), `LAB_ram_8aaa`
(`&8AAA-&8AAE`, 5), `unusedGetFlightMode`, `unusedGetCloakFlag` (about 10): **about 38 bytes**, each still to be confirmed
dynamically (a `jr` from a db run would hide a reference). Fessor's "about 450 bytes" stays unverified.
Revised flight-time budget: **610 + about 38**, not 610 + 180. This makes space the main risk: the Constrictor's flight part
(hull about 250 bytes, spawn and kill hooks) uses most of it, Plans' 80 bytes of flight code is tight, Trumbles' flight hooks may not fit.

### Dynamic part (done: `tools/dead_trace.py`; see `docs/_architecture.md` for the results)
Use `~/.local/bin/cpcxray` via its Python MCP client (see CLAUDE.md), load `work/xray/output/firebird_in_flight.sna`
with the Firebird disk.
1. Put execute breakpoints (`breakpoint_add(address, kind="pc")`) on the entry of every candidate: `&7198`, `&719D`, `&8AAA`,
   `unusedGetFlightMode`, `unusedGetCloakFlag` (addresses from the listing). Also on `&53CF`, `&5DCF`, `&8242`, `&8364`,
   `&89F4`, `&8A10` as positive controls: they must fire, which proves the harness works.
2. Drive a long session (background job, one output file): launch, fly, fight pirates, fire missiles, ECM, energy bomb,
   hyperspace and galactic jump, dock, undock, escape pod, cloak (forced with `memory_write` of `Missionflag` bit 6), supernova
   state (`FlightMode`), tunnel/witchspace. Count hits with `breakpoint_list`; interrupts off for comparable runs.
3. Also check the 812-byte `LARGEAXX` tail (`&1714-&1A3F`) with write and read breakpoints across dock/undock cycles, and
   `&0040-&083F` while docked, to confirm they are free.
4. Record results in `docs/_architecture.md` (replace the "130-155 bytes" paragraph and the "does not exercise" note), correct
   the budget in `docs/_missions.md` section 4 and in `TODO.md`. Correct `CLAUDE.md` Open items if numbers change.
Outcome: a measured list of safe-to-reuse bytes. If a candidate fires, it is live and is removed from the list.

### Step 1b: list of dynamic labels (DONE, `docs/_architecture.md` "Dynamic labels")
Add a section "Dynamic labels" listing every label whose bytes change at runtime or sit inside an instruction, with address,
role, who writes it and how it was found. They are the places that break static dead-code and free-space claims, so a
mission patch must not land on them. Interpretation: self-modifying code operands, runtime buffers inside the code image
and labels that are equ-aliases into instructions. Sources, all read-only first:
- `equ` aliases at the end of `src/elite/*.asm` (labels inside instructions), `smc*`/`patch*` names (for example
  `smcIndicatorPatch1/2`, `patchviewPortInk0/1/3`, the line-plotter patches, `commandsPatchTable` targets).
- Runtime buffers in the image: `dustParticleAdrTable` (`&6BFE`), entity area `&1A40-&1B7A`, `dataShortTunnle`, galactic chart
  buffers `&3B3F-&3B69`, `&3D2D`, and the `&0040-&1A3F` / `&A600-&BFFF` swap area.
- Dynamic confirmation in cpcxray: write breakpoints (`kind="write"`) over the code image `&1A40-&9FFF` during the Step 1
  session; any write outside the known data/variable ranges is a new entry. Table columns: address, label, kind
  (smc operand / buffer / alias), writer routine, status (confirmed static / confirmed dynamic).
Cross-reference this list from the dead-code section and from `CLAUDE.md` gotchas.

## Step 2: measurement branches (each ends with a size report, not a release)
Common measurement method: assemble with the `-DMISSIONS` variant (stock stays byte-exact in `tools/check_src.sh`), then
read the `sjasmplus --lst/--sym` output and report with a small script `tools/size_report.py`: bytes used in `COMMONXX`
tail (`&9D9E-&9FFF`), `LARGEAXX` tail (`&1714-&1A3F`), reclaimed dead bytes, per mission and cumulative, plus bytes
still free. Overflow stops the build (assertion in the source), so the figure is exact.

- `missions-foundation` (from master; started 2026-11-08; DONE so far: docking hook, `missionShow`, test string, `missionState` `&38FD`, tested in cpcxray, docked tail 112 bytes used; `tools/textenc.py` and `tools/size_report.py` done; the four save bytes `&38FD`, `&38FE`, `&3905`, `&3906` are documented never read or written (`docs/_savegame.md`), so mission state needs no bigger save block: candidates state `&38FD`, Trumbles count `&38FE`, overlay queue/order `&3905`, spare `&3906`; the remaining items below are open): save key left unchanged (dropped 2026-11-08: old saves keep loading while the `EquipShip` window, LARGEAXX offset `&2BE` + `&68`, stays identical; `tools/size_report.py` asserts it), mission state byte (candidates `&38FD/&38FE/&3905/&3906`, first check
  no loop indexes them), new-table entry point for strings (~15 bytes, `printStringA` ~commonxx.asm 5808), `tools/textenc.py`
  (inverse of `tools/elitetext.py`, round-trip over the 254 strings), `chkMissions` dispatch (~commonxx.asm 855) into the
  `LARGEAXX` tail, `tools/size_report.py`. Reports its own overhead in bytes.
- `mission-constrictor` (from foundation; docked part BUILT 2026-11-08 and measured: about 772 bytes of the 812-byte `LARGEAXX` tail, i.e. text 552 + code/tables 220; flight part open): hull via `tools/bbc_hull_to_cpc.py` (validate on Viper/Sidewinder), ship table entry 19
  in `shipGFXdataTable`, docked trigger/briefing/hints/debrief in the `LARGEAXX` tail, spawn in `spawnCommand0`/`handleEntitys`,
  kill hook in `targetisKilled`, reward via `getMoney` and `inc killScoreHigh`. Reports exact bytes per region.
  **Built 2026-11-08: the whole Constrictor mission, including the military-laser rule (`mxLaserHook`, 36 bytes; total flight tail 477/610, 133 free). Without the laser rule: flight tail 441/610 (helper 15 + entry 4 + spawn check 128 + kill hook 33 + hull 261), 169 free; docked tail about 772/812.** Tested in cpcxray with forced states and direct calls; a real playthrough is still open.
  **Hull size measured 2026-11-08: 261 bytes** (23-byte header, 17 vertices x 6 = 102, 24 edges x 4 = 96, 10 faces x 4 = 40), counted from Fessor's
  `extended/source/Constrictor.asm`, which already has the Constrictor in the CPC layout (the BBC/CPC vertex, edge and face layouts are the same
  apart from the header). **Licensing:** `extended/CLAUDE.md` forbids committing or publishing his files without asking him, so his hull must not go into this repo.
  Plan: generate our own hull bytes from the decoded MSX data (`work/ext_msx/ricbit/shapes.asm`: 18 vertices incl. one duplicate, 24 edges, 10 face
  normals and edge lists) with a script, and compare with his file locally only; or ask him (CPCWiki profile u=1495) for permission. Free flight tail after the hull: 610 - 261 = 349 bytes
  for the table entry (4), spawn and kill hooks. The ship table `shipGFXdataTable` (`&1B78`, 4 bytes per ship) needs a free slot after entry 19: check what follows it.
- `mission-plans` (from constrictor; BUILT 2026-11-08: docked module 402 bytes, flight +98, tests pass; see CHANGELOG): trigger, 22% Thargoid+Thargon spawn at the top of `spawnCommand0`, Navy energy unit
  (`extraEnergyUnit`, `RechargeEnergy`). Reports incremental bytes and whether it still fits with the Constrictor.
- `mission-trumbles` (from foundation, text only): offer at cash >= 5,017.6 Cr, count byte(s), arrival hook (`&4E58`), sun death,
  inventory text. Reports incremental bytes and whether it fits alone and on top of Constrictor + Plans.
Deliverable: a table in `docs/_missions.md` of measured bytes per mission and per region, and a verdict on what fits together
(for example Constrictor + Plans, or Constrictor + Trumbles). Behaviour is tested only enough to prove the code is complete
enough to count (state forcing in cpcxray), full playtests come after the size verdict.

## Idea (user, 2026-11-08): sequential mission overlays instead of resident missions
Missions run one after another, so only the active mission's code needs RAM. Load one overlay file per mission
(for example `MISS1.BIN`) into the free regions (`COMMONXX` tail for the flight part, `LARGEAXX` tail for the docked part)
and, when the mission is done, load the next overlay over it. RAM cost becomes the **largest** mission, not the sum.
Order can be randomised per commander from bytes that already exist (letters of the name, a checksum of the name), so no
new save bytes except the queue position. Points to settle in the measurement branches:
- Swap point: at docking (after `loadLARGEAXX`, before `chkMissions`) and at launch, when no mission object is alive. Needs a
  small loader (reuse the `loadLARGEAXX`/`loadMusicnIndicator` file-load code; size to be measured) and a free disk slot per file
  (check free sectors on the Firebird DSK; `tools/build_dsk.py` currently keeps file sizes fixed, so it needs to add files).
- Persistent missions (Trumbles keep breeding after the purchase) do not fit "replace when done": give them an end condition
  or keep only their small resident part.
- Dependencies: Plans needs the Constrictor in the BBC order; with a random order, gate Plans by galaxy 3 and make the
  briefing text independent, or draw the order only among independent missions.
- Save/load must restore the right overlay from the state byte (the loader runs after a load too); disk swaps by the player are a risk.
- Each overlay's size is measured separately, so the branch report gives max (needed RAM) and sum (disk).

## Idea: mission order from the pilot name (user, 2026-11-08)
**Decided 2026-11-08: rotate-xor hash.** Order = hash of the saved name (`&38CB`) modulo the number of valid permutations (Plans after Constrictor leaves 3 of 6); only a
3-bit done-mask is stored (`&3905`). No order byte, stable across save/load, new commander = new order. Trumbles is cash-gated.
Hash: for each name byte up to the NUL (at most 10), `a = rotl(a,1) xor byte`, then `a mod 3` picks 0 = Constrictor, Plans, Trumbles;
1 = Constrictor, Trumbles, Plans; 2 = Trumbles, Constrictor, Plans. Results: LEN 2, PETER 1, TEST 0, CHEATER 2, JAMESON 1, PETE 2.
Z80 routine (assembled with sjasmplus, **21 bytes**, `A` = 0..2 on return; verified against the Python model):
```
missionOrder:  ld hl,0x38CB / xor a
mo1:           ld c,(hl) / inc hl / inc c / dec c / jr z,mo2 / rlca / xor c / jr mo1
mo2:           sub 3 / jr nc,mo2 / add a,3 / ret
```
Checked 2026-11-08 on `work/saves/` (German build, key offset `&2C2`; checksums ok): names are plain uppercase ASCII ending in a NUL, and the bytes after the NUL are stale (`LEN` is followed by `SON`, left over from JAMESON), so the hash must stop at the NUL, as the routine does. The routine reads the name from RAM at `&38CB`, where it is not encrypted. LEN, PETE and PETER decode to 2, 2 and 1, as predicted. The UK key does not decode these saves.

## Overlays: BUILT (2026-11-08)
Resident stub (97 bytes) + one overlay file per mission, loaded into the LARGEAXX tail at docking by the game's own `loadFile` (`MISSIONC.BIN` 711 bytes, `MISSIONP.BIN` 362 bytes). Docked
tail 808 of 812 bytes; about 1.75 s of emulated time per docking that loads a module; the flight code of both missions stays resident (575 of 610 bytes). Details and tests in `CHANGELOG.md`.
Dropped `missionOrder` (21 bytes, see the snippet above) from the build until Trumbles exists: with the Constrictor before Plans, the name hash only moves Trumbles.

## Housekeeping
Commits without any Claude/Anthropic trailer (user rule). Mirror label renames into `src/elite_de/` and `src/elite_fr/`; run
`bash tools/check_src.sh`, `... de`, `... fr`. Update `CHANGELOG.md`, `TODO.md` and the docs in the same step as each fact.

## Verification
- Step 1: positive controls fire, candidates' hit counts reported; the doc numbers change accordingly.
- Step 2: `check_src.sh` 4x ok on stock; variant build assembles; `size_report.py` totals equal the difference of the
  assembled bytes against stock (cross-check with `cmp`).

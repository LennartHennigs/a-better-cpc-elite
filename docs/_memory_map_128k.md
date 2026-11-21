# Memory map: the 128K build (branch `elite128`)

The 128K layout (RAM banks, the `&4000` screen window, the resident glue and what is free). The 64K game's map is in `_memory_map.md`; overview of the build: `_128k_version.md`; details and findings: `src/elite128/README.md`. Free-byte figures are measured from `work/elite128/c128.sym` (`tools/check_src128.sh` writes it).

## Gate Array and banking

- The 128K build (`src/elite128`, branch `elite128`) uses these banks: 6 = fill module and records at `&4000` (config `&C6`), 4 = `LARGEAXX` copy and mission overlays, 5 = `INDICATO` and the mission flight images (copied back by `bankLargeaxx`, `mxBankOverlay`, `mxBankFlight` at `&9C80`), 7 = the code block at `&C000`; its `README.md` has the findings. The interrupt (myVBL) runs on its own stack and can only call code in banks 0 and 2, or in bank 7 while a draw configuration (C1/C3) shows it.

- The CRTC/Gate Array fetch video only from the base 64K (banks 0-3). The RAM banking register (`&7Fxx`, `11xxxyyy`) changes what the CPU sees, never what is displayed, so the extra banks 4-7 cannot be shown.
  Source: [CPCWiki Gate Array](https://www.cpcwiki.eu/index.php/Gate_Array) ("The Video RAM is always located in the first 64K").
- Configs used by the double buffer: C0 = banks 0,1,2,3; C1 = 0,1,2,7; C3 = 0,3,2,7; C4-C7 = bank 4-7 at `&4000` with banks 0, 2 and 3 as in C0 (far calls: C6 for the fill module, C4/C5 for the bank copies, C7 at boot). C1/C3 show bank 7 at `&C000`, so code kept there stays visible while the CPU draws at `&4000` (bank 1 or 3);
  R12 `&1C` displays `&4000` (bank 1), `&3C` displays `&C000` (bank 3). C0 hides bank 7: code running there must be elsewhere, and interrupts are off.
- The port is write-only: the draw configuration is kept in `curCfg` (C1 or C3, `dbShown` is the one the CRTC shows); the transient far-call configurations are not recorded anywhere, so an interrupt that remaps must work out the configuration from the interrupted PC and SP (`src/elite128/CLAUDE.md`). Needs 128K; a 464/664 shows "128K CPC REQUIRED".
- The CPCWiki pages return 403 to `curl` and WebFetch; read them with Claude in Chrome (`get_page_text`).

## Layout (branch `elite128`; first measured 2026-11-12, glue and music rows updated 2026-11-21)

CPU view in flight (config C1 or C3; the flip alternates them). Free = bytes not used by anything built today.

| CPU address | RAM bank | What | Used | Free |
|---|---|---|---|---|
| `&0000-&003F` | 0 | vectors (`&0038` IM 1 -> `&2815`) | all | 0 |
| `&0040-&1A3F` | 0 | flight and on the title: the firmware's parked upper RAM (6.5 KB, mostly zero; `loadIndicator` swaps it with `&A600-&BFFF`, `loadLARGEAXX` restores it at docking); docked: `LARGEAXX` `&0840-&1A3F` (4608 B incl. the mission stub) | all | 0 (the parked zeros are not safe to reuse) |
| `&1A40-&3F5F` | 0 | `COMMONXX` core: variables, ISR (`&2815`), disc fill, indicators, trade code, player state `&38CB-&3A..` | all | about 18 B of pinned dead bytes (`loc_293F` 8, `unusedGet*` 10; the file names of the music are in use again since the title music) |
| `&3F60-&7FFF` (window) | 1 or 3 (C1/C3), 4/5/6 (far calls) | screen page A or B (8 scan line blocks of 2 KB: 1536 B pixels + 512 B gap); the gap holds the font and the old COMMON2X tables and code | all | 0 (the only free gap runs are the font, filled at run time) |
| `&8000-&805F` | 2 | `hullQ` (8 entries x 8) and `hullStack` (32) | all | 0 |
| `&8060-&9C6B` | 2 | stock `COMMONXX` code from the old `&7D5E-&9FFF` plus the filled-hull glue (`hullDraw`, queue, `bankInit` boot code `&98AC`, title selection) and the disc trampolines (`CAS_*` run the firmware on `discStack`, `&A400-&A4FF` in the unused first bitmap lines, because the game stack is in bank 7 and the upper ROM hides it) | all | **3** (glue ends `&9C7D`, measured 2026-11-21; the mission bank table is fixed at `&9C80`). `bankInit` (`&98A3-`) is dead after `Init_`: its first 192 bytes are overwritten by the overlay of `lasersights128.asm` (laser sights, `musicState` and `musicHook` of the title music; 183 of 192 bytes used, 9 free): new resident code goes there or into a far-call module |
| `&9C80-&9D8D` | 2 | mission bank routines (`mxBankTable` `&9C80/&9C83`), flip stubs (`dbFlipTail`, `dbIsr`, `dbCopy`), `hullFindType` | all | **13** (pad before `&9D9E`) |
| `&9D9E-&9FFF` | 2 | flight tail: the mission image in use (default 143 B, C 593, T 585, S 337, R 261, P 245), slot 608 B, must end at `&9FFE` | 608 for the largest | **15** with the largest image, 465 with the default one |
| `&A000-&BFFF` | 2 | off-screen bitmap (128 lines x 64 B), wiped every frame; `&9FFE-&9FFF` and the bytes below `&A000` take the interrupt's push | all | 0 |
| `&C000-&FFFF` | 7 | code block (15,870 B of the stock `&3F60-&7D5D` plus title tables), `MainStackNStrings` `&F39B` (game stack grows down into the block's tail) | 16,383 | **1** (the slot `&DF02-&EF01` is the flight-only 4 KB that the title music overlays: loaded at boot, `NOTMUSIC.BIN` puts the flight code back at the title exit) |

Banks not visible at once (mapped over the window by `out (c),c`, never while the stack is in them):

| Bank | Content | Used | Free |
|---|---|---|---|
| 4 (`&4000-&7FFF`) | `&4000-&48FF` four docked mission overlays (4 x `&240`, largest C 561 B), `&4900-&5AFF` copy of `LARGEAXX` (4608 B, copied to `&0840` at every docking) | 6,912 B | **9,472 B** (`&5B00-&7FFF`) |
| 5 | `&5000-&5FFF` `INDICATO` (dashboard graphics, 4096 B), `&6000-&7EDF` 13 flight images (default, packs 1-7, C P T S R: 13 x `&260`), loaded from the one file `INDICATO.BIN` | 11,744 B | **4,640 B** (`&4000-&4FFF` 4,096, `&7EE0-&7FFF` 288) |
| 6 | `&4000-&45DB` fill module + flip code (1,489 B built, copy length `&600`), variables `&4F00`, tables `&5000-&5F00` (built by `fillInit`), `&6000-&6534` hull records (1,333 B) | about 5,100 B | **about 9,200 B** (`&45DC-&4EFF` 2,340 incl. up to 47 B to the copy limit, `&6535-&7FFF` 6,859) |
| 1 / 3 | the two screens (the CRTC shows one, the CPU draws the other) | 32 KB | 0 |

Totals: 128 KB; **about 27.5 KB free**, all of it in banks 4-6 (data only: code that runs must sit in bank 7, the resident part of bank 2, or be a far-call module like the fill). Code space is the scarce kind: **3 + 13 + 15 resident bytes, 9 in the overlay on `bankInit`, and 1 byte in bank 7**, plus about 2.3 KB of module code space in bank 6 (reachable only through `fillHullEntry`-style far calls with the resident stack).

Why it matters: (1) the resident glue has only 3 B left before the fixed mission table (and 13 B before the flight tail), a new language needs its text tables (data) in banks 4-6 and a small copy or pointer switch in the resident part; (2) a mission overlay slot is 576 B with the largest at 561 (15 spare), so longer German or French mission texts need bigger slots (the slots can grow: bank 4 has 9.4 KB free, but the docked stub area in `LARGEAXX` `&17FD-&1A3F` is the real limit: it is 0 B spare); (3) the flip's per-frame copy costs time, not space.

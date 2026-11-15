# Memory map

Where everything sits in the running game, what swaps in and out, and which bytes are free. Addresses are for the stock English build (the German and French
trees shift the data between routines; see `_architecture.md`). What was traced is marked; the rest comes from reading the source.

## Overview (CPC 64 KB, RAM only)

| Range | Content |
|---|---|
| `&0000-&003F` | firmware vectors; the interrupt vector at `&0038` jumps to the game's ISR (`myVBL` is installed by `installVBL`, which patches `(&0039)`) |
| `&0040-&083F` | low RAM that Elite takes over (a copy of the firmware area with the floppy routines; CubeMDOS breaks on this). The BASIC loader sits at `&0170` and is destroyed once the game runs |
| `&0840-&1A3F` | `LARGEAXX` (`&1200` bytes) **while docked**: trading, planet text, save/load, string tables. Its last 812 bytes (`&1714-&1A3F`) are zero |
| `&1A40-&9FFF` | `COMMONXX`, the core (see below) |
| `&A000-&BFFF` | in flight: the off-screen bitmap. Docked: `&A000-&A5FF` is zero and `&A600-&BFFF` holds 6.5 KB of parked data (see "The bitmap and the swap") |
| `&C000-&FFFF` | screen RAM (Mode 1). `COMMON2X` is loaded at `&C000` and its routines hide in screen bytes that stay blank (see below) |

**Load sequence** (`_disks.md`): the loading picture goes to `&C000`, `largeaxx` to `&840`, `commonxx` to `&1A40`, `common2x` to `&C000` (over the picture), then `CALL &1C82`.
`MEMORY &83F` and `MEMORY &A000` in the loader protect the game area; the cheat loader's own program must fit `&170-&83E` (`_cheats.md`).

## COMMONXX (`&1A40-&9FFF`)

| Range | Content |
|---|---|
| `&1A40-&1B7A` | entity (ship) slots, a zero-filled workspace at load time (`&1A40-&1B01` slots; 6 entity slots, 3 reserved) |
| `&1B..` | `shipGFXdataTable`: 19 four-byte entries (`C3 lo hi n`, only the address word is read) |
| `&1C02-&1C39` | flight state (`posDataSun` `&1C26`, `posDataPlanet` `&1C2F`, laser temperature `&1C0F`) |
| `&1C82` | **entry point**; main loop near `&1CD9`; `&1DA8` frame counter (title screen: `splash2Shipnr`) |
| `&1FD2-&1FF0` | `unusedViewBorderFill`, 31 bytes with no references; holds `dustPlotPixel` (11 bytes) and `mxPodHook` (10) in `-DENHANCED`/`-DMISSIONS` builds. `ClearBitmap` follows at `&1FF1` |
| `&20C7-&20CA` | disc-circle parameters; `CircleEntrypoint2` `&20FB`, fills at `&243A` |
| `&2811` | ISR (`doColorSplit`; 300 Hz, counter 1-5 per frame) |
| `&2D6C-&2DC9` | sound tables |
| `&33E1-&34AD` | self-patched line-plotter operands; `tblDustCoordinates` `&34F4-&3544` |
| `&38C1-&3949` | variable block. `&38CB-&3932` is the 104-byte commander save (`_savegame.md`); `&39C7` the default commander; `&3934/&3935` chart cursor |
| `&3D22-&3D63` | galaxy workspace (`qq3`..`travelDistance`) |
| `&4600/&4700`, `&5600-&57FF` | quadratic square tables (maths). A stray `push` near `&57FE` corrupted them in Fessor's double-buffer attempt |
| `&5066` | `handleEntitys`, the safe stop point for tests |
| `&6000-&6FFF` | **music slot**: `MUSIQUEX.BIN` (the Blue Danube player, about 325 bytes plus score data) loads here over this slice while the music plays; `NOTMUSIC.BIN` is the slice's own bytes. Never lay both into one image |
| `&6BED-&6C2D` | dust tables; `&6E21-&6FFF` is the zero tail of `MUSIQUEX` (title-screen ship selection lives there with `-DTITLESEL`) |
| `&7CE5`, `&800D`, `&8025`, `&7EFC` | line-plotter patcher, the two self-patched plotters, pixel address calculation |
| `&8D2D-&8D8B` | `dataFromPPI` (ten keyboard rows) and `keybFlags*`; `getPPI_Input` `&8D8C`; key matrix `tblKeyboardMatrix2` `&8D37` |
| `&9D9E-&9FFF` | **zero tail, 610 bytes** (free at flight time; see below) |

Several of these regions are runtime buffers or contain self-patched operands: the full list is in `_architecture.md` ("Dynamic labels").

## COMMON2X in screen RAM (`&C000-&FFFF`)

The routines are placed among screen bytes that the display never changes (blank border and dashboard areas), so they cost no program memory. Known members:
the disc routine `todoDrawFilledCircle` `&E787` and `clearCircle` `&E795`, the private circle stack `CircleParm0x11Mask` `&F72E`, the self-patched `push af` run from `&CE50`,
and parts of the print routines (`Jumptokens`). The character set is also here. `drawDashboard` copies a stored dashboard image (from `&AE00`, by the code's comment)
into the lower screen rows. Most of the rest of the file is blank screen bytes (13% code).

## The bitmap and the swap

- **In flight** the view is drawn into a linear bitmap `&A000-&BFFF`: 128 lines of 64 bytes (256 pixels wide), wiped by `ClearBitmap` (`&1FF1`, 256 x 16 pushes of `&0F0F` with SP set to `&C000`) and
  copied to the screen by `transferBuffertoScreen` (`&1ED1`) each frame. The whole range is therefore working memory: nothing may be kept there while flying.
- **Docked** screens are drawn straight to screen RAM, so `&A600-&BFFF` is not needed as bitmap and holds 6.5 KB (`&1A00` bytes) of parked data, the firmware's upper RAM including the jumpblock `&BB00-&BDFF`: the same size as `&0040-&1A3F`, which it is swapped with.
- **Swapping** (`loadLARGEAXX`, `loadIndicator`, `switchMemoryContents`): at docking `loadLARGEAXX` copies `&0040-&1A3F` to `&A600` and loads `LARGEAXX.BIN` at `&0840`, so the docked tail is fresh at every docking. At launch
  `loadIndicator` loads the progress-bar screen and swaps `&0040-&1A3F` with `&A600-&BFFF`: the parked data returns to low memory and the docked copy (including `LARGEAXX`) goes to `&A600`, where the bitmap destroys it, which is why
  `LARGEAXX` is reloaded from disk at the next docking. At the title screen `LARGEAXX` is already parked, so code in the `&1714` tail (the mission stub) is valid only after `loadLARGEAXX`.
- **Measured in cpcxray (2026-11-09, Firebird disk, a snapshot per emulated second from `RUN"ELITE`):**
  - Until about 18 s, low memory holds `LARGEAXX` at `&0840` (4607 of 4608 bytes equal the file), `&0040-&083F` is 91% zero, and `&A600-&BFFF` holds 6.5 KB (about 56% zero) that is **not from any disk file**: no 16-byte window matches
    any extracted `.BIN`, and the content drifts slightly while loading (about 90% constant), so it is a RAM residue or runtime data, not code the game loads.
  - At about 19 s (start of the title screen) the first swap happens: low memory afterwards equals the old `&A600` content (6114 of 6656 bytes), `LARGEAXX` is gone from low memory and `&A600` is bitmap.
  - In flight (snapshot `firebird_in_flight.sna` against the boot snapshot): low memory equals the docked-layout `&A600` content (6003 of 6656 bytes) and the old low memory is not recoverable from `&A600`.
  - about 20 s of flight (two key presses, otherwise idle) changed **0 bytes** in `&0000-&1A3F`.
  - `commonxx.asm` has no direct operand into `&0040-&1A3F` (grep for address operands; its `0x0E01`-style hits are immediates), so flight code does not read it directly.
- **What the parked 6.5 KB is (settled in cpcxray, 2026-11-09):** the CPC firmware's own upper RAM. Its main jumpblock `&BB00-&BDFF` sits in it (768 bytes: entries such as `CF F2 8C` at `&BC32`, `SCR_SET_INK`, and `C3 40 1D` at `&BDF4`, `KM_SCAN_KEYS`
  patched to a `jp &1D40`), together with firmware data and zeros. The 768 bytes of the docked-layout snapshot equal the parked copy in low memory in flight (768 of 768). The game needs the firmware at docking, where it loads files
  (`CAS_IN_OPEN` `&BC77`, `KL_ADD_TICKER` `&BCE9`, `KM_SCAN_KEYS` `&BDF4` are called through that jumpblock), but in flight the bitmap `&A000-&BFFF` overwrites it. So the swap saves the firmware's upper RAM into low memory for flight and restores it
  at docking; the mission design is unaffected. (It also explains why the block matches no disk file.)

## Stack

The main stack is set at `&7497` (stored in `&1C7F`) at the entry point. Routines that use SP as a write pointer (`ClearBitmap`, the disc fill `ce2func43FillCompleteLinesinBM` `&243A`, the dust and circle `push` loops)
rely on the interrupt pushing its return address below the buffer: with SP at `&A000` an interrupt writes `&9FFE-&9FFF`. So **`&9FFE-&9FFF` is never free**, and the clamp at `&245B` keeps the disc fill from running further down
(`_architecture.md`, "The disc-drawing routine"). The ISR's worst-case depth is not measured.

## Free space

| Region | Bytes | Free when | Used by |
|---|---|---|---|
| `&9D9E-&9FFF` (end of `COMMONXX`) | 610, of which `&9FFE-&9FFF` stack | flight time (cannot hold docked-only code: it is resident always) | mission vector table (`&9D9E`), launch hook and one flight image, up to `&9FFE` (an `ASSERT` checks it) |
| `&1714-&1A3F` (end of `LARGEAXX`) | 812 | docked only (fresh at each docking) | mission stub (251), the sell-all key (48) plus one overlay loaded at `mxOverlayBase` `&1775`; 0 spare with the Constrictor overlay |
| `&1FD2-&1FF0` (`unusedViewBorderFill`) | 31 | always | `dustPlotPixel` and `mxPodHook`; 10 bytes left |
| `&204E`, `&2053` (`unusedGetFlightMode`, `unusedGetCloakFlag`) | 10 | always (never referenced or executed) | `killSpace` of the kill count with `-DENHANCED` (English); nothing in the stock build |
| `&6E21-&6FFF` (tail of `MUSIQUEX`) | about 480 | while the title screens run (the file is resident only then) | title ship selection, about 120 bytes |
| `&9751-&97A0` | 80 | filler, not verified as free for new code | nothing |
| German build tail | 282 | flight time | (no missions in the German build) |

No other dead code exists: the supposed chains in `db` runs are live (tails of `push ix` routines), see `_architecture.md`. Re-encoding the string tables saves only 48 bytes. Memory is otherwise full and no address
may move, because saves are XORed with the code at `EquipShip`.

## Where the mission code goes

| What | Where | When loaded |
|---|---|---|
| docked stub (251 bytes) and the call from the docking sequence | `&1714` | with `LARGEAXX`, every docking |
| docked overlay `MISSIONC/P/T/R.BIN` | `&1775` (`mxOverlayBase`) | on demand, only where something can happen (about 2 s of disk time) |
| vector table (nine 3-byte `jp`s), id byte `mxFlightId` `&9DB9`, launch hook `mxLaunchEntry`, flight image `MFLIGHT0/C/P/T/S/R.BIN` or a ship pack `MFLIGHT1-7.BIN` (`_ship_packs.md`) | `&9D9E-&9FFE` | image chosen at every launch, loaded only if it differs from the one in RAM |
| mission state bytes | `&38FD` (state), `&38FE` (counter), `&3905-&3906` (Trumbles) | in the save |

Details, sizes and tests: `_missions_built.md`.

## Gate Array and banking (128K)

- The CRTC/Gate Array fetch video only from the base 64K (banks 0-3). The RAM banking register (`&7Fxx`, `11xxxyyy`) changes what the CPU sees, never what is displayed, so the extra banks 4-7 cannot be shown.
  Source: [CPCWiki Gate Array](https://www.cpcwiki.eu/index.php/Gate_Array) ("The Video RAM is always located in the first 64K").
- Configs used by the double-buffer experiment: C0 = banks 0,1,2,3; C1 = 0,1,2,7; C3 = 0,3,2,7. C1/C3 show bank 7 at `&C000`, so code kept there stays visible while the CPU draws at `&4000` (bank 1 or 3);
  R12 `&1C` displays `&4000` (bank 1), `&3C` displays `&C000` (bank 3). C0 hides bank 7: code running there must be elsewhere, and interrupts are off.
- The port is write-only: keep the current config in a variable (`dbCfg`, `dbBank`). Needs 128K; a 464 needs a fallback.
- The CPCWiki pages return 403 to `curl` and WebFetch; read them with Claude in Chrome (`get_page_text`).

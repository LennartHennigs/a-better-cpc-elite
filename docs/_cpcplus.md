# CPC+ (Plus) compatibility and the other byte patches

Elite (UK "Version GOLD") takes no keyboard input on a real CPC464+/6128+. Redbox published a patch (CPC Power #9, UK and German).
Our sources carry the fix; this file records what is known and what is not.

## Source and symptom

CPCWiki forum, "Any way to get Elite working on a Plus?" (Badstarr, 2011-09-19; user-saved HTML copy, not in the repo). Attachments:
`Elite (UK) (1986) (Version GOLD) Patched Keyboard for Plus.dsk` and `Elite (G) ... Gepatcht Tastatur fur Plus.dsk` (190.25 KB each).

- The game loads and the music plays, but the keyboard is dead on a real Plus. On the commander screen `Y`/`N` may need several
  presses (also on a classic CPC, because the title graphics slow the scan; Redbox says that is no keyboard fault).
- Amstrad Action issue 100 (cover tape) had the same complaint from Plus owners; that was a separate disc-ROM init issue in the loader.

## Cause (per Redbox, Executioner, MaV)

- The scan is `getPPI_Input` in `src/elite/commonxx.asm` (runtime `&8D8C`, writes the ten matrix rows to `dataFromPPI` at `&8D2D`).
  The forum listing is byte-for-byte our routine.
- It touches PPI and PSG ports in an order the Plus ASIC does not tolerate ("a critical mistake in the port order"). No ROM is
  involved, so a changed Plus ROM would not help.
- The routine selects PSG register 14 (`&F40E`), reads port C (`&F6xx`) keeping bits 4-5, strobes the PSG select, sets the PPI to
  port A input (`&92`), reads ten lines and restores the PPI (`&82`). Which step the ASIC objects to is **not established by us**.
- WinAPE emulates the bug, but its Plus PPI emulation is off by default even in Plus profiles; turn it on to reproduce.

## The fix: one byte

Diff of Redbox's UK disk (`work/plus_patch/uk_plus.dsk`, SHA-256 `09f7e527760b1232400dd70d8302b1753a4259260def9f82c022c165e24741b5`,
extracted to `work/plus_patch/x/`) against stock, 2026-11-07:

- `COMMONXX.BIN` differs from `work/bin_stock/COMMONXX.BIN` only at file offset `&7360` (runtime `&8DA0`); every other file is
  byte-identical, `ELITE.BAS` is the Firebird loader. The routine keeps its length (59 bytes), so nothing moves. (The forum
  described "Arnoldemu's routine"; what shipped is this single in-place change.)
- In `getPPI_Input` the second `out (c),a` (`ED 79`) becomes `out (c),c` (`ED 49`):

  ```
  and 0x30 / ld c,a / or 0xC0 / out (c),a   ; port C: PSG register-select state (BDIR=BC1=1)
  out (c),a                                 ; stock: same value again (redundant); patched: out (c),c
  inc b / ld a,0x92 / out (c),a             ; PPI control: port A becomes input
  ```

  Patched, the second write puts `C` (the kept bits without `&C0`, PSG *inactive*) on port C, releasing the PSG before port A becomes
  input. That matches the "port order" remark and the usual firmware sequence (select, inactive, change direction), and is a no-op
  on a classic CPC. **Why the ASIC objects remains inference.**
- `Elite_DE_cracked.dsk` already has the same change (`ED 49`, `getPPI_Input` near `&8EE7`, `src/elite_de/commonxx.asm`), so it is the
  patched German version or a copy of its files; no unpatched German build is available to confirm that the original had the bug.
  The French build has no fix. The German patch disk uses German game files with the English `ELITE.BAS` (the German disc had file protection).
- Check any new localized build with `getPPI_Input` (`out (c),c` = fixed).

## Status in our tree

- `src/elite/`, `src/elite_de/`, `src/elite_fr/` carry the fix; the assembled `COMMONXX` differs from stock in exactly that byte and
  equals `work/plus_patch/x/COMMONXX.BIN`. `tools/check_src.sh` expects it; the `TRAINER.ASC` pokes are unaffected.
- `work/elite_plus.dsk` is the Firebird disk with that byte (AMSDOS headers untouched).
- Caprice32 4.6.0 (built from source by a script that was removed 2026-11-16; `./cap32 -O system.model=3 DISK.dsk`, `model=2` is the classic 6128): at the Plus startup
  menu press CPC f1 through the on-screen keyboard (Shift+F1; host F1 opens the emulator menu), then `run"elite`. The **unpatched**
  disk already works there, so Caprice32 does not reproduce the bug and cannot confirm the fix; the patched disk works on both models.
- **Untested** on real hardware or an ASIC-accurate emulator (WinAPE with Plus PPI emulation on). The fix rests on Redbox's disk and
  his real-6128+ test; ours is byte-identical.
- The other PSG writers (`ppiRegAValC` in `COMMONXX`, `SUB_ram_6139` in `MUSIQUEX`) use the firmware order: latch the register on port A, set select (`or &C0`), then inactive (`and &3F`), write the data, strobe write. They never switch the PPI direction, so they do not have the stock scan's pattern (checked in the source).

## The ESC byte (the other change to stock bytes)

`src/elite`, `src/elite_de` and `src/elite_fr` can carry one more change: the key code of ESC in `tblKeyboardmatrix` (row 8 bit 2) is
`ESC_KEYCODE` = `&7F` instead of `&FF` ("no key"), so the buy, sell and equipment prompts leave on Escape (`getInputForFunctionHL` leaves
on any code of `&3A` or more). Runtime address: English `&8C98`, German `&8DE0`, French `&8E37`. It reaches every consumer of
`pressedKey`: `InputString` (names, planet search) ignores codes above `&5A`, pause mode compares specific letters, and on the title
screen ESC counts as "any key" (starts a new commander; the "press space" loop still needs space).

Since 2026-11-09 it is off in a plain build (`ESC_KEYCODE` = `0xFF`, original bytes) and on with `-DENHANCED` or `-DESC_KEYCODE=0x7F`;
`tools/check_src.sh` verifies both for every build.

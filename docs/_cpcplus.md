# CPC+ (Plus) compatibility

Elite (UK "Version GOLD") does not take keyboard input on a real CPC464+/6128+. A patch by Redbox exists (CPC Power #9, UK and
German). This file records what is known, what is not, and our plan. The UK patch disk is in `work/plus_patch/` (diffed 2026-11-07, see "Diff result"); the German one is not.

## Source

CPCWiki forum, topic "Any way to get Elite working on a Plus?" (Badstarr, 2011-09-19; local copy saved as HTML by the user on
2026-11-07, not stored in the repo). Read-only archive; the attachments were `Elite (UK) (1986) (Version GOLD) Patched Keyboard
for Plus.dsk` (190.25 KB) and `Elite (G) (1986) (Version GOLD) Gepatcht Tastatur fur Plus.dsk` (190.25 KB).

## Symptom

- Game loads and the music plays, but the keyboard is dead on a real Plus. On the commander screen `Y`/`N` may need several presses
  (also on a classic CPC, because the title graphics slow the scan down; Redbox says that is not a keyboard fault).
- Amstrad Action issue 100 (cover tape) had the same complaint from Plus owners; that was a separate disc-ROM init issue in the loader.

## Cause (per Redbox, Executioner, MaV)

- The keyboard scan is `getPPI_Input` in `src/elite/commonxx.asm` (runtime address `&8D8C`, writes the ten matrix rows to `&8D2D`,
  `dataFromPPI` in our source). The forum listing is byte-for-byte the routine we have.
- It touches the PPI and the PSG ports in an order the Plus ASIC does not tolerate. Redbox: "they made a critical mistake in the
  port order", the rest of the routine is well written. MaV: no ROM is involved, so the fault is in the ASIC, and a changed Plus ROM
  would not help.
- The routine starts by selecting PSG register 14 (`&F40E`), reads port C (`&F6xx`) to keep bits 4-5, strobes the PSG select, then
  sets the PPI to port A input (`&92`), reads ten lines, and restores the PPI (`&82`). Which of these steps the ASIC objects to has
  **not been established by us**; the forum only says "order".
- WinAPE emulates the bug, but its Plus PPI emulation is off by default even in the Plus profiles (Executioner), so a Plus profile
  alone shows nothing. Turn Plus PPI emulation on to reproduce. cpcxray has not been checked.

## The fix

- Redbox replaced the routine with Arnoldemu's Plus-compatible keyboard scan (reads the ports directly, same order the firmware
  uses) and tested it on a real 6128 Plus.
- **The German disk here already has the fix.** `getPPI_Input` in `Elite_DE_cracked.dsk` (`&8EE7` area, `src/elite_de/commonxx.asm`) has the same one-byte change (`ED 49` for the second port write), so that disk is the patched German version (or a copy of its game files), and the German item of the plan is done by finding it. We do not have an unpatched German build to confirm that the German original had the bug too.
- The German build keeps the routine at a different address, because its code is relocated. The German disc has file protection
  (files in USER 1, writes failed), so the German patch disk uses the German game files with the English `ELITE.BAS` loader.
- CPC Power #9 combines both and adds an English/German menu (see `docs/_disks.md`).

## Diff result (UK patch disk, 2026-11-07)

Disk: `work/plus_patch/uk_plus.dsk` (copy of the user's download of the forum attachment `Elite (UK) (1986) (Version GOLD) Patched Keyboard for
Plus.dsk`), SHA-256 `09f7e527760b1232400dd70d8302b1753a4259260def9f82c022c165e24741b5`. Files extracted with `tools/dskx.py` into
`work/plus_patch/x/`; 9 files, all user 0, same AMSDOS headers as stock.

- **The whole patch is one byte.** `COMMONXX.BIN` differs from `work/bin_stock/COMMONXX.BIN` at file offset `&7360` only (runtime `&8DA0`);
  `COMMON2X`, `INDICATO`, `LARGEAXX`, `MUSIQUEX`, `NOTMUSIC` and `PICTURE` are byte-identical to stock. `ELITE.BAS` is the Firebird disk's
  unprotected loader and `CHEAT.BAS` is also present (so the disk is the cracked UK game plus this one byte). Differences in the `.raw`
  dumps beyond the declared length are sector padding.
- **The byte:** in `getPPI_Input` the second `out (c),a` (`ED 79`) becomes `out (c),c` (`ED 49`). Stock:

  ```
  and 0x30 / ld c,a / or 0xC0 / out (c),a   ; port C: PSG register-select state (BDIR=BC1=1)
  out (c),a                                 ; stock: the same value written again (redundant)
  inc b / ld a,0x92 / out (c),a             ; PPI control: port A becomes input
  ```

  Patched: the second write puts `C` (the kept port-C bits without `&C0`, i.e. PSG *inactive*) on port C, so the PSG is released before the
  PPI's port A is switched to input. Stock never released it. This matches Redbox's "port order" remark and the usual firmware sequence
  (select, inactive, then change direction), and it is a plain no-op for a classic CPC. **The mechanism (why the Plus ASIC objects) is still
  inference, not tested.**
- **So the forum's "Arnoldemu's routine" was not what ended up on the disk:** the shipped fix keeps the original routine and its length (59
  bytes, no byte shifts anywhere) and changes one instruction in place.
- Not checked: the German disk (routine at a different address), and whether the one-byte fix passes a Plus-PPI-emulating emulator.

## Test result (2026-11-07)

- Our `src/elite/` now carries the fix (`getPPI_Input`, `&8DA0` `ED 79` -> `ED 49`). The assembled `COMMONXX` differs from stock in exactly that byte and is identical to `work/plus_patch/x/COMMONXX.BIN`; the file length is unchanged, so nothing moves and the `CHEAT.ASC` pokes are unaffected. `tools/check_src.sh` expects the patched byte.
- `work/elite_plus.dsk` is the Firebird disk with that one byte patched (AMSDOS headers untouched).
- Tested in Caprice32 v4.6.0 (built by `scripts/install-caprice32.sh`, run as `./cap32 -O system.model=3 DISK.dsk`; `model=2` is the classic 6128, `model=3` the 6128+). At the Plus startup menu press the CPC f1 (BASIC) through the on-screen keyboard (Shift+F1 in the emulator); host F1 opens the emulator's own menu. Then `run"elite`.
  - Unpatched Firebird disk on the 6128+: the game ran and the keys worked, so **Caprice32 does not reproduce the Plus keyboard bug**. It cannot confirm the fix.
  - Patched disk (`work/elite_plus.dsk`): works, on the 6128+ and the classic 6128 (regression check passed).
- Still untested on real Plus hardware or in an emulator that models the ASIC port order (WinAPE with Plus PPI emulation on). The fix rests on Redbox's disk and his test on a real 6128+; ours is byte-identical to it.

## Plan

1. **Get the disk.** (Done for UK; the forum links are dead, the user supplied the file.) Download Redbox's patch disk (forum attachment or CPC Power #9; the CPC Power link was a `#` placeholder). Ask
   before downloading. Keep it in `work/`, never re-upload.
2. **Diff against our stock build.** (Done: one byte, see above.) Extract with `tools/dskx.py`, compare `COMMONXX` with `work/bin_stock/` byte by byte. Expect
   the change in `getPPI_Input` only; note any size change, moved bytes, and whether the routine still fits in place.
3. **Reproduce.** WinAPE with Plus PPI emulation on, or cpcxray if it models the ASIC ordering. Real hardware is the final test and
   the user has none to hand, so a test is what we can do in an emulator that has the bug. Record how to enable it in `docs/_cheats.md`
   or here.
4. **Apply the fix in `src/elite/`.** Simplest: change the second `out (c),a` of `getPPI_Input` (`commonxx.asm`, after `or 0xC0`) to `out (c),c` and compare with the patch disk's `COMMONXX.BIN` (must differ from stock in exactly that byte). The original text of this step: Replace the body of `getPPI_Input` with the Plus-safe order (informed by step 2, not copied
   blind). It must keep the same output layout (ten bytes in `dataFromPPI`), the same register use for the caller, and ideally the
   same length so no addresses shift. If it is longer, check for free bytes first (the 812 zero bytes at the end of `LARGEAXX` are
   not in this module). Assemble with sjasmplus and compare with `work/bin_stock/*.BIN`: the only differing bytes must be the routine.
5. **Check it still works on a classic CPC** (cpcxray / WinAPE with Plus PPI emulation off): keys, joystick lines and the
   caps-lock/shift handling in `tblKeyboardMatrix2`.
6. **Do the same for the German build** after the German disassembly exists (routine is relocated there).
7. **Package.** Write the patched `COMMONXX` into a copy of the Firebird DSK (keep the AMSDOS header) as `work/elite_plus.dsk`.
   Optional: make the patch a switchable option so that one build runs on both machines.
8. **Document** the confirmed cause in this file and turn the "per Redbox" statements into verified ones.

Open question: do any other routines touch the PSG or PPI with the same ordering (music player `MUSIQUEX`, joystick reads)? Grep
for `0xF4`/`0xF6` port writes in `src/elite/` while doing step 4.

## Other one-byte patches in the sources

Besides the CPC+ fix, `src/elite`, `src/elite_de` and `src/elite_fr` carry **one more change to the stock bytes**: the key code of ESC in the ASCII keyboard table (`tblKeyboardmatrix`, row 8 bit 2) is `ESC_KEYCODE` = `&7F` instead of `&FF` ("no key"),
so the buy, sell and equipment prompts leave on Escape (`getInputForFunctionHL` leaves on any code of `&3A` or more). Runtime address of the byte: English `&8C98`, German `&8DE0`, French `&8E37`; `tools/check_src.sh` expects it, as it expects the CPC+ byte.
It is unconditional, so it also reaches every other consumer of `pressedKey`: `InputString` (names, planet search) ignores codes above `&5A`, the pause mode compares against specific letters, and on the title screen ESC now counts as "any key" (it starts a new commander like any key other than the load key;
the "press space" loop still needs space). `ESC_KEYCODE` can be overridden at assembly time: `-DESC_KEYCODE=0xFF` gives the original bytes, which `tools/check_src.sh` verifies for every build.


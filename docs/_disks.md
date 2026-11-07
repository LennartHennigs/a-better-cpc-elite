## Disks in the project root (checked 2026-11-07)

### Disks in this folder (checked 2026-11-07)

| File | Creator, tracks | What it is |
|---|---|---|
| `Elite_UK_original_protected.dsk` | CPCRULEZ, 41 | UK original ("Version GOLD"), hidden catalogue. Matches CPC Power #1 (SAMdisk, 41 tracks, "catalogue altered to hide the file list"). Our `Elite_UK_original_protected.dsk` hash: `e50a6627...1b76`. |
| ~~`Elite - Gold.dsk`~~ (deleted 2026-11-07) | CPCRULEZ, 41 | Same as `Elite_UK_original_protected.dsk` plus a stray `TES.BIN`: not a copy of `1.BIN` but a second fresh-commander save named "TES" (decrypts identically except the name bytes and the two checksums; it passes both checksums with the stock key). Nothing uses it. |
| `Elite_UK_Firebird_cracked_trainer.dsk` | WinAPE 32 1.0, 40 | Unprotected UK re-save, plus `CHEAT.BAS`. Probably CPC Power #8. |
| `Elite_DE_cracked.dsk` | WinAPE 2.0A18, 40 | **German** build (confirmed by user). Likely a cleaned copy of CPC Power #3 or #6 (both 42 tracks, so not an exact dump). |
| `Elite (1985)(Firebird Software)(fr).dsk` | French build | **French** Firebird release: `E.BAS`/`EL.BAS`/`SPEED.BAS` loaders, `.BAK` copies, `PICTURE1.SCR`. SHA-256 `86783b29...4585`. Disassembled in `src/elite_fr/` (byte-exact). No CPC+ fix. |
| `Elite (1985)(Firebird Software)(fr)[a].dsk` | French, compacted | Same payloads, files renamed `ELITE.`, `ELITE.1`-`.7` ("COMPACTE PAR CHANY"); only the file-name strings inside the code differ. SHA-256 `0652569e...931e`. |
| `Elite_DE_savegames.dsk` | RVM v2, 43 | Four commander saves (`PETER`, `PETE`, `LEN`, `LEN.BAK`), 104 bytes each at `&39D2`. |

The disk-to-CPC-Power mapping is inferred from track count, creator tool and the page's description. It is not
a hash match (CPC Power only gives CRCs of its zip archives).

- Payloads of `Elite_UK_original_protected.dsk` and the Firebird disk are byte-identical for `COMMONXX`, `COMMON2X`, `INDICATO`,
  `MUSIQUEX`, `NOTMUSIC` and `PICTURE`. `LARGEAXX.BIN` differs in one byte: `&0998` is `&00` on the Firebird
  disk and `&19` on `Elite_UK_original_protected.dsk` (purpose unknown).
- `Elite_UK_original_protected.dsk` (Gold) is the original; the Firebird disk differs from it by one byte, `&0998` in `LARGEAXX`: `jr c,errorforNotEnoughCapacity`
  (`38 19`) became `38 00`, removing the hold-capacity test when buying goods (a trainer patch). Now in `src/elite/`.
- `Elite_UK_original_protected.dsk` adds only the wrapper: every file has the System attribute (hidden from `CAT`), decoy directory
  entries (`0K free.` and `"`), a type-1 (protected) `ELITE.BAS` of 304 bytes, and `1.BIN`.
- `1.BIN` is 104 bytes at `&38CB`, the same size as a save file. It is a save named `1` (a fresh commander), encrypted with the stock key; see `_savegame.md`.
- Tracks 1 and 40 of the 41-track disks use sector IDs `F7–FF` and hold only `0xE5` filler.
- German `[G]`: `COMMONXX`, `LARGEAXX` and `NOTMUSIC` differ from the English files in nearly every byte, which
  is not relocated code but the same program with German text: the data between the routines moves, so address operands shift (about a page, e.g. `&65xx` vs `&66xx`), plus German
  text. `COMMON2X` differs in about 270 bytes; `PICTURE`, `INDICATO`, `MUSIQUEX` are identical. Its header
  load addresses are all `0`. Its `ELITE.BAS` is identical to the Firebird disk's. **It already contains the CPC+ keyboard fix** (see `_cpcplus.md`): with the English unprotected loader, that matches Redbox's "Gepatcht Tastatur fur Plus" disk, so `Elite_DE_cracked.dsk` is probably that patched German disk (or a copy of the same game files); the unpatched German game is not on disk here. Disassembled in `src/elite_de/`.

## Loader sequence (plain `ELITE.BAS`, Firebird and `[G]`)

1. Set mode and inks, `LOAD "!picture",&C000` (loading picture).
2. `MEMORY &83F`, then `LOAD "largeaxx",&840`.
3. `LOAD "commonxx",&1A40`.
4. `MEMORY &A000`, then `LOAD "common2x",&C000`.
5. `CALL &1C82` (entry point, inside `COMMONXX`).

## Other releases (CPC Power)

### CPC Power (https://www.cpc-power.com/index.php?page=detail&onglet=dumps&num=801)

All entries are "Version GOLD", publisher Firebird, loaded with `RUN"ELITE.BAS` (tape: `|TAPE`, `RUN""`).
- #1 UK original `.dsk` (hidden catalogue, 41 tracks, SAMdisk, 2025-04-19); #8 UK `.dsk` (WinAPE, 40 tracks).
- #2 FR `[Bugs]` (flagged for removal, contains a stray Ping Pong program); #7 FR `.dsk`.
- #3 DE original (hidden catalogue, 42 tracks, "many backups", flagged for removal); #6 DE trainer
  (`RUN"CHEAT.BAS`, 42 tracks).
- #9 UK/DE **CPC+ patch** by Redbox: fixes a keyboard-scanning bug on the CPC+ and adds an English/German menu.
  The page's download link is `#` (a placeholder). The UK disk came from the forum attachment instead (now a dead link; copy in `work/plus_patch/uk_plus.dsk`): the patch is a single byte in `COMMONXX`, see `docs/_cpcplus.md`.
- #4 UK tape "v3-86" (Bleepload1 protection, turbo blocks), #5 DE tape (no music). The tape may be an earlier
  code base.
- Separate: *Commander Fuer Elite* (G), a type-in trainer from Schneider CPC International Sonderheft 3-86 (now in `magazines/elite-commander.pdf`, analysed in `docs/_savegame.md`): a commander creator that writes the same 104-byte block; its offsets match ours, its key does not.

## Stock disk wrapper (`Elite_UK_original_protected.dsk`): the protection is ARMOURLOC v1.1

Worked out on 2026-11-07 by letting cpcxray (headless, via its MCP server) boot the disk and dumping memory
at chosen moments. Dumps are in `work/prot/`; `tools/bastok.py` is a CPC BASIC detokenizer.

- Directory entry 0 has a NUL-led name `"\0 0K free"` and claims blocks 2-8 (7 KB); they hold only `0xE5`.
  This is what makes `CAT` show "0K free" and nothing else. Every real file has the System attribute.
- Stock `ELITE.BAS` is type 1 (protected); the BASIC ROM decrypts it while loading. Why `LOAD"ELITE.BAS`
  leaves nothing in memory but `RUN"ELITE.BAS` works (checked in cpcxray, ROM code read at `&C040-&C160`):
  1. `LOAD` reads the whole file (`CAS_IN_DIRECT` to `&170`, closed at `&2A0`) and sets a "protected
     program" flag, byte `&AE2C` = `&FF` (it stays `&00` for the plain Firebird file).
  2. Every time BASIC returns to the command prompt, its top-level loop (`&C06A: LD A,(&AE2C); OR A;
     CALL NZ,&C145`) sees the flag, zero-fills the program area (`&C145`, the `LDIR` at `&C154`) and clears
     the flag. `LOAD` returns to the prompt at once, so the program is wiped.
  3. `RUN` never returns to the prompt: line 0 does `CALL &BE80` and the game takes over the machine.
  `LIST` also prints nothing for a protected program, a separate check.
  **To read a protected BASIC program:** after `LOAD`, stop at `&C06A` (a PC breakpoint) and write `&00` to
  `&AE2C`; the program then survives (`FRE(0)` drops by 302). Dump `&170` onward and run `tools/bastok.py`.
  Result is in `work/prot/ELITE.BAS.plain` and `ELITE.BAS.txt`.
- The program is 3 real lines plus a long line 0. Line 0 is 328 bytes: `MODE 1:INK 0,0:INK 1,24:INK 2,15:INK 3,6:BORDER 0:LOAD"picture",&C000:LOAD CHR$(34):CALL &BE80:CALL 0`,
  then embedded NUL bytes around a `RUN` token and a `REM` box reading "This disc is protected by ****
  ARMOURLOC v1.1 **** Copyright S.Thomas 1985" (box-drawing characters; the text is at `&01BE`). The NULs
  make `LIST` stop printing. After it come `10 MEMORY &1FFF`, `20 LOAD"!"` and `30 CALL 32313` (`&7E39`).
  Those lines are not what runs: the trace of `RUN` shows the third file opened is `largeaxx`, loaded at
  `&840`, and so on. How the stub redirects the flow is not traced.
- `LOAD CHR$(34)` loads the hidden file named `"` (`&BE80`, `&A1` bytes). `CALL &BE80` runs it:
  1. `CALL &BD19` (wait for flyback), `DI`, pop the return address into HL.
  2. `HL = return address - (word at &0172) - &BE64`; `R = H or L`. So the key depends on where it was
     called from and on the first bytes of the BASIC program text. Change either and the decrypt is wrong.
  3. Loop over `&BEB0-&BEFF`: `byte = R xor byte xor (stub byte at the same offset from &BE80)`. `R` is
     the Z80 refresh counter, so the key stream is the instruction count: a trace, single step or any
     extra instruction in the loop breaks it. Reproducing it needs the exact cycle sequence, which the
     emulator gives (the decrypted bytes are in `work/prot/BE00_after_decrypt.bin`).
  4. The decrypted code at `&BEB0` sets `&BE78` to `&FF`, copies `&30` bytes from `&BEDC` to `&0300`, and
     far-calls ROM 7 (AMSDOS) at `&C666` with `DE=&2800`, then copies `&6D` bytes to `&DF00` and loops back
     to `&BE80`. The code at `&BEDC` is a failure path: set mode 1, print the message at `&01BE`, beep
     forever. I did not trace what the AMSDOS call does, so what loads the game from here is still unread.
- `1.BIN` (104 bytes, load `&38CB`, exec `&FFBB`) is not part of the loader: it is a commander save named `1`
  (see `_savegame.md`).
- None of this matters for the disassembly: the Firebird disk carries the same game binaries without the
  wrapper. It matters only if we want to make the original `Elite_UK_original_protected.dsk` boot after changing code (then use
  the Firebird disk's `ELITE.BAS` instead).

### Renamed 2026-11-07

| Old name | New name | Why |
|---|---|---|
| `ELITE.DSK` | `Elite_UK_original_protected.dsk` | UK original, ARMOURLOC protected |
| `Elite_1985_Firebird_Software.dsk` | `Elite_UK_Firebird_cracked_trainer.dsk` | unprotected re-save with the `&0998` trainer patch |
| `Elite - Gold [G].dsk` | `Elite_DE_cracked.dsk` | German build, plain BASIC loader |
| `Elite Savegame.dsk` | `Elite_DE_savegames.dsk` | four saves, German-build key |
| `IMG_9858.JPG` | `Elite_DE_controls_card.jpg` | photo of the German controls card ("Uebersicht der Kontrollen") |

The old names still appear in `work/` file names and in older git-less history; the tools take paths, so nothing breaks.

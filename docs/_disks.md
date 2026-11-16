# Disks (checked 2026-11-07)

The disk-to-CPC-Power mapping is inferred from track count, creator tool and the page's description; CPC Power gives only CRCs of
its zip archives, so it is not a hash match.

| File | Creator, tracks | What it is |
|---|---|---|
| `Elite_UK_original_protected.dsk` | CPCRULEZ, 41 | UK original ("Version GOLD"), hidden catalogue, probably CPC Power #1 (SAMdisk, "catalogue altered to hide the file list"). SHA-256 `e50a6627d98da88f74d3207fc953c3c4d9960b1f190aedc0a5c695d3e9de1b76` |
| `Elite_UK_Firebird_cracked_trainer.dsk` | WinAPE 32 1.0, 40 | Unprotected UK re-save plus `CHEAT.BAS`. Probably CPC Power #8 |
| `Elite_DE_cracked.dsk` | WinAPE 2.0A18, 40 | German build, likely a cleaned copy of CPC Power #3 or #6 (both 42 tracks, so not an exact dump). Already has the CPC+ keyboard fix (see below) |
| `Elite (1985)(Firebird Software)(fr).dsk` | | French Firebird release: `E.BAS`/`EL.BAS`/`SPEED.BAS` loaders, `.BAK` copies, `PICTURE1.SCR`. SHA-256 `86783b29...4585`. No CPC+ fix. Source in `src/elite_fr/` |
| `Elite (1985)(Firebird Software)(fr)[a].dsk` | | Same payloads, files renamed `ELITE.`, `ELITE.1`-`.7` ("COMPACTE PAR CHANY"); only the file-name strings inside the code differ. SHA-256 `0652569e...931e` |
| `Elite_DE_savegames.dsk` | RVM v2, 43 | Four saves (`PETER`, `PETE`, `LEN`, `LEN.BAK`), 104 bytes each at `&39D2` (German key) |

Never modify these in place; work on copies in `work/`. `Elite - Gold.dsk` (the protected disk plus a stray second save `TES.BIN`) was deleted.

## Relations between the builds

- The UK original and the Firebird disk have byte-identical `COMMONXX`, `COMMON2X`, `INDICATO`, `MUSIQUEX`, `NOTMUSIC` and
  `PICTURE`. `LARGEAXX` differs in one byte, `&0998`: `jr c,errorforNotEnoughCapacity` (`38 19`) became `38 00` on the Firebird
  disk, removing the hold-capacity test when buying (a trainer patch; now handled in `src/elite/`).
- The UK original adds only a wrapper: every file has the System attribute (hidden from `CAT`), decoy directory entries
  (`0K free.` and `"`), a type-1 (protected) 304-byte `ELITE.BAS`, and `1.BIN` (a fresh commander named `1`, 104 bytes at
  `&38CB`, exec `&FFBB`, encrypted with the stock key; see `_savegame.md`; not part of the loader).
- Tracks 1 and 40 of the 41-track disks use sector IDs `F7-FF` and hold only `0xE5` filler.
- German: `COMMONXX`, `LARGEAXX` and `NOTMUSIC` differ from English in nearly every byte, but it is the same program with German
  text: data between routines moves, so address operands shift by about a page. `COMMON2X` differs in about 270 bytes;
  `PICTURE`, `INDICATO`, `MUSIQUEX` are identical; header load addresses are all `0`; `ELITE.BAS` equals the Firebird one. It
  already contains the CPC+ keyboard fix (`_cpcplus.md`): with the English unprotected loader it matches Redbox's "Gepatcht Tastatur
  fur Plus" disk, so the unpatched German game is not here. Source in `src/elite_de/`.

## Loader sequence (plain `ELITE.BAS`, Firebird and German)

1. Set mode and inks, `LOAD "!picture",&C000`.
2. `MEMORY &83F`, `LOAD "largeaxx",&840`.
3. `LOAD "commonxx",&1A40`.
4. `MEMORY &A000`, `LOAD "common2x",&C000`.
5. `CALL &1C82` (entry point, inside `COMMONXX`).

## Other releases (CPC Power, https://www.cpc-power.com/index.php?page=detail&onglet=dumps&num=801)

All are "Version GOLD" by Firebird, started with `RUN"ELITE.BAS` (tape: `|TAPE`, `RUN""`).

- #1 UK original (hidden catalogue, 41 tracks, 2025-04-19); #8 UK (WinAPE, 40 tracks).
- #2 FR `[Bugs]` (flagged for removal, stray Ping Pong program); #7 FR.
- #3 DE original (hidden catalogue, 42 tracks, "many backups", flagged for removal); #6 DE trainer (`RUN"CHEAT.BAS`, 42 tracks).
- #9 UK/DE **CPC+ patch** by Redbox: fixes a CPC+ keyboard-scanning bug and adds an English/German menu. The page's download link
  is a placeholder; the UK disk came from the forum attachment (dead link; copy in `work/plus_patch/uk_plus.dsk`). The patch is
  one byte in `COMMONXX` (`_cpcplus.md`).
- #4 UK tape "v3-86" (Bleepload1 protection, turbo blocks), #5 DE tape (no music); the tape may be an earlier code base.
- *Commander Fuer Elite* (G): the Sonderheft 3-86 type-in trainer, analysed in `_savegame.md`.

## The protection on the UK original: ARMOURLOC v1.1

Worked out on 2026-11-07 by booting the disk in cpcxray (headless, MCP) and dumping memory at chosen moments (dumps in
`work/prot/`; `tools/bastok.py` detokenizes CPC BASIC). It does not matter for the disassembly, since the Firebird disk carries
the same binaries; it matters only to make the original boot after changing code (then use the Firebird disk's `ELITE.BAS`).

- Directory entry 0 has a NUL-led name `"\0 0K free"` and claims blocks 2-8 (7 KB, all `0xE5`), which makes `CAT` show "0K free".
- Stock `ELITE.BAS` is type 1 (protected); the BASIC ROM decrypts it while loading. Why `LOAD"ELITE.BAS` leaves nothing but
  `RUN"ELITE.BAS` works (ROM code at `&C040-&C160`):
  1. `LOAD` reads the file (`CAS_IN_DIRECT` to `&170`, closed at `&2A0`) and sets the "protected program" flag, byte `&AE2C` = `&FF`
     (`&00` for the plain Firebird file).
  2. Whenever BASIC returns to the command prompt, its top-level loop (`&C06A: LD A,(&AE2C); OR A; CALL NZ,&C145`) sees the flag,
     zero-fills the program area (`LDIR` at `&C154`) and clears the flag. `LOAD` returns to the prompt at once, so the program is wiped.
  3. `RUN` never returns to the prompt: line 0 does `CALL &BE80` and the game takes over. `LIST` prints nothing for a protected
     program (a separate check).
  **To read a protected program:** after `LOAD`, stop at `&C06A` (PC breakpoint) and write `&00` to `&AE2C`; the program survives
  (`FRE(0)` drops by 302). Dump from `&170` and run `tools/bastok.py` (result: `work/prot/ELITE.BAS.plain`, `.txt`).
- The program is 3 real lines plus a long line 0 (328 bytes): `MODE 1:INK 0,0:INK 1,24:INK 2,15:INK 3,6:BORDER 0:LOAD"picture",&C000:LOAD CHR$(34):CALL &BE80:CALL 0`,
  then NUL bytes around a `RUN` token and a `REM` box ("This disc is protected by **** ARMOURLOC v1.1 **** Copyright S.Thomas 1985",
  text at `&01BE`); the NULs make `LIST` stop. Then `10 MEMORY &1FFF`, `20 LOAD"!"`, `30 CALL 32313` (`&7E39`). Those lines are not
  what runs: a `RUN` trace opens `largeaxx` third, loaded at `&840`. How the stub redirects the flow is not traced.
- `LOAD CHR$(34)` loads the hidden file named `"` (`&BE80`, `&A1` bytes); `CALL &BE80` runs it:
  1. `CALL &BD19` (flyback), `DI`, pop the return address into HL.
  2. `HL = return address - (word at &0172) - &BE64`; `R = H or L`. The key depends on the call site and on the first bytes of the
     BASIC text.
  3. Loop over `&BEB0-&BEFF`: `byte = R xor byte xor (stub byte at the same offset from &BE80)`. `R` is the Z80 refresh counter, so
     the key stream is the instruction count: tracing, single-stepping or any extra instruction breaks it. The emulator reproduces
     it (decrypted bytes in `work/prot/BE00_after_decrypt.bin`).
  4. The decrypted code at `&BEB0` sets `&BE78` to `&FF`, copies `&30` bytes from `&BEDC` to `&0300`, far-calls ROM 7 (AMSDOS) at
     `&C666` with `DE=&2800`, copies `&6D` bytes to `&DF00` and loops to `&BE80`. `&BEDC` is a failure path (mode 1, print the
     message at `&01BE`, beep forever). What the AMSDOS call does, and so what loads the game from there, is not traced.

## Renamed 2026-11-07

| Old name | New name |
|---|---|
| `ELITE.DSK` | `Elite_UK_original_protected.dsk` |
| `Elite_1985_Firebird_Software.dsk` | `Elite_UK_Firebird_cracked_trainer.dsk` |
| `Elite - Gold [G].dsk` | `Elite_DE_cracked.dsk` |
| `Elite Savegame.dsk` | `Elite_DE_savegames.dsk` |
| `IMG_9858.JPG` | `Elite_DE_controls_card.jpg` (photo of the German controls card) |

Old names still appear in some `work/` file names; the tools take paths, so nothing breaks. All original disks and tapes live in `disks/` (gitignored; moved from the project root 2026-11-16).

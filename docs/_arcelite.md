# ArcElite (Acorn Archimedes, 1991)

No annotated disassembly or source of ArcElite is public. Mark Moxon's bbcelite.com covers the 6502 Elites and Lander (Archimedes), not ArcElite;
Ian Bell publishes only the ship tables as C text. Source: <http://www.iancgbell.clara.net/elite/arc/index.htm> (v1.14, unprotected, Gisburne commander added,
patched for all RISC machines). Files live in `work/arcelite/` (untracked).

| File | What |
|---|---|
| `dl/b5052410.arc` | SparkFS archive of v1.14 (SHA-256 `c948350b…140d8`, same as `~/Downloads/b5052410.arc`) |
| `dl/b5052420.zip` | `ELITE.ADF` (ADFS E, 800K) with `!Elite/ilite` (the game, 229024 bytes) |
| `dl/b5052480.zip` | `B5052480.C`: ship point and facet tables as C text |
| `ilite_aif.bin` | unpacked image, base `&8000` (RO `&51ED8`, RW `&CA30`, zero-init `&39C4`) |
| `ilite.s` | generated listing: about 100k lines, 1046 `fn_` labels, entry `&59944` |

## Unpacking `ilite`

1. Four XOR layers over `&8000-`start of each decryptor (`tools/arc_unlayer.py`): the key starts at 0x13, 0xFB, 0x5D, 0x07 and steps by 0xC9, 0x7F, 0x2B, 0x0D per word.
   Each layer's code sits 0x48 bytes below the previous one at the file end.
2. An Acorn Squeeze-style decompressor (entry `&3FB20`, tables at `&3FA80-&3FB1C`) rewrites the image in place.
   `tools/arc_unpack_emu.py` runs it in unicorn and dumps memory when it jumps to `&8004`.
3. Result is a Norcroft C AIF: header at `&8000`, `bl` to the BSS clear at `&8040`, entry at `&59944` (C library start-up). No APCS function-name words, so no symbols.

`tools/adfs_e.py` extracts the ADF, `tools/sparkx.py` the Spark archives (stored and compress methods; crunch `0x88` not done, not needed), `tools/arc_text.py` decodes the mission text, `tools/arc_xref.py` finds `add rX,pc,#` references to strings, `tools/arc_disasm.py` writes the listing
(`uv run --no-project --with capstone python3 -I tools/arc_disasm.py work/arcelite/ilite_aif.bin work/arcelite/ilite.s`). Data words come from pc-relative loads and string runs; the rest is a linear sweep, so
jump tables and some constants still show as instructions.

## EliteCheat (Jon Ribbens, 1991, public domain)

It edits commander files, not memory. `work/arcelite/x_cheat2/!EliteCht/CmdFile` documents the save layout (all words): `+00` cash*10, `+04` kills, `+08` price seed/encryption,
`+0C` offences, `+10..1C` missions 1-4 (88888 failed, 99999 done), `+2C` mission 4 ingredients, `+30` system, `+34` hyperspace system, `+38` galaxy, `+3C` fuel*10,
`+48` missiles, `+4C..58` lasers (4 pulse, 5 beam, C mining, D military), `+5C..80` equipment, `+8C..CC` hold, `+D4..114` market. Useful for the mission and rating thresholds
(Xeaan, Zartid, Z. Pino, Groigans disease) when comparing with the CPC missions.

## Missions (read from `ilite_aif.bin`; wiki differences noted; wiki: https://wiki.alioth.net/index.php/ArcElite_missions)

The scheduler `fn_12D40` runs from the docking routine (`fn_0E9FC`, at `&EA6C`) on every dock. If it returns 1 a message screen replaces the status screen (`fn_1C804`).
Globals, confirmed from the commander load/save code `fn_103AC` and the status screen (file offsets are EliteCheat's `CmdFile`):

| Global | File | Meaning |
|---|---|---|
| `&5A960` | +04 | kills (also the input of the rating names in `fn_1C1BC`: Poor from 400, Competent 4500, Elite 9800) |
| `&6534C` | +00 | cash in 0.1 Cr |
| `&65398` | +0C | offences/legal status |
| `&6527C` / `&65280` | +30 / +38 | present system (0-255) / galaxy (0-7) |
| `&5AE10`, `14`, `18`, `1C` | +10..+1C | mission 1-4 state (`88888` failed, `99999` done, -999..-995 pending outcome) |
| `&5AE20` | +2C | mission 4 compounds in the hold (bits 1 Ziggathol, 2 Paredon, 4 Noitace, 8 Vordquein) |
| `&5AE24` + 4n | not saved | "chatter line already shown" bits per mission |

Helpers: `fn_59BF4(r0=divisor, r1=dividend)` returns quotient in r0 and remainder in r1 (the `x % n` pattern seen in the status screen); `fn_59CD4` is rand. Both are C-library stubs (`mov pc,#0` in the image), so this is inferred from the calling pattern.
Texts: `&28529-&29830`, token-compressed (`tools/arc_text.py`; dictionary of 107 words at `&23A10`, `1B nn` = token `nn-1`). Flight messages ("REPENT SINNER!") are inline strings behind a jump table at `&1AD00`.

| # | Condition (all checked in `fn_12D40`) | Flow | End |
|---|---|---|---|
| 1 Genesis capsule | state 0, galaxy 1, kills > **450**, cash > 1200 Cr | Brief (bit 1). At system 167 Razaar (state 1): second brief (bit 2). At 236 Ordima (state 3): 150 Cr taken (clamped at 0), capsule loaded (state 7). From then on, away from system 80 Xeaan, 1 in 3 docks shows one of three Xeaan lines. | code -999 +500 Cr and `99999`; -998 wrong direction; -997 too high; -996 wrong planet; -995 capsule destroyed (hull type 59 killed); the last four set `88888` |
| 2 Zartid | state 0, any galaxy, kills > 1450, cash > 4000 Cr | Brief names system 116. At 116 (state 1): "has just left" (bit 2). Then each dock increments a counter; above 20 it sets -998 (failed message, `88888`). 1 in 5 docks adds one of three chatter lines. | hull type 44 destroyed sets -999: yaw boosters, offences -9999 (cleared), `99999` |
| 3 Zurid Pino | state 0, any galaxy, kills > 2600 (bit 1); kills > 2650 and 1 in 5 docks for the second message (bit 2) | then 1 in 3 docks one of ten taunts, each once | hull type 47 destroyed sets -999: MisLoc flag set, `99999` |
| 4 Groigan cure | state 0, **galaxy index > 4 (galaxies 6 to 9; EliteCheat lists 6-8)**, kills > 4600, offences < 1000, present system mod 3 = 1 | Brief (bit 1) names 172. At 172 with state exactly 1: Ziggathol, points to 171 and 170, state bit 2. 171 (if bit 4 clear): Paredon, points to 174. 170 (bit 8): Vordquein, points to 173. 173 (bit 16): Noitace, points to 174. 174 mixing lab: compounds are taken every visit. | state = 31: +2000 Cr, `99999`; otherwise "There are more ingredients required" |

Wiki matches the code on every number above except mission 1 (wiki: 550 kills; code compares > 450, which is the "Poor" band that EliteCheat's notes also name).
Not taken from the wiki or confirmed here: the planet names for 170-174 per galaxy, Zartid's five-Mamba convoy, Pino's cloak and "government < 3", the Paredon heat model.
The capsule codes are set by `fn_0CF14` (the jettisoned capsule reaching a planet): wrong system or galaxy (not system 80 in galaxy index 0) gives -996, a miss in the direction test -998, a drop from too high -997, otherwise -999.

Not traced: where hull types 44, 47 and 59 get spawned and what the engine type ids are (they do not follow the order of `B5052480.C`), and what hull 29 does in the destroy handler `fn_0A560`.

## Nine galaxies

The galaxy variable (`&65280`, struct `&6523C` + `0x44`) is switched on in the name routine at `&1FDC0` with `cmp r0,#8`, so nine cases exist: 0 Santaari, 1 Colesque, 2 Lara'tan, 3 Angiana, 4 Proximus, 5 Sol, 6 Jaftra, 7 Xrata, **8 Trojane**
("Trojan" was the working title of the game). Mission 1 is bound to index 0 (the briefing says "Razaar (Santaari)"). Neither the Atari ST/Amiga source (`work/ext_st/repo`: its README speaks of "the eight galaxies"; its missions note covers only mission 5) nor EliteCheat
(galaxy 1-8) mentions a ninth. Not found: the code that advances the galaxy on a galactic jump (the hyperdrive start is `fn_0DD64`, message 63) and so whether index 8 is reachable; the Elite Plus EXE does reach its ninth galaxy with a 300/65536 roll (`docs/_missions.md`, "Unconfirmed features"), so ArcElite may do something similar.

## Next

Name the C functions: match the ship tables against `B5052480.C`, the galaxy generator against the 6502 emulation noted on stardot, and the text against `docs/_missions.md`.

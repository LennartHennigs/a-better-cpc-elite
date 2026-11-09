## Reference material (6502 versions, for naming and understanding logic)

- Apple II annotated disassembly: https://6502disassembly.com/a2-elite/Elite.html
- Disassembled 6502 sources: https://6502disassembly.com/a2-elite/
- BBC Micro cassette Elite, fully annotated: https://github.com/markmoxon/cassette-elite-beebasm
- Christian Pinder, *Elite: The New Kind* (C port).

## Sources and reading

- Elite CPC overview: https://share.google/skG3KDYY0Dx48bvUL
- Amtix Magazine issue 13: https://archive.org/details/Amtix_Magazine_Issue_13 (local copy `magazines/Amtix_Magazine_Issue_13.pdf`, Pinto interview pp. 84-86)
- Ricardo Pinto interview about the Elite Z80 conversions (see links below).
- The King of Grabs, Elite Amstrad CPC: https://thekingofgrabs.com/2020/03/02/elite-amstrad-cpc/
- Amstrad Action issue 3: https://archive.org/details/amstrad-action-003/page/n69/mode/1up (local copy `magazines/Amstrad_Action_003.pdf`, preview pp. 70-71)
- Elite archive, lost ports, 40th anniversary: https://theoasisbbs.com/elite-archive-lost-ports-elites-40th-anniversary-highlights/
- Filfre (The Digital Antiquarian), "Elite": https://www.filfre.net/2013/12/elite/ (history of the game and its ports)

## Commodore 64 and 6502 source (found 2026-11-07)

- Annotated C64 Elite source (original code, Mark Moxon's commentary): https://github.com/markmoxon/elite-source-code-commodore-64
  and https://elite.bbcelite.com/c64/ (map of the source: https://elite.bbcelite.com/c64/articles/map_of_the_source_code.html).
  Contains the Trumbles code (`TBRIEF`, `MVTRIBS`, `TRIBTA`, `TRIBMA`, `spritp`). Copyrighted: read only.
- Library of every annotated version (BBC, Apple II, C64, NES ...): https://github.com/markmoxon/elite-source-code-library
- Forks of the C64 repo, one with mods (blocks buying a ship while carrying Trumbles): https://github.com/ataribaby42/elite-source-code-commodore-64
- A separate full C64 disassembly and enhanced port: https://github.com/Kroc/elite-harmless
- Trumbles deep dive: https://elite.bbcelite.com/deep_dives/the_trumbles_mission.html

## Tools worth a look

- cpcxray (https://github.com/SerErris/cpcxray): reverse-engineering emulator that traces code and writes
  reassemblable sjasmplus source; has an MCP server.
- z80dismblr, z80-smart-disassembler, RASM, iDSK (see `CLAUDE.md`).

## Tools mentioned

- Ghidra for disassembly, RASM 2.2.5, VSCode, ACE-DL (trace window, GFX Explorer, host-directory drive via
  Albireo), WinAPE with symbol table. A CPC reverse-engineering tool was suggested:
  https://www.cpcwiki.eu/forum/programming/any-interest-in-a-cpc-reverse-engineering-tool/
- More references: https://www.bbcelite.com/ (BBC variants explained),
  https://www.ricardopinto.com/2022/09/19/interview-about-elite-z80-conversions/ (Ricardo Pinto interview),
  http://www.elitehomepage.org/archive/index.htm (Ian Bell's BBC sources),
  https://stardot.org.uk/forums/viewtopic.php?t=20377.

## 68000, NES and mission sources (found 2026-11-07)

- Atari ST / Amiga Elite source (original ST code, Mr. Micro 1988, adapted from the MSX version): https://github.com/ataribaby42/elite-source-code-atarist
  (fork: https://github.com/pulchart/elite-source-code-atarist). Cloned to `work/ext_st/repo`. Missions: `src_orig/asm/missions.m68`.
- NES Elite, annotated: https://github.com/markmoxon/nes-elite-beebasm (cloned to `work/ext_nes/repo`).
- Mission pages: https://elite.bbcelite.com/deep_dives/ (Constrictor, Thargoid Plans, Trumbles, Elite-A special cargo).
- Mission lists and per-version notes: https://wiki.alioth.net/index.php/AFE_FAQ2, https://wiki.alioth.net/index.php/AFE_FAQ3,
  https://wiki.alioth.net/index.php/MSX_Elite, https://www.lemon64.com/forum/viewtopic.php?t=6158,
  https://www.atari-forum.com/viewtopic.php?t=5985, https://www.tales-from-darkenedroom.com/post/elite-plus-missions-galaxy-9,
  https://gamefaqs.gamespot.com/nes/581795-elite/answers/635813-can-anyone-give-me-a-full-list-of-quests-for-the-nes-version-with-their-triggers.
- Magazine type-in for commanders: `magazines/elite-commander.pdf` (CPC International 3/86).
- MSX Elite: https://wiki.alioth.net/index.php/MSX_Elite (five missions, trigger and reward list; no source link). TI-99/4A conversion of the
  MSX code with the mission state table: https://github.com/Rasmus-M/elite-ti994a (cloned to `work/ext_msx/ti99`). The SkoolKit MSX
  disassembly it is built from ("elite-msx-skoolkit") was not found online. Found instead (cloned 2026-11-07 into `work/ext_msx/`, read-only):
  - https://github.com/Rasmus-M/elite-skoolkit (`work/ext_msx/skoolkit`): commented SkoolKit disassembly of **ZX Spectrum** Elite
    (`src/elite.skool`, 28,000 lines). The CPC port is a Spectrum port, so this is the closest annotated relative: same mission flag byte
    (bits 3, 5, 6, 7), same Asp spawn code, same shared throttle byte. Use it to name CPC routines.
  - https://github.com/ricbit/elite (`work/ext_msx/ricbit`, listed on https://recomp.fyi/game/elite-msx): complete sjasmplus disassembly of
    the **MSX** game (`code.asm`: 23,770 lines covering `&0100`-`&A7F5`, i.e. the whole 42,752-byte `CODE.COM`; plus the other disk parts in
    separate `.asm` files). Checked 2026-11-07: 1,928 of 1,930 labels have a one-line comment under them, all 764 `equ` variables are
    described, and every line carries its address and bytes; but there is almost no line-by-line commentary (about 2,300 standalone
    comment lines in total) and the label names are descriptive but unverified. Single commit, 2026-07-17. Not built here (rule: no
    building downloaded source), so "byte-exact" is the author's claim.
  - https://github.com/markmoxon/elite-source-code-nes is the NES source already cloned at `work/ext_nes/repo` (origin `nes-elite-beebasm`, same project).


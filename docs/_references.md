# References

Third-party sources are read-only references for naming and logic; copyrighted, do not copy them into the project.
Local clones live under `work/` (untracked).

## History and magazines

- Amtix issue 13: https://archive.org/details/Amtix_Magazine_Issue_13 (`magazines/Amtix_Magazine_Issue_13.pdf`, Pinto interview pp. 84-86)
- Amstrad Action issue 3: https://archive.org/details/amstrad-action-003/page/n69/mode/1up (`magazines/Amstrad_Action_003.pdf`, preview pp. 70-71)
- CPCWiki forum, "Expanding Elite" (**Fessor**): https://www.cpcwiki.eu/forum/programming/expanding-elite/ (pages 1-3). His disassembly, source, beta disk and symbol list are there (his source and beta are not redistributed here; get them from the thread). His post showing the Constrictor, the hull used in `src/elite/missions_hull.asm`: https://www.cpcwiki.eu/forum/programming/expanding-elite/msg205425/#msg205425. He agreed by private mail to the use of the hull and of his names and findings. Source of the off-screen bitmap `&A000-&BFFF`, the memory swapping at takeoff and docking and the 20/23-byte ship header; also his beta and source. Nothing there on `&A600` specifically
- Ricardo Pinto, interview about the Elite Z80 conversions: https://www.ricardopinto.com/2022/09/19/interview-about-elite-z80-conversions/
- The King of Grabs, Elite Amstrad CPC: https://thekingofgrabs.com/2020/03/02/elite-amstrad-cpc/
- Elite archive, lost ports: https://theoasisbbs.com/elite-archive-lost-ports-elites-40th-anniversary-highlights/
- Filfre, "Elite": https://www.filfre.net/2013/12/elite/
- Ian Bell's BBC sources: http://www.elitehomepage.org/archive/index.htm
- Commander type-in: `magazines/elite-commander.pdf` (CPC International 3/86)

## Annotated sources of other versions

| Version | Source | Local clone / notes |
|---|---|---|
| ZX Spectrum (closest relative of the CPC code) | https://github.com/Rasmus-M/elite-skoolkit | `work/ext_msx/skoolkit/src/elite.skool`, 28,000 lines. Same mission flag byte (bits 3, 5, 6, 7), Asp spawn code and shared throttle byte. Use it to name CPC routines |
| MSX | https://github.com/ricbit/elite (https://recomp.fyi/game/elite-msx) | `work/ext_msx/ricbit`; sjasmplus disassembly of `CODE.COM` (`code.asm`, 23,770 lines, `&0100`-`&A7F5`). One-line comment per label, little line commentary, label names unverified; "byte-exact" is the author's claim (not built here) |
| TI-99/4A (MSX code) | https://github.com/Rasmus-M/elite-ti994a | `work/ext_msx/ti99`; has the mission state table |
| Atari ST / Amiga | https://github.com/ataribaby42/elite-source-code-atarist (fork: https://github.com/pulchart/elite-source-code-atarist) | `work/ext_st/repo`; read `src_orig/` (missions: `src_orig/asm/missions.m68`), `src_atari/` is modified |
| NES | https://github.com/markmoxon/nes-elite-beebasm | `work/ext_nes/repo` |
| BBC cassette | https://github.com/markmoxon/cassette-elite-beebasm | |
| C64 (Trumbles code: `TBRIEF`, `MVTRIBS`, `TRIBTA`, `TRIBMA`, `spritp`) | https://github.com/markmoxon/elite-source-code-commodore-64, https://elite.bbcelite.com/c64/ | Forks: https://github.com/ataribaby42/elite-source-code-commodore-64 (blocks buying a ship with Trumbles), full disassembly https://github.com/Kroc/elite-harmless |
| Elite-A (Angus Duggan, BBC) | https://github.com/markmoxon/elite-a-source-code-bbc-micro | `work/ext_elitea/repo` (shallow clone, copyrighted, read-only); `1-source-files/main-sources/`, Angus's own files in `original-sources/` |
| Apple II | https://6502disassembly.com/a2-elite/Elite.html | |
| All annotated versions | https://github.com/markmoxon/elite-source-code-library, https://www.bbcelite.com/ | |
| C port | Christian Pinder, *Elite: The New Kind* | |

## Missions

- Deep dives (Constrictor, Thargoid Plans, Trumbles, Elite-A special cargo): https://elite.bbcelite.com/deep_dives/ (Trumbles: .../the_trumbles_mission.html)
- Lists and per-version notes: https://wiki.alioth.net/index.php/AFE_FAQ2, .../AFE_FAQ3, .../MSX_Elite (five missions),
  https://www.lemon64.com/forum/viewtopic.php?t=6158, https://www.atari-forum.com/viewtopic.php?t=5985,
  https://www.tales-from-darkenedroom.com/post/elite-plus-missions-galaxy-9, NES quest list on GameFAQs
  (https://gamefaqs.gamespot.com/nes/581795-elite/answers/635813-can-anyone-give-me-a-full-list-of-quests-for-the-nes-version-with-their-triggers)
- ArcElite (Archimedes): https://wiki.alioth.net/index.php/ArcElite_missions (four missions with triggers; checked against the code in `docs_other/_arcelite.md` (local only)), game and ship tables from
  http://www.iancgbell.clara.net/elite/arc/index.htm, commander file format in EliteCheat (Jon Ribbens)
- Elite Plus decompilation: https://github.com/rembish/elite-plus-revamp

## Algorithms (Mark Moxon's BBC deep dives, https://elite.bbcelite.com/deep_dives/)

6502 explanations of routines the CPC port shares in structure (it descends from the Spectrum port of the BBC code). Read for the idea, not the code. Index: `/deep_dives/`.

| Topic | Page | Relevant to |
|---|---|---|
| Ship drawing (routine LL9 in 12 parts: visibility distance, orientation, face and vertex visibility, screen conversion, edge selection; per-ship line heap for erasing) | `drawing_ships.html` | `todo_parseEdges`, `pvLoop`, `handleEntitys`; `_ship_occlusion.md` (the CPC redraws a cleared bitmap, so it has no line heap) |
| Which faces are visible | `back-face_culling.html` | edge visibility in the draw path |
| Vertex projection | `calculating_vertex_coordinates.html` | `pvLoop` |
| Flicker-free drawing | `flicker-free_ship_drawing.html` | why the Z80 ports need no such patch (`_gameplay.md`) |
| Ship blueprint layout | `ship_blueprints.html`, `ship_data_blocks.html`, `comparing_ship_specifications.html` | the 23-byte Z80 header vs the 20-byte 6502 one (`_architecture.md`), Constrictor hull conversion |
| Lines | `elites_line-drawing_algorithm.html`, `line-clipping.html` | the two self-patched Bresenham plotters |
| Sun and planets | `drawing_the_sun.html` | the disc routine and its clamp (`_architecture.md`) |
| Cougar | `the_elusive_cougar.html` | the cloak mission (`_missions.md`) |
| Maths | `shift-and-add_multiplication.html`, `shift-and-subtract_division.html`, `calculating_square_roots.html`, `multiplication_and_division_using_logarithms.html`, `the_sine_cosine_and_arctan_tables.html` | the renamed `mult_b_c`, `div_de_h`, `approx_sqrt_16bit` and the square tables |
| Rotation | `orientation_vectors.html`, `pitching_and_rolling.html`, `tidying_orthonormal_vectors.html` | ship movement routines |

Only `drawing_ships.html` was fetched (2026-11-09); the other rows are chosen from its link list and titles, so check a page before relying on it.

## Tools

- cpcxray (https://github.com/SerErris/cpcxray): tracing emulator that writes reassemblable sjasmplus source; MCP server.
- Also used or considered: z80dismblr, z80-smart-disassembler, RASM, iDSK (see `CLAUDE.md`), Ghidra, ACE-DL, WinAPE.
- CPC reverse-engineering tool thread: https://www.cpcwiki.eu/forum/programming/any-interest-in-a-cpc-reverse-engineering-tool/
- Elite on Stardot: https://stardot.org.uk/forums/viewtopic.php?t=20377

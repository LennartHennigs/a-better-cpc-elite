# Elite (Amstrad CPC) – Notes

Index to the research notes. The notes live in `docs/`, one file per topic; this file only says where to look.
Rules, toolchain and workflow are in `CLAUDE.md`, open work in `TODO.md`, dated changes in `CHANGELOG.md`.

| Topic | File |
|---|---|
| Origin of the CPC port, Torus/Firebird, magazine interviews (Amstrad Action 3, Amtix 13), existing work | `docs/_history.md` |
| Disks in the project root, hashes, renames, loader sequence, CPC Power releases, ARMOURLOC protection | `docs/_disks.md` |
| Fessor's source, beta disk and symbols; mapping his labels onto stock; forum thread digest | `docs/_fessor.md` |
| Disassembly of the stock build (`src/elite/`), entry point, port architecture, hazards | `docs/_architecture.md` |
| `CHEAT.BAS` poke targets, instruction-level analysis, the cloaking cheat and its fix, the interactive `CHEAT.BAS` | `docs/_cheats.md` |
| Commander save format, encryption, checksums, field map, the CPC International type-in cross-check | `docs/_savegame.md` |
| The three CPC missions, when they fire, hyperspace/mis-jump, missions in other versions (ST and NES source), keycard and keys | `docs/_gameplay.md` |
| Missions research: table across versions, MSX/ST/NES/C64/Elite Plus source readings, planning findings (system names, spawn rule, free space) | `docs/_missions.md` |
| The implemented missions: order, triggers and prerequisites, architecture (stub, overlays, flight images), sizes, tests | `docs/_missions_built.md` |
| CPC+ keyboard bug, Redbox's patch, plan for our own fix | `docs/_cpcplus.md` |
| CPC routines mapped to the ZX Spectrum disassembly (names, addresses, method) | `docs/_spectrum_map.md` |
| 6502 references, links, tools | `docs/_references.md` |

When you change a fact, edit it in the `docs/` file only. Do not re-upload Fessor's material elsewhere (see
`extended/CLAUDE.md`).

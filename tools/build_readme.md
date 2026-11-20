# build/

What the `make` targets deliver. Everything in here is generated and gitignored: `make clean` deletes this folder, and `make` writes this file again. The sources are in `src/`, the intermediate files in `work/`, the original disks in `disks/`.

| File or folder | Made by | What it is |
|---|---|---|
| `elite_original.dsk` | `make original` | The original game, stock bytes with the CPC+ keyboard fix, on a copy of the Firebird disk (its own `CHEAT.BAS` stays on it). Boot with `RUN"ELITE`. |
| `elite_original_de.dsk`, `elite_original_fr.dsk` | `make original LOC=de` / `LOC=fr` | The same for the German and French builds. The French disk boots with `RUN"EL`. |
| `elite64.dsk` | `make expanded` | The full build, English only: enhancements, all added missions, the ship packs and the busier traffic, our trainer and the save tools, the ship viewer and a ready commander. `RUN"ELITE64` starts the game (its loader is `ELITE64.BAS`, Firebird's `ELITE.BAS` renamed); `RUN"TRAINER`, `RUN"EDITSAVE`, `RUN"LISTSAVE` and `RUN"SHOWSHPS` start the tools. |
| `elite_missions.dsk` | `make missions` | Enhancements plus the added missions, bootable with `RUN"ELITE`, without the trainer, save tools and ship viewer. English only. |
| `stock/<en,de,fr>/` | `make stock [LOC=de\|fr]` | The four code files assembled with no flags (the original bytes), raw, without AMSDOS headers: `largeaxx.bin`, `commonxx.bin`, `common2x.bin`, `musiquex.bin`. |
| `enhanced/<en,de,fr>/` | `make enhanced [LOC=de\|fr]` | The same files with the improvements (`-DENHANCED -DTITLESEL`). |

Only the disks are meant to be played. The `.bin` files are for comparing and for building your own disk (`tools/build_dsk.py` adds the AMSDOS headers).

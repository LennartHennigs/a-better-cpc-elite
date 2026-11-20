# tools/

Helpers for building, checking and analysing the project. Each script has a header docstring with its usage; run Python ones with `python3 -I tools/NAME.py`. The `make` targets call the build ones; the cpcxray tests are in `tools/tests/` (own README).

## Build and disks
| File | Does |
|---|---|
| `check_src.sh [de\|fr]` | assembles `src/elite*` and compares with the original binaries (the byte-exact proof; `make check`) |
| `build_dsk.py` | assembles a build into a copy of the base disk (`--stock`, `--missions`, `--de`, `--fr`) |
| `build_original.sh`, `build_expanded.sh` | the two `make` disks, written to `build/` |
| `build_cheat.sh`, `build_showship.sh` | tokenise the BASIC programs of `src/cheats/` and build the trainer and viewer disks (in `work/`) |
| `build_readme.md` | template for `build/README.md` |
| `dskx.py`, `add_files.py`, `hide_files.py` | list/extract, add files to, and hide files on DSK images (never write to `disks/`) |
| `cheat_tokenise.py`, `bastok.py` | tokenise CPC BASIC with the CPC's own BASIC (cpcxray), detokenise to text |
| `size_report.py` | bytes used in the free tails against the stock files |
| `rvmstate.py` | read an RVM `.rvmstate` file: registers, the 64 KB RAM image, the ship slots, and `--sna` to convert it to a snapshot cpcxray loads (`--curcfg` for a 128K game state; `docs/_build.md` "RVM state files") |

## 128K build (branch `elite128`; `src/elite128/README.md`)
| File | Does |
|---|---|
| `check_src128.sh` | assembles the four 128K files, builds the fill and title-text modules, fails on a stale cross-file `equ` (`make disk6128`) |
| `build_dsk128.py`, `build_show128.sh`, `listing6128.sh` | the 128K disk (`build/elite128.dsk`), the `SHOWSHPS` viewer programs, the readable listing (`make listing6128`) |
| `ship128.py`, `hullfill.py`, `mk_viewer128.py` | filled hulls (stock blueprints or ArcElite), their fill records, the viewer's ship data; generated files go to `work/elite128/` |
| `gen_equs.py`, `sync_equs.py`, `check_moved_labels.py` | cross-file `equ` lines after any size change (`sync_equs.py` exits 0 even when stale: read its last line), raw numbers that still point at a stock address whose label moved |

## Saves and text
| File | Does |
|---|---|
| `saveedit.py`, `savedec.py`, `elitekey.py`, `savekeys.py` | edit and decode commander saves, read the save key from a disk |
| `mk_editsave.py`, `mk_listsave.py`, `mk_showship.py` | generate `EDITSAVE.ASC`, `LISTSAVE.ASC`, `SHOWSHPS.ASC` and the viewer data |
| `elitetext.py`, `textenc.py`, `textcomp.py`, `sprite_enc.py` | Elite text tokens (decode, encode, measure) and sprite art to bytes |

## Source trees (disassembly)
| File | Does |
|---|---|
| `disasm_stock.py`, `disasm_locale.py` (+ `disasm_german.py`, `disasm_french.py`) | disassemble to sjasmplus source with a round-trip check; **never write into the hand-edited trees**, use a scratch directory |
| `map_locale.py` (+ `map_german.py`, `map_french.py`), `map_labels.py` | carry names from the English tree to German and French; map Fessor's labels |
| `relabel.py`, `rename_labels.py`, `z80dis.py`, `lstparse.py` | fold `db` runs into instructions, rename labels in all trees, the Z80 decoder and listing parser |
| `deadcode.py`, `dbcode.py`, `db_ranges.py`, `dead_trace.py`, `exec_in_data.py`, `trace_unknowns.py`, `circle_sweep.py` | find dead or hidden code and unknown variables, statically and by running the game |

## Missions and ships
| File | Does |
|---|---|
| `fessor_hull.py`, `fessor_ships.py` | convert Fessor's hulls (RASM) into `missions_hull.asm` and `missions_ships.asm` |
| `hull_dedupe.py` | measure duplicate byte runs across the ship blueprints |

## Other systems and sources
| File | Does |
|---|---|
| `spectrum_map.py`, `spectrum_data_map.py`, `apply_spectrum_names.py`, `gen_spectrum_map_doc.py` | match the CPC code to the ZX Spectrum disassembly and carry names over; regenerate `work/spectrum_map/` and `docs_other/_spectrum_map.md` with `python3 -I tools/spectrum_map.py && ... spectrum_data_map.py && ... gen_spectrum_map_doc.py`. Take only names and addresses from the Spectrum source, write comments in our own words and mark matches `; ZX Spectrum: name (&ADDR)` |
| `cdt_direct_decode.py`, `unexepack.py`, `sparkx.py` | tape block decoder, DOS EXEPACK unpacker, SparkFS archive extractor |

Other folders: `bin/` (the locally built RASM, untracked), `rename_maps/` (maps used by `rename_labels.py`), `proto_fill/` (filled-ship prototype), `tests/`.

RASM (`tools/bin/rasm`, only for Fessor's source; gitignored, not in the repo) is built locally: `cc -O2 -DNO_3RD_PARTIES -DNOAPI -o rasm rasm.c -lm -lpthread` (the repo's makefile fails to link). Never run it on `work/build_fessor`'s other `.asm` files: it overwrites `rasmoutput.sym`.

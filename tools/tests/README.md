# tools/tests/

Test scripts that drive the game in the **cpcxray** emulator (headless, through its MCP server). They check one routine or feature each: a hook, a mission, a flight image, a screen. They are not unit tests of Python code. For the byte-exact check of the source, use `bash tools/check_src.sh [de|fr]` (or `make check`).

## Running everything

```bash
make test        # rebuilds the disks, then check_src (en, de, fr), test_saves and test_disks; about a minute, no emulator
make test-emu    # the cpcxray tests that print ALL OK (builds and copies the disks itself); several minutes
python3 -I tools/tests/run_all.py [--host] [--emu] [--only NAME ...]
```

`run_all.py` prints one line per test and exits non-zero if any failed. The screenshot and probe tests (`test_star_occlusion`, `test_station_screens`, `test_keydelay`, `test_cloak_asp`, `test_flight_hull`, `test_trumbles_screens`, `test_parked_*`) have no pass/fail and are run by hand.

## Host tests (no emulator)

| Test | Checks |
|---|---|
| `test_disks` | every disk in `build/`: only `.BAS`, `.TXT` and saves visible in `CAT`, valid AMSDOS headers, no block on an odd-sector track, the needed files present, the save key unchanged against the original game of that language |
| `test_saves` | the four build keys (UK, French, German and the 128K build's from `src/elite128`), the saves of the original disks decode with their own key and not with another, decode and encode round trip, German to UK to German conversion, every save to the 128K key and back |

## Running one emulator test

```bash
export PATH="$HOME/.local/bin:$PATH"
cd work/xray                      # the scripts use relative paths (output/, disk/, config/)
~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/tests/test_NAME.py [args]
```

- Use cpcxray's own Python (above), not the system one: it has the `mcp` package.
- Most tests assemble from `src/` when they start, so do not edit `src/` while one runs.
- Most need a built disk copied by hand into `work/xray/disk/` (the build scripts no longer copy there) and the snapshot `work/xray/output/firebird_in_flight.sna`. The header of each script says what to build first.
- Long runs: start them in the background and poll the output; the foreground stops at two minutes.
- Output goes to `work/xray/output/` (screenshots, snapshots); the tests print the result.

## The tests

| Test | Checks | Needs |
|---|---|---|
| `test_mission_hook` | the docked mission stub and the Constrictor and plans overlays | mission disk |
| `test_mission_flight` | `mxSpawnCheck` (Constrictor spawn) and `mxKillHook` | mission disk |
| `test_flight_hull` | spawns the Constrictor and shows it (also a tool for looking at any hull) | mission disk |
| `test_plans` | the flight side of the plans mission (Thargoid and Thargon spawn, energy unit) | mission disk |
| `test_stolen_ship` | the stolen police ship (spawn at Birera, stages) | mission disk |
| `test_rocks` | the asteroid mission (spawns, kill countdown) | mission disk |
| `test_trumbles`, `test_trumble_sprites` | the Trumbles image: breeding, heat death, inventory line, the sprites | mission disk |
| `test_trumbles_screens` | a watch, not a test: one Trumble, then jumps (the game's own arrival code) up to a swarm, screenshots at four stages (`output/trumbles_*.png`) | mission disk |
| `test_launch` | the launch hook puts the right flight image in the `COMMONXX` tail | mission disk, same flags as the disk (`-DENHANCED -DTITLESEL -DTRAFFIC -DMISSIONS`) |
| `test_ship_packs` | the ship pack hook hands out the extra hulls about half the time | in-flight snapshot, any disk |
| `test_sellall` | the A key of the sell menu | mission disk (or a disk as argument) |
| `test_title_ships` | title-screen ship selection | `build_dsk.py` disk (`elite_rebuilt.dsk`) |
| `test_station_screens` | screenshots of the docked screens with the `-DENHANCED` changes | rebuilt disks (`en`, `de`, `fr`) |
| `test_star_occlusion` | stars are not drawn over the planet or sun (`off`, `far`, `sun` as arguments) | in-flight snapshot |
| `test_keydelay` | key pre-delay, stock against `-DENHANCED` | Firebird disk copy |
| `test_cloak_asp` | is the cloaking-mission Asp visible (view and scanner) | Firebird disk copy |
| `test_parked_ram`, `test_parked_save` (`BUILD=128` for the 128K build; `test_parked_save128` drives the 128K file menu instead, `RUNSEL=a:b` marks only some zero runs) | probes: is the zero space in parked firmware RAM really unused, and what survives a disk save. The result is "do not put code there" (`docs/_memory_map.md`); kept as evidence. | Firebird disk copy |

## 128K tests (branch `elite128`)

Run from `work/xray` with absolute script paths (in this worktree `work/xray` is a symlink to the main checkout). They need `build/elite128.dsk` copied to `work/xray/disk/elite128.dsk` (or `DISK128=...`); `python3 -I tools/tests/run_all.py --emu128` builds the disk and runs `packs`, `ship_packs`, `sellall`, `escdigit`, `filemenu`, `music` and `tools` (the ones with an `ALL OK` line); the rest are screenshots and probes, run by hand. Flight tests start from `output/flight128.sna` (`test_flight128.py 3`), launch and docking tests from `output/docked128.sna` (`snap_docked128.py`; regenerate it after any code change).

| Test | Checks |
|---|---|
| `test_boot128`, `snap_docked128`, `test_flight128` | boot to the title, a docked snapshot for the quick tests, launch and fly (the snapshots the others start from) |
| `test_fill128`, `test_hulls128`, `test_order128`, `test_views128` | the polygon fill in bank 6, every hull type, draw order, the other views |
| `test_flip128`, `test_isrjitter128`, `test_soak128` | page flip (banks equal after each flip), raster split jitter, soak with a reset breakpoint |
| `test_ship_packs128` | the pack hook on the 128K build: each pack's flight image at `&9D9E`, the extra hull about half the time, types 8, 15 and 18 untouched (needs `output/flight128.sna`) |
| `test_launch128`, `test_mission128`, `test_packs128` | flight image copied from bank 5, mission overlays from RAM, the random ship pack per launch |
| `test_titleships128`, `test_viewer128` | the title ship selector, `RUN"SHOWSHPS` |
| `test_sellall128`, `test_escdigit128`, `test_killcount128`, `test_sights128`, `test_filemenu128` | A key of the sell menu, Esc at the second digit, kill count on the commander page, laser sights, catalogue/save/load |
| `test_tools128` | the 128K disk's tools: `CONVSAVE` UK to 128K and 128K to UK compared byte for byte with the host, `LISTSAVE` names the builds, `EDITSAVE` edits a 128K save, `TRAINER` with every cheat on (the 13 poke targets, the commander block, still there after the title is up) |
| `test_viewer128` | screenshots of the ship viewer (`RUN"SHOWSHPS`): first ships, the last one, Q back to BASIC; look at `output/viewer128_*.png` (no pass/fail) |
| `test_music128` | the title music: PSG registers change on the title, stop after it, the bank 7 slot is `NOTMUSIC.BIN` again |

Tips: stop at `handleEntitys` (`&5066`) and restore the registers when injecting calls; `run` reports `time_limit`, not a breakpoint stop, so count hits with `breakpoint_list`; hold keys 1.2 to 1.5 s. More in `docs/_build.md` ("Tests and the emulator").

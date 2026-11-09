# Open questions

What we still do not know and could settle. Things that cannot be settled (no cassette image, Fessor's switched-off blocks, details of the Elite Plus hack) or that do not matter for the CPC build are left out; plain work is in `TODO.md`.
When one is settled, put the result in the owning doc and delete the row.

| Question | Status | How to settle it | Doc |
|---|---|---|---|
| Does the one-byte CPC+ fix work on real Plus hardware? Why does the ASIC object to the stock port order? | Rests on Redbox's disk and his test; the mechanism is inference. Caprice32 does not reproduce the bug | WinAPE with Plus PPI emulation on, or a real CPC464+/6128+ | `_cpcplus.md` |
| Does a disk built with `-DENHANCED` boot and behave (Esc in the buy prompt, stars behind the planet)? | The bytes are checked and the ESC byte was tested in a live snapshot; the built disk was never booted | boot `work/elite_rebuilt.dsk` | `_my_changes.md` |
| What is the 6.5 KB parked in `&A600-&BFFF` while docked and in `&0040-&1A3F` in flight? Does the docking direction of the swap behave as read? | Not a disk file, not written in flight, not referenced by `COMMONXX`; probably holds the stored dashboard image. The launch direction was measured, docking only by source and an earlier measurement | write/read breakpoints on `&0040-&1A3F` over a dock-launch cycle | `_memory_map.md` |
| ISR worst-case stack depth: which top bytes of the `&9D9E-&9FFF` tail are safe? | Unmeasured; only `&9FFE-&9FFF` is known to be hit | write watch on the tail over a long session | `_architecture.md` |
| Disc fill on the unclamped screen path (`ce2func46`, charts) and for radii under 9 | Not covered by the 131,072-input sweep of the in-flight path | extend `tools/circle_sweep.py` | `_architecture.md` |
| Does the whole mission chain play through, with save and load? Are the tuning values right (20 asteroids, 50% and 22% spawn rates, Birera as the police target, 4,000/5,000/6,000 Cr)? Do the Constrictor's ECM and missiles work? | Everything is tested with forced states and direct calls; nothing was played through. The stock-mission pokes and trainer stages 2 and 3 were not run end to end | a real playthrough on `work/missions_cheat.dsk` | `_missions_built.md` |
| Does Fessor agree to the committed Constrictor hull (`src/elite/missions_hull.asm`)? | The file header says the owner allowed this one hull; unclear that Fessor agreed | ask him, or drop the file and regenerate it locally before publishing | `TODO.md` |

Not built, by decision: French `TITLESEL`, `--fr` disk builds, hiding stars behind ships (`_ship_occlusion.md`), a random per-commander mission order (no room), the escape-pod clear fix, furs when Trumbles die in a sun (`TODO.md`).

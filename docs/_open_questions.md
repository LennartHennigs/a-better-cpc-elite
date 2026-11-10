# Open questions

What we still do not know and could settle. Things that cannot be settled (no cassette image, Fessor's switched-off blocks, details of the Elite Plus hack) or that do not matter for the CPC build are left out; plain work is in `TODO.md`.
When one is settled, put the result in the owning doc and delete the row.

| Question | Status | How to settle it | Doc |
|---|---|---|---|
| Does the one-byte CPC+ fix work on real Plus hardware? Why does the ASIC object to the stock port order? | Rests on Redbox's disk and his test; the mechanism is inference. Caprice32 does not reproduce the bug | WinAPE with Plus PPI emulation on, or a real CPC464+/6128+ | `_cpcplus.md` |
| Does a save on a writable `-DENHANCED` mission disk work, and what does a write-protected one do? | The user booted and played `work/elite_missions.dsk` in RVM on 2026-11-10 (it worked, felt faster); a save on a write-protected image reset to BASIC. Whether stock does the same and a successful save on the rebuilt code are untested | clean boot in cpcxray with `disk_insert` read-only and writable, save a commander | `TODO.md` |
| Does the docking direction of the swap (`loadLARGEAXX`) behave as read? The 6.5 KB is the firmware's upper RAM (settled); only the docking copy was not re-measured | The launch direction was measured; docking rests on the earlier 2026-11-07 measurement and the source | snapshot before and after a real docking | `_memory_map.md` |
| ISR worst-case stack depth: which top bytes of the `&9D9E-&9FFF` tail are safe? | Unmeasured; only `&9FFE-&9FFF` is known to be hit | write watch on the tail over a long session | `_architecture.md` |
| Disc fill on the unclamped screen path (`ce2func46`, charts) and for radii under 9 | Not covered by the 131,072-input sweep of the in-flight path | extend `tools/circle_sweep.py` | `_architecture.md` |
| Does the whole mission chain play through, with save and load? Are the tuning values right (20 asteroids, 50% and 22% spawn rates, Birera as the police target, 4,000/5,000/6,000 Cr)? Do the Constrictor's ECM and missiles work? | Everything is tested with forced states and direct calls; nothing was played through. The stock-mission pokes and trainer stages 2 and 3 were not run end to end | a real playthrough on `work/missions_cheat.dsk` | `_missions_built.md` |

Not built, by decision: French `TITLESEL`, `--fr` disk builds, hiding stars behind ships (`_ship_occlusion.md`), a random per-commander mission order (no room), the escape-pod clear fix, furs when Trumbles die in a sun (`TODO.md`).

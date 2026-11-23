# Contributing

This repository is a disassembly of the Amstrad CPC *Elite* and a modified build made from it, for study and for building your own disk from your own copy of the game. Bug reports, fixes to the source, the tools and the docs are welcome.

**Not accepted, in a pull request or an issue attachment:**

- game files: disk or tape images, extracted binaries, snapshots or RVM states (they contain the original game's memory)
- third-party source or data: other versions of *Elite*, ArcElite tables, anything from Fessor's archives
- the names or descriptions of the added missions in `README.md` (they are meant to be found by playing)

**Before you open a pull request:**

1. `git config core.hooksPath scripts/hooks` (a pre-commit hook that refuses game files and mass deletions).
2. `make check` must pass: the 64K source has to assemble to the original bytes. Changes sit behind flags (`docs/_build.md`, "Switches").
3. `make test` for code changes; `make test-emu` needs cpcxray (`docs/_build.md`).
4. Update the doc that states the fact you changed.

Every pull request is reviewed by the owner before it is merged. A contribution is under the licence of the files it touches (`LICENSE`, `NOTICE`).

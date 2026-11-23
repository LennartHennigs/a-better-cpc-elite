---
name: release
description: Build the 64K and 128K disks from a clean pushed commit, check them, and publish two GitHub releases on origin. Use only when the user asks for a release.
disable-model-invocation: true
---

# Release the 64K and 128K disks

Two releases per run, one disk each (`LennartHennigs/a-better-cpc-elite`). The disks contain the game's bytes, which `NOTICE` does not allow to be redistributed: never make the repo public, and tell the user if it is.

Git is slow here (iCloud, full disk): run every git and `gh` command in the background, redirect to a scratchpad log (`cmd > LOG 2>&1; echo rc=$?`), and read the log; never judge by `| tail` or "completed (exit code 0)".

1. **Clean and pushed.** `git status --short` is empty (an unrelated edit of the user's: leave it, tell them, and check it does not touch the disks), and `git rev-parse HEAD` equals `git rev-parse origin/main`. If HEAD is not pushed, stop and ask: pushing is the user's call. Note `SHA=$(git rev-parse HEAD)`.
2. **Build and host checks.** `make expanded` (`build/elite64.dsk`, boot `RUN"ELITE64`), `make disk6128` (`build/elite128.dsk`, boot `RUN"ELITE128`), `python3 -I tools/tests/run_all.py --host`. All three must report rc=0 and 5 of 5 passed; do not edit `src/` meanwhile.
3. **Boot both disks** in cpcxray: copy them into `work/xray/disk/`, then from `work/xray` run `~/.local/share/uv/tools/cpcxray/bin/python -I ../../.claude/skills/release/boot_check.py disk/NAME.dsk ELITE64 output/rel64.png` (and `ELITE128` for the other). Look at both PNGs: each must show the title with "Load New Commander (Y/N)?" (64K wireframe ship, 128K filled ship). `make test-emu` (about 4 minutes, in the background) is the thorough option; offer it, do not skip the boot check.
4. **Tags.** `elite64-YYYY-MM-DD` and `elite128-YYYY-MM-DD` (today's date); on a second release the same day append `-2`. Check `gh release list` first: never reuse or delete a tag without asking.
5. **Notes** (one file per release in the scratchpad): what the disk is, the boot command, the commit (7 characters), the `make` target, what was checked and that it was not played through, the SHA-256 (`shasum -a 256`). No mission names or descriptions (`README.md` rule). The 128K says: 6128 only, a 464 or 664 shows "128K CPC (6128) REQUIRED".
6. **Create:** `gh release create TAG build/DISK.dsk --target $SHA --title "Elite 64K (DATE)" --notes-file FILE` and the same for 128K with `--prerelease` (while `README.md` still calls it a preview; drop the flag when it does not). `--target` the SHA, never a branch name.
7. **Record it.** `gh release list` to confirm both; update the "Releases" lines of the Remote bullet in `CLAUDE.md` (tags, commit, SHAs unchanged otherwise); commit that alone with `git add CLAUDE.md`, no attribution trailer. Do not push without being asked.

Report the two release URLs, what was checked, and what was not (no hand play-through unless the user did one).

# Open items, full text

The one-line items in `TODO.md` link here. Moved unchanged; edit both when the status changes.

## Ship packs

Ship packs (`docs/_ship_packs.md`): play through a few jumps and launches (pack mix, 2 s load after a jump, asteroid crowding with `-DTRAFFIC`); try hiding the pack load (load at the end of `DockingSequence`, or chunked during the launch tunnel); Boulder and Transporter do not fit yet; check the new hulls' role flags and kill values against the C64 table.

## Added missions, English only

Added missions (Constrictor, plans, stolen ship, asteroids, Trumbles) are English only: no translated texts, and the mission disk and hooks are built only from `src/elite` (`build_dsk.py --missions` refuses `--de`/`--fr`). The biggest gap between the builds. Suggested: port the texts to German first, then French (same free-space limit as the flight images; the overlays carry the text).

## Write-protected save

Save on a write-protected disk resets to BASIC (seen in RVM on the mission disk). The game's own hook only catches AMSDOS's "Retry, Ignore or Cancel?" message (`LAB_ram_855e`, `checkMedia`); whether the stock game behaves the same, and what a graceful handler would cost in bytes, is untested (needs a clean boot in cpcxray on a read-only disk; `firebird_at_entry.sna` is not valid for disk-menu tests). Suggested: catch the AMSDOS error in `checkMedia` and return to the menu; measure the byte cost in the flight image first.

## Legal status number

(deferred 2026-11-16: no room in the mission build, left for now) Legal status number on the status line ("Status: Offender - 25"): a shared printing routine plus two small entries, about 14 bytes more in the head of every flight image; the images have 0 to 2 bytes left (2026-11-15), so it fits only without `-DMISSIONS` (about 450 bytes free in the tail) or after dropping the Trumble squeak (17 bytes, Trumbles only) and more in the packs. Also open: the kill count and the status number in German and French (spacing, width of the longer labels).

## Laser sights on the mission disk

Laser sights on the English mission disk: `-DENHANCED -DMISSIONS` keeps the stock cross because the sights (108 bytes) do not fit beside the flight images (about 13 bytes short after the cuts that keep the missions as they are; measured launch-table cut: 2 bytes per image; see `docs/_my_changes.md` "Laser sights"). Needs space in the `COMMONXX` tail (images T 608, packs 1/2 606/604, C 606 of 608 since the kill count) or a hull less in packs 1 and 2. The French sights are untested in an emulator (the German ones were played by hand). Suggested: move the sights into an overlay, or drop a hull from packs 1 and 2 to make the 108 bytes.

## Real playthrough

Real playthrough of the whole chain with save and load (so far only forced states, direct calls, the trainer pokes and a booted disk). A real docking triggering each offer has not been seen in the running game. Suggested: script it with cpcxray from `firebird_in_flight.sna`, forcing each offer by docking, saving a snapshot at each step.

## Furs when the Trumbles die in a sun

Optional: furs when the Trumbles die in a sun. Idea: when the sun brings the count to 0, add a fixed 4 t of furs (good 11, `cargoHold+11`), capped by `cargoSpaceFree`. Costs about 24 bytes in `mxSunImpl` (Trumbles image has 8 spare, limit `&9FFE`), so 16 bytes must be freed: cutting the sprite from 14 to 10 rows does it (drop rows 0, 6, 12, 13 of `missions_trumble_art.txt`, `ld c,10` in `mxBlit`). Once per commander (the offer is made once), so no trading exploit. A scaled amount (peak count) needs a stored byte and more space. Also a death sound for the sun: reuse an existing effect via a bit in `sfxFlags2Bitmap` (about 5 bytes), pick by ear with `TRUMBLE.BAS`.

## Hull dedup

Hull dedup behind `-DENHANCED`/`-DMISSIONS` (default keeps the original bytes): point the Splinter header's edge offset (`shipdatSplinter` +14) at `shipdatCapsule`'s edge block and drop the duplicate 24 bytes; move the later hulls down so the free tail grows by the same amount. Check the Splinter and Capsule faces and all other sub-blocks for partial overlaps first (only whole equal blocks were compared; Cargo/Pirate1/Thargon differ). Risks as in the hull compression item: shifted tail addresses, `check_src.sh` marker, all three trees, `tools/tests/test_flight_hull.py` per ship.

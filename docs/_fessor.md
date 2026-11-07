## Fessor's source and symbols (downloaded 2026-11-07)

The downloaded files (archives, source, symbols, forum pages), their layout and handling caveats are described in
`extended/CLAUDE.md`; our comparison with the stock game is in `extended/FESSOR_VS_STOCK.md`. Not for re-upload.
Key facts: `symbolsEnglishVersion.asm` (157 symbols, posted 2021-07-22, post 205120) is correct for the stock English
game (287 call/jump references in the stock binaries, 10 in his patched build), so use it as ground truth. The beta disk
`ELITE_EXT.DSK` uses `P`-suffixed files and `SHIPSETA`-`P` (load `&8DDE`).

What the source is:
- Header: Ghidra 10.0.1, "RASM 1.5", reconstructed Z80 source for LARGEAXX (`&0840`), COMMONXX (`&1A40`),
  COMMON2X (`&C000`). 2451 labels, 474 named by hand, the rest Ghidra names (`LAB_ram_xxxx`).
- Build switches at the top of `EliteMasterSource.asm` (`defextendenddisk`, `defmovegfxtable`,
  `defdeactivate*`, `defmylinedraw`, `defadresschange` and others). Default settings give the patched build.
- It assembles with RASM 3.3.2 with no changes (`tools/bin/rasm EliteMasterSource.asm -s -sq`), writing
  `LARGEAXP`, `COMMONXP`, `COMMON2P`, `NOTMUSIP`, `SHIPSETB` and `rasmoutput.sym`. The result **is
  byte-identical** to the beta disk once the 128-byte AMSDOS header is stripped: `LARGEAXP`, `COMMONXP`,
  `COMMON2P`, `NOTMUSIP` and `SHIPSETB` all match `work/bin_ext/` (checked 2026-11-07). The beta disk is this source.
- It **cannot rebuild the stock binaries** by switching everything off: 4 to 8 errors remain
  (`SETUPSPLASH2SHIP`, `LAB_ram_5958` are only defined in some switch combinations). A byte-exact stock
  rebuild would need hand edits. The author says unused code was deactivated to gain space, and that the
  original binaries were made from a running state (variable areas hold stale values).
- Savegame crypt: the stock game en/decodes saves with a routine over its own code, so any code change breaks
  saves. Fessor's builds key it on the string-token table instead.

### Mapping Fessor's names onto the stock binaries

Fessor's code is shifted against stock (typically by 16 to 400 bytes), so absolute operands differ. Tools:

- `tools/dskx.py IMAGE.dsk [OUTDIR]`: lists a DSK's AMSDOS files with header load/exec/length and extracts
  them (read-only, standard and extended DSK). Stock binaries are in `work/bin_stock/` (header stripped) and
  in `work/stock_bin/`; the beta's are in `work/bin_ext/`.
- `tools/map_labels.py`: takes the labels from `rasmoutput.sym`, masks all 16-bit operands in the first
  14, 24 or 40 bytes of each, searches the stock image and keeps unique matches as anchors (dropping
  any that break address order). Other labels are placed from the nearest anchors: ambiguous hits are
  narrowed to the one between the anchors, and a label between two anchors with the same offset gets
  that offset. Run:
  `python3 -I tools/map_labels.py work/build_fessor work/build_fessor/rasmoutput.sym work/stock_bin work/fessor_to_stock.sym extended/symbolsEnglishVersion.asm`
  (add `--eval` to hold out the known names and score the method instead of writing the file).
- Result `work/fessor_to_stock.sym`: 157 stock symbols (authoritative) plus 2,107 matched labels whose
  names are not in the stock file: 2,020 `exact`, 54 `delta+bytes`, 3 `bracket`, 30 `delta` (offset only,
  weakest). The tag is on each line. In all 2,192 of the 2,623 patched-build labels were placed. 431 labels stay unresolved: about 300 are variables and zero-filled data
  (entity slots at `&1A40`, flags, buffers) with no code bytes to match, and about 130 are code Fessor
  wrote or rewrote (splash screens, `Init`, savegame handling, fade routines) that does not exist in stock.
- Hold-out test (`--eval`): of the 112 labels whose names are in the stock symbol file, the method placed 85
  and got 83 right (97.6%); 27 stayed unresolved. The 2 wrong ones were a `bracket` and a `delta+bytes`.
- Checks: of 83 names present in both Fessor's source and his stock symbol file, 81 matched at the right
  address (first version of the matcher); the 2 wrong ones (`ClearScreen`, `ColorsBuyGoods`) are overridden
  by the stock symbols. The `CHEAT.BAS` pokes also land in the right routines:

| Cheat | Address | Label in the map |
|---|---|---|
| Infinite fuel | `&4F02` | `SetFuel+3` |
| Shield damage | `&35CB` | `TODO_ShipTakingDamage+4` |
| Infinite missiles | `&382D` | `LaunchSuccessfull+0xA` |
| No hyperspace limit | `&4C08`, `&4C12` | `TryHyperspace+9`, `+0x13` |
| No laser temperature | `&7A4F` | `AddLaserTemp+8` |
| One hit destroys | `&7AA8` | `ApplyLaserDamageToEntity+0x15` |
| Energy bomb | `&2F6A` | `ChkUseEnergyBomb+0xB` |
| Cloaking patch | `&4902`, `&4908` | `LAB_ram_48FB+7`, `+0xD` (just before it, `FindPlanet+0x1F` at `&4096`) |

  This supports the "one-byte instruction removed" guess for the zero pokes, but the exact instructions
  are still to be read from the disassembly.
- Treat `delta` and `bracket` labels, and the ~2% of possible false matches, with care: verify by looking at
  callers before trusting a name.

## Findings from the Fessor thread

Post links: `https://www.cpcwiki.eu/forum/index.php?msg=<id>`.

Key posts: 205077 (start), 205120 (ship defs, symbol table), 205954 and 205998 (RASM source v1/v2),
206103 (shipset loader), 206679 (**first beta**, 2021-09-04), 239964 (status 2024-05-23), 240962 (stack bug).

## Beta (2021-09-04) and later state

- Beta changes: new splash screens 1 and 2 (2 is a ship showcase), BBC-disc-style shipset reloading,
  shipset recorded in the savegame (incompatible with stock saves), savegame encryption off, about 1000
  bytes freed by commenting out unused code. Works on 64K machines.
- Shipset loader (post 206103): `getRandomNumber AND 3`, plus 1 bit from government (<3 carry) and 1 bit
  from tech level (<10 carry), giving a file suffix `A`..`P`. Ported from
  https://www.bbcelite.com/disc/flight/subroutine/lships.html.
- Known bugs: showcase crashes after a while (stack left broken when SPACE breaks the djnz loop;
  Fessor said it was fixed, then in 2024 said the intro changes should be undone).
- 2024-05-23: Fessor lost motivation; 128K double buffering never worked (screen move from bank 3 to
  bank 1 failed). 2024-06: most graphics functions work against screen RAM at `0x4000` except line
  drawing; double buffering "works so far" on 2024-06-30 (R12/R13 toggled 0x4000/0xC000 in the vsync
  interrupt). Dashboard redraw and the rupture/colour-split interplay were unsolved. Last Fessor post
  2024-06-30 about the project; thread ends 2024-08-06.
- Roadmap Fessor listed: undo intro changes, relocate code for double buffering, CPC line draw, CPC
  circle draw (with clipping), German/French localisation. Idea for music (Arkos) needs freed RAM.

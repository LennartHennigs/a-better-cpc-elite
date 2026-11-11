# Filled ships (polygons) on a 6128: prototype and findings

Status 2026-11-11: the fill is in the game in the 128K fork (`src/elite128/fill.asm`, bank 6; hulls from `tools/ship128.py`; `src/elite128/README.md`); `src/elite` (64K) has none. The text below is the 2026-11-10 analysis and the prototype: a standalone prototype exists. This file keeps what the prototype measured, what it showed about the 128K banks, and what it would take to put filled hulls into
`src/elite/`. The prototype lives in `tools/proto_fill/` (`gen.py`, `fill.asm`, `flip.asm`, `run.py`, `mkdsk.py`); its data is generated into `work/proto_fill/` and stays out of the repo (see "ArcElite data" below).

## What the prototype is

Two standalone programs for a 6128, written for sjasmplus, run with `python3 -I tools/proto_fill/mkdsk.py` giving `work/proto_fill/proto.dsk`:

| File | What it does |
|---|---|
| `PROTO.BIN` (`fill.asm`) | One turning Cobra from filled, dithered triangles. Triangle data and fill code in RAM bank 4, paged in at `&4000` per draw. Draws on the visible screen, erases only the old bounding box. |
| `FLIP.BIN` (`flip.asm`) | The same, double buffered with a page flip, and 15 ships chosen with cursor left/right. Start with `RUN"FLIP.BIN`. |

Both do a RAM check first (write `&A5` at `&4000`, write `&5A` with bank 4 mapped, read back): a 464 or 664 ignores the banking port, reads `&5A` and gets a red bar instead (tested on cpcxray's 664 config).

## ArcElite data (third party, `work/` only)

- Source: Ian Bell's ship tables as C text (`work/arcelite/x_ships/B5052480.C`, see `_arcelite.md`). Each ship is `points` plus `facets`; a facet is `{v0, v1, v2, colour, n}`: **triangles only**, wound anticlockwise from outside, colour 0-255 baked per face, 47 base hulls, 788 triangles, 27 of them with a `FAR...` low-detail twin (Cobra 26 -> 18 triangles).
- The fifth number `n` counts the facets of the same plane that follow (8,7,...,0). Drawing such a group together **in list order** fixes the decals (the Cobra's exhaust triangles) that a pure depth sort put under the base polygon (a z-buffer comparison showed about 970 wrong pixels over the frames; groups sorted far to near, members in list order, remove them).
- The prototype uses the 15 models the CPC has (`_architecture.md`: 14 blueprints plus the splinter): Cobra Mk III, Viper, Sidewinder, Python, Asp, Fer-de-Lance, Krait, Thargoid, Thargon, Coriolis, escape pod, canister, missile, asteroid, splinter. The numbering and shapes are ArcElite's, not the CPC's.
- Do not copy the table into the repo. `gen.py` regenerates everything under `work/proto_fill/`.

## How it works, step by step

### Start (`flip.asm`)

1. `RUN"FLIP.BIN` loads one 36 KB file at `&1000`: 15 ships (1,824 bytes each, ship n at `&1000 + n * 1824`) up to `&7AE0`, the program at `&8000`.
2. While the firmware is alive: switch the lower ROM on (`KL L ROM ENABLE`), copy the ROM font (characters 32-127, 768 bytes) to `&9D00`, print a message through the firmware.
3. RAM check (see above). No second 64 KB: red bar and stop.
4. `copyShips`: each ship goes through the buffer at `&8800` into bank 4 (ships 0-7) or bank 5 (8-14): copy to the buffer in the normal map, `out (&7Fxx)` config C4 or C5, copy from the buffer to `&4000+`, back to C0. (A ship at `&4000-&7FFF` sits in bank 1, which a mapped bank hides, so it cannot be copied straight.)
5. A few seconds with interrupts on (the firmware switches the disc motor off), then the program takes over: ROMs off, mode 1, our own palette, `jp isr` at `&0038`, both screen pages cleared.
6. Build the module: map bank 7 at `&4000` (config C7), copy the module (539 bytes) there, run `initBank`, which writes the tables the module needs (edge block, column/mask tables, quarter squares, reciprocals) into the same bank. Bank 7 is also what C1 and C3 show at `&C000`, so the same bytes appear at `&C000` while drawing.

### One frame

```
                   +--------------------------- main RAM (bank 2, always visible) ---------------------------+
 cursor keys  -->  | readKeys (PPI) -> new ship? -> loadShip (bank 4/5 -> &8800), erase both pages, name text   |
                   | draw page = V_PIX: config C1 (bank 1 at &4000) or C3 (bank 3 at &4000), bank 7 at &C000    |
                   | clearBox   erase the bounding box this page showed two frames ago                           |
                   | call &C000 -> drawShip (bank 7): for each face in the frame's order list, fill the polygon  |
                   | remember this frame's box for the page                                                      |
                   | wait for vsync, write CRTC R12 = &10 / &30 (show the page just drawn), V_PIX ^= 1          |
                   +---------------------------------------------------------------------------------------------+
```

- **What a frame contains.** In the prototype the host computes the projection: per frame 104 bytes of `x[32]`, `y[32]`, the visible faces in draw order (far to near, coplanar groups kept together) and the bounding box. In the real game the engine would provide projected vertices and visible faces; only the fill would be new.
- **Why two pages.** The page on screen is never touched. The CPU draws at `&4000` either into bank 1 or bank 3 (the pages the CRTC reads at `&4000` and `&C000`), so one set of row addresses serves both.
- **Why bank 7 at `&C000`.** The module needs to be visible during drawing, and `&4000` is where the draw page appears. C1 and C3 both show bank 7 at `&C000`, so the call is a plain `call &C000` with no switching around it.
- **`PROTO.BIN`** differs only in the draw target: it draws on the visible screen at `&C000` through a module paged in at `&4000` by `drawShipTramp` for each ship (config C4 around the call), with the interrupt guard.

### Filling one polygon (`fillTri`)

```
 vertices in screen pixels:        edge walk, one table per side:         spans, per line y:
      A                                x: 8.8 fixed point per line          left  = XL[y]  -> byte column, left mask
     / \             down edges --> XR[y]   up edges --> XL[y]                right = XR[y]  -> byte column, right mask
    /   \            (clockwise)                                              write left byte, bytes between, right byte
   C-----B                                                                    pattern byte chosen by line parity
```

1. Take the three vertices (`x,y`) from the frame; find `ymin` and `ymax`.
2. For each of the three edges, order it top to bottom. If it goes down, its x values go into one table, if it goes up, into the other (visible triangles all wind the same way on screen, so this is always left or right consistently). Flat edges are skipped.
3. The slope is `|dx| / dy` in 8.8: one lookup of `65535/dy` and two quarter-square multiplies (`a*b = sq[a+b] - sq[|a-b|]`, tables built at start).
4. The walk is an unrolled run of `ld a,h / ld (de),a / inc e / add hl,bc` (`HL` = x in 8.8, `DE` = table page and line, `BC` = slope), entered at the line count by `jp (iy)` so the `ret` at the end of the block ends it.
5. For every line from `ymin` to `ymax`: read both x values, look up byte column and the two masks by x, find the line's address from the row table, and write `((old xor pattern) and mask) xor old` into the partial end bytes and the pattern into the whole bytes between. Even and odd lines get different pattern bytes (the dither).
6. Triangles are drawn far to near, so near faces overwrite far ones (painter's algorithm).

### The selection screen

- Name and hint are drawn with the ROM font: each glyph row (8 pixels) becomes two Mode 1 bytes, a nibble `n` giving the byte `n * 17` (pen 3 where the pixel is set), 8 rows `&800` apart.
- A new ship sets both pages' boxes to the whole view (so two frames erase everything), resets the frame counter and draws the name into both pages over the next two frames.

## The fill in short (and why)

- One pair of 256-byte edge tables (left, right edge per scanline). With back-face culling every visible triangle winds the same way on screen, so downward edges all go into one table and upward edges into the other: no init, no min/max compares.
- Each edge steps x in 8.8 fixed point through an unrolled block (`ld a,h / ld (de),a / inc e / add hl,bc`, 26 T-states a line) entered at the line count with `jp (iy)`. The slope is `|dx| * (65535/dy) / 256` from a reciprocal table and two quarter-square multiplies.
- Spans: byte column and end masks by table lookup (page-aligned, indexed by x), masked first and last byte, a plain loop for the bytes between (average span is only about 2 bytes, so unrolling it did not pay). Two passes (even lines, odd lines) keep the dither pattern constant.
- Mode 1 has four pens, so shading is three pens plus dither patterns (solid 1/2/3, and the 1/3, 2/3, 1/2 checkers), brightest first.
- Ideas from the web (`vector_filled.z80` in Dean Belfield's lib-spectrum, mcejp's edge-walk article): the same edge-table-plus-span design, Bresenham edges, page-aligned tables, an unrolled span block entered by computed jump. PUSH fills need interrupts off, which the colour-split interrupts do not allow.

## Measured (cpcxray, one close Cobra, 11.4 visible triangles, about 2,500 pixels a frame)

| Version | Draw time per frame |
|---|---|
| first (division per edge, min/max tables) | 66 ms |
| one table per side, unrolled edge block, lookup tables | 47 ms |
| reciprocal + quarter squares, two-pass spans | 44 ms |

- Fixed cost: about 1.1 ms a triangle (about 13 ms a frame), measured with 4x4-pixel triangles. The rest, about 31 ms, is about 160 microseconds a line.
- Clearing the whole view with `LDIR` took 54 ms; erasing only last frame's bounding box takes 8 ms and halves the frame time (about 100 -> 53 ms).
- Page flip (`flip.asm`): frames come at multiples of 20 ms (mean 62 ms), the displayed page is never drawn into.
- A frame of the game is about 240 ms (`_architecture.md`), so one close hull is about +18%. Several ships or a ship filling the view cost much more. All numbers are emulator timings.

## What the 128K banks gave and cost

- The CRTC shows only banks 0-3; banks 4-7 can hold code and data, never a screen (`_memory_map.md`).
- **Window at `&4000` (`PROTO.BIN`):** configs C4-C7 map bank 4-7 at `&4000-&7FFF`, hiding whatever is there. The 300 Hz interrupt must not call into the hidden range: with the sound call into `&6000` and no guard, the CPU ran into bank 4's empty bytes, slid through the NOPs to `&8000` and restarted the program. A flag test in the handler fixes it.
- **Page flip with bank 7 at `&C000` (`FLIP.BIN`):** C1 (banks 0,1,2,7) and C3 (0,3,2,7) show bank 1 or bank 3 at `&4000` for drawing and bank 7 at `&C000` for the code and tables; R12 `&10`/`&30` shows the page just drawn after the vsync. The module needs no per-call paging, and the stored row table has the same base for both pages. This is the arrangement of the earlier double-buffer experiment (`docs_other/_double_buffer_experiment.md`).
- Loading from disc: a program started with `RUN"X.BIN` found the firmware's cassette vectors selected in cpcxray (`CAS_IN_OPEN` asked for "Press PLAY"), and `|DISC` was not found, so the ship data are part of `FLIP.BIN` itself (one 36 KB file from `&1000`, several extents, which needed multi-extent support in `tools/dskx.py`) and the program copies them into banks 4 and 5. A BASIC loader (as `ELITE.BAS`) still has the disc routines.
- RUN also starts a program with the lower ROM off: reading the ROM font needs `KL L ROM ENABLE` (`&B906`) first.
- Keyboard: with the firmware's interrupt gone, cursor keys are read straight from the PPI (line 0 bit 1 right, line 1 bit 0 left).

## Memory today and what the game would need

| Resident main RAM free | |
|---|---|
| 3 bytes after `cashHome` (`&1FEA`), two 5-byte pockets (`&204E`, `&2053`) | about 13 in all |
| `&9751-&97A0` | 80 bytes of filler, not verified |
| flight tail `&9D9E-&9FFE` | 610 minus the mission flight image (0 spare with Constrictor, 8 with Trumbles) |

Banks 4-7 are 64 KB the game does not use.

| Needed | Where | Size |
|---|---|---|
| fill module, edge block, column/mask tables, squares, reciprocals, edge tables | bank 7 (at `&C000` under C1) | 539 bytes of code plus about 2.8 KB of generated tables |
| face data of the 14 CPC ships | same bank | estimated under 1 KB (not counted) |
| glue: `ld bc,&7FC1 / out (c),c / call &C000 / ld bc,&7FC0 / out (c),c / ret` | main RAM | 14 bytes |
| hook: one 3-byte `call` before `todo_parseEdges` | `commonxx.asm` | 0 new (replaced bytes) |

## Fitting it into `src/elite` (analysis only, nothing built)

- **Draw target.** The game draws into the off-screen bitmap `&A000-&BFFF` (64 bytes a line, always visible), so the fill needs no page flip and no relocation. Page flipping the game needs the code at `&4000-&7FFF` and `COMMON2X` moved into bank 7, which is the large job the double-buffer experiment found.
- **Config C1** keeps bank 1 visible, so the game code at `&4000-&7FFF` stays mapped while bank 7 sits at `&C000`. The interrupt region (`myVBL` onward) references nothing in `COMMON2X` (`&C000+`), so no interrupt guard should be needed; deeper paths (sound, keyboard) were not traced.
- **Engine data to use.** Projected vertices are in `buf_5860`, 3 bytes each: x, y, flags (bit 7 = off view); `lookup_vertex_coords` reads them. The face-visible table is `todo_tableforedges` (`getEntryfromTable`). The engine already drops edges with an off-view vertex, so a face with such a vertex would simply be skipped.
- **Face loops.** ArcElite's vertex numbers do not match the CPC blueprints, so a tool must chain each CPC face's edges (`v1, v2, face1, face2`) into a vertex loop. The fill then walks polygon edges directly, no triangulation.
- **Colour.** The view background is pen 1; which inks the palette splits give pens 2 and 3 was not checked. Plan for three tones with dithering.
- **464.** Detect the second 64 KB at start; patch the glue's first byte to `ret` when absent. The default build must stay byte-exact: a `-DHULLFILL`-style switch with the same proof as `STAR_OCCLUDE` in `check_src.sh`.
- **Loading the module.** The module image (small file) is loaded by `ELITE.BAS` while the disc routines are alive, then copied into bank 7 under config C7 from code below `&4000`.
- **Saves.** Nothing in `LARGEAXX` changes, so the save key window stays untouched.

## Risks and open points

- The 14-byte glue does not fit one pocket: use `&9751-&97A0` after verifying it, or chain with `jp`.
- Speed: 44 ms a close ship in this form; level of detail (a coarse hull or no fill for distant ships), merged coplanar faces and no sorting for convex hulls would be the first savings.
- Concave hulls (Python, Thargoid?) could show wrong overlaps without grouping or sorting.
- Not tested: RVM, a real keyboard, a real 6128, the disc motor after the program takes over (the prototype waits a few seconds with interrupts on).

## Suggested order

1. Tool: CPC blueprint edges to face loops, checked for planarity and winding.
2. Module on a flight snapshot in cpcxray with an injected call (as `tools/test_flight_hull.py`).
3. Glue, hook, 464 fallback, flag, `check_src.sh` proof.
4. Palette and shading; then level of detail.

# Stars behind ships (idea, not built)

Stars already stay behind the planet and sun (`STAR_OCCLUDE`, `dustPlotPixel`, see `changelog_archive.md`). Ships are still
see-through: stars show between their edge lines. Options for hiding them:

## Why ships are different

- `todo_parseEdges` draws each visible edge as a line through `SUB_ram_7c45`. Nothing else is drawn, so no pixel inside the
  hull is written.
- `Spaceflight` draws `ClearBitmap`, `drawPlanetnSun`, `DrawSpaceDust`, `handleEntitys`. Dust comes before ships, so nothing
  in the buffer says "inside a ship" when a star is plotted. The planet fix worked because the disc is already in the bitmap.
- Options A and B therefore move `DrawSpaceDust` after `handleEntitys`, in `Spaceflight` and in the death loop
  (`LAB_ram_1e8d`). Planet and sun keep working, because `dustPlotPixel` plots only on background pixels.

## Options

| | Cost | Result |
|---|---|---|
| **A. Silhouette per scanline** | about 350 bytes: a 128-row table (about 256) of leftmost/rightmost x per scanline, plus a DDA (about 100) walking each edge, roughly 30 edges per ship | Exact, opaque-looking hulls; concave hulls (Thargoid, wings) hide a few stars in the notches |
| **B. Bounding box per ship** | about 80-100 bytes: `pvLoop` already projects vertices, so keep min/max x and y per ship; `dustPlotPixel` skips stars inside a box | A star-free rectangle, larger than a rotated hull; a large close ship blanks a visible patch, a few missing stars among 20-40 go unnoticed |
| **C. Filled hulls** | big rewrite of the draw path (per-face fill, sorting), as on ST and PC | Not recommended |
| **D. Leave it** | none | Matches the original wireframe look |

## Constraints

- **Space.** `unusedViewBorderFill` (`&1FD2-&1FF0`) holds `dustPlotPixel` and has 20 bytes left (`&1FDD-&1FF0`);
  `unusedGetFlightMode` and `unusedGetCloakFlag` give 10 (used by `killSpace` since 2026-11-15). The `&9D9E` tail has 610 bytes, but `-DMISSIONS` builds fill it
  with mission images and the Constrictor flight image has none spare. A does not fit without moving its table (overlay or
  screen-gap memory); B might.
- **Check.** `tools/check_src.sh` needs a second switch with the same proof as `STAR_OCCLUDE` (off = original bytes, on
  differs only inside its slots), ported to `src/elite_de/` and `src/elite_fr/`.

## Recommendation

Try B first, after measuring how many free bytes the missions build leaves. If the box looks wrong in play, look at A with
its table moved out of the tail.

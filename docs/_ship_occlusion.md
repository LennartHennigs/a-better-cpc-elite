# Stars and ships: making hulls opaque (idea, not built)

Status 2026-11-08: the stars already stay behind the planet and sun (`STAR_OCCLUDE`, `dustPlotPixel`, see `CHANGELOG.md`). Ships are still
see-through: stars show between their edge lines. This note records the options for hiding stars behind ships.

## Why ships are different

- `todo_parseEdges` walks a ship's edge list and draws each visible edge as a line through `SUB_ram_7c45`. Nothing else is drawn for a ship, so no
  pixel inside the hull is ever written.
- `Spaceflight` draws in this order: `ClearBitmap`, `drawPlanetnSun`, `DrawSpaceDust`, `handleEntitys`. The dust comes before the ships, so when a
  star is plotted nothing in the buffer says "inside a ship". The planet fix worked because the disc is already in the bitmap at that point.
- Both options below therefore move `DrawSpaceDust` after `handleEntitys`, in `Spaceflight` and in the death loop (`LAB_ram_1e8d`).
  Planet and sun keep working, because `dustPlotPixel` plots only on background pixels.

## Options

**A. Silhouette per scanline** (exact, opaque-looking hulls, about 350 bytes)
- Hook the edge routine to record the leftmost and rightmost x of every scanline the ship touches: a 128-row table (about 256 bytes) plus about
  100 bytes for a DDA that walks each edge.
- `dustPlotPixel` skips a star whose x lies inside a ship's span on its row.
- Concave hulls (Thargoid, wings) hide a few stars in the notches. Cost: one DDA per edge, roughly 30 edges per ship.

**B. Bounding box per ship** (cheap, about 80-100 bytes)
- The vertex projection loop (`pvLoop`) already computes screen coordinates. Keep min and max x and y per ship, a few bytes each.
- `dustPlotPixel` skips stars inside any ship's box.
- Result: a star-free rectangle around each ship, larger than the hull when it is rotated. With 20-40 stars on screen a few missing ones are hard
  to notice, but a large close ship blanks a visible patch.

**C. Filled hulls** (not recommended)
- Draw faces solid like the ST and PC versions: a big rewrite of the draw path with per-face fill and sorting.

**D. Leave it.** Wireframes with stars between the edges match the original look.

## Constraints

- **Space.** The dead block `unusedViewBorderFill` (`&1FD2-&1FF0`) now holds `dustPlotPixel` and has 20 bytes left (`&1FDD-&1FF0`); `unusedGetFlightMode` and
  `unusedGetCloakFlag` give 10. The `&9D9E` tail has 610 bytes, but the `-DMISSIONS` builds fill it with mission images and the Constrictor flight
  image has 1 byte spare. A does not fit without moving its table (overlay or screen-gap memory). B might fit.
- **Check.** `tools/check_src.sh` needs a second switch with the same proof as `STAR_OCCLUDE`: off gives the original bytes, on differs only inside
  its slots. Port to `src/elite_de/` and `src/elite_fr/`.

## Recommendation

Try **B** first. Before that, measure how many free bytes the missions build really leaves. If the box looks wrong in play, look at A with its table
moved out of the tail.

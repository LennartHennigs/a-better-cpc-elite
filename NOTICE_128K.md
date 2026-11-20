Elite 128K (branch `elite128`): what is not covered by the licences in LICENSE

Addendum to NOTICE (on `main`). When this branch is merged, these items move into NOTICE as items 6 to 10. Everything in NOTICE applies here too: Elite is copyrighted by its authors and rights holders (David Braben and Ian Bell; the CPC version was published by Firebird in 1985), this project is not affiliated with them and holds no rights to the game.

1. The 128K game source (src/elite128/, apart from the files named in 2, 3 and 4)
   It is the disassembly of NOTICE item 1 laid out for a 6128: the code block moved to RAM bank 7, the screen page moved to &4000, the loaders changed. The names, labels and comments are mine, but they cannot be separated from the code, which stays under the original copyright. It is published for study and preservation: you may read it, learn from it and build it for your own use from your own copy of the game. No licence is granted beyond that: nothing here allows redistributing the game, the source, or disks built from it. Ask the rights holders, not me.

2. The code written for the 128K build (src/elite128/fill.asm, fill_tt.asm and the glue in src/elite128/commonxx.asm: hullDraw, bankInit, the page flip, the disc trampolines)
   It is my own work, but it only runs inside the original binary. It is treated like item 1: no licence is granted. The scripts around it (tools/ship128.py, hullfill.py, check_src128.sh, listing6128.sh, build_dsk128.py, test_*128.py and the other tools for this build) are code written by me and fall under the MIT licence of tools/ in LICENSE, with the exception in 3.

3. The filled ships made from the game's own blueprints (the default build, `HULLS=stock`)
   tools/hullfill.py is my code, but what it works on and what it produces are the game's: the vertices, edges and face normals of the stock blueprints (item 1) become triangles, dither patterns and a few details of my own (the Cobra's windscreen, the Sidewinder's canopy and wing trim, the Viper's canopy). The generated files (work/elite128/shipdata128.asm, fill128.bin, fill128_late.bin, hull_constrictor.asm), the disks and the listing made from them are treated like item 1: no licence is granted.

4. The Constrictor (src/elite128/missions_hull.asm and the generated work/elite128/hull_constrictor.asm)
   It is based on Fessor's Constrictor hull (NOTICE item 3, used with his permission): his header and, in the default build, his vertices, with triangles built from his edges and faces. It is not his file as it was: the edges and faces are dropped and the triangles are mine. No licence is granted beyond NOTICE item 3.

5. Material derived from ArcElite (only with `HULLS=arcelite`)
   The original look of this build draws the filled hulls from the ship shapes in Ian Bell's ship table of ArcElite, the Archimedes version of Elite. With `HULLS=arcelite`, tools/ship128.py reads it (through tools/proto_fill/gen.py, from work/arcelite/x_ships/B5052480.C) instead of building from the stock blueprints. The table and everything generated from it stay in work/ and are not in the repository; they are not covered by the MIT licence. They end up inside every 128K disk and in the listing made with that switch: build those for your own use only, no licence is granted to redistribute them. The default build does not use ArcElite at all.

6. Not in this repository
   ArcElite's sources and binaries (work/arcelite/), the generated hull data, the 128K disk images and the listing (work/ and build/ are ignored). You need your own copy of the game to build the 128K version; `HULLS=arcelite` also needs your own copy of the ArcElite files. Their authors and rights holders keep all rights.

If you hold rights to anything here and want it removed or credited differently, please open an issue.

; Not the 64K tree's file: the Constrictor is filled like every other hull, so its blueprint is based on Fessor's hull (src/elite/missions_hull.asm, used with his
; permission): his header, with vertices only. The vertices and the fill triangles come from tools/ship128.py into work/elite128/ (never committed): from his own
; vertices, edges and faces with HULLS=stock, from ArcElite's CONSTRICTOR (third party data) with HULLS=arcelite; the fill records are type 19 of fill128_late.bin.
    INCLUDE "../../work/elite128/hull_constrictor.asm"
mxHullTypeImpl:                       ; DE = blueprint address: type 19 (the Constrictor), A = type, carry clear on a match, else carry set (see missions_ships.asm)
    ld hl,shipdatConstrictor
    or a
    sbc hl,de
    ld a,19
    ret z
    scf
    ret

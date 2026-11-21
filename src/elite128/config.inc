; Build configuration of the 128K build: one variant only (enhanced UI, mission hooks, title ship selection, Firebird loader). No -D flags are needed on the
; command line; tools add only the per-image flags -DFL_x (flight image x) and -DOVL_x (docked overlay x). Included first by every source file.
    IFNDEF ENHANCED
    DEFINE ENHANCED
    ENDIF
    IFNDEF MISSIONS
    DEFINE MISSIONS
    ENDIF
    IFNDEF TITLESEL
    DEFINE TITLESEL
    ENDIF
    IFNDEF FIREBIRD
    DEFINE FIREBIRD
    ENDIF
; Hostile ships start at a random distance and direction from the front 270 degrees instead of one of four fixed diagonal corners (spawnVariance in lasersights128.asm, called by
; spawnShip). Remove the define for the original spawn rules. docs/_ship_spawning.md, TODO_128K.md.
    IFNDEF SPAWN_VARIANCE
    DEFINE SPAWN_VARIANCE
    ENDIF
; The title screen's ship viewer (commonxx.asm titleArrows/titleName, common2x.asm titleSpawn; tools/ship128.py VIEW makes the table):
TITLE_SHIPS equ 29                  ; ships the title screen can show: the stock hulls, the Constrictor and the nine ship pack hulls (tools/ship128.py VIEW)
titleViewTable equ 0x6B00           ; bank 6, with the records of the pack hulls (fill128_packs.bin): per ship 4 bytes: base type, flight image slot, wanted hull type (0xFF: any), distance
titleViewNames equ 0x6B80           ; and 16 bytes per name, zero terminated

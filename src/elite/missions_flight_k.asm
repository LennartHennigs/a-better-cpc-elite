; Ship pack image (-DFL_1 .. -DFL_7): the default image plus one or two extra hulls (Fessor's ships, missions_ships.asm, made by tools/fessor_ships.py)
; and a ship table hook that swaps them in for a stock type. The stock 19 types stay: each redirected type uses the extra hull on half the spawns (bit 0 of getRandomNumber).
; Never redirected: 8 police Viper, 15 Thargoid, 18 Thargon (the Thargoid and plans missions need them). Hook: spawnShip, A = type (kept), HL = table base.
; The 64K packs 1 and 2 carry one hull each (the Gecko, the Moray): the room goes to the spawn variance routine (SPAWN_VARIANCE, docs/_ship_spawning.md). The 128K build (HULL_128) keeps both.
    IFDEF FL_1
    DEFINE HULL_GECKO
    IFDEF HULL_128
    DEFINE HULL_COBRAMK1
    ENDIF
    ENDIF
    IFDEF FL_2
    IFDEF HULL_128
    DEFINE HULL_WORM
    ENDIF
    DEFINE HULL_MORAY
    ENDIF
    IFDEF FL_3
    DEFINE HULL_MAMBA
    ENDIF
    IFDEF FL_4
    DEFINE HULL_ADDER
    ENDIF
    IFDEF FL_5
    DEFINE HULL_BOA
    ENDIF
    IFDEF FL_6
    DEFINE HULL_ANACONDA
    ENDIF
    IFDEF FL_7
    DEFINE HULL_SHUTTLE
    ENDIF

mxShipTableImpl:
    ld hl,shipGFXdataTable
    ld c,a                            ; BC is dead after the hook (spawnShip sets B from A and BC for the ldir), so it needs no push
    call getRandomNumber              ; preserves BC and HL
    rrca                              ; carry = coin: set = use the extra hull for this spawn
    ld a,c
    ret nc
    IFDEF FL_1
    IFDEF HULL_128
    cp 16                             ; Sidewinder -> Gecko, Krait -> Cobra Mk I: the two records are adjacent, so one base serves both types
    ret c
    cp 18
    ret nc
    ELSE
    cp 16                             ; Sidewinder -> Gecko
    ret nz
    ENDIF
    ld hl,mxEntryGecko-16*4
    ENDIF
    IFDEF FL_2
    IFDEF HULL_128
    cp 16                             ; Sidewinder -> Worm, Krait -> Moray (adjacent records, as above)
    ret c
    cp 18
    ret nc
    ld hl,mxEntryWorm-16*4
    ELSE
    cp 17                             ; Krait -> Moray
    ret nz
    ld hl,mxEntryMoray-17*4
    ENDIF
    ENDIF
    IFDEF FL_3
    cp 16                             ; Sidewinder -> Mamba
    ret nz
    ld hl,mxEntryMamba-16*4
    ENDIF
    IFDEF FL_4
    cp 17                             ; Krait -> Adder
    ret nz
    ld hl,mxEntryAdder-17*4
    ENDIF
    IFDEF FL_5
    cp 10                             ; Python trader -> Boa (the Boulder hull, 165 bytes, does not fit beside it: 9 bytes over)
    ret nz
    ld hl,mxEntryBoa-10*4
    ENDIF
    IFDEF FL_6
    cp 10                             ; Python trader -> Anaconda
    ret nz
    ld hl,mxEntryAnaconda-10*4
    ENDIF
    IFDEF FL_7
    cp 9                              ; Cobra Mk III trader -> Shuttle
    ret nz
    ld hl,mxEntryShuttle-9*4
    ENDIF
mxShipDone:
    ret

; Records like the stock table (`jp blueprint`, then a tag byte nothing reads).
    IFDEF HULL_GECKO
mxEntryGecko:
    jp shipdatGecko
    db 4
    ENDIF
    IFDEF HULL_COBRAMK1
mxEntryCobraMk1:
    jp shipdatCobraMk1
    db 4
    ASSERT mxEntryCobraMk1 == mxEntryGecko + 4, "the Gecko and Cobra Mk I records must be adjacent (one range test serves both types)"
    ENDIF
    IFDEF HULL_WORM
mxEntryWorm:
    jp shipdatWorm
    db 4
    ENDIF
    IFDEF HULL_MORAY
mxEntryMoray:
    jp shipdatMoray
    db 4
    IFDEF HULL_WORM
    ASSERT mxEntryMoray == mxEntryWorm + 4, "the Worm and Moray records must be adjacent (one range test serves both types)"
    ENDIF
    ENDIF
    IFDEF HULL_MAMBA
mxEntryMamba:
    jp shipdatMamba
    db 4
    ENDIF
    IFDEF HULL_ADDER
mxEntryAdder:
    jp shipdatAdder
    db 4
    ENDIF
    IFDEF HULL_BOA
mxEntryBoa:
    jp shipdatBoa
    db 4
    ENDIF
    IFDEF HULL_ANACONDA
mxEntryAnaconda:
    jp shipdatAnaconda
    db 4
    ENDIF
    IFDEF HULL_SHUTTLE
mxEntryShuttle:
    jp shipdatShuttle
    db 4
    ENDIF

    IFDEF HULL_128
    INCLUDE "../elite128/missions_ships.asm"       ; the 128K tree: vertices-only hulls and the type chain for hullFindType (tools/ship128.py)
    ELSE
    INCLUDE "missions_ships.asm"
    ENDIF

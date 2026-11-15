; Ship pack image (-DFL_1 .. -DFL_7): the default image plus one or two extra hulls (Fessor's ships, missions_ships.asm, made by tools/fessor_ships.py)
; and a ship table hook that swaps them in for a stock type. The stock 19 types stay: each redirected type uses the extra hull on half the spawns (bit 0 of getRandomNumber).
; Never redirected: 8 police Viper, 15 Thargoid, 18 Thargon (the Thargoid and plans missions need them). Hook: spawnShip, A = type (kept), HL = table base.
    IFDEF FL_1
    DEFINE HULL_GECKO
    DEFINE HULL_COBRAMK1
    ENDIF
    IFDEF FL_2
    DEFINE HULL_WORM
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
    push bc
    ld c,a
    call getRandomNumber              ; preserves BC and HL
    rrca                              ; carry = coin: set = use the extra hull for this spawn
    ld a,c
    jr nc,mxShipDone
    IFDEF FL_1
    cp 16                             ; Sidewinder -> Gecko, Krait -> Cobra Mk I
    jr nz,.k1
    ld hl,mxEntryGecko-16*4
    jr mxShipDone
.k1 cp 17
    jr nz,mxShipDone
    ld hl,mxEntryCobraMk1-17*4
    ENDIF
    IFDEF FL_2
    cp 16                             ; Sidewinder -> Worm, Krait -> Moray
    jr nz,.k1
    ld hl,mxEntryWorm-16*4
    jr mxShipDone
.k1 cp 17
    jr nz,mxShipDone
    ld hl,mxEntryMoray-17*4
    ENDIF
    IFDEF FL_3
    cp 16                             ; Sidewinder -> Mamba
    jr nz,mxShipDone
    ld hl,mxEntryMamba-16*4
    ENDIF
    IFDEF FL_4
    cp 17                             ; Krait -> Adder
    jr nz,mxShipDone
    ld hl,mxEntryAdder-17*4
    ENDIF
    IFDEF FL_5
    cp 10                             ; Python trader -> Boa (the Boulder hull, 165 bytes, does not fit beside it: 9 bytes over)
    jr nz,mxShipDone
    ld hl,mxEntryBoa-10*4
    ENDIF
    IFDEF FL_6
    cp 10                             ; Python trader -> Anaconda
    jr nz,mxShipDone
    ld hl,mxEntryAnaconda-10*4
    ENDIF
    IFDEF FL_7
    cp 9                              ; Cobra Mk III trader -> Shuttle
    jr nz,mxShipDone
    ld hl,mxEntryShuttle-9*4
    ENDIF
mxShipDone:
    pop bc
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

    INCLUDE "missions_ships.asm"

; Thargoid plans flight image (-DFL_P): while the plans are aboard (state bits 2-3 = 2) about 22% of the spawn checks add a Thargoid and a Thargon.

mxSpawnCheckImpl:
    push bc
    push de
    push hl
    push ix
    push iy
    ld a,(mxStateByte)
    and 0x0C
    cp 0x08
    jr nz,mxSpawnDone
    call getRandomNumber
    cp 200                            ; a roll of 200 or more: 56 in 256
    jr c,mxSpawnDone
    call mxSpawnThargoidPair
mxSpawnDone:
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    ld a,(cargoSlaves)                ; the instruction the hook replaced
    ret

; A Thargoid (type 15) placed like spawnCommand1 places one, and a Thargon (type 18) on top of it. Stops quietly when no slot is free.
mxSpawnThargoidPair:
    call lookforFreeSlot
    ret nz
    ld a,0x0F
    call spawnShip
    set 0,(ix+37)
    call getRandomNumber
    and 0x0F
    or 0x04
    ld (ix+7),a
    rra
    rra
    rra
    and 0x01
    ld (ix+1),a
    xor a
    ld (ix+4),a
    call setDirectionofEntity
    push ix
    pop hl                            ; the Thargoid's position
    call lookforFreeSlot
    ret nz
    ld a,0x12
    call spawnShip
    push ix
    pop de
    ld bc,0x0009
    ldir                              ; same x, y, z as the mother ship
    set 0,(ix+37)
    jp setDirectionofEntity


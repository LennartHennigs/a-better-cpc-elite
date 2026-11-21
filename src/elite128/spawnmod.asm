; Spawn variance module for the 128K build (config.inc SPAWN_VARIANCE; docs/_ship_spawning.md). Assembled for RAM bank 6 at &4600 (the far-call window, config C6), staged by
; tools/build_dsk128.py in a blank block of the window page (STAGE+0x3000) and copied by bankInit to &4600-&483F.
; Entered from the stub in the overlay on bankInit (lasersights128.asm: spawnVariance, spawnRock) at the end of spawnShip, on the resident stack with IX = the new ship (x_lo, y_lo and
; the x and y signs are random already). A = the mode:
;   0     a lone ship: only the hostile types (bit 2 of byte +33: Sidewinder, Krait, the pirates, the Asp, the Thargoid) are changed
;   1-4   a member of a pack (spawnEscortPack; the number is what is left to spawn, this one included): placed like a lone ship, then the leader (the first of the pack) keeps that spot
;         and the others are put next to it
;   &FF   an asteroid (spawnCommand0): placed anywhere around the player and sent towards the player
; Placement (as the first version in the overlay): x_hi and y_hi random 0 to 63, z_hi 32 to 63, z sign random; a ship that would land behind the player inside the rear cone (x_hi and y_hi
; both below z_hi) is put in front. The front 180 degrees plus the two side wedges behind the lateral axis remain: 270 degrees; a hostile turns towards the player by itself.
; A pack member copies the leader's position and sign bytes, adds 0 or 1 to each high byte and takes a random low byte: within about 500 units of the leader on each axis.
; An asteroid has no AI, so it needs its heading at the start: the vector from the ship to the player (the position negated) plus a random offset of up to 4,000 units per axis is cut down to
; the nearest of 26 directions (each component 0 when it is less than half of the largest, else its sign: 3 x 3 x 3 minus the middle) and the matching orthonormal frame of spawn_table.inc
; becomes the ship's orientation (nosev, roofv, sidev); the engine's own tidy keeps it orthonormal from there. Rocks to the side and behind therefore fly across the player's path.
; Bank 7 (and getRandomNumber with it) is hidden here: the module keeps its own random state (stirred with the R register at every entry). Only A, BC, DE, HL, IY and the flags change.
    INCLUDE "config.inc"
    ORG 0x4600
spawnMod:
    ld d,a
    inc a
    jr z,smPlace                        ; an asteroid goes anywhere
    bit 2,(ix+33)
    ret z                               ; not a hostile type
smPlace:
    ld hl,(smSeed)                      ; stir: the R register changes with every instruction the game runs
    ld a,r
    xor l
    ld l,a
    ld (smSeed),hl
    call smRand
    and 0x3F
    ld (ix+1),a
    call smRand
    and 0x3F
    ld (ix+4),a
    call smRand
    and 0x1F
    or 0x20
    ld (ix+7),a
    call smRand
    and 0x80
    ld (ix+8),a
    inc d
    jr z,smRock                         ; mode &FF: the whole sphere, and a heading
    dec d
    ld a,(ix+8)
    and a
    jr z,smFront
    ld a,(ix+1)
    cp (ix+7)
    jr nc,smFront                       ; x_hi >= z_hi: outside the rear cone
    ld a,(ix+4)
    cp (ix+7)
    jr nc,smFront
    res 7,(ix+8)                        ; inside the rear cone: in front instead
smFront:
    ld a,d
    and a
    jr z,smLone
    ld hl,smLastLeft                    ; a pack: the first of it has more left to spawn than the ship before it left
    ld a,(hl)
    cp d
    ld a,d
    dec a
    ld (hl),a
    jr c,smLeader
    ld iy,(smLeaderIX)                    ; a follower: the leader's spot, shaken a little
    ld b,3
smFollow:
    call smRand
    ld (ix+0),a
    call smRand
    and 1
    add a,(iy+1)
    ld (ix+1),a
    ld a,(iy+2)
    ld (ix+2),a
    inc ix
    inc ix
    inc ix
    inc iy
    inc iy
    inc iy
    djnz smFollow
    ld de,-9
    add ix,de
    ret
smLeader:
    ld (smLeaderIX),ix
    ret
smLone:
    ld (smLastLeft),a                   ; 0: the next pack starts afresh
    ret
smRock:
    push ix                             ; d = -position + a random offset, per axis, as signed bytes (position hi 0 to 63, offset -16 to 15)
    pop iy
    ld hl,smD
    ld b,3
smAxis:
    ld a,(iy+1)
    bit 7,(iy+2)
    jr nz,smNegative
    neg
smNegative:
    ld c,a
    call smRand
    and 0x1F
    sub 16
    add a,c
    ld (hl),a
    inc hl
    inc iy
    inc iy
    inc iy
    djnz smAxis
    ld a,(smD)                          ; B = the largest |d|
    call smAbs
    ld b,a
    ld a,(smD + 1)
    call smAbs
    cp b
    jr c,smMax1
    ld b,a
smMax1:
    ld a,(smD + 2)
    call smAbs
    cp b
    jr c,smMax2
    ld b,a
smMax2:
    ld hl,smD                           ; C = the row: three trits, 0 minus, 1 zero (2 |d| below the largest), 2 plus
    ld c,0
    ld e,3
smTrit:
    ld a,c
    add a,a
    add a,c
    ld c,a
    ld a,(hl)
    inc hl
    ld d,a
    call smAbs
    add a,a
    cp b
    jr c,smZero
    bit 7,d
    jr nz,smNext
    inc c
smZero:
    inc c
smNext:
    dec e
    jr nz,smTrit
    ld l,c                              ; HL = smTable + 9 * C
    ld h,0
    ld e,l
    ld d,h
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,de
    ld de,smTable
    add hl,de
    push ix
    pop iy
    ld de,9
    add iy,de
    ld b,9
smMatrix:
    ld a,(hl)
    inc hl
    ld (iy+0),0                         ; low byte
    ld (iy+1),a                         ; high byte
    inc iy
    inc iy
    djnz smMatrix
    ret
smAbs:
    and a
    ret p
    neg
    ret
; A = a random byte (the stock generator's step on the module's own state); HL and BC are kept
smRand:
    push hl
    push bc
    ld hl,(smSeed)
    ld a,h
    adc a,a
    ld b,a
    adc a,l
    ld h,a
    ld l,b
    ld (smSeed),hl
    pop bc
    pop hl
    ret
smSeed:
    dw 0xB2C5
smLeaderIX:
    dw 0
smLastLeft:
    db 0
smD:
    ds 3
smCodeEnd:
smTable:
    INCLUDE "spawn_table.inc"
smEnd:
    ASSERT smEnd <= 0x4600 + 0x240, "module and table: bankInit copies 0x240 bytes (commonxx.asm), one blank stage block of the window page"

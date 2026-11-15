; Trumbles flight image (-DFL_T). The count is mxTrCount (&3905/&3906, 16 bit, at most &7FFF). Not zero means Trumbles are aboard.
; Vectors: arrival (breeding, they eat the food and narcotics), spawn check (slow breeding), sun (heat halves them), inventory (a line with the count), draw (sprites).

; Hyperspace arrival: replaces `ld (tunnelFlag2),a` (A = 1, kept). With Trumbles aboard the hold's food and narcotics are eaten (the tonnes come back as free
; space) and the count becomes 2 * ((count + 0..15) OR 4); when the sum before the doubling is 0x4000 or more it is held at 0x7FFF instead (so the count never exceeds 0x7FFF and never wraps).
mxArriveImpl:
    ld (tunnelFlag2),a
    push af
    push bc
    push hl
    ld hl,(mxTrCount)
    ld a,h
    or l
    jr z,mxArriveDone
    call getRandomNumber
    and 0x0F
    ld c,a
    ld b,0
    add hl,bc
    ld a,h
    and 0xC0
    jr nz,mxArriveCap                 ; a sum of 0x4000 or more doubles to 0x8000 or more (or wraps past 16 bits at the cap): keep it at 0x7FFF
    set 2,l                           ; was ld a,l / or 4 / ld l,a: 2 bytes saved for the ship pack picker in mxFlightNone
    add hl,hl
    jr mxArriveStore
mxArriveCap:
    ld hl,0x7FFF
mxArriveStore:
    ld (mxTrCount),hl
    ld hl,cargoHold                   ; food, good 0
    ld a,(hl)
    ld (hl),0x00
    ld hl,cargoNarcotics              ; narcotics, good 6
    add a,(hl)
    ld (hl),0x00
    ld hl,cargoSpaceFree              ; the eaten tonnes are free again
    add a,(hl)
    ld (hl),a
mxArriveDone:
    pop hl
    pop bc
    pop af
    ret

; Spawn check (the first instruction of spawnCommand0, which this must end with): with 256 or more Trumbles they squeak now and then, and about 14% of the checks (a roll of 220 or more) add one.
mxSpawnCheckImpl:
    push af
    push hl
    ld a,(mxTrCount+1)
    and a
    jr z,mxSpawnDone
    ld h,a                            ; noise: a squeak (sound effect bit 5 of sfxFlags2Bitmap, a short decaying tone) with a chance of high byte / 64
    call getRandomNumber
    and 0x3F
    cp h
    jr nc,mxSpawnQuiet
    ld a,(sfxFlags2Bitmap)
    or 0x20
    ld (sfxFlags2Bitmap),a
mxSpawnQuiet:
    call getRandomNumber
    cp 220
    jr c,mxSpawnDone
    ld hl,(mxTrCount)
    inc hl
    bit 7,h
    jr nz,mxSpawnDone
    ld (mxTrCount),hl
mxSpawnDone:
    pop hl
    pop af
    ld a,(cargoSlaves)                ; the instruction the hook replaced
    ret

; Sun: replaces `ld hl,CockpitTemp` in todoOverheating (A kept). At a cabin temperature of 240 or more every call halves the count, so near a sun they die out.
mxSunImpl:
    push af
    ld a,(CockpitTemp)
    cp 240
    jr c,mxSunDone
    ld hl,(mxTrCount)
    srl h
    rr l
    ld (mxTrCount),hl
mxSunDone:
    pop af
    ld hl,CockpitTemp
    ret

; Inventory: replaces `call prQuantityofGoodinCargohold` in the loop over the 17 goods. Before the first good (storedByteVariable 0) a line "TRUMBLES  n"
; is printed when there are Trumbles; then the original call runs (its carry result is what the loop tests, so it must be the last thing done).
mxInvHookImpl:
    ld a,(storedByteVariable)
    and a
    jr nz,mxInvNormal
    ld hl,(mxTrCount)
    ld a,h
    or l
    jr z,mxInvNormal
    ld hl,mxTrumblesText
mxInvChar:
    ld a,(hl)
    and a
    jr z,mxInvNumber
    push hl
    call printString
    pop hl
    inc hl
    jr mxInvChar
mxInvNumber:
    ld a,0x05
    ld (numberOfDigits),a
    ld hl,(mxTrCount)
    and a
    call todo_SomethingwithDigits
    call placeCursor
mxInvNormal:
    jp prQuantityofGoodinCargohold
mxTrumblesText:
    db "TRUMBLES ",0

; ---- Sprites ----------------------------------------------------------------------------------------------------------------------------------------------------
; Up to six Trumbles drawn into the off-screen bitmap (&A000, 64 bytes per line, Mode 1) just before it is copied to the screen, so there is nothing to erase: the
; game clears the bitmap every frame. Called in place of the `call transferBuffertoScreen` in Spaceflight (once per frame in the flight views; not in the hyperspace tunnel), it ends with that jump.
; Shape: one 12 x 12 pixel furry blob (tools/sprite_enc.py from missions_trumble_art.txt), 3 x 12 bytes, OR-ed in.
; Position: x in bytes (4 pixels, 3-56), y in lines (2-112), kept inside the view frame. Velocity -1, 0 or +1 in each axis. Like the C64, one Trumble moves per
; call (a tick counter mod 8, only those that are shown) and picks new velocities with an 8% chance (a roll of 235 or more) from 0, +1, -1, 0.
; How many are shown: one per Trumble, at most 6 (256 or more show six).
mxFlightDrawImpl:
    push af
    push bc
    push de
    push hl
    ld hl,(mxTrCount)
    ld a,h
    or l
    jr z,mxDrawDone                   ; no Trumbles aboard
    ld a,h
    and a
    jr nz,mxSix
    ld a,l
    cp 0x07
    jr c,mxHaveN
mxSix:
    ld a,0x06
mxHaveN:
    ld c,a                            ; C = number of Trumbles shown (1-6)
    ld hl,mxTrTick
    ld a,(hl)
    inc (hl)
    and 0x07                          ; this call's Trumble
    cp c
    jr nc,mxNoMove                    ; not one of those shown
    add a,a
    add a,a
    ld e,a
    ld d,0x00
    ld hl,mxTrState
    add hl,de
    push bc                           ; mxMoveSprite uses BC; C is the number shown
    call mxMoveSprite
    pop bc
mxNoMove:
    push ix
    ld ix,mxTrState
    ld b,0x00                         ; B = index of the Trumble being drawn
mxDrawLoop:
    push bc
    ld a,(ix+1)                       ; destination = &A000 + y * 64 + x
    rrca
    rrca
    ld e,a
    and 0xC0
    or (ix+0)
    ld l,a
    ld a,e
    and 0x3F
    or 0xA0
    ld h,a
    ld de,mxTrShape
    call mxBlit
    pop bc
    ld de,0x0004
    add ix,de
    inc b
    ld a,b
    cp c
    jr c,mxDrawLoop
    pop ix
mxDrawDone:
    pop hl
    pop de
    pop bc
    pop af
    jp transferBuffertoScreen

; HL = destination in the bitmap, DE = shape: OR 12 rows of 3 bytes onto the bitmap (the next row is 64 bytes on).
mxBlit:
    ld c,12
mxBlitRow:
    ld b,3
mxBlitByte:
    ld a,(de)
    inc de
    or (hl)
    ld (hl),a
    inc hl
    djnz mxBlitByte
    ld a,l
    add a,61
    ld l,a
    jr nc,mxBlitNext
    inc h
mxBlitNext:
    dec c
    jr nz,mxBlitRow
    ret

; HL = a Trumble's record (x, y, vx, vy): maybe new velocities (8%), then one step in x and one in y.
mxMoveSprite:
    push hl
    call getRandomNumber
    cp 235
    jr c,mxMoveGo
    pop hl
    push hl
    inc hl
    inc hl
    call mxNewVelocity                ; vx, then vy
    call mxNewVelocity
mxMoveGo:
    pop hl
    ld bc,0x0339                      ; x from 3 to 57 (3 bytes wide)
    call mxAxis
    ld bc,0x0272                      ; y from 2 to 114 (12 rows high, so the last line stays above the frame)

; HL -> a position byte, (HL+2) its velocity, B = lowest and C = highest value: add, wrap at the ends, store; HL = HL + 1 on return.
mxAxis:
    ld a,(hl)
    inc hl
    inc hl
    add a,(hl)
    dec hl
    dec hl
    cp b
    jr nc,mxAxisLow
    ld a,c
mxAxisLow:
    inc c
    cp c
    jr c,mxAxisOk
    ld a,b
mxAxisOk:
    ld (hl),a
    inc hl
    ret

; (HL) = one of the four velocities (0, +1, -1, 0), HL = HL + 1 on return.
mxNewVelocity:
    push hl
    call getRandomNumber
    and 0x03
    ld e,a
    ld d,0x00
    ld hl,mxTrDir
    add hl,de
    ld a,(hl)
    pop hl
    ld (hl),a
    inc hl
    ret

mxTrDir:
    db 0x00,0x01,0xFF,0x00            ; the four velocities, as on the C64: 0, +1, -1, 0
mxTrTick:
    db 0x00
mxTrState:                            ; six Trumbles: x, y, vx, vy; they start spread over the view and standing still
    db 10,10,0,0
    db 30,20,0,0
    db 45,40,0,0
    db 15,60,0,0
    db 35,80,0,0
    db 50,100,0,0
    INCLUDE "missions_trumble_data.asm"

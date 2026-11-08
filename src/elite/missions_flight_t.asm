; Trumbles flight image (-DFL_T). The count is mxTrCount (&3905/&3906, 16 bit, at most &7FFF). Not zero means Trumbles are aboard.
; Vectors: arrival (breeding, they eat the food and narcotics), spawn check (slow breeding), sun (heat halves them), inventory (a line with the count).

; Hyperspace arrival: replaces `ld (tunnelFlag2),a` (A = 1, kept). With Trumbles aboard the hold's food and narcotics are eaten (the tonnes come back as free
; space) and the count becomes 2 * ((count + 0..15) OR 4), at most &7FFF.
mxArriveImpl:
    ld (tunnelFlag2),a
    push af
    push bc
    push hl
    ld hl,(mxTrCount)
    ld a,h
    or l
    jr z,mxArriveDone
    ld a,(cargoHold)                  ; food, good 0
    ld b,a
    xor a
    ld (cargoHold),a
    ld a,(cargoNarcotics)             ; narcotics, good 6
    add a,b
    ld b,a
    xor a
    ld (cargoNarcotics),a
    ld a,(cargoSpaceFree)
    add a,b
    ld (cargoSpaceFree),a
    call getRandomNumber
    and 0x0F
    ld c,a
    ld b,0
    add hl,bc
    ld a,l
    or 0x04
    ld l,a
    add hl,hl
    bit 7,h
    jr z,mxArriveStore
    ld hl,0x7FFF
mxArriveStore:
    ld (mxTrCount),hl
mxArriveDone:
    pop hl
    pop bc
    pop af
    ret

; Spawn check (the first instruction of spawnCommand0, which this must end with): with 256 or more Trumbles about 14% of the checks (a roll of 220 or more) add one.
mxSpawnCheckImpl:
    push af
    push hl
    ld a,(mxTrCount+1)
    and a
    jr z,mxSpawnDone
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

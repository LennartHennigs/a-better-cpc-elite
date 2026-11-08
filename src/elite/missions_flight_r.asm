; Asteroid bombardment flight image (-DFL_R), the second mission after the plans (Elite Plus mission 6). After the first mission is paid (missionState bits 2-3 = 3, bits 4-6 = 5) the
; byte &38FE holds the state in bits 0-1 (0 not offered, 1 clearing Ceerdi, 2 cleared, 3 paid) and the asteroids still to destroy in bits 2-7 (20 at the offer, so the byte is &51).
; While the state is 1 and the player is at Ceerdi (galaxy 3, x 215, y 84) the spawn check adds an asteroid (50% of the checks, the stock asteroid spawn of spawnCommand0) and every
; asteroid destroyed there counts the number down by one (the byte minus 4); at 0 the state becomes 2 and the module in MISSIONR pays 6,000 Cr at the next docking.

; Z when the clearing is on and the player is at Ceerdi. Changes A only.
mxRAtTarget:
    ld a,(mxStateByte)
    and 0x7C
    cp 0x5C
    ret nz
    ld a,(mxAsteroidCount)
    and 0x03
    cp 0x01
    ret nz
    ld a,(currentGalaxy)
    cp 0x02
    ret nz
    ld a,(presentSystemX)
    cp 215
    ret nz
    ld a,(presentSystemY)
    cp 84
    ret

mxSpawnCheckImpl:
    push bc
    push de
    push hl
    push ix
    push iy
    call mxRAtTarget
    jr nz,mxSpawnDone
    call getRandomNumber
    cp 128
    jr c,mxSpawnDone
    call lookforFreeSlot
    jr nz,mxSpawnDone
    ld a,0x06                         ; the asteroid of spawnCommand0 (chkSpawnAsteroid)
    call spawnShip
    set 7,(ix+14)
    res 6,(ix+32)
    ld a,0xC0
    ld (ix+29),a
mxSpawnDone:
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    ld a,(cargoSlaves)                ; the instruction the hook replaced
    ret

; Replaces `call getBounty` (IY = the dead ship's blueprint). All registers kept.
mxKillHookImpl:
    call getBounty
    push af
    push de
    push hl
    call mxRAtTarget
    jr nz,mxKillDone
    push iy
    pop de
    ld hl,shipdatAsteroid
    and a
    sbc hl,de
    jr nz,mxKillDone
    ld hl,mxAsteroidCount
    ld a,(hl)
    sub 0x04
    ld (hl),a
    cp 0x04
    jr nc,mxKillDone
    inc (hl)                          ; the number reached 0: state 1 -> 2 (cleared)
mxKillDone:
    pop hl
    pop de
    pop af
    ret

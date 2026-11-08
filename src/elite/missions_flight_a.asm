; Asteroid bombardment flight image (-DFL_A): while Ceerdi is being cleared (missionState bits 2-3 = 3 and bits 4-6 = 1) and the player is at Ceerdi (galaxy 3, x 215, y 84),
; the spawn check adds an asteroid (50% of the checks, the stock asteroid spawn of spawnCommand0) and every asteroid destroyed counts down mxAsteroidCount; at 0 the stage becomes 2
; (cleared) and the plans module pays 6,000 Cr at the next docking.
mxAsteroidCount equ 0x38FE

; Z when the mission is being cleared and the player is at Ceerdi. Changes A only.
mxAstAtTarget:
    ld a,(mxStateByte)
    and 0x7C
    cp 0x1C
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
    call mxAstAtTarget
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
    call mxAstAtTarget
    jr nz,mxKillDone
    push iy
    pop de
    ld hl,shipdatAsteroid
    and a
    sbc hl,de
    jr nz,mxKillDone
    ld hl,mxAsteroidCount
    dec (hl)
    jr nz,mxKillDone
    ld hl,mxStateByte
    ld a,(hl)
    xor 0x30                          ; stage 1 -> 2
    ld (hl),a
mxKillDone:
    pop hl
    pop de
    pop af
    ret

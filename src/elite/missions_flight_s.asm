; Stolen police ship flight image (-DFL_S), the first mission after the plans (Elite Plus mission 4). missionState bits 2-3 = 3 and bits 4-6 = stage:
; 1 waiting: every hyperspace arrival counts mxAsteroidCount (jumps) down, at 0 the stage is 2 (ready: the plans module makes the offer at the next docking);
; 3 hunting: at Birera (galaxy 3, x 63, y 72) the spawn check puts one Viper (ship type 8) there, 22% of the checks, unless the marked one is alive; its kill makes the stage 4
; (the plans module pays 4,000 Cr at the next docking, stage 5).
; The marker needs no extra byte: a police Viper has bits 1 and 6 set in (ix+33) (blueprint byte 18 and &6F), the stolen one has both cleared, so it is not police: its kill is
; no offence (the legal-status rule tests bits 5 and 6) and no police AI. Energy &C8 as in Elite Plus, hostile (ix+37 bit 0).
mxTypeViper equ 8

; Z when the hunt (stage 3) is on and the player is at Birera. Changes A only.
mxSAtTarget:
    ld a,(mxStateByte)
    and 0x7C
    cp 0x3C
    ret nz
    ld a,(currentGalaxy)
    cp 0x02
    ret nz
    ld a,(presentSystemX)
    cp 63
    ret nz
    ld a,(presentSystemY)
    cp 72
    ret

; Z when the ship at IX is the stolen Viper (a Viper with bits 1 and 6 of (ix+33) clear). Changes A only.
mxSIsStolen:
    ld a,(ix+35)
    cp shipdatViper & 0xFF
    ret nz
    ld a,(ix+36)
    cp shipdatViper >> 8
    ret nz
    ld a,(ix+33)
    and 0x42
    ret

mxSpawnCheckImpl:
    push bc
    push de
    push hl
    push ix
    push iy
    call mxSAtTarget
    jr nz,mxSpawnDone
    ld ix,sEntityxlo
    ld de,0x0027
    ld b,0x06
mxSpawnScan:
    add ix,de
    ld a,(ix+34)
    and a
    jr z,mxSpawnNext
    call mxSIsStolen
    jr z,mxSpawnDone                  ; already there
mxSpawnNext:
    djnz mxSpawnScan
    call getRandomNumber
    cp 200
    jr c,mxSpawnDone
    call lookforFreeSlot
    jr nz,mxSpawnDone
    ld a,mxTypeViper
    call spawnShip
    res 6,(ix+33)
    res 1,(ix+33)
    set 0,(ix+37)
    ld a,0xC8
    ld (ix+34),a
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
mxSpawnDone:
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    ld a,(cargoSlaves)                ; the instruction the hook replaced
    ret

; Replaces `call getBounty` (IY = the dead ship's blueprint, IX = the dead ship). All registers kept.
mxKillHookImpl:
    call getBounty
    push af
    push hl
    call mxSAtTarget
    jr nz,mxKillDone
    call mxSIsStolen
    jr nz,mxKillDone
    ld hl,mxStateByte
    ld a,(hl)
    xor 0x70                          ; stage 3 -> 4
    ld (hl),a
mxKillDone:
    pop hl
    pop af
    ret

; Replaces `ld (tunnelFlag2),a` at a hyperspace arrival (A = 1, kept). Stage 1: one jump less to wait; at 0 the stage becomes 2 (add 0x10).
mxArriveImpl:
    ld (tunnelFlag2),a
    push af
    push hl
    ld a,(mxStateByte)
    and 0x7C
    cp 0x1C
    jr nz,mxArriveDone
    ld hl,mxAsteroidCount
    dec (hl)
    jr nz,mxArriveDone
    ld hl,mxStateByte
    ld a,0x10
    add a,(hl)
    ld (hl),a
mxArriveDone:
    pop hl
    pop af
    ret

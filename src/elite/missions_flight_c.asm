; Constrictor flight image (-DFL_C): ship type 19 with its hull, the spawn at Orarra, the kill marker and the military-laser rule. Vectors: ship table, spawn check, kill, laser.

; spawnShip's table lookup (it replaces `ld hl,shipGFXdataTable`, same 3 bytes): A = ship type (kept), returns HL so that
; HL + 4 * (type & &3F) points at the record. Type 19 is served from the one-entry table below, so nothing in the stock table moves.
mxShipTableImpl:
    ld hl,shipGFXdataTable
    push af
    and 0x3F
    cp mxTypeConstrictor
    jr nz,mxShipTableDone
    ld hl,mxConstrictorEntry-mxTypeConstrictor*4
mxShipTableDone:
    pop af
    ret
mxConstrictorEntry:
    jp shipdatConstrictor            ; spawnShip reads bytes +1 and +2 (the blueprint address)
    db 0x04                          ; the unused tag byte of the stock records


; Constrictor image, vector mxSpawnCheck (called in place of the first instruction of spawnCommand0, `ld a,(cargoSlaves)`, and ends with it). While the hunt is on, all seven hints are
; given (stage 7) and the player is in Orarra (galaxy 2, x 144, y 33), it spawns the Constrictor unless one is already alive. All registers are kept
; (spawnCommand0 can be entered with IX/IY in use). The spawn follows spawnCommand1's pattern: hostile flag, far z, then setDirectionofEntity.
mxSpawnCheckImpl:
    push bc
    push de
    push hl
    push ix
    push iy
    ld a,(mxStateByte)
    ld b,a
    and 0x03
    cp 0x01
    jr nz,mxSpawnDone                 ; not hunting
    ld a,b
    and 0x70
    cp 0x70
    jr nz,mxSpawnDone                 ; hints not finished
    ld a,(currentGalaxy)
    cp 0x01
    jr nz,mxSpawnDone
    ld a,(presentSystemX)
    cp 144
    jr nz,mxSpawnDone
    ld a,(presentSystemY)
    cp 33
    jr nz,mxSpawnDone                 ; not Orarra
    ld ix,sEntityxlo
    ld de,0x0027
    ld b,0x06
mxSpawnScan:
    add ix,de
    ld a,(ix+34)
    and a
    jr z,mxSpawnNext
    ld a,(ix+35)
    cp shipdatConstrictor & 0xFF
    jr nz,mxSpawnNext
    ld a,(ix+36)
    cp shipdatConstrictor >> 8
    jr z,mxSpawnDone                  ; already there
mxSpawnNext:
    djnz mxSpawnScan
    call lookforFreeSlot
    jr nz,mxSpawnDone
    ld a,mxTypeConstrictor
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
mxSpawnDone:
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    ld a,(cargoSlaves)                ; the instruction this call replaced
    ret

; Replaces `call getBounty` where a destroyed ship is paid (todo_killedsomeone, IY = its blueprint). Does the original call, then, if the dead ship
; is the Constrictor and the hunt is on, sets state 3 (killed); the reward is paid at the next docking. Keeps all registers.
mxKillHookImpl:
    call getBounty
    push af
    push hl
    ld a,iyl
    cp shipdatConstrictor & 0xFF
    jr nz,mxKillDone
    ld a,iyh
    cp shipdatConstrictor >> 8
    jr nz,mxKillDone
    ld hl,mxStateByte
    ld a,(hl)
    and 0x03
    cp 0x01
    jr nz,mxKillDone
    set 1,(hl)                        ; 01 -> 11
mxKillDone:
    pop hl
    pop af
    ret

; Replaces `ld (ix+34),a` in applyLaserDamagetoEntity (same 3 bytes; A = energy minus the hit, C = laser power: pulse and beam 15, military 23, mining 50,
; flags from the `sub c`). Like the BBC Constrictor, the Constrictor only takes damage from a military laser or better (C >= 23). A weaker hit leaves the energy
; unchanged and returns NZ/NC, so the caller neither kills nor counts it. Every other ship gets the original store, flags untouched.
mxLaserHookImpl:
    push af
    ld a,(ix+35)
    cp shipdatConstrictor & 0xFF
    jr nz,mxLaserNormal
    ld a,(ix+36)
    cp shipdatConstrictor >> 8
    jr nz,mxLaserNormal
    ld a,c
    cp 0x17
    jr nc,mxLaserNormal
    pop af
    ld a,(ix+34)                      ; weak laser: no damage
    or a                              ; NC, and NZ because a live ship has energy
    ret
mxLaserNormal:
    pop af
    ld (ix+34),a
    ret

    INCLUDE "missions_hull.asm"

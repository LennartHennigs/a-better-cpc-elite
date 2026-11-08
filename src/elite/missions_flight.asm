; Mission code that must be resident in flight (COMMONXX tail, &9D9E-&9FFF). Assembled only with -DMISSIONS.

mxTypeConstrictor equ 19            ; ship type after the 19 stock ships (0-18)

; spawnShip's table lookup (it replaces `ld hl,shipGFXdataTable`, same 3 bytes): A = ship type (kept), returns HL so that
; HL + 4 * (type & &3F) points at the record. Type 19 is served from the one-entry table below, so nothing in the stock table moves.
mxShipTable:
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

mxStateByte equ 0x38FD              ; missionState (see missions_docked.asm): bits 0-1 Constrictor, bits 4-6 hint stage

; Replaces the first instruction of spawnCommand0 (`ld a,(cargoSlaves)`, same 3 bytes) and ends with it. While the Constrictor hunt is on, all seven hints are
; given (stage 7) and the player is in Orarra (galaxy 2, x 144, y 33), it spawns the Constrictor unless one is already alive. All registers are kept
; (spawnCommand0 can be entered with IX/IY in use). The spawn follows spawnCommand1's pattern: hostile flag, far z, then setDirectionofEntity.
mxSpawnCheck:
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
mxKillHook:
    call getBounty
    push af
    push de
    push hl
    push iy
    pop de
    ld hl,shipdatConstrictor
    and a
    sbc hl,de
    jr nz,mxKillDone
    ld hl,mxStateByte
    ld a,(hl)
    and 0x03
    cp 0x01
    jr nz,mxKillDone
    set 1,(hl)                        ; 01 -> 11
mxKillDone:
    pop hl
    pop de
    pop af
    ret

    INCLUDE "missions_hull.asm"

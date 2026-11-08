; Thargoid plans module. Loaded at mxOverlayBase by the stub in missions_docked.asm.
; State: missionState bits 2-3: 0 not offered, 1 briefed (go to Ceerdi), 2 plans aboard (go to Birera), 3 finished (reward paid).
; Delivering the plans also offers the asteroid mission (bits 4-6 = 1, 20 asteroids to destroy at Ceerdi, counter mxAsteroidCount); this module pays it (bits 4-6 = 2 -> 3, 6,000 Cr).
; Needs the Constrictor finished (bits 0-1 = 2), 1280 kill points (killScoreHigh >= 5) and galaxy 3. Systems checked against the CPC name generator
; (docs/_missions.md section 7): Ceerdi galaxy 3 x 215 y 84, Birera galaxy 3 x 63 y 72.
    jp mxModuleEntry
    dw missionTextTable
mxModuleEntry:
    ld a,(missionState)
    ld b,a
    and 0x03
    cp 0x02
    ret nz                            ; the Constrictor hunt must be finished
    ld a,b
    and 0x0C
    jr z,mxPlansBrief
    cp 0x0C
    jr z,mxAsteroidReward             ; plans delivered
    ld a,b                            ; stage 1 or 2: the stub loaded this module only at Ceerdi or Birera respectively
    add a,0x04                        ; next stage
    ld (missionState),a
    and 0x0C
    cp 0x0C
    jr z,mxDelivered
    rrca
    rrca                              ; the string number: 2 (the plans)
    jp mxShowEnd
mxDelivered:                          ; the Navy energy unit, one rank step, and the asteroid mission offered in the same box
    ld a,0xFE
    ld (mxExtraEnergyUnit),a
    ld hl,mxKillScoreHigh
    inc (hl)
    ld a,20
    ld (mxAsteroidCount),a
    ld hl,missionState
    set 4,(hl)                        ; asteroid stage 1
    ld a,0x03
    ld de,mxColorsMessage
    ld hl,0x0200
    call missionShow
    ld a,0x04
    call missionPrint
    jp mxActionsAtEndOfMessage

; Asteroid reward (the stub loads this module at stage 2): 6,000 Cr.
mxAsteroidReward:
    ld hl,missionState
    set 4,(hl)                        ; stage 2 -> 3
    ld de,0x0006
    call mxAddDEtoMoney
    ld a,0x05
    jp mxShowEnd

; Offer: Constrictor done, 1280 kill points, galaxy 3.
mxPlansBrief:
    ld a,(mxKillScoreHigh)
    cp 0x05
    ret c
    ld a,(mxCurrentGalaxy)
    cp 0x02
    ret nz
    ld a,b
    or 0x04
    ld (missionState),a
    ld a,0x01
    jp mxShowEnd

; Strings of the mission table (source missions_text_plans.txt; python3 -I tools/textenc.py --asm src/elite/missions_text_plans.txt > src/elite/missions_text_plans.asm)
missionTextTable:
    INCLUDE "missions_text_plans.asm"

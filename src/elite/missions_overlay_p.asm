; Thargoid plans module. Loaded at mxOverlayBase by the stub in missions_docked.asm.
; State: missionState bits 2-3: 0 not offered, 1 briefed (go to Ceerdi), 2 plans aboard (go to Birera), 3 finished (reward paid).
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
    ret z                             ; plans delivered
    ld a,b                            ; stage 1 or 2: the stub loaded this module only at Ceerdi or Birera respectively
    add a,0x04                        ; next stage
    ld (missionState),a
    and 0x0C
    ld c,a
    rrca
    rrca                              ; the string number: 2 (the plans) or 3 (delivered)
    ld b,a
    ld a,c
    cp 0x0C
    ld a,b
    jp nz,mxShowEnd
    push af                           ; delivered: the Navy energy unit and one rank step
    ld a,0xFE
    ld (mxExtraEnergyUnit),a
    ld hl,mxKillScoreHigh
    inc (hl)
    pop af
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

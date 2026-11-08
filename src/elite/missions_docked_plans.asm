; Thargoid plans module of the LARGEAXX tail (&1714-&1A3F). Assembled with -DMISSIONS -DPLANS instead of the Constrictor module.
; State: missionState bits 2-3: 0 not offered, 1 briefed (go to Ceerdi), 2 plans aboard (go to Birera), 3 finished (reward paid).
; Needs the Constrictor finished (bits 0-1 = 2), 1280 kill points (killScoreHigh >= 5) and galaxy 3. Systems checked against the CPC name generator
; (docs/_missions.md section 7): Ceerdi galaxy 3 x 215 y 84, Birera galaxy 3 x 63 y 72.
    INCLUDE "missions_docked_defs.asm"

missionsDockedEntry:                  ; = &1714, the fixed entry the docking code calls
    ld a,(mxThargonMissionVar)
    and a
    jp nz,mxChkMissions               ; an existing mission offer or reward is pending: its turn
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
    ld c,a                            ; 4 = go to Ceerdi, 8 = go to Birera
    ld a,(mxCurrentGalaxy)
    cp 0x02
    ret nz
    ld a,c
    rrca
    rrca
    dec a                             ; row 0 or 1
    ld e,a
    add a,a
    add a,e                           ; times 3
    ld e,a
    ld d,0
    ld hl,mxPlansTable
    add hl,de
    ld a,(mxPresentSystemX)
    cp (hl)
    ret nz
    inc hl
    ld a,(mxPresentSystemY)
    cp (hl)
    ret nz
    inc hl
    ld a,(missionState)
    add a,0x04                        ; next stage
    ld (missionState),a
    and 0x0C
    cp 0x0C
    ld a,(hl)                         ; string number; the flags of the CP survive
    jr nz,mxShowEnd
    push af                           ; delivered: the Navy energy unit and one rank step
    ld a,0xFE
    ld (mxExtraEnergyUnit),a
    ld hl,mxKillScoreHigh
    inc (hl)
    pop af
    jr mxShowEnd

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
    ld a,0x01                         ; string 1 and fall into mxShowEnd
    INCLUDE "missions_docked_show.asm"

; Stage rows: system x, system y, string number.
mxPlansTable:
    db 215,84,0x02                    ; Ceerdi: the agent hands over the plans
    db 63,72,0x03                     ; Birera: delivery

; Strings of the mission table (source missions_text_plans.txt; python3 -I tools/textenc.py --asm src/elite/missions_text_plans.txt > src/elite/missions_text_plans.asm)
missionTextTable:
    INCLUDE "missions_text_plans.asm"

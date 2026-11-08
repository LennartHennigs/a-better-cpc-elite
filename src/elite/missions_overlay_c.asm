; Constrictor module: offer, hints, reward. Loaded at mxOverlayBase by the stub in missions_docked.asm.
    jp mxModuleEntry
    dw missionTextTable
mxModuleEntry:
    ld a,(missionState)
    and 0x03
    jr z,mxBriefing                   ; 0: not offered yet
    cp 0x03
    jr z,mxDebrief                    ; 3: killed, collect the reward
    cp 0x01
    ret nz                            ; 2: finished
                                      ; 1: hunting, fall through to the hints
; Hint chain: at the system of the current stage (table below) show its text and advance the stage.
mxHint:
    ld a,(missionState)
    rrca
    rrca
    rrca
    rrca
    and 0x07
    cp 0x07
    ret nc                            ; stage 7: all hints given
    add a,a
    add a,a
    ld e,a                            ; 4 bytes per row
    ld d,0
    ld hl,missionHintTable
    add hl,de
    ld a,(mxCurrentGalaxy)
    cp (hl)
    ret nz
    inc hl
    ld a,(mxPresentSystemX)
    cp (hl)
    ret nz
    inc hl
    ld a,(mxPresentSystemY)
    cp (hl)
    ret nz
    inc hl
    ld a,(missionState)
    add a,0x10                        ; next stage
    ld (missionState),a
    ld a,(hl)                         ; string number
    jp mxShowEnd

; Offer: needs 256 kill points and galaxy 1 or 2. Galaxy 2 skips the first two hints and starts at Cearso (stage 2).
mxBriefing:
    ld a,(mxKillScoreHigh)
    and a
    ret z
    ld a,(mxCurrentGalaxy)
    cp 0x02
    ret nc
    ld c,a
    ld a,(missionState)
    and 0x8C                          ; keep the Plans and Trumbles bits
    or 0x01                           ; hunting
    ld b,a
    ld a,c
    and a
    jr z,mxBriefing2
    ld a,0x20                         ; stage 2
mxBriefing2:
    or b
    ld (missionState),a
    ld a,0x02
    add a,c                           ; middle part: string 2 (galaxy 1) or 3 (galaxy 2)
    push af
    ld a,0x01                         ; head, then the middle, then the common tail (string 4), all in one box
    ld de,mxColorsMessage
    ld hl,0x0200
    call missionShow
    pop af
    call missionPrint
    ld a,0x04
    call missionPrint
    jp mxActionsAtEndOfMessage

; Reward: 5,000 Cr and one rank step, like the stock rewards (inc killScoreHigh).
mxDebrief:
    ld a,(missionState)
    and 0x8C
    or 0x02                           ; finished, stage cleared
    ld (missionState),a
    ld hl,mxKillScoreHigh
    inc (hl)
    ld de,0x0005
    call mxAddDEtoMoney
    ld a,0x0C                         ; string 12
    jp mxShowEnd
; Hint stages: galaxy (0-7), system x, system y, string number. Coordinates from the CPC name generator (docs/_missions.md section 7).
missionHintTable:
    db 0x00,149,101,0x05              ; Reesdice -> Arexe
    db 0x00,164, 89,0x06              ; Arexe -> galactic jump, Cearso
    db 0x01, 87,109,0x07              ; Cearso -> Errius
    db 0x01,184,149,0x08              ; Errius -> Inbibe
    db 0x01,152,146,0x09              ; Inbibe -> Ausar
    db 0x01,146,102,0x0A              ; Ausar -> Usleri
    db 0x01,148, 68,0x0B              ; Usleri -> Orarra

; Strings (source missions_text.txt; regenerate with python3 -I tools/textenc.py --asm src/elite/missions_text.txt > src/elite/missions_text.asm)
missionTextTable:
    INCLUDE "missions_text.asm"

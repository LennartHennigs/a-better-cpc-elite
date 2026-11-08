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
; Hint chain: the stub only loads this module at the system of the current stage (mxStageTable), so here the stage just advances and its text is shown.
mxHint:
    ld a,(missionState)
    add a,0x10                        ; next stage
    ld (missionState),a
    rrca
    rrca
    rrca
    rrca
    and 0x07
    add a,0x04                        ; string 5 + old stage = 4 + new stage
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
    rrca
    rrca
    rrca                              ; galaxy 1: stage 0, galaxy 2: stage 2 (0x20)
    ld b,a
    ld a,(missionState)
    and 0x8C                          ; keep the Plans and Trumbles bits
    or b
    inc a                             ; hunting (bit 0 was clear)
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
; Strings (source missions_text.txt; regenerate with python3 -I tools/textenc.py --asm src/elite/missions_text.txt > src/elite/missions_text.asm)
missionTextTable:
    INCLUDE "missions_text.asm"

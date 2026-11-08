; Mission code that runs only while docked (LARGEAXX tail, &1714-&1A3F). Assembled only with -DMISSIONS.
; Entered from the docking sequence (commonxx.asm, after loadLARGEAXX), in place of `call chkMissions`.

; Addresses in COMMONXX (stock layout; the check in tools/check_src.sh keeps them honest through the byte-exact build).
mxChkMissions          equ 0x2063
mxThargonMissionVar    equ 0x3926
mxDrawFrame            equ 0x4646
mxPrintStringA         equ 0x4416
mxPrintStringScan      equ 0x442C     ; inside printStringA: HL = table, D = 1-based string number
mxSetColors            equ 0x454F
mxViewdirection        equ 0x1C02
mxCharXY               equ 0x38C4
mxActionsAtEndOfMessage equ 0x499E    ; waits for a key, redraws the frame, then jp InitVariables (returns to the docking code)
mxColorsMessage        equ 0x4A31     ; colour set of the "mission accepted" box (colorsThargonMissionAccepted)
missionState           equ 0x38FD     ; save byte, never used by the stock game (docs/_savegame.md)
;   bits 0-1 Constrictor: 0 not offered, 1 hunting, 3 killed (set by the kill hook), 2 finished (paid)
;   bits 2-3 Thargoid plans (later), bits 4-6 hint stage 0-7 (7 = hints done, the ship waits at Orarra), bit 7 Trumbles offered (later)
mxKillScoreHigh        equ 0x38D9     ; BBC TALLY+1: at least 1 = 256 kill points
mxCurrentGalaxy        equ 0x38DC     ; 0-7
mxPresentSystemY       equ 0x390E
mxPresentSystemX       equ 0x3910
mxAddDEtoMoney         equ 0xFE6A     ; DE thousands of credits (COMMON2X)


missionsDockedEntry:                  ; = &1714, the fixed entry the docking code calls
    ld a,(mxThargonMissionVar)
    and a
    jp nz,mxChkMissions               ; an existing mission offer or reward is pending: its turn, returns to the docking code
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
    jr mxShowEnd

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
    add a,c                           ; string 2 (galaxy 1) or 3 (galaxy 2)
    jr mxShowEnd

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
    ld a,0x0B                         ; string 11
mxShowEnd:
    ld de,mxColorsMessage
    ld hl,0x0200
    call missionShow
    jp mxActionsAtEndOfMessage

; Like drawFlipChart (commonxx.asm) but prints string A of missionTextTable: frame, view 14, colours DE, cursor HL.
missionShow:
    push af
    push hl
    push de
    call mxDrawFrame
    ld a,0x5C
    call mxPrintStringA
    ld a,0x0E
    ld (mxViewdirection),a
    pop de
    call mxSetColors
    pop hl
    ld (mxCharXY),hl
    pop af
    ld d,a
    ld hl,missionTextTable
    jp mxPrintStringScan

; Hint stages: galaxy (0-7), system x, system y, string number. Coordinates from the CPC name generator (docs/_missions.md section 7).
missionHintTable:
    db 0x00,149,101,0x04              ; Reesdice -> Arexe
    db 0x00,164, 89,0x05              ; Arexe -> galactic jump, Cearso
    db 0x01, 87,109,0x06              ; Cearso -> Errius
    db 0x01,184,149,0x07              ; Errius -> Inbibe
    db 0x01,152,146,0x08              ; Inbibe -> Ausar
    db 0x01,146,102,0x09              ; Ausar -> Usleri
    db 0x01,148, 68,0x0A              ; Usleri -> Orarra

; A = mission order 0..2 from the commander name at &38CB: rotate left and xor every letter up to the NUL, then mod 3
; (0: Constrictor, Plans, Trumbles; 1: Constrictor, Trumbles, Plans; 2: Trumbles, Constrictor, Plans). Name bytes after the NUL are stale.
missionOrder:
    ld hl,0x38CB
    xor a
missionOrderLoop:
    ld c,(hl)
    inc hl
    inc c
    dec c
    jr z,missionOrderMod
    rlca
    xor c
    jr missionOrderLoop
missionOrderMod:
    sub 3
    jr nc,missionOrderMod
    add a,3
    ret

; Strings of the mission table: 1-based, NUL-terminated, tokens as in stringsTable2 (references 0x81-0xD6 point into stringsTable2).
; Source text: missions_text.txt; regenerate with: python3 -I tools/textenc.py --asm src/elite/missions_text.txt > src/elite/missions_text.asm
missionTextTable:
    INCLUDE "missions_text.asm"

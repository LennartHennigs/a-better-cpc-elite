; Resident stub of the LARGEAXX tail (&1714-&1A3F), assembled with -DMISSIONS. It picks the active mission module, loads its overlay file
; (MISSIONC.BIN, MISSIONP.BIN, MISSIONT.BIN or MISSIONR.BIN) into the rest of the tail and jumps to it. The tail is reloaded with LARGEAXX at every docking, so the stub is always there.
; Overlay layout: +0 jp moduleEntry, +3 dw missionTextTable, then the module. An overlay file is the bytes from mxOverlayBase to mxOverlayEnd of a build with
; -DOVL_C, -DOVL_P, -DOVL_T or -DOVL_R (tools/build_dsk.py slices them by label). A module ends by `jp mxShowEnd` (message box, then back to the docking code) or `ret`.
    INCLUDE "missions_docked_defs.asm"

missionsDockedEntry:                  ; = &1714, the fixed entry the docking code calls (after loadLARGEAXX, in place of chkMissions)
    ld a,(mxThargonMissionVar)
    and a
    jp nz,mxChkMissions               ; an existing mission offer or reward is pending: its turn, returns to the docking code
    ld hl,(mxTrCount)
    ld a,h
    or l
    ret nz                            ; Trumbles aboard: one mission at a time, nothing else is offered
    ld a,(missionState)
    ld b,a
    and 0x8F
    cp 0x02
    jr z,mxTrumbles                   ; the Trumbles are offered once, in the gap after the Constrictor (bits 0-1 = 2), before the plans (bits 2-3 = 0), offer not made (bit 7 = 0); bits 4-6 are ignored
mxChain:
    ld a,(mxKillScoreHigh)
    and a
    ret z                             ; under 256 kill points no chain mission can be active: do not touch the disk
    ld a,b
    and 0x03
    cp 0x02
    jr z,mxPlansPart
    ld c,"C"                          ; Constrictor not finished
    and a
    jr z,mxCOffer                     ; 0: not offered yet
    cp 0x03
    jr z,mxLoadC                      ; 3: killed, the reward is paid by the module
    ld a,b                            ; 1: hunting. The module is only needed at the system of the current hint stage
    rrca
    rrca
    rrca
    rrca
    and 0x07
    cp 0x07
    ret nc                            ; stage 7: all hints given, the Orarra spawn is a flight matter
    jr mxStageRow
mxCOffer:
    ld a,(mxCurrentGalaxy)
    cp 0x02
    ret nc                            ; offered in galaxy 1 and 2 only
mxLoadC:
    ld a,c
    jr mxLoadModule
mxPlansPart:
    ld c,"P"
    ld a,b
    and 0x0C
    cp 0x0C
    jr z,mxAfterPlans
    and a
    jr nz,mxPlansRow
    ld a,(mxKillScoreHigh)            ; plans not offered yet: 1280 kill points and galaxy 3
    cp 0x05
    ret c
    ld a,(mxCurrentGalaxy)
    cp 0x02
    ret nz
    jr mxLoadC
mxPlansRow:
    rrca
    rrca                              ; 1 (go to Ceerdi) or 2 (go to Birera)
    add a,0x06                        ; rows 7 and 8
mxStageRow:                           ; A = row of mxStageTable: load module C only when the player is at that system
    ld e,a
    add a,a
    add a,e
    ld e,a
    ld d,0
    ld hl,mxStageTable
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
    jr mxLoadC
mxAfterPlans:                         ; plans finished: the stolen police ship (missionState bits 4-6, scheduled when the plans are delivered), then the asteroids
    ld a,b
    and 0x70
    ret z                             ; 0: no mission scheduled (a commander from before this chain)
    cp 0x50
    jr nc,mxRocks                     ; 5: the first one is paid
    bit 4,a
    ret nz                            ; 1 and 3 (waiting, hunting) are flight matters
    jr mxLoadC                        ; 2 ready: the module (c = "P") makes the offer; 4 killed: it pays
mxRocks:                              ; the asteroids: &38FE bits 0-1 0 offer, 1 clearing (flight), 2 reward (module MISSIONR), 3 paid
    ld a,(mxMissionByte2)
    bit 0,a
    ret nz
    ld a,"R"
    jr mxLoadModule
mxTrumbles:
    ld hl,(mxCredits)                 ; offer Trumbles from 5,000 Cr, the price (whole thousands word)
    ld de,-5
    add hl,de
    jp nc,mxChain                     ; carry when the thousands are 5 or more
    ld a,"T"
mxLoadModule:
    ld (mxOverlayName+7),a
    call mxLoadFile
    dw mxOverlayBase
    dw mxOverlayName
    jp mxOverlayBase

mxOverlayName:
    db "MISSION?"

; Where the stage-bound modules have something to do: galaxy (0-7), system x, system y. Rows 0-6 are the Constrictor hint stages (Reesdice, Arexe, Cearso, Errius,
; Inbibe, Ausar, Usleri), rows 7 and 8 the plans (Ceerdi, Birera). Coordinates from the CPC name generator (docs/_missions.md section 7). The stub loads the overlay
; only at the system the current stage asks for, so the 1.75 s disk load is not paid at every docking of a hunt.
mxStageTable:
    db 0,149,101
    db 0,164,89
    db 1,87,109
    db 1,184,149
    db 1,152,146
    db 1,146,102
    db 1,148,68
    db 2,215,84
    db 2,63,72


; Message box for string A of the module's text table (word at overlay +3): frame, view 14, colours, cursor, key, back to the docking code.
mxShowEnd:
    ld de,mxColorsMessage
    ld hl,0x0200
    call missionShow
    jp mxActionsAtEndOfMessage

; Like drawFlipChart (commonxx.asm) but prints string A of the overlay's table: frame, view 14, colours DE, cursor HL.
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
missionPrint:                          ; A = string number: print it at the cursor (no box); returns
    ld d,a
    ld hl,(mxOverlayBase+3)           ; the module's missionTextTable
    jp mxPrintStringScan

mxOverlayBase:                        ; the overlay file is loaded here
    IFDEF OVL_C
    INCLUDE "missions_overlay_c.asm"
    ENDIF
    IFDEF OVL_P
    INCLUDE "missions_overlay_p.asm"
    ENDIF
    IFDEF OVL_T
    INCLUDE "missions_overlay_t.asm"
    ENDIF
    IFDEF OVL_R
    INCLUDE "missions_overlay_r.asm"
    ENDIF
mxOverlayEnd:

; Resident stub of the LARGEAXX tail (&1714-&1A3F), assembled with -DMISSIONS. It picks the active mission module, loads its overlay file
; (MISSIONC.BIN, MISSIONP.BIN or MISSIONT.BIN) into the rest of the tail and jumps to it. The tail is reloaded with LARGEAXX at every docking, so the stub is always there.
; Overlay layout: +0 jp moduleEntry, +3 dw missionTextTable, then the module. An overlay file is the bytes from mxOverlayBase to mxOverlayEnd of a build with
; -DOVL_C or -DOVL_P (tools/build_dsk.py slices them by label). A module ends by `jp mxShowEnd` (message box, then back to the docking code) or `ret`.
    INCLUDE "missions_docked_defs.asm"

missionsDockedEntry:                  ; = &1714, the fixed entry the docking code calls (after loadLARGEAXX, in place of chkMissions)
    ld a,(mxThargonMissionVar)
    and a
    jp nz,mxChkMissions               ; an existing mission offer or reward is pending: its turn, returns to the docking code
    ld hl,(mxTrCount)
    ld a,h
    or l
    ret nz                            ; Trumbles aboard: one mission at a time, nothing else is offered
    ld a,(mxKillScoreHigh)
    and a
    ret z                             ; under 256 kill points no mission can be active: do not touch the disk
    ld a,(missionState)
    ld b,a
    and 0x03
    cp 0x02
    ld a,"C"                          ; Constrictor not finished: its module
    jr nz,mxLoadModule
    ld a,b
    and 0x0C
    cp 0x0C
    ld a,"P"                          ; Thargoid plans not finished: its module
    jr nz,mxLoadModule
    bit 7,b
    ret nz                            ; the Trumbles offer was made already
    ld hl,(mxCredits)                 ; both finished: offer Trumbles at 5,017.6 Cr (whole thousands word, then the decicredits word)
    ld a,h
    and a
    jr nz,mxCashOk
    ld a,l
    cp 0x06
    jr nc,mxCashOk
    cp 0x05
    ret nz
    ld hl,(mxCredits+2)
    ld a,h
    and a
    jr nz,mxCashOk
    ld a,l
    cp 176
    ret c
mxCashOk:
    ld a,"T"
mxLoadModule:
    ld (mxOverlayName+7),a
    call mxLoadFile
    dw mxOverlayBase
    dw mxOverlayName
    jp mxOverlayBase

mxOverlayName:
    db "MISSION?"


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
mxOverlayEnd:

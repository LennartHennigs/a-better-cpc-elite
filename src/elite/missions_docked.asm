; Resident stub of the LARGEAXX tail (&1714-&1A3F), assembled with -DMISSIONS. It picks the active mission module, loads its overlay file
; (MISSIONC.BIN or MISSIONP.BIN) into the rest of the tail and jumps to it. The tail is reloaded with LARGEAXX at every docking, so the stub is always there.
; Overlay layout: +0 jp moduleEntry, +3 dw missionTextTable, then the module. An overlay file is the bytes from mxOverlayBase to mxOverlayEnd of a build with
; -DOVL_C or -DOVL_P (tools/build_dsk.py slices them by label). A module ends by `jp mxShowEnd` (message box, then back to the docking code) or `ret`.
    INCLUDE "missions_docked_defs.asm"

    jp mxDockEntry                    ; &1714: the docking code calls here (after loadLARGEAXX, in place of chkMissions)
    jp mxLaunchEntry                  ; &1717: the launch sequence calls here (in place of its first call, loadIndicator)

missionsDockedEntry:
mxDockEntry:
    ld a,(mxThargonMissionVar)
    and a
    jp nz,mxChkMissions               ; an existing mission offer or reward is pending: its turn, returns to the docking code
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
    ret z                             ; Thargoid plans finished too: nothing left to load
    ld a,"P"
mxLoadModule:
    ld (mxOverlayName+7),a
    call mxLoadFile
    dw mxOverlayBase
    dw mxOverlayName
    jp mxOverlayBase

mxOverlayName:
    db "MISSION?"

; Launch: make sure the flight image the state asks for is in the COMMONXX tail (&9D9E: vector table, id byte at &9DAD, code), then carry on with loadIndicator.
; "C" while the Constrictor hunt is on (state 1 or 3), "P" while the plans are aboard, else "0" (the default image). Nothing is loaded when the right image is there.
mxLaunchEntry:
    ld a,(missionState)
    ld b,a
    and 0x03
    jr z,mxFlightNone                 ; Constrictor not offered
    cp 0x02
    ld a,"C"
    jr nz,mxFlightGo                  ; hunting or killed
    ld a,b
    and 0x0C
    cp 0x08
    ld a,"P"
    jr z,mxFlightGo                   ; plans aboard
mxFlightNone:
    ld a,"0"
mxFlightGo:
    ld hl,mxFlightLoaded
    cp (hl)
    jp z,mxLoadIndicator              ; already in RAM
    ld (mxFlightName+7),a
    call mxLoadFile
    dw mxFlightBase
    dw mxFlightName
    jp mxLoadIndicator

mxFlightName:
    db "MFLIGHT?"

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
mxOverlayEnd:

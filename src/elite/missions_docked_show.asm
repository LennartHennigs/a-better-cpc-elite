; Shared by the docked mission modules: show string A of missionTextTable in a message box and wait for a key (jp, returns to the docking code).
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

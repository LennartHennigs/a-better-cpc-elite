; Trumbles module (offer only; the breeding is in the flight image MFLIGHTT). Loaded at mxOverlayBase by the stub in missions_docked.asm, which loads it at a docking after the Constrictor reward and before the plans offer (missionState & 0x8F == 2)
; when no Trumbles are aboard, the offer was not made yet (missionState bit 7) and cash is at least 5,000 Cr.
; The offer is recorded (bit 7) whatever the answer. Y pays 5,000 Cr (5 thousand) and gives one Trumble (count 1 in &3905).
    jp mxModuleEntry
    dw missionTextTable
mxModuleEntry:
    ld hl,missionState
    set 7,(hl)                        ; the offer is made once
    ld a,0x01
    ld de,mxColorsMessage
    ld hl,0x0200
    call missionShow                  ; "... 5000 CR (Y/N)?"
    call mxWaitForKeypress
    cp "Y"
    ret nz                            ; declined: back to the docking code, which redraws the docked screen
    ld de,0x0005
    call mxSbcDEfromMoney
    ret c                             ; cannot pay (checked by the stub, so not expected)
    ld hl,0x0001
    ld (mxTrCount),hl
    ld a,0x02
    jp mxShowEnd

; Strings (source missions_text_t.txt; regenerate with python3 -I tools/textenc.py --asm src/elite/missions_text_t.txt > src/elite/missions_text_t.asm)
missionTextTable:
    INCLUDE "missions_text_t.asm"

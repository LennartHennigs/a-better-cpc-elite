; Trumbles module and the stolen police ship (Elite Plus mission 4: offer 0 -> 1 here, the flight image V spawns the Viper at Birera and sets 2 when it dies, the reward is paid here); Trumbles (offer only; the breeding is in the flight image MFLIGHTT). Loaded at mxOverlayBase by the stub in missions_docked.asm, which only loads it
; when the Constrictor and the plans are finished, no Trumbles are aboard, the offer was not made yet (missionState bit 7) and cash is at least 5,017.6 Cr.
; The offer is recorded (bit 7) whatever the answer. Y pays 5,000 Cr (5 thousand) and gives one Trumble (count 1 in &3905).
    jp mxModuleEntry
    dw missionTextTable
mxModuleEntry:
    ld a,(missionState)
    and 0x70
    cp 0x50
    jr nz,mxTrumbleOffer              ; the asteroid stage is not 'paid' (a commander without the asteroid chain): Trumbles only
    ld hl,mxAsteroidCount             ; stolen police ship (state in &38FE bits 0-1: 0 not offered, 1 hunting, 2 killed, 3 paid); the stub loads this module at 0 and 2 and, with 3, for the Trumbles
    ld a,(hl)
    and 0x03
    cp 0x03
    jr z,mxTrumbleOffer
    inc (hl)                          ; 0 -> 1: offer. 2 -> 3: reward
    ld a,(hl)
    cp 0x03
    jr z,mxPoliceReward
    ld a,0x03
    jp mxShowEnd
mxPoliceReward:
    ld de,0x0004
    call mxAddDEtoMoney
    ld a,0x04
    jp mxShowEnd
mxTrumbleOffer:
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

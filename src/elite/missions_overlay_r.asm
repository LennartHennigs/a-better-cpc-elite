; Asteroid bombardment module (Elite Plus mission 6), the second mission after the plans. Loaded at mxOverlayBase by the stub when the first mission is paid (missionState bits 4-6 = 5)
; and the state in &38FE bits 0-1 is 0 (offer) or 2 (cleared: reward). Offer: state 1 and 20 asteroids to destroy at Ceerdi (the byte becomes &51); reward: state 3 and 6,000 Cr.
    jp mxModuleEntry
    dw missionTextTable
mxModuleEntry:
    ld hl,mxAsteroidCount
    ld a,(hl)
    and 0x03
    jr nz,mxRocksReward
    ld (hl),0x51                      ; 20 << 2, state 1
    ld a,0x01
    jp mxShowEnd
mxRocksReward:
    inc (hl)                          ; 2 -> 3
    ld de,0x0006
    call mxAddDEtoMoney
    ld a,0x02
    jp mxShowEnd

; Strings (source missions_text_r.txt; regenerate with python3 -I tools/textenc.py --asm src/elite/missions_text_r.txt > src/elite/missions_text_r.asm)
missionTextTable:
    INCLUDE "missions_text_r.asm"

; Sell the whole hold with the A key in the sell menu (-DENHANCED). Entered from csGotoInventoryScreen (largeaxx.asm) with the key that left the quantity prompt in A;
; any other key goes straight to the inventory as before. Sells every good from the first one with the same row handler the prompts use, then leaves the menu.
sellAllEntry:
    cp "A"-2                        ; reAskifNotAllSold counts the key down twice (dec a / dec a) on its way here; the other way in, the end of the menu loop, arrives with A = 0x11 (cp 0x11, sub_403E keeps A)
    jr nz,sellAllDone
    call setPointerstoBeginofInventories
sellAllLoop:
    ld hl,(SCREEN+0x2FF8)                  ; price pointer and hold pointer step as in csLoopThroughInventory
    inc hl
    inc hl
    ld (SCREEN+0x2FF8),hl
    ld hl,(SCREEN+0x2FF6)
    inc hl
    ld (SCREEN+0x2FF6),hl
    ld a,(hl)
    and a
    jr z,sellAllNext                ; none of this good
    ld (todo_storestringnumber),a
    call sellQuantityofGood
sellAllNext:
    ld hl,storedByteVariable
    inc (hl)
    ld a,(hl)
    cp 0x11
    jr c,sellAllLoop
    call sfxForKeyInput             ; the sound of a trade (one for the whole hold; the prompt path adds a 1.6 s delay we skip)
sellAllDone:
    jp Inventory
sellAllEnd:

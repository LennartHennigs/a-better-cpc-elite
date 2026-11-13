; Title text cache (bank 6, at 0x6540: appended to fill128.bin by tools/build_dsk128.py; the record file ends before it). Called from dbFlip6 in fill.asm through
; TT_HOOK / TT_OFF. Needs from the build: DBBASES (dbBases in fill.asm), DB_COPY, DB_CURCFG, DB_SHIPNR, DB_PRT1, DB_PRT2 (tools/check_src128.sh).
    DEVICE AMSTRADCPC464
    ORG 0x6540
TT_ST       equ 0x4F30
TT_KEY      equ 0x4F31
TT_CNT      equ 0x4F32
    jp ttHook                           ; 0x6540 TT_HOOK
    jp ttOff                            ; 0x6543 TT_OFF
dbBases     equ DBBASES
; --- title text cache -------------------------------------------------------------------------------------------------------------------------------------------------------
; The two title screens print a heading (text row 1) and a prompt (text row 14) into the bitmap every frame, which costs about 65 ms of a 320 ms frame. The titles draw straight into
; the displayed bank (single buffer), so the other bank is idle: after one frame that printed the text, its 8 lines x 52 bytes (columns 8-59) of both rows are copied to the same
; places of the other bank, and the two printers (printSplashscreen1, printPressSpace) are patched to a `ret`. Every later frame copies the rows back after the bitmap transfer
; (about 5 ms). The cache belongs to one title ship index (splash2Shipnr changes on every screen change and cursor key), a different index, or any flight frame, unpatches the
; printers again. The copy overwrites ship pixels inside those rows with the ones of the capture frame: only a ship reaching the first or last text row would show it.
ttHook:
    ld a,(TT_ST)
    and a
    jr z,ttCapture
    ld a,(DB_SHIPNR)
    ld hl,TT_KEY
    cp (hl)
    jr nz,ttOff                         ; another ship: print again (this frame has no text, the next one has)
    ld a,(DB_CURCFG)
    call dbBases                        ; HL = displayed bank, DE = the other one
    ex de,hl                            ; restore: other -> displayed
    jr ttCopyAll
ttCapture:
    ld a,(DB_CURCFG)
    call dbBases
    call ttCopyAll                      ; displayed -> other
    ld a,(DB_SHIPNR)
    ld (TT_KEY),a
    ld a,1
    ld (TT_ST),a
    ld a,0xC9                           ; ret
    ld (DB_PRT1),a
    ld (DB_PRT2),a
    ret
ttOff:
    xor a
    ld (TT_ST),a
    ld a,0xCD                           ; call: both printers start with one
    ld (DB_PRT1),a
    ld (DB_PRT2),a
    ret
ttCopyAll:
    ld bc,0x48                          ; text row 1, byte 8
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    call ttBand
    ld bc,0xC340                        ; the 8 lines moved 0x4000 on: back, and to text row 14 (0x340 further)
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
ttBand:
    ld a,8
    ld (TT_CNT),a
ttLine:
    ld bc,52
    call DB_COPY
    ld bc,0x0800-52
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld a,(TT_CNT)
    dec a
    ld (TT_CNT),a
    jr nz,ttLine
    ret

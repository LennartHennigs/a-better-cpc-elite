; Ship viewer of the 128K disk (RUN"SHOWSHPS): the page flip prototype (tools/proto_fill/flip.asm) with the ships of the 128K build (tools/mk_viewer128.py), 11 per RAM bank in banks 4-6, loaded by SHOWSHPS.BAS
; (OUT &7FC4..&7FC6, LOAD"SHIPSn",&4000); cursor left/right select the ship, Q returns to BASIC. Derived from tools/proto_fill/flip.asm: keep changes there in mind.
; Original header of the prototype:
; Standalone (not part of the game). Build and run: tools/proto_fill/run.py --flip. Data: tools/proto_fill/gen.py --ships (work/proto_fill/).
;
; Screen pages: physical bank 1 (CRTC &4000) and bank 3 (CRTC &C000). The CPU always draws at &4000: RAM config C1 (banks 0,1,2,7) shows bank 1
; there, C3 (0,3,2,7) shows bank 3. Both configs show the extra bank 7 at &C000, where the fill module and its tables live, so the module is always
; visible while drawing and no per-call paging is needed. After a frame the CRTC start address (R12) is switched to the page just drawn, at vsync.
; Each page remembers the bounding box of what it showed two frames ago and erases only that.
; The ships (15, 1824 bytes each: 160 bytes of triangles and 16 projected frames) are part of FLIP.BIN, loaded at &1000 (the file runs from &1000 to
; &9DFF); at start the program copies them into the extra banks 4 and 5 (8 and 7 ships), and the selected ship is copied into main RAM at &8800 as needed.
; Cursor left / right select the ship.
; Main RAM (bank 2, always visible): &8000 code, &8800 selected ship, &9500 screen row tables (base &4000), &9700 variables, &9900 staging copy of the
; module image, &9D00 the ROM font (characters 32-127).
    DEVICE AMSTRADCPC464

NPTS      equ 32
FRAMESZ   equ 104               ; x[32], y[32], order[36], bounding box xmin xmax ymin ymax
SHIPBUF   equ 0x8800            ; the selected ship: 160 bytes of triangles (v0 v1 v2 pattern), then the frames
FRAMES    equ SHIPBUF + 160
NFRAMES   equ 12
SHIPSZ    equ 160 + NFRAMES * FRAMESZ
FONT      equ 0x9D00
ROWLOP    equ 0x95
ROWHIP    equ 0x96
XLP       equ 0xCB              ; the module and its tables, in bank 7 as seen at &C000
XRP       equ 0xCC
COLP      equ 0xCD
LMP       equ 0xCE
RMP       equ 0xCF
EDB       equ 0xC800            ; unrolled edge block, 128 lines of 4 bytes, then ret (generated at start)
EDEND     equ EDB + 512
SQLP      equ 0xD0              ; quarter squares: low bytes at &D000-&D1FF, high bytes at &D200-&D3FF
RLOP      equ 0xD4              ; 65535 / dy for dy = 1..127: low bytes &D400, high bytes &D500
RHIP      equ 0xD5
STAGE     equ 0x9900
FACETS    equ SHIPBUF            ; the module reads the selected ship's triangles from main RAM
SHIPSRC   equ 0x1000            ; where the ship data sit after the load: ship n at SHIPSRC + n * SHIPSZ

; variables (main RAM)
V_FRAMEP  equ 0x9700            ; word: frame data being drawn
V_ORDP    equ 0x9702            ; word: next entry of its order list
V_X0      equ 0x9704            ; X0 Y0 X1 Y1 X2 Y2
V_Y0      equ 0x9705
V_X1      equ 0x9706
V_Y1      equ 0x9707
V_X2      equ 0x9708
V_Y2      equ 0x9709
V_PATE    equ 0x970A
V_PATO    equ 0x970B
V_YMIN    equ 0x970C
V_YMAX    equ 0x970D
V_XA      equ 0x970E
V_ROWS    equ 0x970F
V_NEG     equ 0x9710
V_ML      equ 0x9711
V_MR      equ 0x9712
V_NMID    equ 0x9713
V_T0      equ 0x9714            ; word
V_TLP     equ 0x9716            ; word
V_CURF    equ 0x9718            ; word
V_YA      equ 0x971A
V_Y       equ 0x971B
V_PAGE    equ 0x971C
V_PATC    equ 0x971D
V_DX      equ 0x971E
V_BX0     equ 0x971F
isrCount  equ 0x9720            ; word, 300 Hz
has128    equ 0x9724            ; 1 = a second 64 KB bank set answers, 0 = no banking
frameNo   equ 0x9725
V_NB      equ 0x9727
V_PB      equ 0x9728            ; box to erase now: xmin xmax ymin ymax
V_PIX     equ 0x972C            ; page being drawn: 0 = bank 1 (config C1), 1 = bank 3 (config C3)
V_BOXES   equ 0x9730            ; boxes of the two pages, 4 bytes each
V_SHIP    equ 0x9740            ; selected ship
V_KPREV   equ 0x9741            ; keys down at the last frame: bit 0 left, bit 1 right
V_NAMEFL  equ 0x9742            ; frames still to draw the name and the hint into (one per page)
V_TXT     equ 0x9744            ; word: screen address of the next character
tickLog   equ 0x9800            ; per frame: word ticks for the erase, word ticks for the draw

    ORG 0x8000
start:
    ld (savedSP),sp             ; back to BASIC with Q
    ld sp,0x94FE
    call 0xB906                 ; KL L ROM ENABLE: RUN starts a program with the lower ROM off
    ld hl,0x3900                ; the ROM font, characters 32..127
    ld de,FONT
    ld bc,96 * 8
    ldir
    call 0xB909                 ; KL L ROM DISABLE
    di
    call detect128
    ld (has128),a
    and a
    jr z,setup
    ei                          ; let the firmware run a few seconds more: it switches the disc motor off
    ld b,64
mWait:
    halt
    halt
    halt
    halt
    djnz mWait
setup:
    di
    ld bc,0x7F8D                ; both ROMs off, mode 1
    out (c),c
    ld hl,palette
    ld bc,0x7F00
palLoop:
    out (c),c                   ; select pen / border C
    ld a,(hl)
    inc hl
    out (c),a                   ; its colour (0x40 | hardware ink)
    inc c
    ld a,c
    cp 5
    jr nz,palLoop
    ld hl,0x0038                ; our interrupt handler
    ld (hl),0xC3
    inc hl
    ld (hl),isr & 255
    inc hl
    ld (hl),isr >> 8
    ld hl,0xC000                ; clear the screen
    ld de,0xC001
    ld bc,0x3FFF
    ld (hl),0
    ldir
    xor a
    ld (isrCount),a
    ld (isrCount + 1),a
    ld (frameNo),a
    ld (V_PIX),a
    ld (V_SHIP),a
    ld (V_KPREV),a
    ld a,(has128)
    and a
    jr nz,have128
    ld hl,0xC000 + 20 * 80 + 36 ; no banking: a bar of red (pen 3) at the top, and stop
    ld de,0xC001 + 20 * 80 + 36
    ld bc,8
    ld (hl),0xFF
    ldir
    ei
stop:
    jr stop
have128:
    ld hl,0x4000                ; clear the other screen page (bank 1)
    ld de,0x4001
    ld bc,0x3FFF
    ld (hl),0
    ldir
    ld bc,0x7FC7                ; bank 7 at &4000: copy the module there, build its tables
    out (c),c
    ld hl,STAGE
    ld de,0x4000
    ld bc,modEnd - 0xC000
    ldir
    call initBank
    ld bc,0x7FC0
    out (c),c
    xor a
    call loadShip
    ei
    call resetShow
mainLoop:
    call readKeys               ; cursor left / right: previous / next ship
    ld b,a
    ld hl,V_KPREV
    ld a,(hl)
    ld (hl),b
    xor b
    and b                       ; keys that went down since the last frame
    jr z,noKey
    ld c,a
    bit 2,c
    jp nz,quit                  ; Q
    ld a,(V_SHIP)
    bit 1,c
    jr z,keyLeft
    inc a
    cp NSHIPS
    jr c,keySet
    xor a
    jr keySet
keyLeft:
    and a
    jr nz,keyDec
    ld a,NSHIPS
keyDec:
    dec a
keySet:
    ld (V_SHIP),a
    call loadShip
    call resetShow
noKey:
    ld a,(V_PIX)                ; draw page: config C1 (bank 1) or C3 (bank 3) at &4000
    add a,a
    add a,0xC1
    ld c,a
    ld b,0x7F
    out (c),c
    ld a,(V_PIX)                ; this page's box (what it showed two frames ago)
    add a,a
    add a,a
    ld e,a
    ld d,0
    ld hl,V_BOXES
    add hl,de
    ld de,V_PB
    ld bc,4
    ldir
    ld hl,(isrCount)
    ld (V_T0),hl
    call clearBox
    ld a,(V_NAMEFL)             ; after a change of ship the name and the hint go into both pages
    and a
    call nz,showName
    ld hl,(isrCount)            ; ticks spent erasing
    ld de,(V_T0)
    or a
    sbc hl,de
    ld a,(frameNo)              ; tickLog[frameNo] = (erase ticks, draw ticks)
    add a,a
    add a,a
    ld e,a
    ld d,tickLog >> 8
    ld a,l
    ld (de),a
    inc e
    ld a,h
    ld (de),a
    inc e
    ld (V_TLP),de
    ld hl,(isrCount)
    ld (V_T0),hl
    ld hl,(V_CURF)
    call 0xC000                 ; the module, in bank 7 at &C000
    ld hl,(isrCount)            ; ticks spent drawing
    ld de,(V_T0)
    or a
    sbc hl,de
    ld de,(V_TLP)
    ld a,l
    ld (de),a
    inc e
    ld a,h
    ld (de),a
    ld hl,(V_CURF)              ; this frame's box goes to the page
    ld de,100
    add hl,de
    push hl
    ld a,(V_PIX)
    add a,a
    add a,a
    ld e,a
    ld d,0
    ld hl,V_BOXES
    add hl,de
    ex de,hl
    pop hl
    ld bc,4
    ldir
    ld bc,0xF500                ; wait for the start of vsync, then show the page just drawn (R12 = &10 / &30)
wv1:
    in a,(c)
    rra
    jr c,wv1
wv2:
    in a,(c)
    rra
    jr nc,wv2
    ld a,(V_PIX)
    and a
    ld a,0x10
    jr z,flip1
    ld a,0x30
flip1:
    ld bc,0xBC0C
    out (c),c
    ld bc,0xBD00
    out (c),a
    ld a,(V_PIX)
    xor 1
    ld (V_PIX),a
frameDone:
    nop                         ; the runner breaks here, once per frame
    ld a,(frameNo)
    inc a
    ld hl,(V_CURF)
    ld de,FRAMESZ
    add hl,de
    cp NFRAMES
    jr c,fnOk
    xor a
    ld hl,FRAMES
fnOk:
    ld (frameNo),a
    ld (V_CURF),hl
    jp mainLoop

; A new ship: start at its first frame, erase the whole view on both pages, draw the name into both pages.
resetShow:
    ld hl,FRAMES
    ld (V_CURF),hl
    xor a
    ld (frameNo),a
    ld hl,V_BOXES               ; box 0..255 x 0..127 for both pages
    ld b,2
rsBox:
    ld (hl),0
    inc hl
    ld (hl),255
    inc hl
    ld (hl),0
    inc hl
    ld (hl),127
    inc hl
    djnz rsBox
    ld a,2
    ld (V_NAMEFL),a
    ret

; Q: the firmware's world again, then back to BASIC (SHOWSHPS.BAS sets MODE 1 afterwards)
quit:
    di
    ld bc,0x7FC0
    out (c),c
    ld bc,0x7F81                ; mode 1, both ROMs on
    out (c),c
    ld hl,0x0038                ; the firmware's interrupt handler: JP &B939
    ld (hl),0xC3
    inc hl
    ld (hl),0x39
    inc hl
    ld (hl),0xB9
    ld bc,0xBC0C                ; CRTC R12/R13: the screen at &C000 again
    out (c),c
    ld bc,0xBD30
    out (c),c
    ld bc,0xBC0D
    out (c),c
    ld bc,0xBD00
    out (c),c
    ld sp,(savedSP)
    ei
    ret

printMsg:                       ; HL = zero-terminated text, through the firmware (TXT OUTPUT)
    ld a,(hl)
    and a
    ret z
    inc hl
    call 0xBB5A
    jr printMsg

; A = ship number: copy its SHIPSZ bytes from RAM bank 4, 5 or 6 (SHIPS_PER_BANK = 11 ships each) to SHIPBUF
loadShip:
    ld b,0xC4                   ; B = the bank configuration
    ld hl,0x4000
lsBank:
    cp 11
    jr c,lsIn
    sub 11
    inc b
    jr lsBank
lsIn:
    and a
    jr z,lsGo
    ld c,a
    ld de,SHIPSZ
lsAdd:
    add hl,de
    dec c
    jr nz,lsAdd
lsGo:
    ld c,b
    ld b,0x7F
    out (c),c
    ld de,SHIPBUF
    ld bc,SHIPSZ
    ldir
    ld bc,0x7FC0
    out (c),c
    ret

; A = bits of the cursor keys now down: bit 0 left, bit 1 right (PPI keyboard lines 1 and 0)
readKeys:
    ld bc,0xF40E
    out (c),c
    ld bc,0xF6C0
    out (c),c
    ld bc,0xF600
    out (c),c
    ld bc,0xF792
    out (c),c
    ld bc,0xF640                ; line 0: bit 1 = cursor right (0 = down)
    out (c),c
    ld b,0xF4
    in a,(c)
    cpl
    and 2
    ld d,a
    ld bc,0xF641                ; line 1: bit 0 = cursor left
    out (c),c
    ld b,0xF4
    in a,(c)
    cpl
    and 1
    or d
    ld d,a
    ld bc,0xF648                ; line 8: bit 3 = Q
    out (c),c
    ld b,0xF4
    in a,(c)
    cpl
    and 8
    rrca
    or d
    ld d,a                      ; bit 2 = Q
    ld bc,0xF782
    out (c),c
    ld a,d
    ret

; the name of the ship and the hint, into the page that is the draw page now
showName:
    dec a
    ld (V_NAMEFL),a
    ld hl,0x4000 + 248          ; 8 lines of 48 bytes: text row 3, bytes 8..55
    call clearText
    ld hl,0x4000 + 22 * 80 + 8
    call clearText
    ld a,(V_SHIP)               ; HL = nameTable + 17 * ship
    ld l,a
    ld h,0
    ld e,l
    ld d,h
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,de
    ld de,nameTable
    add hl,de
    ld de,0x4000 + 248
    call drawText
    ld hl,hint
    ld de,0x4000 + 22 * 80 + 8
    jp drawText

clearText:                      ; zero 8 lines (0x800 apart) of 48 bytes from HL
    ld b,8
ctRow:
    push hl
    push bc
    ld d,h
    ld e,l
    inc de
    ld (hl),0
    ld bc,47
    ldir
    pop bc
    pop hl
    ld a,h
    add a,8
    ld h,a
    djnz ctRow
    ret

drawText:                       ; HL = zero-terminated text, DE = screen address of the first character cell (mode 1, 2 bytes wide, pen 3)
    ld (V_TXT),de
dtChar:
    ld a,(hl)
    and a
    ret z
    inc hl
    push hl                     ; the text pointer
    sub 32
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,FONT
    add hl,de                   ; HL = glyph
    ld de,(V_TXT)               ; DE = top line of the cell
    ld b,8
dtRow:
    ld a,(hl)                   ; glyph row, 8 pixels = 2 mode 1 bytes; a nibble n becomes the byte n * 17 (pen 3 where the pixel is set)
    inc hl
    push hl
    ld c,a
    rrca
    rrca
    rrca
    rrca
    and 15
    ld l,a
    rlca
    rlca
    rlca
    rlca
    or l
    ld (de),a
    inc de
    ld a,c
    and 15
    ld l,a
    rlca
    rlca
    rlca
    rlca
    or l
    ld (de),a
    dec de
    ld a,d                      ; next line of the cell: +0x800
    add a,8
    ld d,a
    pop hl
    djnz dtRow
    ld hl,(V_TXT)               ; next cell: two bytes right
    inc hl
    inc hl
    ld (V_TXT),hl
    pop hl
    jr dtChar

hint:   db "<  >  SELECT SHIP   Q QUIT",0
savedSP: dw 0
    INCLUDE "../../work/viewer128/names.inc"

; A = 1 when the RAM banking port answers: write 0xA5 at &4000, write 0x5A at &4000 with bank 4 mapped, read &4000 with the normal
; map again. A 464 or 664 ignores the port and reads 0x5A back.
detect128:
    ld hl,0x4000
    ld e,(hl)                   ; keep the normal byte
    ld (hl),0xA5
    ld bc,0x7FC4
    out (c),c
    ld d,(hl)                   ; keep bank 4's byte
    ld (hl),0x5A
    ld bc,0x7FC0
    out (c),c
    ld a,(hl)
    ld (hl),e
    cp 0xA5
    jr nz,dt464
    ld bc,0x7FC4                ; put bank 4's own byte back
    out (c),c
    ld (hl),d
    ld bc,0x7FC0
    out (c),c
    ld a,1
    ret
dt464:
    xor a
    ret

clearBox:                       ; erase the bounding box of the last frame (bytes xmin>>2 .. xmax>>2, lines ymin..ymax)
    ld a,(V_PB + 3)
    ld hl,V_PB + 2
    sub (hl)
    ret c
    inc a
    ld b,a                      ; lines
    ld c,(hl)                   ; first line
    ld a,(V_PB)
    srl a
    srl a
    ld (V_BX0),a
    ld e,a
    ld a,(V_PB + 1)
    srl a
    srl a
    sub e
    inc a
    ld (V_NB),a                 ; bytes per line
cbRow:
    ld h,ROWHIP
    ld l,c
    ld a,(hl)
    ld h,ROWLOP
    ld l,(hl)
    ld h,a
    ld a,(V_BX0)
    add a,l
    ld l,a
    adc a,h
    sub l
    ld h,a
    ld d,h
    ld e,l
    ld (hl),0
    push bc
    ld a,(V_NB)
    dec a
    jr z,cbOne
    ld c,a
    ld b,0
    inc de
    ldir
cbOne:
    pop bc
    inc c
    djnz cbRow
    ret

; Runs with bank 7 mapped at &4000 (config C7): builds the tables the module uses (it runs at &C000, the same bank, in C1/C3).
initBank:
    ld hl,EDB - 0x8000          ; edge block: 128 times ld a,h / ld (de),a / inc e / add hl,bc, then ret
    ld b,128
ibEdge:
    ld (hl),0x7C
    inc hl
    ld (hl),0x12
    inc hl
    ld (hl),0x1C
    inc hl
    ld (hl),0x09
    inc hl
    djnz ibEdge
    ld (hl),0xC9
    ld e,0                      ; column, left mask, right mask by x
ibCol:
    ld d,COLP - 0x80
    ld a,e
    srl a
    srl a
    ld (de),a
    ld a,e
    and 3
    ld c,a
    ld b,0
    ld hl,ibLM
    add hl,bc
    ld a,(hl)
    inc d
    ld (de),a
    ld hl,ibRM
    add hl,bc
    ld a,(hl)
    inc d
    ld (de),a
    inc e
    jr nz,ibCol
    ld hl,0                     ; quarter squares n*n/4, n = 0..511: k*k for n = 2k, k*k + k for n = 2k+1
    ld de,0                     ; HL = k*k, DE = k
ibSq:
    push hl
    ld a,e                      ; n = 2k: BC = page, index
    add a,a
    ld c,a
    ld a,d
    rla
    add a,SQLP - 0x80
    ld b,a
    ld a,l
    ld (bc),a
    inc b
    inc b
    ld a,h
    ld (bc),a
    add hl,de                   ; n = 2k+1
    dec b
    dec b
    inc c
    jr nz,ibSq2
    inc b
ibSq2:
    ld a,l
    ld (bc),a
    inc b
    inc b
    ld a,h
    ld (bc),a
    pop hl                      ; (k+1)^2 = k*k + 2k + 1
    add hl,de
    add hl,de
    inc hl
    inc de
    ld a,d
    cp 1
    jr c,ibSq
    ld a,e
    and a
    jr nz,ibSq                  ; stop at k = 256
    ld c,1                      ; reciprocals 65535 / dy
ibRec:
    ld hl,0xFFFF
    ld b,16
    xor a
ibDiv:
    add hl,hl
    rla
    cp c
    jr c,ibDivS
    sub c
    inc l
ibDivS:
    djnz ibDiv
    ld d,RLOP - 0x80
    ld e,c
    ld a,l
    ld (de),a
    inc d
    ld a,h
    ld (de),a
    inc c
    ld a,c
    cp 128
    jr nz,ibRec
    ret
ibLM:   db 0xFF, 0x77, 0x33, 0x11
ibRM:   db 0x88, 0xCC, 0xEE, 0xFF

isr:
    push af
    push hl
    ld hl,(isrCount)
    inc hl
    ld (isrCount),hl
    pop hl
    pop af
    ei
    reti

palette:
    db 0x54, 0x44, 0x57, 0x4B   ; pens 0-3: black, blue, bright blue-cyan, bright white
    db 0x54                     ; border

    ASSERT $ <= SHIPBUF
    ORG 0x9500
    INCBIN "../../work/viewer128/rowtab_flip.bin"

; ---------------------------------------------------------------------------------------------------------------- bank 4 image
    ORG STAGE
    DISP 0xC000
module:
    jp drawShip
; dither patterns, (even line, odd line), pens 0-3 of mode 1: solid 1, solid 2, solid 3, 1/3, 2/3, 1/2 checkers
PATS:   db 0x0F,0x0F, 0xF0,0xF0, 0xFF,0xFF, 0x5F,0xAF, 0xF5,0xFA, 0x5A,0xA5
    INCLUDE "../../work/viewer128/winding.inc"     ; DOWNPAGE / UPPAGE: which edge table the downward edges of a visible triangle go to

; HL = frame data (x[32], y[32], order). Draws the faces in order, far to near.
drawShip:
    ld (V_FRAMEP),hl
    ld de,64
    add hl,de
    ld (V_ORDP),hl
dsLoop:
    ld hl,(V_ORDP)
    ld a,(hl)
    cp 0xFF
    ret z
    inc hl
    ld (V_ORDP),hl
    ld l,a                      ; HL = FACETS + 4 * face
    ld h,0
    add hl,hl
    add hl,hl
    ld de,FACETS
    add hl,de
    ld a,(hl)                   ; v0
    inc hl
    call getVertex              ; D = x, E = y
    ld a,d
    ld (V_X0),a
    ld a,e
    ld (V_Y0),a
    ld a,(hl)
    inc hl
    call getVertex
    ld a,d
    ld (V_X1),a
    ld a,e
    ld (V_Y1),a
    ld a,(hl)
    inc hl
    call getVertex
    ld a,d
    ld (V_X2),a
    ld a,e
    ld (V_Y2),a
    ld a,(hl)                   ; pattern index
    add a,a
    ld e,a
    ld d,0
    ld hl,PATS
    add hl,de
    ld a,(hl)
    ld (V_PATE),a
    inc hl
    ld a,(hl)
    ld (V_PATO),a
    call fillTri
    jr dsLoop

; A = vertex number -> D = x, E = y of this frame; HL kept
getVertex:
    push hl
    ld hl,(V_FRAMEP)
    ld c,a
    ld b,0
    add hl,bc
    ld d,(hl)
    ld bc,NPTS
    add hl,bc
    ld e,(hl)
    pop hl
    ret

fillTri:
    ld a,(V_Y0)                 ; B = ymin, C = ymax
    ld b,a
    ld c,a
    ld a,(V_Y1)
    cp b
    jr nc,ft1
    ld b,a
ft1:
    cp c
    jr c,ft2
    ld c,a
ft2:
    ld a,(V_Y2)
    cp b
    jr nc,ft3
    ld b,a
ft3:
    cp c
    jr c,ft4
    ld c,a
ft4:
    ld a,b
    ld (V_YMIN),a
    ld (V_Y),a
    ld a,c
    ld (V_YMAX),a
    ld a,(V_X0)
    ld b,a
    ld a,(V_Y0)
    ld c,a
    ld a,(V_X1)
    ld d,a
    ld a,(V_Y1)
    ld e,a
    call edge
    ld a,(V_X1)
    ld b,a
    ld a,(V_Y1)
    ld c,a
    ld a,(V_X2)
    ld d,a
    ld a,(V_Y2)
    ld e,a
    call edge
    ld a,(V_X2)
    ld b,a
    ld a,(V_Y2)
    ld c,a
    ld a,(V_X0)
    ld d,a
    ld a,(V_Y0)
    ld e,a
    call edge
    ; spans, ymin..ymax, in two passes (even lines, odd lines) so that the pattern is constant within a pass.
    ; Every row of the range was written in both tables by exactly one downward and one upward edge.
    ld a,(V_YMIN)
    call spPass
    ld a,(V_YMIN)
    inc a
spPass:                         ; A = first line
    ld hl,V_YMAX
    cp (hl)
    jr c,spPassGo
    ret nz                      ; beyond the last line
spPassGo:
    ld (V_Y),a
    and 1
    ld a,(V_PATE)
    jr z,spPatSet
    ld a,(V_PATO)
spPatSet:
    ld (V_PATC),a
spRow:
    ld a,(V_Y)
    ld e,a
    ld d,XRP
    ld a,(de)
    ld c,a                      ; xr
    ld d,XLP
    ld a,(de)                   ; xl
    cp c
    jr z,spOK
    jp nc,spNext                ; xl > xr: nothing
spOK:
    ld l,a
    ld h,COLP
    ld b,(hl)                   ; byte column of xl
    ld h,LMP
    ld a,(hl)
    ld (V_ML),a                 ; left mask
    ld l,c
    ld h,COLP
    ld a,(hl)
    sub b
    ld d,a                      ; bytes between the first and the last
    ld h,RMP
    ld c,(hl)                   ; right mask
    ld h,ROWHIP                 ; HL = row start
    ld l,e
    ld a,(hl)
    ld h,ROWLOP
    ld l,(hl)
    ld h,a
    ld a,b                      ; + first byte column
    add a,l
    ld l,a
    adc a,h
    sub l
    ld h,a
    ld a,(V_PATC)
    ld b,a
    ld a,d
    and a
    jr nz,spWide
    ld a,(V_ML)                 ; one byte: both masks
    and c
    ld c,a
    ld a,(hl)
    ld e,a
    xor b
    and c
    xor e
    ld (hl),a
    jr spNext
spWide:
    push hl                     ; right byte first
    ld a,l
    add a,d
    ld l,a
    adc a,h
    sub l
    ld h,a
    ld a,(hl)
    ld e,a
    xor b
    and c
    xor e
    ld (hl),a
    pop hl
    ld a,(V_ML)                 ; left byte
    ld c,a
    ld a,(hl)
    ld e,a
    xor b
    and c
    xor e
    ld (hl),a
    dec d                       ; whole bytes in between
    jr z,spNext
    ld a,b
    ld b,d
    inc hl
spMid:
    ld (hl),a
    inc hl
    djnz spMid
spNext:
    ld a,(V_Y)
    add a,2
    ld (V_Y),a
    ld hl,V_YMAX
    cp (hl)
    jp c,spRow
    jp z,spRow
    ret

; HL = A * C, by quarter squares: a*c = sq[a+c] - sq[|a-c|]
mulq:
    ld b,a
    add a,c
    ld l,a
    ld h,SQLP
    jr nc,mq1
    inc h
mq1:
    ld e,(hl)
    inc h
    inc h
    ld d,(hl)                   ; DE = sq[a+c]
    ld a,b
    sub c
    jr nc,mq2
    neg
mq2:
    ld l,a
    ld h,SQLP
    ld a,(hl)
    inc h
    inc h
    ld h,(hl)
    ld l,a                      ; HL = sq[|a-c|]
    ex de,hl
    or a
    sbc hl,de
    ret

; B = xa, C = ya, D = xb, E = yb: write x for every line of the edge into one edge table (down edges into one, up edges into the other)
; through the unrolled block at EDB (4 bytes per line, entered at the line count); x walks in 8.8 fixed point
edge:
    ld a,c
    cp e
    ret z                       ; flat edges add nothing
    jr c,edDown
    ld a,b                      ; going up: swap so that ya < yb
    ld b,d
    ld d,a
    ld a,c
    ld c,e
    ld e,a
    ld a,UPPAGE
    jr edGo
edDown:
    ld a,DOWNPAGE
edGo:
    ld (V_PAGE),a
    ld a,b
    ld (V_XA),a
    ld a,c
    ld (V_YA),a
    ld a,e
    sub c
    ld (V_ROWS),a               ; dy
    ld a,d
    sub b                       ; dx
    ld hl,V_NEG
    ld (hl),0
    jr nc,edPos
    neg
    ld (hl),1
edPos:
    ld (V_DX),a
    ld a,(V_ROWS)               ; slope = |dx| * (65535 / dy) / 256 = |dx| * Rh + (|dx| * Rl) / 256
    ld l,a
    ld h,RHIP
    ld c,(hl)
    ld a,(V_DX)
    call mulq
    push hl
    ld a,(V_ROWS)
    ld l,a
    ld h,RLOP
    ld c,(hl)
    ld a,(V_DX)
    call mulq
    pop de
    ld a,h
    add a,e
    ld l,a
    ld h,d
    jr nc,edSl1
    inc h
edSl1:
    ld a,(V_NEG)
    and a
    jr z,edSlope
    xor a                       ; HL = -HL
    sub l
    ld l,a
    sbc a,a
    sub h
    ld h,a
edSlope:
    ld b,h                      ; BC = slope
    ld c,l
    ld a,(V_ROWS)               ; lines = dy + 1; entry = EDEND - 4 * lines
    inc a
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    ex de,hl
    ld hl,EDEND
    or a
    sbc hl,de
    push hl
    pop iy
    ld a,(V_XA)
    ld h,a                      ; HL = xa + 0.5
    ld l,0x80
    ld a,(V_YA)
    ld e,a
    ld a,(V_PAGE)
    ld d,a
    jp (iy)

modEnd:
    ENT

    SAVEBIN "../../work/viewer128/viewer.bin", 0x8000, 0x9E00 - 0x8000

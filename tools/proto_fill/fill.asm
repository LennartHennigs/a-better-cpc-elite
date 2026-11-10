; Prototype: a ship drawn from filled triangles, with the triangle data and the fill routine in RAM bank 4 of a 6128.
; Standalone (not part of the game). Build and run: tools/proto_fill/run.py. Data comes from tools/proto_fill/gen.py (work/proto_fill/).
;
; Main RAM (always visible):   &8000 code, &8800 frames (projected vertices and draw order from the host), &9500 screen row tables,
;                              &9700 variables, &9900 staging copy of the bank image, &C000 screen
; Bank 4 (paged at &4000-&7FFF while drawing):  &4000 module: entry, patterns, triangle table, fill code, &4800 unrolled edge block,
;                              &4B00 edge tables, &4D00 column and mask tables, &5000 quarter squares, &5400 reciprocals
;                              (the tables and the edge block are generated at start by initBank)
; Interrupts stay on while the bank is paged; the 300 Hz handler would call &6000 (like the game's sound path, `jp &604A`), which is
; hidden then, so it skips that call while `paged` is set (GUARD=1). With -DGUARD=0 it calls it anyway.
    IFNDEF GUARD
GUARD equ 1
    ENDIF
    DEVICE AMSTRADCPC464

NPTS      equ 32
FRAMESZ   equ 104               ; x[32], y[32], order[40]
FRAMES    equ 0x8800
ROWLOP    equ 0x95
ROWHIP    equ 0x96
XLP       equ 0x4B              ; left/right edge tables and the column/mask tables live in bank 4 (&4B00-&4FFF)
XRP       equ 0x4C
COLP      equ 0x4D
LMP       equ 0x4E
RMP       equ 0x4F
EDB       equ 0x4800            ; unrolled edge block, 128 lines of 4 bytes, then ret (generated at start)
EDEND     equ EDB + 512
SQLP      equ 0x50              ; quarter squares: low bytes at &5000-&51FF, high bytes at &5200-&53FF
RLOP      equ 0x54              ; 65535 / dy for dy = 1..127: low bytes &5400, high bytes &5500
RHIP      equ 0x55
STAGE     equ 0x9900

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
V_NB      equ 0x9727
V_PB      equ 0x9728            ; bounding box of the last drawn frame: xmin xmax ymin ymax
isrCount  equ 0x9720            ; word, 300 Hz
paged     equ 0x9722            ; 1 while a bank is mapped at &4000
soundCnt  equ 0x9723            ; bumped by the stub at &6000
has128    equ 0x9724            ; 1 = a second 64 KB bank set answers, 0 = no banking
frameNo   equ 0x9725
tickLog   equ 0x9800            ; per frame: word ticks for clear, word ticks for draw

    ORG 0x8000
start:
    di
    ld sp,0x94FE
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
    ld (paged),a
    ld (soundCnt),a
    ld (frameNo),a
    call detect128
    ld (has128),a
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
    ld hl,0x6000                ; the stub the handler calls: ld hl,soundCnt / inc (hl) / ret
    ld (hl),0x21
    inc hl
    ld (hl),soundCnt & 255
    inc hl
    ld (hl),soundCnt >> 8
    inc hl
    ld (hl),0x34
    inc hl
    ld (hl),0xC9
    ld bc,0x7FC4                ; bank 4 at &4000
    out (c),c
    ld hl,STAGE
    ld de,0x4000
    ld bc,modEnd - 0x4000
    ldir
    call initBank
    ld bc,0x7FC0
    out (c),c
    ei
    ld hl,FRAMES
    ld (V_CURF),hl
    ld a,1                      ; empty box: ymin > ymax
    ld (V_PB + 2),a
    xor a
    ld (V_PB + 3),a
mainLoop:
    ld hl,(isrCount)
    ld (V_T0),hl
    call clearBox
    ld hl,(isrCount)            ; ticks spent clearing
    ld de,(V_T0)
    or a
    sbc hl,de
    ld a,(frameNo)              ; tickLog[frameNo] = (clear ticks, draw ticks)
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
    call drawShipTramp
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
    ld hl,(V_CURF)              ; remember this frame's box for the next erase
    ld de,100
    add hl,de
    ld de,V_PB
    ld bc,4
    ldir
frameDone:
    nop                         ; the runner breaks here, once per frame
    ld a,(frameNo)
    inc a
    ld hl,(V_CURF)
    ld de,FRAMESZ
    add hl,de
    cp 24
    jr c,fnOk
    xor a
    ld hl,FRAMES
fnOk:
    ld (frameNo),a
    ld (V_CURF),hl
    jp mainLoop

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

; HL = frame data. Maps bank 4, runs the module, maps the normal RAM again.
drawShipTramp:
    ld a,1
    ld (paged),a
    ld bc,0x7FC4
    out (c),c
    call 0x4000
    ld bc,0x7FC0
    out (c),c
    xor a
    ld (paged),a
    ret

; Runs with bank 4 mapped: builds the tables the module uses.
initBank:
    ld hl,EDB                   ; edge block: 128 times ld a,h / ld (de),a / inc e / add hl,bc, then ret
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
    ld d,COLP
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
    add a,SQLP
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
    ld d,RLOP
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
    IF GUARD
    ld a,(paged)
    and a
    jr nz,isrSkip
    ENDIF
    call 0x6000                 ; stands for the sound path of the game's handler
isrSkip:
    pop hl
    pop af
    ei
    reti

palette:
    db 0x54, 0x44, 0x57, 0x4B   ; pens 0-3: black, blue, bright blue-cyan, bright white
    db 0x54                     ; border

    ORG FRAMES
    INCBIN "../../work/proto_fill/frames.bin"
    ORG 0x9500
    INCBIN "../../work/proto_fill/rowtab.bin"

; ---------------------------------------------------------------------------------------------------------------- bank 4 image
    ORG STAGE
    DISP 0x4000
module:
    jp drawShip
; dither patterns, (even line, odd line), pens 0-3 of mode 1: solid 1, solid 2, solid 3, 1/3, 2/3, 1/2 checkers
PATS:   db 0x0F,0x0F, 0xF0,0xF0, 0xFF,0xFF, 0x5F,0xAF, 0xF5,0xFA, 0x5A,0xA5
FACETS:
    INCLUDE "../../work/proto_fill/facets.inc"
    INCLUDE "../../work/proto_fill/winding.inc"     ; DOWNPAGE / UPPAGE: which edge table the downward edges of a visible triangle go to

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

    SAVEBIN "../../work/proto_fill/proto.bin", 0x8000, 0x9E00 - 0x8000

; Filled hulls for the 128K build: polygon fill into the game's off-screen bitmap (&A000, 128 lines of 64 bytes, Mode 1, 4 pixels per byte).
; Assembled to run in RAM bank 6, which the far-call glue maps at &4000 (config C6). Everything it writes (edge tables, variables) lives in that bank;
; it reads the projected vertices from a resident buffer (VBUF in main RAM, because buf_5860 at &5860 is hidden by the window) and writes the bitmap in bank 2.
; Ported from tools/proto_fill/flip.asm (same edge walk, quarter squares, reciprocal table, masked spans); differences: the target is the linear bitmap, the
; vertices are the engine's (x magnitude, y magnitude, flag), triangles whose screen winding is wrong are culled here (back faces), vertices flagged off view
; (bit 7) drop their triangle (clip v1).
;
; Entry points (all with bank 6 mapped at &4000):
;   fillInit   &4003     once at start: builds the tables (edge block, column and mask tables, quarter squares, reciprocals, bitmap row table)
;   fillHull   &4000     A = ship type (0..19). Draws the hull's triangles from VBUF. Carry set on return = the type has no fill record (draw wireframe instead)
;
; Bank layout (page numbers are the high bytes of the addresses): code &4000-&4EFF, variables &4F00, XL &5000, XR &5100, column &5200, left mask &5300,
; right mask &5400, quarter squares &5500-&5800 (low bytes &5500, &5600; high bytes &5700, &5800), reciprocals &5900 (low) &5A00 (high), bitmap row table &5B00 (low)
; &5C00 (high), unrolled edge block &5D00-&5F00, fill records &6000 (tools/ship128.py: fill128.bin).
    DEVICE AMSTRADCPC464
    IFNDEF VBUF
VBUF        equ 0x9D9E          ; resident copy of the projected vertices (3 bytes each); the build sets the real address
    ENDIF
    IFNDEF VISPOS
VISPOS      equ 1               ; 1: a triangle is front facing when its screen cross product is positive (clockwise on screen); 0: negative
    ENDIF
BITMAP      equ 0xA000

XLP         equ 0x50
XRP         equ 0x51
COLP        equ 0x52
LMP         equ 0x53
RMP         equ 0x54
SQLP        equ 0x55
RLOP        equ 0x59
RHIP        equ 0x5A
ROWLOP      equ 0x5B
ROWHIP      equ 0x5C
EDB         equ 0x5D00
EDEND       equ EDB + 512
DATA        equ 0x6000

    IF VISPOS
DOWNPAGE    equ XRP             ; clockwise on screen: the downward edges are the right edges
UPPAGE      equ XLP
    ELSE
DOWNPAGE    equ XLP
UPPAGE      equ XRP
    ENDIF

V_X0        equ 0x4F00
V_Y0        equ 0x4F01
V_X1        equ 0x4F02
V_Y1        equ 0x4F03
V_X2        equ 0x4F04
V_Y2        equ 0x4F05
V_PATE      equ 0x4F06
V_PATO      equ 0x4F07
V_PATC      equ 0x4F08
V_YMIN      equ 0x4F09
V_YMAX      equ 0x4F0A
V_Y         equ 0x4F0B
V_XA        equ 0x4F0C
V_YA        equ 0x4F0D
V_ROWS      equ 0x4F0E
V_NEG       equ 0x4F0F
V_DX        equ 0x4F10
V_PAGE      equ 0x4F11
V_ML        equ 0x4F12
V_NTRI      equ 0x4F13
V_TRIP      equ 0x4F14          ; word: next triangle record
V_S1        equ 0x4F16          ; sign work for the cull test
V_M1        equ 0x4F17          ; word
V_M2        equ 0x4F19          ; word
V_S2        equ 0x4F1B

    ORG 0x4000
fillHull:
    jp fillHullGo
    jp fillInit                 ; &4003
fillHullGo:
    cp 20
    jr nc,fhNone
    add a,a
    ld l,a
    ld h,0
    ld de,DATA + 1
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld a,d
    or e
    jr z,fhNone
    ld hl,DATA                  ; offsets in the fill file count from its start
    add hl,de                   ; HL = record: ntri, flags, triangles
    ld a,(hl)
    ld (V_NTRI),a
    inc hl
    inc hl                      ; skip the flags byte
    ld (V_TRIP),hl
fhLoop:
    ld a,(V_NTRI)
    and a
    jr z,fhDone
    dec a
    ld (V_NTRI),a
    ld hl,(V_TRIP)
    ld a,(hl)
    inc hl
    ld c,(hl)
    inc hl
    ld b,(hl)
    inc hl
    ld d,(hl)                   ; byte 3: pattern << 5 | group
    inc hl
    ld (V_TRIP),hl
    push de                     ; D = pattern/group
    ld de,V_X0
    call getVertex              ; vertex A (v0): sets Z=0 / carry when off view
    jr c,fhSkip
    ld a,c
    ld de,V_X1
    call getVertex
    jr c,fhSkip
    ld a,b
    ld de,V_X2
    call getVertex
    jr c,fhSkip
    call cull                   ; carry set = back face or degenerate
    jr c,fhSkip
    pop de
    ld a,d
    rlca
    rlca
    rlca
    and 7                       ; pattern index
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
    jr fhLoop
fhSkip:
    pop de
    jr fhLoop
fhDone:
    or a                        ; carry clear: drawn
    ret
fhNone:
    scf
    ret

; A = vertex number, DE = destination (x, y); reads VBUF. Absolute x = 127 -/+ xmag (flag bit 1: left), y = 63 +/- ymag (flag bit 0: below). Carry set if off view.
getVertex:
    push bc
    ld l,a
    ld h,0
    ld c,l
    ld b,h
    add hl,hl
    add hl,bc
    ld bc,VBUF
    add hl,bc
    ld a,(hl)                   ; x magnitude
    inc hl
    ld b,(hl)                   ; y magnitude
    inc hl
    ld c,(hl)                   ; flag
    bit 7,c
    jr nz,gvOff
    bit 1,c
    jr z,gvXr
    ld l,a                      ; left of the centre: 127 - xmag, clamped at 0
    ld a,127
    sub l
    jr nc,gvXok
    xor a
    jr gvXok
gvXr:
    add a,127
    jr nc,gvXok
    ld a,255
gvXok:
    ld (de),a
    inc de
    ld a,b
    bit 0,c
    jr z,gvYu
    add a,63                    ; below the centre
    cp 128
    jr c,gvYok
    ld a,127
    jr gvYok
gvYu:
    ld b,a
    ld a,63
    sub b                       ; above the centre
    jr nc,gvYok
    xor a
gvYok:
    ld (de),a
    dec de                      ; DE back on x (the caller advances by name)
    pop bc
    or a
    ret
gvOff:
    pop bc
    scf
    ret

; Back-face test from the three absolute vertices in V_X0..V_Y2: cross = (x1-x0)*(y2-y0) - (x2-x0)*(y1-y0). Carry set = not front facing (or area 0).
cull:
    ld a,(V_X1)
    ld hl,V_X0
    sub (hl)                    ; dx1
    call absA                   ; A = |dx1|, C = 1 if negative
    ld d,a
    ld e,c
    ld a,(V_Y2)
    ld hl,V_Y0
    sub (hl)                    ; dy2
    call absA
    ld b,a                      ; |dy2|
    ld a,c
    xor e
    ld (V_S1),a                 ; sign of P1 = dx1 * dy2
    ld a,d
    ld c,b
    call mulq                   ; HL = |dx1| * |dy2|
    ld (V_M1),hl
    ld a,(V_X2)
    ld hl,V_X0
    sub (hl)                    ; dx2
    call absA
    ld d,a
    ld e,c
    ld a,(V_Y1)
    ld hl,V_Y0
    sub (hl)                    ; dy1
    call absA
    ld b,a
    ld a,c
    xor e
    ld (V_S2),a                 ; sign of P2 = dx2 * dy1
    ld a,d
    ld c,b
    call mulq
    ld (V_M2),hl                ; |dx2| * |dy1|
    ld a,(V_S1)
    ld hl,V_S2
    xor (hl)
    jr z,cuSame
    ld hl,(V_M1)                ; different signs: |cross| = m1 + m2, the sign is that of P1
    ld de,(V_M2)
    add hl,de
    ld a,h
    or l
    jr z,cuBad
    ld a,(V_S1)
    jr cuTest
cuSame:                         ; same signs: negative P1 and P2: cross = m2 - m1; positive: m1 - m2. Negative cross = borrow XOR (P1 negative)
    ld hl,(V_M1)
    ld de,(V_M2)
    or a
    sbc hl,de
    jr z,cuBad
    ld a,0
    rla                         ; A = borrow
    ld c,a
    ld a,(V_S1)
    xor c
cuTest:
    and 1
    IF VISPOS
    jr nz,cuBad                 ; negative = not front facing
    ELSE
    jr z,cuBad
    ENDIF
    or a
    ret
cuBad:
    scf
    ret

; A = signed difference (carry from the subtraction); returns A = |A|, C = 1 if the difference was negative. Needs the carry of the SUB: x - y borrows when negative.
absA:
    ld c,0
    ret nc
    neg
    ld c,1
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
    ld h,ROWHIP                 ; HL = row start in the bitmap
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

; dither patterns (even line, odd line), Mode 1 pens 0-3: solid pen 1, solid pen 2, solid pen 3, 1/3, 2/3, 1/2 checkers. Tuned by eye later.
PATS:   db 0x0F,0x0F, 0xF0,0xF0, 0xFF,0xFF, 0x5F,0xAF, 0xF5,0xFA, 0x5A,0xA5

; Builds the tables. Run once with bank 6 mapped.
fillInit:
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
    ld e,0                      ; bitmap row table: row y at BITMAP + y * 64
ibRow:
    ld a,e
    and 3
    rrca
    rrca                        ; (y & 3) << 6
    ld d,ROWLOP
    ld (de),a
    ld a,e
    srl a
    srl a
    add a,BITMAP >> 8
    inc d
    ld (de),a
    inc e
    ld a,e
    cp 128
    jr nz,ibRow
    ret
ibLM:   db 0xFF, 0x77, 0x33, 0x11
ibRM:   db 0x88, 0xCC, 0xEE, 0xFF
fillEnd:
    ASSERT fillEnd <= 0x4F00

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
TT_HOOK     equ 0x6540          ; the title text cache lives in fill_tt.asm, appended to the record file at this address (the code here is full)
TT_OFF      equ 0x6543
TT_ST       equ 0x4F30          ; title text cache: 0 empty, 1 the text rows are held in the other screen bank
TT_KEY      equ 0x4F31          ; the title ship index the cached text belongs to
TT_CNT      equ 0x4F32

    ORG 0x4000
fillHull:
    jp fillHullGo
    jp fillInit                 ; &4003
fillHullGo:
    cp 20
    jp nc,fhNone
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
    ld a,(VIEWDIR)                      ; title screens (Viewdirection &94): stop filling as soon as a key is down, so a key press is answered within one triangle
    cp 0x94                             ; instead of after the whole ship (about 250 ms with a close hull)
    jr nz,fhNoKey
    ld a,(DB_KEY)
    inc a
    jr nz,fhDone
fhNoKey:
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
    jr c,gvYcl                  ; magnitude of 193 or more wrapped: clamp, do not wrap to the top of the view
    cp 128
    jr c,gvYok
gvYcl:
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
    xor a
    ld (TT_ST),a
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
    ASSERT fillEnd <= 0x43B8
    DS 0x43B8-$

; --- page flip (runs here, in RAM bank 6, so that the resident glue stays small): called through dbFlipTail (commonxx.asm) with config C6 and the resident stack ---
; The addresses of the resident variables and of dbCopy come from the build (tools/check_src128.sh).
    IFNDEF DB_CURCFG
DB_CURCFG   equ 0
DB_ON       equ 0
DB_SHOWN    equ 0
DB_CNT      equ 0
DB_COPY     equ 0
DB_SCAN     equ 0
DB_MISS     equ 0
DB_STAT     equ 0
DB_LOCK     equ 0
DB_VARS     equ 0
DB_VLEN     equ 0
DB_KEY      equ 0
DB_SHIPNR   equ 0
DB_STATUS   equ 0
DB_PRT1     equ 0
DB_PRT2     equ 0
    ENDIF
VIEWDIR     equ 0x1C02
; Flight views: wait for the vertical sync, point the CRTC at the bank just drawn (R12 &1C = bank 1, &3C = bank 3), make the other bank the draw bank, then copy what the game
; writes straight to the screen (cockpit rows 16-23 of each scan line block, two 16-byte variable areas in the gaps) from the shown bank to the new draw bank.
; The first call after a non-flight view copies the whole page. Charts and docked screens draw into the displayed bank (dbIsr in the ISR).
dbFlip6:
    ld a,(VIEWDIR)
    cp 4
    ret nc
    and a                               ; view 0 with the status flag below 4 is the title (flight, the launch and docking tunnels have 4): single buffered like the other
    jr nz,dbfFlight                     ; non-flight screens (dbIsr follows curCfg), which is what lets the text cache use the idle bank
    ld a,(DB_STATUS)
    cp 4
    jp c,TT_HOOK
dbfFlight:
    ld a,(TT_ST)
    and a
    call nz,TT_OFF                      ; leaving the title: the text printers must run again next time
    ld a,(DB_ON)
    and a
    jr nz,dbfFlip
    inc a
    ld (DB_ON),a
    ld a,(DB_CURCFG)                    ; entering: the draw bank is the one on screen; the other one gets a full copy
    call dbBases
    ld a,64
    ld (DB_CNT),a
dbfAll:
    ld bc,256
    call dbCopyB
    ld a,(DB_CNT)
    dec a
    ld (DB_CNT),a
    jr nz,dbfAll
dbfFlip:
    ld bc,0xF500
dbfw1:
    in a,(c)
    rra
    jr c,dbfw1                          ; wait until the frame is not in vsync
dbfw2:
    in a,(c)
    rra
    jr nc,dbfw2                         ; and until the next one starts
    di
    ld a,(DB_CURCFG)
    ld (DB_SHOWN),a
    and 2
    add a,a
    add a,a
    add a,a
    add a,a
    add a,0x1C
    ld bc,0xBC0C
    out (c),c
    ld b,0xBD
    out (c),a
    ld a,(DB_SHOWN)
    xor 2                               ; C1 <-> C3
    ld (DB_CURCFG),a
    ld hl,0
    ld (dbBudget),hl                    ; the first copy waits for an interrupt: every copy then starts right after one
    ei
    ; what changed in the cockpit since the last flip, found without hooks in the drawing routines:
    ;  gauges (bars, missiles, speed digit, text): the player variables the bars are drawn from (DB_VARS, with their "last drawn" copies) and the missile count, compared with a
    ;  snapshot; every 64th frame in any case (alert light, station and ECM letters are drawn on events that have no variable of their own here)
    ;  scanner: busy while a ship is in range or ECM runs, one frame longer for the clean-up (dbScanFlag, computed by dbFlipTail)
    ;  compass: every frame
    ld c,0
    ld hl,DB_VARS
    ld de,dbSnap
    ld b,DB_VLEN
dbfCmp:
    ld a,(de)
    cp (hl)
    jr z,dbfSame
    ld a,(hl)
    ld (de),a
    ld c,1
dbfSame:
    inc hl
    inc de
    djnz dbfCmp
    ld hl,dbWatch                       ; single variables behind indicators that are drawn on events: missiles, lock state, station near
    ld de,dbSnapM
    ld b,3
dbfW:
    ld a,(hl)
    inc hl
    push hl
    ld h,(hl)
    ld l,a
    ld a,(de)
    cp (hl)
    jr z,dbfWs
    ld a,(hl)
    ld (de),a
    ld c,1
dbfWs:
    pop hl
    inc hl
    inc de
    djnz dbfW
    ld hl,dbTick
    inc (hl)
    ld a,(hl)
    and 63
    jr nz,dbfNoTick
    ld c,1
dbfNoTick:
    ld a,c
    and a
    jr z,dbfPart
    ld a,(DB_SHOWN)                     ; everything: the 8 cockpit rows of every scan line block
    call dbBases
    ld bc,0x0400
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld a,8
    ld (DB_CNT),a
dbfRows:
    ld bc,256
    call dbCopyB
    ld bc,256
    call dbCopyB
    ld bc,0x0600
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld a,(DB_CNT)
    dec a
    ld (DB_CNT),a
    jr nz,dbfRows
    jr dbfGaps
dbfPart:
    ld a,(DB_SCAN)
    and a
    ld hl,dbZScanner
    jr nz,dbfZ
    ld hl,dbZCompass
dbfZ:
    call dbZone
dbfGaps:
    ld a,(DB_SHOWN)
    call dbBases
    ld bc,0x0E00
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld bc,16
    call dbCopyB
    ld a,(DB_SHOWN)
    call dbBases
    ld bc,0x2FF0
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld bc,16
    call dbCopyB
    ld a,(DB_SHOWN)                     ; smc_dfcPatchpos (&27B0): the opcode that drawFilledCircle's size test is patched to. It is patched in the draw bank only but runs from either one,
    call dbBases                        ; so a stale copy made planets and suns blink on alternate frames
    ld bc,0x27B0
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld bc,1
    jp dbCopyB
; HL = zone descriptor: offset in the page of the first strip (word), width (byte), rows (byte), step to the next row = 64 - width (word), step to the next scan line block (word).
; Copies rows x width bytes in each of the 8 scan line blocks from the shown bank to the draw bank.
dbZone:
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld c,(hl)
    inc hl
    ld b,(hl)
    inc hl
    ld (zWR),bc                         ; C = width, B = rows
    ld c,(hl)
    inc hl
    ld b,(hl)
    inc hl
    ld (zRowStep),bc
    ld c,(hl)
    inc hl
    ld b,(hl)
    ld (zBlkStep),bc
    ld (zOff),de
    ld a,(DB_SHOWN)
    call dbBases
    ld bc,(zOff)
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld a,8
    ld (zBlk),a
dbzBlk:
    ld a,(zWR+1)
    ld (zRow),a
dbzRow:
    ld a,(zWR)
    ld c,a
    ld b,0
    call dbCopyB
    ld bc,(zRowStep)
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld a,(zRow)
    dec a
    ld (zRow),a
    jr nz,dbzRow
    ld bc,(zBlkStep)
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    ld a,(zBlk)
    dec a
    ld (zBlk),a
    jr nz,dbzBlk
    ret
; compass: columns 42-47 of rows 17-19; scanner, ECM letter and compass: columns 16-47 of rows 17-23
dbZCompass:
    dw 17*64+42
    db 6, 3
    dw 64-6, 0x0800-3*64
dbZScanner:
    dw 17*64+16
    db 32, 7
    dw 64-32, 0x0800-7*64
zWR:        dw 0
zRowStep:   dw 0
zBlkStep:   dw 0
zOff:       dw 0
zBlk:       db 0
zRow:       db 0
dbTick:     db 0
dbSnapM:    ds 3
dbWatch:    dw DB_MISS, DB_STAT, DB_LOCK
dbSnap      equ 0x4F40                  ; DB_VLEN bytes in the variable page (it would not fit in the 0x600 staged bytes of code)
    ASSERT 0x4F40 + DB_VLEN <= 0x5000
; The copy keeps interrupts off while it runs, which would delay the raster-timed interrupts (colour split of the view and the dashboard). So the copies are paced by the interrupts:
; each one starts right after an interrupt handler returned (HALT) and at most DBWIN bytes are copied before the next HALT (DBWIN x 5.25 us stays below the 3.3 ms between interrupts
; minus the handler). HL, DE, BC as for dbCopy.
DBWIN       equ 160
dbCopyB:
    push hl
    ld hl,(dbBudget)
    and a
    sbc hl,bc
    jr nc,dbcbOk
    ei
    halt
    ld hl,DBWIN
    and a
    sbc hl,bc
    jr nc,dbcbOk
    ld hl,0                             ; a chunk larger than the window: it runs alone
dbcbOk:
    ld (dbBudget),hl
    pop hl
    jp DB_COPY
dbBudget:   dw 0
; A = config of the bank to copy from; returns HL = its address and DE = the other bank's address in the C0 configuration
dbBases:
    bit 1,a
    ld hl,0x4000
    ld de,0xC000
    ret z
    ex de,hl
    ret
dbFlip6End:
    ASSERT dbFlip6End <= 0x4600             ; the staging copy of bankInit is 0x600 bytes (a stage area is 0x600 blank pixel bytes in a screen page)

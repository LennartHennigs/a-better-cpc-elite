; Frame routine of the ship viewer (SHOWSHIP.BAS): CALL &4000 rotates the current ship by the angle in the parameter block and redraws its edges with its own Bresenham
; line routine, which XORs pen 1 straight into the mode 1 screen at &C000 (drawing a line twice erases it; the firmware's GRA LINE was about five times slower). Assembled by tools/mk_showship.py into SHOWCODE.BIN (sjasmplus, load &4000; below &A67B, where AMSDOS keeps its work area).
; The BASIC program fills the tables below once per ship (scaled to signed bytes: vertices to +-125, face normals to +-64) and POKEs the cosine and sine of the spin angle (x127)
; before every call. The view is orthographic: spin about the ship's y axis, then a fixed tilt about x (P_CT, P_ST), x and y of the result are the screen coordinates.
; Edges are drawn when the face on either side points at the viewer (the same test as the game: the rotated normal has a negative z), or all of them when P_ALL is not 0.
CENTRE_X equ 160                    ; screen position of the ship's centre in mode 1 pixels (the view is x 8..312, y 22..172)
CENTRE_Y equ 103

PARAMS equ 0x4800
P_NV equ PARAMS+0                   ; vertex, edge and face counts
P_NE equ PARAMS+1
P_NF equ PARAMS+2
P_ALL equ PARAMS+3                  ; not 0: draw every edge
P_C equ PARAMS+4                    ; cos and sin of the spin angle, signed, x127
P_S equ PARAMS+5
P_CT equ PARAMS+6                   ; cos and sin of the tilt, signed, x127
P_ST equ PARAMS+7
P_CNT equ PARAMS+8                  ; loop counter
P_TMP equ PARAMS+9
P_D equ PARAMS+10
P_HA equ PARAMS+11                  ; 1: the ship has no faces, draw every edge
P_SRC equ PARAMS+12                 ; word: packed ship record for `select`
LV equ 0x4D60                       ; line routine variables (after the old segments)
LN_X equ LV+0                       ; start pixel of the line
LN_Y equ LV+1
LN_CNT equ LV+2                     ; major axis length
LN_FL equ LV+3                      ; 1: the line goes up (x-major) or left (y-major)
LN_SL equ LV+4                      ; slope, 8-bit fraction

VERT equ 0x4810                     ; 8 bytes per vertex: x y z px py (signed bytes, then the pixel column and row), 64 vertices
FACE equ 0x4A10                     ; 4 bytes per face: nx ny nz visible, 16 faces
EDGE equ 0x4A50                     ; 4 bytes per edge: vertex a, vertex b, face 1, face 2, 64 edges
OLD equ 0x4B50                      ; 8 bytes per edge: drawn flag, x1 y1 x2 y2 of the segment on screen (to erase it next frame)

    org 0x4000
    jp frame                        ; CALL &4000: one frame
    jp select                       ; CALL &4003: copy the packed ship record at (P_SRC) into the tables, clear the old segments

; packed record: nv ne nf ha nfp killword(2) bounty(2) speed energy (11 bytes), then nv vertices of 8 bytes, ne edges of 4 bytes, nf faces of 4 bytes
select:
    ld hl,(P_SRC)
    ld a,(hl)
    ld (P_NV),a
    inc hl
    ld a,(hl)
    ld (P_NE),a
    inc hl
    ld a,(hl)
    ld (P_NF),a
    inc hl
    ld a,(hl)
    ld (P_HA),a
    ld de,8                         ; skip the rest of the 11-byte header
    add hl,de
    ld a,(P_NV)
    ld c,a
    ld b,0
    sla c
    rl b
    sla c
    rl b
    sla c
    rl b
    ld de,VERT
    ldir
    ld a,(P_NE)
    ld c,a
    ld b,0
    sla c
    rl b
    sla c
    rl b
    ld de,EDGE
    ldir
    ld a,(P_NF)
    ld c,a
    ld b,0
    sla c
    rl b
    sla c
    rl b
    ld de,FACE
    ldir
    ld hl,OLD
    ld de,8
    ld b,64
    xor a
selclr:
    ld (hl),a
    add hl,de
    djnz selclr
    ret

frame:
    ld a,(P_HA)
    ld (P_ALL),a
    ld a,(P_NV)
    ld (P_CNT),a
    ld ix,VERT
vloop:
    ld a,(P_C)                      ; px = (x*c + z*s) >> 7
    ld b,a
    ld a,(ix+0)
    call mul
    push hl
    ld a,(P_S)
    ld b,a
    ld a,(ix+2)
    call mul
    pop de
    add hl,de
    call sra7
    call zoomx
    ld (ix+3),a
    ld a,(P_C)                      ; z1 = (z*c - x*s) >> 7
    ld b,a
    ld a,(ix+2)
    call mul
    push hl
    ld a,(P_S)
    ld b,a
    ld a,(ix+0)
    call mul
    pop de
    ex de,hl
    or a
    sbc hl,de
    call sra7
    ld (P_TMP),a
    ld a,(P_CT)                     ; py = (y*ct - z1*st) >> 7
    ld b,a
    ld a,(ix+1)
    call mul
    push hl
    ld a,(P_ST)
    ld b,a
    ld a,(P_TMP)
    call mul
    pop de
    ex de,hl
    or a
    sbc hl,de
    call sra7
    call zoomy
    ld (ix+4),a
    ld de,8
    add ix,de
    ld hl,P_CNT
    dec (hl)
    jr nz,vloop

    ld a,(P_NF)                     ; face visibility: ((nz*c - nx*s) >> 7) * ct + ny * st < 0
    or a
    jr z,nofaces
    ld (P_CNT),a
    ld iy,FACE
floop:
    ld a,(P_C)
    ld b,a
    ld a,(iy+2)
    call mul
    push hl
    ld a,(P_S)
    ld b,a
    ld a,(iy+0)
    call mul
    pop de
    ex de,hl
    or a
    sbc hl,de
    call sra7
    ld b,a
    ld a,(P_CT)
    call mul
    push hl
    ld a,(P_ST)
    ld b,a
    ld a,(iy+1)
    call mul
    pop de
    add hl,de
    ld a,h
    rlca
    ld a,0
    rla
    ld (iy+3),a
    ld de,4
    add iy,de
    ld hl,P_CNT
    dec (hl)
    jr nz,floop
nofaces:

    ld a,(P_NE)
    ld (P_CNT),a
    ld iy,EDGE
    ld ix,OLD
eloop:
    ld a,(P_ALL)
    or a
    jr nz,evis
    ld a,(iy+2)                     ; face 1
    call faceptr
    ld a,(hl)
    or a
    jr nz,evis
    ld a,(iy+3)                     ; face 2
    call faceptr
    ld a,(hl)
    or a
    jr nz,evis
    xor a
    jr egot
evis:
    ld a,1
egot:
    ld (P_D),a
    ld a,(ix+0)                     ; erase the segment drawn last frame
    or a
    call nz,segdraw
    ld a,(P_D)
    or a
    jr z,enone
    ld a,(iy+0)                     ; vertex a screen position
    call vptr
    ld a,(hl)
    ld (ix+1),a
    inc hl
    ld a,(hl)
    ld (ix+2),a
    ld a,(iy+1)                     ; vertex b
    call vptr
    ld a,(hl)
    ld (ix+3),a
    inc hl
    ld a,(hl)
    ld (ix+4),a
    ld (ix+0),1
    call segdraw
    jr enext
enone:
    ld (ix+0),0
enext:
    ld de,4
    add iy,de
    ld e,8
    add ix,de
    ld hl,P_CNT
    dec (hl)
    jr nz,eloop
    ret

; A = face number -> HL = address of its visible flag
faceptr:
    add a,a
    add a,a
    ld l,a
    ld h,0
    ld de,FACE+3
    add hl,de
    ret

; A = vertex number -> HL = address of its screen x (screen y follows)
vptr:
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,VERT+3
    add hl,de
    ret

; A (signed byte, +-125) -> HL = A * 9 / 16 (signed): the ship fills about 140 of the 150 pixel rows of the view
zoom:
    ld l,a
    add a,a
    sbc a,a
    ld h,a
    ld d,h
    ld e,l
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,de
    sra h
    rr l
    sra h
    rr l
    sra h
    rr l
    sra h
    rr l
    ret
zoomx:                              ; A -> pixel column CENTRE_X + A*9/16
    call zoom
    ld de,CENTRE_X
    add hl,de
    ld a,l
    ret
zoomy:                              ; A -> pixel row CENTRE_Y - A*9/16 (y points up)
    call zoom
    ex de,hl
    ld hl,CENTRE_Y
    or a
    sbc hl,de
    ld a,l
    ret

; draw (XOR, pen 2) the segment stored at IX: x1 y1 x2 y2 (mode 1 pixels) at +1..+4. A DDA with an 8-bit fraction (slope = minor * 256 / major): the major axis steps every pixel, the
; minor axis when the fraction overflows. The endpoints are swapped so that x-major lines run to the right and y-major lines downwards; pen 2 keeps the pixel mask in the low nibble
; (&08 &04 &02 &01), so a step to the right shows itself as the carry out of `srl c`. No alternate registers: the firmware's interrupt routine uses them.
segdraw:
    ld b,(ix+1)                     ; x0
    ld c,(ix+2)                     ; y0
    ld d,(ix+3)                     ; x1
    ld e,(ix+4)                     ; y1
    ld a,d
    sub b
    jr nc,sd1
    neg
sd1:
    ld h,a                          ; dx
    ld a,e
    sub c
    jr nc,sd2
    neg
sd2:
    ld l,a                          ; dy
    ld a,h
    cp l
    jr c,ymajor
    ld a,d                          ; x-major: x0 <= x1
    cp b
    jr nc,xm1
    ld a,b
    ld b,d
    ld d,a
    ld a,c
    ld c,e
    ld e,a
xm1:
    ld a,e                          ; flag: y1 < y0, the line goes up
    cp c
    ld a,0
    rla
    ld (LN_FL),a
    ld a,h
    ld (LN_CNT),a
    ld a,b
    ld (LN_X),a
    ld a,c
    ld (LN_Y),a
    ld a,l                          ; slope = dy * 256 / dx
    ld e,h
    call divslope
    ld (LN_SL),a
    call scrstart                   ; HL = address, C = mask, B = pixels, D = fraction, E = slope
    ld a,(LN_FL)
    or a
    jr nz,xup
xdn:
    ld a,(hl)
    xor c
    ld (hl),a
    srl c
    jr nc,xdn1
    ld c,0x08
    inc hl
xdn1:
    ld a,d
    add a,e
    ld d,a
    jr nc,xdn2
    ld a,h
    add a,8
    ld h,a
    jr nc,xdn2
    ld a,l
    add a,0x50
    ld l,a
    ld a,h
    adc a,0xC0
    ld h,a
xdn2:
    djnz xdn
    ret
xup:
    ld a,(hl)
    xor c
    ld (hl),a
    srl c
    jr nc,xup1
    ld c,0x08
    inc hl
xup1:
    ld a,d
    add a,e
    ld d,a
    jr nc,xup2
    ld a,h
    sub 8
    ld h,a
    and 0x38
    cp 0x38
    jr nz,xup2
    ld a,l
    add a,0xB0
    ld l,a
    ld a,h
    adc a,0x3F
    ld h,a
xup2:
    djnz xup
    ret

ymajor:                             ; y0 <= y1
    ld a,e
    cp c
    jr nc,ym1
    ld a,b
    ld b,d
    ld d,a
    ld a,c
    ld c,e
    ld e,a
ym1:
    ld a,d                          ; flag: x1 < x0, the line goes left
    cp b
    ld a,0
    rla
    ld (LN_FL),a
    ld a,l
    ld (LN_CNT),a
    ld a,b
    ld (LN_X),a
    ld a,c
    ld (LN_Y),a
    ld a,h                          ; slope = dx * 256 / dy
    ld e,l
    call divslope
    ld (LN_SL),a
    call scrstart
    ld a,(LN_FL)
    or a
    jr nz,yl
yr:
    ld a,(hl)
    xor c
    ld (hl),a
    ld a,d
    add a,e
    ld d,a
    jr nc,yr1
    srl c
    jr nc,yr1
    ld c,0x08
    inc hl
yr1:
    ld a,h
    add a,8
    ld h,a
    jr nc,yr2
    ld a,l
    add a,0x50
    ld l,a
    ld a,h
    adc a,0xC0
    ld h,a
yr2:
    djnz yr
    ret
yl:
    ld a,(hl)
    xor c
    ld (hl),a
    ld a,d
    add a,e
    ld d,a
    jr nc,yl1
    sla c
    bit 4,c
    jr z,yl1
    ld c,0x01
    dec hl
yl1:
    ld a,h
    add a,8
    ld h,a
    jr nc,yl2
    ld a,l
    add a,0x50
    ld l,a
    ld a,h
    adc a,0xC0
    ld h,a
yl2:
    djnz yl
    ret

; A = minor * 256 / major (E = major, 0 < minor <= major; 0 when major is 0), at most 255
divslope:
    ld b,e
    inc b
    dec b
    jr nz,dv0
    xor a
    ret
dv0:
    ld b,8
    ld c,0
dvl:
    add a,a
    jr c,dvs
    cp e
    jr c,dvz
dvs:
    sub e
    scf
    jr dvn
dvz:
    or a
dvn:
    rl c
    djnz dvl
    ld a,c
    ret

; the pixel position, count and DDA registers of the line: HL = screen address of (LN_X, LN_Y), C = pen 2 mask, B = pixels (major length + 1), D = fraction (&80), E = slope
scrstart:
    ld a,(LN_Y)
    ld c,a
    rrca
    rrca
    rrca
    and 0x1F
    ld l,a
    ld h,0
    ld d,h
    ld e,l
    add hl,hl
    add hl,hl
    add hl,de
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl                       ; row * 80
    ld a,(LN_X)
    ld b,a
    srl a
    srl a
    ld e,a
    ld d,0
    add hl,de
    ld a,c
    and 7
    rlca
    rlca
    rlca
    ld d,a
    ld e,0
    add hl,de
    ld de,0xC000
    add hl,de
    ld a,b
    and 3
    ld b,a
    ld c,0x08
    jr z,ss1
ss0:
    srl c
    djnz ss0
ss1:
    ld a,(LN_CNT)
    inc a
    ld b,a
    ld a,(LN_SL)
    ld e,a
    ld d,0x80
    ret

; HL = A * B, both signed bytes; clobbers A, B, C, DE
mul:
    ld c,0
    or a
    jp p,mulA
    neg
    ld c,1
mulA:
    ld e,a
    ld d,0
    ld a,b
    or a
    jp p,mulB
    neg
    inc c
mulB:
    ld b,a
    ld hl,0
    ld a,8
mulL:
    add hl,hl
    sla b
    jr nc,mulS
    add hl,de
mulS:
    dec a
    jr nz,mulL
    ld a,c
    dec a
    ret nz
    ex de,hl
    ld hl,0
    or a
    sbc hl,de
    ret

; A = HL >> 7 (bits 14..7 of HL); the values stay inside +-16383, so the result is a signed byte
sra7:
    ld a,l
    rla
    ld a,h
    rla
    ret

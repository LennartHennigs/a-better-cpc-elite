; Mission code that must be resident in flight (COMMONXX tail, &9D9E-&9FFF). Assembled only with -DMISSIONS.

mxTypeConstrictor equ 19            ; ship type after the 19 stock ships (0-18)

; spawnShip's table lookup (it replaces `ld hl,shipGFXdataTable`, same 3 bytes): A = ship type (kept), returns HL so that
; HL + 4 * (type & &3F) points at the record. Type 19 is served from the one-entry table below, so nothing in the stock table moves.
mxShipTable:
    ld hl,shipGFXdataTable
    push af
    and 0x3F
    cp mxTypeConstrictor
    jr nz,mxShipTableDone
    ld hl,mxConstrictorEntry-mxTypeConstrictor*4
mxShipTableDone:
    pop af
    ret
mxConstrictorEntry:
    jp shipdatConstrictor            ; spawnShip reads bytes +1 and +2 (the blueprint address)
    db 0x04                          ; the unused tag byte of the stock records

    INCLUDE "missions_hull.asm"

; Flight tail of COMMONXX (&9D9E-&9FFF), assembled with -DMISSIONS. The tail holds a vector table at fixed addresses, an id byte and the code of at most one
; mission image. Without a flight flag it is the default image (no mission): every vector points at a stub that does what the hooked stock instruction did.
; With -DFL_C / -DFL_P the same layout carries that mission's code; tools/build_dsk.py cuts those images out as FLIGHTC.BIN / FLIGHTP.BIN (mxFlightBase to
; mxFlightEnd) and the launch hook in the docked stub loads the one the state byte asks for.
mxStateByte equ 0x38FD              ; missionState (see missions_docked.asm): bits 0-1 Constrictor, bits 2-3 Thargoid plans, bits 4-6 hint stage, bit 7 Trumbles
mxTypeConstrictor equ 19            ; ship type after the 19 stock ships (0-18)

    IFDEF FL_C
    DEFINE FLID "C"
    DEFINE HAS_SHIP
    DEFINE HAS_SPAWN
    DEFINE HAS_KILL
    DEFINE HAS_LASER
    ENDIF
    IFDEF FL_P
    DEFINE FLID "P"
    DEFINE HAS_SPAWN
    ENDIF
    IFNDEF FLID
    DEFINE FLID "0"
    ENDIF

mxFlightBase:
; Vector table: the hook sites in commonxx.asm call these fixed addresses (3 bytes each).
mxShipTable:                        ; replaces `ld hl,shipGFXdataTable` in spawnShip: A = ship type (kept), HL = table base
    jp mxShipTableImpl
mxSpawnCheck:                       ; replaces `ld a,(cargoSlaves)` at the start of spawnCommand0 and must end with it
    jp mxSpawnCheckImpl
mxKillHook:                         ; replaces `call getBounty` in todo_killedsomeone (IY = the dead ship's blueprint)
    jp mxKillHookImpl
mxLaserHook:                        ; replaces `ld (ix+34),a` after `sub c` in applyLaserDamagetoEntity (flags from the sub must survive)
    jp mxLaserHookImpl
mxRecharge:                         ; replaces `call nz,SUB_ram_3693` in RechargeEnergy
    jp mxRechargeImpl
mxFlightId:
    db FLID                         ; "0" default, "C", "P": which image is in RAM (the launch hook compares it)

; Defaults for the vectors the image does not use.
    IFNDEF HAS_SHIP
mxShipTableImpl:
    ld hl,shipGFXdataTable
    ret
    ENDIF
    IFNDEF HAS_SPAWN
mxSpawnCheckImpl:
    ld a,(cargoSlaves)
    ret
    ENDIF
    IFNDEF HAS_KILL
mxKillHookImpl:
    jp getBounty
    ENDIF
    IFNDEF HAS_LASER
mxLaserHookImpl:
    ld (ix+34),a
    ret
    ENDIF

; Navy energy unit (extraEnergyUnit = &FE, the Thargoid plans reward): it stays fitted after the mission, so this is in every image. One extra recharge step
; for an extra energy unit, and a second one for the Navy unit: 3 steps per call (ordinary unit 2, none 1).
mxRechargeImpl:
    call SUB_ram_3693
    ld a,(extraEnergyUnit)
    cp 0xFE
    ret nz
    jp SUB_ram_3693

    IFDEF FL_C
    INCLUDE "missions_flight_c.asm"
    ENDIF
    IFDEF FL_P
    INCLUDE "missions_flight_p.asm"
    ENDIF
mxFlightEnd:

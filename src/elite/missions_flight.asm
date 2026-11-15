; Flight tail of COMMONXX (&9D9E-&9FFF), assembled with -DMISSIONS. The tail holds a vector table at fixed addresses, an id byte and the code of at most one
; mission image. Without a flight flag it is the default image (no mission): every vector points at a stub that does what the hooked stock instruction did.
; With -DFL_C / -DFL_P / -DFL_T the same layout carries that mission's code; tools/build_dsk.py cuts those images out as MFLIGHTC.BIN / MFLIGHTP.BIN / MFLIGHTT.BIN
; (mxFlightBase to mxFlightEnd) and the launch hook below loads the one the state byte asks for.
mxTrCount equ 0x3905                ; Trumble count, 16 bit, kept at 0x7FFF or less (save bytes the stock game never uses; docs/_savegame.md)
mxStateByte equ 0x38FD              ; missionState (see missions_docked.asm): bits 0-1 Constrictor, bits 2-3 Thargoid plans, bits 4-6 hint stage, bit 7 Trumbles
mxMissionByte2 equ 0x38FE            ; first mission: jumps to wait; second mission (after the first is paid): state in bits 0-1, asteroids to go in bits 2-7
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
    IFDEF FL_T
    DEFINE FLID "T"
    DEFINE HAS_SPAWN
    DEFINE HAS_ARRIVE
    DEFINE HAS_SUN
    DEFINE HAS_INV
    DEFINE HAS_DRAW
    ENDIF
    IFDEF FL_S
    DEFINE FLID "S"
    DEFINE HAS_SPAWN
    DEFINE HAS_KILL
    DEFINE HAS_ARRIVE
    ENDIF
    IFDEF FL_R
    DEFINE FLID "R"
    DEFINE HAS_SPAWN
    DEFINE HAS_KILL
    ENDIF
    IFDEF FL_1
    DEFINE FLID "1"
    DEFINE FL_PACK
    ENDIF
    IFDEF FL_2
    DEFINE FLID "2"
    DEFINE FL_PACK
    ENDIF
    IFDEF FL_3
    DEFINE FLID "3"
    DEFINE FL_PACK
    ENDIF
    IFDEF FL_4
    DEFINE FLID "4"
    DEFINE FL_PACK
    ENDIF
    IFDEF FL_5
    DEFINE FLID "5"
    DEFINE FL_PACK
    ENDIF
    IFDEF FL_6
    DEFINE FLID "6"
    DEFINE FL_PACK
    ENDIF
    IFDEF FL_7
    DEFINE FLID "7"
    DEFINE FL_PACK
    ENDIF
    IFDEF FL_PACK
    DEFINE HAS_SHIP
    ENDIF
    IFNDEF FLID
    DEFINE FLID "0"
    ENDIF

mxFlightBase:
    ASSERT mxFlightBase == 0x9D9E             ; the tail starts here: the launch hook, tools/build_dsk.py and the tests rely on it
; Vector table: the hook sites in commonxx.asm call or jump to these fixed addresses (3 bytes each).
mxShipTable:                        ; replaces `ld hl,shipGFXdataTable` in spawnShip: A = ship type (kept), HL = table base
    jp mxShipTableImpl
mxSpawnCheck:                       ; replaces `ld a,(cargoSlaves)` at the start of spawnCommand0 and must end with it
    jp mxSpawnCheckImpl
mxKillHook:                         ; replaces `call getBounty` in todo_killedsomeone (IY = the dead ship's blueprint)
    IFDEF HAS_KILL
    jp mxKillHookImpl
    ELSE
    jp getBounty                    ; an image without the hook jumps straight to the stock routine (no stub)
    ENDIF
mxLaserHook:                        ; replaces `ld (ix+34),a` after `sub c` in applyLaserDamagetoEntity (flags from the sub must survive)
    jp mxLaserHookImpl
mxRecharge:                         ; replaces `call nz,SUB_ram_3693` in RechargeEnergy
    jp mxRechargeImpl
mxArrive:                           ; replaces `ld (tunnelFlag2),a` at the start of setShipvarsAtArrival (A = 1, must be kept)
    jp mxArriveImpl
mxSun:                              ; replaces `ld hl,CockpitTemp` in todoOverheating (A must be kept)
    jp mxSunImpl
mxInvHook:                          ; replaces `call prQuantityofGoodinCargohold` in the Inventory loop (carry of the result must survive)
    IFDEF HAS_INV
    jp mxInvHookImpl
    ELSE
    jp prQuantityofGoodinCargohold
    ENDIF
mxFlightDraw:                       ; replaces the `call transferBuffertoScreen` in Spaceflight (draws into the off-screen bitmap, then jumps there)
    IFDEF HAS_DRAW
    jp mxFlightDrawImpl
    ELSE
    jp transferBuffertoScreen
    ENDIF
mxFlightId:
    db FLID                         ; "0" default, "C", "P": which image is in RAM (the launch hook compares it)

; Launch hook: replaces the first call of launchSequence (`call loadIndicator`). Makes sure the flight image the state asks for is in this tail, then carries on with
; loadIndicator. "T" while Trumbles are aboard, "C" while the Constrictor hunt is on (state 1 or 3), "P" while the plans are aboard, "S" while the stolen-ship mission waits or hunts, "R" while Ceerdi is being cleared, else a ship pack "0" to "7" (0 = the default image, no extra ships).
; Nothing is loaded when the right image is already there. This code is the same in every image, at the same address, so the load can overwrite it while it waits.
mxLaunchEntry:
    ld hl,(mxTrCount)
    ld a,h
    or l
    ld a,"T"
    jr nz,mxFlightGo
    ld a,(mxStateByte)
    ld b,a
    ld hl,mxLaunchTable               ; (mask, value, image) for the state byte, first match wins: C = bit 0 set (hunting or killed), P = plans aboard, S = stolen ship
    ld d,3
mxLaunchLoop:
    ld a,(hl)
    and b
    inc hl
    cp (hl)
    inc hl
    ld a,(hl)
    inc hl
    jr z,mxFlightGo
    dec d
    jr nz,mxLaunchLoop
    ld a,b
    and 0x7C
    cp 0x5C                           ; first mission paid: the second one clearing (&38FE bits 0-1 = 1) needs the R image
    jr nz,mxFlightNone
    ld a,(mxMissionByte2)
    and 0x03
    cp 0x01
    ld a,"R"
    jr z,mxFlightGo
mxFlightNone:                         ; no mission: ship pack "0" (none) to "7" for this visit. jumpCounter changes at every arrival and the system byte with the system, so a
    ld a,(jumpCounter)                ; relaunch from the same station asks for the same pack (already in RAM, nothing loaded); stock was `ld a,"0"`
    ld hl,presentSystemSeed
    add a,(hl)
    and 0x07
    add a,"0"
mxFlightGo:
    ld hl,mxFlightId
    cp (hl)
    jp z,loadIndicator                ; already in RAM
    ld (mxFlightName+7),a
    call loadFile
    dw mxFlightBase
    dw mxFlightName
    jp loadIndicator
mxFlightName:
    db "MFLIGHT?"
; Launch picker table: (mask, value, image) tested against the state byte (mxStateByte), first match wins. "C": bit 0 set (Constrictor hunting or killed, state 1 or 3);
; "P": bits 0-3 = 1010 (plans stage, plans aboard); "S": bits 0-4 and 6 = 1 1110 and 0 (stolen ship stage). The asteroid image "R" needs the second byte as well, see above.
mxLaunchTable:
    db 0x01,0x01,"C"
    db 0x0F,0x0A,"P"
    db 0x5F,0x1E,"S"
    IF KILL_COUNT
    INCLUDE "killcount.asm"           ; shared head: the same address in every image (the hook in commonxx.asm calls it)
    ASSERT killCountHook == 0x9E1A, "the kill count hook must sit at the same address in every flight image (the status code calls it): the shared head changed size"
    ENDIF

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
    IFNDEF HAS_LASER
mxLaserHookImpl:
    ld (ix+34),a
    ret
    ENDIF

    IFNDEF HAS_ARRIVE
mxArriveImpl:
    ld (tunnelFlag2),a
    ret
    ENDIF
    IFNDEF HAS_SUN
mxSunImpl:
    ld hl,CockpitTemp
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
    IFDEF FL_T
    INCLUDE "missions_flight_t.asm"
    ENDIF
    IFDEF FL_S
    INCLUDE "missions_flight_s.asm"
    ENDIF
    IFDEF FL_R
    INCLUDE "missions_flight_r.asm"
    ENDIF
    IFDEF FL_PACK
    INCLUDE "missions_flight_k.asm"
    ENDIF
mxFlightEnd:
    ASSERT mxFlightEnd <= 0x9FFE              ; with SP at &A000 an interrupt pushes at &9FFE-&9FFF (docs/_architecture.md): no image byte may sit there

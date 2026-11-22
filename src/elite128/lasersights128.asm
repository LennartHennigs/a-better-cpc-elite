; Laser sights for the 128K build (ENHANCED): a sight for each laser type instead of the one cross for all of them. Same drawing as src/elite/lasersights.asm (main).
; There is no free resident code space in this build (docs/_memory_map_128k.md), so the routine is an overlay: it is assembled by tools/build_dsk128.py at the address of
; bankInit (laserSightsHome, the boot code that is dead after Init_), carried in the data stage of COMMON2X (STAGE+0x1700), and copied over bankInit by the last step of
; bankInit itself (commonxx.asm). LaserSights in COMMON2X jumps to laserSightsHome.
; Drawing: every sight is two or three lines given for one quadrant (x1, y1, x2, y2 as offsets from the view centre, the form drawLaserLine takes in H, L, D, E) and drawn four times,
; mirrored through the quadrant bits of C (0, 0x05 = y flipped, 0x0A = x flipped, 0x0F = both). No laser in the view (laserTypes = 0): no sight, like the ST.
; Externals, given with -D by the build: VIEWDIR (Viewdirection), LASERTYPES (laserTypes), DRAWLINE (drawLaserLine), CURCFG (curCfg), HOME (bankInit, where the overlay starts).
; The overlay starts with bankCopy (20 bytes, the title ship viewer's bank 6 reader: no room for it in the glue), the sights follow at HOME + 20 (laserSightsHome in commonxx.asm).
    INCLUDE "config.inc"
    ORG HOME
; A = count, HL = source (window address in bank 6), DE = destination (resident): maps RAM bank 6 for the copy only, no stack use while it is mapped
bankCopy:
    di
    ld bc,0x7FC6
    out (c),c
    ld c,a
    ld b,0
    ldir
    ld a,(CURCFG)                       ; back to the draw configuration (the mapMain macro of commonxx.asm)
    ld b,0x7F
    out (c),a
    ei
    ret
    ASSERT $ - bankCopy == 20, "bankCopy must be 20 bytes (laserSightsHome = bankInit + 20 in commonxx.asm)"
laserSightsNew:
    ld a,(VIEWDIR)
    ld e,a
    ld d,0x00
    ld hl,LASERTYPES                ; 0 none, 1 pulse, 2 beam, 3 military, 4 mining; one byte per view (front, rear, left, right)
    add hl,de
    ld a,(hl)
    and a
    ret z
    dec a
    ld c,a                          ; sight index: 0 pulse, 1 beam, 2 military, 3 mining
    and 0x01
    add a,0x02
    ld b,a                          ; lines to draw: 2 (pulse, military) or 3 (beam, mining); lsLine keeps B
    ld a,c
    srl a
    add a,c
    add a,c
    add a,a
    add a,a                         ; 4 * (2 * index + index / 2) = 0, 8, 20, 28: the two-line sights take 8 bytes, the three-line ones 12
    ld e,a
    ld hl,lsData                    ; D is still 0
    add hl,de
lsLoop:
    call lsLine
    djnz lsLoop
    ret
; One line at (HL): load H, L, D, E from its four bytes, draw it with C = 0x0F, 0x0A, 0x05, 0x00; HL = the next line on return
lsLine:
    ld a,(hl)
    inc hl
    ld c,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld e,(hl)
    inc hl
    push hl
    ld h,a
    ld l,c
    ld c,0x0F
lsMirror:
    push bc
    push hl
    push de
    call DRAWLINE
    pop de
    pop hl
    pop bc
    ld a,c
    sub 0x05
    ld c,a
    jr nc,lsMirror
    pop hl
    ret
; x1, y1, x2, y2 for one quadrant: two lines for the pulse and military sights, three for the beam and mining sights (the order and the 8 / 12 byte sizes are what the offset code above computes)
lsData:
    db 8,0,16,0,   0,8,0,16                    ; pulse: the stock cross
    db 0,7,15,7,   0,7,0,11,   15,7,15,4       ; beam: two bars with a tick at the centre and short ends
    db 5,5,13,13,  7,5,15,13                   ; military: four double diagonals pointing at the centre
    db 0,7,15,7,   0,7,0,11,   0,0,0,0         ; mining: the same bars and ticks without the ends, plus a dot in the centre
laserSightsEnd:
    ASSERT laserSightsEnd <= HOME + 0x80, "the laser sights must end before the title music block (musicState = bankInit + 0x80 in commonxx.asm)"
    DS HOME + 0x80 - $
; ---- Title music hook (src/elite128/musiquex.asm): resident code needs bytes the glue does not have, so it rides in this overlay too ----------------------------------------------
; musicState (commonxx.asm: bankInit + 0x80): 0 = no music, 1 = on, no tick owed, n > 1 = n - 1 ticks owed. It starts at 1 (the overlay is copied at the end of bankInit, after the
; player was loaded) and loadNotMusique sets it to 0 before the player is overwritten. dbIsr jumps to musicHook (bankInit + 0x81) on the title (view 0), after the key latch.
; As in the stock IRSound the music replaces the sound effects (no IRdrivenSound): the hook drops the return into IRSound and returns to the ISR itself.
; The player sits in bank 7 (&C000-&FFFF), which is only visible in the draw configurations C1/C3. myVBL runs the ISR on its own stack and keeps the interrupted SP in stack5:
;  - SP at or above &C000: the main thread runs in a draw configuration, bank 7 is visible: run the owed ticks (MusicRun with B = 1 + owed).
;  - SP below &C000 and the interrupted PC (the word at stack5) in the window &4000-&7FFF: the ship fill runs, bank 6 is mapped at &4000 (C6) and nothing else (the hull call
;    switches the stack and the map together, but the PC is in the glue then): map C1 for the ticks and put C6 back.
;  - anything else (setup code on another stack, the glue around the far calls): the configuration is not known, the tick is owed (counted up to 255) and runs later.
; The player runs with interrupts disabled: its PSG writes no longer end in ei (a nested myVBL would overwrite stack5).
; Externals: MUSICRUN (MusicRun in musiquex.asm), STACK5 (stack5), both given by tools/build_dsk128.py.
musicState:
    db 1
musicHook:
    ld a,(musicState)
    and a
    ret z                               ; music off: IRSound goes on with the sound effects
    pop hl                              ; the music replaces the sound effects: return to the ISR from here
    ld hl,(STACK5)                      ; the interrupted SP
    ld a,h
    cp 0xC0
    jr nc,musicRun                      ; a draw configuration: bank 7 is visible
    inc hl
    ld a,(hl)                           ; high byte of the interrupted PC
    cp 0x40
    jr c,musicOwe
    cp 0x80
    jr nc,musicOwe
    ld bc,0x7FC1                        ; C6 (bank 6 at &4000, bank 3 at &C000) -> C1 (bank 7 at &C000) ...
    out (c),c
    call musicRun
    ld bc,0x7FC6                        ; ... and back
    out (c),c
    ret
musicRun:
    ld hl,musicState
    ld b,(hl)                           ; 1 + the ticks owed
    ld (hl),1
    jp MUSICRUN
musicOwe:
    ld hl,musicState
    inc (hl)
    ret nz
    dec (hl)                            ; not past 255: 0 would switch the music off
    ret
musicHookEnd:
    IFDEF SPAWN_VARIANCE
    ASSERT musicHookEnd == HOME + 0xB7, "spawnVariance = bankInit + 0xB7 in commonxx.asm"
; ---- Spawn variance (src/elite128/config.inc SPAWN_VARIANCE; docs/_ship_spawning.md) ------------------------------------------------------------------------------------------
; The rules are in the module in RAM bank 6 (spawnmod.asm, &4600), which these stubs call on the resident stack like the fill module (the game stack is in bank 7, hidden by config C6).
; spawnVariance: the end of spawnShip, IX = the new ship (a hostile type or a pack member is placed, the other types keep the stock start).
; spawnRock: the end of the asteroid branch of spawnCommand0: a random place and a heading towards the player.
; spawnPackShip: spawnEscortPack's call of spawnShip, with the number of ships still to come for the module (spawnPackC, 0 outside a pack).
; Externals: HULLSAVESP, HULLSTACKTOP (the resident stack of the far calls), CURCFG, SPAWNSHIP.
spawnVariance:
    ld a,(spawnPackC)
    jr spawnFar
    ASSERT $ == HOME + 0xBC, "spawnRock = bankInit + 0xBC in commonxx.asm"
spawnRock:
    ld a,0xFF
spawnFar:
    ld (HULLSAVESP),sp
    ld sp,HULLSTACKTOP
    ld bc,0x7FC6                        ; RAM bank 6 at &4000
    out (c),c
    call 0x4600                         ; spawnMod (src/elite128/spawnmod.asm)
    ld a,(CURCFG)                       ; back to the draw configuration (the mapMain macro of commonxx.asm)
    ld b,0x7F
    out (c),a
    ld sp,(HULLSAVESP)
    xor a                               ; spawnShip returns A = 0
    ret
    ASSERT $ == HOME + 0xDA, "spawnPackShip = bankInit + 0xDA in commonxx.asm"
spawnPackShip:
    ld (spawnPackC),bc                  ; C (B is ignored); A, the ship type, stays
    call SPAWNSHIP
    ld (spawnPackC),a                   ; A = 0
    ret
spawnPackC:
    dw 0
spawnVarianceEnd:
    ENDIF

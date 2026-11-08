; Mission code that runs only while docked (LARGEAXX tail, &1714-&1A3F). Assembled only with -DMISSIONS.
; Entered from the docking sequence (commonxx.asm, after loadLARGEAXX), in place of `call chkMissions`.

; Addresses in COMMONXX (stock layout; the check in tools/check_src.sh keeps them honest through the byte-exact build).
mxChkMissions          equ 0x2063
mxThargonMissionVar    equ 0x3926
mxDrawFrame            equ 0x4646
mxPrintStringA         equ 0x4416
mxPrintStringScan      equ 0x442C     ; inside printStringA: HL = table, D = 1-based string number
mxSetColors            equ 0x454F
mxViewdirection        equ 0x1C02
mxCharXY               equ 0x38C4
mxActionsAtEndOfMessage equ 0x499E    ; waits for a key, redraws the frame, then jp InitVariables (returns to the docking code)
mxColorsMessage        equ 0x4A31     ; colour set of the "mission accepted" box (colorsThargonMissionAccepted)
missionState           equ 0x38FD     ; save byte, never used by the stock game (docs/_savegame.md)
;   bits 0-1 Constrictor: 0 not offered, 1 hunting, 3 killed (set by the kill hook), 2 finished (paid)
;   bits 2-3 Thargoid plans (later), bits 4-6 hint stage 0-7 (7 = hints done, the ship waits at Orarra), bit 7 Trumbles offered (later)
mxKillScoreHigh        equ 0x38D9     ; BBC TALLY+1: at least 1 = 256 kill points
mxCurrentGalaxy        equ 0x38DC     ; 0-7
mxPresentSystemY       equ 0x390E
mxPresentSystemX       equ 0x3910
mxAddDEtoMoney         equ 0xFE6A     ; DE thousands of credits (COMMON2X)
mxExtraEnergyUnit      equ 0x3902     ; 0 none, 0xFF extra energy unit, 0xFE Navy unit (Thargoid plans reward; recharges 3 steps per call)

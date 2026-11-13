    INCLUDE "config.inc"
SCREEN equ 0x4000            ; the screen page (the 128K layout); the block below runs in RAM bank 7 at &C000
killHook equ 0x9C56   ; generated: label of commonxx
irki2_8 equ 0x8EB2   ; generated: label of commonxx
mxArrive equ 0x9DAD   ; generated: label of commonxx
mxInvHook equ 0x9DB3   ; generated: label of commonxx
mxKillHook equ 0x9DA4   ; generated: label of commonxx
mxLaserHook equ 0x9DA7   ; generated: label of commonxx
mxLaunchEntry equ 0x9DBA   ; generated: label of commonxx
mxSun equ 0x9DB0   ; generated: label of commonxx
curCfg equ 0x9854   ; generated: label of commonxx
dbCopy equ 0x9D66   ; generated: label of commonxx
dbOn equ 0x9CFF   ; generated: label of commonxx
dbShown equ 0x9CFB   ; generated: label of commonxx
ActDeponEnergy equ 0x881C   ; generated: label of commonxx
AddDEtoKillScore equ 0x39A5   ; generated: label of commonxx
Altitude equ 0x1C11   ; generated: label of commonxx
BYTE_ram_1c3c equ 0x1C3C   ; generated: label of commonxx
BYTE_ram_3933 equ 0x3933   ; generated: label of commonxx
CallprintString equ 0x3F0B   ; generated: label of commonxx
CircleEntrypoint1 equ 0x20F2   ; generated: label of commonxx
CirclewheretoDrawFlag equ 0x2812   ; generated: label of commonxx
ClearBitmap equ 0x1FF1   ; generated: label of commonxx
CockpitTemp equ 0x1C0D   ; generated: label of commonxx
DockedDigrams equ 0x8DC6   ; generated: label of commonxx
DrawBytesMask0 equ 0x3F56   ; generated: label of commonxx
FillmemoryRegionDEwithA equ 0x20B9   ; generated: label of commonxx
FlagStationNear equ 0x1C38   ; generated: label of commonxx
FlightMode equ 0x38F8   ; generated: label of commonxx
FuelbarValue equ 0x1C0B   ; generated: label of commonxx
GameOverFlag equ 0x1C3B   ; generated: label of commonxx
GenPriceAndStockEntry1 equ 0x6F7D   ; generated: label of commonxx
GetSquareforAinDE equ 0x21CF   ; generated: label of commonxx
GetYlocationofText equ 0x3F16   ; generated: label of commonxx
LAB_ram_33bc equ 0x33BC   ; generated: label of commonxx
LAB_ram_3475 equ 0x3475   ; generated: label of commonxx
Lasertemp equ 0x1C0F   ; generated: label of commonxx
MissileDestroyedbyECM equ 0x8A11   ; generated: label of commonxx
Missionflag equ 0x3927   ; generated: label of commonxx
PresentPlanetX equ 0x3934   ; generated: label of commonxx
PresentPlanetY equ 0x3935   ; generated: label of commonxx
SUB_ram_2058 equ 0x2058   ; generated: label of commonxx
SUB_ram_33cf equ 0x33CF   ; generated: label of commonxx
SUB_ram_3dc6 equ 0x3DC6   ; generated: label of commonxx
SUB_ram_3f25 equ 0x3F25   ; generated: label of commonxx
SUB_ram_3f7e equ 0x3F7E   ; generated: label of commonxx
SUB_ram_e74c equ 0x674C   ; generated: label of commonxx
SUB_ram_ff39 equ 0x7F39   ; generated: label of commonxx
StationEnergy equ 0x1C39   ; generated: label of commonxx
ThargonMissionVar equ 0x3926   ; generated: label of commonxx
VerticalPlacement equ 0x3F2D   ; generated: label of commonxx
Viewdirection equ 0x1C02   ; generated: label of commonxx
WaitForKeypress equ 0x3E5E   ; generated: label of commonxx
anotherPrintWithToken3A equ 0x3EFC   ; generated: label of commonxx
askBuyGood equ 0x3E77   ; generated: label of commonxx
buf_1B51 equ 0x1B51   ; generated: label of commonxx
buf_1B5A equ 0x1B5A   ; generated: label of commonxx
buf_1B73 equ 0x1B73   ; generated: label of commonxx
calcDustParticlePixel equ 0x3387   ; generated: label of commonxx
cargoSpaceFree equ 0x38F3   ; generated: label of commonxx
charXY equ 0x38C4   ; generated: label of commonxx
charsATAT equ 0x8DAC   ; generated: label of commonxx
chkConditionNSetIndicatorColors equ 0x3545   ; generated: label of commonxx
chkMissions equ 0x2063   ; generated: label of commonxx
circleOffsetXhi equ 0x20C9   ; generated: label of commonxx
circleOffsetXlo equ 0x20C8   ; generated: label of commonxx
circleOffsetY equ 0x20C7   ; generated: label of commonxx
cleanScannerUpdateECMIndicator equ 0x29FE   ; generated: label of commonxx
clearCircle equ 0x6797   ; generated: label of commonxx
clearKeyBuffer equ 0x3E6C   ; generated: label of commonxx
clrLine0x15 equ 0x9712   ; generated: label of commonxx
creditsHighWord equ 0x38DD   ; generated: label of commonxx
creditsLowWord equ 0x38DF   ; generated: label of commonxx
currentGalaxy equ 0x38DC   ; generated: label of commonxx
dat_38E1 equ 0x38E1   ; generated: label of commonxx
dataSpaceStationPosXh equ 0x1C31   ; generated: label of commonxx
dataSpaceStationPosYh equ 0x1C34   ; generated: label of commonxx
dataSpaceStationPosZh equ 0x1C37   ; generated: label of commonxx
dataSpaceStationPosZl equ 0x1C36   ; generated: label of commonxx
displayAlertStateinHeader equ 0x3F97   ; generated: label of commonxx
dockingComputer equ 0x3903   ; generated: label of commonxx
dot_product_scale_factor equ 0x8C08   ; generated: label of commonxx
drawDashboard equ 0x1F8C   ; generated: label of commonxx
drawradius equ 0x20CA   ; generated: label of commonxx
dustPlotPixel equ 0x1FD5   ; generated: label of commonxx
ecmEquipped equ 0x38FC   ; generated: label of commonxx
economy equ 0x3D5E   ; generated: label of commonxx
emptyDefaultsave equ 0x39C7   ; generated: label of commonxx
energyBomb equ 0x3901   ; generated: label of commonxx
execSelectedKeyFunctions equ 0x2ADB   ; generated: label of commonxx
extraEnergyUnit equ 0x3902   ; generated: label of commonxx
flagCanScoopFuel equ 0x1C3A   ; generated: label of commonxx
flagCloakingDeviceActive equ 0x38C3   ; generated: label of commonxx
flagDockingComputerOn equ 0x1C3E   ; generated: label of commonxx
flagDrawLaserline equ 0x8CD5   ; generated: label of commonxx
flagPausemode equ 0x1C3D   ; generated: label of commonxx
fuel equ 0x38F9   ; generated: label of commonxx
fuelPriceByte equ 0x2F36   ; generated: label of commonxx
fuelScoops equ 0x38FF   ; generated: label of commonxx
galacticHyperdrive equ 0x3904   ; generated: label of commonxx
galaxySeed equ 0x3907   ; generated: label of commonxx
getBounty equ 0x39B7   ; generated: label of commonxx
government equ 0x3D5F   ; generated: label of commonxx
hullBegin equ 0x99E4   ; generated: label of commonxx
hullDeferEntry equ 0x99FE   ; generated: label of commonxx
hullDraw equ 0x985D   ; generated: label of commonxx
hullDummy equ 0x9855   ; generated: label of commonxx
hullFlush equ 0x9A4D   ; generated: label of commonxx
inputPitch equ 0x1C04   ; generated: label of commonxx
inputRoll equ 0x1C03   ; generated: label of commonxx
irki2_dat1 equ 0x8F3E   ; generated: label of commonxx
jumpCounter equ 0x38DA   ; generated: label of commonxx
keybFlags0 equ 0x8E07   ; generated: label of commonxx
keybFlags1 equ 0x8D6B   ; generated: label of commonxx
keybFlags2 equ 0x8D6C   ; generated: label of commonxx
keybFlags3 equ 0x8D6D   ; generated: label of commonxx
keybFlags4CounterNstringNumber equ 0x8D6E   ; generated: label of commonxx
keybFlags5 equ 0x8D6F   ; generated: label of commonxx
killScoreHigh equ 0x38D9   ; generated: label of commonxx
largeCargoBay equ 0x38FB   ; generated: label of commonxx
laserTypes equ 0x38F4   ; generated: label of commonxx
legalStatus equ 0x38D6   ; generated: label of commonxx
loadIndicator equ 0x8717   ; generated: label of commonxx
loadLARGEAXX equ 0x8732   ; generated: label of commonxx
longDelay equ 0x9705   ; generated: label of commonxx
marketStock equ 0x3914   ; generated: label of commonxx
missileLockState equ 0x38C6   ; generated: label of commonxx
missileTargetEntity equ 0x3951   ; generated: label of commonxx
movementspeed equ 0x1C05   ; generated: label of commonxx
msgECMJammer equ 0x3936   ; generated: label of commonxx
msgSupernovaMission equ 0x3944   ; generated: label of commonxx
msgTargetLost equ 0x393A   ; generated: label of commonxx
numberOfDigits equ 0x3947   ; generated: label of commonxx
parseStoredToken equ 0x96C5   ; generated: label of commonxx
placeCursor equ 0x3F0E   ; generated: label of commonxx
pointerUnitMarketPrice equ 0x3E2A   ; generated: label of commonxx
populationCount equ 0x3D61   ; generated: label of commonxx
posDataPlanet equ 0x1C2F   ; generated: label of commonxx
posDataSun equ 0x1C26   ; generated: label of commonxx
prLYDistance equ 0x6F43   ; generated: label of commonxx
prQuantityofGoodinCargohold equ 0x3ECD   ; generated: label of commonxx
presentSystemSeed equ 0x390D   ; generated: label of commonxx
presentSystemX equ 0x3910   ; generated: label of commonxx
presentSystemY equ 0x390E   ; generated: label of commonxx
presentTechLevel equ 0x3913   ; generated: label of commonxx
printFollowingTokenWithSpace equ 0x3F21   ; generated: label of commonxx
printPlanetname equ 0x3F8C   ; generated: label of commonxx
printTokenAndToken0x20 equ 0x3F03   ; generated: label of commonxx
printwithToken3a equ 0x3EF7   ; generated: label of commonxx
productivityCredits equ 0x3D62   ; generated: label of commonxx
punishCheater equ 0x2078   ; generated: label of commonxx
qq3 equ 0x3D22   ; generated: label of commonxx
qq4 equ 0x3D24   ; generated: label of commonxx
qq5 equ 0x3D26   ; generated: label of commonxx
sEntityRole equ 0x1A61   ; generated: label of commonxx
sEntityRoll equ 0x1A5D   ; generated: label of commonxx
sEntityZSign equ 0x1A48   ; generated: label of commonxx
sEntityZhi equ 0x1A47   ; generated: label of commonxx
sEntitynosevXhi equ 0x1A4A   ; generated: label of commonxx
sEntitynosevXlo equ 0x1A49   ; generated: label of commonxx
sEntitynosevZhi equ 0x1A4E   ; generated: label of commonxx
sEntityroofvYhi equ 0x1A52   ; generated: label of commonxx
sEntitysidevXhi equ 0x1A56   ; generated: label of commonxx
sEntitysidevzhi equ 0x1A5A   ; generated: label of commonxx
sEntityunknown equ 0x1A66   ; generated: label of commonxx
sEntityxhi equ 0x1A41   ; generated: label of commonxx
sEntityxlo equ 0x1A40   ; generated: label of commonxx
sEntityxsign equ 0x1A42   ; generated: label of commonxx
saveGameRam equ 0x38CB   ; generated: label of commonxx
seedvar1 equ 0x3D34   ; generated: label of commonxx
seedvar2 equ 0x3D36   ; generated: label of commonxx
sfxFlags1Bitmap equ 0x2DB1   ; generated: label of commonxx
sfxFlags2Bitmap equ 0x2DB2   ; generated: label of commonxx
sfxForKeyInput equ 0x3E4F   ; generated: label of commonxx
shipEnergyBank4 equ 0x1C1B   ; generated: label of commonxx
shipFrontShieldEnergy equ 0x1C07   ; generated: label of commonxx
shipRearShieldEnergy equ 0x1C09   ; generated: label of commonxx
shuffle_particle_table equ 0x34D4   ; generated: label of commonxx
singleDigit equ 0x3946   ; generated: label of commonxx
smc_dfcPatchpos equ 0x67B0   ; generated: label of commonxx
spawnCommandParser equ 0x809C   ; generated: label of commonxx
storeScoopedGood equ 0x396E   ; generated: label of commonxx
storedByteVariable equ 0x3E4E   ; generated: label of commonxx
strChar32 equ 0x1BC4   ; generated: label of commonxx
strPLANETNAME1 equ 0x3D4A   ; generated: label of commonxx
strPLANETNAME2 equ 0x3D53   ; generated: label of commonxx
stringsTable equ 0x2FAF   ; generated: label of commonxx
sub_2F81 equ 0x2F81   ; generated: label of commonxx
tblDustCoordinates equ 0x34F4   ; generated: label of commonxx
techLevel equ 0x3D60   ; generated: label of commonxx
tempString1 equ 0x1BC5   ; generated: label of commonxx
tempString1End equ 0x1BE3   ; generated: label of commonxx
tempString2 equ 0x1BE4   ; generated: label of commonxx
todoDigitCalculation equ 0x7E00   ; generated: label of commonxx
todoDrawCircleFlag equ 0x671D   ; generated: label of commonxx
todoDrawFilledCircle equ 0x6789   ; generated: label of commonxx
todoLaunchFlag equ 0x1C22   ; generated: label of commonxx
todoPrintFlag3948 equ 0x3948   ; generated: label of commonxx
todoSomePrintFlag equ 0x3949   ; generated: label of commonxx
todoUnknownStatusFlags equ 0x1C23   ; generated: label of commonxx
todo_planet3dCoordX2 equ 0x1C28   ; generated: label of commonxx
todo_planet3dCoordY equ 0x1C2B   ; generated: label of commonxx
todo_planet3dCoordZ equ 0x1C2E   ; generated: label of commonxx
todo_varEscapepod equ 0x1C24   ; generated: label of commonxx
transferBuffertoScreen equ 0x1ED1   ; generated: label of commonxx
travelDistance equ 0x3D5C   ; generated: label of commonxx
tunnelFlag1 equ 0x38C1   ; generated: label of commonxx
tunnelFlag2 equ 0x38C2   ; generated: label of commonxx
txtScreenOffset equ 0x38C5   ; generated: label of commonxx
useJumpTokens1 equ 0x7EA8   ; generated: label of commonxx
useJumpTokens2 equ 0x7EA3   ; generated: label of commonxx
    IFNDEF STAR_OCCLUDE
      IFDEF ENHANCED
STAR_OCCLUDE equ 1
      ELSE
STAR_OCCLUDE equ 0
      ENDIF
    ENDIF
    IFDEF MISSIONS
MISSIONS_POD equ STAR_OCCLUDE
    ENDIF
    org 0xC000
    ds 0x3A                             ; the block starts at &C03A: its stock addresses (&413A...) move by &7F00, a whole number of pages, so that the page-aligned tables stay aligned
loc_5958 equ mi_5957+1   ; inside the instruction at mi_5957 (patched or jumped into)
sub_61B5 equ mi_61B4+1   ; inside the instruction at mi_61B4 (patched or jumped into)
sub_6953 equ mi_6952+1   ; inside the instruction at mi_6952 (patched or jumped into)
sub_71CB equ mi_71CA+1   ; inside the instruction at mi_71CA (patched or jumped into)
loc_7873 equ mi_7872+1   ; inside the instruction at mi_7872 (patched or jumped into)
; Code block of the 128K build: DistanceToPlanet..end of the line drawing code (stock &413A-&8072), assembled for RAM bank 7 at &C000 (loaded there by the BASIC loader, as COMMON2X.BIN).
DistanceToPlanet:
    call SUB_ram_3dc6
placeCrossHairPrintDistance:
    call clrLine0x15
    ld a,0x03
    call SUB_ram_3f7e
    call placeCursor
    call prLYDistance
    jp sfxForKeyInput
MapCrossHairUp:
    call DrawTargetReticule
    ld a,(PresentPlanetY)
    dec a
    dec a
    cp 0xFE
    jr c,mchu1
    xor a
mchu1:
    ld (PresentPlanetY),a
    jr goMapDrawCrosshair
MapCrossHairDown:
    call DrawTargetReticule
    ld a,(PresentPlanetY)
    inc a
    inc a
    cp 0x02
    jr nc,mchd1
    ld a,0xFF
mchd1:
    ld (PresentPlanetY),a
    jr goMapDrawCrosshair
MapCrossHairLeft:
    call DrawTargetReticule
    ld a,(PresentPlanetX)
    dec a
    jr nz,mchl1
    inc a
mchl1:
    ld (PresentPlanetX),a
goMapDrawCrosshair:
    jp DrawTargetReticule
MapCrossHairRight:
    call DrawTargetReticule
    ld a,(PresentPlanetX)
    inc a
    cp 0xFF
    jr nz,mchr1
    dec a
mchr1:
    ld (PresentPlanetX),a
    jr goMapDrawCrosshair
RecenteronDockedPlanet:
    call DrawTargetReticule
    ld a,(presentSystemX)
    ld (PresentPlanetX),a
    ld a,(presentSystemY)
    ld (PresentPlanetY),a
    jr goMapDrawCrosshair
; Prints the framed title-box token 0x96
DrawFramedTitlebox:
    ld a,0x96
    jp printStringA
; ZX Spectrum: add_a_to_hl (&EB3E)
SetTableBegintoAofHL:
    ld d,0x00
    ld e,a
    add hl,de
    ret
; Prints the token A in header style, then the planet name
printFlightToken:
    push af
    call printFollowingTokenWithSpace
chartTitleCol:
    IFDEF ENHANCED
    db 0x01                         ; chart headlines start in column 2 (was 0x06)
    ELSE
    db 0x06
    ENDIF
    pop af
    jp printPlanetname
digitNumber:
    db 0x00,0x00
; Prints A as a plain decimal byte (carry set: leading digits are padded)
printCount:
    scf
    jr LAB_ram_41be
; ZX Spectrum: print_byte (&D2E1)
; Three entries share one body: here A is printed as a plain decimal byte; the next entry honours the carry flag as a decimal-place flag; a third
; prints the 16-bit value in HL. The minimum digit count is in a variable set by the caller.
printNumber:
    and a
LAB_ram_41be:
    ld h,0x00
    ld l,a
; Prints HL as a decimal number from 10000 down to 1, respecting the set digit count
todo_SomethingwithDigits:
    push af
    push hl
    call todoDigitCalculation
    pop hl
    ld a,0x01
    ld (singleDigit),a
    ld (digitNumber),hl
    ld de,0x2710
    call PrintHowManyOfIt
    ld de,0x03E8
    call PrintHowManyOfIt
    ld de,0x0064
    call PrintHowManyOfIt
    ld de,0x000A
    call PrintHowManyOfIt
    pop af
    jr nc,LAB_ram_41f9
    ld a,(singleDigit)
    and a
    jp z,loc_41F5
    xor a
    call goPrintNumber
loc_41F5:
    call printStringFollowingByte
    db "."
LAB_ram_41f9:
    ld hl,(digitNumber)
    ld a,l
    call goPrintNumber
    xor a
    ld (numberOfDigits),a
    inc a
    ld (singleDigit),a
    ret
; ZX Spectrum: print_cash (&D32D)
; Prints the cash balance, kept as two words: whole thousands of credits and the 0-9999 remainder in tenths of a credit (thousands printed
; without leading zeros, then the remainder with one decimal place).
getMoneyinHLDE:
    ld hl,(creditsHighWord)
    ld de,(creditsLowWord)
; Prints a credit amount in DE:HL with one decimal place (for the cash display)
printDeciCredit:
    push de
    ld a,l
    or h
    jr z,LAB_ram_4229
    ld a,0x03
    ld (numberOfDigits),a
    and a
    call todo_SomethingwithDigits
    xor a
    ld (singleDigit),a
    ld a,0x04
    ld (numberOfDigits),a
    jr LAB_ram_422e
LAB_ram_4229:
    ld a,0x07
    ld (numberOfDigits),a
LAB_ram_422e:
    pop hl
    scf
    jp todo_SomethingwithDigits
; Draws the target reticule on the chart, clipped to the chart's X/Y limits per view
DrawTargetReticule:
    ld a,(Viewdirection)
    cp 0x07
    jr z,drawReticuleAtXY
    cp 0x08
    ret nz
    ld a,(presentSystemX)
    ld b,a
    ld a,(PresentPlanetX)
    sub b
    jr c,LAB_ram_4252
    add a,a
    ret c
    add a,a
    ret c
    ld b,a
    ld a,0x61
    add a,b
    ret c
    jr LAB_ram_425d
LAB_ram_4252:
    neg
    add a,a
    ret c
    add a,a
    ret c
    ld b,a
    ld a,0x61
    sub b
    ret c
LAB_ram_425d:
    ld (storePresPlanetX),a
    ld a,(presentSystemY)
    ld b,a
    ld a,(PresentPlanetY)
    sub b
    jr c,LAB_ram_4273
    add a,a
    ret c
    ld b,a
    ld a,0x60
    add a,b
    ret c
    jr reticuleMinMaxY
LAB_ram_4273:
    neg
    add a,a
    ret c
    ld b,a
    ld a,0x60
    sub b
    ret c
reticuleMinMaxY:
    cp 0x19
    ret c
    cp 0xA7
    ret nc
    ld (storePresPlanetY),a
    jr jpDrawReticule
drawReticuleAtXY:
    ld a,(PresentPlanetX)
    ld (storePresPlanetX),a
    ld a,(PresentPlanetY)
    srl a
    add a,0x18
    ld (storePresPlanetY),a
jpDrawReticule:
    jp drawReticule
; Divides digitNumber by DE by repeated subtraction and prints one digit, skipping leading zeros
PrintHowManyOfIt:
    ld hl,(digitNumber)
    xor a
    and a
LAB_ram_429f:
    sbc hl,de
    jr c,LAB_ram_42a6
    inc a
    jr LAB_ram_429f
LAB_ram_42a6:
    add hl,de
    ld (digitNumber),hl
    and a
    jr z,LAB_ram_42b8
    ld b,a
    xor a
    ld (singleDigit),a
    ld a,b
; Adds 0x30 to A and prints it as an ASCII digit
goPrintNumber:
    add a,0x30
    jp printString
LAB_ram_42b8:
    ld a,(singleDigit)
    and a
    jr z,goPrintNumber
    ret
locateLine6:
    ld a,0x06
    jr LAB_ram_42c5
locateLine10:
    ld a,0x0A
LAB_ram_42c5:
    jp VerticalPlacement
; Prints the char at HL unless it is '?' (0x3F)
printCharofDigram:
    ld a,(hl)
    cp 0x3F
    ret z
    jp printString
DataonPlanet:
    call DrawFramedTitlebox
    ld de,ColorsDataonPlanet
    call setColors
    call SUB_ram_3dc6
    ld a,0xA3
    call printPlanetname
    ld a,0x03
    call VerticalPlacement
    call prLYDistance
    call placeCursor
    call printEconomy
    ld a,0xA2
    call anotherPrintWithToken3A
    call printSpace
    ld a,0xB1
    ld b,a
    ld a,(government)
    add a,b
    call anotherPrintwithTokeninA
    ld a,0xC4
    call anotherPrintWithToken3A
    ld a,0x03
    ld (numberOfDigits),a
    ld a,(techLevel)
    inc a
    call printNumber
    call CurHomeinFrame
    ld a,0xD7
    call printwithToken3a
    ld a,(populationCount)
    call printCount
    ld a,0xC6
    call CallprintString
    call placeCursor
    call printStringFollowingByte
    db "("
    call printRace
    call printStringFollowingByte
    db "S"
    ld a,0x29
    call anotherPrintwithTokeninA
    ld a,0x6F
    call printwithToken3a
    ld hl,(productivityCredits)
    ld a,0x05
    ld (numberOfDigits),a
    and a
    call todo_SomethingwithDigits
    call printStringFollowingByte
    db " "
    call printStringFollowingByte
    db "M"
    ld a,0xE2
    call SUB_ram_3f7e
    call CurHomeinFrame
    ld a,0xFA
    call anotherPrintWithToken3A
    call printPlanetsRadius
    call printStringFollowingByte
    db " "
    ld a,0x11
    ld (storedByteVariable),a
    call parseStoredToken
    call CurHomeinFrame
    ld a,(ThargonMissionVar)
    and a
    jr z,printPlanetDescription
    ld hl,qq3
    call CompareHLtoSEED
    jr c,printPlanetDescription
    ld a,0xDE
    jp printStringA
; Prints a space
printSpace:
    ld a,0x20
    jp printString
printPlanetDescription:
    ld hl,(qq4)
    ld (seedvar1),hl
    ld hl,(qq5)
    ld (seedvar2),hl
    ld a,0x05
    jp printStringA
; Prints A via CallprintString and places the cursor
anotherPrintwithTokeninA:
    call CallprintString
    jr LAB_ram_43a0
; Places the cursor twice (new line and home) inside a framed screen
CurHomeinFrame:
    call placeCursor
LAB_ram_43a0:
    jp placeCursor
; ZX Spectrum: sysdata_print_economy (&EEA8)
; System data screen: the economy line (a prosperity adjective for 0-7 plus industrial or agricultural, from the economy byte).
printEconomy:
    ld a,0x70
    call printwithToken3a
    ld a,(economy)
    cp 0x04
    jr z,LAB_ram_43c3
    jr c,LAB_ram_43b3
    sub 0x05
LAB_ram_43b3:
    add a,0xAA
    call printString
LAB_ram_43b8:
    ld a,(economy)
    srl a
    srl a
    add a,0xA8
    jr anotherPrintwithTokeninA
LAB_ram_43c3:
    call printStringFollowingByte
    db 0xAD
    jr LAB_ram_43b8
; Prints the race of the system: alien race string if seed bit 7 is set, else the human token
printRace:
    ld hl,(qq5)
    ld a,l
    cp 0x80
    jp nc,printAlienRace
    ld a,0xBC
    jp printRaceString
BYTE_ram_43d7:
    db 0x01
; Prints the token held in the byte after the call (return address stepped past it)
printStringFollowingByte:
    pop hl
    ld a,(hl)
    inc hl
    push hl
; Prints token or character A: plain ASCII, jump tokens, string-table tokens or two-letter tokens
printString:
    cp 0x0E
    jp c,useJumpTokens1
    cp 0x20
    jp c,addx72toToken
    cp 0x60
    jp c,DrawASCIIChar
    cp 0x80
    jr c,todo_useStringtable
    cp 0xA0
    jp c,print_two_letter_token
    sub 0xA0
    jr todo_useStringtable
addx72toToken:
    add a,0x72
todo_useStringtable:
    ld hl,stringsTable
    ld d,a
    inc d
searchTokenInStringstableLoop:
    dec d
    jp z,printfoundString
    ld bc,0xFFFF
    xor a
    cpir
    jr searchTokenInStringstableLoop
; ZX Spectrum: recursive_other_token_loop (&D48E)
printfoundString:
    ld a,(hl)
    and a
    ret z
    push hl
    call printString
    pop hl
    inc hl
    jr printfoundString
; Prints the token A into the text buffer; stack and buffer choice depend on the current view
printStringA:
    ld hl,MainStackNStrings
    push af
    ld a,(Viewdirection)
    cp 0x04
    jr c,LAB_ram_442a
    ld a,(todoUnknownStatusFlags)
    and a
    jr nz,LAB_ram_442a
    ld hl,0x0FCA
LAB_ram_442a:
    pop af
    ld d,a
LAB_ram_442c:
    dec d
    jr z,LAB_ram_4456
    ld bc,0xFFFF
    xor a
    cpir
    jp LAB_ram_442c
; ZX Spectrum: print_other_token (&D470)
parseToken:
    ld b,a
    ld a,(BYTE_ram_43d7)
    cp 0x00
    ld a,b
    jr z,printString
    cp 0x20
    jp c,useJumpTokens2
    cp 0x5B
    jr c,DrawASCIIChar
    cp 0x81
    jp c,expandDescription
    cp 0xD7
    jr c,printStringA
    jp printaCharofDigram
LAB_ram_4456:
    ld a,(hl)
    and a
    ret z
    push hl
    call parseToken
    pop hl
    inc hl
    jr LAB_ram_4456
; Prints an ASCII character, upper-casing letters unless the capitals-state flag says otherwise
DrawASCIIChar:
    cp 0x41
    jr c,LAB_ram_449a
    cp 0x5B
    jr nc,LAB_ram_449a
    push af
    ld a,(todoPrintFlag3948)
    cp 0x01
    jr z,LAB_ram_44a0
    ld a,(0x394A)
    and a
    jr z,LAB_ram_4480
    xor a
    ld (0x394A),a
    ld (todoSomePrintFlag),a
    jr LAB_ram_44a0
LAB_ram_4480:
    ld a,(todoSomePrintFlag)
    cp 0x01
    jr nz,LAB_ram_4494
    xor a
    ld (todoSomePrintFlag),a
    ld a,(todoPrintFlag3948)
    cp 0x02
    jr z,LAB_ram_4494
    jr LAB_ram_44a0
LAB_ram_4494:
    pop af
    add a,0x20
    push af
    jr LAB_ram_44a0
LAB_ram_449a:
    push af
    ld a,0x01
    ld (todoSomePrintFlag),a
LAB_ram_44a0:
    ld a,(0x394B)
    cp 0x01
    jp z,buffer_justified_char
    pop af
; Advances charXY and draws the character in A; wraps to the next line past column 32
printCharAtLocationXY:
    push af
    ld hl,charXY
    inc (hl)
    ld a,(hl)
    cp 0x20
    jr c,GetAddressofChardef
    ld a,0x01
    ld (hl),a
    call GetYlocationofText
GetAddressofChardef:
    pop af
    ld h,(((SCREEN+0x1500)>>8)-5)/8       ; the glyph address is ((H:A * 2 + &100) * 4 + &100) with H = &1A at &D500: the base of the character set is encoded in this byte
    ld l,a
    add hl,hl
    inc h
    add hl,hl
    add hl,hl
    inc h
    cp 0x60
    jr c,dcNextStep
    ld a,h
    add a,0x06
    ld h,a
dcNextStep:
    push hl
    ld a,(flagWhichScreenToPrint)
    rla
    jr c,doDrawCharatBitmap
doDrawChar0xc000:
    ld a,(txtScreenOffset)
    ld l,a
    ld h,SCREEN>>14                     ; the five add hl,hl below make H = 64 * this: &C0 for the screen at &C000, &40 at &4000
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld a,(charXY)
    add a,l
    ld l,a
    add hl,hl
    jr DrawCharLoopsetup
doDrawCharatBitmap:
    ld a,(txtScreenOffset)
    ld h,a
    ld a,(charXY)
    ld l,a
    add hl,hl
    ld de,0xA000
    add hl,de
DrawCharLoopsetup:
    pop de
    ex de,hl
    ld b,0x08
DrawCharLoop:
    push af
    push bc
    ld a,(hl)
    and 0xF0
    ld c,a
    rrca
    rrca
    rrca
    rrca
    or c
    ld c,a
    ld a,(de)
smc_dcPatchAdr1:
    nop
    or c
smc_dcPatchAdr2:
    nop
    ld (de),a
    inc e
    ld a,(hl)
    and 0x0F
    ld c,a
    rrca
    rrca
    rrca
    rrca
    or c
    ld c,a
    ld a,(de)
smc_dcPatchAdr3:
    nop
    or c
smc_dcPatchAdr4:
    nop
    ld (de),a
    dec e
    pop bc
    pop af
    inc hl
    ld a,(flagWhichScreenToPrint)
    rla
    jr c,dcNextPixelline
    ld a,d
    add a,0x08
    ld d,a
    djnz DrawCharLoop
    ret
dcNextPixelline:
    ld a,e
    add a,0x40
    ld e,a
    jr nc,LAB_ram_452e
    inc d
LAB_ram_452e:
    djnz DrawCharLoop
    ret
; Patches the four commands patch-table bytes to 0x2F (cpl)
setCommandsCPL:
    ld a,0x2F
    jr LAB_ram_4537
; Patches the four commands patch-table bytes to 0x00 (nop)
setCommandsNOP:
    ld a,0x00
LAB_ram_4537:
    ld hl,commandsPatchTable
    ld b,0x04
LAB_ram_453c:
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld (de),a
    djnz LAB_ram_453c
    ret
commandsPatchTable:
    ; addresses of the 4 operand bytes that setCommandsNOP overwrites (self-patched operand bytes, labelled)
    dw smc_dcPatchAdr1,smc_dcPatchAdr2,smc_dcPatchAdr3,smc_dcPatchAdr4
    db 0x28,0x9B
flagWhichScreenToPrint:
    db 0x00
; Copies a colour table at DE into the colour operand bytes patched in the screen code
setColors:
    ld a,(de)
    inc de
    ld (0x28E7),a
    ld a,(de)
    inc de
    ld (0x28F0),a
    ld a,(de)
    inc de
    ld (0x28F9),a
    ld a,(de)
    inc de
    ld (0x291E),a
    ld a,(de)
    ld (0x2915),a
    ret
ColorsMarketBuyGoods:
    db "X_KTB"
ColorsSellGoods:
    db "X_JT["
ColorsEquipShip:
    db "X_LTG"
ColorsGalChart:
    db "TL]@B"
ColorsLocalChart:
    db "TL]@B"
ColorsDataonPlanet:
    db "TLCTB"
ColorsMarketplace:
    db "VRJTC"
ColorsCommanderStatus:
    db "D_NT["
ColorsInventory:
    db "D_MT["
ColorsFilemenu:
    db 0x5C,"KLTC"
printaCharofDigram:
    sub 0xD7
    ld hl,charsATAT
    jr subprintCharofDigram
; ZX Spectrum: print_two_letter_token (&D59C)
; Tokens &80-&9F of the text stream: index the two-letter table (DockedDigrams) and fall into the shared digram printer.
print_two_letter_token:
    sub 0x80
    ld hl,DockedDigrams
subprintCharofDigram:
    add a,a
    ld d,0x00
    ld e,a
    add hl,de
    ld a,(hl)
    push hl
    call DrawASCIIChar
    pop hl
    inc hl
loc_45B2:
    ld a,(hl)
    cp 0x3F
    ret z
    jp DrawASCIIChar
; ZX Spectrum: other_token_92_to_128 (&D5B4)
; Other-tokens &5B-&80: each indexes a run of five near-synonyms (synonym_group_table); text_rng picks one of the five.
expandDescription:
    ld d,0x00
    sub 0x5B
    ld e,a
    ld hl,synonym_group_table
    add hl,de
    ld a,(hl)
    push af
    call text_rng
    ld b,0x00
    cp 0x33
    jp c,incOption
    cp 0x66
    jp c,incOption1
    cp 0x99
    jp c,incOption2
    cp 0xCC
    jp c,incOption3
    inc b
incOption3:
    inc b
incOption2:
    inc b
incOption1:
    inc b
incOption:
    pop af
    add a,b
    jp printStringA
; ZX Spectrum: text_rng (&D5E1)
; Returns a pseudo-random byte in A for the text generator: a pair of words is shifted and added (the low word's low byte only is shifted, a quirk),
; rotated, and the high byte of the sum is returned.
text_rng:
    ld hl,(seedvar1)
    sla l
    ex de,hl
    ld hl,(seedvar2)
    adc hl,de
    ld a,h
    ld (seedvar1),hl
    ex de,hl
    ld (seedvar2),hl
    ret
synonym_group_table:
    djnz loc_4611
    ld a,(de)
    rra
    sbc a,e
    and b
    ld l,0xA5
    inc h
    add hl,hl
    dec a
    inc sp
    jr c,loc_45B2
    ld b,d
    ld b,a
    ld c,h
    ld d,c
    ld d,(hl)
    adc a,h
    ld h,b
    ld h,l
    add a,a
loc_4611:
    add a,d
    ld e,e
    ld l,d
    or h
    cp c
    cp (hl)
    pop hl
    and 0xEB
    ret p
    push af
    jp m,loc_7873
    ld a,l
    nop
    nop
; Fills the 0xC600 screen area with the pattern 0x0F0F (default entry of the fill routine)
sub_4622:
    ld de,0x0F0F
; Fill the screen from &C600 upwards with the word in DE, using stack pushes with interrupts off
SUB_ram_4625:
    ld hl,SCREEN+0x600
    di
    ld (stack1),sp
LAB_ram_462d:
    ld sp,hl
    ld b,0x80
LAB_ram_4630:
    push de
    push de
    push de
    push de
    push de
    push de
    djnz LAB_ram_4630
    ld a,h
    add a,0x08
    ld h,a
    bit 7,h                           ; 128K layout: loop while inside the screen page &4000-&7FFF (it was the carry out of H at &C000)
    jr z,LAB_ram_462d
    ld sp,(stack1)
    ei
    ret
stack1:
    db "!Q"
; Clear the screen, draw the border frame and put the text cursor at column 0, row 1
drawFrame:
    ld de,0x0000
    call SUB_ram_4625
    ld hl,0x0100
    ld (charXY),hl
; Draw the frame: top and bottom lines, then the left and right vertical edges (no screen clear)
drawTitleBoxframe:
    ld de,SCREEN
    call drawHorLineofFrame
    ld de,SCREEN+0x3DC0
    call drawHorLineofFrame
    ld hl,SCREEN
    ld e,0x80
    ld d,0xF7
    call SUB_ram_466f
    ld hl,SCREEN+0x03F
    ld e,0x10
    ld d,0xFE
; Draw one vertical frame edge at HL: 24 character rows of 8 lines, OR with E then AND with D
SUB_ram_466f:
    ld c,0x18
LAB_ram_4671:
    push hl
    ld b,0x08
todo_somethingLinecalculation:
    ld a,(hl)
    or e
    and d
    ld (hl),a
    ld a,h
    add a,0x08
    ld h,a
    djnz todo_somethingLinecalculation
    pop hl
    ld a,l
    add a,0x40
    ld l,a
    jr nc,LAB_ram_4686
    inc h
LAB_ram_4686:
    dec c
    jr nz,LAB_ram_4671
    ret
drawHorLineAt0xd880:
    ld hl,SCREEN+0x1880
    ex de,hl
; Fill 64 bytes at DE with &F0 to draw one horizontal frame line
drawHorLineofFrame:
    ld bc,0x0040
    ld a,0xF0
    jp FillmemoryRegionDEwithA
todo_stringpointer:
    db 0x00,0x00
BYTE_ram_4698:
    db 0x00
todo_stringend:
    db 0x00
BYTE_ram_469a:
    db 0x00,0x00
; ZX Spectrum: buffer_justified_char (&D6B9)
; Word-wrap engine: every character printed while justification is on (token control code 28) is appended to the line buffer here and,
; when the line is full, the buffer is output with the spaces spread out.
buffer_justified_char:
    ld hl,(todo_stringpointer)
    inc hl
    ld (todo_stringpointer),hl
    pop af
    ld (hl),a
    cp 0x2E
    jp z,todoPrintAWord
    cp 0x29
    jp z,todoPrintAWord
    ld b,a
    ld a,(todo_stringend)
    inc a
    ld (todo_stringend),a
    cp 0x1F
    ret c
    ld a,0x20
    cp b
    jp z,todoPrintAWord
    call SUB_ram_476b
    ld a,b
    ld (BYTE_ram_4698),a
    and a
    jr z,LAB_ram_46f7
    ld hl,(todo_stringpointer)
    inc hl
    ld c,b
    ld b,0x00
    ld de,tempString2
    ldir
    ld hl,strChar32
    ld a,(BYTE_ram_4698)
    ld e,a
    ld d,0x00
    add hl,de
    ld (BYTE_ram_469a),hl
    ld a,(BYTE_ram_4698)
    cp 0x1F
    jp nc,todoPrintAWord
    ld hl,(todo_stringpointer)
    ld b,a
LAB_ram_46ef:
    ld (hl),0x00
    inc hl
    djnz LAB_ram_46ef
    ld a,(BYTE_ram_4698)
LAB_ram_46f7:
    push af
    call SUB_ram_476b
    call SUB_ram_4789
    pop af
    dec a
    jr nz,LAB_ram_46f7
; Print the buffered justified-text word (tempString1, 30 chars) and refill the buffer (probably)
todoPrintAWord:
    ld hl,tempString1
    ld b,0x1E
LAB_ram_4707:
    push bc
    push hl
    ld a,(hl)
    call printCharAtLocationXY
    pop hl
    inc hl
    pop bc
    djnz LAB_ram_4707
    call placeCursor
    ld a,0x00
    ld (todoSomePrintFlag),a
LAB_ram_471a:
    ld hl,(BYTE_ram_469a)
    ld (todo_stringpointer),hl
    ld hl,strChar32
    ld (BYTE_ram_469a),hl
    ld a,(BYTE_ram_4698)
    ld (todo_stringend),a
    xor a
    ld (BYTE_ram_4698),a
    ld b,0x1E
    ld c,0x20
    ld hl,tempString2
    ld de,tempString1
LAB_ram_473a:
    ld a,(hl)
    ld (de),a
    ld (hl),c
    inc hl
    inc de
    djnz LAB_ram_473a
    ret
; ZX Spectrum: begin_justified_text (&D75A)
; Token control code 28: switches word-wrap buffering on, clears the word staging area and the buffer pointers, then joins buffer_justified_char.
begin_justified_text:
    ld a,0x01
    ld (0x394B),a
    ld b,0x1F
    ld a,0x20
    ld hl,tempString2
LAB_ram_474e:
    ld (hl),a
    inc hl
    djnz LAB_ram_474e
    ld hl,strChar32
    ld (BYTE_ram_469a),hl
    xor a
    ld (BYTE_ram_4698),a
    jr LAB_ram_471a
LAB_ram_475e:
    ld a,0x00
    ld (0x394B),a
    ld a,(todo_stringend)
    and a
    call nz,todoPrintAWord
    ret
; ZX Spectrum: - (&D783)
; Word-wrap engine: steps the buffer pointer back to the previous space, counting the characters skipped in B (wrapping at the buffer start).
SUB_ram_476b:
    ld hl,(todo_stringpointer)
    ld b,0x00
LAB_ram_4770:
    dec hl
    ld a,(hl)
    inc b
    cp 0x20
    jr nz,LAB_ram_4770
    ld (todo_stringpointer),hl
    ld de,tempString1
    and a
    sbc hl,de
    ret nc
    ld hl,tempString1End
    ld (todo_stringpointer),hl
    jr SUB_ram_476b
; ZX Spectrum: - (&D7A1)
; Word-wrap engine: overwrites the buffer with spaces from the cursor up to the next space (stops at a zero byte).
SUB_ram_4789:
    ld b,0x20
    ld hl,(todo_stringpointer)
LAB_ram_478e:
    ld a,(hl)
    ld c,a
    ld (hl),b
    ld b,c
    inc hl
    xor a
    cp c
    jr nz,LAB_ram_478e
    ret
; ZX Spectrum: sysdata_print_species (&EECE)
; System data screen: the inhabitants line, built in four parts from bit fields of the system seed (a human colony is one fixed token).
printAlienRace:
    ld a,h
    srl a
    srl a
    push af
    and 0x07
    cp 0x03
    jr nc,prRaceColor
    add a,0xE3
    call printTokenAndToken0x20
prRaceColor:
    pop af
    srl a
    srl a
    srl a
    cp 0x06
    jr nc,prRaceProperty
    add a,0xE6
    call printTokenAndToken0x20
prRaceProperty:
    ld hl,(qq3)
    ld a,h
    ld b,a
    ld hl,(qq4)
    ld a,h
    xor b
    and 0x07
    push af
    cp 0x06
    jr nc,prRace
    add a,0xEC
    call printTokenAndToken0x20
prRace:
    ld hl,(qq5)
    ld a,h
    and 0x03
    ld b,a
    pop af
    add a,b
    and 0x07
    add a,0xF2
printRaceString:
    push af
    call SUB_ram_ff39
    pop af
    jp printString
; ZX Spectrum: sysdata_print_radius (&EF21)
; System data screen: average planetary radius in km: high byte = (seed bits & &0F) + 11, low byte from the seed, printed as a 5-digit number.
printPlanetsRadius:
    ld hl,(qq5)
    ld a,h
    and 0x0F
    add a,0x0B
    ld hl,(qq4)
    ld l,h
    ld h,a
    ld a,0x06
    ld (numberOfDigits),a
    and a
    jp todo_SomethingwithDigits
; ZX Spectrum: - (&EF37)
; Compares the 6 bytes at HL with the current galaxy seed: carry clear if they are equal. Used to spot the galaxy's first system (the invasion target).
CompareHLtoSEED:
    ld de,galaxySeed
    ld b,0x06
LAB_ram_47ff:
    ld a,(de)
    cp (hl)
    jr nz,LAB_ram_4809
    inc de
    inc hl
    djnz LAB_ram_47ff
    and a
    ret
LAB_ram_4809:
    scf
    ret
; ZX Spectrum: show_market_prices (&EF48)
; Key K: the market prices screen.
MarketPrices:
    call DrawFramedTitlebox
    ld a,0xA7
    call printPlanetname
    ld hl,0x0310
    ld (charXY),hl
    ld a,0xFF
    call CallprintString
    ld de,ColorsMarketplace
    call setColors
    ld a,(todoLaunchFlag)
    and a
    ret nz
    xor a
    ld (storedByteVariable),a
    ld hl,pointerUnitMarketPrice
    ld (SCREEN+0x2FF8),hl
    ld hl,marketStock
    ld (SCREEN+0x2FFA),hl
LAB_ram_4839:
    call askBuyGood
    ld hl,storedByteVariable
    inc (hl)
    ld a,(hl)
    cp 0x11
    jr c,LAB_ram_4839
    ret
laserDirections:
    db 0x00
; Show the Commander status page: name, system, fuel, cash, legal state, rank, ship equipment
CommanderStatus:
    ld a,0x0B
    ld (Viewdirection),a
    ld a,0x96
    call printStringA
    ld de,ColorsCommanderStatus
    call setColors
    call displayAlertStateinHeader
    call printFollowingTokenWithSpace
statusTitleCol:
    IFDEF ENHANCED
    db 0x01                         ; the title starts in column 2 like the other headlines (was 0x06)
    ELSE
    db 0x06
    ENDIF
    call printStringFollowingByte
    db "~"
    ld a,0x03
    call VerticalPlacement
    ld a,0x02
    call todo_printlabeledVar
    ld a,0x03
    call todo_printlabeledVar
    ld a,0x05
    call VerticalPlacement
    call printStringFollowingByte
    db 0x05
    call printStringFollowingByte
    db 0x07
    ld a,0x71
    call printwithToken3a
    call printStringFollowingByte
    db " "
    ld b,0x12
    ld a,(legalStatus)
    and a
    jr z,LAB_ram_4895
    cp 0x32
    jr c,LAB_ram_4894
    inc b
LAB_ram_4894:
    inc b
LAB_ram_4895:
    ld a,b
    call CallprintString
    ld a,0x72
    call printwithToken3a
    call printStringFollowingByte
    db " "
    call getRank
    call killHook                       ; commonxx.asm: the rank name, " - <kills>", then the two new lines (was call anotherPrintwithTokeninA)
    call printStringFollowingByte
    db 0x11
    call SUB_ram_491a
    ld a,(largeCargoBay)
    call status_print_equip
    db "k"
    ld a,(fuelScoops)
    call status_print_equip
    db "o"
    ld a,(Missionflag)
    bit 7,a
    jr z,piPrintEquipment
    ld a,0xCF
    call printStringA
    call SUB_ram_491a
    jr piPrintOtherEquipment
piPrintEquipment:
    ld a,(ecmEquipped)
    call status_print_equip
    db "l"
piPrintOtherEquipment:
    ld a,(energyBomb)
    call status_print_equip
    db "q"
    ld a,(extraEnergyUnit)
    call status_print_equip
    db "r"
    ld a,(dockingComputer)
    call status_print_equip
    db "s"
    ld a,(galacticHyperdrive)
    call status_print_equip
    db "t"
    ld a,0xFF
    ld (laserDirections),a
    ld hl,laserTypes
    ld b,0x04
LAB_ram_48fb:
    push bc
    call prListEquippedLasers
    pop bc
    djnz LAB_ram_48fb
    ld a,(Missionflag)
    bit 6,a
    jr z,LAB_ram_490d
    call printStringFollowingByte
    db "}"
LAB_ram_490d:
    jp drawTitleBoxframe
; ZX Spectrum: status_print_equip (&F068)
; Called with an inline byte after the CALL (the equipment name token); A = that item's flag from the commander record. Prints the name when fitted.
status_print_equip:
    pop hl
    ld b,(hl)
    inc hl
    push hl
    and a
    ret z
    ld a,b
    call printString
; Place the cursor, then continue into SUB_ram_3f25 with A=5 (tail of the status page)
SUB_ram_491a:
    call placeCursor
    ld a,0x05
    jp SUB_ram_3f25
; ZX Spectrum: status_print_laser (&F07A)
; Status page: one laser mount line (HL walks the four mount bytes, &EF86 counts the mounts); nothing is printed for an empty mount.
prListEquippedLasers:
    ld a,(laserDirections)
    inc a
    ld (laserDirections),a
    ld a,(hl)
    inc hl
    and a
    ret z
    push hl
    push af
    ld a,(laserDirections)
    add a,0x60
    call printTokenAndToken0x20
    pop af
    cp 0x03
    jr c,LAB_ram_4940
    ld b,0x72
    jr LAB_ram_4942
LAB_ram_4940:
    ld b,0x66
LAB_ram_4942:
    add a,b
    call printString
    pop hl
    jr SUB_ram_491a
; Print a status label token followed by ':' and then the string whose number is in A
todo_printlabeledVar:
    ex af,af'
    call printFollowingTokenWithSpace
statusColon:
    IFDEF ENHANCED
    db 0x08                         ; the system names start in column 9, like the other lines (was 0x15); the colon is part of the label now
    ELSE
    db 0x15
    ENDIF
statusColonPrint:
    IFDEF ENHANCED
    ds 4                            ; nops: no colon (the 4 bytes of `call printStringFollowingByte / db ":"`)
    ELSE
    call printStringFollowingByte
    db ":"
    ENDIF
    ex af,af'
    jp CallprintString
; Return the commander rank index in A by scanning the rank thresholds against the kill score
getRank:
    ld hl,killScoreHigh
    ld a,(hl)
    and a
    jr nz,LAB_ram_4965
    dec hl
    ld de,Rankingbytes
    ld b,0x15
    jr LAB_ram_496a
LAB_ram_4965:
    ld de,RankingBytes2
    ld b,0x1A
LAB_ram_496a:
    ld a,(de)
    cp (hl)
    jr nc,LAB_ram_4972
    inc b
    inc de
    jr LAB_ram_496a
LAB_ram_4972:
    ld a,b
    ret
Rankingbytes:
    db 0x08,0x10," @",0x80,0xFF
RankingBytes2:
    db 0x02,0x0A,0x19,0xFF
; Show the pirates-boarded message box, wait for a key, then restart via ActionsAtEndOfMessage
printBoardedByMessage:
    push af
    ld a,0x0B
    ld de,colorsBoardedbyPirates
    ld hl,0x0703
    call drawFlipChart
    pop af
    call printStringA
    ld a,0x5D
    call printStringA
    ld hl,0x0B04
    ld (charXY),hl
    ld a,0xFF
    call printStringA
ActionsAtEndOfMessage:
    call sfxForKeyInput
    call WaitForKeypress
    call drawFrame
    call longDelay
    jp InitVariables
AskMissionThargonInvasion:
    ld a,0xDF
    ld de,colorsThargonInvasionQuestion
    ld hl,0x0405
    call drawFlipChart
    call WaitForKeypress
    cp 0x59
    jr z,ThargonMissionAccepted
    xor a
    ld (ThargonMissionVar),a
    ret
ThargonMissionAccepted:
    ld hl,Missionflag
    set 7,(hl)
    ld a,0x03
    ld (ThargonMissionVar),a
    ld a,0xE0
    ld de,colorsThargonMissionAccepted
    ld hl,0x0200
; Draw a mission message box (A message, HL cursor, DE colours), then wait for a key and resume
printMissionText:
    call drawFlipChart
    jr ActionsAtEndOfMessage
ThargonMissionFinished:
    ld hl,killScoreHigh
    inc (hl)
    xor a
    ld (ThargonMissionVar),a
    ld hl,Missionflag
    set 3,(hl)
    ld hl,strFLORENCE
    ld de,saveGameRam
    ld bc,0x0009
    ldir
    ld a,0x0A
    ld de,colorsThargonMissionFinished
    ld hl,0x0400
    jr printMissionText
strFLORENCE:
    db "FLORENCE",0x00
; Draw the frame, set view 14 and colours from DE, then print message A at cursor HL
drawFlipChart:
    push af
    push hl
    push de
    call drawFrame
    ld a,0x5C
    call printStringA
    ld a,0x0E
    ld (Viewdirection),a
    pop de
    call setColors
    pop hl
    ld (charXY),hl
    pop af
    jp printStringA
colorsSuperNovaStart:
    db "T",0x5C,"^N^"
colorsSuperNovaMissionEnd:
    db "VNTTJ"
colorsThargonInvasionQuestion:
    db "^KRTR"
colorsThargonMissionAccepted:
    db "DWMTM"
colorsThargonMissionFinished:
    db "UWGTG"
colorsBoardedbyPirates:
    db 0x5C,"KMTM"
Inventory:
    ld a,0x0C
    ld (Viewdirection),a
    ld a,0x96
    call printStringA
    ld a,0xA4
    call printPlanetname
    ld de,ColorsInventory
    call setColors
    ld a,0x03
    call VerticalPlacement
    call printStringFollowingByte
    db 0x05
    ld a,0x07
    call CallprintString
    ld a,(largeCargoBay)
    and a
    jr z,LAB_ram_4a72
    ld hl,0x58C1
    ld a,0x05
    call printStringFollowingByte
    db "k"
LAB_ram_4a72:
    call placeCursor
    ld a,(Missionflag)
    bit 5,a
    jr z,LAB_ram_4a84
    ld a,0x0C
    call printStringA
    call placeCursor
LAB_ram_4a84:
    xor a
    ld (storedByteVariable),a
    ld hl,dat_38E1
    ld (SCREEN+0x2FF6),hl
LAB_ram_4a8e:
    IFDEF MISSIONS
    call mxInvHook                  ; missions_flight.asm: a Trumbles line before the first good
    ELSE
    call prQuantityofGoodinCargohold
    ENDIF
    call nc,placeCursor
    ld hl,storedByteVariable
    inc (hl)
    ld a,(hl)
    cp 0x11
    jr c,LAB_ram_4a8e
    ret
; Reset the commander save block (&66 bytes) to the default commander
ClearSaveGameRam:
    ld hl,emptyDefaultsave
    ld de,saveGameRam
    ld bc,0x0066
    ldir
    ret
smc_patch1:
    db 0x00
countdownnumberhypspace2:
    db 0x00
smc_patch3:
    db 0x00
msgCoordinateX:
    db 0x00
tokenToPrint:
    db 0x00
bountyforShip:
    db 0x00,0x00
destroyedEquipmentNumber:
    db 0xF5
; Print the current view's title (views 0-3) and then run the per-frame message handler
printViewPortLabel:
    xor a
    ld (todoPrintFlag3948),a
    ld a,(Viewdirection)
    cp 0x04
    jr c,LAB_ram_4acd
    jr viewLabelSkip                  ; stock clears the two cells at column 2 here (the view name); the screen was cleared already and the headlines start in column 2 now, so it would erase their first two letters
    ds 10                             ; the stock clear, kept as padding: later labels keep their offsets
viewLabelSkip:
    call SUB_ram_4aee
    ret
LAB_ram_4acd:
    ld hl,flagWhichScreenToPrint
    set 7,(hl)
    ld hl,0x010A
    ld (charXY),hl
    ld a,(Viewdirection)
    add a,0x60
    call printString
    ld a,0xAF
    call CallprintString
    call SUB_ram_4aee
    ld hl,flagWhichScreenToPrint
    res 7,(hl)
    ret
; ZX Spectrum: - (&DAB4)
SUB_ram_4aee:
    call CountDowntoHyperJump
    call chkConditionNSetIndicatorColors
    ld hl,countdownnumberhypspace2
    ld a,(hl)
    and a
    jr nz,printFlightMessage
    ld hl,smc_patch3
    inc (hl)
    bit 0,(hl)
    jr nz,LAB_ram_4b68
    ld b,0x08
    ld hl,msgECMJammer
LAB_ram_4b08:
    bit 7,(hl)
    jr nz,LAB_ram_4b11
    inc hl
    inc hl
    djnz LAB_ram_4b08
    ret
; ZX Spectrum: - (&DAD7)
LAB_ram_4b11:
    res 7,(hl)
    ld c,(hl)
    inc hl
    ld b,(hl)
LAB_ram_4b16:
    push bc
    call sfxForKeyInput
    pop bc
prinFlightMessage:
    ld a,0x0E
    ld (countdownnumberhypspace2),a
; Queue an in-flight message: C is its x position, B its token number
prTokeninBatPosC:
    ld a,c
    ld (msgCoordinateX),a
    ld a,b
    ld (tokenToPrint),a
    ret
printFlightMessage:
    dec (hl)
    cp 0x04
    ret c
    ld a,(Viewdirection)
    cp 0x04
    ret nc
    ld a,(msgCoordinateX)
    ld l,a
    ld h,0x0E
    ld (charXY),hl
    ld a,(tokenToPrint)
    cp 0xFD
    jr z,printDestroyedEquipment
    cp 0xE2
    jr z,printBountycredits
goprintFlightMessage:
    ld a,(tokenToPrint)
    jp CallprintString
printDestroyedEquipment:
    ld a,(destroyedEquipmentNumber)
    cp 0x73
    jr z,LAB_ram_4b5a
    ld hl,charXY
    inc (hl)
    inc (hl)
    inc (hl)
LAB_ram_4b5a:
    call printString
    jr goprintFlightMessage
printBountycredits:
    ld hl,(bountyforShip)
    scf
    call todo_SomethingwithDigits
    jr goprintFlightMessage
LAB_ram_4b68:
    ld a,(shipEnergyBank4)
    cp 0x9F
    jr c,setEnergyLowMessage
    ld a,(flagCanScoopFuel)
    and a
    jr nz,ScoopFuel
    ld a,(flagDockingComputerOn)
    and a
    jr nz,msgDockingComputersOn
    ld hl,smc_patch1
    ld a,(hl)
    and a
    jr nz,LAB_ram_4b9a
    ld a,0x3C
    ld (hl),a
    ld a,(ThargonMissionVar)
    dec a
    jr z,msgMayDay
    ld a,(FlightMode)
    and a
    ret z
    ld a,(BYTE_ram_3933)
    and a
    ret nz
    ld bc,0xC202
    jr gotoSetMsgInBC
LAB_ram_4b9a:
    dec (hl)
    ret
msgMayDay:
    ld bc,0x0F03
    jr gotoSetMsgInBC
msgDockingComputersOn:
    ld bc,0x7B05   ; flight message id (bc = message pair)
    jr gotoSetMsgInBC
ScoopFuel:
    ld a,(fuelScoops)
    and a
    ret z
    ld a,(fuel)
    inc a
    call setFuel
    ld bc,0xA008
gotoSetMsgInBC:
    jp prinFlightMessage
setEnergyLowMessage:
    xor a
    ld (flagCloakingDeviceActive),a
    ld bc,0x640A   ; flight message id (bc = message pair)
    jr gotoSetMsgInBC
; ZX Spectrum: - (&DB91)
resetInflightMessagesFlags:
    ld b,0x08
    ld hl,msgECMJammer
LAB_ram_4bc6:
    res 7,(hl)
    inc hl
    inc hl
    djnz LAB_ram_4bc6
    xor a
    ld (tokenToPrint),a
    ret
CountDownNumberForHyperspace:
    db 0x00
; Handle the hyperspace/galactic jump key: check fuel, set the tunnel flag and start the countdown
SUB_ram_4bd2:
    ld hl,keybFlags3
    ld a,(hl)
    and 0x30
    ret z
    ld b,a
    ld a,(hl)
    and 0xCF
    ld (hl),a
    ld a,(CountDownNumberForHyperspace)
    and a
    ret nz
    ld a,(todoUnknownStatusFlags)
    and a
    jr z,LAB_ram_4c30
    bit 5,b
    jr z,tryHyperSpace
    bit 4,b
    ret z
    ld a,(galacticHyperdrive)
    and a
    ret z
    ld a,0x02
    ld (tunnelFlag1),a
    ld bc,buf_7406
    jr doSpaceJumpafterCountDown
tryHyperSpace:
    call SUB_ram_3dc6
    ld hl,(travelDistance)
    ld a,h
    and a
    jr nz,msgOutofHyperSpaceRange
    ld a,l
    and a
    ret z
    ld b,a
    ld a,(fuel)
    sub b
    jr c,msgOutofHyperSpaceRange
    ld a,0x01
    ld (tunnelFlag1),a
    ld bc,0xC005
doSpaceJumpafterCountDown:
    ld a,0x15
    ld (CountDownNumberForHyperspace),a
    ld (countdownnumberhypspace2),a
    call prTokeninBatPosC
    call sfxForKeyInput
    ret
msgOutofHyperSpaceRange:
    ld bc,0xC106
    jp LAB_ram_4b16
LAB_ram_4c30:
    call drawFrame
    ld hl,0x070B
    ld (charXY),hl
    ld a,0x01
    ld (todoPrintFlag3948),a
    ld a,0xCD
    call printStringA
    call sfxForKeyInput
    call longDelay
    call clearKeyBuffer
    jp CommanderStatus
; Tick the hyperspace countdown, show it at the top of the view and make the jump at zero
CountDowntoHyperJump:
    ld hl,CountDownNumberForHyperspace
    ld a,(hl)
    and a
    ret z
    dec (hl)
    jr z,makeHyperjump
    ld b,a
    ld a,0x02
    ld (numberOfDigits),a
    IFDEF ENHANCED
    ld hl,0x0105                    ; the count starts at column 6: the station headlines now begin in column 2 and the count (printed in every frame) covered their first letters
    ELSE
    ld hl,0x0101
    ENDIF
hyperCountPos equ $ - 2
    ld (charXY),hl
    ld a,b
    srl a
    jp printNumber
makeHyperjump:
    call resetInflightMessagesFlags
    ld a,(tunnelFlag1)
    sub 0x02
    jr nz,someHyperSpaceFunctions
makeGalacticJump:
    xor a
    ld (ThargonMissionVar),a
    ld a,(FlightMode)
    and a
    jr z,contGalacticJump
    xor a
    ld (FlightMode),a
    ld (BYTE_ram_3933),a
contGalacticJump:
    ld (galacticHyperdrive),a
    ld a,(currentGalaxy)
    inc a
    ld (fuelPriceByte),a
    and 0x07
    ld (currentGalaxy),a
    ld hl,galaxySeed
    call randomizeGalSeed
    call randomizeGalSeed
    call randomizeGalSeed
    xor a
    ld (legalStatus),a
    call SUB_ram_3dc6
    jp generateTargetSystemparAtHyperjump
; ZX Spectrum: rotate_word_left (&DC83)
; Rotates the 16-bit word at HL left by one bit and advances HL by 2 (one step of the galaxy seed twist).
randomizeGalSeed:
    ld e,(hl)
    rlc e
    ld (hl),e
    inc hl
    ld d,(hl)
    rlc d
    ld (hl),d
    inc hl
    ret
someHyperSpaceFunctions:
    ld a,(FlightMode)
    and a
    jr nz,makeGalacticJump
    ld a,(travelDistance)
    ld b,a
    ld a,(fuel)
    sub b
    ld c,a
    call setFuel
    ld a,0x46
    sub c
    ld b,a
    ld a,(economy)
    add a,a
    add a,b
    ld (fuelPriceByte),a
    ld hl,legalStatus
    srl (hl)
    ld a,(keybFlags0)
    bit 6,a
    jr nz,todoMisJump
    ld a,(todo_varEscapepod)
    cp 0x40
    jr nz,generateTargetSystemparAtHyperjump
    cp 0x20
    jr nz,generateTargetSystemparAtHyperjump
todoMisJump:
    inc a
    ld (todoLaunchFlag),a
    ld hl,presentSystemX
    ld de,PresentPlanetX
    ld a,(de)
    add a,(hl)
    rr a
    ld (hl),a
    ld (de),a
    ld hl,presentSystemY
    ld de,PresentPlanetY
    ld a,(de)
    add a,(hl)
    rr a
    ld (hl),a
    ld (de),a
    xor a
    ld (FlagStationNear),a
    ld (strPLANETNAME1),a
    ld (strPLANETNAME2),a
    jp setShipvarsAtArrival
tableSystemColors:
    db "WCDLJV]LXKG@UC",0x5C,"N"
    db "SULKWBJ^"
; Patch three colour bytes from tableSystemColors, picked by the low 3 bits of the present system X
setViewColors:
    ld a,(presentSystemX)
    and 0x07
    ld b,a
    add a,a
    add a,b
    ld hl,tableSystemColors
    call SetTableBegintoAofHL
    ld a,(hl)
    ld (0x28B5),a
    inc hl
    ld a,(hl)
    ld (0x28AC),a
    inc hl
    ld a,(hl)
    ld (0x28A3),a
    ret
generateTargetSystemparAtHyperjump:
    xor a
    ld (todoLaunchFlag),a
    ld hl,qq3
    ld de,presentSystemSeed
    ld bc,0x0006
    ldir
    ld hl,strPLANETNAME2
    ld de,strPLANETNAME1
    ld bc,0x0008
    ldir
    ld a,(techLevel)
    ld (presentTechLevel),a
    ld a,(government)
    ld (marketStock),a
    call GenPriceAndStockEntry1
    ld b,0x12
    xor a
    ld hl,posDataSun
gtsClearCoordsLoop:
    ld (hl),a
    inc hl
    djnz gtsClearCoordsLoop
    ld a,0xFF
    ld (StationEnergy),a
    call setViewColors
    ld hl,(qq3)
    ld de,(qq4)
    ld bc,(qq5)
    ld a,b
    and 0x83
    or 0x01
    ld (todo_planet3dCoordX2),a
    ld a,c
    and 0x83
    or 0x01
    ld (todo_planet3dCoordY),a
    ld a,d
    or e
    and 0x07
    add a,0x04
    or 0x81
    ld (todo_planet3dCoordZ),a
    ld a,l
    and 0x83
    or 0x01
    ld (dataSpaceStationPosXh),a
    ld a,e
    and 0x83
    or 0x01
    ld (dataSpaceStationPosYh),a
    ld a,h
    or l
    and 0x07
    add a,0x03
    ld (dataSpaceStationPosZh),a
    push bc
    ld bc,0x0009
    ld hl,posDataPlanet
    ld de,sEntityxlo
    ldir
    pop bc
    ld a,(dataSpaceStationPosZh)
    ld hl,sEntityZhi
    srl c
    jr c,LAB_ram_4ddf
    ld a,(dataSpaceStationPosXh)
    ld hl,sEntityxhi
LAB_ram_4ddf:
    set 7,(hl)
    ld b,a
    and 0x7F
    srl c
    jr c,LAB_ram_4df8
    cp 0x01
    jr nz,LAB_ram_4df4
    ld d,a
    ld a,b
    xor 0x80
    ld b,a
    ld a,d
    jr LAB_ram_4df5
LAB_ram_4df4:
    dec a
LAB_ram_4df5:
    dec a
    jr LAB_ram_4df9
LAB_ram_4df8:
    inc a
LAB_ram_4df9:
    add a,a
    sla b
    rr a
    inc hl
    ld (hl),a
    xor a
    ld hl,sEntitynosevXlo
    ld b,0x12
LAB_ram_4e06:
    ld (hl),a
    inc hl
    djnz LAB_ram_4e06
    ld hl,dataSpaceStationPosZl
    ld a,(sEntityZhi)
    cp (hl)
    ld a,0x7F
    ld (sEntityroofvYhi),a
    jr nz,LAB_ram_4e31
    ld bc,sEntitysidevzhi
    ld de,sEntitynosevXhi
    ld (bc),a
    ld (de),a
    ld hl,dataSpaceStationPosXh
    ld a,(sEntityxsign)
    cp (hl)
    ld a,0xFF
    jr c,LAB_ram_4e2e
    ld (de),a
    jr LAB_ram_4e4c
LAB_ram_4e2e:
    ld (bc),a
    jr LAB_ram_4e4c
LAB_ram_4e31:
    ld bc,sEntitysidevXhi
    ld de,sEntitynosevZhi
    ld hl,dataSpaceStationPosZh
    ld a,(sEntityZSign)
    cp (hl)
    jr c,LAB_ram_4e48
    ld a,0xFF
    jr LAB_ram_4e4a
LAB_ram_4e44:
    ld a,0x05
    jr LAB_ram_4e83
LAB_ram_4e48:
    ld a,0x7F
LAB_ram_4e4a:
    ld (bc),a
    ld (de),a
LAB_ram_4e4c:
    ld a,(PresentPlanetX)
    ld (presentSystemX),a
    ld a,(PresentPlanetY)
    ld (presentSystemY),a
    ld a,(currentGalaxy)
    and a
    jr z,setShipvarsAtArrival
    ld hl,sEntityunknown
    bit 7,(hl)
    res 7,(hl)
    jr nz,LAB_ram_4e44
    ld hl,ThargonMissionVar
    ld a,(hl)
    and a
    jr z,chkSuperNovaMission
    dec a
    jr nz,LAB_ram_4e74
    inc (hl)
    jr LAB_ram_4e79
LAB_ram_4e74:
    cp 0x03
    jr nz,LAB_ram_4e79
    ld (hl),a
LAB_ram_4e79:
    ld hl,presentSystemSeed
    call CompareHLtoSEED
    jr c,chkSuperNovaMission
    ld a,0x04
LAB_ram_4e83:
    ld (ThargonMissionVar),a
chkSuperNovaMission:
    ld hl,(jumpCounter)
    inc hl
    ld (jumpCounter),hl
    ld de,Missionflag
    ld a,(de)
    rrca
    jr nc,todo_Missionstage1
    rrca
    jr nc,todo_Missionstage2
    rrca
    jr nc,todo_Missionstage3
chkEnemyStation:
    ld hl,todo_varEscapepod
    ld a,(marketStock)
    xor 0xFF
    and 0x07
    cp (hl)
    jr c,setShipvarsAtArrival
    ld hl,sEntityRoll
    res 7,(hl)
setShipvarsAtArrival:
    ld a,0x01
    IFDEF MISSIONS
    call mxArrive                   ; missions_flight.asm: Trumbles breed (replaces ld (tunnelFlag2),a)
    ELSE
    ld (tunnelFlag2),a
    ENDIF
    xor a
    ld (Viewdirection),a
    ld (CockpitTemp),a
    ld (flagCanScoopFuel),a
    ld (missileLockState),a
    ld (aspMissionState),a
    ld a,0xA0
    ld (Altitude),a
    ret
todo_Missionstage1:
    ld a,l
    cp 0x20
    jr c,chkEnemyStation
    ex de,hl
    set 0,(hl)
    ld a,0x01
    ld (FlightMode),a
    ld l,0x02
    call removeFuel
    jr setShipvarsAtArrival
todo_Missionstage2:
    ld a,l
    cp 0x80
    jr c,chkEnemyStation
    ex de,hl
    set 1,(hl)
    jr setShipvarsAtArrival
todo_Missionstage3:
    ld a,l
    cp 0xFE
    jr c,chkEnemyStation
    ex de,hl
    set 2,(hl)
    ld a,0x01
    ld (ThargonMissionVar),a
    jr setShipvarsAtArrival
; Set the supernova-mission message flag and zero the fuel (does nothing if already empty)
removeFuel:
    ld a,(fuel)
    and a
    ret z
    ld hl,msgSupernovaMission
    set 7,(hl)
    xor a
; Store A as the fuel level (capped at &46) and update the fuel bar value (about 2.25 x fuel)
setFuel:
    cp 0x47
    jr c,LAB_ram_4f05
    ld a,0x46
LAB_ram_4f05:
    ld (fuel),a
    add a,a
    ld b,a
    srl a
    srl a
    srl a
    add a,b
    ld (FuelbarValue),a
    ret
    db 0x01
; Page the lower ROM in through the gate array (&7F89)
enableROM:
    ld bc,0x7F89   ; gate array: mode and ROM select value
    out (c),c
    ret
; Page the lower ROM out through the gate array (&7F8D)
disableROM:
    ld bc,0x7F8D
    out (c),c
    ret
; Copy the ROM character set into &D600-&DEFF and patch a few glyphs from the charPatch tables
copyCharset:
    di
    call enableROM
    ld hl,0x3900
    ld de,SCREEN+0x1600
    ld bc,0x0200
    ldir
    ld de,SCREEN+0x1E00
    ld bc,0x0100
    ldir
    call disableROM
    ld hl,smc_charPatchD628
    ld de,SCREEN+0x1628
    ld bc,0x0010
    ldir
    ld hl,smc_charPatchD650
    ld de,SCREEN+0x1650
    ld bc,0x0010
    ldir
    ld hl,smc_charPatchD6D8
    ld de,SCREEN+0x16D8
    ld bc,0x0020
    ldir
    ld hl,smc_charPatchD700
    ld de,SCREEN+0x1700
    ld bc,0x0008
    ldir
    ld hl,smc_charPatchD7D8
    ld de,SCREEN+0x17D8
    ld bc,0x0028
    ldir
    ret
smc_charPatchD628:
    db 0x00,"~BBB~",0x00,0xFF,0x00,0xC0,0xF0,0xF8,0xFC,0xFC,0xFE,0xFE
smc_charPatchD650:
    db 0x18,0x18,0x18,0x18,0x18,0x00,0x18,0x00,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0xFF
smc_charPatchD6D8:
    db 0x00,0x00,0x1F,0x1F,0x18,0x18,0x18,0x1F,0x00,0x00,0xE0,0xE0,0x00,0x00,0x00,0xC0
    db 0x18,0x18,0x18,0x1F,0x1F,0x00,0x00,0xFF,0x00,0x00,0x00,0xE0,0xE0,0x00,0x00,0xFF
smc_charPatchD700:
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF
smc_charPatchD7D8:
    db 0x00,0x00,0x07,0x07,0x06,0x06,0x06,0x07,0x01,0x01,0xF1,0xF1,"1",0x01,0x01,0xF1
    db 0x00,0x00,0x06,0x07,0x07,0x00,0x00,0xFF,"111",0xF1,0xF1,0x01,0x01,0xFF
    db 0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01
gcMinY:
    db 0x00
gcMaxY:
    db 0x00
; XOR-plot the four arms of the chart cursor crosshair around the stored cursor position
drawReticule:
    call getCrosshairCoordinates
LAB_ram_4fe9:
    call chkPlotOnChart
    dec c
    jr z,LAB_ram_4ff2
    dec a
    jr nz,LAB_ram_4fe9
LAB_ram_4ff2:
    call getCrosshairCoordinates
LAB_ram_4ff5:
    call chkPlotOnChart
    inc c
    jr z,LAB_ram_4ffe
    dec a
    jr nz,LAB_ram_4ff5
LAB_ram_4ffe:
    call getCrosshairCoordinates
LAB_ram_5001:
    call chkPlotOnChart
    inc b
    dec a
    jr nz,LAB_ram_5001
    call getCrosshairCoordinates
LAB_ram_500b:
    call chkPlotOnChart
    dec b
    dec a
    jr nz,LAB_ram_500b
    ret
; Load BC with the stored chart cursor position and A with the crosshair arm length
getCrosshairCoordinates:
    ld bc,(storePresPlanetX)
    ld a,(txt_hpos)
    ret
; XOR one pixel at (C,B) into the screen if it is inside the chart area; keeps AF and BC
chkPlotOnChart:
    push af
    push bc
    ld a,(Viewdirection)
    cp 0x08
    jr nz,cpp1
    ld a,b
    cp 0xA8
    jr nc,cppLeave
    jr cpp2
cpp1:
    ld a,b
    cp 0x99
    jr nc,cppLeave
cpp2:
    cp 0x18
    jr c,cppLeave
    call cirGetScrAddr
    call cppSetPixelmask
    ld a,(hl)
    xor c
    ld (hl),a
cppLeave:
    pop bc
    pop af
    ret
; Return in C the mode 1 pixel mask for pixel number A (0-3) within a byte
cppSetPixelmask:
    inc a
    ld c,0x88
cpp5:
    rlc c
    dec a
    jr nz,cpp5
    ret
storePresPlanetX:
    db 0xF0
storePresPlanetY:
    db "d"
txt_hpos:
    db 0x0A
distVal:
    db 0x00
; Asp mission state (ZX Spectrum: shared throttle &9CB2): 0 idle, 1 Asp just spawned, 2 it has you lined up with the cloak off,
; 3 marked Asp shot down by the player's laser, canister pending (cleared when scooped, see fsGetRandomGood).
aspMissionState:
    db 0x00,0x00
todoLaserVar2:
    db 0x00
entityMassLocked:
    db 0x00
flagEnergyBombActivated:
    db 0x00
storeEntityEnergy1:
    db 0x00
shipInCrosshair:
    db 0x00,0x00
todoActiveSlots:
    db 0x00
flagCorrectOrientation:
    db 0x00
ecmActiveFlag:
    db 0x00
todoLaserVar3:
    db 0x00
damageToFrontShield:
    db 0x00
damageToRearShield:
    db 0x00
storeEntityEnergy2:
    db 0x00
countShipsLaunchedByStation:
    db 0x00
missileTargetEntityNr:
    db 0x00,0xDD,"!G",0x04,0xFD,"!TP"
; Per-frame pass over the entity slots: maybe spawn a station ship, reset damage and target state (probably)
handleEntitys:
    jp hullBegin                        ; 128K build: starts the deferred hull list, then ld a,(ThargonMissionVar)
heResume:
    cp 0x04
    jr nz,loc_5072
    ld hl,sEntityRole
    set 2,(hl)
loc_5072:
    ld a,(BYTE_ram_1c3c)
    and a
    ld a,0xB1
    jr z,heNotOnThargonMission
    ld a,0xA9
heNotOnThargonMission:
    ld a,(todoLaserVar2)
    dec a
    ld (todoLaserVar2),a
    ld b,a
    ld a,(FlagStationNear)
    and a
    jr nz,LAB_ram_509c
    ld a,(todoLaunchFlag)
    and a
    jr nz,LAB_ram_509c
    ld a,(countShipsLaunchedByStation)
    cp 0x04
    jr nc,LAB_ram_509c
    ld a,b
    and a
    call z,spawnCommandParser
LAB_ram_509c:
    xor a
    ld (todoLaserVar3),a
    ld (damageToRearShield),a
    ld (damageToFrontShield),a
    ld (shipInCrosshair),a
    ld (storeEntityEnergy2),a
    ld (storeEntityEnergy1),a
    ld (entityMassLocked),a
    ld c,a
    ld ix,sEntityxlo
    ld de,0x0027
    ld b,0x06
LAB_ram_50bc:
    add ix,de
    ld a,(ix+34)
    and a
    jr z,LAB_ram_50cb
    bit 6,(ix+32)
    jr z,LAB_ram_50cb
    inc c
LAB_ram_50cb:
    djnz LAB_ram_50bc
    ld a,c
    ld (countShipsLaunchedByStation),a
    ld ix,sEntityxlo
    ld a,0x08
LAB_ram_50d7:
    push af
    ld b,a
    ld (missileTargetEntityNr),a
    ld a,(ix+34)
    and a
    jp z,LAB_ram_51fb
    ld (storeEntityEnergy1),a
    bit 2,(ix+38)
    jr nz,LAB_ram_50ef
    ld (storeEntityEnergy2),a
LAB_ram_50ef:
    ld a,(todoLaserVar2)
    ld c,a
    bit 3,(ix+38)
    jr nz,LAB_ram_50fe
    ld a,0x01
    ld (entityMassLocked),a
LAB_ram_50fe:
    ld a,(flagEnergyBombActivated)
    and a
    jr z,LAB_ram_5115
    bit 2,(ix+38)
    jr nz,LAB_ram_5115
    ld a,(iy+6)
    cp 0x27
    jr z,LAB_ram_5115
    set 4,(ix+32)
LAB_ram_5115:
    bit 2,(ix+33)
    jr z,LAB_ram_5127
    ld a,(ix+33)
    and 0x60
    jr z,LAB_ram_5127
    ld a,0x01
    ld (todoActiveSlots),a
LAB_ram_5127:
    ld a,(buf_1B73)
    and a
    jr nz,LAB_ram_5133
    ld a,(todoActiveSlots)
    and a
    jr z,LAB_ram_5137
LAB_ram_5133:
    set 2,(ix+33)
LAB_ram_5137:
    ld h,(ix+36)
    ld l,(ix+35)
    push hl
    pop iy
    ld a,(ix+32)
    and 0x30
    jr z,LAB_ram_51ae
    sub 0x20
    jp nz,LAB_ram_51e0
    res 5,(ix+32)
    ld (ix+30),a
    ld a,0xC0
    ld (ix+29),a
    bit 0,(ix+38)
    jr nz,todo_killedsomeone
    ld hl,sfxFlags1Bitmap
    set 2,(hl)
    ld a,(aspMissionState)
    and a
    jr z,todo_killedsomeone
    cp 0x03
    jr z,aspGateClearIfBlueprint1E
    bit 6,(ix+38)
    jr z,todo_killedsomeone
    jr aspGateReset
; ZX Spectrum: &9DD6. State 3 demands blueprint byte +1 == &1E, which no ship has, so a pending canister (3) is never cleared here.
aspGateClearIfBlueprint1E:
    ld a,(iy+1)
    cp 0x1E
    jr nz,todo_killedsomeone
; ZX Spectrum: &9DDD. Marked ship finished exploding in state 1/2 (non-laser death): reset the state to 0.
aspGateReset:
    xor a
    ld (aspMissionState),a
todo_killedsomeone:
    xor a
    ld (ix+34),a
    call chkEntityWasMissiletarget
    ld d,(iy+9)
    ld e,(iy+8)
    IFDEF MISSIONS
    call mxKillHook                 ; missions_flight.asm: getBounty, then marks the Constrictor as killed
    ELSE
    call getBounty
    ENDIF
    ld d,(iy+22)
    ld e,(iy+21)
    srl d
    rr e
    call AddDEtoKillScore
    ld a,(ix+33)
    and 0x60
    jr z,LAB_ram_51fb
    ld a,(legalStatus)
    or 0x40
    ld (legalStatus),a
    jr LAB_ram_51fb
LAB_ram_51ae:
    ld a,b
    xor c
    and 0x0F
    bit 6,(ix+32)
    jr z,LAB_ram_51c8
    bit 0,(ix+38)
    jr z,LAB_ram_51c3
    call MissileDestroyedbyECM
    jr LAB_ram_51c8
LAB_ram_51c3:
    and 0x03
    call z,ActDeponEnergy
LAB_ram_51c8:
    call SUB_ram_531d
    call SUB_ram_5dcf
    push ix
    ld de,0x0009
    add ix,de
    call todoSomethingwithSine
    call todoSomethingwithSine
    call todoSomethingwithSine
    pop ix
LAB_ram_51e0:
    call TryScoopGood
    call SUB_ram_564f
    res 3,(ix+32)
    ld a,(ix+32)
    and 0x30
    cp 0x10
    jr nz,LAB_ram_51fb
    set 5,(ix+32)
    res 4,(ix+32)
LAB_ram_51fb:
    pop af
    ld de,0x0027
    add ix,de
    dec a
    jp nz,LAB_ram_50d7
    call hullFlush                      ; 128K build: draws the queued hulls far to near, then xor a / ld (flagEnergyBombActivated),a
    nop
    ld a,(entityMassLocked)
    and a
    ret nz
    ld (todoActiveSlots),a
    ret
; ZX Spectrum: normalize_position_vector (&9E73)
; In: IX = an encoded position vector (3 components). Squares and sums the components (square_position_component), takes the square root
; (approx_sqrt_16bit) = the vector's length, then divides each component by it (normalize_position_component): the vector becomes a unit vector in place.
; Out: DE = the approximate length. The bytes are still a db run: z80dis cannot decode push ix / pop ix.
normalize_position_vector:
    push ix
    call square_position_component
    push hl
    call square_position_component
    push hl
    call square_position_component
    pop de
    add hl,de
    pop de
    add hl,de
    pop ix
    call approx_sqrt_16bit
    ex de,hl
    push ix
    call normalize_position_component
    call normalize_position_component
    call normalize_position_component
    pop ix
    ret
; ZX Spectrum: square_position_component (&9E98)
; In: IX = an encoded position component (15-bit magnitude, sign in bit 7 of the high byte). Out: HL = magnitude squared / 256 (hi*hi + 2*hi*lo + lo*lo,
; the cross term through mult_b_c, the rest from the squares table), IX += 2.
square_position_component:
    ld b,(ix+1)
    ld c,(ix+0)
    res 7,b
    push ix
    ld ix,0x0000
    call mult_b_c
    xor a
    ld d,a
    add hl,hl
    rl d
    ld e,h
    add ix,de
    ld h,l
    ld l,a
    push hl
    ld h,(SCREEN+0x600)>>8              ; high byte of the quarter-square table in the screen gap (a byte value, not an address: symbolize_screen cannot see it)
    ld l,b
    ld e,(hl)
    inc h
    ld d,(hl)
    dec h
    add ix,de
    ld l,c
    ld e,(hl)
    inc h
    ld d,(hl)
    pop hl
    add hl,de
    jr nc,LAB_ram_5266
    inc ix
LAB_ram_5266:
    ex (sp),ix
    pop hl
    inc ix
    inc ix
    ret
; ZX Spectrum: normalize_position_component (&9ECF)
; In: IX = an encoded position component, DE = the vector's length. Divides the magnitude by DE (div_hl_a_de), halves it, restores the sign,
; stores it back over the component and advances IX by 2: one step of normalising a vector.
normalize_position_component:
    ld h,(ix+1)
    ld l,(ix+0)
    push hl
    res 7,h
    call div_hl_a_de
    srl b
    rr c
    pop hl
    bit 7,h
    jr z,LAB_ram_5285
    set 7,b
LAB_ram_5285:
    ld (ix+0),c
    ld (ix+1),b
    inc ix
    inc ix
    ret
; ZX Spectrum: approx_sqrt_16bit (&9EF1)
; In: HL. Out: HL = &100 * sqrt(HL), i.e. 8.8 fixed point (H = integer part). Inputs below &1000 are scaled up first (by 2^4 or 2^8) so
; sqrt_approx_core always sees H >= &10, and the root is shifted back by 2 or 4 bits. Used to normalise vectors.
approx_sqrt_16bit:
    ld a,h
    cp 0x10
    jr nc,sqrt_approx_core
    and a
    jr z,sqrt_approx_rescale_256
    ld b,0x04
LAB_ram_529a:
    add hl,hl
    djnz LAB_ram_529a
    call sqrt_approx_core
    srl h
    rr l
    srl h
    rr l
    ret
; ZX Spectrum: sqrt_approx_rescale_256 (&9F0A)
; Input fits in one byte: treat L as the high byte (x256), take the root, shift the result right 4 times.
sqrt_approx_rescale_256:
    ld h,l
    ld l,a
    call sqrt_approx_core
    ld b,0x04
LAB_ram_52b0:
    srl h
    rr l
    djnz LAB_ram_52b0
    ret
; ZX Spectrum: sqrt_approx_core (&9F18)
; Newton's method, x' = (x + N*&10000/x) / 2, from the fixed guess DE = &8000: one rough opening pass and two full steps, good to about 2
; in the integer part for H >= &10. The divides go through div_hl_a_de, which already scales the quotient by &100.
sqrt_approx_core:
    xor a
    push hl
    push hl
    srl h
    rr l
    rra
    ld de,0x8000                        ; the constant &8000 (was the address of a label that sat there in the stock build)
    call SUB_ram_52d4
    pop de
    call SUB_ram_52ca
    pop de
; 16-bit helper: halves HL and DE, divides via div_hl_a_de and adds half the quotient (probably interpolation)
SUB_ram_52ca:
    rr h
    rr l
    ex de,hl
    srl h
    rr l
    rra
; Divide HL by A (div_hl_a_de), halve the quotient and return DE plus that in HL
SUB_ram_52d4:
    push de
    call div_hl_a_de
    srl b
    rr c
    xor a
    pop hl
    add hl,bc
    ret
; ZX Spectrum: tidy_vector (&9F41)
todoSomethingwithSine:
    ld h,(SCREEN+0x700)>>8
    ld l,(ix+1)
    sla l
    ld a,(hl)
    ld l,(ix+3)
    sla l
    add a,(hl)
    ld l,(ix+5)
    sla l
    add a,(hl)
    sra a
    sra a
    neg
    xor 0x80
    ld b,a
    call SUB_ram_5303
    call SUB_ram_5303
; Double the coordinate at IX+1, multiply via mult_b_c, store it with its sign and advance IX by 2 (probably)
SUB_ram_5303:
    ld c,(ix+1)
    sla c
    call mult_b_c
    sla h
    sla (ix+1)
    rr h
    ld (ix+1),h
    inc ix
    inc ix
    ret
Entityroll:
    db 0x00
Entitypitch:
    db 0x00
; Move the entity at IX (MVIT); if lined up near the origin rotate its orientation, else clear its flag
SUB_ram_531d:
    call MVIT
    bit 2,(ix+38)
    jr nz,LAB_ram_532b
    ld a,l
    cp 0x60
    jr nc,LAB_ram_5330
LAB_ram_532b:
    ld a,h
    and 0x7F
    jr z,LAB_ram_5337
LAB_ram_5330:
    xor a
    ld (ix+34),a
    jp chkEntityWasMissiletarget
LAB_ram_5337:
    ld a,(ix+2)
    and 0x7F
    jr nz,LAB_ram_5330
    ld a,(ix+5)
    and 0x7F
    jr nz,LAB_ram_5330
    ld hl,(inputRoll)
    ld (Entityroll),hl
    push ix
    ld de,0x0009
    add ix,de
    call rotate_orientation_vector
    call rotate_orientation_vector
    call rotate_orientation_vector
    pop ix
    ld a,(ix+29)
    ld b,a
    bit 7,a
    jr nz,LAB_ram_5370
    and 0x0F
    ld a,0x00
    jr z,LAB_ram_537a
    ld a,b
    dec a
    ld (ix+29),a
LAB_ram_5370:
    ld a,0x0C
    bit 6,(ix+29)
    jr z,LAB_ram_537a
    add a,0x80
LAB_ram_537a:
    ld (Entityroll),a
    ld a,(ix+30)
    ld b,a
    bit 7,a
    jr nz,LAB_ram_5390
    and 0x0F
    ld a,0x00
    jr z,applyRollandPitch
    ld a,b
    dec a
    ld (ix+30),a
LAB_ram_5390:
    ld a,0x08
    bit 6,(ix+30)
    jr z,applyRollandPitch
    add a,0x80
; Store A as the entity's pitch and rotate its orientation vectors by roll and pitch (probably)
applyRollandPitch:
    ld (Entitypitch),a
    push ix
    call calcMatrixBankingClimbing
    call calcMatrixBankingClimbing
    call calcMatrixBankingClimbing
    pop ix
    ld a,(ix+28)
    and a
    jr z,LAB_ram_53cf
    ld b,(ix+27)
    add a,b
    bit 7,a
    jr z,LAB_ram_53bb
    xor a
    jr LAB_ram_53cc
LAB_ram_53bb:
    ld c,(iy+6)
    bit 0,(ix+33)
    jr z,LAB_ram_53c8
    sla c
    sla c
LAB_ram_53c8:
    cp c
    jr c,LAB_ram_53cc
    ld a,c
LAB_ram_53cc:
    ld (ix+27),a
LAB_ram_53cf:
    push ix
    push iy
    ld c,(ix+27)
    push ix
    pop iy
    call move_ship_forward
    call move_ship_forward
    call move_ship_forward
    pop iy
    pop ix
    ret
; ZX Spectrum: move_ship_forward (&A04B)
; Called once per axis: position += speed (C) * the matching nosev component, i.e. the ship moves along its nose by its speed (the MVEIT step).
move_ship_forward:
    push bc
    ld d,(ix+10)
    ld e,(ix+9)
    call multiply_speed_nosev
    ld a,(iy+2)
    ld h,(iy+1)
    ld l,(iy+0)
    call todoCalcSpeedtoPositionX
    ld (iy+2),b
    ld (iy+1),h
    ld (iy+0),l
    inc iy
    inc iy
    inc iy
    inc ix
    inc ix
    pop bc
    ret
; ZX Spectrum: multiply_speed_nosev (&A076)
; DE = C * DE / 96 (roughly) by a 6-bit shift-and-add: the distance moved this frame along one axis. Out: C = sign.
multiply_speed_nosev:
    sla d
    rl c
    rl c
    srl d
    ld hl,0x0000
    ld b,0x06
LAB_ram_5420:
    srl d
    rr e
    sla c
    jr nc,LAB_ram_5429
    add hl,de
LAB_ram_5429:
    djnz LAB_ram_5420
    ld de,0x00FF
    add hl,de
    ld e,h
    sla c
    rr d
    ret
; Add a sign-magnitude product in DE to the position word at HL; inner part of move_ship_forward
todoCalcSpeedtoPositionX:
    ld b,a
    ld c,d
    xor c
    res 7,d
    jr nz,LAB_ram_543e
    add hl,de
    ret
LAB_ram_543e:
    sbc hl,de
    ret nc
    add hl,de
    ex de,hl
    and a
    sbc hl,de
    ld b,c
    ret
; ZX Spectrum: rotate_orientation_vector (&A0AB)
; Applies the small pitch and roll rotation to one orientation vector's own x, y and z high bytes. Out: IX advanced by 6 for the next vector.
rotate_orientation_vector:
    ld a,(Entitypitch)
    xor 0x80
    sra a
    res 6,a
    ld c,a
    ld b,(ix+3)
    ld d,(ix+5)
    call todoCalcAngle
    ld (ix+5),a
    ld a,(Entityroll)
    xor 0x80
    ld c,a
    ld b,(ix+3)
    ld d,(ix+1)
    call todoCalcAngle
    ld (ix+1),a
    ld a,(Entityroll)
    ld c,a
    ld b,(ix+1)
    ld d,(ix+3)
    call todoCalcAngle
    ld (ix+3),a
    ld a,(Entitypitch)
    sra a
    res 6,a
    ld c,a
    ld b,(ix+5)
    ld d,(ix+3)
    call todoCalcAngle
    ld (ix+3),a
    ld de,0x0006
    add ix,de
    ret
; ZX Spectrum: combine_vector_rotation_rate (&A0FD)
todoCalcAngle:
    push de
    xor b
    sla b
    res 7,c
    ld e,a
    call mult_b_c_msb
    pop bc
    ld c,a
    ld a,e
    xor b
    sla b
    rr e
    sla c
    rla
    ld a,b
    jr c,LAB_ram_54ba
    add a,c
    jp nc,LAB_ram_54c1
    ld a,0xFF
    jr LAB_ram_54c1
LAB_ram_54ba:
    sub c
    jr nc,LAB_ram_54c1
    neg
    rl e
LAB_ram_54c1:
    rl e
    rra
    ret
; ZX Spectrum: rotate_orientation_vectors (&A127)
; Per axis: applies pitch between nosev and roofv and roll between roofv and sidev (the BBC's MVEIT orientation step).
calcMatrixBankingClimbing:
    ld a,(Entitypitch)
    xor 0x80
    ld c,a
    ld b,(ix+16)
    ld d,(ix+10)
    call todoCalcAngle
    ld (ix+10),a
    ld a,(Entityroll)
    xor 0x80
    ld c,a
    ld b,(ix+16)
    ld d,(ix+22)
    call todoCalcAngle
    ld (ix+22),a
    ld a,(Entityroll)
    ld c,a
    ld b,(ix+22)
    ld d,(ix+16)
    call todoCalcAngle
    ld (ix+16),a
    ld a,(Entitypitch)
    ld c,a
    ld b,(ix+10)
    ld d,(ix+16)
    call todoCalcAngle
    ld (ix+16),a
    inc ix
    inc ix
    ret
; ZX Spectrum: rotate_and_step_ship (&A173)
; Moves a ship: rotates its position by the player's roll and pitch (extended-precision combine) and steps it forward along z. IX = ship record.
MVIT:
    ld a,(inputPitch)
    xor 0x80
    ld c,a
    ld de,0x0003
    ld hl,0x0006
    call SUB_ram_5583
    ld a,(inputRoll)
    xor 0x80
    call reshuffle_rate_bits
    ld de,0x0003
    ld h,d
    ld l,d
    call SUB_ram_5583
    ld a,(inputRoll)
    call reshuffle_rate_bits
    ld hl,0x0003
    ld d,h
    ld e,h
    call SUB_ram_5583
    ld a,(inputPitch)
    ld c,a
    ld hl,0x0003
    ld de,0x0006
    call SUB_ram_5583
    ld a,(movementspeed)
    inc a
    add a,a
    ld b,a
    ld h,(ix+8)
    ld l,(ix+7)
    ld a,(ix+6)
    bit 7,h
    jr z,LAB_ram_556a
    add a,b
    ld (ix+6),a
    ret nc
    inc hl
    bit 7,h
    jr nz,LAB_ram_557c
    ld hl,0x7FFF
    jr LAB_ram_5577
LAB_ram_556a:
    sub b
    ld (ix+6),a
    ret nc
    dec hl
    bit 7,h
    jr z,LAB_ram_557c
    ld hl,0x8000                        ; the constant &8000 (was the address of a label that sat there in the stock build)
LAB_ram_5577:
    neg
    ld (ix+6),a
LAB_ram_557c:
    ld (ix+8),h
    ld (ix+7),l
    ret
; Ship vertex projection helper, still a db blob (sign-magnitude scale and add of coordinates, probably)
SUB_ram_5583:
    push ix
    push ix
    ex (sp),iy
    add ix,de
    ex de,hl
    add iy,de
    ld a,(ix+2)
    ld d,(ix+1)
    ld e,(ix+0)
    ld b,a
    xor c
    and 0x80
    push af
    res 7,c
    res 7,b
    push de
    call mult_b_c
    pop de
    push hl
    ld b,d
    push de
    call mult_b_c
    pop de
    ld b,e
    ld a,l
    ld l,h
    ld h,0x00
    pop de
    add hl,de
    ld e,a
    push hl
    call mult_b_c_msb
    add a,e
    pop hl
    jr nc,LAB_ram_55bd
    inc hl
LAB_ram_55bd:
    ld b,a
    ld a,h
    ld h,l
    ld l,b
    pop bc
    ld c,b
    ld b,(iy+2)
    ld d,(iy+1)
    ld e,(iy+0)
    push af
    ld a,b
    xor c
    rlc c
    rlc c
    rla
    rr c
    rrc c
    srl a
    ld b,a
    pop af
    bit 6,c
    jr nz,LAB_ram_55eb
    add a,a
    sla c
    rra
    add a,b
    add hl,de
    jr nc,LAB_ram_560c
    inc a
    jr LAB_ram_560c
LAB_ram_55eb:
    and a
    ex de,hl
    sbc hl,de
    jr nc,LAB_ram_55f2
    inc a
LAB_ram_55f2:
    ld d,a
    ld a,b
    sub d
    ld b,a
    jr nc,LAB_ram_5605
    cpl
    ld b,a
    ld a,c
    xor 0x80
    ld c,a
    ex de,hl
    and a
    ld hl,0x0000
    sbc hl,de
LAB_ram_5605:
    ld a,b
    rla
    sla c
    rra
    xor 0x80
LAB_ram_560c:
    ld (iy+2),a
    ld (iy+1),h
    ld (iy+0),l
    pop iy
    pop ix
    ret
; ZX Spectrum: reshuffle_rate_bits (&A281)
; Rearranges the bits of a rate byte before it is combined in the extended-precision rotate: bit 0 becomes a copy of bit 6, bits 5-0 shift up one place.
reshuffle_rate_bits:
    ld c,a
    rl c
    rra
    rl c
    rla
    rr c
    ret
; ZX Spectrum: draw_title_ship (&A28D)
; Title screen: steps the demo ship's rotation and position one frame with fixed rates, tidies its orientation vectors and draws it.
drawIntroShip:
    ld ix,buf_1B51
    ld h,(ix+36)
    ld l,(ix+35)
    push hl
    pop iy
    ld a,0x94
    ld (Entityroll),a
    ld a,0x8C
    call applyRollandPitch
    call SUB_ram_5dcf
    ld ix,buf_1B5A
    call todoSomethingwithSine
    call todoSomethingwithSine
    ld ix,buf_1B51
    jp SUB_ram_564f
; For views 0-3, test a ship face normal against the view direction and return early if it is hidden (probably)
SUB_ram_564f:
    ld a,(Viewdirection)
    ld b,a
    cp 0x04
    ret nc
    push ix
    pop hl
    bit 1,a
    jr nz,LAB_ram_5661
    ld de,0x0006
    add hl,de
LAB_ram_5661:
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld c,(hl)
    srl a
    xor b
    rrca
    xor c
    and 0x80
    ret nz
    ld (varCoordinate),de
    ld h,0x00
    ld l,(iy+1)
    push hl
    and a
    sbc hl,de
    jr c,LAB_ram_567f
    pop hl
    ret
LAB_ram_567f:
    push de
    push de
    bit 1,b
    jr nz,LAB_ram_56aa
    ex de,hl
    ld d,(ix+1)
    ld e,(ix+0)
    xor a
    ld c,a
    call div_de_h
    ld a,c
    ld (pitchVal),a
    pop hl
    ld d,(ix+4)
    ld e,(ix+3)
    xor a
    ld c,a
    call div_de_h
    ld a,c
    ld (rollVal),a
    ld b,(ix+2)
    jr LAB_ram_56cd
LAB_ram_56aa:
    ex de,hl
    ld d,(ix+7)
    ld e,(ix+6)
    xor a
    ld c,a
    call div_de_h
    ld a,c
    ld (pitchVal),a
    pop hl
    ld d,(ix+4)
    ld e,(ix+3)
    xor a
    ld c,a
    call div_de_h
    ld a,c
    ld (rollVal),a
    ld b,(ix+8)
LAB_ram_56cd:
    ld a,(ix+5)
    sla b
    rla
    rla
    ld (BYTE_ram_5929),a
    pop hl
    pop de
    xor a
    ld c,a
    call div_de_h
    ld h,c
    ld a,c
    ld (distVal),a
    ld e,c
    ld a,(rollVal)
    ld c,a
    sub h
    jr c,LAB_ram_56f0
    sub 0x40
    jp nc,chkEntityFiresLaser
LAB_ram_56f0:
    ld a,(pitchVal)
    ld b,a
    sub h
    jr c,LAB_ram_56fc
    sub 0x80
    jp nc,chkEntityFiresLaser
LAB_ram_56fc:
    ld a,b
    add a,c
    ld d,a
    jr c,LAB_ram_5741
    sub e
    jr nc,LAB_ram_5712
    ld a,(ix+7)
    cp 0x2C
    jr nc,LAB_ram_5712
    pop hl
    pop af
    push af
    push hl
    ld (shipInCrosshair),a
LAB_ram_5712:
    bit 6,(ix+32)
    jr z,LAB_ram_5741
    bit 2,(ix+33)
    jr z,LAB_ram_5741
    ld a,(Viewdirection)
    bit 1,a
    ld a,(ix+14)
    ld e,(ix+7)
    jr z,LAB_ram_5731
    ld a,(ix+10)
    ld e,(ix+1)
LAB_ram_5731:
    ld b,a
    and 0x7F
    cp 0x40
    jr c,LAB_ram_5741
    ld a,d
    cp 0x20
    jr nc,LAB_ram_5741
    res 5,(ix+38)
LAB_ram_5741:
    bit 4,(ix+32)
    jp nz,cache_explosion_screen_pos
; ZX Spectrum: &A7D9. While the state is exactly 1 and this is the marked Asp (bit 6 of (ix+38)), draw only its laser, not the wireframe.
    ld a,(aspMissionState)
    dec a
    jr nz,drawShipDistanceCheck
    bit 6,(ix+38)
    jp nz,chkEntityFiresLaser
; ZX Spectrum: &A7E6. Normal path: compare the distance high byte with blueprint byte +11 (visibility distance).
drawShipDistanceCheck:
    ld hl,(varCoordinate)
    ld a,h
    cp (iy+11)
    jr c,LAB_ram_57bc
    ld a,(pitchVal)
    cp 0x7F
    jp nc,chkEntityFiresLaser
    ld c,a
    ld a,(rollVal)
    cp 0x3F
    jp nc,chkEntityFiresLaser
    ld b,a
    ld a,(Viewdirection)
    bit 0,a
    ld a,(BYTE_ram_5929)
    jr z,LAB_ram_577c
    xor 0x02
LAB_ram_577c:
    ld d,a
    bit 1,d
    jr nz,LAB_ram_5787
    ld a,c
    add a,0x7F
    ld c,a
    jr LAB_ram_578b
LAB_ram_5787:
    ld a,0x7F
    sub c
    ld c,a
LAB_ram_578b:
    bit 0,d
    jr z,drawShippixels
    ld a,b
    add a,0x3F
    ld b,a
    jr LAB_ram_5799
drawShippixels:
    ld a,0x3F
    sub b
    ld b,a
LAB_ram_5799:
    call putshippixelstoBM
    inc b
    call putshippixelstoBM
    inc c
    call putshippixelstoBM
    dec b
    call putshippixelstoBM
    jp chkEntityFiresLaser
; OR one mode 1 pixel at (C,B) into the game bitmap; preserves BC
putshippixelstoBM:
    push bc
    call getByteAddressinBitmap
    inc a
    ld c,0x88
LAB_ram_57b2:
    rlc c
    dec a
    jr nz,LAB_ram_57b2
    ld a,(hl)
    or c
    ld (hl),a
    pop bc
    ret
LAB_ram_57bc:
    push iy
    call SUB_ram_761a
    pop iy
    ld hl,(varCoordinate)
    add hl,hl
    ld b,0x1F
    jr c,LAB_ram_57d0
    ld a,h
    cp b
    jr nc,LAB_ram_57d0
    ld b,h
LAB_ram_57d0:
    jp hullDeferEntry                   ; 128K build: queue the hull (far to near order), else ld a,b / sub 0x02 and carry on below
hullDrawResume:
    jr nc,LAB_ram_57d6
    xor a
LAB_ram_57d6:
    ld (varCoordinate),a
    ld a,0xFD
    ld (todoCounterNextVertice),a
    call parseFaces
    call todo_parseVertices
    call hullDraw                       ; 128K build: filled hull (falls back to todo_parseEdges)
    bit 3,(ix+32)
    ret z
    ld a,(iy+20)
    call lookup_vertex_coords
    ld c,a
drawEnemyLaser:
    call getRandomNumber
    ld l,a
    sub 0xFF
    neg
    ld h,a
    ld a,c
    cpl
    and 0x03
    sla c
    sla c
    or c
    ld c,a
    push af
    set 7,a
    call drawLaserLine
    pop af
    res 3,(ix+32)
    ret
; ZX Spectrum: cache_explosion_screen_pos (&A8AC)
cache_explosion_screen_pos:
    ld a,(pitchVal)
    ld (ix+28),a
    ld a,(rollVal)
    ld (ix+29),a
    ld a,(distVal)
    ld (ix+31),a
    ld a,(Viewdirection)
    bit 0,a
    ld a,(BYTE_ram_5929)
    jr z,LAB_ram_5830
    xor 0x02
LAB_ram_5830:
    ld c,a
    xor a
    rr c
    rla
    rr c
    rla
    xor 0x03
    add a,0x0C
    ld (ix+30),a
    set 5,(ix+32)
    ret
; ZX Spectrum: draw_laser_only (&A8DE)
; Reached from the early exits of the draw routine (ship off screen or too far to draw): if the ship should fire, draws its laser from the last
; projected coordinates, so laser fire stays visible when the ship itself is not drawn.
chkEntityFiresLaser:
    bit 3,(ix+32)
    ret z
    ld a,(pitchVal)
    ld d,a
    ld a,(rollVal)
    ld e,a
    ld a,(Viewdirection)
    bit 0,a
    ld a,(BYTE_ram_5929)
    jr z,loc_585D
    xor 0x02
loc_585D:
    ld c,a
    jr drawEnemyLaser
buf_5860:
    jr nz,loc_5869
    bit 6,(ix+38)
    jp nz,loc_5958
loc_5869:
    ld hl,(LAB_ram_5a31+1)
    ld a,h
    cp (iy+11)
    jr c,loc_58D0
    ld a,(LAB_ram_5a3a+1)
    cp 0x7F
    jp nc,loc_5958
    ld c,a
    ld a,(LAB_ram_5a3c)
    cp 0x3F
    jp nc,loc_5958
    ld b,a
    ld a,(Viewdirection)
    bit 0,a
    ld a,(LAB_ram_5a3c+1)
    jr z,loc_5890
    xor 0x02
loc_5890:
    ld d,a
    bit 1,d
    jr nz,loc_589B
    ld a,c
    add a,0x7F
    ld c,a
    jr loc_589F
loc_589B:
    ld a,0x7F
    sub c
    ld c,a
loc_589F:
    bit 0,d
    jr z,loc_58A9
    ld a,b
    add a,0x3F
    ld b,a
    jr loc_58AD
loc_58A9:
    ld a,0x3F
    sub b
    ld b,a
loc_58AD:
    call sub_58BF
    inc b
    call sub_58BF
    inc c
    call sub_58BF
    dec b
    call sub_58BF
    jp loc_5958
; Copy of putshippixelstoBM: OR one pixel at (C,B) into the bitmap; its call target is a raw db operand
sub_58BF:
    push bc
    call LAB_ram_6798+1                 ; into the operand of the call at LAB_ram_6798 (as in the stock build)
    inc a
    ld c,0x88
loc_58C6:
    rlc c
    dec a
    jr nz,loc_58C6
    ld a,(hl)
    or c
    ld (hl),a
    pop bc
    ret
loc_58D0:
    db 0xFD,0xE5,0xCD,"aw",0xFD,0xE1,"*2Z)",0x06,0x1F,"8",0x05,"|"
    db 0xB8,"0",0x01,"Dx",0xD6,0x02,"0",0x01,0xAF
todo_tableforedges:
    db 0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01
tableUnkownFacedata:
    db "~2",0x81,0x8D,0xF3,"$",0x81,0x8D,"~2",0xF3,"$",0xF2,0xA4,0xF2,0xA4
    db 0xF3,"$",0xFF,0xED,"Dgy/",0xE6,0x03,0xCB,"!",0xCB,"!",0xB1,"O"
    db 0xF5,0xCB,0xFF,0xCD
varCoordinate:
    db 0x00,0x00
todoCounterNextVertice:
    db 0x01
edgeVecX:
    db 0x00,0x00
edgeVecY:
    db 0x00,0x00
edgeVecZ:
    db 0x00,0x00
pitchVal:
    db 0x00
rollVal:
    db 0x00
BYTE_ram_5929:
    db 0x00
BYTE_ram_592a:
    db 0x00
BYTE_ram_592b:
    db 0x00
BYTE_ram_592c:
    db 0x00
BYTE_ram_592d:
    db 0x00
BYTE_ram_592e:
    db 0x00
; Walk the ship's vertex list and test each vertex against the visible-face table (probably)
todo_parseVertices:
    push iy
    push iy
    ld a,(iy+3)
    ex (sp),ix
    ld d,(iy+13)
    ld e,(iy+12)
    add ix,de
    ld iy,tableUnkownFacedata
pvLoop:
    push af
    ld a,(todoCounterNextVertice)
    add a,0x03
    ld (todoCounterNextVertice),a
    ld a,(ix+3)
    and 0x1F
    cp 0x1F
    jr z,LAB_ram_595d
    ld b,a
mi_5957:
    ld a,(varCoordinate)
    cp b
    jr nc,LAB_ram_596e
LAB_ram_595d:
    ld a,(ix+4)
    call getEntryfromTable
    jr nz,LAB_ram_596b
    ld a,(ix+5)
    call getEntryfromTable
LAB_ram_596b:
    jp nz,LAB_ram_5c09
LAB_ram_596e:
    inc a
    ld (BYTE_ram_592e),a
    pop af
    jp todoNextVertice
; ZX Spectrum: check_face_visible (&AA10)
; A = the two face numbers of an edge (bits 0-3 and 4-7). Zero flag clear if either face is visible according to the face visibility table.
getEntryfromTable:
    ld b,a
    srl b
    srl b
    srl b
    srl b
    and 0x0F
    call SUB_ram_5986
    ret nz
    ld a,b
; Look up entry A in todo_tableforedges; return it in A with Z set if it is zero
SUB_ram_5986:
    ld hl,todo_tableforedges
    add a,l
    ld l,a
    jr nc,LAB_ram_598e
    inc h
LAB_ram_598e:
    ld a,(hl)
    and a
    ret
; ZX Spectrum: rotate_vertex_axis (&AA2B)
; In: IX = a vertex (magnitudes at +0..+2, signs at +3), IY = the ship calculation table. Out: HL = one coordinate of the vertex rotated into the ship's
; orientation (x*sidev + y*roofv + z*nosev for this axis), IY += 6. If the vertex has the same magnitudes as the previous one (the cache is valid)
; the cached products are reused (rotate_vertex_axis_cached); otherwise LAB_ram_59f2 recomputes the three products with mult_b_coord_scaled.
rotate_vertex_axis:
    ld a,(BYTE_ram_592e)
    and a
    jr nz,LAB_ram_59f2
    ld a,(ix+0)
    cp (ix-6)
    jr nz,LAB_ram_59f2
    ld a,(ix+1)
    cp (ix-5)
    jr nz,LAB_ram_59f2
    ld a,(ix+2)
    cp (ix-4)
    jr nz,LAB_ram_59f2
    ld a,(ix+3)
    xor (ix-3)
    ld b,a
    ld l,(iy+18)
    ld h,(iy+19)
    ld e,(iy+20)
    ld d,(iy+21)
    xor h
    and 0x80
    ld h,a
    ld (iy+19),h
    rl b
    ld a,b
    xor d
    and 0x80
    ld d,a
    ld (iy+21),d
    call add_sign_mag_bytes
    ld l,a
    ld e,(iy+22)
    ld d,(iy+23)
    ld a,b
    rla
    xor d
    and 0x80
    ld d,a
    ld (iy+23),d
    call add_sign_mag_bytes
    ld l,a
    ld de,0x0006
    add iy,de
    jp LAB_ram_5a4a
LAB_ram_59f2:
    ld b,(ix+0)
    call mult_b_coord_scaled
    ld a,(ix+3)
    xor (iy+1)
    rla
    rr h
    ld (iy+18),l
    ld (iy+19),h
    ex de,hl
    inc iy
    inc iy
    ld b,(ix+1)
    call mult_b_coord_scaled
    ld a,(ix+3)
    rla
    xor (iy+1)
    rla
    rr h
    ld (iy+18),l
    ld (iy+19),h
    call add_sign_mag_bytes
    ld l,a
    ex de,hl
    inc iy
    inc iy
    ld b,(ix+2)
    call mult_b_coord_scaled
LAB_ram_5a31:
    ld a,(ix+3)
    rla
    rla
    xor (iy+1)
    rla
LAB_ram_5a3a:
    rr h
LAB_ram_5a3c:
    ld (iy+18),l
    ld (iy+19),h
    call add_sign_mag_bytes
    ld l,a
    inc iy
    inc iy
LAB_ram_5a4a:
    ld a,(BYTE_ram_592d)
    ld b,a
    xor a
    ld c,h
    res 7,h
LAB_ram_5a52:
    srl h
    rr l
    rra
    djnz LAB_ram_5a52
    jr nc,LAB_ram_5a5c
    inc hl
LAB_ram_5a5c:
    bit 7,c
    ret z
    set 7,h
    ret
; ZX Spectrum: add_sign_mag_bytes (&AAFB)
; In: H, L = sign and magnitude of the first number, D, E = sign and magnitude of the second. Out: H = sign, A = magnitude of the sum.
add_sign_mag_bytes:
    ld a,h
    xor d
    rla
    jr c,LAB_ram_5a6a
    ld a,l
    add a,e
    ret
LAB_ram_5a6a:
    ld a,l
    sub e
    ret nc
    neg
    and a
    ld h,d
    ret
; ZX Spectrum: mult_b_c_msb (&AB0B)
; In: B, C. Out: A = high byte of B*C (may be 1 off). Same x*x - y*y trick as mult_b_c, using only the high-byte page &C700 of the table.
mult_b_c_msb:
    ld a,b
    sub c
    jr nc,LAB_ram_5a78
    neg
LAB_ram_5a78:
    srl a
    ld h,(SCREEN+0x700)>>8
    ld l,a
    ld d,(hl)
    ld a,b
    add a,c
    rra
    ld l,a
    ld a,(hl)
    sub d
    ret
; ZX Spectrum: mult_b_coord_scaled (&AB1E)
; In: B = a vertex coordinate magnitude, IY = the ship's calculation table (IY+1 = an orientation byte). Out: HL = high byte of
; (B << n) * |orientation byte|. n is the shift count held in BYTE_ram_592d, chosen elsewhere to keep the most precision; the caller shifts the result back.
mult_b_coord_scaled:
    ld a,(BYTE_ram_592d)
LAB_ram_5a88:
    sla b
    dec a
    jr nz,LAB_ram_5a88
    ld c,(iy+1)
    res 7,c
    push de
    call mult_b_c_msb
    ld l,a
    ld h,0x00
    pop de
    ret
; ZX Spectrum: mult_b_c (&AB34)
; In: B, C. Out: HL = B*C, with no multiply instruction. With x = (B+C)/2 and y = |B-C|/2 we have B*C = x*x - y*y, and both
; squares come from the table (&C600/&C700). The halving truncates, so the result is 1 low when B+C is odd.
mult_b_c:
    ld a,b
    sub c
    jr nc,LAB_ram_5aa1
    neg
LAB_ram_5aa1:
    srl a
    ld h,(SCREEN+0x600)>>8              ; high byte of the quarter-square table in the screen gap (a byte value, not an address: symbolize_screen cannot see it)
    ld l,a
    ld e,(hl)
    inc h
    ld d,(hl)
    dec h
    ld a,b
    add a,c
    rra
    ld l,a
    ld a,(hl)
    inc h
    ld h,(hl)
    ld l,a
    and a
    sbc hl,de
    ret
; Add the doubled sign-magnitude value in DE to HL, with the signs in B and C (probably)
SUB_ram_5ab6:
    ld c,d
    rl e
    rl d
    ld a,b
    xor c
    jr nz,LAB_ram_5ac2
    add hl,de
    ld a,b
    ret
LAB_ram_5ac2:
    sbc hl,de
    jr nc,LAB_ram_5acd
    add hl,de
    ex de,hl
    and a
    sbc hl,de
    ld a,c
    ret
LAB_ram_5acd:
    ld a,h
    or l
    ld a,c
    ret z
    pop de
    pop af
    neg
    push af
    push de
    dec hl
    ld a,b
    ret
LAB_ram_5ada:
    ld a,(BYTE_ram_592e)
    and a
    push ix
    jr nz,LAB_ram_5b06
    ld b,0x03
LAB_ram_5ae4:
    ld a,(ix+0)
    cp (ix-6)
    jr nz,LAB_ram_5b06
    inc ix
    djnz LAB_ram_5ae4
    pop ix
    call rotate_vertex_axis_cached
    ld (edgeVecX),hl
    call rotate_vertex_axis_cached
    ld (edgeVecY),hl
    call rotate_vertex_axis_cached
    ld (edgeVecZ),hl
    jr LAB_ram_5b1a
LAB_ram_5b06:
    pop ix
    call face_normal_component
    ld (edgeVecX),hl
    call face_normal_component
    ld (edgeVecY),hl
    call face_normal_component
    ld (edgeVecZ),hl
LAB_ram_5b1a:
    xor a
    ld (BYTE_ram_5c06),a
    ld (BYTE_ram_5c07),a
    ld (BYTE_ram_5c08),a
    jp LAB_ram_5c45
; ZX Spectrum: rotate_vertex_axis_cached (&ABC0)
; Rotates one vertex coordinate into the ship's orientation when the vertex has the same magnitudes as the previous one (mirrored points): reuses
; the three products cached at IY and only flips the sign of each whose axis sign changed. Out: HL = coordinate, IY += 6.
rotate_vertex_axis_cached:
    ld a,(ix+3)
    xor (ix-3)
    ld b,a
    ld l,(iy+18)
    ld h,(iy+19)
    ld e,(iy+20)
    ld d,(iy+21)
    xor h
    and 0x80
    ld h,a
    ld (iy+19),h
    rl b
    ld a,b
    xor d
    and 0x80
    ld d,a
    ld (iy+21),d
    call add_sign_mag_bytes
    ld l,a
    ld e,(iy+22)
    ld d,(iy+23)
    ld a,b
    rla
    xor d
    and 0x80
    ld d,a
    ld (iy+23),d
    call add_sign_mag_bytes
    ld l,a
    ld de,0x0006
    add iy,de
    ret
; ZX Spectrum: face_normal_component (&AC01)
; In: IX = a face's normal, IY = ship calculation table (offset 0, 6 or 12 for x, y, z). Out: HL = normal_x*sidev + normal_y*roofv +
; normal_z*nosev (the matching component, sign-magnitude), IY += 6.
face_normal_component:
    ld b,(ix+0)
    ld c,(iy+1)
    res 7,c
    call mult_b_c_msb
    ld l,a
    ld a,(ix+3)
    xor (iy+1)
    and 0x80
    ld h,a
    ld (iy+18),l
    ld (iy+19),h
    ex de,hl
    ld b,(ix+1)
    ld c,(iy+3)
    res 7,c
    push de
    call mult_b_c_msb
    pop de
    ld l,a
    ld a,(ix+3)
    rla
    xor (iy+3)
    and 0x80
    ld h,a
    ld (iy+20),l
    ld (iy+21),h
    call add_sign_mag_bytes
    ld l,a
    ex de,hl
    ld b,(ix+2)
    ld c,(iy+5)
    res 7,c
    push de
    call mult_b_c_msb
    pop de
    ld l,a
    ld a,(ix+3)
    rla
    rla
    xor (iy+5)
    and 0x80
    ld h,a
    ld (iy+22),l
    ld (iy+23),h
    call add_sign_mag_bytes
    ld l,a
    ld de,0x0006
    add iy,de
    ret
; ZX Spectrum: div_de_h (&AC69)
; Divides DE:C by HL:A into an 8-bit fraction in C (saturating at &FF once the dividend reaches the divisor). A and C extend the divisor and
; dividend by one low byte each for precision. The divisor is first shifted left until HL's top bit is set (DE:C shifts the same amount),
; then a plain restoring division produces the quotient.
div_de_h:
    ld b,0x09
LAB_ram_5bd2:
    dec b
    jr z,LAB_ram_5beb
    rla
    adc hl,hl
    jr c,LAB_ram_5be7
    rl c
    rl e
    rl d
    jr nc,LAB_ram_5bd2
    rr d
    rr e
    scf
LAB_ram_5be7:
    rr h
    rr l
LAB_ram_5beb:
    ld a,d
    ld c,0xFF
    cp h
    ret nc
    ld b,h
    dec c
; Long-division loop: shifts E into A and builds quotient bits in C for A divided by B
SUB_ram_5bf2:
    sla e
    rla
    jr c,LAB_ram_5bff
    cp b
    jr nc,LAB_ram_5bff
    sla c
    ret nc
    jr SUB_ram_5bf2
LAB_ram_5bff:
    sub b
    scf
    rl c
    ret nc
    jr SUB_ram_5bf2
BYTE_ram_5c06:
    db 0x00
BYTE_ram_5c07:
    db 0x00
BYTE_ram_5c08:
    db 0x00
LAB_ram_5c09:
    push iy
    ld a,(varCoordinate)
    cp 0x04
    jp nc,LAB_ram_5ada
    ld a,(ix+0)
    or (ix+1)
    or (ix+2)
    ld b,0xFF
LAB_ram_5c1e:
    inc b
    add a,a
    jr nc,LAB_ram_5c1e
    ld a,b
    ld (BYTE_ram_592d),a
    and a
    jp z,LAB_ram_5ada
    call rotate_vertex_axis
    ld (BYTE_ram_5c06),a
    ld (edgeVecX),hl
    call rotate_vertex_axis
    ld (BYTE_ram_5c07),a
    ld (edgeVecY),hl
    call rotate_vertex_axis
    ld (BYTE_ram_5c08),a
    ld (edgeVecZ),hl
LAB_ram_5c45:
    xor a
    ld (BYTE_ram_592e),a
    pop iy
    pop hl
    ex (sp),ix
    push hl
    ld l,(ix+0)
    ld h,(ix+1)
    ld b,(ix+2)
    ld de,(edgeVecX)
    ld a,(BYTE_ram_5c06)
    rla
    push af
    call SUB_ram_5ab6
    ld (edgeVecX),hl
    ld (BYTE_ram_592a),a
    pop af
    ld (BYTE_ram_5c06),a
    ld l,(ix+3)
    ld h,(ix+4)
    ld b,(ix+5)
    ld de,(edgeVecY)
    ld a,(BYTE_ram_5c07)
    rla
    push af
    call SUB_ram_5ab6
    ld (edgeVecY),hl
    ld (BYTE_ram_592b),a
    pop af
    ld (BYTE_ram_5c07),a
    ld l,(ix+6)
    ld h,(ix+7)
    ld b,(ix+8)
    ld de,(edgeVecZ)
    ld a,(BYTE_ram_5c08)
    rla
    push af
    call SUB_ram_5ab6
    ld (edgeVecZ),hl
    ld (BYTE_ram_592c),a
    pop af
    ld (BYTE_ram_5c08),a
    ld a,(Viewdirection)
    bit 1,a
    jr nz,LAB_ram_5ce8
    ld de,(edgeVecX)
    ld a,(BYTE_ram_5c06)
    ld c,a
    ld a,(BYTE_ram_5c08)
    call div_de_h
    ld a,c
    ld (pitchVal),a
    ld de,(edgeVecY)
    ld hl,(edgeVecZ)
    ld a,(BYTE_ram_5c07)
    ld c,a
    ld a,(BYTE_ram_5c08)
    call div_de_h
    ld a,c
    ld (rollVal),a
    ld a,(BYTE_ram_592a)
    rla
    rl c
    ld a,(BYTE_ram_592c)
    rla
    rl b
    jr LAB_ram_5d1b
LAB_ram_5ce8:
    ex de,hl
    ld hl,(edgeVecX)
    ld a,(BYTE_ram_5c08)
    ld c,a
    ld a,(BYTE_ram_5c06)
    call div_de_h
    ld a,c
    ld (pitchVal),a
    ld de,(edgeVecY)
    ld hl,(edgeVecX)
    ld a,(BYTE_ram_5c07)
    ld c,a
    ld a,(BYTE_ram_5c06)
    call div_de_h
    ld a,c
    ld (rollVal),a
    ld a,(BYTE_ram_592a)
    rla
    rl b
    ld a,(BYTE_ram_592c)
    rla
    rl c
LAB_ram_5d1b:
    ld a,(BYTE_ram_592b)
    rla
    rl c
    ld a,(Viewdirection)
    bit 0,a
    ld a,c
    jr z,LAB_ram_5d2b
    xor 0x02
LAB_ram_5d2b:
    and 0x03
    ld (BYTE_ram_5929),a
    ld a,(todoCounterNextVertice)
    ld hl,buf_5860
    add a,l
    jr nc,LAB_ram_5d3a
    inc h
LAB_ram_5d3a:
    ld l,a
    ld a,(pitchVal)
    ld (hl),a
    inc hl
    ld a,(rollVal)
    ld (hl),a
    inc hl
    ld a,(Viewdirection)
    ld c,a
    rra
    xor c
    xor b
    rra
    ld a,(BYTE_ram_5929)
    jr nc,LAB_ram_5d54
    ld a,0xFF
LAB_ram_5d54:
    ld (hl),a
    pop af
    ex (sp),ix
todoNextVertice:
    ld bc,0x0006
    add ix,bc
    inc de
    dec a
    jp nz,pvLoop
    pop ix
    pop iy
    ret
; Walk the ship's edge list and draw each edge whose face and end vertices are visible (probably)
todo_parseEdges:
    ld e,(iy+14)
    ld d,(iy+15)
    ld b,(iy+4)
    push iy
    ex (sp),ix
    add ix,de
edgeParseLoop:
    push bc
    ld a,(ix+0)
    cp 0x1F
    jr z,parseVisibleEdges
    ld c,a
    ld a,(varCoordinate)
    cp c
    jr nc,todo_getNextEdge
parseVisibleEdges:
    ld a,(ix+3)
    call getEntryfromTable
    jr z,todo_getNextEdge
    ld a,(ix+1)
    call lookup_vertex_coords
    jr nz,todo_getNextEdge
    ld c,a
    push de
    ld a,(ix+2)
    call lookup_vertex_coords
    ex de,hl
    pop de
    jr nz,todo_getNextEdge
    rrca
    rra
    rl c
    rla
    rl c
    call SUB_ram_7c45
todo_getNextEdge:
    pop bc
    ld de,0x0004
    add ix,de
    djnz edgeParseLoop
    pop ix
    ret
; ZX Spectrum: lookup_vertex_coords (&AE50)
; A = vertex number: finds its coordinates in the ship's vertex data.
lookup_vertex_coords:
    ld b,a
    add a,a
    ld hl,buf_5860
    jr nc,LAB_ram_5dbe
    inc h
LAB_ram_5dbe:
    add a,b
    jr nc,LAB_ram_5dc2
    inc h
LAB_ram_5dc2:
    add a,l
    ld l,a
    jr nc,LAB_ram_5dc7
    inc h
LAB_ram_5dc7:
    ld d,(hl)
    inc hl
    ld e,(hl)
    inc hl
    ld a,(hl)
    bit 7,a
    ret
; Re-orthogonalise the ship orientation by running add_scaled_nosev_to_roofv on three components (probably)
SUB_ram_5dcf:
    push ix
    push ix
    ex (sp),iy
    ld de,0x0009
    add ix,de
    ld e,0x0F
    add iy,de
    call dot_product_scale_factor
    ld e,a
    call add_scaled_nosev_to_roofv
    call add_scaled_nosev_to_roofv
    call add_scaled_nosev_to_roofv
    pop iy
    pop ix
    ret
; roofv += E * nosev for one component (a sign-magnitude multiply-and-add through mult_b_c_msb, saturating at &FF), stored back at (IY+1).
; In: IX = nosev component, IY = roofv component, E = scale. Advances IY by 2. Part of keeping the orientation vectors perpendicular.
add_scaled_nosev_to_roofv:
    ld c,(ix+1)
    ld b,e
    sla b
    sla c
    call mult_b_c_msb
    ld c,a
    ld a,e
    xor (ix+1)
    rla
    rr c
    ld b,(iy+1)
    ld a,b
    xor c
    sla c
    rl h
    sla b
    rl h
    rla
    ld a,b
    jr c,LAB_ram_5e1b
    add a,c
    jr nc,LAB_ram_5e22
    ld a,0xFF
    jr LAB_ram_5e22
LAB_ram_5e1b:
    sub c
    jr nc,LAB_ram_5e22
    neg
    rr h
LAB_ram_5e22:
    rr h
    rra
    ld (iy+1),a
    inc ix
    inc ix
    inc iy
    inc iy
    ret
; Pattern data for the scanner background: cleanScanner reads it a nibble at a time and draws it into the screen area at &C492.
gfxdataScanner:
    db 0x01,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xDF,0xFF,0xF7,0xFF
    db 0xF7,0xFD,0xFF,0xFF,0xFF,0xBF,0xEF,0xFF,0xEF,0xF7,0x7F,0xFF,0xF7,0xFF,0xFF,0xFD
    db 0xFF,0xBF,0xFF,0xFF,0xEF,0xFF,0xFE,0xFF,0xF7,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0xEF,0xFF,0xFE,0x7F,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFE
    db 0x7F,0xFF,0xFF,0xFF,0xF0,0x7F,0xFF,0xFF,0xFF,0xFE,0x0F,0xFF,0xFF,0xFF,0x01,0xFF
    db 0xFF,0xFF,0xFF,0xAA,0xAA,0xAA,0xFF,0xFF,0xFF,0xFF,0xDF,0xFF,0xDF,0xFF,0xFF,0xFE
    db 0xFF,0xFF,0xFF,0x7F,0xFF,0xFF,0xFB,0xFB,0xFF,0xFF,0xFF,0xFF,0xFF,0xFE,0xFF,0x7F
    db 0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xF7,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0xFF,0x9F,0xFF,0xFF,0xFF,0xFF,0xF7,0xFF,0xFF,0xFF,0xFF,0xF9,0xFF,0xFF
    db 0xFF,0xFF,0xFF,0x80,0x7F,0xF7,0xFE,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0xFF,0xFF,0xFF
    db 0xEA,0xFF,0xFF,0xFF,0xAB,0xFF,0xFF,0xFF,0xDF,0xFF,0x7F,0xFF,0xDF,0xFF,0x7F,0xFF
    db 0xFE,0xFF,0xFB,0xFF,0xFE,0xFD,0xFF,0xFF,0xDF,0xFF,0xFF,0xFF,"~",0xFF,0xFF,0xFF
    db 0xFB,0xFF,0xFF,0x7F,0xDF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFB,0xFE
    db 0xFF,0xE7,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xE7,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0x80,0x00,0x01,0xFF,0xFF,0xFF,0xFF,0xFF,0x03,0xFF,0xFF,0xFA,"?",0xFF
    db 0xFF,0xFF,0xFE,"_",0xFF,0xFF,0xDF,0xFD,0xDD,0xDD,0xFB,0xBB,0xBF,0xFF,0xFD,0xDD
    db 0xDF,0xBB,0xBB,0xBE,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xBD,0xFF,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xBF,0xFF,0xFF,0xFF,0xFF,0xFF,0xEF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFD,0xFF,0xF9
    db 0xFF,0xFF,0xFF,0xFF
    db 0xEF,0xFF,0xFF,0xFF,0xFF,0x9F,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0xFF,0xFF,0x03,0xFF,0xFF,0x0F,"_",0xFF,0xFF,0xFF,0xFA,0xF0,0xFF,0xFF
    db 0xDF,0xF7,0xFF,0xFF,0x7F,0xFF,0xDF,0xFF,0xFB,0xFF,0xFE,0xFF,0xFF,0xEF,0xFF,0xFF
    db 0x7F,0xFF,0xFF,0xFF,0xDB,0xFF,0xFF,0xFF,0xFE,0xFF,0xFF,0xDF,0x7F,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFE,0xFB,0xFF,0xFE,"?",0xFF,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0xFC,0x7F,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0x07,0xFF,0xF1,0xFF,0xEF,0xFF,0xFF,0xFF,0xF7,0xFF,0x8F,0xFF,0xDF,0xFF
    db 0xFF,0xFF,0xFF,0xFF,0xEF,0xFF,0xF7,0xFF,0xFF,0xFF,0xFF,0xFF,0xEE,0xEF,0xEE,0xEE
    db 0xEE,0xEE,0xE7,"wwww",0xEE,0xEE,0xEF,0xFF,0xFF,0xFF,0xFF,0xFF,0xF7
    db 0xFF,0xFF,0xFF,0xFF,0xFF,0xF7,0xFF,0xFF,0xC7,0xFF,0xFF,0xFF,0xF7,0xFF,0xFF,0xFF
    db 0xE3,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF
    db 0x0F,0xFF,0x9F,0xFD,0xF7,0xFF,0xFF,0xFF,0xEF,0xBF,0xF9,0xFF,0xEF,0xDF,0xFF,0xFD
    db 0xFF,0xFF,0xF7,0xFF,0xEF,0xFF,0xFF,0xBF,0xFF,0xFB,0xFF,0xFD,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0xFF,0xFF,0xFF,0xBF,0xFF,0xF5,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xFF,0xFF,0xAF,0xFF,0xFF,0xF8,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x1F,0xFF
    db 0xFF,0xFF,0xFF,0xFF,0xFF
loc_604A:
    rst 0x38
    rst 0x38
    rst 0x38
    rst 0x38
    rst 0x38
    rst 0x38
    rst 0x38
    rst 0x38
    rst 0x38
    ccf
    call m,0xFFFF
    ei
    rst 0x38
    rst 0x38
    rst 0x38
    rst 0x18
    db 0xFF,0xFF
    ccf
    rst 0x28
    db 0xFF,0xFF
    db 0xFF,0xFF,0xFF,0xFB,0xFF,0xDF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF
    db 0xFF,0xEF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xF9,"wwwwwn",0xEE
    db 0xEE,0xEE,0xEE,0xEE,0x9F,0xFF,0xFF,0xFF,0x0F,0xFF,0xFF,0xEF,0xFF,0xFF,0xF0,0xFF
    db 0xFF,0xFF,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
; Redraw each of the 11 dashboard indicator bars whose value changed since the last frame
UpdateIndicatorBars:
    ld de,tableScreenAdressesofIndicatorbars
    exx
    ld c,0x0B
    exx
    ld hl,shipFrontShieldEnergy
uib1:
    ld a,(hl)
    dec hl
    cp (hl)
    jr z,uib2
    ld (hl),a
    srl a
    srl a
    push hl
    push de
    call DrawIndicatorBars
    pop de
    pop hl
uib2:
    inc de
    inc de
    inc hl
    inc hl
    inc hl
    exx
    dec c
    exx
    jr nz,uib1
    ld a,0x01
    ld (todoIndBarValue),a
    exx
    ld c,0x02
    exx
uib3:
    ld a,(hl)
    dec hl
    cp (hl)
    jr z,uib4
    ld (hl),a
    push hl
    push de
    call DrawIndicatorBars
    pop de
    pop hl
uib4:
    inc de
    inc de
    inc hl
    inc hl
    inc hl
    exx
    dec c
    exx
    jr nz,uib3
    xor a
    ld (todoIndBarValue),a
    ret
todoIndBarValue:
    db 0x00
tableScreenAdressesofIndicatorbars:
    dw SCREEN+0x0C46,SCREEN+0x0C86,SCREEN+0x0CC6,SCREEN+0x0D06,SCREEN+0x0D46,SCREEN+0x0D86,SCREEN+0x0C70,SCREEN+0x0D30
    dw SCREEN+0x0D70,SCREEN+0x0DB0,SCREEN+0x0DF0,SCREEN+0x0CB0,SCREEN+0x0CF0
; Draw one indicator bar at the screen address from the table: clear its 5 lines, then fill by value
DrawIndicatorBars:
    ld c,a
    ld a,(de)
    ld l,a
    inc de
    ld a,(de)
    ld h,a
    push hl
    ld d,0x05
clrNextLineofIndicatorBar:
    ld b,0x09
    push hl
clrindbarloop:
    ld (hl),0xFF
    inc l
    djnz clrindbarloop
    ld (hl),0xEE
    pop hl
    ld a,h
    add a,0x08
    ld h,a
    dec d
    jr nz,clrNextLineofIndicatorBar
    pop hl
    ld a,c
    srl a
    srl a
    ld b,a
    ld a,(todoIndBarValue)
    and a
    jr nz,LAB_ram_6166
    ld a,c
    and 0x03
    ld c,0xFF
    jr z,todoDrawIndBarPixel
    ld c,0x77
    dec a
    jr z,todoDrawIndBarPixel
    ld c,0x33
    dec a
    jr z,todoDrawIndBarPixel
    ld c,0x11
todoDrawIndBarPixel:
    ld d,0x05
    inc b
    dec b
    jr z,LAB_ram_615b
    ld e,b
drawIndbarNextLine:
    push hl
    ld b,e
drawIndbarPixel:
    ld (hl),0x00
    inc l
    djnz drawIndbarPixel
    ld a,(hl)
    and c
    ld (hl),a
    pop hl
    ld a,h
    add a,0x08
    ld h,a
    dec d
    jr nz,drawIndbarNextLine
    ret
LAB_ram_615b:
    ld a,(hl)
    and c
    ld (hl),a
    ld a,h
    add a,0x08
smcIndicatorPatch1:
    ld h,a
    dec d
smcIndicatorPatch2:
    jr nz,LAB_ram_615b
    ret
LAB_ram_6166:
    ld a,c
    and 0x03
    ld c,0x33
    jr z,LAB_ram_6179
    ld c,0x99
    dec a
    jr z,LAB_ram_6179
    ld c,0xCC
    dec a
    jr z,LAB_ram_6179
    ld c,0xEE
LAB_ram_6179:
    ld d,0x05
    inc b
    dec b
    jr z,LAB_ram_61a0
    ld e,b
LAB_ram_6180:
    push hl
    ld b,e
LAB_ram_6182:
    ld (hl),0xFF
    inc l
    djnz LAB_ram_6182
    ld a,c
    cp 0xEE
    jr z,LAB_ram_6197
    and (hl)
    ld (hl),a
LAB_ram_618e:
    pop hl
    ld a,h
    add a,0x08
    ld h,a
    dec d
    jr nz,LAB_ram_6180
    ret
LAB_ram_6197:
    and (hl)
    ld (hl),a
    inc hl
    ld a,0x77
    and (hl)
    ld (hl),a
    jr LAB_ram_618e
LAB_ram_61a0:
    ld a,(hl)
    and c
    ld (hl),a
    ld a,h
    add a,0x08
    ld h,a
    dec d
    jr nz,LAB_ram_615b
    ret
SunMassLocked:
    db 0x00
planetMassLocked:
    db 0x00
compassY:
    db 0x00
compassZ:
    db 0x00
compassX:
    db 0x00
; ZX Spectrum: position_tracked_markers (&81A9)
; Runs every frame: updates the two tracked objects (the planet and the station, positions in 9-byte sign-magnitude blocks) on the dashboard compass.
; (Fessor's name is misleading: the Spectrum disassembly reads this as the compass update.)
chkAltitude:
    xor a
    ld (SunMassLocked),a
mi_61B4:
    ld ix,posDataSun
    ld a,(ix+2)
    and 0x7F
    jr nz,chalt2
    ld a,(ix+5)
    and 0x7F
    jr nz,chalt2
    ld a,(ix+8)
    and 0x7F
    jr nz,chalt2
    call chalt21
    ld a,h
    or l
    jr z,chalt2
    ld a,0x01
    ld (SunMassLocked),a
    ex de,hl
    ld hl,0x0000
    sbc hl,de
    ex de,hl
    ld hl,0x4000
    and a
    sbc hl,de
    jp c,crashOnPlanet
    ld hl,0x2000
    xor a
    sbc hl,de
    jr nc,chalt1
    ld a,0x01
chalt1:
    ld (flagCanScoopFuel),a
    ex de,hl
    call chalt15
    ld a,h
    ld (CockpitTemp),a
chalt2:
    xor a
    ld (planetMassLocked),a
    ld ix,posDataPlanet
    ld a,(ix+2)
    and 0x7F
    cp 0x02
    jr nc,chalt6
    ld b,a
    ld a,(ix+5)
    and 0x7F
    cp 0x02
    jr nc,chalt6
    or b
    ld b,a
    ld a,(ix+8)
    and 0x7F
    cp 0x02
    jr nc,chalt6
    or b
    ld a,0x01
    ld (planetMassLocked),a
    jr nz,chalt3
    call chalt21
    ld a,h
    or l
    jr z,chalt3
    ex de,hl
    ld hl,0x0000
    sbc hl,de
    ex de,hl
    ld hl,0x4000
    and a
    sbc hl,de
    jp c,crashOnPlanet
    ex de,hl
    call chalt15
    ld a,0xA0
    sub h
    ld (Altitude),a
chalt3:
    ld a,0x01
    ld (FlagStationNear),a
    ld a,(StationEnergy)
    inc a
    ld ix,sEntityxlo
    jr z,chalt7
    call chalt21
    ld a,h
    or l
    jr nz,chalt4
    dec hl
chalt4:
    ex de,hl
    push de
    call chalt5
    ld (compassY),a
    inc ix
    inc ix
    inc ix
    pop de
    call chalt5
    jr chalt9
; ZX Spectrum: load_and_divide_position_component (&8271)
chalt5:
    xor a
    ld l,(ix+0)
    ld h,(ix+1)
    jr chalt12
chalt6:
    xor a
    ld (FlagStationNear),a
chalt7:
    inc ix
    call chalt20
    ld a,h
    or l
    jr nz,chalt8
    dec hl
chalt8:
    ex de,hl
    dec ix
    push de
    call chalt11
    ld (compassY),a
    inc ix
    inc ix
    inc ix
    pop de
    call chalt11
chalt9:
    ld (compassZ),a
    ld a,(ix+5)
    and 0x80
    ld a,0x00
    jr z,chalt10
    ld a,0x01
chalt10:
    ld (compassX),a
    jp drawCompass
; ZX Spectrum: divide_scale_8_and_sign (&82BB)
chalt11:
    ld a,(ix+0)
    ld l,(ix+1)
    ld h,(ix+2)
    res 7,h
chalt12:
    call div_hl_a_de
    rl b
    rla
    rl b
    rla
    rl b
    rla
    ld h,(ix+2)
    bit 7,h
    jr z,chalt13
    or 0x80
chalt13:
    ret
crashOnPlanet:
    ld a,0x01
    ld (GameOverFlag),a
    ret
; ZX Spectrum: scale_distance_and_step_busy_flag (&82D7)
chalt15:
    push hl
    add hl,hl
    pop de
    srl d
    rr e
    add hl,de
    ld a,(todoUnknownStatusFlags)
    ld b,a
    ld a,h
    cp 0x50
    jr c,chalt17
    cp 0x78
    jr nc,chalt16
    ld a,b
    cp 0x63
    ret z
    ld a,0x02
    jr chalt18
chalt16:
    ld a,0x63
    jr chalt18
chalt17:
    ld a,b
    cp 0x04
    ret nz
    ld a,0x06
chalt18:
    ld (todoUnknownStatusFlags),a
    ret
; Load DE, BC and HL with the x, y and z words of the entity at IX
todo_getCoordinatesinSpace:
    ld e,(ix+0)
    ld d,(ix+1)
    ld c,(ix+3)
    ld b,(ix+4)
    ld l,(ix+6)
    ld h,(ix+7)
    ret
; Load entity coordinates with sign bits cleared and shift them down together until they fit; A counts shifts
chalt20:
    call todo_getCoordinatesinSpace
    res 7,h
    res 7,d
    res 7,b
    ld a,0x01
    jr chalt22
; Load entity coordinates (signs kept) and shift them down together until they fit; A counts shifts
chalt21:
    call todo_getCoordinatesinSpace
    ld a,0x01
chalt22:
    ex de,hl
    add hl,hl
    ex de,hl
    jr c,chalt23
    sla c
    rl b
    jr c,chalt24
    add hl,hl
    jr c,chalt25
    add a,a
    jr chalt22
chalt23:
    rr d
    jr chalt26
chalt24:
    rr b
    srl d
    jr chalt26
chalt25:
    rr h
    srl b
    srl d
chalt26:
    ld c,d
    push af
    ld a,h
    call GetSquareforAinDE
    ex de,hl
    ld a,b
    ld b,0x00
    call GetSquareforAinDE
    add hl,de
    jr nc,chalt27
    inc b
chalt27:
    ld a,c
    call GetSquareforAinDE
    add hl,de
    jr nc,chalt28
    inc b
chalt28:
    ld a,b
    and a
    jr z,chalt29
    srl b
    rr h
    rr l
    srl b
    rr h
    rr l
    pop af
    srl a
    jr z,chalt31
    push af
chalt29:
    call approx_sqrt_16bit
    pop af
chalt30:
    srl a
    jr z,chalt32
    srl h
    rr l
    jr chalt30
chalt31:
    call approx_sqrt_16bit
    add hl,hl
    jr nc,chalt32
    ld hl,0x0000
chalt32:
    ret
wkscrAdrCompassCentre:
    db 0x00,0x00
drawCompass:
    ld a,(Viewdirection)
    cp 0x04
    ret nc
    ld hl,SCREEN+0xCAC
    ld a,(compassZ)
    ld b,a
    and 0x7F
    jr z,pti4
    ld a,b
    and 0x80
    jr nz,pti2
pti1:
    call getPrevScreenLineAdr
    djnz pti1
    jr pti4
pti2:
    res 7,b
pti3:
    call getNextScreenLineAdr
    djnz pti3
pti4:
    ld (wkscrAdrCompassCentre),hl
    call drawCompassFrame
    ld a,(compassY)
    bit 7,a
    jr z,pti5
    and 0x7F
    neg
pti5:
    add a,0x02
    ld b,a
    and 0x03
    add a,a
    add a,a
    add a,a
    ld l,a
    ld a,(compassX)
    and a
    ld a,0x00
    jr z,selectCompassDot
    ld a,0x20
selectCompassDot:
    add a,l
    ld l,a
    ld h,0x00
    ld de,gfxCompassDot
    add hl,de
    ld a,b
    add a,0x08
    srl a
    srl a
    ld de,(wkscrAdrCompassCentre)
    dec de
    dec de
    add a,e
    ld e,a
    jr nc,pti7
    inc d
pti7:
    ld b,0x04
pti8:
    ld a,(de)
    or (hl)
    ld (de),a
    inc de
    inc hl
    ld a,(de)
    or (hl)
    ld (de),a
    dec de
    inc hl
    ex de,hl
    call getNextScreenLineAdr
    ex de,hl
    djnz pti8
    ret
; Step screen address HL down one scan line, wrapping to the next 64-byte character row
getNextScreenLineAdr:
    ld a,h
    add a,0x08
    ld h,a
    cp 0x80                             ; 128K layout: the screen page is &4000-&7FFF; the step leaves it at &80xx (it was the carry out of H at &C000)
    ret c
    sub 0x40
    ld h,a
    ld a,l
    add a,0x40
    ld l,a
    ret nc
    inc h
    ret
; Step screen address HL up one scan line, wrapping to the previous 64-byte character row
getPrevScreenLineAdr:
    ld a,h
    sub 0x08
    ld h,a
    cp 0x40                             ; 128K layout: the screen page is &4000-&7FFF (it was cp 0xC0 for &C000-&FFFF)
    ret nc
    add a,0x40
    ld h,a
    ld a,l
    sub 0x40
    ld l,a
    ret nc
    dec h
    ret
; Copy the 6 x 24 byte compass frame graphic to the screen at &C46A
drawCompassFrame:
    ld de,SCREEN+0x46A
    ld hl,gfxCompassFrame
    ld c,0xFF
    ld b,0x18
dpiloop:
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ld a,e
    sub 0x06
    ld e,a
    ex de,hl
    call getNextScreenLineAdr
    ex de,hl
    djnz dpiloop
    ret
gfxCompassDot:
    db "f",0x00,0xFF,0x00,0xFF,0x00,"f",0x00,"3",0x00,"w",0x88,"w",0x88,"3",0x00
    db 0x11,0x88,"3",0xCC,"3",0xCC,0x11,0x88,0x00
    db 0xCC,0x11,0xEE,0x11,0xEE,0x00,0xCC,0xFF,0x00,0x99,0x00,0x99,0x00,0xFF,0x00,"w"
    db 0x88,"D",0x88,"D",0x88,"w",0x88,"3",0xCC,0x22,"D",0x22,"D3",0xCC,0x11
    db 0xEE,0x11,0x22,0x11,0x22,0x11,0xEE
gfxCompassFrame:
    db 0x0F,0x0F,0x0F,0x0F,0x0F,0x0E,0x0F,0x0F,0x08,0x01,0x0F,0x0E,0x0F,0x0E,0x07,0x0E
    db 0x07,0x0E,0x0F,0x0D,0x0F,0x0F,0x0B,0x0E,0x0F,0x0B,0x0F,0x0F,0x0D,0x0E,0x0F,0x07
    db 0x0F,0x0F,0x0E,0x0E,0x0E,0x0F,0x0F,0x0F,0x0F,0x06,0x0E,0x0F,0x0F,0x0F,0x0F,0x06
    db 0x0D,0x0F,0x0F,0x0F,0x0F,0x0A,0x0D,0x0F,0x0F,0x0F,0x0F,0x0A,0x0D,0x0F,0x0F,0x0F
    db 0x0F,0x0A,0x0D,0x0F,0x0F,0x0F,0x0F,0x0A,0x0D,0x0F,0x0F,0x0F,0x0F,0x0A,0x0D,0x0F
    db 0x0F,0x0F,0x0F,0x0A,0x0E,0x0F,0x0F,0x0F,0x0F,0x06,0x0E,0x0F,0x0F,0x0F,0x0F,0x06
    db 0x0F,0x07,0x0F,0x0F,0x0E,0x0E,0x0F,0x0B,0x0F,0x0F,0x0D,0x0E,0x0F,0x0D,0x0F,0x0F
    db 0x0B,0x0E,0x0B,0x0E,0x07,0x0E,0x07,0x0E,0x0E,0x0F,0x08,0x01,0x0F,0x0E,0x0F,0x0F
    db 0x0F,0x0F,0x0F,0x0E,0x0F,0x0B,0x0F,0x0F,0x0F,0x0E,0x0F,0x0F,0x0F,0x0F,0x0F,0x0E
scnX:
    db 0x00
scnY:
    db 0x00
scnZ:
    db 0x00
scnCountShipslots:
    db 0x00
todo_CleanScanCounter:
    db 0x00
; ZX Spectrum: shift_bc_right (&96C5)
; Four entries share one srl b / rr c pair: this one shifts BC right by 4 bits, the next by 3, 2 and 1.
BCdiv16:
    srl b
    rr c
; Divide the unsigned word BC by 8
BCDiv8:
    srl b
    rr c
; Divide the unsigned word BC by 4
BCdiv4:
    srl b
    rr c
; Divide the unsigned word BC by 2
BCdiv2:
    srl b
    rr c
    ret
notinScannerRange:
    jp scnNextShip
; Redraw the scanner: clear the ECM indicator, then plot each of the 8 ship slots that is in range
UpdateScanner:
    call cleanScannerUpdateECMIndicator
    ld a,(storeEntityEnergy1)
    and a
    ret z
    call force_loading_busy_state
    ld a,0x08
    ld (scnCountShipslots),a
    ld ix,sEntityxlo
scnShipsloop:
    ld a,(ix+34)
    and a
    jr z,notinScannerRange
    ld a,(ix+1)
    cp 0x40
    jr nc,notinScannerRange
    ld a,(ix+4)
    cp 0x40
    jr nc,notinScannerRange
    ld a,(ix+7)
    cp 0x40
    jr nc,notinScannerRange
    ld a,(ix+1)
    call GetSquareforAinDE
    ex de,hl
    ld a,(ix+7)
    call GetSquareforAinDE
    add hl,de
    jr c,notinScannerRange
    ld de,0x1600
    and a
    sbc hl,de
    jr nc,notinScannerRange
    ld a,0x01
    ld (todo_CleanScanCounter),a
    ld de,0x4000
    xor a
    ld l,(ix+0)
    ld h,(ix+1)
    call div_hl_a_de
    call BCDiv8
    ld h,b
    ld l,c
    call BCdiv2
    add hl,bc
    ld a,(ix+2)
    and 0x80
    ld a,h
    jr z,uscn1
    or 0x80
uscn1:
    ld (scnX),a
    xor a
    ld l,(ix+3)
    ld h,(ix+4)
    call div_hl_a_de
    call BCdiv16
    ld h,b
    ld l,c
    call BCdiv4
    add hl,bc
    ld a,(ix+5)
    and 0x80
    ld a,h
    jr z,uscn2
    or 0x80
uscn2:
    ld (scnY),a
    xor a
    ld l,(ix+6)
    ld h,(ix+7)
    call div_hl_a_de
    call BCdiv16
    ld h,b
    ld l,c
    call BCdiv4
    add hl,bc
    ld a,(ix+8)
    and 0x80
    ld a,h
    jr z,uscn3
    or 0x80
uscn3:
    ld (scnZ),a
    ld a,(scnY)
    ld d,a
    and 0x7F
    cp 0x19
    jr nc,scnNextShip
    ld a,(scnZ)
    ld b,a
    and 0x7F
    cp 0x19
    jr nc,scnNextShip
    ld e,0x01
    ld a,b
    xor d
    rla
    jr c,uscn4
    ld a,b
    add a,d
    cp 0x19
    jr c,uscn4
    ld e,0x00
    ld a,0x19
    sub b
    ld d,a
uscn4:
    ld a,(scnX)
    bit 7,a
    jr z,uscn5
    and 0x7F
    neg
uscn5:
    add a,0x7B
    ld c,a
    ld a,(scnZ)
    bit 7,a
    jr z,uscn6
    and 0x7F
    neg
uscn6:
    neg
    add a,0xA5
    ld b,a
    call cirGetScrAddr
    inc a
    ld c,0x88
uscn7:
    rlc c
    dec a
    jr nz,uscn7
    ld a,d
    bit 7,a
    jr z,uscn8
    and 0x7F
    jr z,uscn10
    ld b,a
scnDrawStick:
    ld a,(hl)
    or c
    ld (hl),a
    call getNextScreenLineAdr
    djnz scnDrawStick
    jr uscn10
uscn8:
    and a
    jr z,uscn10
    ld b,a
uscn9:
    ld a,(hl)
    or c
    ld (hl),a
    call getPrevScreenLineAdr
    djnz uscn9
uscn10:
    ld a,(hl)
    or c
    ld (hl),a
    bit 0,e
    jr z,scnNextShip
    rlc c
    jr nc,uscn11
    dec l
uscn11:
    ld a,(hl)
    or c
    ld (hl),a
    rlc c
    jr nc,uscn12
    dec l
uscn12:
    ld a,(hl)
    or c
    ld (hl),a
scnNextShip:
    ld a,(scnCountShipslots)
    dec a
    ret z
    ld (scnCountShipslots),a
    ld de,0x0027
    add ix,de
    jp scnShipsloop
; Get the byte address for pixel (C,B): screen layout when the circle flag is set, else the game bitmap
cirGetBMAdress:
    ld a,(CirclewheretoDrawFlag)
    and a
    jr nz,cirGetScrAddr
; HL = byte address in the game bitmap for pixel (C,B); A = pixel number within the byte
getByteAddressinBitmap:
    ld h,0x02
    ld l,b
    add hl,hl
    inc h
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
circgetPixelmaskinBitmap:
    ld a,c
    srl a
    srl a
    add a,l
    ld l,a
    ld a,c
    and 0x03
    sub 0x03
    neg
    ret
; HL = screen memory address for pixel (C,B) in CPC layout; adds 24 to Y if todoDrawCircleFlag is set
cirGetScrAddr:
    ld a,(todoDrawCircleFlag)
    and a
    jr z,getByteAdrinScrMem
    ld a,b
    add a,0x18
    ld b,a
getByteAdrinScrMem:
    ld a,b
    rra
    rra
    rra
    and 0x1F
    ld h,a
    ld a,b
    add a,a
    add a,a
    add a,a
    add a,a
    add a,a
    add a,h
    ld h,a
    ld l,0x00
    scf
    rr h
    rr l
    and a                               ; 128K layout: the second SCF made the base &C000; this gives &4000
    rr h
    rr l
    jr circgetPixelmaskinBitmap
; ZX Spectrum: force_loading_busy_state (&988E)
force_loading_busy_state:
    ld a,(storeEntityEnergy2)
    and a
    ret z
    ld a,(todoUnknownStatusFlags)
    cp 0x63
    ret z
    cp 0x02
    ret z
    ld a,0x06
    ld (todoUnknownStatusFlags),a
    ret
; Docking check: enter the station if the orientation flag is set, else test the docking computer
chkManualDocking:
    ld a,(flagCorrectOrientation)
    and a
    jr z,chkCanDockStation
    xor a
    ld (flagCorrectOrientation),a
    jr EnterStation
; ZX Spectrum: handle_demo_fire_key (&717B)
chkCanDockStation:
    ld a,(keybFlags4CounterNstringNumber)
    ld b,a
    and 0x80
    res 7,b
    ld a,b
    ld (keybFlags4CounterNstringNumber),a
    ret z
    ld a,(FlagStationNear)
    and a
    ret z
    ld a,(dockingComputer)
    and a
    ret z
    ld a,(todoUnknownStatusFlags)
    and a
    ret z
    ld a,(tunnelFlag1)
    and a
    ret nz
    ld hl,sEntityRole
    bit 2,(hl)
    ret nz
    ld a,0x01
    ld (flagDockingComputerOn),a
EnterStation:
    xor a
    ld (Viewdirection),a
    call drawDashboard
LAB_ram_6718:
    call nudge_tracked_marker
    jp DockingSequence
; ZX Spectrum: nudge_tracked_marker (&71C0)
nudge_tracked_marker:
    ld iy,posDataSun
    ld ix,sEntityxlo
    call SUB_ram_672c
    call SUB_ram_672c
; Double the half-difference from half_diff_ship_marker, keep its sign, store at IY+1/+2 and step IX, IY by 3
SUB_ram_672c:
    call half_diff_ship_marker
    add hl,hl
    jr nc,LAB_ram_6734
    set 7,h
LAB_ram_6734:
    ld (iy+2),h
    ld (iy+1),l
    ld de,0x0003
    add iy,de
    add ix,de
    ret
; ZX Spectrum: half_diff_ship_marker (&71E4)
half_diff_ship_marker:
    ld h,(iy+2)
    ld l,(iy+1)
    ld d,(ix+2)
    ld e,(ix+1)
    jp minus_de_plus_hl_div_2
; ZX Spectrum: handle_chart_cursor_keys (&71F3)
handle_chart_cursor_keys:
    ld a,(Viewdirection)
    cp 0x07
    ret c
    cp 0x09
    ret nc
    ld a,(tunnelFlag1)
    and a
    ret nz
    ld a,(keybFlags2)
    and 0x0F
    ld c,a
    ld a,(keybFlags5)
    and 0x70
    or c
    ret z
    ld b,0x08
todo_676e:
    inc b
    srl a
    jr nc,todo_676e
    ld a,b
    call execSelectedKeyFunctions
    xor a
    ld (keybFlags5),a
    ld (keybFlags2),a
    ret
pos3dX1:
    db 0x00
pos3dX2:
    db 0x00
pos3dX3:
    db 0x00
todo_3dpos_y1:
    db 0x00
todo_3dpos_y2:
    db 0x00,0x00
todo_3dpos_z1:
    db 0x00
todo_3dpos_z2:
    db 0x00
todo_3dpos_z3:
    db 0x00
todoSunRadius:
    db 0x00
; Draw the sun and planet circles, erasing or redrawing the previous circle as needed
drawPlanetnSun:
    ld hl,posDataSun
    ld de,pos3dX1
    ld bc,0x0009
    ldir
    call calcSunPlanetCoordinates
    push af
LAB_ram_6798:
    call todoOverheating
    pop af
    and a
    jr z,drawPlanet
    call StoreCircleOffsets
    call SUB_ram_6802
    jr z,undrawCircle
    ld a,(BYTE_ram_683a)
    ld b,a
    ld a,(drawradius)
    cp b
    jr nc,RedrawCircle
    call todoDrawFilledCircle
    call RestoreCircleOffsets
    jp clearCircle
; Save circleOffsetY and circleOffsetXhi to the store copies
StoreCircleOffsets:
    ld hl,(circleOffsetY)
    ld (storeCircleOffsetY),hl
    ld hl,(circleOffsetXhi)
    ld (storeCircleOffsetX),hl
    ret
; Restore circleOffsetY and circleOffsetXhi from the store copies
RestoreCircleOffsets:
    ld hl,(storeCircleOffsetY)
    ld (circleOffsetY),hl
    ld hl,(storeCircleOffsetX)
    ld (circleOffsetXhi),hl
    ret
drawPlanet:
    call SUB_ram_6802
    ret z
    jp todoDrawFilledCircle
undrawCircle:
    call RestoreCircleOffsets
    jp clearCircle
RedrawCircle:
    ld hl,(circleOffsetY)
    ld (workstoreCircleOffsetY),hl
    ld hl,(circleOffsetXhi)
    ld (workstoreCircleOffsetX),hl
    call RestoreCircleOffsets
    call clearCircle
    ld hl,(workstoreCircleOffsetY)
    ld (circleOffsetY),hl
    ld hl,(workstoreCircleOffsetX)
    ld (circleOffsetXhi),hl
    jp todoDrawFilledCircle
; Copy the planet position into the 3D buffer and compute its screen coordinates; flags left in A
SUB_ram_6802:
    ld hl,posDataPlanet
    ld de,pos3dX1
    ld bc,0x0009
    ldir
    call calcSunPlanetCoordinates
    and a
    ret
; ZX Spectrum: set_demo_message_flag (&75C0)
todoOverheating:
    ld a,(BYTE_ram_3933)
    and a
    ret z
    ld a,(todoSunRadius)
    and a
    jr nz,LAB_ram_6820
    ld a,(drawradius)
LAB_ram_6820:
    IFDEF MISSIONS
    call mxSun                      ; missions_flight.asm: Trumbles die in the heat (replaces ld hl,CockpitTemp)
    ELSE
    ld hl,CockpitTemp
    ENDIF
    inc (hl)
    add a,0x02
    jr z,killmebyoverheating
    jr nc,LAB_ram_6830
killmebyoverheating:
    ld a,0x01
    ld (GameOverFlag),a
    xor a
LAB_ram_6830:
    ld (drawradius),a
    ld (todoSunRadius),a
    ret
storeCircleOffsetY:
    db "!@"
storeCircleOffsetX:
    db 0x1A
BYTE_ram_683a:
    db 0xCD
workstoreCircleOffsetY:
    db "@h"
workstoreCircleOffsetX:
    db 0xCD,"@"
; Move the sun and the planet entries with MVIT
moveSunNPlanet:
    ld ix,posDataSun
    call MVIT
    ld ix,posDataPlanet
    jp MVIT
; ZX Spectrum: fly_ship0_to_origin (&7861)
; Flies the object in slot 0 (the planet or station on arrival) in to the origin and then marks the move as done.
moveSpaceStation:
    ld a,(StationEnergy)
    and a
    ld ix,sEntityxlo
    jr nz,LAB_ram_6860
    ld a,(ix+34)
    and a
    ret nz
    dec a
    ld (StationEnergy),a
LAB_ram_6860:
    call SUB_ram_531d
    ld a,(ix+2)
    and 0x7F
    ret nz
    ld a,(ix+5)
    and 0x7F
    ret nz
    ld a,(ix+8)
    and 0x7F
    ret nz
    bit 7,(ix+38)
    ret nz
    xor a
    ld (StationEnergy),a
    ld a,0xF0
    ld (ix+34),a
    ret
; Draw the explosion cloud for each of the 8 entity slots whose flag bits 4-5 are set
todoDrawExplosions:
    ld a,(storeEntityEnergy1)
    and a
    ret z
    ld ix,sEntityxlo
    ld b,0x08
LAB_ram_688f:
    push bc
    ld a,(ix+32)
    ld c,a
    and 0x30
    cp 0x30
    jr nz,LAB_ram_68df
    ld a,(0x28B5)
; Probably the explosion/flash effect: sets circle mask and sound flag, then draws circles for each ship slot
sub_689D:
    ld (CirclePixelMask),a
    ld a,0x4E
    ld (0x28B5),a
    ld a,(sfxFlags2Bitmap)
    or 0x40
    ld (sfxFlags2Bitmap),a
    ld h,(ix+28)
    ld l,(ix+29)
    ld (circleOffsetY),hl
    ld l,(ix+30)
    ld h,(ix+31)
    ld (circleOffsetXhi),hl
    ld c,0x0F
LAB_ram_68c1:
    push ix
    push bc
    call SUB_ram_e74c
    pop bc
    pop ix
    ld a,(drawradius)
    add a,0x02
    ld (drawradius),a
    dec c
    jr nz,LAB_ram_68c1
    ld a,(CirclePixelMask)
    ld (0x28B5),a
    res 4,(ix+32)
LAB_ram_68df:
    ld de,0x0027
    add ix,de
    pop bc
    djnz LAB_ram_688f
    ret
CirclePixelMask:
    db 0xCD
; Projects the sun/planet 3D position into view coordinates for the current view direction
calcSunPlanetCoordinates:
    exx
    ld bc,0x0003
    exx
    ld a,(Viewdirection)
    and a
    jp nz,LAB_ram_699d
    ld a,(todo_3dpos_z3)
    bit 7,a
    jp nz,LAB_ram_6b30
    and 0x7F
    ld (todo_3dpos_z3),a
    ld hl,(todo_3dpos_z2)
    ex de,hl
    ld hl,(pos3dX2)
    ld a,(todo_3dpos_z1)
    ld b,a
    ld a,(pos3dX1)
    ld c,a
    ld a,h
    bit 7,a
    jr nz,LAB_ram_691a
    exx
    set 0,b
    exx
LAB_ram_691a:
    and 0x7F
    ld h,a
    call divide_signed
    ld a,d
    ld (circleOffsetXlo),a
    ld hl,(todo_3dpos_z2)
    ex de,hl
    ld hl,(todo_3dpos_y2)
    ld a,(todo_3dpos_z1)
    ld b,a
    ld a,(todo_3dpos_y1)
    ld c,a
    ld a,h
    bit 7,a
    jr nz,LAB_ram_693c
    exx
    set 1,b
    exx
LAB_ram_693c:
    and 0x7F
    ld h,a
    call divide_signed
    ld a,d
    ld (circleOffsetY),a
    exx
    ld a,b
    exx
    ld (circleOffsetXhi),a
    ld a,(todo_3dpos_z3)
    and a
    jr nz,LAB_ram_6961
mi_6952:
    ld hl,0xA000
    ld de,(todo_3dpos_z1)
    sbc hl,de
    jr c,LAB_ram_6961
    ld a,0xFF
    jr LAB_ram_699a
LAB_ram_6961:
    ld hl,0xA000
    ld de,(todo_3dpos_z2)
    and a
    sbc hl,de
    jp c,LAB_ram_6b30
    ld a,(todo_3dpos_z3)
    and a
    jr z,LAB_ram_6990
    ld b,a
    ld a,(todo_3dpos_z2)
    ld c,a
    xor a
    ld e,0xA0
LAB_ram_697c:
    sla c
    rl b
    jr c,LAB_ram_6987
    sla e
    rla
    jr LAB_ram_697c
LAB_ram_6987:
    scf
    rr b
    call SUB_ram_6b43
    ld a,d
    jr LAB_ram_699a
LAB_ram_6990:
    ld a,(todo_3dpos_z2)
    ld b,a
    ld a,0xA0
    call SUB_ram_6b41
    ld a,d
LAB_ram_699a:
    jp LAB_ram_6a9a
LAB_ram_699d:
    dec a
    jr nz,LAB_ram_69cb
    ld a,(todo_3dpos_z3)
    bit 7,a
    jp z,LAB_ram_6b30
    and 0x7F
    ld (todo_3dpos_z3),a
    ld hl,(todo_3dpos_z2)
    ex de,hl
    ld hl,(pos3dX2)
    ld a,(todo_3dpos_z1)
    ld b,a
    ld a,(pos3dX1)
    ld c,a
    ld a,h
    bit 7,a
    jr z,LAB_ram_69c8
    and 0x7F
    ld h,a
    exx
    set 0,b
    exx
LAB_ram_69c8:
    jp LAB_ram_691a
LAB_ram_69cb:
    dec a
    jp nz,LAB_ram_6a77
    ld a,(pos3dX3)
    bit 7,a
    jp z,LAB_ram_6b30
    and 0x7F
    ld (pos3dX3),a
    ld hl,(pos3dX2)
    ex de,hl
    ld hl,(todo_3dpos_z2)
    ld a,(pos3dX1)
    ld b,a
    ld a,(todo_3dpos_z1)
    ld c,a
    ld a,h
    bit 7,a
    jr nz,LAB_ram_69f4
    exx
    set 0,b
    exx
LAB_ram_69f4:
    and 0x7F
    ld h,a
    call divide_signed
    ld a,d
    ld (circleOffsetXlo),a
    ld hl,(pos3dX2)
    ex de,hl
    ld hl,(todo_3dpos_y2)
    ld a,(pos3dX1)
    ld b,a
    ld a,(todo_3dpos_y1)
    ld c,a
    ld a,h
    bit 7,a
    jr nz,LAB_ram_6a16
    exx
    set 1,b
    exx
LAB_ram_6a16:
    and 0x7F
    ld h,a
    call divide_signed
    ld a,d
    ld (circleOffsetY),a
    exx
    ld a,b
    exx
    ld (circleOffsetXhi),a
    ld a,(pos3dX3)
    and a
    jr nz,LAB_ram_6a3b
    ld hl,0xA000
    ld de,(pos3dX1)
    sbc hl,de
    jr c,LAB_ram_6a3b
    ld a,0xFF
    jr LAB_ram_6a74
LAB_ram_6a3b:
    ld hl,0xA000
    ld de,(pos3dX2)
    and a
    sbc hl,de
    jp c,LAB_ram_6b30
    ld a,(pos3dX3)
    and a
    jr z,LAB_ram_6a6a
    ld b,a
    ld a,(pos3dX2)
    ld c,a
    xor a
    ld e,0xA0
LAB_ram_6a56:
    sla c
    rl b
    jr c,LAB_ram_6a61
    sla e
    rla
    jr LAB_ram_6a56
LAB_ram_6a61:
    scf
    rr b
    call SUB_ram_6b43
    ld a,d
    jr LAB_ram_6a74
LAB_ram_6a6a:
    ld a,(pos3dX2)
    ld b,a
    ld a,0xA0
    call SUB_ram_6b41
    ld a,d
LAB_ram_6a74:
    jp LAB_ram_6a9a
LAB_ram_6a77:
    ld a,(pos3dX3)
    bit 7,a
    jp nz,LAB_ram_6b30
    ld hl,(pos3dX2)
    ex de,hl
    ld hl,(todo_3dpos_z2)
    ld a,(pos3dX1)
    ld b,a
    ld a,(todo_3dpos_z1)
    ld c,a
    ld a,h
    bit 7,a
    jr z,LAB_ram_6a97
    exx
    set 0,b
    exx
LAB_ram_6a97:
    jp LAB_ram_69f4
LAB_ram_6a9a:
    ld (drawradius),a
    ld a,0x01
    ret
LAB_ram_6aa0:
    ld h,l
    ld l,c
    ld d,e
    ld e,b
    jr LAB_ram_6aca
; ZX Spectrum: divide_signed (&77A0)
; The Spectrum port of the BBC's DVID3B2. Divides a 24-bit numerator (H L C) by a 24-bit divisor (D E B), both magnitudes, into an 8-bit
; quotient in D. calcSunPlanetCoordinates feeds it a coordinate over the depth, so D comes back as an offset from the screen centre.
; Numerator and divisor are shifted left in step (the ratio is unchanged) to use the full precision. The alternate register C' counts the call
; (3 on entry, one less each call) so the near-centre marker lands in bit 2 of B' for x and bit 3 for y; those become the overflow flags in
; circleOffsetXhi (&20C9). Returns A = 0 elsewhere to say the object cannot be drawn.
divide_signed:
    push hl
    exx
    dec c
    exx
    and a
    sbc hl,de
    jp c,divide_underflow
    jp z,LAB_ram_6ae3
LAB_ram_6ab3:
    pop hl
    ld a,h
    and a
    jr z,LAB_ram_6aa0
    ld a,0x08
LAB_ram_6aba:
    sla c
    adc hl,hl
    jp c,divide_overflow
    sla b
    rl e
    rl d
    dec a
    jr nz,LAB_ram_6aba
LAB_ram_6aca:
    ld a,0x08
LAB_ram_6acc:
    add hl,hl
    jp c,divide_overflow
    ex de,hl
    add hl,hl
    ex de,hl
    dec a
    jr nz,LAB_ram_6acc
    ld a,0x08
LAB_ram_6ad8:
    sla h
    jp c,divide_overflow
    sla d
    dec a
    jr nz,LAB_ram_6ad8
    ret
LAB_ram_6ae3:
    push bc
    ld a,c
    sub b
    pop bc
    jr c,divide_underflow
    jr z,divide_underflow
    jp LAB_ram_6ab3
LAB_ram_6aee:
    set 2,b
    jp LAB_ram_6af9
; ZX Spectrum: divide_underflow (&77ED)
; Numerator smaller than divisor (the object is within a pixel of the centre on this axis): marks bit 2 (first call) or bit 3 (second call)
; of B' and carries on shifting for the fraction.
divide_underflow:
    exx
    dec c
    jr nz,LAB_ram_6aee
    set 3,b
LAB_ram_6af9:
    inc c
    exx
    pop hl
    ld a,0x17
LAB_ram_6afe:
    sla c
    adc hl,hl
    push af
    sla b
    rl e
    rl d
    jr c,LAB_ram_6b37
    pop af
    dec a
    jr nz,LAB_ram_6afe
    ret
; ZX Spectrum: divide_overflow (&780A)
; Reached when the lockstep shift carried a 1 out of the numerator: if the quotient cannot fit in a byte the routine returns 0 (not drawable),
; otherwise it finishes with the top-byte divide.
divide_overflow:
    sla b
    rl e
    rl d
    push af
    scf
    rr h
    rr l
    pop af
    jr c,LAB_ram_6b26
    push hl
    and a
    sbc hl,de
    jr nc,LAB_ram_6b2e
    pop hl
LAB_ram_6b26:
    scf
    rr d
    and a
    sbc hl,de
    jr LAB_ram_6b3f
LAB_ram_6b2e:
    pop hl
    pop af
LAB_ram_6b30:
    xor a
    ret
LAB_ram_6b32:
    scf
    rr h
    jr LAB_ram_6b3c
; ZX Spectrum: divide_underflow_overflow (&7831)
LAB_ram_6b37:
    pop af
    jr c,LAB_ram_6b32
    rr h
LAB_ram_6b3c:
    scf
    rr d
LAB_ram_6b3f:
    ld a,h
    ld b,d
; Divide setup: clears E and falls into the A/B shift-subtract division (quotient in D, fraction in E)
SUB_ram_6b41:
    ld e,0x00
; Shift-and-subtract division of A by B, building the quotient in D (0xFE seed)
SUB_ram_6b43:
    ld d,0xFE
LAB_ram_6b45:
    sla e
    rla
    jr c,LAB_ram_6b52
    cp b
    jr nc,LAB_ram_6b52
    sla d
    ret nc
    jr LAB_ram_6b45
LAB_ram_6b52:
    sub b
    scf
    rl d
    ret nc
    jr LAB_ram_6b45
togglelcljumpFX:
    db 0x00
; Handles the local (short) jump key: checks no mass lock or station, then moves dust and ships
chkLocalJump:
    ld a,(keybFlags3)
    bit 6,a
    push af
    and 0xBF
    ld (keybFlags3),a
    pop af
    ret z
    ld a,(SunMassLocked)
    dec a
    ret z
    ld a,(planetMassLocked)
    dec a
    ret z
    ld a,(entityMassLocked)
    and a
    ret nz
    ld a,(StationEnergy)
    and a
    ret z
    xor a
    ld (aspMissionState),a
    ld ix,sEntityxlo
    call cleanShipSlots
    ld a,(dustByte6BFD)
    rrca
    ld (dustByte6BFD),a
    ld a,0x01
    jr c,lcljmp1
    ld (todoLaserVar2),a
lcljmp1:
    ld (togglelcljumpFX),a
    ld ix,posDataSun
    call lcljmp2
    ld ix,posDataPlanet
    call lcljmp2
    ld ix,sEntityxlo
; Local jump: shifts one ship coordinate by 0x20 toward the player, wrapping at the range limit
lcljmp2:
    ld bc,0x0020
    ld h,(ix+8)
    ld l,(ix+7)
    ld d,l
    bit 7,h
    jr nz,lcljmp3
    and a
    sbc hl,bc
    jr c,lcljmp6
    jr lcljmp4
lcljmp3:
    add hl,bc
    jr c,lcljmp7
lcljmp4:
    ld (ix+8),h
    ld (ix+7),l
lcljmp5:
    ret
lcljmp6:
    ld hl,0x2000
    ld e,(ix+6)
    and a
    sbc hl,de
    ld a,0x80
    ld (ix+8),a
    ld (ix+7),h
    ld (ix+6),l
    ret
lcljmp7:
    ld a,0x7F
    ld (ix+8),a
    ld a,0xFF
    ld (ix+7),a
    ld (ix+6),a
    ret
dustRoll:
    db 0x00
dustPitch:
    db 0x00
dustVar15:
    db 0x00
dustVar3:
    db 0x00
adrOfCoordinatesTable:
    db 0x00,0x00
dustParticleSpeed:
    db 0x00
dustVar12:
    db 0x00
dustVar9:
    db 0x00
dustVar13:
    db 0x00
dustVar10:
    db 0x00
dustVar11:
    db 0x00
dustViewDirection:
    db 0x00
dustVar5:
    db 0x00
adrOfParticleAdrTable:
    db 0x00,0x00
dustPixelMask:
    db 0x00
numDustParticles:
    db 0x00
dustByte6BFD:
    db "U"
dustParticleAdrTable:
    db 0x08,0xC3,0xC7,"k",0xCB,0xD0,0xC3,0x0D,"l",0xD9,0x0D," ",0xF7,0xCB,0xD8,0x0C
    db 0xD9,0xE1,">",0x17,0xCB,"!",0xED,"j",0xF5,0xCB," ",0xCB,0x13,0xCB,0x12,"8"
    db ",",0xF1,"= ",0xEF,0xC9,0xCB," ",0xCB,0x13,0xCB,0x12,0xF5,"7",0xCB,0x1C
    db 0xCB,0x1D,0xF1,"8",0x07,0xE5,0xA7,0xED,"R0",0x09,0xE1
; Draws the space dust for the frame; a pending local jump draws it twice at different speeds
DrawSpaceDust:
    ld a,(togglelcljumpFX)
    dec a
    jr nz,dust2
    ld (togglelcljumpFX),a
    ld a,0x1E
    ld (movementspeed),a
    call dust2
dust1:
    ld a,0x10
    ld (movementspeed),a
    call dust2
; Per-pass dust setup (speed, roll, view direction) then loops over all dust particles
dust2:
    xor a
    ld (numDustParticles),a
    ld (dustVar3),a
    ld a,(movementspeed)
    srl a
    inc a
    ld (dustParticleSpeed),a
    ld hl,(inputRoll)
    ld (dustRoll),hl
    ld a,0x10
    ld (dustVar5),a
    ld a,(todoLaunchFlag)
    and a
    jr z,dust3
    ld a,0x04
    ld (dustVar5),a
dust3:
    ld a,(dustViewDirection)
    ld b,a
    ld a,(Viewdirection)
    cp b
    ld (dustViewDirection),a
    call nz,shuffle_particle_table
    ld hl,dustParticleAdrTable
    ld (adrOfParticleAdrTable),hl
    ld b,0x00
    ld de,tblDustCoordinates
    ld (adrOfCoordinatesTable),de
    ld a,(de)
    cp 0x80
    jr c,dust4
    and 0x7F
    set 7,b
dust4:
    ld (dustVar9),a
    inc de
    ld a,(de)
    cp 0x80
    jr c,dust5
    and 0x7F
    set 6,b
dust5:
    ld (dustVar10),a
    inc de
    ld a,(de)
    ld (dustVar11),a
    inc de
    ld a,(de)
    ld (dustVar12),a
    inc de
    ld a,(de)
    ld (dustVar13),a
    ld a,(dustRoll)
    cp 0x80
    jr c,dust6
    and 0x7F
    set 4,b
    ld (dustRoll),a
dust6:
    ld a,(dustPitch)
    cp 0x80
    jr c,dust7
    and 0x7F
    set 3,b
    ld (dustPitch),a
dust7:
    ld a,b
    ld (dustPixelMask),a
    ld a,(Viewdirection)
    and a
    jp nz,dust57
dust8:
    ld a,(dustParticleSpeed)
    ld c,a
    ld a,(dustVar9)
    ld b,0x05
    call dust73
    push hl
    ld a,(dustParticleSpeed)
    ld c,a
    ld a,(dustVar12)
    ld b,0x05
    call dust73
    pop de
    ld a,(dustVar12)
    add a,l
    ld (dustVar12),a
    ld a,h
    jr nc,dust9
    inc a
dust9:
    add a,e
    ld e,a
    jr nc,dust10
    inc d
dust10:
    ld a,(dustVar11)
    ld b,a
    ld a,d
    and a
    jr nz,dust11
    ld a,e
    cp b
    jr nc,dust11
    call dust81
    ld b,0x00
    jr dust12
dust11:
    ld a,d
    ld l,e
    call dust77
    ld b,c
dust12:
    ld c,d
    ld a,(dustPixelMask)
    and 0x20
    ld hl,(dustVar12)
    jr nz,dust13
    add hl,bc
    ld a,h
    cp 0x78
    jr nc,dust18
    jr dust14
dust13:
    and a
    sbc hl,bc
    jr c,dust18
    jr z,dust18
dust14:
    ld (dustVar12),hl
    ld a,(dustParticleSpeed)
    ld c,a
    ld a,(dustVar10)
    ld b,0x05
; Dust particle update: moves the particle by pitch, roll and speed, clipping it on the edges
sub_6D4E:
    call dust73
    push hl
    ld a,(dustParticleSpeed)
    ld c,a
    ld a,(dustVar13)
    ld b,0x05
    call dust73
    pop de
    ld a,(dustVar13)
    add a,l
    ld (dustVar13),a
    ld a,h
    inc a
    add a,e
    ld e,a
    jr nc,dust15
    inc d
dust15:
    ld a,(dustVar11)
    ld b,a
    ld a,d
    and a
    jr nz,dust16
    ld a,e
    cp b
    jr nc,dust16
    call dust81
    ld b,0x00
    jr dust17
dust16:
    ld a,d
    ld l,e
    call dust77
    ld b,c
dust17:
    ld c,d
    ld a,(dustPixelMask)
    and 0x20
    ld hl,(dustVar13)
    jr nz,dust19
    add hl,bc
    ld a,h
    cp 0x78
    jr nc,dust18
    jr dust20
dust18:
    jp LAB_ram_33bc
dust19:
    and a
    sbc hl,bc
    jr c,dust18
dust20:
    ld (dustVar13),hl
    ld a,(dustParticleSpeed)
    ld c,a
    ld a,(dustPixelMask)
    and 0x20
    jr nz,dust21
    ld a,(dustVar11)
    sub c
    jr dust22
dust21:
    ld a,(dustVar11)
    add a,c
dust22:
    jr c,dust18
    jr z,dust18
    ld (dustVar11),a
dust23:
    ld a,(dustRoll)
    and a
    jp z,dust38
    ld c,a
    ld a,(dustVar10)
    ld b,0x04
    call dust35
    jr z,dust30
    ld l,a
    ld a,(dustPixelMask)
    bit 7,a
    jr nz,dust25
    bit 6,a
    jr nz,dust24
    bit 4,a
    jr nz,dust27
    jr dust28
dust24:
    bit 4,a
    jr nz,dust28
    jr dust27
dust25:
    bit 6,a
    jr nz,dust26
    bit 4,a
    jr nz,dust28
    jr dust27
dust26:
    bit 4,a
    jr nz,dust27
    jr dust28
dust27:
    ld a,(dustVar9)
    add a,l
    cp 0x78
    jr nc,dust18
    jr dust29
dust28:
    ld a,(dustVar9)
    sub l
    call c,dust72
dust29:
    ld (dustVar9),a
dust30:
    ld a,(dustRoll)
    ld c,a
    ld a,(dustVar9)
    ld b,0x04
    call dust35
    jr z,dust38
    ld l,a
    ld a,(dustPixelMask)
    bit 7,a
    jr nz,dust32
    bit 6,a
    jr nz,dust31
    bit 4,a
    jr nz,dust34
    jr dust36
dust31:
    bit 4,a
    jr nz,dust36
    jr dust34
dust32:
    bit 6,a
    jr nz,dust33
    bit 4,a
    jr nz,dust36
    jr dust34
dust33:
    bit 4,a
    jr z,dust36
dust34:
    ld a,(dustVar10)
    sub l
    call c,dust71
    jr dust37
; Multiplies A by C via dust73 and returns the doubled high part in A (dust coordinate scaling)
dust35:
    ld b,0x04
    call dust73
    ld a,h
    rl l
    rla
    and a
    ret
dust36:
    ld a,(dustVar10)
    add a,l
    cp 0x78
    jp nc,LAB_ram_33bc
dust37:
    ld (dustVar10),a
dust38:
    ld a,(dustPitch)
    and a
    jp z,dust49
    ld c,a
    ld a,(dustVar10)
    ld e,a
    ld b,0x04
    call dust73
    ex de,hl
    ld hl,0x4000
    ld a,(dustPixelMask)
    bit 6,a
    jr nz,dust39
    bit 3,a
    jr z,dust41
    jr dust40
dust39:
    bit 3,a
    jr nz,dust41
dust40:
    add hl,de
    jr dust42
dust41:
    and a
    sbc hl,de
dust42:
    add hl,hl
    ld a,h
    ld (dustVar15),a
    ld a,(dustVar11)
    ld e,a
    ld b,0x08
    ld c,h
    call dust73
    and a
    adc hl,hl
    jr c,dust45
    jr z,dust45
    ld a,h
    ld (dustVar11),a
    ld a,(dustVar15)
    ld b,a
    ld a,(dustVar9)
    srl a
    call dust81
    ld a,d
    and a
    jr z,dust45
    bit 7,a
    jr nz,dust45
    ld (dustVar9),a
    ld a,(dustPitch)
    ld b,a
    ld a,(dustVar10)
    ld c,a
    ld a,(dustPixelMask)
    bit 6,a
    jr nz,dust43
    bit 3,a
    jr nz,dust44
    jr dust46
dust43:
    bit 3,a
    jr nz,dust46
dust44:
    ld a,c
    sub b
    call c,dust71
    jr dust47
dust45:
    jp LAB_ram_33bc
dust46:
    ld a,c
    add a,b
dust47:
    srl a
    ld c,a
    ld a,(dustVar15)
    ld b,a
    ld a,c
    call dust81
    ld a,d
    and a
    jr nz,dust48
    ld a,(dustPixelMask)
    xor 0x40
    ld (dustPixelMask),a
dust48:
    ld a,d
    cp 0x40
    jr nc,dust45
    ld (dustVar10),a
dust49:
    ld a,(dustRoll)
    and a
    ld a,(dustVar10)
    jr nz,drawParticlesinJumpMode
    cp 0x3F
    jr nc,dust45
drawParticlesinJumpMode:
    cp 0x3F
    jr nc,dust51
    call calcDustParticlePixel
    ld hl,(adrOfParticleAdrTable)
    ld (hl),e
    inc hl
    ld (hl),d
    inc hl
    ld (hl),c
    inc hl
    ld (adrOfParticleAdrTable),hl
    ld a,(numDustParticles)
    inc a
    ld (numDustParticles),a
dust51:
    ld hl,(adrOfCoordinatesTable)
    ld a,(dustPixelMask)
    ld b,a
    ld a,(dustVar9)
    bit 7,b
    jr z,dust52
    or 0x80
dust52:
    ld (hl),a
    inc hl
    ld a,(dustVar10)
    bit 6,b
    jr z,dust53
    or 0x80
dust53:
    ld (hl),a
    inc hl
    ld a,(dustVar11)
    ld (hl),a
    inc hl
    ld a,(dustVar12)
    ld (hl),a
    inc hl
    ld a,(dustVar13)
    ld (hl),a
    inc hl
    ld (adrOfCoordinatesTable),hl
dust54:
    ld a,(dustVar5)
    dec a
    jp z,drawDustParticles
    ld (dustVar5),a
    ld a,(dustPixelMask)
    and 0x3B
    ld b,a
    ld de,(adrOfCoordinatesTable)
    ld a,(de)
    cp 0x80
    jr c,dust55
    and 0x7F
    set 7,b
dust55:
    ld (dustVar9),a
    inc de
    ld a,(de)
    cp 0x80
    jr c,dust56
    and 0x7F
    set 6,b
dust56:
    ld (dustVar10),a
    inc de
    ld a,(de)
    ld (dustVar11),a
    inc de
    ld a,(de)
    ld (dustVar12),a
    inc de
    ld a,(de)
    ld (dustVar13),a
    ld a,b
    ld (dustPixelMask),a
    ld a,(dustVar3)
    dec a
    jp z,dust62
    jr dust58
dust57:
    dec a
    jr nz,dust59
    ld a,(dustPixelMask)
    xor 0x38
    ld (dustPixelMask),a
dust58:
    jp dust8
dust59:
    ld b,a
    ld a,0x01
    ld (dustVar3),a
    dec b
    jr nz,dust60
    ld a,(dustPixelMask)
    xor 0x10
    ld b,a
    and 0x10
    srl a
    ld c,a
    ld a,b
    and 0x08
    add a,a
    or c
    ld c,a
    ld a,b
    and 0xE7
    or c
    ld (dustPixelMask),a
    jr dustSwitchRollnPitch
dust60:
    ld a,(dustPixelMask)
    xor 0x08
    ld b,a
    and 0x10
    srl a
    ld c,a
    ld a,b
    and 0x08
    add a,a
    or c
    ld c,a
    ld a,b
    and 0xE7
    or c
    xor 0x20
    ld (dustPixelMask),a
dustSwitchRollnPitch:
    ld a,(dustRoll)
    ld b,a
    ld a,(dustPitch)
    ld (dustRoll),a
    ld a,b
    ld (dustPitch),a
dust62:
    ld a,(dustVar11)
    ld b,a
    ld a,(dustParticleSpeed)
    cp b
dust63:
    jp nc,LAB_ram_33bc
    call dust81
    srl d
    inc d
    ld a,(dustPixelMask)
    bit 5,a
    jr nz,dust65
    bit 7,a
    jr nz,dust64
    jr dust66
dust64:
    jr dust67
dust65:
    bit 7,a
    jr nz,dust66
    jr dust67
dust66:
    ld a,(dustVar9)
    sub d
    call c,dust72
    jr dust68
dust67:
    ld a,(dustVar9)
    add a,d
    cp 0x77
    jr nc,dust63
dust68:
    ld (dustVar9),a
    jp dust23
; ZX Spectrum: erase_starfield (&7C92)
; Plots the frame's stars (the particle list built by DrawSpaceDust) into the off-screen bitmap; ClearBitmap wipes them again next frame.
drawDustParticles:
    ld hl,dustParticleAdrTable
    ld a,(numDustParticles)
    and a
    ret z
    ld b,a
dust70:
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld c,(hl)
    IF STAR_OCCLUDE
    call dustPlotPixel
    inc hl
    djnz dust70
    ret
    DS 2                             ; keeps the routine the length of the original (5 bytes became 3)
    ELSE
    ld a,(de)
    cpl
    or c
    cpl
    ld (de),a
    inc hl
    djnz dust70
    ret
    ENDIF
; Negates A and flips the dust pixel mask bit 6
dust71:
    neg
    ld b,a
    ld a,(dustPixelMask)
    xor 0x40
    ld (dustPixelMask),a
    ld a,b
    ret
; Negates A and flips the dust pixel mask bit 7
dust72:
    neg
    ld b,a
    ld a,(dustPixelMask)
    xor 0x80
    ld (dustPixelMask),a
    ld a,b
    ret
; Multiplies A by C (B bits, shift-and-add); 16-bit product in HL
dust73:
    ld d,0x00
    ld hl,0x0000
    and a
    jr dust75
; ZX Spectrum: mul_a_by_c_loop (&7CC9)
; The shift-and-add loop of an A x C multiply: each bit of C that is set adds the running multiplicand into HL, which doubles for the next bit.
dust74:
    add a,a
    rl d
dust75:
    rr c
    jr nc,dust76
    ld e,a
    add hl,de
dust76:
    djnz dust74
    ret
; Divides a 16-bit value (A:L) by B with shift-and-subtract, quotient scaled in C
dust77:
    sla l
    rla
    sla l
    rla
    sla l
    rla
    ld c,0xF8
    cp b
    jr nc,dust79
    sla c
dust78:
    sla l
    rla
    jr c,dust79
    cp b
    jr nc,dust79
    sla c
    jr nc,dust80
    jr dust78
dust79:
    sub b
    scf
    rl c
    jr c,dust78
dust80:
    and a
    ret z
; Divides A by B with shift-and-subtract, quotient in D (0xFE seed)
dust81:
    ld d,0xFE
dust82:
    add a,a
    jr c,dust83
    cp b
    jr nc,dust83
    sla d
    ret nc
    jr dust82
dust83:
    sub b
    scf
    rl d
    ret nc
    jr dust82
; Redraws the hyperspace/docking tunnel if its flag is set, after printing the view label
DrawTunnle:
    call printViewPortLabel
    ld a,(tunnelFlag1)
    and a
    ret z
    jr LAB_ram_7106
; Witchspace entry: resets variables and ship slots, clears the screen, starts the tunnel effect
Witchspace:
    ld a,(tunnelFlag2)
    and a
    ret z
    call InitVariables
    call cleanShipSlots
    ld a,(todoLaunchFlag)
    and a
    jr z,normalWitchSpace
    ld ix,sEntityxlo
    xor a
    ld (ix+34),a
    inc a
    call spawnCommandParser
normalWitchSpace:
    call ClearBitmap
    call transferBuffertoScreen
    ld a,0x42
    ld (BYTE_ram_720c),a
    ld a,(sfxFlags2Bitmap)
    or 0x02
    ld (sfxFlags2Bitmap),a
    ld hl,dataLongTunnle
    ld (LAB_ram_7129+1),hl
    ld a,0x10
    ld (varTunnleLength),a
    ld a,0x01
    ld (smc_PatchORat7159+1),a
    ld a,0x15
    ld (smc_PatchJRat715e+1),a
LAB_ram_7106:
    ld a,(tunnelFlag2)
    and a
    jr nz,LAB_ram_7113
    ld a,0x1E
    ld (smc_PatchJRZat714b+1),a
    jr LAB_ram_7118
LAB_ram_7113:
    ld a,0x05
    ld (smc_PatchJRZat714b+1),a
LAB_ram_7118:
    ld a,0x0F
    ld (circleOffsetXhi),a
    ld hl,0x0000
    ld (circleOffsetY),hl
    ld a,(varTunnleLength)
    ld (workTunnleLength),a
LAB_ram_7129:
    ld hl,dataLongTunnle
LAB_ram_712c:
    ld a,(hl)
    dec a
    ld (hl),a
    inc hl
    ld b,a
    ld a,0x01
    call todoCalcTunnleSegments
    ld a,c
    cp 0x04
    jr c,LAB_ram_7147
    cp 0xC8
    jr nc,LAB_ram_7147
    ld (drawradius),a
    push hl
    call CircleEntrypoint1
    pop hl
LAB_ram_7147:
    ld a,(workTunnleLength)
    dec a
smc_PatchJRZat714b:
    jr z,LAB_ram_7152
    ld (workTunnleLength),a
    jr LAB_ram_712c
LAB_ram_7152:
    call drawViewPorttoScreen
    ld a,(BYTE_ram_720c)
    dec a
smc_PatchORat7159:
    cp 0x30
    ld (BYTE_ram_720c),a
smc_PatchJRat715e:
    jr c,LAB_ram_7192
    ld a,(varTunnleLength)
    ld (workTunnleLength),a
    call ClearBitmap
altJrPoint1:
    jr LAB_ram_7129
    ld a,(BYTE_ram_720c)
    dec a
    ld (BYTE_ram_720c),a
    jr z,alt_animated_effect_reset
    ret
altJrPoint2:
    xor a
    ld (tunnelFlag2),a
    ld (tunnelFlag1),a
    ld a,0x10
    ld b,a
    ld hl,dataLongTunnle
LAB_ram_7182:
    ld a,(hl)
    sub 0xBE
    ld (hl),a
    inc hl
    djnz LAB_ram_7182
    call ClearBitmap
    call transferBuffertoScreen
    jp SFXforLeavingHyperspace
LAB_ram_7192:
    xor a
    ld (tunnelFlag2),a
    jr seed_starfield
altJrPoint3:
    xor a
    ld (tunnelFlag2),a
    ret
; ZX Spectrum: alt_animated_effect_reset (&9369)
alt_animated_effect_reset:
    xor a
    ld (tunnelFlag1),a
    ld a,0x08
    ld b,a
    ld hl,dataShortTunnle
LAB_ram_71a7:
    ld a,(hl)
    sub 0xC0
    ld (hl),a
    inc hl
    djnz LAB_ram_71a7
    ret
; ZX Spectrum: seed_starfield (&937B)
; Fills all 16 records of the starfield table with fresh pseudo-random particles (reuses the one-particle regenerate path with narrowed limits).
seed_starfield:
    ld a,0x83
    ld (0x33D0),a
    ld (0x33D5),a
    ld a,0xC9
    ld (LAB_ram_3475),a
    ld a,0x07
    ld (movementspeed),a
    ld hl,(todo_varEscapepod)
    ld de,tblDustCoordinates
    ld b,0x10
LAB_ram_71c9:
    push bc
mi_71CA:
    call SUB_ram_33cf
    pop bc
    djnz LAB_ram_71c9
    ld a,0xBF
    ld (0x33D0),a
    ld a,0x9F
    ld (0x33D5),a
    ld a,0xC3
    ld (LAB_ram_3475),a
    ret
; Shift-and-subtract division of A by B, quotient in C (tunnel segment scaling, probably)
todoCalcTunnleSegments:
    ld c,0xFE
LAB_ram_71e2:
    add a,a
    jr c,LAB_ram_71ed
    cp b
    jr nc,LAB_ram_71ed
    sla c
    ret nc
    jr LAB_ram_71e2
LAB_ram_71ed:
    sub b
    scf
    rl c
    ret nc
    jr LAB_ram_71e2
SFXforLeavingHyperspace:
    xor a
    ld (todoSunRadius),a
    ld a,(sfxFlags2Bitmap)
    or 0x04
    ld (sfxFlags2Bitmap),a
    ret
; Prints the viewport label, draws the laser sights and copies the buffer to the screen
drawViewPorttoScreen:
    call printViewPortLabel
    call LaserSights
    jp transferBuffertoScreen
varTunnleLength:
    db 0x08
workTunnleLength:
    db 0x00
BYTE_ram_720c:
    db 0x00
dataLongTunnle:
    db 0x1E,"!#&(+-0257:<?AD"
dataShortTunnle:
    db 0x10,0x10,0x10,0x18," (08"
; Sets up the docking (or launch) tunnel animation and, if docking, resets controls and pauses
DockingSequence:
    ld a,(todoLaunchFlag)
    and a
    ret nz
    ld hl,dataShortTunnle
    ld (LAB_ram_7129+1),hl
    ld a,0x08
    ld (varTunnleLength),a
    ld a,0x30
    ld (smc_PatchORat7159+1),a
    ld a,0x40
    ld (BYTE_ram_720c),a
    ld hl,0x0101
    ld (tunnelFlag1),hl
    ld a,(todoUnknownStatusFlags)
    and a
    jr z,launchSequence
    ld a,0x38
    ld (smc_PatchJRat715e+1),a
    ld a,0x0C
    ld (movementspeed),a
    xor a
    ld (inputPitch),a
    ld (inputRoll),a
    ld (ecmActiveFlag),a
    ld (CountDownNumberForHyperspace),a
    inc a
    ld (flagPausemode),a
    ld hl,ecmEquipped
    res 7,(hl)
    call ClearBitmap
    call DrawTunnle
    ld b,0x06
LAB_ram_7273:
    push bc
    call ClearBitmap
    call DrawTunnle
    call LaserSights
    call transferBuffertoScreen
    pop bc
    djnz LAB_ram_7273
    ld a,(sfxFlags2Bitmap)
    or 0x08
    ld (sfxFlags2Bitmap),a
    ld b,0x29
todoDockingProcedure:
    push bc
    call ClearBitmap
    call DrawTunnle
    call LaserSights
    call transferBuffertoScreen
    pop bc
    djnz todoDockingProcedure
    xor a
    ld (todoUnknownStatusFlags),a
    call InitVariables
    call loadLARGEAXX
    IFDEF MISSIONS
    call 0x1714                     ; missionsDockedEntry (missions_docked.asm in the LARGEAXX tail); falls back to chkMissions
    ELSE
    call chkMissions
    ENDIF
    call punishCheater
    ld a,0x07
    jp execSelectedKeyFunctions
launchSequence:
    IFDEF MISSIONS
    call mxLaunchEntry              ; missions_flight.asm: loads the flight image the mission state asks for, then loadIndicator
    ELSE
    call loadIndicator
    ENDIF
    ld a,0x04
    ld (todoUnknownStatusFlags),a
    ld a,(sfxFlags2Bitmap)
    or 0x10
    ld (sfxFlags2Bitmap),a
    xor a
    ld (smc_dfcPatchpos),a
    ld (flagCorrectOrientation),a
    ld (Viewdirection),a
    ld (StationEnergy),a
    ld (flagCloakingDeviceActive),a
    ld a,0x32
    ld (smc_PatchJRat715e+1),a
    call drawDashboard
    call sub_2F81
    call SUB_ram_2058
    ld hl,posDataPlanet
    ld b,0x07
    call todo_clearvars
    ld (hl),0x80
    inc hl
    ld (hl),0x01
    ld a,(todo_planet3dCoordZ)
    xor 0x80
    ld (todo_planet3dCoordZ),a
    ld hl,sEntityxlo
    ld b,0x1B
    call todo_clearvars
    ld ix,sEntityxlo
    ld a,0xF0
    ld (ix+6),a
    ld a,0x80
    ld (ix+8),a
    dec a
    ld (ix+14),a
    ld (ix+18),a
    ld (ix+22),a
    ld a,0xF0
    ld (ix+34),a
    call cleanShipSlots
    call UpdateIndicatorBars
    call ClearBitmap
    call DrawTunnle
    ld b,0x24
launchTunnleSequence:
    push bc
    call ClearBitmap
    call DrawTunnle
    ld a,(drawradius)
    dec a
    ld (drawradius),a
    call todoDrawFilledCircle
    call DrawSpaceDust
    call LaserSights
    call transferBuffertoScreen
    pop bc
    djnz launchTunnleSequence
    ld b,0x0B
LAB_ram_7347:
    push bc
    call ClearBitmap
    call moveSunNPlanet
    call DrawTunnle
    call drawPlanetnSun
    call DrawSpaceDust
    call LaserSights
    call transferBuffertoScreen
    pop bc
    djnz LAB_ram_7347
    ld a,0xD8
    ld (smc_dfcPatchpos),a
    xor a
    ld (flagPausemode),a
; Clears five tunnel/input variables and sets the following byte to 0x0C
InitVariables:
    ld b,0x05
    ld hl,irki2_dat1
    call todo_clearvars
    ld (hl),0x0C
; Clears five bytes starting at keybFlags1
todoclearCounter:
    ld b,0x05
    ld hl,keybFlags1
; Zeroes B bytes at HL
todo_clearvars:
    xor a
LAB_ram_7379:
    ld (hl),a
    inc hl
    djnz LAB_ram_7379
    ret
; ZX Spectrum: reset_ship_slots_1_to_7 (&9509)
; Clears ship 0's exploding flag and resets the state byte of ship slots 1-7 (&27 = the size of a slot record).
cleanShipSlots:
    ld ix,sEntityxlo
    res 2,(ix+33)
    xor a
    ld (todoActiveSlots),a
    ld de,0x0027
    ld b,0x07
LAB_ram_738f:
    add ix,de
    ld (ix+34),a
    djnz LAB_ram_738f
    ret
    db ":",0xB2,"-",0xF6,0x08,"2",0xB2,"-",0x06,")",0xC5,0xCD,0xF1,0x1F,0xCD,0xCB
    db "q",0xCD,0xF8,"|",0xCD,0xD1,0x1E,0xC1,0x10,0xF0,0xAF,"2#",0x1C,0xCD,"}"
    db "t",0xCD,"z",0x88,0xCD,"c ",0xCD,"x >",0x07,0xC3,0xDB,"*",0xCD
    db "_",0x88,">",0x04,"2#",0x1C,":",0xB2,"-",0xF6,0x10,"2",0xB2,"-",0xAF
    db "2",0xAE,0xE7,"2jQ2",0x02,0x1C,"29",0x1C,"2",0xCA,"9>"
    db "22sr",0xCD,0x89,0x1F,0xCD,0x81,"/",0xCD,"X !/",0x1C
    db 0x06,0x07,0xCD,0x8C,"t6",0x80,"#6",0x01,":.",0x1C,0xEE,0x80
buf_7406:
    ld (todo_planet3dCoordZ),a
    ld hl,sEntityxlo
    ld b,0x1B
    call sub_748C
    ld ix,sEntityxlo
    ld a,0xF0
    ld (ix+6),a
    ld a,0x80
    ld (ix+8),a
    dec a
    ld (ix+14),a
    ld (ix+18),a
    ld (ix+22),a
    ld a,0xF0
    ld (ix+34),a
    call sub_7492
    call sub_61B5
    call ClearBitmap
    call sub_71CB
    ld b,0x24
loc_743C:
    push bc
    call ClearBitmap
    call sub_71CB
    ld a,(drawradius)
    dec a
    ld (drawradius),a
    call todoDrawFilledCircle
    call sub_6D4E
    call manipulate_drawroutine1
    call transferBuffertoScreen
    pop bc
    djnz loc_743C
    ld b,0x0B
loc_745B:
    push bc
    call ClearBitmap
    call sub_6953
    call sub_71CB
    call sub_689D
    call sub_6D4E
    call manipulate_drawroutine1
    call transferBuffertoScreen
    pop bc
    djnz loc_745B
    ld a,0xD8
    ld (smc_dfcPatchpos),a
    xor a
    ld (flagPausemode),a
    ld b,0x05
    ld hl,hullDummy                     ; stock: dat_90A2, which lies inside the Asp's edge list (a stock quirk: the write zeroes 5 edge bytes); the 128K build writes a scratch buffer instead
    call sub_748C
    ld (hl),0x0C
    ld b,0x05
    ld hl,irki2_8+1
; Zeroes B bytes at HL (same fill loop as todo_clearvars)
sub_748C:
    xor a
loc_748D:
    ld (hl),a
    inc hl
    djnz loc_748D
    ret
; Starts a routine that loads IX with the ship workspace (sEntityxlo); body is hidden in a db run
sub_7492:
    ld ix,sEntityxlo
    db 0xDD
; Two things share this address. `ld sp,MainStackNStrings` makes it the top of the main stack, which grows down into the bytes before it.
; From here up it is the message table that printStringA indexes in flight (zero-terminated strings, same format as stringsTable).
MainStackNStrings:
    db 0x00,0x00,0x00,0x00,0x00,"  ",0x95,0xCE,0x00,"P",0xF2,"SS S"
    db "PA",0xE9,", ",0x9A,0x00
    db 0x00," GAME O",0xFA,"R",0x00,0x00,0x00,0xF2,"FU"
    db 0xE7,0xED,0x00,0x00,0x15,"PLANET NAME"
    db "? ",0x1A,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,"A"
    db "RCHANGEL",0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db "GROSS ",0x06,0xBA,0x0A,"IV",0xDB,"Y",0x00
    db "ECO",0xE3,"MY",0x00
    IFDEF ENHANCED
statusToken:
    db 0xDE,0xF5,0xEC,0x14,0x14,0x14,0x14,0x00   ; "STATUS" (was "LEGAL STATUS"), padded with a control code that prints nothing so the table keeps its token numbers
    ELSE
    db 0xE5,"G",0xE4," ",0xDE,0xF5,0xEC,0x00
    ENDIF
    db 0xF8,0xFB,"NG",0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0xE0,"AD NEW ",0x9A,0x00,0x09,0x0B,0x01,0x08
    db 0x00,0x00,0x00,0x00,0x13,"COMM",0xFF,"D",0xF4,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db " ",0x01,"(Y/N)?",0x02,0x00
    db 0x02,0x06,"l",0x0A," JAMM",0xF4,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,"POPUL",0xF5,"I",0xDF,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    db 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
SUB_ram_761a:
    ld iy,tableUnkownFacedata
    ld b,(ix+12)
    ld c,(ix+20)
    ld d,(ix+14)
    ld e,(ix+18)
    call diff_of_products
    ld (ix+22),h
    ld (iy+1),h
    ld b,(ix+14)
    ld (iy+17),b
    ld c,(ix+16)
    ld (iy+3),c
    ld d,(ix+10)
    ld e,(ix+20)
    ld (iy+15),e
    call diff_of_products
    ld (ix+24),h
    ld (iy+7),h
    ld b,(ix+10)
    ld (iy+5),b
    ld c,(ix+18)
    ld (iy+9),c
    ld d,(ix+12)
    ld (iy+11),d
    ld e,(ix+16)
    call diff_of_products
    ld (ix+26),h
    ld (iy+13),h
    ret
; ZX Spectrum: diff_of_products (&AF22)
; In: B, C = x1, x2; D, E = y1, y2, all sign-magnitude bytes. Out: HL = 2*(y1*y2 - x1*x2) as a sign-magnitude word (saturating at &FFFF).
; One axis of a cross product; init_ship_calculations uses it to build the side vector from the nose and roof vectors.
diff_of_products:
    sla b
    rra
    xor c
    sla c
    and 0x80
    ld h,a
    sla d
    rra
    xor e
    sla e
    and 0x80
    xor h
    sla h
    rra
    xor 0x80
    push af
    push de
    call mult_b_c
    pop bc
    push hl
    call mult_b_c
    pop de
    pop af
    bit 6,a
    jr z,LAB_ram_769f
    add hl,de
    jr nc,LAB_ram_76ac
    ld hl,0xFFFF
    jr LAB_ram_76ac
LAB_ram_769f:
    ex de,hl
    and a
    sbc hl,de
    jr nc,LAB_ram_76ac
    add hl,de
    ex de,hl
    and a
    sbc hl,de
    xor 0x80
LAB_ram_76ac:
    rla
    rr h
    rr l
    ret
    db 0xDD,0xE5,0xDD,"!",0x00,0x00,"G",0xC5,0xD5,0xC5,0xD5,0xC5,0xD5,"C",0xCD,0x9B
    db "Z",0xEB,0xDD,0x19,0xD1,0xC1,"B",0xCD,0x9B,"Z",0x1E,0x00
    db "U",0xDD,0x19,"lc0",0x01,"#"
LAB_ram_76d6:
    pop bc
    pop de
    push hl
    ld b,d
    call mult_b_c
    ld e,0x00
    ld d,l
    add ix,de
    pop de
    ld l,h
    ld h,0x00
    jr nc,LAB_ram_76e9
    inc hl
LAB_ram_76e9:
    add hl,de
    pop bc
    pop de
    ld c,d
    push hl
    call mult_b_c
    pop de
    add hl,de
    pop ix
    ret
; Divides HL:A by DE into a 16-bit quotient in BC: the dividend is doubled and DE subtracted when it fits, 16 times, with a marker bit
; (&FFFE) in BC ending the loop. BC = (HL + A/256) * &10000 / DE, so it overflows once HL >= DE. No normalisation or saturation, unlike div_de_h.
div_hl_a_de:
    ld bc,0xFFFE
LAB_ram_76f9:
    add a,a
    rl l
    rl h
    jr c,LAB_ram_770c
    sbc hl,de
    jr nc,LAB_ram_770f
    add hl,de
    sla c
    rl b
    ret nc
    jr LAB_ram_76f9
LAB_ram_770c:
    and a
    sbc hl,de
LAB_ram_770f:
    scf
    rl c
    rl b
    ret nc
    jr LAB_ram_76f9
; ZX Spectrum: minus_de_plus_hl_div_2 (&AFC9)
; As de_plus_hl_div_2 with the sign of DE flipped first: HL = (HL - DE) / 2.
minus_de_plus_hl_div_2:
    ld a,d
    xor 0x80
    ld d,a
; ZX Spectrum: de_plus_hl_div_2 (&AFCD)
; In: HL, DE = sign-magnitude words (sign in bit 7 of H and D). Out: HL = (HL + DE) / 2, B = sign of the result.
de_plus_hl_div_2:
    ld a,h
    xor d
    ld b,h
    ld c,d
    res 7,h
    res 7,d
    and 0x80
    jr nz,LAB_ram_772a
    add hl,de
    jr LAB_ram_7734
LAB_ram_772a:
    sbc hl,de
    jr nc,LAB_ram_7734
    add hl,de
    ex de,hl
    and a
    sbc hl,de
    ld b,c
LAB_ram_7734:
    srl h
    rr l
    bit 7,b
    ret z
    set 7,h
    ret
dat_773E:
    db 0x00,0x00
zoom:
    db 0x00
dat_7741:
    db 0x00,0x00
workY:
    db 0x00,0x00
workZ:
    db 0x00,0x00
workXsign:
    db 0x00
workYsign:
    db 0x00
workZsign:
    db 0x00
; Ship face visibility loop (partly in a db run): decides which faces of a ship are drawn
parseFaces:
    push ix
    push iy
    push iy
    ex (sp),ix
    pop hl
    ld (dat_773E),hl
    ld d,(ix+17)
    ld e,(ix+16)
    add ix,de
    ld de,todo_tableforedges
SUB_ram_7761:
    ld a,(iy+19)
    ld (zoom),a
    ld a,(iy+5)
    and a
    ld iy,tableUnkownFacedata
    jr nz,LAB_ram_7775
    inc a
    ld (de),a
    jr LAB_ram_77d0
LAB_ram_7775:
    push af
    push de
    ld a,(ix+3)
    and 0x1F
    cp 0x1F
    jr z,LAB_ram_778b
    ld b,a
    ld a,(varCoordinate)
    cp b
    jr c,LAB_ram_778b
    pop de
    xor a
    jr LAB_ram_77c5
LAB_ram_778b:
    push iy
    ld hl,(dat_773E)
    push hl
    call line_of_sight_vector_component
    ld (workXsign),a
    ld (dat_7741),hl
    call line_of_sight_vector_component
    ld (workYsign),a
    ld (workY),hl
    call line_of_sight_vector_component
    ld (workZsign),a
    ld (workZ),hl
    pop hl
    push ix
    ld iy,dat_7741
    ld ix,workXsign
    call calculate_visibility
    pop ix
    pop iy
    pop de
    xor a
    sla h
    jr nc,LAB_ram_77c5
    inc a
LAB_ram_77c5:
    ld (de),a
    inc de
    ld bc,0x0004
    add ix,bc
    pop af
    dec a
    jr nz,LAB_ram_7775
LAB_ram_77d0:
    pop iy
    pop ix
    ret
; ZX Spectrum: calculate_visibility (&BD5F)
; Face visibility: works out the face normal (IX) . ship orientation dot products and combines them with the ship's position.
; A negative result means the face points at the viewer. The BBC rotates the ship's position into the ship's own frame; this build rotates the
; normal instead, as the Spectrum does.
calculate_visibility:
    ld e,(iy+1)
    ld c,(iy+0)
    ld a,(ix+0)
    call mult_2_A_EC
    push hl
    ld e,(iy+3)
    ld c,(iy+2)
    ld a,(ix+1)
    call mult_2_A_EC
    push hl
    ld e,(iy+5)
    ld c,(iy+4)
    ld a,(ix+2)
    call mult_2_A_EC
    pop de
    call de_plus_hl_div_2
    adc hl,hl
    bit 7,b
    jr z,LAB_ram_7807
    set 7,h
LAB_ram_7807:
    pop de
    jp de_plus_hl_div_2
; ZX Spectrum: mult_2_A_EC (&BD95)
; In: A = sign-magnitude byte X (bit 7 = sign), E = sign and high byte of a sign-magnitude word Y, C = its low byte.
; Out: H = sign of X*Y, L = magnitude of 2*X*Y/256. Used for the face visibility test.
mult_2_A_EC:
    ld b,a
    sla b
    and 0x80
    xor e
    ld e,a
    call mult_b_c_msb
    ld d,e
    ld e,a
    ld c,d
    res 7,c
    push de
    call mult_b_c
    pop de
    ld a,d
    ld d,0x00
    add hl,de
    add hl,hl
    rla
    rr h
    rr l
    ret
; In: IX = a face's normal, IY = the ship calculation table. Out: A = normal . orientation vector (one component, sign-magnitude), HL = the
; same plus the ship's position coordinate. Part of the face visibility test (calculate_visibility).
line_of_sight_vector_component:
    call face_normal_component
    pop bc
    ex (sp),ix
    ld e,(ix+0)
    ld d,(ix+1)
    ld a,(ix+2)
    inc ix
    inc ix
    inc ix
    ex (sp),ix
    push bc
    ld c,a
    ld a,(zoom)
    sla l
    push hl
    ld b,a
    inc b
LAB_ram_784b:
    srl l
    djnz LAB_ram_784b
    rl l
    ld a,c
    xor h
    sla h
    rla
    jr c,LAB_ram_785b
    add hl,de
    jr LAB_ram_786a
LAB_ram_785b:
    ex de,hl
    and a
    sbc hl,de
    jr nc,LAB_ram_786a
    add hl,de
    ex de,hl
    and a
    sbc hl,de
    ld a,c
    xor 0x80
    ld c,a
LAB_ram_786a:
    sla c
    rr h
    rr l
    pop de
    ld a,e
mi_7872:
    rl d
    rra
    ret
drawLaserVar1:
    db 0x00
todoLaserVar1:
    db 0x00
; Checks whether a scooped canister is within range of the ship and not game-over, then picks it up
TryScoopGood:
    ld a,(GameOverFlag)
    and a
    ret nz
    ld d,0x00
    ld e,(iy+1)
    bit 0,(ix+38)
    jr z,LAB_ram_7890
    ld a,(ix+37)
    and a
    jr nz,LAB_ram_7890
    ld d,0x01
LAB_ram_7890:
    bit 1,(ix+38)
    jr z,LAB_ram_7898
    ld e,0xB4
LAB_ram_7898:
    ld l,(ix+0)
    ld h,(ix+1)
    sbc hl,de
    ret nc
    and a
    ld l,(ix+3)
    ld h,(ix+4)
    sbc hl,de
    ret nc
    and a
    ld l,(ix+6)
    ld h,(ix+7)
    sbc hl,de
    ret nc
    ld a,(ix+8)
    and 0x7F
    ret nz
    bit 1,(ix+38)
    jr z,todoCollisionCheck
    bit 7,(ix+5)
    jp z,ApplyCollisionDamage
    ld a,(fuelScoops)
    and a
    jp z,ApplyCollisionDamage
    xor a
    ld (ix+34),a
    call chkEntityWasMissiletarget
    ld a,(cargoSpaceFree)
    and a
    jr z,ApplyCollisionDamage
    ld a,(iy+0)
    and 0xF0
    jr z,fsGetRandomGood
    rrca
    rrca
    rrca
    rrca
    inc a
    jr AddScoopedGoodToInventory
fsGetRandomGood:
    ld a,(aspMissionState)
    sub 0x03
    jr nz,AddRandomGoodToInventory
    ld (aspMissionState),a
    dec a
    jr AddScoopedGoodToInventory
AddRandomGoodToInventory:
    call getRandomNumber
    and 0x07
AddScoopedGoodToInventory:
    jp storeScoopedGood
todoCollisionCheck:
    bit 2,(ix+38)
    jr z,ApplyCollisionDamage
    bit 7,(ix+14)
    jr z,setImKilledFlag0xf
    bit 7,(ix+8)
    jr nz,setImKilledFlag0xf
    bit 2,(ix+33)
    jr nz,setImKilledFlag0xf
    ld a,(ix+10)
    add a,a
    cp 0xDC
    jr nc,setImKilledFlag0xf
    ld b,a
    ld a,(ix+12)
    add a,a
    cp 0xDC
    jr nc,setImKilledFlag0xf
    cp 0x3C
    jr nc,DamageMyFrontshield
    ld a,b
    cp 0x3C
    jr nc,DamageMyFrontshield
    ld a,0x01
    ld (flagCorrectOrientation),a
    ret
DamageMyFrontshield:
    ld hl,sfxFlags1Bitmap
    set 6,(hl)
    ld hl,movementspeed
    ld a,(damageToFrontShield)
    add a,0x0C
    add a,(hl)
    add a,(hl)
    ld (damageToFrontShield),a
    ret
ApplyCollisionDamage:
    ld b,(iy+1)
    xor a
    ld (ix+34),a
    bit 6,(ix+38)
    jr z,SFXandDamageForCollision
    ld a,(aspMissionState)
    and a
    jr z,SFXandDamageForCollision
    xor a
    ld (aspMissionState),a
SFXandDamageForCollision:
    ld hl,sfxFlags1Bitmap
    set 2,(hl)
    bit 7,(ix+8)
    jr z,collisionDamagesFronshield
    ld a,(damageToRearShield)
    add a,b
    ld (damageToRearShield),a
    jr chkEntityWasMissiletarget
setImKilledFlag0xf:
    ld a,0x0F
    ld (GameOverFlag),a
    ret
collisionDamagesFronshield:
    ld a,(damageToFrontShield)
    add a,b
    ld (damageToFrontShield),a
; Flags ships that had this one as missile target; drops the player's lock if it was the target
chkEntityWasMissiletarget:
    ld a,(missileTargetEntityNr)
    ld h,a
    push iy
    ld iy,sEntityxlo
    ld de,0x0027
    ld b,0x07
mslchkTargetLoop:
    add iy,de
    ld a,(iy+34)
    and a
    jr z,mslchkNextEntity
    ld a,(iy+37)
    cp h
    jr nz,mslchkNextEntity
    bit 0,(ix+38)
    jr z,mslchkNextEntity
    set 4,(iy+32)
mslchkNextEntity:
    djnz mslchkTargetLoop
    pop iy
    ld a,(missileLockState)
    cp 0x02
    ret nz
    ld a,(missileTargetEntity)
    sub h
    ret nz
    ld (missileLockState),a
    ld hl,msgTargetLost
    set 7,(hl)
    ret
; ZX Spectrum: reset_all_ships (&B618)
; Resets all ship slots and performs two ship actions at the start of the arrival animation.
SpawnMyRemains:
    ld hl,sfxFlags1Bitmap
    set 2,(hl)
    xor a
    ld (Viewdirection),a
    ld ix,0x1A19
    ld de,0x0027
    ld b,0x08
mkKillAllSlotsLoop:
    add ix,de
    ld (ix+34),a
    djnz mkKillAllSlotsLoop
    ld a,0x16
    call spawnCommandParser
    ld a,0x15
    jp spawnCommandParser
; Laser firing and cooldown: checks the temperature, key flag and fitted laser, then fires
FiringLaser:
    ld a,(todoLaserVar1)
    ld c,a
    xor a
    ld (todoLaserVar1),a
    ld a,(Lasertemp)
    cp 0x02
    jr nc,cooldownLaser
    ld a,0x02
cooldownLaser:
    sub 0x02
    ld (Lasertemp),a
    ld hl,keybFlags4CounterNstringNumber
    bit 0,(hl)
    ret z
    res 0,(hl)
    cp 0x90
    ret nc
    ld b,a
    ld a,(Viewdirection)
    ld hl,laserTypes
    ld d,0x00
    ld e,a
    add hl,de
    ld a,(hl)
    and a
    ret z
    ld e,c
    ld c,a
    dec a
    jr nz,LAB_ram_7a1a
    ld d,0x01
LAB_ram_7a1a:
    sub 0x03
    jr nz,LAB_ram_7a20
    ld d,0x07
LAB_ram_7a20:
    ld a,e
    and e
    ld a,0x01
    ld (todoLaserVar1),a
    jr z,LAB_ram_7a2e
    ld a,(todoLaserVar2)
    and d
    ret nz
LAB_ram_7a2e:
    ld a,(todoLaserVar3)
    inc a
    ld (todoLaserVar3),a
    ld hl,sfxFlags1Bitmap
    set 4,(hl)
    ld a,c
    sub 0x03
    ld a,0x0F
    jr c,addLaserTemp
    jr z,addmoreLaserTemp
    add a,0x1B
addmoreLaserTemp:
    add a,0x08
addLaserTemp:
    ld c,a
    ld a,d
    dec a
    and 0x01
    rla
    add a,0x08
    add a,b
    cp 0xA0
    jr c,storeLaserTemp
    ld a,0xA0
storeLaserTemp:
    ld (Lasertemp),a
    ld a,(shipInCrosshair)
    and a
    jp z,nothingInCrosshairDrawLaser
    dec a
    sub 0x09
    cpl
    ld ix,sEntityxlo
    ld de,0x0027
searchWhomIsHit:
    dec a
    jr z,laserHit
    add ix,de
    jr searchWhomIsHit
laserHit:
    set 2,(ix+33)
    ld hl,sfxFlags1Bitmap
    set 3,(hl)
    bit 2,(ix+38)
    jr nz,nothingInCrosshairDrawLaser
    bit 5,(ix+32)
    jr nz,nothingInCrosshairDrawLaser
    ld a,(ix+37)
    ld b,a
    sub 0x0E
    jr nc,applyLaserDamagetoEntity
    and 0x01
    add a,0x06
applyLaserDamagetoEntity:
    rla
    sla b
    rra
    ld (ix+37),a
    ld a,(ix+34)
    cp 0xFF
    jr z,nothingInCrosshairDrawLaser
    sub c
    IFDEF MISSIONS
    call mxLaserHook                ; missions_flight.asm: the Constrictor ignores weak lasers
    ELSE
    ld (ix+34),a
    ENDIF
    jr z,targetisKilled
    jr nc,nothingInCrosshairDrawLaser
targetisKilled:
    xor a
    dec a
    set 4,(ix+32)
    ld (ix+34),a
    bit 6,(ix+38)
    jr z,spawnLeftovers
    ld a,(aspMissionState)
    and a
    jr z,spawnLeftovers
    cp 0x03
    jr z,spawnLeftovers
    ld a,0x03
    ld (aspMissionState),a
    add a,a
    jr lsGotoSpawnCommandParser
spawnLeftovers:
    ld h,(ix+36)
    ld l,(ix+35)
    ld a,(hl)
    and 0x0F
    ld a,0x06
    jr nz,lsGotoSpawnCommandParser
    ld de,0x0007
    add hl,de
    ld a,(hl)
    cp 0x55
    ld a,0x05
    jr nc,lsGotoSpawnCommandParser
    ld a,(hl)
    cp 0x3C
    jr nz,nothingInCrosshairDrawLaser
    ld a,c
    cp 0x32
    jr nz,nothingInCrosshairDrawLaser
    ld a,0x08
lsGotoSpawnCommandParser:
    call spawnCommandParser
nothingInCrosshairDrawLaser:
    call getRandomNumber
    ld b,a
    and 0x0C
    ld c,a
    ld (drawLaserVar1),a
    ld a,b
    and 0x03
    or 0x01
    sub 0x01
    ld d,a
    rlc b
    rlc b
    ld a,b
    and 0x03
    or 0x01
    sub 0x01
    ld e,a
    push de
    ld a,c
    or 0x03
    ld c,a
    ld hl,0x543F
    push hl
    call drawLaserLine
    pop hl
    pop de
    ld a,(drawLaserVar1)
    or 0x01
    ld c,a
    push de
    call drawLaserLine
    pop de
    ld hl,0x403F
    ld a,(drawLaserVar1)
    or 0x03
    ld c,a
    push hl
    push de
    call drawLaserLine
    pop de
    pop hl
    ld a,(drawLaserVar1)
    or 0x01
    ld c,a
    jp drawLaserLine
; ZX Spectrum: rand_no (&B799)
; Out: A = pseudo-random byte (a 16-bit seed folded back into itself with adc; the high byte is returned).
getRandomNumber:
    push hl
    push bc
    ld hl,(storedRandomSeed)
    ld a,h
    adc a,a
    ld b,a
    adc a,l
    ld h,a
    ld l,b
    ld (storedRandomSeed),hl
    pop bc
    pop hl
    ret
storedRandomSeed:
    db "b",0xF5
emptyShields:
    xor a
    ld (shipFrontShieldEnergy),a
    ld (shipRearShieldEnergy),a
    ret
; Per-frame laser and ECM handling: fires the laser if fitted and processes the ECM key
handleLaser:
    ld a,(GameOverFlag)
    and a
    jr nz,emptyShields
    ld a,(Viewdirection)
    cp 0x04
    ret nc
    ld hl,laserTypes
    ld d,0x00
    ld e,a
    add hl,de
    ld a,(hl)
    and a
    jr z,LAB_ram_7b79
    call LaserSights
    call FiringLaser
LAB_ram_7b79:
    ld a,(Missionflag)
    bit 7,a
    jr z,doActivateECM
    ld a,(ThargonMissionVar)
    cp 0x04
    ret z
doActivateECM:
    ld hl,keybFlags4CounterNstringNumber
    ld b,(hl)
    res 4,(hl)
    ld a,(ecmEquipped)
    ld c,a
    ld a,(ecmActiveFlag)
    and a
    jr z,ECMSetDurationofEffect
    dec a
    ld (ecmActiveFlag),a
    jr nz,aePlayECMSFX
    res 7,c
aePlayECMSFX:
    ld hl,sfxFlags1Bitmap
    set 5,(hl)
    ld a,c
    and a
    ret z
    ld (ecmEquipped),a
    ld a,(todoLaserVar3)
    inc a
    ld (todoLaserVar3),a
    ret
; Draws the four lines of the laser crosshair
LaserSights:
    ld hl,0x0800
    ld de,0x1000
    ld c,0x0A
    call drawLaserLine
    ld hl,0x0800
    ld de,0x1000
    ld c,e
    call drawLaserLine
    ld hl,0x0010
    ld de,0x0008
    ld c,d
    call drawLaserLine
    ld hl,0x0010
    ld de,0x0008
    ld c,0x05
    call drawLaserLine
    ret
ECMSetDurationofEffect:
    ld a,c
    and a
    ret z
    bit 4,b
    ret z
    or 0x80
    ld (ecmEquipped),a
    ld a,0x0A
    ld (ecmActiveFlag),a
    ret
line_lookup_table:
    db 0x00,0x04,0x02,0x03,0x00,0x04,0x06,0x05,0x00,0x08,0x02,0x01,0x00,0x08,0x06,0x07
    db 0x00,0x00,0x00,0x02,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x02,0x02,0x01,0x02,0x02
    db 0x00,0x00,0x00,0x00,0x00,0x02,0x01,0x02,0x02,0x02,0x00,0x00,0x00,0x02,0x02,0x01
    db 0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x02,0x02,0x01,0x02,0x02,0x00,0x00,0x00,0x02
    db 0x00,0x02,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x02,0x02,0x01,0x02,0x02,0x00,0x00
BYTE_ram_7c3d:
    db 0x00,0x00
BYTE_ram_7c3f:
    db 0x00,0x00
; Draws one laser line; sets the draw flag then shares clipping code with SUB_ram_7c45
drawLaserLine:
    ld a,0x01
    jr LAB_ram_7c46
; Draws or erases a line with clipping against the view; carry out of the shared line routine
SUB_ram_7c45:
    xor a
LAB_ram_7c46:
    ld (flagDrawLaserline),a
    ld a,h
    and e
    inc a
    ret z
    ld a,l
    and d
    inc a
    ret z
    push de
    push hl
    push bc
    ld a,c
    and 0x0C
    ld b,a
    ld a,d
    cp 0x80
    jr c,LAB_ram_7c5f
    set 0,b
LAB_ram_7c5f:
    ld a,e
    cp 0x40
    jr c,LAB_ram_7c66
    set 1,b
LAB_ram_7c66:
    ld a,c
    and 0x03
    add a,a
    add a,a
    ld c,a
    ld a,h
    cp 0x80
    jr c,LAB_ram_7c73
    set 0,c
LAB_ram_7c73:
    ld a,l
    cp 0x40
    jr c,LAB_ram_7c7a
    set 1,c
LAB_ram_7c7a:
    ld hl,line_lookup_table
    ld a,b
    and 0x03
    jr z,LAB_ram_7cc0
    ld a,b
    add a,l
    ld l,a
    jr nc,LAB_ram_7c88
    inc h
LAB_ram_7c88:
    ld b,(hl)
    ld hl,line_lookup_table
    ld a,c
    and 0x03
    jr z,LAB_ram_7cb0
    ld a,c
    add a,l
    ld l,a
    jr nc,LAB_ram_7c97
    inc h
LAB_ram_7c97:
    ld c,(hl)
    ld a,b
    add a,a
    add a,a
    add a,a
    add a,c
    ld hl,line_lookup_table
    add a,0x07
    add a,l
    jr nc,LAB_ram_7ca6
    inc h
LAB_ram_7ca6:
    ld l,a
    ld a,(hl)
    and a
    jp nz,LAB_ram_7d7e
    pop hl
    pop hl
    pop hl
    ret
LAB_ram_7cb0:
    pop bc
    pop de
    pop hl
    ld a,c
    add a,a
    add a,a
    srl c
    srl c
    or c
    and 0x0F
    ld c,a
    jr LAB_ram_7cc8
LAB_ram_7cc0:
    ld a,c
    and 0x03
    jr z,todo_drawJumpEntrypoint1
    pop bc
    pop hl
    pop de
LAB_ram_7cc8:
    ld b,c
    call todo_calculationstuff
    call CalcPointAdressinBitmap
    jp todo_linecalchelper
todo_drawJumpEntrypoint1:
    pop bc
    pop hl
    pop de
    ld b,c
    call todo_calculationstuff
    call CalcPointAdressinBitmap
    inc h
    inc l
    ld d,b
    bit 4,b
    ld a,l
    jr z,todo_drawJumpEntrypoint2
    ld a,h
todo_drawJumpEntrypoint2:
    exx
    cp 0x02
    jr nc,LAB_ram_7cec
    ld a,0x02
LAB_ram_7cec:
    dec a
    ld d,a
    exx
    ld a,d
    and 0x1C
    cp 0x0E
    jr nc,manipulate_drawroutine2
    cp 0x06
; Patches the line-drawing code (opcode and address bytes) to suit the line's length and slope
manipulate_drawroutine1:
    jr nc,LAB_ram_7d06
    cp 0x02
    ld hl,0x012D
    ld de,0xC624   ; opcode bytes &C6 (add a,n) and &24 (inc h) for the self-patched line routines, not a screen address
    jr c,smc_md1_patchcommands
    jr LAB_ram_7d10
LAB_ram_7d06:
    cp 0x0A
    ld hl,0x092C
    ld de,0xC624   ; opcode bytes &C6 (add a,n) and &24 (inc h) for the self-patched line routines, not a screen address
    jr c,smc_md1_patchcommands
LAB_ram_7d10:
    set 4,d
    inc e
smc_md1_patchcommands:
    ld a,h
    ld (dvRotatePixmask+1),a
    ld (dh2RotatePixmask+1),a
    ld a,l
    ld (dvgetscrbyte),a
    ld (dh2SetnextByteadr),a
    ld a,d
    ld (smc_dvpatchadr5),a
    ld (smc_dhpatchadr6),a
    ld a,e
    ld (smc_dvpatchadr7),a
    ld (dh2nextPixellineBlock),a
    exx
    ld a,(flagDrawLaserline)
    and a
    jp nz,LAB_ram_803d
    jp drawVerticals
manipulate_drawroutine2:
    cp 0x16
    jr nc,LAB_ram_7d4a
    cp 0x12
    ld hl,0xC624   ; opcode bytes &C6 (add a,n) and &24 (inc h) for the self-patched line routines, not a screen address
    ld de,0x012D
    jr c,smc_md2_patchcommands
    jr LAB_ram_7d54
LAB_ram_7d4a:
    cp 0x1A
    ld hl,0xC624   ; opcode bytes &C6 (add a,n) and &24 (inc h) for the self-patched line routines, not a screen address
    ld de,0x092C
    jr c,smc_md2_patchcommands
LAB_ram_7d54:
    set 4,h
    inc l
smc_md2_patchcommands:
    ld a,h
    ld (dh1nextPixelline),a
    ld (dh3nextPixelline),a
    ld a,l
    ld (dh1nextPixellineBlock),a
    ld (dh3nextPixellineBlock),a
    ld a,d
    ld (dh1RotatePixmask+1),a
    ld (dh3RotatePixmask+1),a
    ld a,e
    ld (dh1SetnextByteadr),a
    ld (dh3SetnextByteadr),a
    exx
    ld a,(flagDrawLaserline)
    and a
    jp nz,gotodrawHPB3
    jp drawHorizontals
LAB_ram_7d7e:
    pop hl
    push hl
    dec a
    jr nz,LAB_ram_7dcb
    bit 0,b
    jr z,LAB_ram_7dbc
    ld a,l
    and 0x0C
    srl l
    srl l
    or l
    ld b,a
    ld hl,drawHorizontalsPixelbyte2
    call todo_calculationstuff
    ld (BYTE_ram_7c3f),bc
    pop bc
    pop hl
    ld b,c
    call todo_calculationstuff
    ld de,(BYTE_ram_7c3f)
    ld a,b
    xor d
    and 0x10
    jr z,LAB_ram_7dac
    ld e,0xFF
LAB_ram_7dac:
    bit 4,b
    jr z,LAB_ram_7db4
    ld a,c
    sub e
    jr LAB_ram_7db6
LAB_ram_7db4:
    ld a,e
    sub c
LAB_ram_7db6:
    jp c,todoStartpointoflinedrawing
    jp LAB_ram_7ea6
LAB_ram_7dbc:
    pop bc
    pop hl
    ld b,c
    call todo_calculationstuff
    ld a,e
    cp 0x40
    jp nc,todoStartpointoflinedrawing
    jp LAB_ram_7ea6
LAB_ram_7dcb:
    ld (BYTE_ram_7c3d),bc
    bit 0,b
    jr z,LAB_ram_7df2
    pop bc
    pop de
    pop hl
    push de
    push hl
    ld a,c
    srl a
    srl a
    sla c
    sla c
    or c
    and 0x0F
    ld c,a
    ld l,c
    push bc
    ld bc,(BYTE_ram_7c3d)
    ld a,b
    ld b,c
    ld c,a
    ld (BYTE_ram_7c3d),bc
LAB_ram_7df2:
    ld a,b
    add a,c
    cp 0x07
    ld h,0x00
    jr c,LAB_ram_7e26
    cp 0x0C
    ld h,0x03
    jr nc,LAB_ram_7e26
    ld a,b
    xor c
    dec h
    cp 0x08
    jr nc,LAB_ram_7e26
    dec h
    cp 0x04
    jr c,LAB_ram_7e26
    cp 0x05
    jr z,LAB_ram_7e20
    ld a,b
    xor 0x06
    ld h,0x03
    and c
    jr z,LAB_ram_7e26
    cp 0x06
    jr z,LAB_ram_7e26
    ld h,0x00
    jr LAB_ram_7e26
LAB_ram_7e20:
    ld a,b
    cp 0x02
    jr nz,LAB_ram_7e26
    inc h
LAB_ram_7e26:
    ld a,l
    and 0x0C
    or h
    ld b,a
    ld hl,drawHorizontalsPixelbyte2
    call todo_calculationstuff
    ld (BYTE_ram_7c3f),bc
    pop bc
    pop hl
    ld b,c
    call todo_calculationstuff
    ld de,(BYTE_ram_7c3f)
    ld a,b
    xor d
    and 0x10
    jr z,LAB_ram_7e47
    ld e,0xFF
LAB_ram_7e47:
    ld hl,(BYTE_ram_7c3d)
    bit 4,b
    jr z,LAB_ram_7e54
    bit 1,h
    jr nz,LAB_ram_7e58
    jr LAB_ram_7e62
LAB_ram_7e54:
    bit 1,h
    jr nz,LAB_ram_7e62
LAB_ram_7e58:
    ld a,e
    sub c
    jr nc,LAB_ram_7e66
LAB_ram_7e5c:
    bit 1,h
    jr z,LAB_ram_7ea6
    jr todoStartpointoflinedrawing
LAB_ram_7e62:
    ld a,c
    sub e
    jr c,LAB_ram_7e5c
LAB_ram_7e66:
    pop hl
    ret
todoStartpointoflinedrawing:
    pop de
    push bc
    ld a,e
    sub 0x40
    ld e,a
    ld l,b
    bit 4,b
    jr nz,LAB_ram_7e78
    call mult_a_c
    jr LAB_ram_7e7c
LAB_ram_7e78:
    ld b,c
    call todo_anothersubbeforedraw
LAB_ram_7e7c:
    ld a,l
    rra
    rra
    xor l
    and 0x02
    jr nz,LAB_ram_7ea0
    ld a,d
    sub c
    ld d,a
    pop bc
    jr nc,LAB_ram_7e91
    neg
    ld d,a
    ld a,b
    xor 0x02
    ld b,a
LAB_ram_7e91:
    ld e,0x3F
    ld a,d
    cp 0x80
    jr c,LAB_ram_7e9a
    ld d,0x7F
LAB_ram_7e9a:
    call CalcPointAdressinBitmap
    jp todo_linecalchelper
LAB_ram_7ea0:
    ld a,d
    add a,c
    ld d,a
    pop bc
    jr LAB_ram_7e91
LAB_ram_7ea6:
    pop de
    push bc
    ld a,d
    sub 0x80
    ld d,a
    ld l,b
    bit 4,b
    jr z,LAB_ram_7eb6
    call mult_a_c
    jr LAB_ram_7eba
LAB_ram_7eb6:
    ld b,c
    call todo_anothersubbeforedraw
LAB_ram_7eba:
    ld a,l
    rra
    rra
    xor l
    and 0x01
    jr nz,LAB_ram_7ede
    ld a,e
    sub c
    ld e,a
    pop bc
    jr nc,LAB_ram_7ecf
    neg
    ld e,a
    ld a,b
    xor 0x01
    ld b,a
LAB_ram_7ecf:
    ld d,0x7F
    ld a,e
    cp 0x40
    jr c,LAB_ram_7ed8
    ld e,0x3F
LAB_ram_7ed8:
    call CalcPointAdressinBitmap
    jp todo_linecalchelper
LAB_ram_7ede:
    ld a,e
    add a,c
    ld e,a
    pop bc
    jr LAB_ram_7ecf
; ZX Spectrum: mult_a_c (&B2F0)
; In: A, C. Out: C = A*C/256 rounded to nearest (mult_b_c, then &80 is added before taking the high byte). DE and HL are kept.
mult_a_c:
    push de
    push hl
    ld b,a
    call mult_b_c
    ld de,0x0080
    add hl,de
    ld c,h
    pop hl
    pop de
    ret
; Calls SUB_ram_5bf2 with C=0xFE, E=0 while preserving DE
todo_anothersubbeforedraw:
    ld c,0xFE
    push de
    ld e,0x00
    call SUB_ram_5bf2
    pop de
    ret
; Converts a signed view point (BC, DE) to a bitmap screen address and pixel mask
CalcPointAdressinBitmap:
    push bc
    push de
    exx
    pop bc
    pop de
    bit 1,d
    jr nz,LAB_ram_7f0a
    ld a,0x7F
    add a,b
    jr LAB_ram_7f0d
LAB_ram_7f0a:
    ld a,0x7F
    sub b
LAB_ram_7f0d:
    ld b,a
    bit 0,d
    jr z,getPixelAddrrEntrypoint1
    ld a,0x3F
    add a,c
    jr getPixelAddrrEntrypoint2
getPixelAddrrEntrypoint1:
    ld a,0x3F
    sub c
getPixelAddrrEntrypoint2:
    ld c,b
    ld h,0x02
    ld l,a
    add hl,hl
    inc h
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld a,c
    srl a
    srl a
    add a,l
    ld l,a
    ld a,c
    and 0x03
    inc a
    ld b,a
    ld c,0x11
gpaloop:
    rrc c
    djnz gpaloop
    ld b,e
    ld e,0x80
    exx
    ret
todo_linecalchelper:
    push bc
    ld hl,drawHorizontalsPixelbyte2
    ld a,b
    rra
    rra
    and 0x03
    sla b
    sla b
    or b
    xor 0x03
    and 0x0F
    ld b,a
    call todo_calculationstuff
    pop de
    ld a,b
    xor d
    and 0x10
    jr z,LAB_ram_7f5b
    ld c,0xFF
LAB_ram_7f5b:
    bit 4,d
    jr z,LAB_ram_7f6b
    ld a,e
    sub c
    ld a,h
    jp c,todo_drawJumpEntrypoint2
    jp z,todo_drawJumpEntrypoint2
    ld a,l
    jr LAB_ram_7f75
LAB_ram_7f6b:
    ld a,e
    sub c
    ld a,l
    jp c,todo_drawJumpEntrypoint2
    jp z,todo_drawJumpEntrypoint2
    ld a,h
LAB_ram_7f75:
    ld b,e
    and a
    jr z,LAB_ram_7f7a
    dec a
LAB_ram_7f7a:
    call todo_anothersubbeforedraw
    ld a,c
    jp todo_drawJumpEntrypoint2
; Step of the line plot: updates the pixel/error byte and advances the address from the counts in B, D, H
todo_calculationstuff:
    ld a,b
    srl a
    srl a
    xor b
    add a,a
    add a,a
    add a,a
    add a,a
    or b
    or 0x03
    ld b,a
    res 5,b
    and 0x20
    ld a,d
    jr z,LAB_ram_7fa1
    bit 3,b
    jr z,LAB_ram_7f9c
    set 5,b
LAB_ram_7f9c:
    add a,h
    jr nc,LAB_ram_7fb4
    jr LAB_ram_7fb6
LAB_ram_7fa1:
    sub h
    jr c,LAB_ram_7fac
    bit 3,b
    jr z,LAB_ram_7fb4
    set 5,b
    jr LAB_ram_7fb4
LAB_ram_7fac:
    neg
    bit 3,b
    jr nz,LAB_ram_7fb4
    set 5,b
LAB_ram_7fb4:
    res 1,b
LAB_ram_7fb6:
    ld h,a
    bit 4,b
    ld a,e
    res 4,b
    jr z,LAB_ram_7fc9
    bit 2,b
    jr z,LAB_ram_7fc4
    set 4,b
LAB_ram_7fc4:
    add a,l
    jr nc,LAB_ram_7fdc
    jr LAB_ram_7fde
LAB_ram_7fc9:
    sub l
    jr c,LAB_ram_7fd4
    bit 2,b
    jr z,LAB_ram_7fdc
    set 4,b
    jr LAB_ram_7fdc
LAB_ram_7fd4:
    neg
    bit 2,b
    jr nz,LAB_ram_7fdc
    set 4,b
LAB_ram_7fdc:
    res 0,b
LAB_ram_7fde:
    ld l,a
    ld c,l
    rrc b
    rr c
    ld a,h
    rrc b
    rra
    cp c
    jr c,LAB_ram_7ff6
    set 4,b
    push bc
    bit 7,b
    jr z,LAB_ram_8000
    ld b,a
    ld a,c
    jr LAB_ram_8006
LAB_ram_7ff6:
    res 4,b
    push bc
    bit 6,b
    jr z,LAB_ram_8004
    ld b,c
    jr LAB_ram_8006
LAB_ram_8000:
    ld a,l
    ld b,h
    jr LAB_ram_8006
LAB_ram_8004:
    ld a,h
    ld b,l
LAB_ram_8006:
    call todo_anothersubbeforedraw
    ld a,c
    pop bc
    ld c,a
    ret
drawVerticals:
    ld a,(hl)
    or c
    ld (hl),a
    dec d
    ret z
    ld a,e
    add a,b
    ld e,a
    jr nc,dvscrgetnextline
dvRotatePixmask:
    rrc c
    jr nc,dvscrgetnextline
dvgetscrbyte:
    inc l
dvscrgetnextline:
    ld a,l
smc_dvpatchadr5:
    add a,0x40
    ld l,a
    jr nc,drawVerticals
smc_dvpatchadr7:
    inc h
    jr drawVerticals
drawHorizontals:
    ld a,(hl)
    or c
    ld (hl),a
    dec d
    ret z
    ld a,e
    add a,b
    ld e,a
    jr nc,dh1RotatePixmask
    ld a,l
dh1nextPixelline:
    add a,0x40
    ld l,a
    jr nc,dh1RotatePixmask
dh1nextPixellineBlock:
    inc h
dh1RotatePixmask:
    rrc c
    jr nc,drawHorizontals
dh1SetnextByteadr:
    inc l
    jr drawHorizontals
LAB_ram_803d:
    ld a,c
    cpl
    ld c,a
drawHorizontalsPixelbyte2:
    ld a,(hl)
    and c
    ld (hl),a
    dec d
    ret z
    ld a,e
    add a,b
    ld e,a
    jr nc,dh2nextPixelline
dh2RotatePixmask:
    rrc c
    jr c,dh2nextPixelline
dh2SetnextByteadr:
    inc l
dh2nextPixelline:
    ld a,l
smc_dhpatchadr6:
    add a,0x40
    ld l,a
    jr nc,drawHorizontalsPixelbyte2
dh2nextPixellineBlock:
    inc h
    jr drawHorizontalsPixelbyte2
gotodrawHPB3:
    ld a,c
    cpl
    ld c,a
drawHorizontalsPixelbyte3:
    ld a,(hl)
    and c
    ld (hl),a
    dec d
    ret z
    ld a,e
    add a,b
    ld e,a
    jr nc,dh3RotatePixmask
    ld a,l
dh3nextPixelline:
    add a,0x40
    ld l,a
    jr nc,dh3RotatePixmask
dh3nextPixellineBlock:
    inc h
dh3RotatePixmask:
    rrc c
    jr c,drawHorizontalsPixelbyte3
dh3SetnextByteadr:
    inc l
    jr drawHorizontalsPixelbyte3
 IFDEF TITLESEL
; spawnCommandParser actions: ship type in the high nibble, action 9 (title ship) in the low one
titleShips:
    db 0x69                         ; Viper
    db 0xB9                         ; Asp Mk II
    db 0x79                         ; Cobra Mk III (index 2 is where splash2Shipnr starts)
    db 0xC9                         ; Fer-de-Lance
    db 0xE9                         ; Sidewinder
    db 0xF9                         ; Krait
    db 0x59                         ; Rock Hermit (the Python is too long for the window)
    db 0xD9                         ; Thargoid
; Ship names in the order of titleShips, zero-terminated, 16 bytes each
titleNames:
    db "VIPER",0
    ds 16 - 6
    db "ASP MK II",0
    ds 16 - 10
    db "COBRA MK III",0
    ds 16 - 13
    db "FER-DE-LANCE",0
    ds 16 - 13
    db "SIDEWINDER",0
    ds 16 - 11
    db "KRAIT",0
    ds 16 - 6
    db "ROCK HERMIT",0
    ds 16 - 12
    db "THARGOID",0
    ds 16 - 9
 ENDIF
    ds 0xC000 + 16384 - $               ; the file is 16384 bytes (tools/build_dsk128.py keeps the AMSDOS header length)
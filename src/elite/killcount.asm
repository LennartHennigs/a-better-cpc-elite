; Kill count on the status page (-DENHANCED, English): "Rating: Harmless - 12". Called in place of the `call anotherPrintwithTokeninA` after `call getRank` in the status code
; (killHookSite in commonxx.asm, A = the rank token); resident in flight and docked. With -DMISSIONS it sits in the shared head of every flight image
; (missions_flight.asm, the same address in all of them), without it after the laser sights block in the zero tail of COMMONXX.
; The count is the word at killScore+1: the low byte of the 24-bit score is a fraction (getRank compares the middle byte).
killCountHook:
    push af                             ; the rank token
    call printString                    ; the rank, no new line yet (CallprintString would add it)
    pop af
    call killSpace                      ; one space, unless the rank string ends in one already (commonxx.asm, in the dead bytes at &204E)
    call printStringFollowingByte
    db "-"
    call printStringFollowingByte
    db " "
    ld hl,(killScore + 1)
    and a                               ; carry clear: a plain number, no decimal point
    call todo_SomethingwithDigits
    jp CurHomeinFrame                   ; the two new lines anotherPrintwithTokeninA gave the rank
killCountHookEnd:

; Build configuration of the 128K build: one variant only (enhanced UI, mission hooks, title ship selection, Firebird loader). No -D flags are needed on the
; command line; tools add only the per-image flags -DFL_x (flight image x) and -DOVL_x (docked overlay x). Included first by every source file.
    IFNDEF ENHANCED
    DEFINE ENHANCED
    ENDIF
    IFNDEF MISSIONS
    DEFINE MISSIONS
    ENDIF
    IFNDEF TITLESEL
    DEFINE TITLESEL
    ENDIF
    IFNDEF FIREBIRD
    DEFINE FIREBIRD
    ENDIF

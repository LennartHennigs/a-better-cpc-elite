## Origin of the CPC port

- The Z80 conversions (ZX Spectrum, Amstrad CPC) were made by Torus for Firebird. The CPC version is a
  port of the ZX Spectrum version, not of the BBC original.
- Ricardo Pinto, programmer of the Amstrad version: Braben and Bell gave the team a 6502 hex dump, which
  did not help. "In the end we wrote our version by playing Elite on a [BBC Micro] and making ours look
  the same."
- The CPC conversion has fewer ships than other platforms (no Anaconda or Transport) and some minor
  differences in missions and titles.
- It includes the "supernova rescue" and "cloaking device" missions, and refinements to the launch tube
  and jump drive animations.
- The ZX Spectrum version was a Gallup chart bestseller and #7 in the Your Sinclair Readers' Top 100.
- The first CPC cassette release had a bug that locked up the machine after about an hour of play.
  Torus traced it to the disk-drawing routine also used in *Gyron* and Spectrum Elite. Firebird sent
  free replacement cassettes. (Web search results.) **Primary source** (Amtix Nov 1986, Pinto): the
  routine was the same "disk drawing routine" used in *Gyron* and Spectrum Elite and had never given
  trouble there. He found it when "just drifting towards a planet, and the planet just moved off the
  screen and the thing crashed" with no key pressed. The crash came "after hours, or after a couple of
  minutes", so it depended on state, not time. See "Magazine sources" below, and `docs/_architecture.md` ("The disc-drawing routine") for where it is and why the stock build survives it.

## Existing work

- No public, complete Z80 disassembly of CPC Elite was found.
- **Fessor** (CPCWiki user, CPC464/Kubuntu) disassembled the CPC version with Ghidra and rebuilt it as a
  RASM source. Thread "Expanding Elite", 68 posts over 3 pages, 2021-07-21 to 2024-08-06. Forum is now
  read-only; the saved pages are `extended/forum/Expanding Elite 1of3.html`, `- Page 2.html`, `- Page 3.html`.
  **No public source.** The source and the beta disk were forum attachments (guests cannot see them).
  Fessor self-hosted git (GitBucket, then Gitea, on a QNAP NAS) and asked that nothing be re-uploaded
  elsewhere. See "Findings from the Fessor thread" in `_fessor.md`.
- **CNGSoft** lists Firebird Elite saving games as `ELITE64E.BS1`, and a cracked "Syrox" version that fits in 25K.

## Magazine sources (`magazines/`, text in `magazines/text/`, read 2026-11-07)

Two 4-page scans, OCR'd with `pdftotext -layout` (the layout is two columns interleaved and the Amstrad
Action scan is badly garbled; check the PDF page before quoting). Index in `magazines/README.md`.

**Amstrad Action no. 3, December 1985, pp. 70-71** (preview, written before release):
- Torus was to add four new special missions instead of the two original ones; they had not finished the
  fourth. They promised an "enhanced disc version" with the full set of ships "perhaps even some new ones of
  their own design" and more missions (what shipped has fewer ships than the BBC; see "Existing work").
- Seven colours for suns and planets, which could "mask each other like an eclipse".
- Music planned but undecided: the C64 version played the Blue Danube on docking; the Amstrad docking
  sequence differs, so Torus had not chosen where it would go. (The stock disk carries `MUSIQUEX`, the
  Blue Danube player, plus `NOTMUSIC`, a copy of `COMMONXX &6000-&6FFF`.)
- The team: Torus, four members, Ricardo Pinto (maths, Dundee), Dominic Prior (Oxford), Mark Whighton, and
  Philip Mochan; previous game *Gyron* on the Spectrum. They developed on an Apricot.

**Amtix, November 1986, pp. 84-86** (interview with Ricardo Pinto, who says Elite was done for the money
after *Gyron*, planned as three or four months and taking about a year):
- Source material was a BBC 6502 hex dump ("a list of numbers"), so they wrote the Z80 version by playing
  the BBC game and copying it, "mimic what were really bugs". The original game data had been copied from
  the board game *Traveller*.
- Changes they list: the **launch tube** and the **refined jump drive**; the four special missions are the
  **Supernova rescue, pirates taking over Space Station 1, the cloaking device** and the **ECM jammer** used
  in the Thargoid invasion. (Match these to the code: notes list supernova `&3927` bit 5, cloak bit 6,
  ECM jammer bit 7; the "pirates take over a station" mission is the Thargoid invasion, see "Amtix's four missions" in `docs/_missions.md`.)
- Pinto wanted asteroid storms, generation ships and black holes, but "there wasn't time".
- "There are huge chunks of the program just sitting there unused because we didn't have time to debug
  them. So we just turned off all the switches that used those routines." This is what Fessor's `defdeactivate*`
  work found: code with no entry points. It also explains the stale variable areas.
- They used no ROM routines ("using someone else's program is just asking for trouble"); they poked the
  CRTC so the screen matched the Spectrum's. (The code does use the firmware jump block at `&A600` for disk
  I/O, so "no ROM routines" means no graphics or maths ROM.)
- Tools: a 40-minute-compile cross assembler at first, then the PDS assembler by Andrew Glaister (author of
  *Empires* for Firebird). Work was done on cassette recorders, then on the floor of Pinto's flat in Edinburgh.
- The Amstrad version "looked best" but the Spectrum one was faster.
- The bug story is given above (history).

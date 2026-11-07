#!/usr/bin/env python3
"""Regenerate docs/_spectrum_map.md from work/spectrum_map/matches.tsv and data_matches.tsv.
usage: python3 -I tools/spectrum_map.py && python3 -I tools/spectrum_data_map.py && python3 -I tools/gen_spectrum_map_doc.py"""
import csv
from pathlib import Path
R = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(R / "work/spectrum_map/matches.tsv"), delimiter="\t"))
def good(r):
    if r["how"] == "prop": return float(r["ratio"]) >= 0.70
    return float(r["ratio"]) >= 0.85 and float(r["ratio"]) - float(r["second"]) >= 0.05 and r["mutual"] == "1"
g = sorted((r for r in rows if good(r)), key=lambda r: (r["cpc_file"], int(r["cpc_addr"], 16)))
data = list(csv.DictReader(open(R / "work/spectrum_map/data_matches.tsv"), delimiter="\t"))
L = ["# CPC to ZX Spectrum routine map (generated)", "",
"The CPC port is a Spectrum port, so most game logic has the same instruction skeleton on both. `tools/spectrum_map.py` matched",
"routines of `src/elite/*.asm` against the blocks of the Spectrum SkoolKit disassembly (`work/ext_msx/skoolkit/src/elite.skool`, by",
"Rasmus-M) by comparing instruction skeletons (immediates, addresses and offsets masked) with difflib; a second pass followed the",
"call graph from confident pairs (`prop`). A pair is listed when the ratio is at least 0.85 (propagated: 0.70), the margin over the",
"runner-up is at least 0.05 and the match is mutual best. Read the Spectrum commentary at the given address in `elite.skool`:",
"`grep -n '^c\\$ADDR' work/ext_msx/skoolkit/src/elite.skool`.", "",
"What is in `src/elite/` (byte-exact, `tools/check_src.sh`):",
"- Generic labels with a confident Spectrum name were renamed (maps in `tools/rename_maps/2026-11-07-spectrum-*.txt`, applied by",
"  `tools/apply_spectrum_names.py` and `tools/rename_dat.py`), including Fessor's `todo_*` placeholders that have an exact counterpart.",
"- Every pair has a `; ZX Spectrum: name (&ADDR) ratio` line above its label.",
"- About 170 routines carry our own comment (maths, divides, square root, circle/disc code, text engine, charts, trade, ship movement, spawning);",
"  the wording is ours, written from the code, with the Spectrum I/O descriptions as a check. No Spectrum commentary is copied.",
"- Pre-change copies of the sources: `work/backup_src_pre_spectrum/`. Fessor's other names were left alone.", "",
"Disagreements: Fessor's `todoOverheating` (`&6812`) matches the Spectrum's \"end the demo once a counter wraps\" at 0.94; the code adds 2 to the",
"disc radius counter and bumps `CockpitTemp` and sets `GameOverFlag` when it wraps, so the CPC reading (overheating) was kept. Fessor's",
"`chkAltitude` is the dashboard compass update in the Spectrum disassembly. His ship names (`shipdatAlloy`, `shipdatSplinter`, ...) differ from",
"the Spectrum labels for several blueprints (the CPC `shipdatAlloy` is the Spectrum splinter, `shipdatSplinter` the boulder).", "",
"## Routines", "", "| CPC file | CPC address | CPC label | Spectrum address | Spectrum label | ratio | how |", "|---|---|---|---|---|---|---|"]
for r in g:
    L.append(f'| {r["cpc_file"]} | &{r["cpc_addr"]} | {r["cpc_label"] or "-"} | ${r["spec_addr"]} | {r["spec_label"] or "-"} | {float(r["ratio"]):.2f} | {r["how"]} |')
L += ["", "## Data tables identical on both machines (`tools/spectrum_data_map.py`)", "", "| Spectrum label | Spectrum address | bytes | CPC address | CPC label |", "|---|---|---|---|---|"]
for r in data: L.append(f'| {r["spec_label"]} | ${r["spec_addr"]} | {r["len"]} | &{r["cpc_addr"]} | {r["cpc_labels"] or "-"} |')
L += ["", "The squares table `sqr_table` (`&C600`, 512 bytes) and the default commander (`&39D1`, 92 bytes) are identical too but have no label in `src/elite` yet.",
"", "## Not matched", "", "Hardware routines (screen, keyboard, sound, loading, copy protection) differ by design; routines the CPC splits or joins differently from",
"the Spectrum also fail the whole-routine comparison. Candidates below 0.85 are in `work/spectrum_map/matches.tsv`.", ""]
(R / "docs/_spectrum_map.md").write_text("\n".join(L))
print(len(g), "rows")

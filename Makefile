# Assemble the four code files. Needs sjasmplus (scripts/install-tools.sh puts it in ~/.local/bin).
#   make stock      original bytes (CPC+ keyboard fix included in en/fr)           -> work/build/stock/
#   make enhanced   star occlusion, Escape in the menus, title-screen ship choice  -> work/build/enhanced/
#   make missions   enhanced plus the added missions (English only): bootable disk -> work/elite_missions.dsk
#   make check      bash tools/check_src.sh for en, de and fr
# LOC=de or LOC=fr picks the German or French tree (stock and enhanced only; no TITLESEL in French).
SJASM ?= $(HOME)/.local/bin/sjasmplus
LOC   ?= en
TREE_en = src/elite
TREE_de = src/elite_de
TREE_fr = src/elite_fr
TREE    = $(TREE_$(LOC))
TITLE   = $(if $(filter fr,$(LOC)),,-DTITLESEL)
OUT     = work/build

.PHONY: stock enhanced missions check

stock:
	@mkdir -p $(OUT)/stock/$(LOC)
	@for f in largeaxx commonxx common2x musiquex; do $(SJASM) --nologo --msg=err --raw=$(OUT)/stock/$(LOC)/$$f.bin $(TREE)/$$f.asm || exit 1; done
	@echo "stock ($(LOC)): $(OUT)/stock/$(LOC)/"

enhanced:
	@mkdir -p $(OUT)/enhanced/$(LOC)
	@for f in largeaxx commonxx common2x musiquex; do $(SJASM) --nologo --msg=err -DENHANCED $(TITLE) --raw=$(OUT)/enhanced/$(LOC)/$$f.bin $(TREE)/$$f.asm || exit 1; done
	@echo "enhanced ($(LOC)): $(OUT)/enhanced/$(LOC)/"

missions:
	python3 -I tools/build_dsk.py --missions work/elite_missions.dsk

check:
	bash tools/check_src.sh && bash tools/check_src.sh de && bash tools/check_src.sh fr

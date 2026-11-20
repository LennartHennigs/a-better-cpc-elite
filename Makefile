# Assemble the four code files. Needs sjasmplus (scripts/install-tools.sh puts it in ~/.local/bin).
#   make stock      original bytes (CPC+ keyboard fix included in en/fr)           -> work/build/stock/
#   make enhanced   star occlusion, Escape in the menus, title-screen ship choice  -> work/build/enhanced/
#   make missions   enhanced plus the added missions (English only): bootable disk -> work/elite_missions.dsk
#   make check      bash tools/check_src.sh for en, de and fr
#   make disk6128     the 128K disk (6128 only) -> work/elite128.dsk; HULLS=stock (default) or HULLS=arcelite picks where the filled ships come from
#   make listing6128  the readable listing of the 128K build (includes expanded, addresses and bytes) -> build/listing6128/elite6128.lst (same HULLS switch)
# LOC=de or LOC=fr picks the German or French tree (stock and enhanced).
SJASM ?= $(HOME)/.local/bin/sjasmplus
LOC   ?= en
TREE_en = src/elite
TREE_de = src/elite_de
TREE_fr = src/elite_fr
TREE    = $(TREE_$(LOC))
TITLE   = -DTITLESEL
OUT     = work/build

.PHONY: stock enhanced missions check disk6128 listing6128
HULLS ?= stock
export HULLS

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

disk6128:
	bash tools/check_src128.sh && python3 -I tools/build_dsk128.py

listing6128:
	bash tools/listing6128.sh build/listing6128

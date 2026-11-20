# Assemble the four code files. Needs sjasmplus (scripts/install-tools.sh puts it in ~/.local/bin).
#   make original   the original game on a disk (stock bytes)                     -> build/elite_original.dsk
#   make expanded   everything: enhancements, missions, ship packs, trainers, viewer -> build/elite_expanded.dsk (English only for now)
#   make stock      original bytes (CPC+ keyboard fix included in en/fr)           -> build/stock/
#   make enhanced   star occlusion, Escape in the menus, title-screen ship choice  -> build/enhanced/
#   make missions   enhanced plus the added missions (English only): bootable disk -> build/elite_missions.dsk (no trainers or viewer; `expanded` is the full build)
#   make check      bash tools/check_src.sh for en, de and fr
#   make disk6128     the 128K disk (6128 only) -> work/elite128.dsk; HULLS=stock (default) or HULLS=arcelite picks where the filled ships come from
#   make listing6128  the readable listing of the 128K build (includes expanded, addresses and bytes) -> build/listing6128/elite6128.lst (same HULLS switch)
#   make test       rebuild the disks, then the host tests: check_src (en, de, fr), saves, disk rules (about a minute; tools/tests/run_all.py)
#   make test-quick the host tests alone, on the disks already in build/ (seconds)
#   make test-emu   the cpcxray tests with a pass/fail result (several minutes; needs cpcxray and work/xray/output/firebird_in_flight.sna)
#   make clean      delete build/
# Everything a make target delivers lands in build/ (gitignored); intermediate files stay in work/.
# LOC=de or LOC=fr picks the German or French tree (original, stock and enhanced; expanded is not ported yet).
SJASM ?= $(HOME)/.local/bin/sjasmplus
LOC   ?= en
TREE_en = src/elite
TREE_de = src/elite_de
TREE_fr = src/elite_fr
TREE    = $(TREE_$(LOC))
TITLE   = -DTITLESEL
OUT     = build

.PHONY: original expanded stock enhanced missions check test test-quick test-emu clean disk6128 listing6128
HULLS ?= stock
export HULLS

$(OUT)/README.md: tools/build_readme.md
	@mkdir -p $(OUT)
	@cp $< $@

original: $(OUT)/README.md
	bash tools/build_original.sh $(LOC)

expanded: $(OUT)/README.md
	bash tools/build_expanded.sh $(LOC)

stock: $(OUT)/README.md
	@mkdir -p $(OUT)/stock/$(LOC)
	@for f in largeaxx commonxx common2x musiquex; do $(SJASM) --nologo --msg=err --raw=$(OUT)/stock/$(LOC)/$$f.bin $(TREE)/$$f.asm || exit 1; done
	@echo "stock ($(LOC)): $(OUT)/stock/$(LOC)/"

enhanced: $(OUT)/README.md
	@mkdir -p $(OUT)/enhanced/$(LOC)
	@for f in largeaxx commonxx common2x musiquex; do $(SJASM) --nologo --msg=err -DENHANCED $(TITLE) --raw=$(OUT)/enhanced/$(LOC)/$$f.bin $(TREE)/$$f.asm || exit 1; done
	@echo "enhanced ($(LOC)): $(OUT)/enhanced/$(LOC)/"

missions: $(OUT)/README.md
	python3 -I tools/build_dsk.py --missions $(OUT)/elite_missions.dsk

check:
	bash tools/check_src.sh && bash tools/check_src.sh de && bash tools/check_src.sh fr

disk6128:
	bash tools/check_src128.sh && python3 -I tools/build_dsk128.py

listing6128:
	bash tools/listing6128.sh build/listing6128

test:
	$(MAKE) original
	$(MAKE) original LOC=de
	$(MAKE) original LOC=fr
	$(MAKE) expanded
	$(MAKE) missions
	python3 -I tools/tests/run_all.py --host

test-quick:
	python3 -I tools/tests/run_all.py --host

test-emu:
	python3 -I tools/tests/run_all.py --emu

clean:
	rm -rf $(OUT)

FONT_STYLES = Regular Bold Italic BoldItalic

CACHE_DIR := .cache
BUILD_DIR := build
GLYPHS_DIR := resources/glyphs

ERROR_LOG_FILE := error.txt

MODIFY_HACK_SCRIPT := src/fontforge_/modify_hack.py
MODIFY_IBMPLEX_SCRIPT := src/fontforge_/modify_ibm_plex_sans_jp.py
MODIFY_HACK_NERD_SCRIPT := src/fontforge_/modify_hack_nerd.py
MERGE_SCRIPT := src/fontforge_/merge.py
BUNDLE_NF_SCRIPT := src/fontforge_/bundle_nf.py
BRAILLE_GEN_SCRIPT := src/fontforge_/braille_gen.py
PATCH_SCRIPT := src/fontforge_/patch.py
FONTTOOLS_SCRIPT := src/fonttools_/main.py


.PHONY: all
all:
	@docker-compose up fontforge
	@docker-compose up fonttools

.PHONY: release
release:
	@echo "Current version is" $(shell python -c "import src.fontforge_.properties as p; print(p.VERSION, end='')")
	@read -p "Type new version: " new_version && \
		sed -i '' 's/^VERSION =.*/VERSION = "'$$new_version'"/' src/fontforge_/properties.py
	@make clean
	@make
	@cp LICENSE build/
	@version=$$(python -c "import src.fontforge_.properties as p; print(p.VERSION, end='')") && \
		cd build && \
		zip -r AgaveJP_v$$version.zip * && \
		shasum -a 256 AgaveJP_v$$version.zip | awk '{print $$1}' > AgaveJP_v$$version.sha256
	@rm build/LICENSE

.PHONY: clean
clean:
	@rm -f $(ERROR_LOG_FILE)
	@rm -rf $(CACHE_DIR) $(BUILD_DIR)

.PHONY: fontforge
fontforge: $(CACHE_DIR) $(addprefix $(CACHE_DIR)/AgaveJP-, $(addsuffix .ttf, $(FONT_STYLES)))
	@echo "Completed: fontforge"

.PHONY: fonttools
fonttools: $(BUILD_DIR) $(addprefix $(BUILD_DIR)/AgaveJP-, $(addsuffix .ttf, $(FONT_STYLES)))
	@echo "Completed: fonttools"

# Do not renove intermediate TTF files
.SECONDARY: $(wildcard *.ttf)

# Fix by Fonttools
$(BUILD_DIR)/AgaveJP-%.ttf: $(CACHE_DIR)/AgaveJP-%.ttf $(FONTTOOLS_SCRIPT)
	@python3 $(FONTTOOLS_SCRIPT) $< $(CACHE_DIR) $@ 2>> $(ERROR_LOG_FILE)

# Patch
$(CACHE_DIR)/AgaveJP-%.ttf: $(CACHE_DIR)/merged-AgaveJP-%.ttf $(CACHE_DIR)/NerdFonts.ttf $(CACHE_DIR)/Braille.ttf $(PATCH_SCRIPT)
	@python3 $(PATCH_SCRIPT) $< $(word 2, $^) $(word 3, $^) $@ 2>> $(ERROR_LOG_FILE)

# Generate patch glyphs
$(CACHE_DIR)/NerdFonts.ttf: $(GLYPHS_DIR)/FontPatcher-glyphs $(BUNDLE_NF_SCRIPT)
	@python3 $(BUNDLE_NF_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/Braille.ttf: $(BRAILLE_GEN_SCRIPT)
	@python3 $(BRAILLE_GEN_SCRIPT) $@ 2>> $(ERROR_LOG_FILE)

# Merge base fonts
$(CACHE_DIR)/merged-AgaveJP-Regular.ttf: $(CACHE_DIR)/modified-Hack-Regular.ttf $(CACHE_DIR)/modified-IBMPlexSansJP-Medium.ttf $(MERGE_SCRIPT)
	@python3 $(MERGE_SCRIPT) $(word 1, $^) $(word 2, $^) Regular $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/merged-AgaveJP-Bold.ttf: $(CACHE_DIR)/modified-Hack-Bold.ttf $(CACHE_DIR)/modified-IBMPlexSansJP-Bold.ttf $(MERGE_SCRIPT)
	@python3 $(MERGE_SCRIPT) $(word 1, $^) $(word 2, $^) Bold $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/merged-AgaveJP-Italic.ttf: $(CACHE_DIR)/modified-Hack-Regular.ttf $(CACHE_DIR)/modified-IBMPlexSansJP-Medium.ttf $(MERGE_SCRIPT)
	@python3 $(MERGE_SCRIPT) $(word 1, $^) $(word 2, $^) Italic $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/merged-AgaveJP-BoldItalic.ttf: $(CACHE_DIR)/modified-Hack-Bold.ttf $(CACHE_DIR)/modified-IBMPlexSansJP-Bold.ttf $(MERGE_SCRIPT)
	@python3 $(MERGE_SCRIPT) $(word 1, $^) $(word 2, $^) BoldItalic $@ 2>> $(ERROR_LOG_FILE)

# Modify base fonts
$(CACHE_DIR)/modified-Hack-%.ttf: $(GLYPHS_DIR)/Agave-%.ttf $(MODIFY_HACK_SCRIPT)
	@python3 $(MODIFY_HACK_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-IBMPlexSansJP-%.ttf: $(GLYPHS_DIR)/IBMPlexSansJP-%.ttf $(MODIFY_IBMPLEX_SCRIPT)
	@python3 $(MODIFY_IBMPLEX_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

# Setup directory
$(CACHE_DIR) $(BUILD_DIR):
	@mkdir -p $@

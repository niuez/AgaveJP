CACHE_DIR := .cache
BUILD_DIR := build
RESOURCES_DIR := resources
GLYPHS_DIR := $(RESOURCES_DIR)/glyphs

ERROR_LOG_FILE := error.txt

MODIFY_HACK_SCRIPT := src/modify_hack.py
MODIFY_IBMPLEX_SCRIPT := src/modify_ibm_plex_sans_jp.py
MODIFY_HACK_NERD_SCRIPT := src/modify_hack_nerd.py
MERGE_SCRIPT := src/merge.py

all: $(CACHE_DIR) $(BUILD_DIR) \
	$(BUILD_DIR)/PleckJP-Regular.ttf $(BUILD_DIR)/PleckJP-Bold.ttf
	@echo "Completed."

# Do not renove intermediate files
.SECONDARY: $(wildcard *.ttf)

$(BUILD_DIR)/PleckJP-%.ttf: $(CACHE_DIR)/modified-Hack-%.ttf $(CACHE_DIR)/modified-IBMPlexSansJP-%.ttf $(CACHE_DIR)/modified-HackNerdFont.ttf $(MERGE_SCRIPT)
	@python3 $(MERGE_SCRIPT) $(word 1, $^) $(word 2, $^) $(word 3, $^) $* $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-HackNerdFont.ttf: $(GLYPHS_DIR)/HackNerdFont-Regular.ttf $(MODIFY_HACK_NERD_SCRIPT)
	@python3 $(MODIFY_HACK_NERD_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-Hack-%.ttf: $(GLYPHS_DIR)/Hack-%.ttf $(MODIFY_HACK_SCRIPT)
	@python3 $(MODIFY_HACK_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-IBMPlexSansJP-%.ttf: $(GLYPHS_DIR)/IBMPlexSansJP-%.ttf $(MODIFY_IBMPLEX_SCRIPT)
	@python3 $(MODIFY_IBMPLEX_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR) $(BUILD_DIR):
	@mkdir -p $@

clean:
	@rm -f $(ERROR_LOG_FILE)
	@rm -rf $(CACHE_DIR) $(BUILD_DIR)
.PHONY: clean

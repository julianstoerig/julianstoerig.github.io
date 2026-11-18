# Build the site into _site/ with pandoc.  Usage: make | make serve | make clean

# Prefer the pinned pandoc from tools/install-pandoc.sh over any system one.
PANDOC     ?= $(firstword $(wildcard $(HOME)/.local/bin/pandoc) pandoc)
SITE_TITLE := DD4JS
EMAIL      := julian.stoerig+site@gmail.com
SITE_URL   := https://dd4js.com

# build.py reads its settings from the environment
export PANDOC SITE_TITLE SITE_URL

PAGE_FLAGS := --from markdown --to html5 --standalone --math-method=mathml --wrap=none \
    --template templates/page.html \
    --variable lang=en \
    --variable site-title="$(SITE_TITLE)" \
    --variable email="$(EMAIL)"

# Source layout (file names must not contain spaces):
#   content/home.md          the home page, built to the site root
#   content/<slug>.md        a page without extra files
#   content/<slug>/index.md  a page with extra files; everything else in
#                            that folder is copied next to the built page
HOME_PAGE      := content/home.md
FLAT_SOURCES   := $(filter-out $(HOME_PAGE),$(wildcard content/*.md))
FOLDER_SOURCES := $(wildcard content/*/index.md)
ASSET_SOURCES  := $(shell find content -mindepth 2 -type f ! -name index.md)

FLAT_PAGES   := $(patsubst content/%.md,_site/%/index.html,$(FLAT_SOURCES))
FOLDER_PAGES := $(patsubst content/%/index.md,_site/%/index.html,$(FOLDER_SOURCES))
ASSETS       := $(patsubst content/%,_site/%,$(ASSET_SOURCES))
STATIC       := $(patsubst static/%,_site/%,$(wildcard static/*))

all: _site/index.html $(FLAT_PAGES) $(FOLDER_PAGES) $(ASSETS) $(STATIC) \
     _site/articles/index.html _site/feed.xml

# The home page is the site root: content/home.md -> _site/index.html
_site/index.html: $(HOME_PAGE) templates/page.html
	mkdir -p $(dir $@)
	$(PANDOC) $(PAGE_FLAGS) --output $@ $<

# content/foo.md -> _site/foo/index.html  (gives the clean URL /foo/)
$(FLAT_PAGES): _site/%/index.html: content/%.md templates/page.html
	mkdir -p $(dir $@)
	$(PANDOC) $(PAGE_FLAGS) --output $@ $<

# content/foo/index.md -> _site/foo/index.html
$(FOLDER_PAGES): _site/%/index.html: content/%/index.md templates/page.html
	mkdir -p $(dir $@)
	$(PANDOC) $(PAGE_FLAGS) --output $@ $<

# content/foo/figure.svg -> _site/foo/figure.svg
$(ASSETS): _site/%: content/%
	mkdir -p $(dir $@)
	cp $< $@

# article list and feed are written together by build.py
_site/articles/index.html _site/feed.xml &: build.py $(FLAT_SOURCES) $(FOLDER_SOURCES) templates/page.html templates/meta.json
	python3 build.py

_site/%: static/%
	mkdir -p $(dir $@)
	cp $< $@

serve: all
	python3 -m http.server --directory _site 8000

clean:
	rm -rf _site

.PHONY: all serve clean

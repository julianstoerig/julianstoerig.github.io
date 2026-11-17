# Build the site into _site/ with pandoc.  Usage: make | make serve | make clean

# Prefer the pinned pandoc from tools/install-pandoc.sh over any system one.
PANDOC     ?= $(firstword $(wildcard $(HOME)/.local/bin/pandoc) pandoc)
SITE_TITLE := DD4JS
EMAIL      := julian.stoerig+site@gmail.com
SITE_URL   := https://julianstoerig.github.io

# build.py reads its settings from the environment
export PANDOC SITE_TITLE SITE_URL

SOURCES := $(wildcard content/*.md)
PAGES   := $(patsubst content/%.md,_site/%/index.html,$(SOURCES))
STATIC  := $(patsubst static/%,_site/%,$(wildcard static/*))

all: $(PAGES) $(STATIC) _site/index.html _site/feed.xml

# content/foo.md -> _site/foo/index.html  (gives the clean URL /foo/)
_site/%/index.html: content/%.md templates/page.html
	mkdir -p $(dir $@)
	$(PANDOC) --from markdown --to html5 --standalone --math-method=mathml --wrap=none \
	    --template templates/page.html \
	    --variable lang=en \
	    --variable site-title="$(SITE_TITLE)" \
	    --variable email="$(EMAIL)" \
	    --output $@ $<

# index and feed are written together by build.py
_site/index.html _site/feed.xml &: build.py $(SOURCES) templates/page.html templates/meta.json
	python3 build.py

_site/%: static/%
	mkdir -p $(dir $@)
	cp $< $@

serve: all
	python3 -m http.server --directory _site 8000

clean:
	rm -rf _site

.PHONY: all serve clean

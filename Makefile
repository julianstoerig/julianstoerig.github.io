# Build the site into _site/ with pandoc.  Usage: make | make serve | make clean

PANDOC     ?= pandoc
SITE_TITLE := DD4JS
EMAIL      := julian.stoerig+site@gmail.com

SOURCES := $(wildcard content/*.md)
PAGES   := $(patsubst content/%.md,_site/%/index.html,$(SOURCES))
STATIC  := $(patsubst static/%,_site/%,$(wildcard static/*))

all: $(PAGES) $(STATIC)

# content/foo.md -> _site/foo/index.html  (gives the clean URL /foo/)
_site/%/index.html: content/%.md templates/page.html
	mkdir -p $(dir $@)
	$(PANDOC) --from markdown --to html5 --standalone --math-method=mathml --wrap=none \
	    --template templates/page.html \
	    --variable lang=en \
	    --variable site-title="$(SITE_TITLE)" \
	    --variable email="$(EMAIL)" \
	    --output $@ $<

_site/%: static/%
	mkdir -p $(dir $@)
	cp $< $@

serve: all
	python3 -m http.server --directory _site 8000

clean:
	rm -rf _site

.PHONY: all serve clean

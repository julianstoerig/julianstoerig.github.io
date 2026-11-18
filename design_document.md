# Design document

How dd4js.com is built, and why. Each entry gives the choice and its reason, so that a later change can start from the reason.

## Goal

A tiny, fast, accessible personal site for things worth keeping, sharing, or not retelling: amateur radio, electrical and RF engineering, programming.

Four principles follow. The site stays small, because every tool and file is something to maintain and something that can break. Every page works without JavaScript. The host only serves files, so a move changes only the deploy step. Visitors contact one host only, hence no web fonts and no analytics.

## Build

The site is built with pandoc, a Makefile and one short Python script that uses only the standard library. A framework (Hugo was the alternative) is more than a few pages and a feed need.

`make` renders each `content/<slug>.md` and `content/<slug>/index.md` to `_site/<slug>/index.html` through one pandoc template, and `content/home.md` to `_site/index.html`. `build.py` then reads the metadata of each article and writes the article list and the feed. The other files of an article folder and of `static/` are copied unchanged. File names must not contain spaces, which make cannot handle.

`build.py` obtains the metadata as JSON from pandoc (`templates/meta.json`). The standard library has no YAML parser, and a hand-written one would restrict the front matter and add code to maintain.

The pandoc version is pinned. `tools/install-pandoc.sh` installs one release into `~/.local` after checking its SHA-256, CI runs the same script, and the Makefile prefers that binary. The same input should give the same output on every machine, and an older distribution package has already failed once on an unknown flag.

## Content

Articles are evergreen. They carry a `published` date and a hand-written `changelog` in the front matter, and "last updated" is the newest changelog entry. Only meaningful edits count, so that the date keeps its meaning. A page without `published`, such as the Impressum or About me, is not an article and stays out of the article list and the feed. One rule replaces a list of special pages. The language is English.

Math is written as LaTeX and converted to MathML at build time, which browsers render natively, so no script is needed. Code blocks are highlighted at build time: pandoc emits token classes and the CSS supplies the colours for light and dark. JavaScript is allowed only for optional extras such as a calculator, and reading a page never depends on it.

## Look

The stylesheet relies on browser defaults and sets only what they lack: the reader's light or dark scheme, a readable column width, scrolling for wide code and equations, the size and plain colour of the site title, and the code colours. The aim is less CSS, not a custom style that imitates the default. The article list and the changelog are plain paragraphs, not lists.

The site title at the top of every page links to the home page. It is a paragraph and not a heading, so each page keeps the one `h1` of its own title, and the home page has none. The favicon stands in front of it as a decorative image, larger than the text and hanging below the baseline so that its centre stays near the middle of the lowercase letters.

The favicon is one SVG file, `static/favicon.svg`: a spectrum-analyser screen, a rounded frame around a rippling noise floor with one carrier peak. It is square and cropped to its box, so that it fills a tab, and a rule inside the file turns it white on dark themes. At 16 px the ripples blur, and they show at larger sizes. There is no `favicon.ico`, since current browsers accept the SVG.

## Requests

The browser reads the HTML first and only then learns what else is needed. A resource named in the HTML is fetched at once, in parallel with the others. A resource named only inside another one, such as an image in a stylesheet, has to wait for it. Each such link is one more round trip, which is felt most on a slow mobile connection.

The dependency tree is therefore kept one level deep: the page is the root, and every other resource is referenced directly from its HTML. Images are `<img>` elements and never CSS backgrounds, CSS has no `url()` or `@import`, SVG figures are self-contained, a script is loaded by a `<script>` tag and loads nothing further, and fonts are the system's own. Lighthouse's "Network dependency tree" shows the result and should list only direct children of the document.

## Pages and URLs

| URL | Source | Purpose |
| --- | --- | --- |
| `/` | `content/home.md` | Home page with links to the rest |
| `/articles/` | written by `build.py` | Article list, newest first |
| `/<slug>/` | `content/<slug>.md` or `content/<slug>/index.md` | An article or a page |
| `/<slug>/<file>` | `content/<slug>/<file>` | A figure or data file of that article |
| `/about-me/` | `content/about-me.md` | Biography |
| `/impressum/` | `content/impressum.md` | Impressum and privacy note |
| `/feed.xml` | written by `build.py` | Atom feed |

Every page is written as `<slug>/index.html` for clean URLs. Its footer links to Home, Articles, About me, Feed and the Impressum, so no further navigation is needed. A slug may exist once, as a file or as a folder, and `build.py` stops with an error otherwise.

Links in content are root-relative (`/articles/`), which works in the local preview and survives a domain change. Only in the feed does `build.py` make them absolute, because feed readers have no site to resolve them against. Links relative to the article folder (`figure.svg`) are resolved against that folder.

The feed is Atom and holds the 20 most recently published articles with their full content. `SITE_URL` in the Makefile is the only place that names the domain, and changing it needs `make clean`, because the Makefile is not a dependency of the output.

## Replies and legal

Each article ends with a "Reply by email" link with a prefilled subject. That needs no comment system, and so no script and no third party. The site and the Impressum use different `+tag` addresses, so that the tag shows where an address was harvested. Mastodon or Webmentions could be added later.

The Impressum, which German law requires, and a short privacy note share one page. The site sets no cookies and loads nothing from third parties, so the note only names GitHub as the host and its server logs.

## Writing and publishing

Unpublished work stays out of this repository, because it is public and anything committed to a pushed branch is visible and stays in the history. Drafts, raw data and the scripts for the figures live in the separate private repository `writing`, with one folder per article. An article with figures or data is published as `content/<slug>/index.md` with those files next to it, referenced by relative path (`![](figure.svg)`). Otherwise it stays a single `content/<slug>.md`.

To publish, the article and its figures are copied into `content/<slug>/` on a branch `article/<slug>`, `published` and the first `changelog` entry are added, and the result is checked with `make serve`. The branch is merged into `main` as a fast-forward, and `main` is pushed to `deploy`.

## Hosting and domain

The site is hosted on GitHub Pages and deployed by GitHub Actions (`.github/workflows/pages.yml`), which installs the pinned pandoc, runs `make` and uploads `_site`. The workflow runs when `deploy` is pushed, so that publishing (`git push origin main:deploy`) is a deliberate step apart from working on `main`. The Pages source is "GitHub Actions", because a branch deploy would serve the raw Markdown: the built output is not in the repository.

The domain is dd4js.com, after the callsign. The apex has `A` and `AAAA` records for GitHub Pages, and `www` is a `CNAME` to the `github.io` address, which GitHub redirects to the apex. The DNS provider runs without a proxy, since GitHub cannot issue the HTTPS certificate through one. The custom domain is set in the repository's Pages settings, because a `CNAME` file is ignored for Actions deploys.

## Rejected or deferred

- Typst HTML export: experimental, and likely to break.
- Hugo: workable, but more framework than needed.
- Codeberg Pages: was moving to a new system and had custom-domain certificate problems reported in 2026.
- Comment widgets (Giscus, Disqus): they need JavaScript and third parties.
- A hand-picked colour scheme and fonts: dropped in favour of browser defaults, to keep the CSS small.
- Inlining the stylesheet into every page: it would save the one request that Lighthouse shows as a chain of two, about 20 ms on a fast connection and a round trip on a slow one. It would also repeat about 0.6 KiB per page and move the CSS into the template. Left as a separate file, with the rule under Requests keeping the chain from growing.

## Open

The sample article `hello-world` is placeholder content and should be replaced by a real article.

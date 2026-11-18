# Design document

How and why dd4js.com is built.

## Goal

A blazingly fast and accessible personal site for stuff worth keeping and sharing on the topics of amateur radio, electrical & RF engineering and programming.

The basic idea is that the site stays small, because what does not exist cannot break. The site is merely a heap of static files. No JS required. Barebones styling, let the browser deal with that.

## Build

The site is built with pandoc, make and python.

`make` renders `content/<slug>.md` and `content/<slug>/index.md` to `_site/<slug>/index.html` through one pandoc template, and `content/home.md` to `_site/index.html`. `build.py` writes the article list and the feed. Other files in article folders and in `static/` are copied as they are. File names must not contain spaces, make cannot handle them.

`build.py` gets the front matter from pandoc as JSON (`templates/meta.json`), since the standard library has no YAML parser.

Pinned pandoc version gets installed into `~/.local` by `tools/install-pandoc.sh`. Makefile and CI both prefer that binary.

## Content

Articles are evergreen: a `published` date and a hand-written `changelog` in the front matter. "Last updated" is the newest changelog entry. All changes (including "fix typo") are tracked. The source repo is public, so old versions are not kept.

Pages without `published` (home, About me, Impressum) are not articles but are based on the same template.

Math is Markdown LaTex, converted to MathML at build time. Code is highlighted at build time, the colours are in the CSS. 
Currently nothing uses JS. Eventually maybe some e.g. calculators might. Minimalism here as well.

## Looks

Browser defaults. Minimal CSS: a readable column width, images that shrink to the column, scrolling for code & equations, a site title and code colours.

The site title is large and links home. It is a paragraph, not a heading, so every page keeps its own single `h1`, and the home page has none. The favicon sits in front of it, larger than the text and hanging below the baseline.

`static/favicon.svg` is a spectrum analyser screen: a rounded frame, a noisy floor, one carrier peak. It is square, turns white on dark themes, and there is no `favicon.ico`.

## Requests

To reduce load times, all resources must be embedded in or linked to directly from the main html. This way no more than two round trips must ever be made.

## Pages and URLs

| URL | Source | Purpose |
| --- | --- | --- |
| `/` | `content/home.md` | Home page with links to the rest |
| `/articles/` | written by `build.py` | Article list, newest first |
| `/<slug>/` | `content/<slug>.md` or `content/<slug>/index.md` | An article or a page |
| `/<slug>/<file>` | `content/<slug>/<file>` | A figure or data file of that article |
| `/about-me/` | `content/about-me/index.md` | Biography |
| `/impressum/` | `content/impressum.md` | Impressum and privacy note |
| `/feed.xml` | written by `build.py` | Atom feed |

Every page is `<slug>/index.html`. The footer links to Home, Articles, About me, Feed and the Impressum. A slug exists once, as a file or as a folder, `build.py` stops otherwise.

Links in content are root-relative (`/articles/`), so they work in the local preview and survive a domain change. Only the feed gets absolute links, from `build.py`. Links relative to the article folder resolve against that folder.

The feed is Atom with the 20 newest articles in full. `SITE_URL` in the Makefile names the domain, run `make clean` after changing it.

## Replies and legal

Each article ends with a "Reply by email" link with a prefilled subject. Site and Impressum use different `+tag` addresses, to trace spam. Mastodon or Webmentions maybe later.

Impressum and privacy note share one page. No cookies, no third parties, so the note only names GitHub as host.

## Writing and publishing

Unpublished work stays out of this public repo. Drafts, raw data and the plot scripts live in the private `writing` repo, one folder per article. A finished article with figures goes to `content/<slug>/index.md` with its files next to it, referenced by relative path. Without extra files it stays a single `content/<slug>.md`.

To publish: branch `article/<slug>`, copy the files in, add `published` and the first `changelog` entry, check with `make serve`, merge into `main` as a fast-forward, then `git push origin main:deploy`.

## Hosting and domain

The site is hosted on GitHub Pages. It is deployed by Actions (`.github/workflows/pages.yml`) when the branch `deploy` is pushed. `main` is for working.

dd4js.com has `A` and `AAAA` records for GitHub Pages IPs on the apex and a `CNAME` from `www` to the `github.io` address. DNS only, no proxy since otherwise GitHub cannot issue the certificate.

## Rejected or deferred

- Typst HTML export: experimental.
- SSGs: overkill.
- Codeberg/... Pages: TLS-problems, too new.
- Comment widgets: JS & third parties.
- More theming: looks worse, larger filesize, less accesibility.
- Inlining stylesheet: other additional files like images and even the favicon itself negate any benefits.

## Open

`hello-world` is a placeholder article.

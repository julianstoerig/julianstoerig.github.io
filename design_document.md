# Design document

How dd4js.com is built, and why. Each entry gives the choice and the reason for it, so that a later change can start from the reason.

## Goal

A tiny, fast, accessible personal site for things worth keeping, sharing, or not retelling: amateur radio, electrical and RF engineering, programming.

This gives four principles. The site stays small, with few tools, few files and little CSS, because that is less to maintain and less to break. Every page works without JavaScript. The host only serves files, so moving means changing the deploy step. Visitors make requests to one host only, so there are no web fonts and no analytics.

## Build

There is no site framework. The site is built with pandoc, a Makefile and one short Python script that uses only the standard library. A framework (Hugo was the alternative) is more than a handful of pages and a feed need, and each dependency is one more thing that can break.

`build.py` asks pandoc for each article's metadata as JSON, through the one-line template `templates/meta.json`. The standard library has no YAML parser, and parsing a subset by hand would restrict the front matter and add code to maintain. Pandoc parses the front matter anyway.

The pandoc version is pinned. `tools/install-pandoc.sh` installs one exact release into `~/.local` and checks its SHA-256. CI runs the same script, and the Makefile prefers that binary over any system one. The same input must give the same output on every machine, and a distribution's older pandoc has already failed once on a flag it did not know.

## Content

Articles are evergreen. Each has a `published` date and a hand-written `changelog` in the front matter, and "last updated" is the newest changelog entry. Only meaningful edits count, so a typo fix does not. The reader sees what changed and when, and the date means something.

A page without `published` is not an article and stays out of the article list and the feed. The Impressum and the About me page are such pages. This is one rule, where the alternative would be a separate list of special pages.

The language is English.

## Math and code

Math is kept. It is written as LaTeX in Markdown and converted to MathML at build time, with no JavaScript and no math libraries. The subject needs equations, and MathML renders natively.

Code blocks are highlighted at build time. Pandoc emits token classes and our CSS supplies the colours for light and dark. This costs nothing at runtime and needs no script. The colours are the only part of the CSS that goes beyond browser defaults, because browsers do not colour code.

JavaScript is allowed only for optional extras such as a calculator. Reading a page never depends on it.

## Look

The stylesheet relies on browser defaults. It sets only what the defaults do not give: the browser's own light or dark scheme (`color-scheme: light dark`), a text column of readable width, scrolling for wide code and equations, and the code colours. The aim is to change less, not to imitate the default look with more CSS, so fonts, colours and dark mode are decided by the reader's browser.

The favicon is one SVG file, `static/favicon.svg`: a spectrum-analyser trace, a flat noise floor with small ripples and one narrow carrier spike in the middle. A vector icon stays sharp at any size and is a few hundred bytes. It is drawn in one colour with plain attributes, and a `prefers-color-scheme` rule inside the file turns it white on dark browser themes. There is no `favicon.ico`, because current browsers take the SVG.

The same file is shown beside the heading of the home page. A page asks for this with `icon: /favicon.svg` in its front matter, and the template adds a decorative image of fixed size in front of the title. Sizing it with attributes means no CSS is needed.

Lists have no place in the markup of the article list or the changelog. Their entries are plain paragraphs.

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

The footer on every page links to Home, Articles, About me, Feed and the Impressum. Every page links to everything, so no further navigation is needed. Each page is written as `<slug>/index.html`, which gives clean URLs.

Links in content are root-relative, such as `/articles/`. They work in the local preview and survive a domain change. Only the feed gets absolute links, which `build.py` rewrites, because feed readers have no site to resolve relative links against. Root-relative links are resolved against the site and relative links such as `figure.svg` against the article's folder. Anchors, links with a scheme and protocol-relative links stay as they are.

## Feed

The feed is Atom, holds the 20 most recently published articles, and contains their full content. `SITE_URL` in the Makefile is the one place that names the domain. Changing it needs `make clean`, since the Makefile is not a dependency of the output.

## Replies

Each article ends with a "Reply by email" link with a prefilled subject. That needs no comment system, and so no JavaScript and no third party. Mastodon or Webmentions can be added later.

The site and the Impressum use different `+tag` addresses. The tag shows where an address was harvested, which helps to trace spam.

## Writing and publishing

Unpublished work does not belong in this repository. It is public, and anything committed to a pushed branch is visible and stays in the history. Drafts, raw measurements and the scripts that produce the figures live in a separate private repository, `writing`, with one folder per article. Only the finished article and the figures it needs are copied here.

An article with figures or data is a folder, `content/<slug>/index.md`, with those files next to it. The article is published at `/<slug>/` and the other files at `/<slug>/<file>`, so the text refers to them by relative path, for example `![](figure.svg)`. A page without extra files stays a single `content/<slug>.md`. Keeping an article and its files in one folder means that removing the article removes its files too.

To publish, make a branch `article/<slug>`, copy the article and its figures into `content/<slug>/`, and add `published` and the first `changelog` entry to the front matter. Then check the result with `make serve`, merge into `main` as a fast-forward and push `main` to `deploy`.

A slug may exist only once, either as a file or as a folder. `build.py` stops with an error if both exist.

## Hosting and deployment

The site is hosted on GitHub Pages and deployed by GitHub Actions (`.github/workflows/pages.yml`). It is free and reliable, and it only serves files.

The workflow runs when `deploy` is pushed. `main` is the working branch, and publishing is `git push origin main:deploy`. That keeps publishing a deliberate step, apart from committing.

The Pages source is "GitHub Actions", not "Deploy from a branch". A branch deploy would serve the raw Markdown, because the built output is not in the repository.

## Domain

The domain is dd4js.com, after the callsign. The apex has `A` and `AAAA` records that point at GitHub Pages, and `www` is a `CNAME` to the `github.io` address. GitHub redirects `www` and the old address to the apex.

DNS runs without a proxy at the DNS provider, because GitHub cannot issue the HTTPS certificate through one. The custom domain is set in the repository's Pages settings. A `CNAME` file in the repository is ignored for Actions deploys.

## Legal

One page, `/impressum/`, holds the Impressum that German law requires and a short privacy note. The site sets no cookies and loads nothing from third parties, so the note is short. It names GitHub as the host and its server logs.

## Build flow

1. `make` renders every `content/<slug>.md` and `content/<slug>/index.md` to `_site/<slug>/index.html` with one pandoc template, MathML for math (`--math-method=mathml`) and class-based syntax highlighting. `content/home.md` goes to `_site/index.html`.
2. `build.py` reads the metadata of every article through pandoc, then writes `_site/articles/index.html` and `_site/feed.xml`.
3. The other files in an article folder are copied next to its page, and files in `static/` are copied unchanged. File names must not contain spaces, because make cannot handle them.
4. In CI the workflow installs the pinned pandoc, runs `make` and uploads `_site` to Pages.

## Rejected or deferred

- Typst HTML export: experimental, and likely to break.
- Hugo: workable, but more framework than needed.
- Codeberg Pages: was moving to a new system and had custom-domain certificate problems reported in 2026.
- Comment widgets (Giscus, Disqus): they need JavaScript and third parties.
- Mastodon and Webmentions for replies: possible later.
- A hand-picked colour scheme and fonts: dropped in favour of browser defaults, to keep the CSS small.

## Open

The sample article `hello-world` is placeholder content and should be replaced by a real article.

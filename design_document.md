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

Lists have no place in the markup of the article list or the changelog. Their entries are plain paragraphs.

## Pages and URLs

| URL | Source | Purpose |
| --- | --- | --- |
| `/` | `content/home.md` | Home page with links to the rest |
| `/articles/` | written by `build.py` | Article list, newest first |
| `/<slug>/` | `content/<slug>.md` | An article or a page |
| `/about-me/` | `content/about-me.md` | Biography |
| `/impressum/` | `content/impressum.md` | Impressum and privacy note |
| `/feed.xml` | written by `build.py` | Atom feed |

The footer on every page links to Home, Articles, About me, Feed and the Impressum. Every page links to everything, so no further navigation is needed. Each page is written as `<slug>/index.html`, which gives clean URLs.

Links in content are root-relative, such as `/articles/`. They work in the local preview and survive a domain change. Only the feed gets absolute links, which `build.py` rewrites, because feed readers have no site to resolve relative links against.

## Feed

The feed is Atom, holds the 20 most recently published articles, and contains their full content. `SITE_URL` in the Makefile is the one place that names the domain. Changing it needs `make clean`, since the Makefile is not a dependency of the output.

## Replies

Each article ends with a "Reply by email" link with a prefilled subject. That needs no comment system, and so no JavaScript and no third party. Mastodon or Webmentions can be added later.

The site and the Impressum use different `+tag` addresses. The tag shows where an address was harvested, which helps to trace spam.

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

1. `make` renders every `content/*.md` to `_site/<slug>/index.html` with one pandoc template, MathML for math (`--math-method=mathml`) and class-based syntax highlighting. `content/home.md` goes to `_site/index.html`.
2. `build.py` reads the metadata of every article through pandoc, then writes `_site/articles/index.html` and `_site/feed.xml`.
3. Files in `static/` are copied unchanged.
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

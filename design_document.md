# Design document

How dd4js.com is built, and why. Each entry gives the choice and the reason for it, so a later change can start from the reason.

## Goal

A tiny, fast, accessible personal site for things worth keeping, sharing, or not retelling: amateur radio, electrical and RF engineering, programming.

Principles that follow from this:

- **Small.** Few tools, few files, little CSS. Less to maintain and less to break.
- **Works without JavaScript.** Every page loads and reads fully without it.
- **Portable.** The host only serves files, so moving is a matter of changing the deploy step.
- **No third parties.** No web fonts, no analytics, no embeds. Visitors make requests to one host only.

## Decisions

### Build

- **No site framework.** Pandoc, a Makefile and one short Python script that uses only the standard library.
  *Why:* a framework (Hugo was the alternative) is more than a few pages and a feed need, and every dependency is something that can break.
- **Pandoc reads the front matter.** `build.py` asks pandoc for the metadata as JSON, through a one-line template (`templates/meta.json`).
  *Why:* the standard library has no YAML parser. Parsing a subset by hand would restrict the front matter, and it would be code to maintain. Pandoc has to parse the front matter anyway.
- **Pandoc version pinned.** `tools/install-pandoc.sh` installs one exact release into `~/.local` and checks its SHA-256. CI runs the same script, and the Makefile prefers that binary over any system one.
  *Why:* the same input must give the same output on every machine. A distribution's older pandoc already failed once on a flag that did not exist there.

### Content

- **Evergreen articles.** Each has a `published` date and a hand-written `changelog` in the front matter. "Last updated" is the newest changelog entry. Only meaningful edits count; typo fixes do not.
  *Why:* the reader sees what changed and when, and the date means something.
- **A page without `published` is not an article.** It is left out of the article list and the feed. The Impressum and the About me page are such pages.
  *Why:* one rule instead of a separate list of special pages.
- **Language:** English.

### Math and code

- **Math is kept.** LaTeX in Markdown, converted to MathML at build time. No JavaScript and no math libraries.
  *Why:* the subject needs equations, and native MathML renders without any script.
- **Code is highlighted at build time.** Pandoc emits token classes; the colours are in our CSS, for light and dark.
  *Why:* no runtime cost, no script. The colours are the one place the CSS goes beyond browser defaults, because browsers do not colour code.

### JavaScript

- **Allowed only as optional extras**, for example a calculator. Reading a page never depends on it.

### Look

- **Browser defaults.** The stylesheet only sets what the defaults do not provide: the browser's own light or dark scheme (`color-scheme: light dark`), a text column of readable width, scrolling for wide code and equations, and the code colours.
  *Why:* the aim is to change less, not to imitate the default look with more CSS. The reader's browser decides fonts, colours and dark mode.
- **No decorative markup.** Lists and bullets are not used for the article list or the changelog; entries are plain paragraphs.

### Pages and URLs

| URL | Source | Purpose |
| --- | --- | --- |
| `/` | `content/home.md` | Home page with links to the rest |
| `/articles/` | written by `build.py` | Article list, newest first |
| `/<slug>/` | `content/<slug>.md` | An article or a page |
| `/about-me/` | `content/about-me.md` | Biography |
| `/impressum/` | `content/impressum.md` | Impressum and privacy note |
| `/feed.xml` | written by `build.py` | Atom feed |

- **Footer on every page:** Home, Articles, About me, Feed, Impressum & privacy. *Why:* every page links to everything, so no navigation structure is needed.
- **Clean URLs.** Each page is `<slug>/index.html`.
- **Links in content are root-relative** (`/articles/`). Only the feed gets absolute links, rewritten in `build.py`.
  *Why:* relative links work in the local preview and survive a domain change. Feed readers have no site to resolve them against.

### Feed

- Atom, the 20 most recently *published* articles, full content.
- `SITE_URL` in the Makefile is the one place that names the domain. Changing it needs `make clean`, since the Makefile is not a dependency of the output.

### Replies

- Each article ends with a "Reply by email" link with a prefilled subject.
  *Why:* no comment system, no JavaScript, no third party. Mastodon or Webmentions can be added later.
- **Tagged addresses.** The site and the Impressum use different `+tag` addresses.
  *Why:* the tag shows where an address was harvested, which helps trace spam.

### Hosting and deployment

- **GitHub Pages, deployed by GitHub Actions** (`.github/workflows/pages.yml`).
  *Why:* free, reliable, and it only serves files.
- **Deploys happen when `deploy` is pushed.** `main` is the working branch. Publishing is `git push origin main:deploy`.
  *Why:* publishing is a deliberate step, separate from committing.
- **Pages source is "GitHub Actions"**, not "Deploy from a branch". A branch deploy would serve the raw Markdown, because the built output is not in the repo.

### Domain

- **dd4js.com**, the callsign. Apex `A` and `AAAA` records point at GitHub Pages, and `www` is a `CNAME` to the `github.io` address. GitHub redirects `www` and the old address to the apex.
- **DNS only, no proxy** at the DNS provider. *Why:* GitHub cannot issue the HTTPS certificate through a proxy.
- **The custom domain is set in the repository's Pages settings.** A `CNAME` file in the repo is ignored for Actions deploys.

### Legal

- One page, `/impressum/`: the Impressum as German law requires, plus a short privacy note. The site sets no cookies and loads nothing from third parties, so the note is short. It names GitHub as the host and its server logs.

## Build flow

1. `make` renders every `content/*.md` to `_site/<slug>/index.html` with one pandoc template, `--math-method=mathml`, and class-based syntax highlighting. `content/home.md` goes to `_site/index.html`.
2. `build.py` reads the metadata of every article through pandoc, then writes `_site/articles/index.html` and `_site/feed.xml`.
3. Files in `static/` are copied unchanged.
4. In CI the workflow installs the pinned pandoc, runs `make`, and uploads `_site` to Pages.

## Rejected or deferred

- **Typst HTML export:** experimental, and likely to break.
- **Hugo:** workable, but more framework than needed.
- **Codeberg Pages:** was moving to a new system and had custom-domain certificate problems reported in 2026.
- **Comment widgets (Giscus, Disqus):** need JavaScript and third parties.
- **Mastodon and Webmentions for replies:** possible later.
- **Hand-picked colour scheme and fonts:** dropped in favour of browser defaults, to keep the CSS small.

## Open

- The sample article `hello-world` is placeholder content and should be replaced by a real article.

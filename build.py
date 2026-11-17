#!/usr/bin/env python3
"""Build the index page and Atom feed from content/*.md.

Pandoc does all the Markdown work, including reading the front matter
(via templates/meta.json), so this script needs only the standard library.
Configuration comes from the environment (set by the Makefile).
"""
import html
import json
import os
import subprocess
from pathlib import Path

PANDOC = os.environ.get("PANDOC", "pandoc")
SITE_TITLE = os.environ["SITE_TITLE"]
SITE_URL = os.environ["SITE_URL"].rstrip("/")
AUTHOR = "Julian Störig"
FEED_LIMIT = 20

CONTENT = Path("content")
OUT = Path("_site")


def pandoc(*args, stdin=None):
    """Run pandoc and return its output as text."""
    result = subprocess.run(
        [PANDOC, *args], input=stdin, text=True, check=True, stdout=subprocess.PIPE
    )
    return result.stdout


def load_article(path):
    """Return a dict describing one article, or None if it is not published.

    Text fields (title, summary, changelog notes) are HTML strings,
    as rendered by pandoc.
    """
    meta = json.loads(
        pandoc("--from", "markdown", "--to", "html5", "--template", "templates/meta.json", str(path))
    )
    if "published" not in meta:
        return None  # e.g. the Impressum: a page, not an article

    changelog = meta.get("changelog", [])
    return {
        "slug": path.stem,
        "title": meta["title"],
        "summary": meta.get("summary", ""),
        "published": meta["published"],
        # "Last updated" is the newest changelog entry, else the publication date.
        "updated": max([meta["published"]] + [entry["date"] for entry in changelog]),
        "body": pandoc(
            "--from", "markdown", "--to", "html5", "--math-method=mathml", "--wrap=none", str(path)
        ),
    }


def write_index(articles):
    items = "\n".join(
        f'<p><a href="/{a["slug"]}/">{a["title"]}</a>'
        f' <time datetime="{a["published"]}">{a["published"]}</time><br>{a["summary"]}</p>'
        for a in articles
    )
    page = pandoc(
        "--from", "markdown", "--to", "html5", "--standalone",
        "--template", "templates/page.html",
        "--variable", "lang=en",
        "--variable", f"site-title={SITE_TITLE}",
        "--metadata", "title=Articles",
        stdin=items + "\n",
    )
    (OUT / "index.html").write_text(page)


def atom_date(date):
    return f"{date}T00:00:00Z"


def absolute(body):
    """Make root-relative links absolute: feed readers have no site to resolve them against."""
    return body.replace('href="/', f'href="{SITE_URL}/').replace('src="/', f'src="{SITE_URL}/')


def write_feed(articles):
    recent = articles[:FEED_LIMIT]
    entries = "\n".join(
        f"""<entry>
<id>{SITE_URL}/{a["slug"]}/</id>
<link href="{SITE_URL}/{a["slug"]}/"/>
<title type="html">{html.escape(a["title"])}</title>
<published>{atom_date(a["published"])}</published>
<updated>{atom_date(a["updated"])}</updated>
<summary type="html">{html.escape(a["summary"])}</summary>
<content type="html">{html.escape(absolute(a["body"]))}</content>
</entry>"""
        for a in recent
    )
    feed = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<id>{SITE_URL}/</id>
<link href="{SITE_URL}/"/>
<link rel="self" href="{SITE_URL}/feed.xml"/>
<title>{html.escape(SITE_TITLE)}</title>
<author><name>{html.escape(AUTHOR)}</name></author>
<updated>{atom_date(max(a["updated"] for a in recent))}</updated>
{entries}
</feed>
"""
    (OUT / "feed.xml").write_text(feed)


def main():
    articles = [load_article(path) for path in sorted(CONTENT.glob("*.md"))]
    articles = [a for a in articles if a]
    articles.sort(key=lambda a: a["published"], reverse=True)
    OUT.mkdir(exist_ok=True)
    write_index(articles)
    write_feed(articles)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the static Pasteroll site from reviewed source fragments."""
from pathlib import Path
import html
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site"

PAGES = {
    "home": {
        "output": "index.html",
        "title": "Pasteroll: an earlier copy at the pointer",
        "description": "Pasteroll keeps a searchable history of text, files and images for Windows and Linux X11. Press Ctrl, Shift and middle-click to open an earlier copy at the pointer. An experimental GNOME 46 Wayland build is available.",
        "path": "/",
        "nav": "home",
    },
    "features": {
        "output": "features/index.html",
        "title": "Pasteroll features: search, favorites, multi-paste and image editing",
        "description": "Search clipboard history, keep favorites and rolls, join clips for one paste, edit images locally, and share selected rolls with a coding agent over MCP.",
        "path": "/features/",
        "nav": "features",
    },
    "download": {
        "output": "download/index.html",
        "title": "Download — Pasteroll",
        "description": "Download Pasteroll for Windows 10 or 11, Linux X11 or XWayland, or the experimental GNOME 46 Wayland build.",
        "path": "/download/",
        "nav": "download",
    },
    "guide": {
        "output": "guide/index.html",
        "title": "Guide — Pasteroll",
        "description": "Install Pasteroll on Windows or Linux, set up the experimental GNOME 46 companion, find the keyboard shortcuts, update the app and fix common problems.",
        "path": "/guide/",
        "nav": "guide",
    },
    "privacy": {
        "output": "privacy/index.html",
        "title": "Privacy — Pasteroll",
        "description": "How Pasteroll encrypts clips, protects its key, uses the network, and lets a local MCP server share selected rolls with a coding agent.",
        "path": "/privacy/",
        "nav": "privacy",
    },
    "changelog": {
        "output": "changelog/index.html",
        "title": "Beta builds for Windows and Linux — Pasteroll",
        "description": "Pasteroll beta release notes for Windows and Linux, newest first, with dates, platforms, downloads and commit history.",
        "path": "/changelog/",
        "nav": "changelog",
    },
}

NAV = [
    ("features", "/features/", "Features"),
    ("guide", "/guide/", "Guide"),
    ("changelog", "/changelog/", "Changelog"),
]

GITHUB = "https://github.com/qpd-v/pasteroll"

def load(name):
    return json.loads((SRC / name).read_text(encoding="utf-8"))

def validate_release(data):
    required = {"version", "release_url", "checksums_url", "download_base", "assets"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"release.json is missing: {', '.join(sorted(missing))}")
    assets = data["assets"]
    expected = {"windows_setup", "windows_portable", "linux_archive", "linux_deb", "gnome_archive", "gnome_deb"}
    if set(assets) != expected or not all(isinstance(v, str) and v for v in assets.values()):
        raise ValueError("release.json must name the six user-facing downloads")
    if not all(name.startswith("pasteroll") for name in assets.values()):
        raise ValueError("release asset names look incomplete")

def nav_html(current):
    links = []
    for key, href, label in NAV:
        active = ' aria-current="page"' if key == current else ""
        links.append(f'<a href="{href}"{active}>{label}</a>')
    links.append(f'<a class="nav-download" href="/download/"{" aria-current=\"page\"" if current == "download" else ""}>Download</a>')
    return "".join(links)

def header(current):
    return f'''<header class="site-header">
  <div class="shell header-inner">
    <a class="brand" href="/" aria-label="Pasteroll home">
      <img src="/assets/favicon-64.png" width="30" height="30" alt="">
      <span>pasteroll</span>
    </a>
    <button class="menu-button" type="button" aria-expanded="false" aria-controls="site-menu">
      <span class="menu-icon" aria-hidden="true"></span><span>Menu</span>
    </button>
    <nav class="site-nav" id="site-menu" aria-label="Main navigation">
      {nav_html(current)}
      <a class="nav-github" href="{GITHUB}" rel="noopener">GitHub <span aria-hidden="true">↗</span></a>
    </nav>
  </div>
</header>'''

def footer(release):
    return f'''<footer class="site-footer">
  <div class="shell footer-grid">
    <div class="footer-brand">
      <a class="brand" href="/" aria-label="Pasteroll home"><img src="/assets/favicon-64.png" width="28" height="28" alt=""><span>pasteroll</span></a>
      <p>A clipboard history for Windows and Linux. Open source under MIT or Apache-2.0.</p>
    </div>
    <div class="footer-links">
      <div><h2>Use Pasteroll</h2><a href="/features/">Features</a><a href="/download/">Download</a><a href="/guide/">Guide</a></div>
      <div><h2>Source</h2><a href="/changelog/">Release notes</a><a href="{GITHUB}" rel="noopener">GitHub</a><a href="{GITHUB}/issues" rel="noopener">Report a bug</a></div>
      <div><h2>Policies</h2><a href="/privacy/">Privacy</a><a href="{GITHUB}/blob/main/SECURITY.md" rel="noopener">Security</a><a href="{GITHUB}/blob/main/LICENSE-MIT" rel="noopener">License</a></div>
    </div>
    <div class="footer-bottom">
      <p>Pasteroll {html.escape(release["version"])} · MIT or Apache-2.0</p>
    </div>
  </div>
</footer>'''

def layout(meta, body, release):
    canonical = "https://pasteroll.com" + meta["path"]
    return f'''<!doctype html>
<html lang="en" class="no-js" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(meta["title"])}</title>
<meta name="description" content="{html.escape(meta["description"])}">
{('<meta name="robots" content="noindex">' if meta.get('robots') else '')}
<meta name="theme-color" content="#1f1713">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="64x64" href="/assets/favicon-64.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Pasteroll">
<meta property="og:title" content="{html.escape(meta["title"])}">
<meta property="og:description" content="{html.escape(meta["description"])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://pasteroll.com/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{header(meta["nav"])}
<main id="main">{body}</main>
{footer(release)}
<script src="/script.js" defer></script>
</body>
</html>
'''

def tokens(release):
    data = {"version": release["version"], "release_url": release["release_url"],
            "checksums_url": release["checksums_url"]}
    for key, name in release["assets"].items():
        data[key] = release["download_base"] + name
        data[key + "_name"] = name
    return data

def render_fragment(name, release):
    text = (SRC / "pages" / f"{name}.html").read_text(encoding="utf-8")
    for key, value in tokens(release).items():
        text = text.replace("{{" + key + "}}", html.escape(value, quote=True))
    return text

def changelog_body(releases):
    items = []
    for index, release in enumerate(releases):
        tags = "".join(f'<span class="tag">{html.escape(p.strip())}</span>' for p in release["platforms"].split("and"))
        bullets = "".join(f"<li>{html.escape(x)}</li>" for x in release["summary"])
        featured = " featured" if index == 0 else ""
        items.append(f'''<article class="release{featured}">
  <div class="release-head"><p class="eyebrow">{html.escape(release["date"])}</p><h2>{html.escape(release["version"])}</h2><div class="tags">{tags}</div></div>
  <ul>{bullets}</ul>
  <a class="text-link" href="{html.escape(release["url"])}" rel="noopener" aria-label="Open the Pasteroll {html.escape(release["version"])} release tag on GitHub">Release tag, downloads and commits on GitHub <span aria-hidden="true">↗</span></a>
</article>''')
    return f'''<section class="page-hero compact"><div class="shell"><h1>Pasteroll beta builds for Windows and Linux</h1><p class="lede">Builds appear newest first. Each entry gives its release date, version and platforms, then links to its GitHub release for downloads and the full commit history. Older versions are in the <a href="{GITHUB}/commits/main" rel="noopener">repository history</a>.</p></div></section>
<section class="section"><div class="shell release-list">{''.join(items)}</div></section>'''

def sitemap():
    urls = "".join(f"  <url><loc>https://pasteroll.com{meta['path']}</loc></url>\n" for meta in PAGES.values())
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>
'''

def main():
    release = load("release.json")
    validate_release(release)
    releases = load("releases.json")
    for key, meta in PAGES.items():
        if key == "changelog":
            body = changelog_body(releases)
        else:
            body = render_fragment(key, release)
        out = ROOT / meta["output"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(layout(meta, body, release), encoding="utf-8", newline="\n")
    (ROOT / "404.html").write_text(layout({
        "title": "Page not found — Pasteroll",
        "description": "There is no page at this address.",
        "path": "/404.html",
        "nav": "",
        "robots": True,
    }, '''<section class="lost"><img src="/assets/favicon-64.png" width="64" height="64" alt=""><p class="eyebrow">404</p><h1>There is no page at this address</h1><p class="lede">It may have moved, or a character in the address may be wrong.</p><a class="button primary" href="/">Go to the Pasteroll home page</a></section>''', release), encoding="utf-8", newline="\n")
    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8", newline="\n")
    print(f"built {len(PAGES) + 1} pages for {release['version']}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Builds changelog/index.html from the commits of github.com/qpd-v/pasteroll.

Plain Python 3, standard library only. The page it writes is static HTML (nothing is fetched
when someone visits the site), so it keeps the site's "no outside requests" promise.

    python scripts/changelog.py                     read the commits from GitHub, write the page
    python scripts/changelog.py --local ../pasteroll   read them from a local clone instead
    python scripts/changelog.py --keep-on-error     if GitHub cannot be reached, leave the
                                                    existing page alone and exit normally
                                                    (what a hosting build should use)

Set GITHUB_TOKEN to raise GitHub's rate limit (not needed for a few builds an hour).

How each commit is shown: its subject is the heading; the bullet lines of its message ("- ...")
are the list under it; any plain paragraph of the message is shown above the list. Git trailers
at the end of a message (Co-Authored-By: and the like) are left out.
"""
import argparse
import datetime
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "qpd-v/pasteroll"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "changelog", "index.html")


# ------------------------------------------------------------------ reading the commits
def from_github(repo, token):
    commits, page = [], 1
    while True:
        url = f"https://api.github.com/repos/{repo}/commits?per_page=100&page={page}"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "pasteroll-site-changelog",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.load(r)
        for c in batch:
            commits.append({
                "sha": c["sha"],
                "url": c["html_url"],
                "date": c["commit"]["author"]["date"],
                "message": c["commit"]["message"],
            })
        if len(batch) < 100:
            return commits
        page += 1


def from_local(path, repo):
    fmt = "%H%x1f%aI%x1f%B%x1e"
    out = subprocess.run(["git", "-C", path, "log", "main", f"--format={fmt}"], check=True,
                         capture_output=True, text=True, encoding="utf-8").stdout
    commits = []
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec.strip():
            continue
        sha, date, message = rec.split("\x1f", 2)
        commits.append({"sha": sha.strip(), "url": f"https://github.com/{repo}/commit/{sha.strip()}",
                        "date": date, "message": message})
    return commits


# ------------------------------------------------------------------ understanding a message
TRAILER = re.compile(r"^[A-Za-z][A-Za-z-]*: \S")


def parse_message(message):
    """(subject, [paragraphs], [bullets])"""
    lines = message.replace("\r\n", "\n").strip().split("\n")
    subject = lines[0].strip()
    body = lines[1:]
    # drop a trailing block of git trailers
    while body and not body[-1].strip():
        body.pop()
    j = len(body)
    while j > 0 and TRAILER.match(body[j - 1]):
        j -= 1
    if j < len(body) and (j == 0 or not body[j - 1].strip()):
        body = body[:j]
    paragraphs, bullets, para = [], [], []

    def flush():
        if para:
            paragraphs.append(" ".join(s.strip() for s in para))
            para.clear()

    for line in body:
        if not line.strip():
            flush()
        elif re.match(r"^\s*[-*] ", line):
            flush()
            bullets.append(re.sub(r"^\s*[-*] ", "", line).strip())
        elif line.startswith("  ") and bullets and not para:
            bullets[-1] += " " + line.strip()
        else:
            para.append(line)
    flush()
    return subject, paragraphs, bullets


def day_of(iso):
    """The calendar day in UTC (GitHub reports UTC; a local clone must agree with it)."""
    t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if t.tzinfo is not None:
        t = t.astimezone(datetime.timezone.utc)
    return t.date().isoformat()


def long_date(day):
    d = datetime.date.fromisoformat(day)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


# ------------------------------------------------------------------ writing the page
GITHUB_ICON = ('<svg class="gh" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path fill="currentColor" '
               'd="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')

PAGE = """<!doctype html>
<html lang="en" data-theme="cinnamon">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Changelog · Pasteroll</title>
<meta name="description" content="Every change to Pasteroll, taken from the commits in its GitHub repository.">
<meta name="theme-color" content="#1f1713">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:title" content="Pasteroll changelog">
<meta property="og:description" content="Every change to Pasteroll, from the commits in its GitHub repository.">
<meta property="og:url" content="https://pasteroll.com/changelog/">
<meta property="og:image" content="https://pasteroll.com/assets/og.png">
<link rel="stylesheet" href="/styles.css">
<script src="/theme-init.js"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="top">
  <div class="wrap bar">
    <a class="brand" href="/" aria-label="Pasteroll, home">
      <img src="/assets/favicon-64.png" width="28" height="28" alt="">
      <span>pasteroll</span>
    </a>
    <nav aria-label="Sections">
      <a href="/#how">How it works</a>
      <a href="/#features">Features</a>
      <a href="/#privacy">Privacy</a>
      <a href="/#download">Download</a>
      <a href="/#faq">FAQ</a>
      <a class="keep" href="/changelog/" aria-current="page">Changelog</a>
      <a class="keep nav-gh" href="https://github.com/__REPO__">__ICON__ GitHub</a>
    </nav>
  </div>
</header>

<main id="main" class="wrap">
  <section class="log-head">
    <h1>Changelog</h1>
    <p class="lead">Every change to Pasteroll, generated from its <a href="https://github.com/__REPO__/commits/main">commit history on GitHub</a>.</p>
  </section>

  <ol class="log">
__DAYS__
  </ol>
</main>

<footer class="foot">
  <div class="wrap foot-in">
    <p>__COUNT__ commits, latest <a href="__LATEST_URL__">__LATEST__</a>.</p>
    <nav aria-label="Project links">
      <a href="https://github.com/__REPO__">GitHub</a>
      <a href="https://github.com/__REPO__/issues">Report an issue</a>
      <a href="https://github.com/__REPO__/blob/main/CHANGELOG.md">Release notes</a>
      <a href="https://github.com/__REPO__/blob/main/PRIVACY.md">Privacy</a>
      <a href="https://github.com/__REPO__/blob/main/SECURITY.md">Security</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""


def render(commits, repo):
    esc = html.escape
    by_day = {}
    for c in commits:
        by_day.setdefault(day_of(c["date"]), []).append(c)
    days = []
    for day in sorted(by_day, reverse=True):
        arts = []
        for c in by_day[day]:
            subject, paragraphs, bullets = parse_message(c["message"])
            url = esc(c["url"], quote=True)
            parts = ['        <article class="commit">',
                     f'          <div class="commit-head"><h2>{esc(subject)}</h2> '
                     f'<a class="hash" href="{url}" title="View this commit on GitHub">{esc(c["sha"][:7])}</a></div>']
            for p in paragraphs:
                parts.append(f"          <p>{esc(p)}</p>")
            if bullets:
                parts.append("          <ul>")
                for b in bullets:
                    parts.append(f"            <li>{esc(b)}</li>")
                parts.append("          </ul>")
            parts.append("        </article>")
            arts.append("\n".join(parts))
        days.append(f'    <li class="day">\n      <time datetime="{day}">{long_date(day)}</time>\n      <div class="day-body">\n'
                    + "\n".join(arts) + "\n      </div>\n    </li>")
    latest = commits[0]
    page = PAGE
    for k, v in {"__REPO__": repo, "__ICON__": GITHUB_ICON, "__DAYS__": "\n".join(days), "__COUNT__": str(len(commits)),
                 "__LATEST__": latest["sha"][:7], "__LATEST_URL__": html.escape(latest["url"], quote=True)}.items():
        page = page.replace(k, v)
    return page


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--local", metavar="PATH", help="read the commits from this local clone")
    ap.add_argument("--keep-on-error", action="store_true")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    try:
        commits = from_local(args.local, args.repo) if args.local else from_github(args.repo, os.environ.get("GITHUB_TOKEN"))
        if not commits:
            raise RuntimeError("no commits found")
    except (urllib.error.URLError, subprocess.CalledProcessError, RuntimeError, OSError, ValueError, KeyError) as e:
        print(f"changelog: could not read the commits: {e}", file=sys.stderr)
        if args.keep_on_error and os.path.exists(args.out):
            print("changelog: keeping the existing page", file=sys.stderr)
            return 0
        return 1
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    page = render(commits, args.repo)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    print(f"changelog: {len(commits)} commits -> {os.path.relpath(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

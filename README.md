# pasteroll.com

The Pasteroll website: plain generated HTML, CSS and a small script. No framework,
no runtime dependencies and no external requests.

## Source layout

| Path | Purpose |
|---|---|
| `site/pages/` | Home, Features, Download, Guide and Privacy content |
| `site/release.json` | Current version, release URLs and the six download asset names |
| `site/releases.json` | Reviewed release summaries used by the changelog |
| `scripts/build_site.py` | Shared layout, validation and page generation |
| `scripts/changelog.py` | Deployment-compatible wrapper that runs the site build |
| generated root pages | `index.html`, `features/`, `download/`, `guide/`, `privacy/`, `changelog/`, `404.html`, `sitemap.xml` |
| `assets/shots/` | Product screenshots captured with synthetic clipboard data |
| `assets/fonts/` | Locally hosted Source Sans 3 and its OFL license |

`site/` and `scripts/` are development sources. Keep both excluded from deployment
through `.assetsignore`.

## Build

```sh
python scripts/build_site.py
```

The build validates the release data and writes the public pages in place at the
repository root. The site has no package install step.

## Preview

```sh
python -m http.server 8800
```

Then open `http://127.0.0.1:8800/`. Use the browser tools to check 390px and 1440px
widths. The 404 page is `http://127.0.0.1:8800/404.html`; a generic local server's
own 404 response is not the deployed page.

## Design

- Six primary pages: Home, Features, Download, Guide, Privacy and Changelog.
- Fixed Cinnamon coffee palette: deep brown surfaces, warm text and an amber accent.
- Mobile navigation appears below the header with a Menu / Close control, Escape
  handling and a no-JavaScript fallback.
- Section content stays readable at narrow widths and the only horizontal scroll
  areas are command blocks and wide reference tables.
- Product images use synthetic history captured from a private test profile.

## Release updates

Change `site/release.json` once per release. It supplies the version, release link,
checksum link and six user-facing asset names to the Download and Guide pages.

Add the reviewed release summary to `site/releases.json`. The changelog is no longer
generated from raw commits, so internal work does not displace user-facing release
notes.

## Deploying

The existing Cloudflare build command `python scripts/changelog.py --keep-on-error`
remains valid: it runs the new site build and keeps the committed pages if the build
fails. Output directory remains `/`.

Every push to `main` redeploys the site. The `_headers` file sets a strict CSP and
allows local fonts with `font-src 'self'`. Assets are cached for a day.

The site mirrors the six `v0.1.0-beta.24` installation packages under `downloads/` so
the download page remains usable when GitHub's release CDN is unavailable. The GitHub
release remains canonical. Physical GNOME helper, login/lock, suspend and mixed-DPI
behavior remain unverified.

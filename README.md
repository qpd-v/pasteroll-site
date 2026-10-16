# pasteroll.com

The one-page site for [Pasteroll](https://github.com/qpd-v/pasteroll). Plain HTML, CSS and a small
script: no framework, no build step, no external requests (fonts, scripts and analytics included).

```
index.html      the page
changelog/      the changelog page (generated, see below)
scripts/        changelog.py, which builds that page from the GitHub commits
styles.css      layout and the colour themes
script.js       theme picker, media slots, copy buttons, scroll reveal
theme-init.js   applies the saved theme before first paint
404.html        the not-found page
_headers        security headers and caching (Cloudflare Pages reads this file)
assets/         icon, favicons, the roll cut-out, the social card
assets/media/   your demo clips (see below)
```

## Preview locally

```sh
python -m http.server 8080
```

then open http://localhost:8080. (Opening `index.html` straight from the disk works for the look,
but the demo clips are only picked up when served.)

## Adding the demo clips

Each demo area on the page is a slot with a name. Put a file with that name in `assets/media/` and
it replaces the placeholder: nothing else to edit.

| Slot | File |
|---|---|
| hero | `assets/media/demo.mp4` |
| carousel | `assets/media/carousel.mp4` |
| viewer | `assets/media/viewer.mp4` |
| editor | `assets/media/editor.mp4` |

Use `.mp4` (H.264). A `.gif` with the same name also works but is much bigger. The clips play
muted and looping; a click pauses them. Keep each under a few MB: about 1280 px wide and 10 to 20
seconds is plenty.

## Colour themes

`:root[data-theme="..."]` blocks in `styles.css` define five themes: `cinnamon` (coffee, the
default), and the Catppuccin flavours `frappe`, `macchiato`, `mocha` and `latte`. The round button
at the bottom right (or the **T** key) cycles through them while you choose. When you have picked
one, set it as the default (`data-theme` on `<html>` in `index.html`, `404.html` and the
`theme-color` meta tag), then delete the block marked `THEME PICKER` in `index.html` and the theme
code in `script.js`.

## The changelog page

`changelog/index.html` is generated from the commits of https://github.com/qpd-v/pasteroll by
`scripts/changelog.py` (Python 3, standard library only). Each commit is a heading, and the
bullet lines of its message are the list under it, so a commit message written like this reads
well on the page:

```
Short title of the change

- First thing it does
- Second thing it does
```

```sh
python scripts/changelog.py                        # read the commits from GitHub
python scripts/changelog.py --local ../pasteroll   # or from a local clone, offline
```

The result is plain static HTML, so visitors' browsers never contact GitHub.

### Keeping it in sync automatically

1. In Cloudflare Pages, set the **build command** to `python scripts/changelog.py --keep-on-error`
   (output directory `/`). Every deploy then rebuilds the page from the live repository. If GitHub
   cannot be reached, the build keeps the page that is committed here and carries on.
2. In the Pages project, Settings, Builds, **Deploy hooks**: create a hook and copy its URL.
3. In the app repository on GitHub, Settings, Webhooks, **Add webhook**: paste that URL as the
   Payload URL, content type `application/json`, and choose *Just the push event*.

From then on every push to the app repository redeploys the site and the changelog updates itself.
(No GitHub Actions are involved.) Without steps 2 and 3 the page still updates whenever the site
itself is deployed.

## Deploying (Cloudflare Pages)

1. Push this repository to GitHub.
2. In the Cloudflare dashboard: Workers & Pages, Create, Pages, Connect to Git, choose this
   repository. Framework preset: none. Build command: `python scripts/changelog.py --keep-on-error`
   (see the changelog section). Output directory: `/`.
3. Add the custom domain `pasteroll.com` to the project (and `www.pasteroll.com`, redirected to the
   bare domain).

Every push to `main` redeploys. The `_headers` file sets a strict Content-Security-Policy, so
anything new that loads from another site (a font, a script) will be blocked until the policy is
changed on purpose.

# Goodall Family Dentistry website

Static site for goodallfamilydentistry.com, hosted on Cloudflare (Workers static assets).
Every push to `main` deploys automatically. Test address:
https://goodall-family-dentistry-website.wellness-795.workers.dev

## Layout
- `src/index.html` — the source: all pages, content, styles and scripts. **Edit this.**
- `public/` — what gets published (built pages, `images/`, `videos/`, `_redirects`, `_headers`, `robots.txt`, `sitemap.xml`).
- `tools/build.py` — builds `public/*.html` from the source: one file per page with its title,
  description, structured data and content already in the HTML (good for Google and AI search), plus `404.html` and `sitemap.xml`.
- `tools/serve.py` — local preview that behaves like Cloudflare (`python3 tools/serve.py`, then open http://127.0.0.1:8765).
- `wrangler.jsonc` — Cloudflare settings (publish `public/`, real 404 page).

## Making a change
1. Edit `src/index.html` (new photos go in `public/images/`).
2. `python3 tools/build.py`
3. Commit `src/` and `public/`, push.

## At launch (when the real domain is connected)
- Delete the `X-Robots-Tag: noindex` line in `public/_headers`.
- Old site addresses keep working: page addresses match the old site, and other moves are in `public/_redirects`.

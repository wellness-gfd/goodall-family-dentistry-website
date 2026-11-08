# Goodall Family Dentistry website

Static site for goodallfamilydentistry.com, hosted on Cloudflare Workers static assets (auto-deploys from `main`; test URL goodall-family-dentistry-website.wellness-795.workers.dev).

- `index.html` — the whole site (pages, content, styles and scripts)
- `images/`, `videos/` — media (WebP versions are generated for every photo)
- `_redirects` — old-site URL redirects
- `_headers` — security headers and caching. Remove the `X-Robots-Tag: noindex` line at launch.

`.assetsignore` keeps repo files (.git, README) from being published.

# Goodall Family Dentistry website

Static site for goodallfamilydentistry.com, hosted on Cloudflare Pages (auto-deploys from `main`).

- `index.html` — the whole site (pages, content, styles and scripts)
- `images/`, `videos/` — media (WebP versions are generated for every photo)
- `_redirects` — old-site URL redirects
- `_headers` — security headers and caching. Remove the `X-Robots-Tag: noindex` line at launch.

Cloudflare Pages settings: Framework preset **None**, build command **(blank)**, output directory **/**.

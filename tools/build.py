"""Build the published site from src/index.html.

    python3 tools/build.py

For every page it writes public/<page>.html (home -> public/index.html) with that page's
title, description, canonical URL, structured data, menu and content already in the HTML,
so search engines and AI answer tools can read each page without running JavaScript.
Also writes public/404.html and public/sitemap.xml.

Needs Python Playwright and Chrome. Edit src/index.html, run this, then commit src/ and public/.
"""
import asyncio, datetime, html, json, os, re, subprocess, sys, time

from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")
SRC = os.path.join(ROOT, "src", "index.html")
SITE = "https://www.goodallfamilydentistry.com/"
PORT = 8799
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")

COLLECT = r"""() => {
  const q = s => document.querySelector(s);
  return {
    title: document.title,
    desc: q('meta[name=description]').content,
    robots: q('meta[name=robots]').content,
    canonical: q('link[rel=canonical]').href,
    ogTitle: q('meta[property="og:title"]').content,
    ogDesc: q('meta[property="og:description"]').content,
    ogUrl: q('meta[property="og:url"]').content,
    ld: q('#ld-page').textContent,
    main: q('#main').innerHTML,
    menu: q('#menu').innerHTML,
    drawer: q('#drawerNav').innerHTML,
  };
}"""

ROUTES = r"""() => [...new Set(["home", ...Object.keys(PAGES), ...Object.keys(SERVICES), ...BLOG.map(b => b.slug)])]"""


def attr(v):
    return html.escape(v, quote=True)


def fill(src, d):
    out = src
    def sub(pattern, repl):
        nonlocal out
        new, n = re.subn(pattern, lambda m: repl, out, count=1)
        assert n == 1, pattern
        out = new
    sub(r"<title>.*?</title>", f"<title>{html.escape(d['title'])}</title>")
    sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{attr(d["desc"])}">')
    sub(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{attr(d["robots"])}">')
    sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{attr(d["canonical"])}">')
    sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{attr(d["ogTitle"])}">')
    sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{attr(d["ogDesc"])}">')
    sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{attr(d["ogUrl"])}">')
    sub(r'<script type="application/ld\+json" id="ld-page"></script>',
        '<script type="application/ld+json" id="ld-page">' + d["ld"].replace("</", "<\\/") + "</script>")
    sub(r'<ul class="menu" id="menu"></ul>', f'<ul class="menu" id="menu">{d["menu"]}</ul>')
    sub(r'<div id="drawerNav"></div>', f'<div id="drawerNav">{d["drawer"]}</div>')
    sub(r'<main id="main" tabindex="-1"></main>', f'<main id="main" tabindex="-1">{d["main"]}</main>')
    return out


async def build():
    src = open(SRC, encoding="utf-8").read()
    server = subprocess.Popen([sys.executable, os.path.join(ROOT, "tools", "serve.py"), "--src", f"--port={PORT}"])
    time.sleep(1)
    base = f"http://127.0.0.1:{PORT}"
    written, sitemap = [], []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
            page = await browser.new_page(viewport={"width": 1366, "height": 900})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            await page.goto(base + "/")
            routes = await page.evaluate(ROUTES)
            for key in routes:
                await page.goto(base + ("/" if key == "home" else "/" + key))
                await page.wait_for_timeout(250)
                d = await page.evaluate(COLLECT)
                if errors:
                    raise SystemExit(f"JavaScript error on {key}: {errors}")
                name = "index" if key == "home" else key
                with open(os.path.join(PUBLIC, name + ".html"), "w", encoding="utf-8") as f:
                    f.write(fill(src, d))
                written.append(name)
                if "noindex" not in d["robots"] and key != "404":
                    sitemap.append(SITE + ("" if key == "home" else key))
            await browser.close()
    finally:
        server.terminate()

    # remove pages that no longer exist
    keep = {n + ".html" for n in written}
    for f in os.listdir(PUBLIC):
        if f.endswith(".html") and f not in keep:
            os.remove(os.path.join(PUBLIC, f))

    today = datetime.date.today().isoformat()
    with open(os.path.join(PUBLIC, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in sitemap:
            f.write(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n")
        f.write("</urlset>\n")
    print(f"Built {len(written)} pages, {len(sitemap)} in sitemap.xml")


if __name__ == "__main__":
    asyncio.run(build())

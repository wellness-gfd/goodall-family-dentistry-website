"""Local preview server that behaves like Cloudflare for this site.

    python3 tools/serve.py            # serves public/ on http://127.0.0.1:8765
    python3 tools/serve.py --src      # serves src/index.html for every page (used by the build)

/dental-implants -> public/dental-implants.html, unknown pages -> public/404.html (status 404).
"""
import http.server, os, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")
SRC = os.path.join(ROOT, "src", "index.html")
USE_SRC = "--src" in sys.argv
PORT = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--port=")), 8765))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=PUBLIC, **k)

    def log_message(self, *a):
        pass

    def send_file(self, path, status=200):
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if os.path.splitext(path)[1] and path != "/index.html":
            return super().do_GET()  # images, videos, robots.txt, sitemap.xml ...
        if USE_SRC:
            return self.send_file(SRC)
        slug = path.strip("/").removesuffix(".html") or "index"
        page = os.path.join(PUBLIC, slug + ".html")
        if os.path.isfile(page):
            return self.send_file(page)
        return self.send_file(os.path.join(PUBLIC, "404.html"), 404)


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

#!/usr/bin/env python3
"""Local-only diagnostic backend for the Wii U eShop applet.

No credentials, account services, purchases, tickets, installs or downloads.
Not connected to the Wii U; a development aid, not a replacement shop.
"""
import argparse
import json
from datetime import datetime
from html import escape
from shop_ui import render_page
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

ROOT = Path(__file__).resolve().parent
PATH = "/ninja/wood_index.html"
NAV = (
    ("home", "Home"),
    ("best", "Best Sellers"),
    ("new", "New Releases"),
    ("mario", "Mario Games"),
    ("all", "All games"),
    ("profile", "My Profile"),
)

def safe(value):
    return escape(str(value), quote=True)

def link(view, **params):
    return PATH + "?" + urlencode({"view": view, **params})

def load_catalog(path):
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = document["titles"]
    if not isinstance(entries, list):
        raise ValueError("titles must be an array")
    ids = set()
    for item in entries:
        required = ("id", "name", "description", "category", "release", "popularity")
        if not isinstance(item, dict) or any(key not in item for key in required):
            raise ValueError("missing catalog fields")
        title_id = item["id"]
        if not isinstance(title_id, str) or not title_id.isascii() or not title_id or not all(
            c.isalnum() or c in "-_" for c in title_id
        ):
            raise ValueError("invalid title ID")
        if title_id in ids:
            raise ValueError("duplicate title ID")
        ids.add(title_id)
        datetime.strptime(item["release"], "%Y-%m-%d")
        int(item["popularity"])
    return entries

def render(view, catalog, query="", title_id="", frm="all"):
    """Public API preserved for the original diagnostic backend."""
    return render_page(view, catalog, query, title_id, frm).encode("utf-8")


STATIC_FILES = {
    "/static/shop.css": ("static/shop.css", "text/css; charset=utf-8"),
    "/static/shop.js": ("static/shop.js", "application/javascript; charset=utf-8"),
}


def make_handler(catalog):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path in ("/health", "/healthz"):
                self.reply(200, b'{"status":"ok","mode":"demo"}', "application/json")
                return
            if parsed.path in STATIC_FILES:
                filename, mime = STATIC_FILES[parsed.path]
                self.reply(200, (ROOT / filename).read_bytes(), mime)
                return
            if parsed.path not in ("/", PATH):
                self.reply(404, b"Not Found", "text/plain")
                return
            params = parse_qs(parsed.query, keep_blank_values=True)
            def param(name, max_length):
                return params.get(name, [""])[0][:max_length]
            self.reply(200, render(param("view", 24) or "home", catalog,
                                   param("q", 60), param("title", 64),
                                   param("frm", 24)),
                       "text/html; charset=utf-8")

        def reply(self, status, body, mime):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            # Do not log users, query strings, or potential account data.
            pass
    return Handler

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--catalog", default=str(ROOT / "catalog.example.json"))
    args = parser.parse_args()
    catalog = load_catalog(args.catalog)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(catalog))
    print("Development only: http://%s:%s%s" %
          (args.host, server.server_address[1], PATH))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Local-only diagnostic backend for the Wii U eShop applet.

No credentials, account services, purchases, tickets, installs or downloads.
Not connected to the Wii U; a development aid, not a replacement shop.
"""
import argparse
import json
from datetime import datetime
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from geisha_archive import GeishaArchive
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

def render(view, catalog, query="", title_id=""):
    if view == "best":
        heading, entries = "Best Sellers", sorted(catalog, key=lambda x: -int(x["popularity"]))
    elif view == "new":
        heading, entries = "New Releases", sorted(catalog, key=lambda x: x["release"], reverse=True)
    elif view == "mario":
        heading, entries = "Mario Games", [x for x in catalog if x["category"] == "mario"]
    elif view == "all":
        heading, entries = "All games", sorted(catalog, key=lambda x: x["name"])
    elif view == "search":
        heading = "Search: " + query
        entries = [x for x in catalog if query.strip() and query.casefold() in (
            x["name"] + " " + x["description"]
        ).casefold()]
    elif view == "profile":
        heading, entries = "My Profile", []
    elif view == "detail":
        entry = next((x for x in catalog if x["id"] == title_id), None)
        heading, entries = (entry["name"] if entry else "Title not found"), []
    else:
        heading, entries = "Home", catalog

    nav = " ".join(
        '<a class="nav" href="%s">%s</a>' % (safe(link(key)), safe(label))
        for key, label in NAV
    )
    search = ('<form action="%s" method="get"><input type="hidden" name="view" value="search">'
              '<input type="text" name="q" maxlength="60" value="%s" placeholder="Search">'
              '<button type="submit">Search</button></form>') % (PATH, safe(query))
    if view == "profile":
        content = "<p>Demo only: no Nintendo or Pretendo profile data is accessed.</p>"
    elif view == "detail":
        content = ("<p>%s</p>" % safe(entry["description"]) if entry else "<p>Unknown ID.</p>")
        content += "<p>Installation and downloads are disabled.</p>"
    else:
        content = "".join(
            '<a class="tile" href="%s"><strong>%s</strong><small>%s</small></a>'
            % (safe(link("detail", title=x["id"])), safe(x["name"]), safe(x["category"]))
            for x in entries
        ) or "<p>No titles in this category.</p>"

    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>%s — zShop diagnostic</title>
<style>body{margin:0;background:#f2f2f2;color:#333;font:18px Arial,sans-serif}
header{background:#eea02d;color:white;padding:16px;font-weight:bold;font-size:24px}
nav{background:white;padding:15px;border-bottom:1px solid #ccc}
a{color:#165e91}.nav{display:inline-block;padding:12px;border:1px solid #ccd;border-radius:8px;margin:3px;text-decoration:none}
main{padding:18px}.tile{display:inline-block;vertical-align:top;box-sizing:border-box;padding:20px;margin:8px;width:190px;height:110px;background:white;border:1px solid #ddd;border-radius:8px;text-decoration:none}
.tile strong,.tile small{display:block}.tile small{color:#777;margin-top:12px}
input,button{font:18px Arial;padding:8px}footer{padding:15px;font-size:13px;color:#555}
</style>
<script type="text/javascript">(function(){try{if(window.wiiuBrowser){
if(wiiuBrowser.endStartUp){wiiuBrowser.endStartUp(true);}
if(wiiuBrowser.lockHomeButtonMenu){wiiuBrowser.lockHomeButtonMenu(false);}
}}catch(e){}})();</script></head>
<body><header>zShop / eShop applet diagnostic (NOT Nintendo eShop)</header>
<nav>%s</nav><main><p><a href="%s">Back to Home</a> | <a href="%s">My Profile</a></p>
<h1>%s</h1>%s<div>%s</div></main>
<footer>Demo catalog; no tickets, installs, account access, or download requests.</footer>
</body></html>''' % (
        safe(heading), nav, safe(link("home")), safe(link("profile")),
        safe(heading), search, content
    )
    return page.encode("utf-8")

def make_handler(catalog, geisha=None):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path in ("/health", "/healthz"):
                self.reply(200, b'{"status":"ok","mode":"demo"}', "application/json")
                return
            if geisha is not None:
                if parsed.path in ("/", PATH, "/geisha", "/geisha/"):
                    self.send_response(302)
                    self.send_header("Location", "/geisha/index.html")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                content = geisha.read(parsed.path)
                if content is not None:
                    mime, payload = content
                    self.reply(200, payload, mime)
                else:
                    self.reply(404, b"Not Found", "text/plain")
                return
            if parsed.path not in ("/", PATH):
                self.reply(404, b"Not Found", "text/plain")
                return
            params = parse_qs(parsed.query, keep_blank_values=True)
            def param(name, max_length):
                return params.get(name, [""])[0][:max_length]
            self.reply(200, render(param("view", 24) or "home", catalog,
                                   param("q", 60), param("title", 64)),
                       "text/html; charset=utf-8")

        def reply(self, status, body, mime):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            if geisha is not None:
                self.send_header("Content-Security-Policy",
                                 "default-src 'self'; script-src 'none'; "
                                 "connect-src 'none'; form-action 'none'; "
                                 "object-src 'none'; frame-src 'none'; "
                                 "img-src 'self' data:; style-src 'self' 'unsafe-inline'")
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
    parser.add_argument("--geisha-root", default=None,
                        help="Local Geisha backup folder; read-only HTML/CSS/images preview "
                             "with all original JavaScript disabled")
    args = parser.parse_args()
    catalog = load_catalog(args.catalog)
    geisha = GeishaArchive(args.geisha_root, catalog) if args.geisha_root else None
    server = ThreadingHTTPServer((args.host, args.port),
                                 make_handler(catalog, geisha=geisha))
    print("Development only: http://%s:%s%s" %
          (args.host, server.server_address[1], PATH))
    if geisha:
        print("Geisha read-only preview (NO JavaScript):", geisha.root)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()

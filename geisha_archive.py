"""Read-only browser preview for a LOCAL user-supplied Wii U Geisha archive."""
from pathlib import Path
from urllib.parse import unquote
import mimetypes
import re

from geisha_preview_renderer import hydrate_index

# Only audited JavaScript executed in read-only Geisha mode. The historical
# boot.js is NOT served. This bridge only dismisses the native startup screen.
SAFE_STARTUP_BRIDGE = b"""(function(){try{
var b=window.wiiuBrowser;
if(b){
 if(typeof b.endStartUp==='function'){b.endStartUp(true);}
 if(typeof b.lockHomeButtonMenu==='function'){b.lockHomeButtonMenu(false);}
}
}catch(ignored){}}());"""

ARCHIVE_SUBDIR = Path("geisha_wup.cdn.nintendo.net/geisha-wup.cdn.nintendo.net/geisha")
EXTENSIONS = {".html", ".htm", ".css", ".png", ".jpg", ".jpeg", ".gif",
              ".webp", ".bmp", ".ico", ".woff", ".woff2", ".ttf"}
SCRIPT_TAGS = re.compile(r"(?is)<script\b[^>]*>.*?</script\s*>")
FRAMES = re.compile(r"(?is)<(?:iframe|object)\b[^>]*>.*?</(?:iframe|object)\s*>")
META_REFRESH = re.compile(r"(?is)<meta\b[^>]*http-equiv\s*=\s*['\"]?refresh['\"]?[^>]*>")
EVENTS = re.compile(r"""(?is)\s+on[a-z]+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)""")
REMOTE = re.compile(r"""(?is)\s+(?:href|src|action|poster|srcset)\s*=\s*(?:"(?:https?:|//|javascript:)[^"]*"|'(?:https?:|//|javascript:)[^']*')""")
CSS_IMPORT = re.compile(r"(?is)@import\s+[^;]+;")
CSS_REMOTE = re.compile(r"""(?is)url\(\s*['"]?(?:https?:|//)[^)]*\)""")


def preview_html(data, name=None, catalog=()):
    """Preserve archived layout without enabling unreviewed console API calls."""
    page = data.decode("utf-8", errors="replace")
    page = SCRIPT_TAGS.sub("", page)
    page = FRAMES.sub("", page)
    page = re.sub(r"(?is)<(?:embed|base)\b[^>]*>", "", page)
    page = META_REFRESH.sub("", page)
    page = EVENTS.sub("", page)
    page = REMOTE.sub("", page)
    # Keep external image requests blocked even in inline CSS, on Wii U
    # browsers that may not enforce the Content-Security-Policy header.
    page = CSS_IMPORT.sub("", page)
    page = CSS_REMOTE.sub("none", page)
    page = re.sub(r"(?is)\s+(?:href|src|action)\s*=\s*(?:javascript:|https?://|//)[^\s>]+",
                  "", page)
    page = re.sub(r"""(?is)\s+srcset\s*=\s*(?:"[^"]*"|'[^']*')""", "", page)
    page = re.sub(r"(?is)<form\b[^>]*>", "<div>", page)
    page = re.sub(r"(?is)</form\s*>", "</div>", page)
    page = re.sub(r"(?i)<head([^>]*)>",
                  r'<head\1><meta name="zshop-geisha-mode" content="read-only-preview">',
                  page, count=1)
    if name == "index.html":
        page = hydrate_index(page, catalog)
        # Geisha's original CSS hides #wrapper with display:none until its
        # original boot.js makes it visible. That script is intentionally
        # blocked here, so expose the historical wrapper without replacing UI.
        page = re.sub(
            r"(?i)</head\s*>",
            '<style type="text/css" id="zshop-geisha-visibility">'
            '#wrapper{display:block!important}</style></head>',
            page, count=1
        )
    # The only script served is the small, audited applet startup bridge.
    startup_tag = '<script src="/geisha/zshop-bridge.js"></script>'
    if re.search(r"(?i)</body\s*>", page):
        page = re.sub(r"(?i)</body\s*>", startup_tag + "</body>", page, count=1)
    else:
        page += startup_tag
    return page.encode("utf-8")


def preview_css(data):
    css = data.decode("utf-8", errors="replace")
    css = CSS_IMPORT.sub("", css)
    return CSS_REMOTE.sub("none", css).encode("utf-8")


class GeishaArchive:
    def __init__(self, directory, catalog=()):
        self.catalog = tuple(catalog)
        root = Path(directory).expanduser().resolve()
        choices = (root / ARCHIVE_SUBDIR, root / "geisha", root)
        self.root = next((p.resolve() for p in choices if (p / "index.html").is_file()), None)
        if self.root is None:
            raise ValueError("Geisha index.html not found in local archive")

    def read(self, url_path):
        """Return (MIME, bytes) or None; reject traversals and executable scripts."""
        if url_path == "/geisha/zshop-bridge.js":
            return "application/javascript; charset=utf-8", SAFE_STARTUP_BRIDGE
        if not url_path.startswith("/geisha/"):
            return None
        name = unquote(url_path[len("/geisha/"):]).replace("\\", "/")
        if not name or name.startswith("/") or "\x00" in name:
            return None
        if any(part in ("", ".", "..") or part.startswith(".")
               for part in name.split("/")):
            return None
        file = (self.root / name).resolve()
        if not file.is_relative_to(self.root) or not file.is_file():
            return None
        if file.suffix.lower() not in EXTENSIONS:
            return None
        data = file.read_bytes()
        if file.suffix.lower() in (".html", ".htm"):
            return "text/html; charset=utf-8", preview_html(data, name, self.catalog)
        if file.suffix.lower() == ".css":
            return "text/css; charset=utf-8", preview_css(data)
        return mimetypes.guess_type(str(file))[0] or "application/octet-stream", data

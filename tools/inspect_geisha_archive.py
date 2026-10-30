#!/usr/bin/env python3
"""Inspect a LOCAL, user-supplied Geisha site backup without modifying it.

No network, account credentials, certificates, uploads, or script execution.
A resource inventory does NOT certify that the Wii U eShop works.
"""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

EXPECTED = ("index.html", "always02_01.html", "shelf02_01.html")
CSS_URLS = re.compile(r"url\(\s*['\"]?([^)'\"\s]+)|@import\s+['\"]([^'\"]+)", re.I)


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "img", "source") and attrs.get("src"):
            self.values.append(attrs["src"])
        if tag == "link" and attrs.get("href"):
            self.values.append(attrs["href"])


def inspect(folder):
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError("An existing local directory is required")
    if (root / "geisha" / "index.html").is_file():
        root = (root / "geisha").resolve()

    pages = sorted(p for p in root.rglob("*.html")
                   if p.is_file() and p.resolve().is_relative_to(root))
    css_files = sorted(p for p in root.rglob("*.css")
                       if p.is_file() and p.resolve().is_relative_to(root))
    missing = set()
    unsafe = set()
    external = set()
    checked = 0

    for file in pages + css_files:
        content = file.read_text(encoding="utf-8", errors="replace")
        if file.suffix == ".html":
            parser = References()
            parser.feed(content)
            resources = parser.values
        else:
            resources = [a or b for a, b in CSS_URLS.findall(content)]
        for resource in resources:
            resource = resource.strip()
            if not resource or resource.startswith(("data:", "javascript:", "#")):
                continue
            parts = urlsplit(resource)
            if parts.scheme or parts.netloc:
                external.add(parts.netloc or parts.scheme)
                continue
            name = unquote(parts.path).replace("\\", "/")
            if not name:
                continue
            if name.startswith("/"):
                name = name.lstrip("/")
                if name.startswith("geisha/"):
                    name = name[7:]
                target = root / name
            else:
                target = file.parent / name
            resolved = target.resolve()
            if not resolved.is_relative_to(root):
                unsafe.add(resource)
                continue
            checked += 1
            if not resolved.is_file():
                missing.add(str(resolved.relative_to(root)).replace("\\", "/"))

    html_pages = [str(p.relative_to(root)).replace("\\", "/") for p in pages]
    missing_expected = [name for name in EXPECTED if name not in html_pages]
    return {
        "html_pages": html_pages,
        "missing_expected_pages": missing_expected,
        "checked_local_resource_references": checked,
        "missing_local_resources": sorted(missing),
        "external_hosts": sorted(external),
        "unsafe_paths": sorted(unsafe),
        "reference_complete": bool(html_pages) and not (
            missing_expected or missing or unsafe
        ),
        "disclaimer": "Reference inventory only. Originality, licensing, API calls, runtime and console rendering are not verified.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", help="Local Geisha backup directory")
    args = parser.parse_args()
    report = inspect(args.folder)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["reference_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

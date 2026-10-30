"""Read-only static risk/provenance inventory for a local Geisha frontend copy.

This does not execute the source, connect to Nintendo, inspect user account
data, or copy the Nintendo files into the zShop repository.
"""
import argparse
import json
import re
from pathlib import Path
from geisha_archive import GeishaArchive

MARKERS = {
    "native_download": re.compile(
        r"\bwiiuEC\s*\.\s*(ticketDownloadSync|registerTitleDownloadTask|registerAocDownloadTask|registerPatchTitleDownloadTask)\s*\("
    ),
    "native_account": re.compile(
        r"\bwiiuNNA\s*\.\s*(getServiceToken|principalId|principalIdHashKey)"
    ),
    "ninja_session": re.compile(r"/ninja/(?:ws|debug)/my/session", re.I),
    "local_mock": re.compile(
        r"wiiuBrowser Mock|wiiuNNA mock|Mock session storage|"
        r"Offline-safe placeholder|Local Game Database|mock_service_token", re.I
    ),
    "external_url": re.compile(r"https?://[a-z0-9-]+\.[a-z0-9.-]+", re.I),
}
EXPECTED = ("index.html", "always02_01.html", "shelf02_01.html")


def inspect_source(directory):
    archive = GeishaArchive(directory)
    root = archive.root
    files = sorted(
        p for p in root.rglob("*") if p.is_file()
        and p.suffix.lower() in (".js", ".html", ".css")
        and p.resolve().is_relative_to(root)
    )
    flagged = []
    counts = {name: 0 for name in MARKERS}
    for p in files:
        content = p.read_text(encoding="utf-8", errors="replace")
        rules = [name for name, regex in MARKERS.items() if regex.search(content)]
        if rules:
            flagged.append({"file": str(p.relative_to(root)).replace("\\", "/"),
                            "markers": rules})
            for name in rules:
                counts[name] += 1
    return {
        "source": str(root),
        "scanned_files": len(files),
        "expected_pages_present": {
            name: (root / name).is_file() for name in EXPECTED
        },
        "counts": counts,
        "flagged": flagged,
        "interpretation": (
            "Markers do not prove a function executes. This report does not "
            "certify the source as original, safe or suitable for Wii U."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", help="Local user-provided Geisha archive")
    args = parser.parse_args()
    print(json.dumps(inspect_source(args.directory), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

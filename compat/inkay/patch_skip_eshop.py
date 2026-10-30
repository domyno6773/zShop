#!/usr/bin/env python3
"""Experimental build-time Inkay compatibility edit for zShop.

This tool edits a LOCAL checkout of PretendoNetwork/Inkay.
It is intentionally fail-closed: only one exact upstream call may be altered.
It never modifies the user's Wii U, settings, network or the zShop plugin.
"""
import argparse
from pathlib import Path

TARGET = "src/main.cpp"
NEEDLE = "        patchEshop();"
REPLACEMENT = (
    "        // zShop compatibility EXPERIMENT: leave only the Inkay eShop applet "
    "redirect disabled.\n"
    "        // Other Inkay patches remain in place. The original eShop may still "
    "be unavailable.\n"
    "        // patchEshop();  // intentionally not called"
)

def patch_inkay(root: Path) -> None:
    source = root / TARGET
    if not source.is_file():
        raise RuntimeError("Inkay source file is missing: " + str(source))
    text = source.read_text(encoding="utf-8")
    if text.count(NEEDLE) != 1:
        raise RuntimeError(
            "Unsupported Inkay version: expected exactly one eShop patch call; "
            "refusing to change files."
        )
    if "        patchDNS();" not in text or "        patchOlvApplet();" not in text:
        raise RuntimeError("Unexpected Inkay patch call sequence; aborting.")
    # Replacing exactly this call leaves DNS, account, OLV, gameplay patch calls
    # untouched; it does NOT undo the separate IOSU-side shop URL rewrites.
    source.write_text(text.replace(NEEDLE, REPLACEMENT, 1), encoding="utf-8")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="Root of a local Inkay source checkout")
    options = parser.parse_args()
    patch_inkay(options.checkout)
    print("Patched only the Inkay eShop applet hook in", options.checkout / TARGET)

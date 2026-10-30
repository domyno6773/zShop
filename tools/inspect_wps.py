#!/usr/bin/env python3
"""Passive WUPS .wps ELF inspector: no execution, patching or networking."""
import argparse
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path

COMPRESSED = 0x08000000
MAX_SECTION = 32 * 1024 * 1024

def inspect(filename):
    blob = Path(filename).read_bytes()
    if len(blob) < 0x400 or blob[:4] != b"\x7fELF" or blob[5] != 2:
        raise ValueError("Expected big-endian ELF binary")
    shoff = struct.unpack_from(">I", blob, 32)[0]
    entsize = struct.unpack_from(">H", blob, 46)[0]
    count = struct.unpack_from(">H", blob, 48)[0]
    if not (0 < count <= 128 and entsize == 40 and shoff + entsize*count <= len(blob)):
        raise ValueError("Invalid section table")

    sections = []
    for i in range(count):
        (_, kind, flags, _, offset, size, _, _, _, _) = struct.unpack_from(
            ">10I", blob, shoff + 40*i
        )
        if kind == 8:  # SHT_NOBITS
            continue
        if offset + size > len(blob):
            raise ValueError("Section outside ELF")
        raw = blob[offset:offset+size]
        if flags & COMPRESSED:
            if size < 4:
                raise ValueError("Invalid compressed section")
            expected = struct.unpack_from(">I", raw)[0]
            if expected > MAX_SECTION:
                raise ValueError("Section exceeds inspection safety limit")
            inflater = zlib.decompressobj()
            data = inflater.decompress(raw[4:], expected + 1)
            if not inflater.eof or len(data) != expected:
                raise ValueError("Corrupt or oversized compressed section")
        else:
            if size > MAX_SECTION:
                raise ValueError("Section exceeds inspection safety limit")
            data = raw
        sections.append(data)

    strings = [
        match.group().decode("ascii") for section in sections
        for match in re.finditer(rb"[\x20-\x7e]{7,}", section)
    ]
    urls = sorted(set(
        match.group() for line in strings
        for match in re.finditer(r"https?://[^\s\"<>]{5,}", line)
    ))
    probes = {
        "eshop_applet_patch": "vol/content/initial.oma",
        "function_patcher": "FunctionPatcher",
        "unsafe_iosu_opt_in": "vol/content/ushop-unsafe.txt",
        "remote_reporting": "/plugreport?stage=",
        "ec_soap_rewrite": "ECommerceSOAP",
        "ias_auth_rewrite": "IdentityAuthenticationSOAP",
        "nus_rewrite": "NetUpdateSOAP",
        "cdn_rewrite": "/ccs/download",
        "wups_0_9_1_metadata": "wups=0.9.1",
    }
    meta = {}
    for key in ("name", "version", "author", "description", "buildtimestamp"):
        value = next((s.split("=", 1)[1] for s in strings if s.startswith(key+"=")), None)
        if value is not None:
            meta[key] = value
    return {
        "filename": Path(filename).name,
        "size_bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "format": "ELF32 big-endian (Wii U WPS)",
        "metadata": meta,
        "section_count": count,
        "parsed_sections": len(sections),
        "markers": {key: any(probe in s for s in strings) for key, probe in probes.items()},
        "network_urls": urls,
        "warning": "Static indicators only. No behavior or trustworthiness verified.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wps")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    result = json.dumps(inspect(args.wps), indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result, end="")

if __name__ == "__main__":
    main()

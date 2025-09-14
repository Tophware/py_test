#!/usr/bin/env python3
"""
Deep Metadata Scanner - Extract ALL possible metadata from images
Including hidden GPS data, steganographic content, and embedded information
"""

import os
import sys
import json
import struct
import binascii
from pathlib import Path

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import exifread

    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False


def scan_binary_for_metadata(file_path):
    """Scan binary content for embedded metadata signatures."""
    metadata = {}

    with open(file_path, "rb") as f:
        content = f.read()

    # Look for common metadata signatures
    signatures = {
        b"GPS": "GPS data signature",
        b"EXIF": "EXIF data signature",
        b"<?xml": "XML metadata",
        b"<x:xmpmeta": "XMP metadata",
        b"<rdf:RDF": "RDF metadata",
        b"GPS\x00": "GPS null-terminated",
        b"coordinates": "Coordinates text",
        b"latitude": "Latitude text",
        b"longitude": "Longitude text",
        b"location": "Location text",
        b"place": "Place text",
        b"address": "Address text",
        b"geo:": "Geo URI scheme",
    }

    found_signatures = []
    for sig, desc in signatures.items():
        positions = []
        start = 0
        while True:
            pos = content.find(sig, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        if positions:
            found_signatures.append(
                {
                    "signature": sig.decode("utf-8", errors="ignore"),
                    "description": desc,
                    "positions": positions[:10],  # Limit to first 10 occurrences
                    "context": (
                        extract_context(content, positions[0]) if positions else None
                    ),
                }
            )

    metadata["binary_signatures"] = found_signatures

    # Look for hidden text strings
    text_strings = extract_text_strings(content)
    metadata["text_strings"] = text_strings

    # Check for WebP-specific chunks
    if file_path.suffix.lower() == ".webp":
        webp_chunks = parse_webp_chunks(content)
        metadata["webp_chunks"] = webp_chunks

    return metadata


def extract_context(content, position, context_size=50):
    """Extract context around a found signature."""
    start = max(0, position - context_size)
    end = min(len(content), position + context_size)
    context = content[start:end]
    return {
        "hex": context.hex(),
        "ascii": context.decode("utf-8", errors="ignore"),
        "position": position,
    }


def extract_text_strings(content, min_length=4):
    """Extract readable text strings from binary content."""
    strings = []
    current_string = ""

    for byte in content:
        if 32 <= byte <= 126:  # Printable ASCII
            current_string += chr(byte)
        else:
            if len(current_string) >= min_length:
                strings.append(current_string)
            current_string = ""

    # Don't forget the last string
    if len(current_string) >= min_length:
        strings.append(current_string)

    # Filter for potentially interesting strings
    interesting_strings = []
    keywords = [
        "gps",
        "location",
        "coordinate",
        "latitude",
        "longitude",
        "place",
        "address",
        "geo",
        "map",
        "camera",
        "phone",
        "device",
    ]

    for s in strings:
        s_lower = s.lower()
        if any(keyword in s_lower for keyword in keywords):
            interesting_strings.append(s)
        elif len(s) > 20 and any(c.isdigit() for c in s):  # Long strings with numbers
            interesting_strings.append(s)

    return {
        "all_strings_count": len(strings),
        "interesting_strings": interesting_strings[:20],  # Limit output
        "sample_strings": strings[:10] if strings else [],
    }


def parse_webp_chunks(content):
    """Parse WebP file format chunks for metadata."""
    chunks = []

    if not content.startswith(b"RIFF"):
        return {"error": "Not a valid WebP file"}

    # Skip RIFF header (12 bytes)
    pos = 12

    while pos < len(content) - 8:
        try:
            # Read chunk header
            chunk_id = content[pos : pos + 4]
            chunk_size = struct.unpack("<I", content[pos + 4 : pos + 8])[0]

            chunk_data = content[pos + 8 : pos + 8 + chunk_size]

            chunks.append(
                {
                    "id": chunk_id.decode("ascii", errors="ignore"),
                    "size": chunk_size,
                    "position": pos,
                    "data_preview": chunk_data[:100].hex() if chunk_data else "",
                    "data_ascii": (
                        chunk_data[:100].decode("utf-8", errors="ignore")
                        if chunk_data
                        else ""
                    ),
                }
            )

            # Move to next chunk (with padding)
            pos += 8 + chunk_size
            if chunk_size % 2:  # WebP chunks are padded to even length
                pos += 1

        except (struct.error, UnicodeDecodeError):
            break

    return chunks


def deep_scan_image(file_path):
    """Perform comprehensive metadata extraction."""
    file_path = Path(file_path)

    results = {
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "scan_timestamp": None,
        "binary_analysis": {},
        "pil_analysis": {},
        "exifread_analysis": {},
    }

    # Binary analysis
    print("Scanning binary content...")
    results["binary_analysis"] = scan_binary_for_metadata(file_path)

    # PIL analysis
    if PIL_AVAILABLE:
        print("Analyzing with PIL...")
        try:
            with Image.open(file_path) as img:
                results["pil_analysis"] = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "info_keys": list(img.info.keys()),
                    "info_data": dict(img.info),
                    "has_exif_method": hasattr(img, "_getexif"),
                    "has_getexif_method": hasattr(img, "getexif"),
                }

                # Try multiple EXIF extraction methods
                if hasattr(img, "_getexif"):
                    exif = img._getexif()
                    if exif:
                        results["pil_analysis"]["_getexif_data"] = exif

                if hasattr(img, "getexif"):
                    exif = img.getexif()
                    if exif:
                        results["pil_analysis"]["getexif_data"] = dict(exif)

        except Exception as e:
            results["pil_analysis"]["error"] = str(e)

    # ExifRead analysis
    if EXIFREAD_AVAILABLE:
        print("Analyzing with ExifRead...")
        try:
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f, details=True)
                if tags:
                    results["exifread_analysis"] = {
                        tag: str(value) for tag, value in tags.items()
                    }
        except Exception as e:
            results["exifread_analysis"]["error"] = str(e)

    return results


def main():
    if len(sys.argv) != 2:
        print("Usage: python deep_metadata_scanner.py <image_file>")
        sys.exit(1)

    image_path = sys.argv[1]

    print(f"Deep scanning: {image_path}")
    print("=" * 60)

    results = deep_scan_image(image_path)

    # Save results
    output_file = f"deep_scan_{Path(image_path).stem}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Results saved to: {output_file}")

    # Print summary
    print("\nSUMMARY:")
    print("-" * 40)

    binary_sigs = results["binary_analysis"].get("binary_signatures", [])
    if binary_sigs:
        print(f"Found {len(binary_sigs)} binary signatures:")
        for sig in binary_sigs:
            print(f"  - {sig['description']}: {len(sig['positions'])} occurrences")

    interesting_strings = (
        results["binary_analysis"]
        .get("text_strings", {})
        .get("interesting_strings", [])
    )
    if interesting_strings:
        print(f"\nInteresting text strings found:")
        for s in interesting_strings[:5]:
            print(f"  - {s}")

    webp_chunks = results["binary_analysis"].get("webp_chunks", [])
    if isinstance(webp_chunks, list) and webp_chunks:
        print(f"\nWebP chunks found:")
        for chunk in webp_chunks:
            print(f"  - {chunk['id']}: {chunk['size']} bytes")

    pil_info = results.get("pil_analysis", {}).get("info_data", {})
    if pil_info:
        print(f"\nPIL image info:")
        for key, value in pil_info.items():
            print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only Nintendo Switch NRO structural inventory (no execution/extraction)."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

MAX_SIZE = 256 * 1024 * 1024

def inspect_nro(data: bytes) -> dict:
    if len(data) < 0x80 or data[0x10:0x14] != b"NRO0":
        raise ValueError("missing NRO0 header")
    image_size = struct.unpack_from("<I", data, 0x18)[0]
    if not 0x80 <= image_size <= len(data):
        raise ValueError("invalid NRO image size")
    names = ("text", "rodata", "data")
    segments = {}
    last_end = 0
    for index, name in enumerate(names):
        offset, size = struct.unpack_from("<II", data, 0x20 + index * 8)
        if offset < last_end or offset + size > image_size:
            raise ValueError("out-of-bounds or overlapping segment")
        segments[name] = {"offset": offset, "size": size}
        last_end = offset + size
    assets = {}
    if len(data) > image_size:
        if data[image_size:image_size+4] != b"ASET" or len(data) < image_size + 0x38:
            raise ValueError("unexpected trailing data")
        for index, name in enumerate(("icon", "nacp", "romfs")):
            offset, size = struct.unpack_from("<QQ", data, image_size + 8 + index * 16)
            if size and (offset < 0x38 or offset > len(data) - image_size or size > len(data) - image_size - offset):
                raise ValueError(f"invalid {name} asset range")
            assets[name] = {"present": size > 0, "size": size}
    return {
        "schema_version": 1, "format": "NRO0",
        "total_size": len(data), "image_size": image_size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "mod0_marker_present": data.find(b"MOD0", 0, min(image_size, 0x1000)) >= 0,
        "segments": segments, "assets": assets,
        "nxnative_nsp_builder_compatible": False,
        "gameplay_compatibility_proven": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    if args.file.is_symlink() or not args.file.is_file() or args.file.stat().st_size > MAX_SIZE:
        parser.error("expected regular NRO file (up to 256 MiB)")
    try:
        report = inspect_nro(args.file.read_bytes())
    except (ValueError, struct.error) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

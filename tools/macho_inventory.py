#!/usr/bin/env python3
"""Inspect Mach-O arm64 headers and load commands without executing the binary."""
import argparse
import json
import struct
from pathlib import Path

MAGIC_64_LE = b"\xcf\xfa\xed\xfe"
FAT_BE = b"\xca\xfe\xba\xbe"
CPU_ARM64 = 0x0100000c
LC_BUILD_VERSION = 0x32
LC_VERSION_MIN_IPHONEOS = 0x25

def inspect_bytes(data: bytes) -> dict:
    result = {"schema_version": 1, "arm64": False, "format": "unknown",
              "instruction_compatibility_proven": False, "slices": []}
    offsets = []
    if data[:4] == MAGIC_64_LE:
        offsets = [0]
        result["format"] = "macho64"
    elif data[:4] == FAT_BE:
        if len(data) < 8:
            raise ValueError("truncated fat header")
        count = struct.unpack_from(">I", data, 4)[0]
        if count > 64 or len(data) < 8 + count * 20:
            raise ValueError("invalid fat slice table")
        result["format"] = "fat32"
        for i in range(count):
            cpu, _, offset, size, _ = struct.unpack_from(">IIIII", data, 8 + i * 20)
            if offset > len(data) or size > len(data) - offset:
                raise ValueError("slice exceeds input")
            if cpu == CPU_ARM64:
                offsets.append(offset)
    else:
        raise ValueError("unsupported file magic")
    for offset in offsets:
        if data[offset:offset+4] != MAGIC_64_LE or len(data) - offset < 32:
            raise ValueError("invalid arm64 Mach-O header")
        _, cpu, subtype, _, ncmds, sizeofcmds, _, _ = struct.unpack_from("<IiiIIIII", data, offset)
        if cpu != CPU_ARM64:
            continue
        if ncmds > 100000 or sizeofcmds > len(data) - offset - 32:
            raise ValueError("invalid load command region")
        pos, end = offset+32, offset+32+sizeofcmds
        platforms = []
        for _ in range(ncmds):
            if pos + 8 > end:
                raise ValueError("truncated load command")
            cmd, size = struct.unpack_from("<II", data, pos)
            if size < 8 or pos + size > end:
                raise ValueError("invalid load command size")
            if cmd == LC_BUILD_VERSION and size >= 24:
                platform, minos, sdk, _ = struct.unpack_from("<IIII", data, pos+8)
                platforms.append({"platform_id": platform, "min_os_packed": minos, "sdk_packed": sdk})
            elif cmd == LC_VERSION_MIN_IPHONEOS and size >= 16:
                minos, sdk = struct.unpack_from("<II", data, pos+8)
                platforms.append({"platform_id": "legacy_iphoneos", "min_os_packed": minos, "sdk_packed": sdk})
            pos += size
        result["slices"].append({"cpu_type": "arm64", "cpu_subtype": subtype, "platforms": platforms})
    result["arm64"] = bool(result["slices"])
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    args = parser.parse_args()
    try:
        path = args.binary
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 1024*1024*1024:
            raise ValueError("expected a regular non-symlink Mach-O file no larger than 1 GiB")
        report = inspect_bytes(path.read_bytes())
    except (OSError, ValueError, struct.error) as exc:
        parser.exit(2, f"Unable to inspect Mach-O: {exc}\n")
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

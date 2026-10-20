"""Read-only classification of NRO RELR relocation sites by mapped segment.

This is a structural report, not a relocator or proof of safe execution.
"""
import struct
from tools.relr_decoder import relr_sites


def relocation_map(data: bytes) -> dict:
    if len(data) < 0x80 or data[0x10:0x14] != b"NRO0":
        raise ValueError("not an NRO")
    image_size = struct.unpack_from("<I", data, 0x18)[0]
    if not 0x80 <= image_size <= len(data):
        raise ValueError("invalid NRO image size")
    segments = {}
    previous_end = 0
    for i, name in enumerate(("text", "rodata", "data")):
        begin, size = struct.unpack_from("<II", data, 0x20 + 8 * i)
        if begin < previous_end or begin + size > image_size:
            raise ValueError("invalid segment boundaries")
        segments[name] = (begin, begin + size)
        previous_end = begin + size
    mod = struct.unpack_from("<I", data, 4)[0]
    if mod > image_size - 0x1c or data[mod:mod + 4] != b"MOD0":
        raise ValueError("invalid MOD0 location")
    dynamic = mod + struct.unpack_from("<i", data, mod + 4)[0]
    if not 0 <= dynamic <= image_size - 16:
        raise ValueError("invalid dynamic table")
    tags = {}
    for index in range(512):
        pos = dynamic + index * 16
        if pos + 16 > image_size:
            raise ValueError("unterminated dynamic table")
        key, value = struct.unpack_from("<QQ", data, pos)
        if key == 0:
            break
        if key in tags and tags[key] != value:
            raise ValueError("conflicting dynamic tag")
        tags[key] = value
    else:
        raise ValueError("dynamic table too long")
    relr_size = tags.get(35, 0)
    relr_offset = tags.get(36, 0)
    if relr_size and tags.get(37) not in (None, 8):
        raise ValueError("unsupported RELR width")
    sites = relr_sites(data, relr_offset, relr_size, image_size) if relr_size else []
    counts = {name: 0 for name in (*segments, "unmapped")}
    for site in sites:
        name = next((n for n, (a, b) in segments.items() if a <= site and site + 8 <= b), "unmapped")
        counts[name] += 1
    return {
        "schema_version": 1,
        "relr_site_count": len(sites),
        "relr_targets_by_segment": counts,
        "relr_target_min": min(sites) if sites else None,
        "relr_target_max": max(sites) if sites else None,
        "has_unmapped_targets": counts["unmapped"] != 0,
        "relocation_writes_performed": False,
        "native_execution_verified": False,
    }

#!/usr/bin/env python3
"""Read-only Switch NRO MOD0 and ELF dynamic-table inventory (no code execution)."""
import argparse
import json
import struct
from pathlib import Path

DT_NAMES = {
    0:"NULL", 4:"HASH", 5:"STRTAB", 6:"SYMTAB", 7:"RELA", 8:"RELASZ",
    9:"RELAENT", 10:"STRSZ", 11:"SYMENT", 12:"INIT", 13:"FINI",
    23:"JMPREL", 24:"BIND_NOW", 25:"INIT_ARRAY", 26:"FINI_ARRAY",
    27:"INIT_ARRAYSZ", 28:"FINI_ARRAYSZ", 35:"RELRSZ", 36:"RELR",
    37:"RELRENT", 0x6ffffffb:"FLAGS_1",
}
MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_ENTRIES = 512

def inspect_mod0(data: bytes) -> dict:
    if len(data) < 0x80 or data[0x10:0x14] != b"NRO0":
        raise ValueError("invalid NRO header")
    image_size = struct.unpack_from("<I", data, 0x18)[0]
    if image_size < 0x80 or image_size > len(data):
        raise ValueError("invalid image length")
    # The first word contains a branch instruction; the next is the MOD0 offset.
    mod_offset = struct.unpack_from("<I", data, 4)[0]
    # Most homebrew images put the MOD0 pointer here. Never scan arbitrary
    # image bytes as a fallback: a string containing MOD0 is not an ABI header.
    if mod_offset > image_size - 0x1c or data[mod_offset:mod_offset+4] != b"MOD0":
        raise ValueError("missing MOD0 at declared offset")
    dynamic_relative = struct.unpack_from("<i", data, mod_offset+4)[0]
    dynamic_offset = mod_offset + dynamic_relative
    if not (0 <= dynamic_offset <= image_size-16):
        raise ValueError("dynamic table outside image")
    tags = []
    for i in range(MAX_ENTRIES):
        offset = dynamic_offset + 16*i
        if offset+16 > image_size:
            raise ValueError("dynamic table is truncated")
        tag, value = struct.unpack_from("<QQ", data, offset)
        name = DT_NAMES.get(tag, "UNKNOWN")
        tags.append({"tag": f"0x{tag:x}", "name": name, "value": f"0x{value:x}"})
        if tag == 0:
            break
    else:
        raise ValueError("dynamic table exceeds entry limit")
    values = {int(x["tag"],16): int(x["value"],16) for x in tags}
    if values.get(37) not in (None, 8):
        raise ValueError("unexpected RELR entry width")
    for addr_tag, size_tag in ((36,35),(7,8)):
        addr, size = values.get(addr_tag,0), values.get(size_tag,0)
        if size and (addr > image_size or size > image_size - addr):
            raise ValueError("relocation table outside image")
    return {
        "schema_version": 1, "format": "NRO0",
        "mod0_offset": mod_offset, "dynamic_offset": dynamic_offset,
        "dynamic_entries": tags,
        "rela_present": values.get(8,0) > 0,
        "relr_present": values.get(35,0) > 0,
        "relr_size": values.get(35,0),
        "relr_entry_size": values.get(37, None),
        "relocations_applied": False,
        "executable_loaded": False,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("nro", type=Path)
    args = parser.parse_args()
    if args.nro.is_symlink() or not args.nro.is_file() or args.nro.stat().st_size > MAX_FILE_BYTES:
        parser.error("expected a regular NRO file up to 256 MiB")
    try:
        result = inspect_mod0(args.nro.read_bytes())
    except (ValueError, struct.error) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

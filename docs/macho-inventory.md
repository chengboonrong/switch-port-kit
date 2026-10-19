# Mach-O Inventory

Runs on an **owned, locally built** binary; no keys or game files should be uploaded.

```sh
python3 tools/macho_inventory.py /private/path/to/app-executable
```

Reads Mach-O 64-bit little-endian arm64 headers and 32-bit big-endian fat Mach-O slice tables, including supported build-version load commands. It emits only basic metadata and no binary bytes, strings or executable content.

**Not an instruction-set validator.** arm64 headers, CPU subtype and deployment minimum do not guarantee A17 Pro instruction compatibility. Disassembly, actual compiler settings and a real device execution test are still required. Unsupported formats are rejected. Review stdout before sharing.

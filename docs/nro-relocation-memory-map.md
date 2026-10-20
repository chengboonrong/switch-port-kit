# NRO relocation target memory map

This tool classifies DT_RELR target addresses by the NRO's declared text, rodata and data segments. It never applies relocations, modifies the file, or executes code.

### Evidence from the supplied 2048.nro (local-only)
- NRO image size: 0x148000
- text: [0x0, 0x2b000)
- rodata: [0x2b000, 0x143000)
- data: [0x143000, 0x148000)
- DT_RELR: offset 0x2b010, 0x90 bytes / 18 entries
- Decoded relocation sites: **521**
- All **521 sites fall within the data segment** (0 unmapped).

This strongly suggests no relocation writes are needed in the read-only text section for this version of this sample, but says **nothing** about its ABI, imports, signing, service dependencies, or whether it can run on iPadOS. Additional relocations or fixup schemes must be investigated independently.

Usage (from the repo root):
```sh
python3 -c 'import json,sys; from tools.nro_relocation_map import relocation_map; print(json.dumps(relocation_map(open(sys.argv[1],"rb").read()),indent=2))' /private/2048.nro
```

No NRO binaries or extracted assets belong in Git.

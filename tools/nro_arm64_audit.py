"""Read-only scan for selected AArch64 privileged/trap instruction encodings.

Only examines the NRO text segment. This is not a disassembler, and results
may include literal data inside .text. It does not identify x18 usage.
"""
import struct

def audit_arm64_text(blob: bytes) -> dict:
    if len(blob) < 0x80 or blob[0x10:0x14] != b"NRO0":
        raise ValueError("not an NRO")
    image_size = struct.unpack_from("<I", blob, 0x18)[0]
    text_offset, text_size = struct.unpack_from("<II", blob, 0x20)
    if not (0x80 <= image_size <= len(blob) and text_size % 4 == 0 and
            text_offset % 4 == 0 and text_offset <= image_size and
            text_size <= image_size-text_offset):
        raise ValueError("invalid NRO text section")
    hits = {key: [] for key in ("svc", "hvc", "smc", "mrs", "msr_register")}
    for off in range(text_offset, text_offset + text_size, 4):
        w = struct.unpack_from("<I", blob, off)[0]
        if w & 0xffe0001f == 0xd4000001:
            hits["svc"].append({"offset":off,"immediate":(w>>5)&0xffff})
        elif w & 0xffe0001f == 0xd4000002:
            hits["hvc"].append({"offset":off,"immediate":(w>>5)&0xffff})
        elif w & 0xffe0001f == 0xd4000003:
            hits["smc"].append({"offset":off,"immediate":(w>>5)&0xffff})
        elif w & 0xfff00000 == 0xd5300000:
            hits["mrs"].append({"offset":off,"instruction":f"0x{w:08x}"})
        elif w & 0xfff00000 == 0xd5100000:
            hits["msr_register"].append({"offset":off,"instruction":f"0x{w:08x}"})
    return {
        "schema_version":1,"text_bytes_scanned":text_size,
        "counts":{key:len(value) for key,value in hits.items()},
        "hits":hits,"scope":"selected instruction encodings; no control-flow disassembly",
        "x18_usage_analyzed":False,"executed":False,
    }

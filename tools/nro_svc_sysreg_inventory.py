"""Read-only inventory of AArch64 SVC immediates and MRS system registers."""
from collections import Counter
import struct

def inventory(data: bytes) -> dict:
    if len(data) < 0x80 or data[0x10:0x14] != b"NRO0":
        raise ValueError("invalid NRO")
    image_size = struct.unpack_from("<I", data, 0x18)[0]
    text_off, text_size = struct.unpack_from("<II", data, 0x20)
    if not 0x80 <= image_size <= len(data) or text_off % 4 or text_size % 4 or text_off > image_size or text_size > image_size - text_off:
        raise ValueError("invalid text span")
    svc = Counter()
    mrs = Counter()
    msr = Counter()
    for at in range(text_off, text_off + text_size, 4):
        word = struct.unpack_from("<I", data, at)[0]
        if word & 0xffe0001f == 0xd4000001:
            svc[(word >> 5) & 0xffff] += 1
        if word & 0xfff00000 in (0xd5300000, 0xd5100000):
            op0 = (word >> 19) & 3
            op1 = (word >> 16) & 7
            crn = (word >> 12) & 15
            crm = (word >> 8) & 15
            op2 = (word >> 5) & 7
            name = f"S{op0}_{op1}_C{crn}_C{crm}_{op2}"
            (mrs if word & 0x00200000 else msr)[name] += 1
    return {
        "schema_version": 1,
        "svc_immediate_counts": {f"0x{k:x}": svc[k] for k in sorted(svc)},
        "mrs_register_counts": dict(sorted(mrs.items())),
        "msr_register_counts": dict(sorted(msr.items())),
        "counts_are_static_candidates": True,
        "instructions_executed": False,
        "control_flow_analyzed": False,
    }

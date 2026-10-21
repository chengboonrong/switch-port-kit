"""Read-only partial AArch64 x18 register operand scan (not full disassembly)."""
import struct

def audit_x18(data: bytes) -> dict:
    if len(data) < 0x80 or data[0x10:0x14] != b"NRO0":
        raise ValueError("invalid NRO")
    image_size = struct.unpack_from("<I", data, 0x18)[0]
    off, length = struct.unpack_from("<II", data, 0x20)
    if not (0x80 <= image_size <= len(data) and off % 4 == length % 4 == 0
            and off <= image_size and length <= image_size-off):
        raise ValueError("invalid text span")
    hits = []
    for addr in range(off, off+length, 4):
        word = struct.unpack_from("<I", data, addr)[0]
        family, regs = None, ()
        if word & 0x1f000000 == 0x11000000:
            family, regs = "add_sub_immediate", (word & 31, (word >> 5) & 31)
        elif word & 0x3b000000 == 0x39000000:
            family, regs = "load_store_unsigned_offset", (word & 31, (word >> 5) & 31)
        elif word & 0x1fe00000 == 0x0b000000:
            # ADD/SUB shifted-register forms; Rm/Rn/Rd are real GPRs.
            family, regs = "add_sub_shifted_register", (word & 31, (word >> 5) & 31, (word >> 16) & 31)
        elif word & 0x1f000000 == 0x0a000000:
            # AND/BIC/ORR/ORN/EOR/EON/ANDS/BICS shifted-register.
            # These have three register fields, including x18 as Rm.
            family, regs = "logical_shifted_register", (word & 31, (word >> 5) & 31, (word >> 16) & 31)
        elif word & 0x1f800000 == 0x12800000:
            family, regs = "move_wide_immediate", (word & 31,)
        if 18 in regs:
            hits.append({"offset": addr, "instruction": f"0x{word:08x}", "family": family})
    counts = {name: sum(hit["family"] == name for hit in hits)
              for name in ("add_sub_immediate", "load_store_unsigned_offset", "add_sub_shifted_register", "logical_shifted_register", "move_wide_immediate")}
    return {"schema_version": 1, "recognized_x18_candidates": len(hits),
            "by_instruction_family": counts, "hits": hits,
            "coverage": "partial; other AArch64 instructions NOT examined",
            "control_flow_analyzed": False, "executable_loaded": False}

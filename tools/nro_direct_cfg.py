"""Conservative AArch64 direct-branch candidate graph from NRO entry.

No execution. Indirect branches remain unresolved, and code/data confusion can
produce false-positive edges; this is NOT a proof of reachable game code.
"""
import struct
from collections import Counter, deque

def _signed(value, bits):
    sign = 1 << (bits - 1)
    return (value ^ sign) - sign

def analyze_entry(blob: bytes, max_instructions: int = 100000, start: int | None = None) -> dict:
    """Explore from the text entry, or from `start` (offset relative to text)."""
    if len(blob) < 0x80 or blob[0x10:0x14] != b"NRO0":
        raise ValueError("invalid NRO")
    image_size = struct.unpack_from("<I", blob, 0x18)[0]
    text_off, text_size = struct.unpack_from("<II", blob, 0x20)
    if not (0x80 <= image_size <= len(blob) and text_off % 4 == text_size % 4 == 0
            and text_size > 0 and text_off <= image_size and text_size <= image_size-text_off):
        raise ValueError("invalid text segment")
    if not 1 <= max_instructions <= 1000000:
        raise ValueError("invalid instruction limit")
    end = text_off + text_size
    entry = text_off if start is None else text_off + start
    if not (text_off <= entry < end and entry % 4 == 0):
        raise ValueError("invalid start offset")
    queue = deque([entry])
    visited = set()
    kinds = Counter()
    svc_immediates = Counter()
    indirect = set()
    invalid_edges = 0
    while queue:
        pc = queue.popleft()
        if pc in visited:
            continue
        if pc < text_off or pc >= end or pc % 4:
            invalid_edges += 1
            continue
        if len(visited) >= max_instructions:
            raise ValueError("instruction limit exceeded")
        visited.add(pc)
        word = struct.unpack_from("<I", blob, pc)[0]
        next_pc = pc + 4
        targets = []
        if word & 0x7c000000 == 0x14000000:
            target = pc + (_signed(word & 0x03ffffff, 26) << 2)
            if word & 0x80000000:
                kinds["bl"] += 1
                targets = [target, next_pc]
            else:
                kinds["b"] += 1
                targets = [target]
        elif word & 0xff000010 == 0x54000000:
            kinds["b_cond"] += 1
            targets = [pc + (_signed((word >> 5) & 0x7ffff, 19) << 2), next_pc]
        elif word & 0x7e000000 == 0x34000000:
            kinds["cbz_cbnz"] += 1
            targets = [pc + (_signed((word >> 5) & 0x7ffff, 19) << 2), next_pc]
        elif word & 0x7e000000 == 0x36000000:
            kinds["tbz_tbnz"] += 1
            targets = [pc + (_signed((word >> 5) & 0x3fff, 14) << 2), next_pc]
        elif word & 0xfffffc1f in (0xd61f0000, 0xd65f0000):
            kinds["indirect_or_return"] += 1
            indirect.add(pc)
        elif word & 0xfffffc1f == 0xd63f0000:
            kinds["blr"] += 1
            indirect.add(pc)
            targets = [next_pc]
        elif word & 0xffe0001f == 0xd4000001:
            kinds["svc"] += 1
            svc_immediates[(word >> 5) & 0xffff] += 1
            targets = [next_pc]
        elif word & 0xffe0001f in (0xd4000002, 0xd4000003, 0xd4200000):
            kinds["trap_stop"] += 1
        elif word & 0xffff0000 == 0:
            # UDF #imm16: permanently undefined, emitted after noreturn calls.
            kinds["udf_stop"] += 1
        else:
            targets = [next_pc]
        queue.extend(targets)
    return {
        "schema_version": 1, "entry_offset": entry,
        "visited_instruction_count": len(visited),
        "text_instruction_slots": text_size // 4,
        "branch_kinds": dict(sorted(kinds.items())),
        "reachable_svc_candidates": {f"0x{k:x}":v for k,v in sorted(svc_immediates.items())},
        "indirect_frontier_count": len(indirect),
        "out_of_text_edge_count": invalid_edges,
        "control_flow_complete": False,
        "runtime_execution_proven": False,
    }

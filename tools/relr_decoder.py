"""Statically decode ELF DT_RELR relocation target offsets without applying them.

No executable memory, relocation writes, or file extraction.
"""
import struct

def relr_sites(image: bytes, offset: int, byte_count: int, image_size: int,
               max_sites: int = 500_000) -> list[int]:
    if byte_count < 0 or byte_count % 8 != 0 or offset < 0:
        raise ValueError("invalid RELR table span")
    if image_size > len(image) or image_size < 0:
        raise ValueError("invalid image bounds")
    if offset > image_size or byte_count > image_size - offset:
        raise ValueError("RELR table lies outside image")
    if max_sites < 1:
        raise ValueError("max_sites must be positive")
    result = []
    cursor = None

    def append_target(target):
        if target % 8 or target < 0 or target > image_size - 8:
            raise ValueError("RELR relocation target outside image or misaligned")
        if len(result) >= max_sites:
            raise ValueError("RELR relocation count exceeds safety limit")
        result.append(target)

    for pos in range(offset, offset + byte_count, 8):
        word = struct.unpack_from("<Q", image, pos)[0]
        if (word & 1) == 0:
            append_target(word)
            cursor = word + 8
        else:
            if cursor is None:
                raise ValueError("RELR bitmap has no preceding address")
            bitmap = word >> 1
            for bit in range(63):
                if bitmap & (1 << bit):
                    append_target(cursor + bit * 8)
            cursor += 63 * 8
    if len(result) != len(set(result)):
        raise ValueError("duplicate RELR targets")
    return result

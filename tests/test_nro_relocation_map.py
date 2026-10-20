import struct
import unittest
from tools.nro_relocation_map import relocation_map

def nro_fixture(relr_target=0x180):
    b = bytearray(0x200)
    b[0x10:0x14] = b"NRO0"
    struct.pack_into("<I", b, 4, 0x80)
    struct.pack_into("<I", b, 0x18, 0x200)
    for i, (off, size) in enumerate(((0, 0x100), (0x100, 0x60), (0x160, 0xa0))):
        struct.pack_into("<II", b, 0x20 + i * 8, off, size)
    b[0x80:0x84] = b"MOD0"
    struct.pack_into("<i", b, 0x84, 0x20)
    struct.pack_into("<QQ", b, 0xa0, 36, 0xc0)
    struct.pack_into("<QQ", b, 0xb0, 35, 8)
    struct.pack_into("<QQ", b, 0xc0, 37, 8)
    struct.pack_into("<QQ", b, 0xd0, 0, 0)
    struct.pack_into("<Q", b, 0xc0 + 0x60, relr_target)
    # RELR bytes reside at 0x120, not the dynamic table.
    struct.pack_into("<QQ", b, 0xa0, 36, 0x120)
    struct.pack_into("<Q", b, 0x120, relr_target)
    return b

class RelocationMapTests(unittest.TestCase):
    def test_data_target(self):
        r = relocation_map(bytes(nro_fixture()))
        self.assertEqual(r["relr_targets_by_segment"]["data"], 1)
        self.assertFalse(r["native_execution_verified"])

    def test_text_target(self):
        r = relocation_map(bytes(nro_fixture(0x20)))
        self.assertEqual(r["relr_targets_by_segment"]["text"], 1)

    def test_unaligned_target_rejected(self):
        with self.assertRaises(ValueError):
            relocation_map(bytes(nro_fixture(0x181)))

    def test_invalid_magic(self):
        with self.assertRaises(ValueError):
            relocation_map(bytes(0x200))

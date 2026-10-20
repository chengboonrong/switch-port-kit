import struct
import unittest
from tools.relr_decoder import relr_sites

class RelrTests(unittest.TestCase):
    def test_explicit_then_bitmap(self):
        data = bytearray(0x100)
        struct.pack_into("<QQ", data, 0x80, 0x20, 0b1011)
        self.assertEqual(relr_sites(data, 0x80, 16, 0x100), [0x20, 0x28, 0x38])
    def test_multiple_explicit(self):
        data = bytearray(0x100)
        struct.pack_into("<QQ", data, 0x80, 0x10, 0x40)
        self.assertEqual(relr_sites(data, 0x80, 16, 0x100), [0x10, 0x40])
    def test_bitmap_without_base(self):
        data = struct.pack("<Q", 3)
        with self.assertRaisesRegex(ValueError, "preceding"):
            relr_sites(data, 0, 8, len(data))
    def test_out_of_bounds_target(self):
        data = bytearray(0x40)
        struct.pack_into("<Q", data, 0x10, 0x40)
        with self.assertRaisesRegex(ValueError, "outside"):
            relr_sites(data, 0x10, 8, len(data))
    def test_count_limit(self):
        data = bytearray(0x100)
        struct.pack_into("<QQ", data, 0x80, 0x10, 0b111)
        with self.assertRaisesRegex(ValueError, "safety limit"):
            relr_sites(data, 0x80, 16, 0x100, max_sites=1)
    def test_rejects_duplicate(self):
        data = bytearray(0x100)
        struct.pack_into("<QQ", data, 0x80, 0x10, 0x10)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            relr_sites(data, 0x80, 16, 0x100)

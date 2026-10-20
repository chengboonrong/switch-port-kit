import struct
import unittest
from tools.nro_inspector import inspect_nro

def fixture():
    data = bytearray(0x100)
    data[0x10:0x14] = b"NRO0"
    struct.pack_into("<I", data, 0x18, 0x100)
    for i, (o, n) in enumerate(((0, 0x40), (0x40, 0x40), (0x80, 0x20))):
        struct.pack_into("<II", data, 0x20 + i * 8, o, n)
    return data

class NroTests(unittest.TestCase):
    def test_valid_minimal(self):
        result = inspect_nro(bytes(fixture()))
        self.assertEqual(result["format"], "NRO0")
        self.assertFalse(result["nxnative_nsp_builder_compatible"])
    def test_wrong_magic(self):
        with self.assertRaises(ValueError):
            inspect_nro(bytes(256))
    def test_invalid_segment(self):
        data = fixture()
        struct.pack_into("<II", data, 0x20, 0, 0xffffffff)
        with self.assertRaises(ValueError):
            inspect_nro(bytes(data))
    def test_assets(self):
        data = fixture() + bytearray(0x50)
        data[0x100:0x104] = b"ASET"
        struct.pack_into("<QQ", data, 0x108, 0x38, 24)
        data.extend(b"\x00" * 24)
        result = inspect_nro(bytes(data))
        self.assertTrue(result["assets"]["icon"]["present"])
    def test_unexpected_trailer(self):
        with self.assertRaises(ValueError):
            inspect_nro(bytes(fixture()) + b"bad")

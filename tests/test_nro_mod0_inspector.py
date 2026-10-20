import struct
import unittest
from tools.nro_mod0_inspector import inspect_mod0

def fixture():
    b=bytearray(0x200)
    b[0x10:0x14]=b"NRO0"
    struct.pack_into("<I",b,4,0x80)
    struct.pack_into("<I",b,0x18,len(b))
    b[0x80:0x84]=b"MOD0"
    struct.pack_into("<i",b,0x84,0x20)
    struct.pack_into("<QQ",b,0xa0,36,0xc0)
    struct.pack_into("<QQ",b,0xb0,35,8)
    struct.pack_into("<QQ",b,0xc0,0,0) # overlap fixture data but valid terminator
    return b

class NroMod0Tests(unittest.TestCase):
    def test_detects_relr(self):
        r=inspect_mod0(bytes(fixture()))
        self.assertTrue(r["relr_present"])
        self.assertFalse(r["relocations_applied"])
    def test_rejects_missing_header(self):
        with self.assertRaises(ValueError):
            inspect_mod0(bytes(0x200))
    def test_rejects_bad_mod0_pointer(self):
        b=fixture()
        struct.pack_into("<I",b,4,0x300)
        with self.assertRaises(ValueError):
            inspect_mod0(bytes(b))
    def test_rejects_out_of_bounds_dynamic(self):
        b=fixture()
        struct.pack_into("<i",b,0x84,0x1000)
        with self.assertRaises(ValueError):
            inspect_mod0(bytes(b))

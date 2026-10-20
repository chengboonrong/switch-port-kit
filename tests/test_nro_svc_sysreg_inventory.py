import struct
import unittest
from tools.nro_svc_sysreg_inventory import inventory

def sample(words):
    b=bytearray(0x100)
    b[0x10:0x14]=b"NRO0"
    struct.pack_into("<I",b,0x18,len(b))
    struct.pack_into("<II",b,0x20,0x80,len(words)*4)
    for i,w in enumerate(words):struct.pack_into("<I",b,0x80+i*4,w)
    return bytes(b)

class InventoryTests(unittest.TestCase):
    def test_svc_counts(self):
        r=inventory(sample([0xd4000021,0xd4000021,0xd503201f]))
        self.assertEqual(r["svc_immediate_counts"]["0x1"],2)
    def test_sysreg_fields(self):
        r=inventory(sample([0xd53bd060]))
        self.assertEqual(r["mrs_register_counts"]["S3_3_C13_C0_3"],1)
    def test_invalid(self):
        with self.assertRaises(ValueError):inventory(bytes(256))

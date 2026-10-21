import struct
import unittest
from tools.nro_x18_audit import audit_x18

def sample(words):
    b = bytearray(0x100)
    b[0x10:0x14] = b"NRO0"
    struct.pack_into("<I", b, 0x18, len(b))
    struct.pack_into("<II", b, 0x20, 0x80, len(words)*4)
    for i, word in enumerate(words):
        struct.pack_into("<I", b, 0x80+i*4, word)
    return bytes(b)

class X18Tests(unittest.TestCase):
    def test_supported_families(self):
        result = audit_x18(sample([0x91000252, 0xf9400252, 0xd2800012]))
        self.assertEqual(result["recognized_x18_candidates"], 3)
        self.assertFalse(result["control_flow_analyzed"])
    def test_unrelated_word(self):
        self.assertEqual(audit_x18(sample([0xd503201f]))["recognized_x18_candidates"], 0)
    def test_invalid_nro(self):
        with self.assertRaises(ValueError):
            audit_x18(bytes(256))

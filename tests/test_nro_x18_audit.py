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

    def test_shifted_register_detects_all_operand_positions(self):
        # ADD X0, X18, X1; ADD X18, X0, X1; ADD X0, X1, X18
        words = [0x8b010240, 0x8b010012, 0x8b120020]
        r = audit_x18(sample(words))
        self.assertEqual(r["by_instruction_family"]["add_sub_shifted_register"], 3)
    def test_shifted_register_without_x18(self):
        r = audit_x18(sample([0x8b010000]))
        self.assertEqual(r["recognized_x18_candidates"], 0)

    def test_logical_shifted_register_x18_positions(self):
        # ORR X0,X18,X1; ORR X18,X0,X1; ORR X0,X1,X18
        words = [0xaa010240, 0xaa010012, 0xaa120020]
        r = audit_x18(sample(words))
        self.assertEqual(r["by_instruction_family"]["logical_shifted_register"], 3)

    def test_logical_register_unrelated(self):
        r = audit_x18(sample([0xaa010000]))
        self.assertEqual(r["recognized_x18_candidates"], 0)

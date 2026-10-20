import struct
import unittest
from tools.nro_arm64_audit import audit_arm64_text

def fixture(words):
    blob=bytearray(0x100)
    blob[0x10:0x14]=b"NRO0"
    struct.pack_into("<I",blob,0x18,len(blob))
    struct.pack_into("<II",blob,0x20,0x80,4*len(words))
    for i,word in enumerate(words):
        struct.pack_into("<I",blob,0x80+i*4,word)
    return bytes(blob)

class Arm64AuditTests(unittest.TestCase):
    def test_svc_immediate(self):
        report=audit_arm64_text(fixture([0xd4000001 | (0x42<<5)]))
        self.assertEqual(report["hits"]["svc"][0]["immediate"],0x42)
    def test_other_traps(self):
        r=audit_arm64_text(fixture([0xd4000002,0xd4000003]))
        self.assertEqual(r["counts"]["hvc"],1)
        self.assertEqual(r["counts"]["smc"],1)
    def test_system_registers(self):
        r=audit_arm64_text(fixture([0xd53bd040,0xd51bd040]))
        self.assertEqual(r["counts"]["mrs"],1)
        self.assertEqual(r["counts"]["msr_register"],1)
    def test_malformed(self):
        with self.assertRaises(ValueError):
            audit_arm64_text(bytes(256))

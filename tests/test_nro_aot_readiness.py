import struct
import unittest
from tools.nro_aot_readiness import assess

def sample():
    b=bytearray(0x300)
    b[0x10:0x14]=b"NRO0"
    struct.pack_into("<I",b,4,0x80)
    struct.pack_into("<I",b,0x18,len(b))
    for i,(off,size) in enumerate(((0,0x100),(0x100,0x100),(0x200,0x100))):
        struct.pack_into("<II",b,0x20+i*8,off,size)
    b[0x80:0x84]=b"MOD0"
    struct.pack_into("<i",b,0x84,0x20)
    struct.pack_into("<QQ",b,0xa0,0,0)
    struct.pack_into("<I",b,0,0xd65f03c0)
    return bytes(b)

class AOTReadinessTests(unittest.TestCase):
    def test_always_blocks_unimplemented_aot(self):
        report=assess(sample())
        self.assertFalse(report["ready_to_build_ipa"])
        self.assertIn("signed_aot_macho_generation_unimplemented",report["blockers"])
    def test_bad_nro_rejected(self):
        with self.assertRaises(ValueError):
            assess(bytes(0x300))

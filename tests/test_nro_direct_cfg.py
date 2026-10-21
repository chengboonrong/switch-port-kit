import struct
import unittest
from tools.nro_direct_cfg import analyze_entry

def sample(words):
    b=bytearray(0x100)
    b[0x10:0x14]=b"NRO0"
    struct.pack_into("<I",b,0x18,len(b))
    struct.pack_into("<II",b,0x20,0x80,4*len(words))
    for i,w in enumerate(words):
        struct.pack_into("<I",b,0x80+4*i,w)
    return bytes(b)

class CFGTests(unittest.TestCase):
    def test_branch_skips_svc(self):
        r=analyze_entry(sample([0x14000002,0xd40000e1,0xd4000021,0xd65f03c0]))
        self.assertEqual(r["reachable_svc_candidates"],{"0x1":1})
        self.assertEqual(r["visited_instruction_count"],3)
    def test_conditional_explores_both(self):
        r=analyze_entry(sample([0x54000040,0xd4000021,0xd65f03c0]))
        self.assertEqual(r["reachable_svc_candidates"],{"0x1":1})
    def test_indirect_stops(self):
        r=analyze_entry(sample([0xd61f0000,0xd4000021]))
        self.assertEqual(r["indirect_frontier_count"],1)
        self.assertEqual(r["reachable_svc_candidates"],{})
    def test_limit(self):
        with self.assertRaises(ValueError):
            analyze_entry(sample([0x14000000]),max_instructions=0)
    def test_bad_magic(self):
        with self.assertRaises(ValueError):
            analyze_entry(bytes(256))

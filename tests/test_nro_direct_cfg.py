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
    def test_udf_stops_fallthrough(self):
        # A zero word (udf #0) after a call ends the path; the svc behind it is not reached.
        r=analyze_entry(sample([0x94000003,0x00000000,0xd4000021,0xd65f03c0]))
        self.assertEqual(r["reachable_svc_candidates"],{})
        self.assertEqual(r["branch_kinds"]["udf_stop"],1)
    def test_start_offset(self):
        r=analyze_entry(sample([0xd65f03c0,0xd4000041,0xd65f03c0]),start=4)
        self.assertEqual(r["entry_offset"],0x84)
        self.assertEqual(r["reachable_svc_candidates"],{"0x2":1})
        for bad in (2,12,-4,4.0):
            with self.assertRaises(ValueError):
                analyze_entry(sample([0xd65f03c0]*3),start=bad)
    def test_limit(self):
        with self.assertRaises(ValueError):
            analyze_entry(sample([0x14000000]),max_instructions=0)
    def test_bad_magic(self):
        with self.assertRaises(ValueError):
            analyze_entry(bytes(256))

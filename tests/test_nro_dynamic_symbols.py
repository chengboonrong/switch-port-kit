import struct
import unittest
from tools.nro_dynamic_symbols import inspect_dynamic_symbols

def fixture():
    b=bytearray(0x300)
    b[0x10:0x14]=b"NRO0"
    struct.pack_into("<I",b,4,0x80)
    struct.pack_into("<I",b,0x18,len(b))
    b[0x80:0x84]=b"MOD0"
    struct.pack_into("<i",b,0x84,0x20)
    entries=[(4,0x200),(5,0x240),(6,0x260),(10,1),(11,24),(0,0)]
    for i,t in enumerate(entries):struct.pack_into("<QQ",b,0xa0+16*i,*t)
    struct.pack_into("<II",b,0x200,1,1)
    struct.pack_into("<II",b,0x208,0,0)
    b[0x240]=0
    return b

class DynamicSymbolTests(unittest.TestCase):
    def test_empty_symbol_table(self):
        r=inspect_dynamic_symbols(bytes(fixture()))
        self.assertEqual(r["symbol_count"],1)
        self.assertEqual(r["named_symbol_count"],0)
        self.assertFalse(r["execution_performed"])
    def test_bad_magic(self):
        with self.assertRaises(ValueError):inspect_dynamic_symbols(bytes(0x300))
    def test_invalid_count(self):
        b=fixture()
        struct.pack_into("<II",b,0x200,1,1000)
        with self.assertRaises(ValueError):inspect_dynamic_symbols(bytes(b))
    def test_invalid_string_size(self):
        b=fixture()
        struct.pack_into("<QQ",b,0xa0+3*16,10,0x100000)
        with self.assertRaises(ValueError):inspect_dynamic_symbols(bytes(b))

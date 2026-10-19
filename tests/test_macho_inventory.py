import struct
import unittest
from tools.macho_inventory import inspect_bytes, CPU_ARM64

def macho(cpu=CPU_ARM64, commands=b"", ncmds=0):
    return struct.pack("<IiiIIIII", 0xfeedfacf, cpu, 0, 2, ncmds, len(commands), 0, 0) + commands

class MachOInventoryTests(unittest.TestCase):
    def test_arm64(self):
        report = inspect_bytes(macho())
        self.assertTrue(report["arm64"])
        self.assertFalse(report["instruction_compatibility_proven"])
    def test_non_arm64(self):
        self.assertFalse(inspect_bytes(macho(cpu=0x01000007))["arm64"])
    def test_build_version(self):
        cmd = struct.pack("<IIIIII", 0x32, 24, 2, 0x1a0000, 0x1a0100, 0)
        report = inspect_bytes(macho(commands=cmd, ncmds=1))
        self.assertEqual(report["slices"][0]["platforms"][0]["platform_id"], 2)
    def test_truncated(self):
        with self.assertRaises(ValueError):
            inspect_bytes(b"\xcf\xfa\xed\xfe")
    def test_invalid_commands(self):
        with self.assertRaises(ValueError):
            inspect_bytes(macho(commands=b"\x00"*8, ncmds=1))

import struct
import unittest
from tools.nro_llvm_disasm import make_analysis_elf


class NroLLVMTests(unittest.TestCase):
    def test_elf_machine_and_text(self):
        nro = bytearray(0x100)
        nro[0x10:0x14] = b"NRO0"
        struct.pack_into("<I", nro, 0x18, len(nro))
        struct.pack_into("<II", nro, 0x20, 0x80, 4)
        struct.pack_into("<I", nro, 0x80, 0xd503201f)
        elf = make_analysis_elf(bytes(nro))
        self.assertEqual(elf[:4], b"\x7fELF")
        self.assertEqual(struct.unpack_from("<H", elf, 18)[0], 183)
        self.assertEqual(elf[0x1000:0x1004], bytes(nro[0x80:0x84]))
        shoff = struct.unpack_from("<Q", elf, 40)[0]
        self.assertEqual(struct.unpack_from("<Q", elf, shoff + 64 + 16)[0], 0x80)

    def test_invalid_header(self):
        with self.assertRaises(ValueError):
            make_analysis_elf(bytes(256))

    def test_oob_text(self):
        nro = bytearray(256)
        nro[0x10:0x14] = b"NRO0"
        struct.pack_into("<I", nro, 0x18, len(nro))
        struct.pack_into("<II", nro, 0x20, 0x80, 0x1000)
        with self.assertRaises(ValueError):
            make_analysis_elf(bytes(nro))

import ctypes
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "apps/A17ProMetalProbe/GuestStartup.c"
OK, INVALID = 0, 0xF602

class Entry(ctypes.Structure):
    _fields_ = [("key", ctypes.c_uint32), ("flags", ctypes.c_uint32),
                ("value", ctypes.c_uint64 * 2)]

class Startup(ctypes.Structure):
    _fields_ = [("main_thread_handle", ctypes.c_uint32),
                ("heap_address", ctypes.c_uint64), ("heap_size", ctypes.c_uint64)]

class GuestStartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc = shutil.which("cc")
        if not cc:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        output = pathlib.Path(cls.temp.name) / "libguest.so"
        subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(output)],
                       check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output))
        cls.lib.spk_guest_config_build.argtypes = [
            ctypes.POINTER(Startup), ctypes.POINTER(Entry), ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.spk_guest_config_build.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temp"):
            cls.temp.cleanup()

    def build(self, startup, capacity=4):
        out, count = (Entry * 4)(), ctypes.c_uint32(0xDEAD)
        code = self.lib.spk_guest_config_build(ctypes.byref(startup), out, capacity,
                                               ctypes.byref(count))
        return code, count.value, [(e.key, e.flags, tuple(e.value)) for e in out]

    def test_entry_layout_matches_libnx_config_entry(self):
        self.assertEqual(ctypes.sizeof(Entry), 24)  # 2048 envSetup strides by 0x18

    def test_with_heap_override(self):
        code, count, entries = self.build(Startup(0x1234, 0x8000000, 0x2000000))
        self.assertEqual((code, count), (OK, 3))
        self.assertEqual(entries[:3], [(1, 0, (0x1234, 0)),
                                       (3, 0, (0x8000000, 0x2000000)),
                                       (0, 0, (0, 0))])

    def test_without_heap_override(self):
        code, count, entries = self.build(Startup(7, 0, 0))
        self.assertEqual((code, count), (OK, 2))
        self.assertEqual(entries[:2], [(1, 0, (7, 0)), (0, 0, (0, 0))])

    def test_rejects_missing_main_thread_handle(self):
        self.assertEqual(self.build(Startup(0, 0, 0))[0], INVALID)

    def test_rejects_half_heap_override(self):
        for startup in (Startup(1, 0x8000000, 0), Startup(1, 0, 0x2000000)):
            self.assertEqual(self.build(startup)[0], INVALID)

    def test_small_buffer_reports_needed_size_and_writes_nothing(self):
        code, count, entries = self.build(Startup(1, 0x8000000, 0x2000000), capacity=2)
        self.assertEqual((code, count), (INVALID, 3))
        self.assertEqual(entries, [(0, 0, (0, 0))] * 4)

    def test_null_arguments_rejected(self):
        count = ctypes.c_uint32()
        fn = self.lib.spk_guest_config_build
        self.assertEqual(fn(None, (Entry * 4)(), 4, ctypes.byref(count)), INVALID)
        self.assertEqual(fn(ctypes.byref(Startup(1, 0, 0)), (Entry * 4)(), 4, None), INVALID)
        self.assertEqual(fn(ctypes.byref(Startup(1, 0, 0)), None, 4, ctypes.byref(count)),
                         INVALID)
        self.assertEqual(count.value, 2)

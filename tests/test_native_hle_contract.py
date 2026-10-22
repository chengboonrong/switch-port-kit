import ctypes
import pathlib
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "apps/A17ProMetalProbe/HLEContract.c"

class Reply(ctypes.Structure):
    _fields_ = [("abi_version", ctypes.c_uint32),
                ("result", ctypes.c_uint32),
                ("value", ctypes.c_uint64)]

class HostContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc = shutil.which("cc")
        if not cc:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        output = pathlib.Path(cls.temp.name) / "libhle.so"
        subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(output)],
                       check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output))
        cls.lib.spk_host_dispatch.argtypes = [ctypes.c_uint32, ctypes.c_uint64,
                                                ctypes.POINTER(Reply)]
        cls.lib.spk_host_dispatch.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temp"):
            cls.temp.cleanup()

    def test_ping(self):
        r = Reply()
        code = self.lib.spk_host_dispatch(1, 0x1234, ctypes.byref(r))
        self.assertEqual(code, 0)
        self.assertEqual(r.abi_version, 1)
        self.assertEqual(r.value, 0x1234 ^ 0xA17A17A17A17A17)
    def test_unknown_fails_closed(self):
        r = Reply()
        code = self.lib.spk_host_dispatch(0x52, 123, ctypes.byref(r))
        self.assertEqual(code, 0xF601)
        self.assertEqual(r.value, 0)
    def test_monotonic_clock(self):
        # Bracketing with the same OS clock checks the nanosecond unit and clock.
        first, second = Reply(), Reply()
        before = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
        self.assertEqual(self.lib.spk_host_dispatch(2, 0, ctypes.byref(first)), 0)
        self.assertEqual(self.lib.spk_host_dispatch(2, 0, ctypes.byref(second)), 0)
        after = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
        self.assertEqual((first.abi_version, second.abi_version), (1, 1))
        self.assertGreater(before, 0)
        self.assertLessEqual(before, first.value)
        self.assertLessEqual(first.value, second.value)
        self.assertLessEqual(second.value, after)
    def test_monotonic_clock_rejects_reserved_argument(self):
        r = Reply(value=0xFFFF)
        self.assertEqual(self.lib.spk_host_dispatch(2, 1, ctypes.byref(r)), 0xF602)
        self.assertEqual((r.abi_version, r.result, r.value), (1, 0xF602, 0))

    def test_null_pointer_rejected(self):
        self.assertEqual(self.lib.spk_host_dispatch(1, 1, None), 0xF602)

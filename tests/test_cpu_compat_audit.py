import tempfile
import unittest
from pathlib import Path
from tools.cpu_compat_audit import audit

class CPUAuditTests(unittest.TestCase):
    def test_detects_target_and_assembly(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "project.yml").write_text("OTHER_CFLAGS: -mcpu=apple-a18\n")
            (p / "atomic.S").write_text("casal x0, x1, [x2]\n")
            report = audit(p)
            kinds = {x["category"] for x in report["findings"]}
            self.assertIn("apple_a18_target", kinds)
            self.assertIn("lse_atomic_mnemonic", kinds)
            self.assertFalse(report["instruction_compatibility_proven"])

    def test_ignores_build_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "build").mkdir()
            (p / "build" / "test.S").write_text("casal x0,x1,[x2]\n")
            self.assertEqual(audit(p)["findings"], [])

    def test_does_not_include_source_snippets(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "Makefile").write_text("FLAGS=-mcpu=apple-a18 # private_value\n")
            self.assertNotIn("private_value", str(audit(p)))

    def test_rejects_missing_directory(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                audit(Path(td) / "missing")

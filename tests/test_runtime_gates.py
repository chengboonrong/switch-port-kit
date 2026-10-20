import tempfile
import unittest
from pathlib import Path
from tools.runtime_gates import analyze

class RuntimeGatesTests(unittest.TestCase):
    def test_empty_repo_has_missing_sources(self):
        with tempfile.TemporaryDirectory() as td:
            output = analyze(Path(td))
            self.assertFalse(output["a17pro_compatibility_proven"])
            self.assertTrue(all(x["status"] == "missing_source" for x in output["checks"].values()))

    def test_matches_settings_without_claiming_compatibility(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "dm/ios").mkdir(parents=True)
            (root / "dm/ios/project.yml").write_text('iOS: "26.0"\nOTHER_CFLAGS: -mcpu=apple-a18\nTARGETED_DEVICE_FAMILY: "1,2"')
            output = analyze(root)
            self.assertEqual(output["checks"]["ios26_deployment"]["status"], "found")
            self.assertEqual(output["checks"]["a18_compiler_target"]["status"], "found")
            self.assertFalse(output["a17pro_compatibility_proven"])

if __name__ == "__main__":
    unittest.main()

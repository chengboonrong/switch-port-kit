import tempfile
import unittest
from pathlib import Path
from tools.shinchan_preflight import inspect

class PreflightTests(unittest.TestCase):
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "dm/games").mkdir(parents=True)
            (root / "scripts/build_ipa_from_nsp.py").touch()
            (root / "dm/games/README.md").touch()
            result = inspect(root, root)
            self.assertFalse(result["ready_for_private_survey"])
            self.assertEqual(result["nsp_count"], 0)

    def test_counts_without_reading_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game, upstream = root / "private", root / "nxnative"
            game.mkdir()
            (upstream / "scripts").mkdir(parents=True)
            (upstream / "dm/games").mkdir(parents=True)
            (upstream / "scripts/build_ipa_from_nsp.py").touch()
            (upstream / "dm/games/README.md").touch()
            (game / "test.nsp").write_bytes(b"not a real NSP")
            result = inspect(game, upstream)
            self.assertTrue(result["ready_for_private_survey"])
            self.assertEqual(result["nsp_count"], 1)
            self.assertNotIn("test.nsp", str(result))

    def test_missing_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = inspect(root / "missing", root / "other")
            self.assertFalse(result["ready_for_private_survey"])
            self.assertGreaterEqual(len(result["notes"]), 2)

if __name__ == "__main__":
    unittest.main()

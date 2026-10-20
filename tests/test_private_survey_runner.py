import tempfile
import unittest
from pathlib import Path
from tools.private_survey_runner import plan, validate_log_dir

class PrivateSurveyRunnerTests(unittest.TestCase):
    def test_missing_files_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            self.assertFalse(plan(d, d, d / "missing.keys")["ready"])
    def test_local_presence_is_not_identity_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            upstream, game = d / "nxnative", d / "game"
            (upstream / "scripts").mkdir(parents=True)
            game.mkdir()
            (upstream / "scripts/build_ipa_from_nsp.py").touch()
            (game / "unverified.nsp").touch()
            (d / "private.keys").touch()
            report = plan(upstream, game, d / "private.keys")
            self.assertTrue(report["ready"])
            self.assertFalse(report["executes_game_data"])
            self.assertFalse(report["no_network_enforced"])

if __name__ == "__main__":
    unittest.main()

    def test_log_folder_cannot_be_inside_sources_or_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nxnative, game = root / "nxnative", root / "game"
            nxnative.mkdir()
            game.mkdir()
            with self.assertRaises(ValueError):
                validate_log_dir(nxnative / "logs", nxnative, game)
            with self.assertRaises(ValueError):
                validate_log_dir(game / "logs", nxnative, game)

    def test_separate_log_folder_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = validate_log_dir(root / "private-logs", root / "nxnative", root / "game")
            self.assertEqual(result, root / "private-logs")

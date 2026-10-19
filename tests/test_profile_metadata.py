import unittest
from tools.profile_metadata import validate

GOOD = {
    "title_id": "010015100B514000",
    "graphics": "nvn",
    "module_build_ids": {"main": "a" * 64},
    "evidence": "locally_verified",
}

class ProfileMetadataTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(GOOD), [])
    def test_guessed_evidence_rejected(self):
        self.assertTrue(validate({**GOOD, "evidence": "guessed"}))
    def test_missing_build_ids_rejected(self):
        self.assertTrue(validate({**GOOD, "module_build_ids": {}}))
    def test_secret_fields_rejected(self):
        self.assertTrue(validate({**GOOD, "prod_keys": "secret"}))
    def test_invalid_identity(self):
        self.assertTrue(validate({**GOOD, "title_id": "../../game"}))

if __name__ == "__main__":
    unittest.main()

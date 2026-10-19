import unittest
from tools.survey_sanitizer import sanitize

class SanitizerTests(unittest.TestCase):
    def test_whitelisted_values_only(self):
        raw = "Title ID: 010015100B514000\nGraphics: nvn\nModule count: 4\n/Users/alice/keys/prod.keys\n"
        output = sanitize(raw)
        self.assertEqual(output["title_id"], "010015100b514000")
        self.assertEqual(output["graphics_api"], "nvn")
        self.assertEqual(output["module_count"], 4)
        self.assertNotIn("/Users", str(output))
        self.assertTrue(output["requires_manual_review"])

    def test_untrusted_inline_text_is_discarded(self):
        result = sanitize("Title ID: 010015100B514000 /secret\nGraphics: nvn token=abc\n")
        self.assertNotIn("title_id", result)
        self.assertNotIn("graphics_api", result)

    def test_conflicting_metadata_rejected(self):
        with self.assertRaises(ValueError):
            sanitize("Graphics: nvn\nGraphics: vulkan")

    def test_same_value_repeated_is_allowed(self):
        result = sanitize("Graphics: nvn\\nGraphics: nvn\\n")
        self.assertEqual(result["graphics_api"], "nvn")

    def test_invalid_title_id_is_discarded(self):
        result = sanitize("Title ID: 010015100B514000 /Users/private\\n")
        self.assertNotIn("title_id", result)

    def test_unknown_and_key_lines_discarded(self):
        result = sanitize("prod.keys: sensitive\nNSO main: 123456\nuser: test\n")
        self.assertEqual(set(result), {"schema_version", "source_type", "requires_manual_review"})

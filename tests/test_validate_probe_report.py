import unittest
from tools.validate_probe_report import assess, parse_report

SAMPLE = """SwitchPortKit Metal Capability Report
metal_device: Apple GPU
apple9_family: true
bc_texture_compression: true
BC1_texture_allocation: OK
BC3_texture_allocation: OK
BC7_texture_allocation: OK
command_queue: OK
"""

class ReportTests(unittest.TestCase):
    def test_valid_report(self):
        assessment = assess(parse_report(SAMPLE))
        self.assertTrue(assessment["probe_pass"])
        self.assertFalse(assessment["game_compatibility_proven"])
        self.assertFalse(assessment["rendering_correctness_proven"])

    def test_missing_field(self):
        with self.assertRaisesRegex(ValueError, "Missing required"):
            parse_report(SAMPLE.replace("command_queue: OK\n", ""))

    def test_duplicate_field(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            parse_report(SAMPLE + "command_queue: OK\n")

    def test_failure_report(self):
        fields = parse_report(SAMPLE.replace("BC7_texture_allocation: OK",
                                             "BC7_texture_allocation: FAILED"))
        self.assertFalse(assess(fields)["probe_pass"])

    def test_unknown_fields_are_allowed(self):
        self.assertTrue(assess(parse_report(SAMPLE + "os: iPadOS 26\n"))["probe_pass"])

if __name__ == "__main__":
    unittest.main()

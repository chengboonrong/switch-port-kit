import unittest
from tools.gpu_evidence_gate import classify

class GPUProofTests(unittest.TestCase):
    def test_simulator_never_proves_hardware(self):
        r = classify("execution_environment: simulator\nmetal4_compute: OUTPUT_VERIFIED\nbc_texture_compression: true")
        self.assertFalse(r["metal4_compute_output_verified"])
        self.assertFalse(r["bc_support_reported"])
    def test_real_device_report_is_scoped(self):
        r = classify("execution_environment: physical_device\nmetal4_compute: OUTPUT_VERIFIED\nbc_texture_compression: true")
        self.assertTrue(r["metal4_compute_output_verified"])
        self.assertFalse(r["full_nxnative_compatibility_proven"])
        self.assertFalse(r["shinchan_gameplay_proven"])
    def test_missing_device_marker_fails_closed(self):
        r = classify("metal4_compute: OUTPUT_VERIFIED\\nbc_texture_compression: true")
        self.assertFalse(r["metal4_compute_output_verified"])
        self.assertFalse(r["bc_support_reported"])
    def test_missing_result_fails_closed(self):
        self.assertFalse(classify("")["metal4_compute_output_verified"])
    def test_submitted_is_not_verified(self):
        self.assertFalse(classify("metal4_compute: SUBMITTED")["metal4_compute_output_verified"])

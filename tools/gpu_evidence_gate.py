#!/usr/bin/env python3
"""Classify exported Probe diagnostics without inflating simulator evidence."""
import argparse
import json
from pathlib import Path

def classify(report: str) -> dict:
    fields = {}
    for line in report.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            fields[key.strip()] = value.strip()
    simulator = fields.get("execution_environment") == "simulator"
    physical = fields.get("execution_environment") == "physical_device"
    output = fields.get("metal4_compute") == "OUTPUT_VERIFIED"
    bc = fields.get("bc_texture_compression", "").lower() == "true"
    return {
        "schema_version": 1,
        "simulator": simulator,
        "physical_device_reported": physical,
        "metal4_compute_output_verified": bool(output and physical),
        "bc_support_reported": bool(bc and physical),
        "full_nxnative_compatibility_proven": False,
        "shinchan_gameplay_proven": False,
        "requires_real_device_evidence": True,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    print(json.dumps(classify(args.report.read_text(encoding="utf-8")), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

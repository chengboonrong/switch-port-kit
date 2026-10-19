#!/usr/bin/env python3
"""Validate text diagnostics exported by A17ProMetalProbe (no third-party deps)."""
import argparse
import json
from pathlib import Path

REQUIRED = (
    "metal_device", "apple9_family", "bc_texture_compression",
    "BC1_texture_allocation", "BC3_texture_allocation",
    "BC7_texture_allocation", "command_queue",
)

def parse_report(text: str) -> dict[str, str]:
    fields = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in fields:
            raise ValueError(f"Duplicate report field: {key}")
        fields[key] = value.strip()
    missing = sorted(set(REQUIRED) - fields.keys())
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))
    return fields

def assess(fields: dict[str, str]) -> dict:
    gpu = fields["apple9_family"] == "true"
    bc = fields["bc_texture_compression"] == "true"
    allocations = all(fields[f"{kind}_texture_allocation"] == "OK"
                      for kind in ("BC1", "BC3", "BC7"))
    queue = fields["command_queue"] == "OK"
    return {
        "schema_version": 1,
        "report_type": "allocation_only",
        "apple9_family": gpu,
        "bc_supported": bc,
        "texture_allocations_pass": allocations,
        "command_queue_pass": queue,
        "probe_pass": gpu and bc and allocations and queue,
        "game_compatibility_proven": False,
        "rendering_correctness_proven": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Local text report exported from probe")
    parser.add_argument("--output", type=Path, help="Optional JSON output")
    args = parser.parse_args()
    try:
        assessment = assess(parse_report(args.report.read_text(encoding="utf-8")))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Report validation failed: {exc}\n")
    result = json.dumps(assessment, indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
    return 0 if assessment["probe_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())

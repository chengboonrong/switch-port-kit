#!/usr/bin/env python3
"""Allowlist metadata extraction from local nxnative survey Markdown.

Never share raw surveys. Generated JSON must still be reviewed before publishing.
"""
import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "title_id": re.compile(r"^\s*title[ _-]?id\s*[:=]\s*([0-9a-fA-F]{16})\s*$", re.I),
    "graphics_api": re.compile(r"^\s*graphics(?:[ _-]?api)?\s*[:=]\s*(nvn|vulkan)\s*$", re.I),
    "module_count": re.compile(r"^\s*module[ _-]?count\s*[:=]\s*(\d{1,4})\s*$", re.I),
}
MAX_BYTES = 2 * 1024 * 1024

def sanitize(text: str) -> dict:
    output = {"schema_version": 1, "source_type": "nxnative_survey",
              "requires_manual_review": True}
    for line in text.splitlines():
        for field, pattern in PATTERNS.items():
            match = pattern.fullmatch(line)
            if match is None:
                continue
            value = int(match[1]) if field == "module_count" else match[1].lower()
            if field in output and output[field] != value:
                raise ValueError("conflicting approved field: " + field)
            output[field] = value
    return output

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("survey", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.survey.is_symlink() or not args.survey.is_file():
        parser.error("survey must be a regular, non-symlink file")
    if args.survey.stat().st_size > MAX_BYTES:
        parser.error("survey too large")
    try:
        raw = args.survey.read_text(encoding="utf-8")
        output = json.dumps(sanitize(raw), indent=2) + "\n"
    except (UnicodeError, ValueError) as exc:
        parser.error("invalid input: " + str(exc))
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

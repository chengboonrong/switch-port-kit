#!/usr/bin/env python3
"""Safe, offline readiness check for a local nxnative Shin chan survey.

Does not open NSP/XCI files or key files; executes nothing.
"""
import argparse
import json
from pathlib import Path

IGNORED_NAMES = (".DS_Store",)
SENSITIVE_EXTENSIONS = {".nsp", ".xci", ".nca", ".tik", ".key", ".keys", ".ipa"}

def inspect(root: Path, upstream: Path) -> dict:
    root = root.expanduser().resolve()
    upstream = upstream.expanduser().resolve()
    findings = []
    if not root.is_dir():
        findings.append("game directory does not exist")
    if not (upstream / "scripts" / "build_ipa_from_nsp.py").is_file():
        findings.append("nxnative builder not found")
    if not (upstream / "dm" / "games" / "README.md").is_file():
        findings.append("nxnative game-profile documentation not found")
    count = 0
    if root.is_dir():
        for entry in root.iterdir():
            if entry.is_file() and entry.suffix.lower() == ".nsp":
                count += 1
    if count == 0:
        findings.append("no NSP files detected in game directory")
    return {
        "schema_version": 1,
        "target": "Shin chan: Me and the Professor on Summer Vacation",
        "ready_for_private_survey": not findings,
        "nsp_count": count,
        "notes": findings,
        "privacy": "No NSP content, filenames, key paths or game assets were read or exported.",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--nxnative", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.game_dir, args.nxnative)
    print(json.dumps(result, indent=2))
    return 0 if result["ready_for_private_survey"] else 1

if __name__ == "__main__":
    raise SystemExit(main())

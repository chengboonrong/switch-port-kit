#!/usr/bin/env python3
"""Validate a human-entered, non-copyrighted summary before profile planning.

Never consumes actual game binaries, raw surveys, assets or keys.
"""
import argparse
import json
import re
from pathlib import Path

HEX16 = re.compile(r"^[0-9a-fA-F]{16}$")
HEX32 = re.compile(r"^[0-9a-fA-F]{32,64}$")
FIELDS = {"title_id", "graphics", "module_build_ids", "evidence"}
ALLOWED_GRAPHICS = {"nvn", "vulkan", "unknown"}

def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    unexpected = set(data) - FIELDS
    if unexpected:
        errors.append("unrecognized fields: " + ", ".join(sorted(unexpected)))
    if not HEX16.fullmatch(str(data.get("title_id", ""))):
        errors.append("title_id must contain exactly 16 hexadecimal characters")
    if data.get("graphics") not in ALLOWED_GRAPHICS:
        errors.append("graphics must be nvn, vulkan, or unknown")
    modules = data.get("module_build_ids")
    if not isinstance(modules, dict) or not modules:
        errors.append("module_build_ids must be a nonempty object")
    else:
        for name, build_id in modules.items():
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name):
                errors.append("invalid module name")
            if not isinstance(build_id, str) or not HEX32.fullmatch(build_id):
                errors.append("invalid build ID for module " + str(name))
    if data.get("evidence") != "locally_verified":
        errors.append("evidence must be locally_verified (never guessed)")
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", type=Path)
    args = parser.parse_args()
    data = json.loads(args.metadata.read_text(encoding="utf-8"))
    errors = validate(data)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())

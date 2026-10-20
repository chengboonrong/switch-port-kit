#!/usr/bin/env python3
"""Conservative source-level checklist of nxnative iOS runtime requirements.

Does not infer device compatibility and never runs proprietary game files.
"""
import argparse
import json
import re
from pathlib import Path

CHECKS = {
    "ios26_deployment": ("dm/ios/project.yml", r'iOS:\s*["\x27]?26\.0'),
    "a18_compiler_target": ("dm/ios/project.yml", r"-mcpu=apple-a18\b"),
    "universal_ios_app": ("dm/ios/project.yml", r'TARGETED_DEVICE_FAMILY:\s*["\x27]?1,2'),
    "embedded_game_modules": ("dm/ios/tools/build_ipa.sh", r"gen_embed\.py"),
    "bc_texture_requirement": ("dm/gfx/tex/README.md", r"supportsBCTextureCompression"),
}

def analyze(root: Path) -> dict:
    checks = {}
    for key, (name, pattern) in CHECKS.items():
        file = root / name
        if not file.is_file():
            checks[key] = {"status": "missing_source", "source": name}
            continue
        content = file.read_text(encoding="utf-8", errors="replace")
        checks[key] = {"status": "found" if re.search(pattern, content) else "not_found",
                       "source": name}
    return {"schema_version": 1, "mode": "source_checks_only",
            "a17pro_compatibility_proven": False, "checks": checks}

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--nxnative", required=True, type=Path)
    args = p.parse_args()
    if not args.nxnative.is_dir():
        p.error("nxnative directory missing")
    print(json.dumps(analyze(args.nxnative), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

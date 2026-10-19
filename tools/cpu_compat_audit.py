#!/usr/bin/env python3
"""Read-only AArch64 source risk inventory; NOT a binary compatibility verdict."""
import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "apple_a18_target": re.compile(r"-mcpu\s*=\s*apple-a18\b", re.I),
    "architecture_target": re.compile(r"-(?:mcpu|march)\s*=\s*[\w+.-]+", re.I),
    "lse_atomic_mnemonic": re.compile(r"^\s*(?:cas(?:a|al|l)?|swp(?:a|al|l)?|ldadd(?:a|al|l)?|casp(?:a|al|l)?)\b", re.I),
    "assembly_directive": re.compile(r"^\s*\.(?:arch|cpu)\s+\S+", re.I),
}
EXTS = {".s", ".S", ".asm", ".c", ".h", ".m", ".mm", ".sh", ".yml", ".yaml", ".mk"}

def audit(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("upstream directory does not exist")
    findings = []
    for p in sorted(root.rglob("*")):
        if any(x in {".git", "build", "DerivedData", "node_modules"} for x in p.relative_to(root).parts):
            continue
        if not p.is_file() or (p.suffix not in EXTS and p.name not in {"Makefile", "CMakeLists.txt"}):
            continue
        if p.stat().st_size > 1024 * 1024:
            continue
        for number, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for category, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append({"path": p.relative_to(root).as_posix(), "line": number, "category": category})
    return {"schema_version": 1, "analysis_type": "textual_source_inventory",
            "instruction_compatibility_proven": False,
            "binary_disassembly_performed": False, "findings": findings}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = audit(args.upstream)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    result = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

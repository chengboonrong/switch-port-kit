#!/usr/bin/env python3
"""Opt-in local nxnative survey launcher; never uploads or reads game bytes itself."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

def plan(nxnative: Path, game_dir: Path, keys: Path) -> dict:
    builder = nxnative / "scripts" / "build_ipa_from_nsp.py"
    problems = []
    if not builder.is_file(): problems.append("nxnative builder missing")
    if not game_dir.is_dir(): problems.append("private game directory missing")
    if not keys.is_file(): problems.append("local keys file missing")
    if game_dir.is_dir() and not any(p.is_file() and p.suffix.lower() == ".nsp" for p in game_dir.iterdir()):
        problems.append("no top-level NSP found")
    return {"ready": not problems, "issues": problems,
            "operation": "nxnative --survey-only",
            "executes_game_data": False, "no_network_enforced": False}

def validate_log_dir(log_dir: Path, nxnative: Path, game_dir: Path) -> Path:
    destination = log_dir.expanduser().resolve()
    excluded = [Path(__file__).resolve().parent.parent,
                nxnative.expanduser().resolve(), game_dir.expanduser().resolve()]
    for root in excluded:
        if destination == root or root in destination.parents:
            raise ValueError("logs must be outside project, nxnative and game folders")
    if destination.exists() and not destination.is_dir():
        raise ValueError("log destination must be a directory")
    return destination


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--nxnative", type=Path, required=True)
    p.add_argument("--game-dir", type=Path, required=True)
    p.add_argument("--keys", type=Path, required=True)
    p.add_argument("--run", action="store_true", help="explicitly run local nxnative survey")
    p.add_argument("--log-dir", type=Path, help="private local log directory")
    args = p.parse_args()
    status = plan(args.nxnative, args.game_dir, args.keys)
    if not args.run:
        print(json.dumps(status, indent=2))
        print("DRY RUN ONLY: --run executes upstream code on your local game files.")
        return 0 if status["ready"] else 1
    if not status["ready"]:
        print(json.dumps(status, indent=2))
        return 2
    if args.log_dir is None:
        p.error("--log-dir is required with --run; keep it outside public repositories")
    try:
        log_dir = validate_log_dir(args.log_dir, args.nxnative, args.game_dir)
    except ValueError as exc:
        p.error(str(exc))
    log_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        help_result = subprocess.run(
            [sys.executable, str(args.nxnative / "scripts/build_ipa_from_nsp.py"), "--help"],
            cwd=args.nxnative, capture_output=True, text=True, check=False, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        p.error("could not verify upstream --survey-only support")
    if help_result.returncode != 0 or "--survey-only" not in help_result.stdout:
        p.error("upstream builder does not confirm --survey-only support")
    log = log_dir / "survey-run.log"
    if log.is_symlink():
        p.error("refusing symlink log")
    command = [sys.executable, str(args.nxnative / "scripts/build_ipa_from_nsp.py"),
               str(args.game_dir), "-k", str(args.keys), "--survey-only"]
    # Logs can contain local paths and game-derived material: private only.
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        outcome = subprocess.run(command, cwd=args.nxnative, stdout=stream,
                                 stderr=subprocess.STDOUT, check=False)
    print("Local survey command finished. Review the private log before sharing anything.")
    print("No game data or output has been uploaded by this wrapper.")
    return outcome.returncode

if __name__ == "__main__":
    raise SystemExit(main())

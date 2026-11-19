#!/usr/bin/env python3
"""Revibe local engineering-session bootstrap. Read-only except --check test execution."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ORDER = ("AGENTS.md", "README.md", "Messenger/CONTINUATION.md",
         "Messenger/STATUS.json", "Messenger/README.md", "Messenger/COMPATIBILITY_MATRIX.md")

def git_state():
    def call(*args):
        try:
            r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=10)
            return r.stdout.strip() if r.returncode == 0 else "unavailable"
        except (OSError, subprocess.TimeoutExpired):
            return "unavailable"
    return {"branch": call("branch", "--show-current"),
            "head": call("rev-parse", "--short=12", "HEAD"),
            "working_tree": call("status", "--porcelain") or "clean"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Run the independent offline unit tests")
    args = parser.parse_args()
    print("REVIBE — continuation bootstrap")
    print("Repository: https://github.com/BlazeDevStudio/Revibe")
    print("Git:", json.dumps(git_state()))
    for item in ORDER:
        path = ROOT / item
        print(("FOUND " if path.is_file() else "MISSING ") + item)
        if item == "Messenger/STATUS.json" and path.is_file():
            status = json.loads(path.read_text(encoding="utf-8"))
            for key in ("release_status", "latest_milestone", "next_blocker", "not_verified"):
                print(" ", key, json.dumps(status.get(key)))
    print("Research APK is not a working Messenger release. Do not confuse signing with backend support.")
    if args.check:
        tests = ROOT / "Messenger" / "engineering" / "tests"
        if not tests.is_dir():
            print("Missing tests:", tests)
            return 1
        return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s",
                               str(tests), "-v"], cwd=str(tests.parent), check=False).returncode
    return 0

if __name__ == "__main__":
    sys.exit(main())

"""Repo checks: tests pass, no secrets, machine paths, banned words or project names.

Exit 1 on any failure. Project-name patterns are split so this file itself does
not contain the forbidden words.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv"}
BAD = [
    (re.compile(r"[A-Za-z]:\\\\?Users\\\\?[A-Za-z]", re.I), "Windows home path"),
    (re.compile(r"/home/[a-z]"), "Linux home path"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile("head" + "less", re.I), "banned word"),
]
# Split so this source does not itself contain the forbidden project names.
PROJECT_REFS = [
    (re.compile("r" + "tr", re.I), "forbidden project name"),
    (re.compile("premium" + r"\s+package", re.I), "forbidden project name"),
    (re.compile(r"\bD" + r"an\b"), "forbidden project name"),
]
BAD_EXT = (".step", ".stp", ".f3d", ".sldprt", ".iges", ".igs", ".x_t", ".sat")


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def scan() -> list[str]:
    """Return a list of problem strings for the repository tree."""
    errors: list[str] = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(root, name)
            rel = _rel(path)
            if name.lower().endswith(BAD_EXT):
                errors.append("%s: vendor/CAD file type is not allowed in this public repo" % rel)
                continue
            if name.endswith((".png", ".ico", ".svg")):
                continue
            try:
                text = open(path, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            for rx, what in BAD:
                if rel == "tools/check.py" and what == "banned word":
                    continue
                if rx.search(text):
                    errors.append("%s: %s" % (rel, what))
            for rx, what in PROJECT_REFS:
                if rx.search(text):
                    errors.append("%s: %s" % (rel, what))
    return errors


def main() -> int:
    errors = scan()
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    rc = subprocess.call(
        [sys.executable, "-m", "pytest", "-q", os.path.join(ROOT, "tests")],
        cwd=ROOT,
        env=env,
    )
    if rc:
        errors.append("pytest failed")
    for e in errors:
        print("FAIL", e)
    print("checks: %s" % ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

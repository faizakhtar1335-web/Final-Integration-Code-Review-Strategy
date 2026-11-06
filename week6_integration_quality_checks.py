"""
Week 6 – Final Integration & Code Review Strategy
A small Python utility for repeatable pre-merge quality checks.

What it does:
- Compiles Python source files to detect syntax errors.
- Runs pytest if it is installed.
- Optionally runs Ruff lint checks if Ruff is installed.
- Produces a concise summary and non-zero exit code when a check fails.

Usage:
    python week6_integration_quality_checks.py
    python week6_integration_quality_checks.py --path ./src
    python week6_integration_quality_checks.py --path . --skip-tests

Optional tools:
    python -m pip install pytest ruff

Adapt this utility to your repository and add project-specific checks
(e.g., type checking, security scanning, API contract tests, or build steps).
"""

from __future__ import annotations

import argparse
import compileall
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], label: str, cwd: Path) -> bool:
    """Run a command and return True when it exits successfully."""
    print(f"\\n[CHECK] {label}")
    print("$ " + " ".join(command))
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode == 0:
        print(f"[PASS] {label}")
        return True
    print(f"[FAIL] {label} (exit code {result.returncode})")
    return False


def check_python_syntax(target: Path) -> bool:
    """Compile Python files to detect syntax errors without executing them."""
    print("\\n[CHECK] Python syntax compilation")
    success = compileall.compile_dir(
        str(target),
        quiet=1,
        force=True,
        rx=r"(^|/)(.git|.venv|venv|__pycache__)(/|$)",
    )
    if success:
        print("[PASS] Python syntax compilation")
    else:
        print("[FAIL] Python syntax compilation")
    return success


def main() -> int:
    parser = argparse.ArgumentParser(description="Run basic pre-merge quality checks.")
    parser.add_argument(
        "--path",
        default=".",
        help="Project directory to check (default: current directory).",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest execution.",
    )
    parser.add_argument(
        "--skip-lint",
        action="store_true",
        help="Skip Ruff linting.",
    )
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists() or not target.is_dir():
        print(f"[ERROR] Directory does not exist: {target}", file=sys.stderr)
        return 2

    results: list[tuple[str, bool]] = []

    results.append(("Python syntax", check_python_syntax(target)))

    if not args.skip_tests:
        if shutil.which("pytest"):
            results.append((
                "Automated tests (pytest)",
                run_command(
                    ["pytest", "-q"],
                    "Automated tests (pytest)",
                    target,
                ),
            ))
        else:
            print("\\n[SKIP] pytest is not installed. Install it with: python -m pip install pytest")
            results.append(("Automated tests (pytest)", False))

    if not args.skip_lint:
        if shutil.which("ruff"):
            results.append((
                "Static lint check (Ruff)",
                run_command(
                    ["ruff", "check", "."],
                    "Static lint check (Ruff)",
                    target,
                ),
            ))
        else:
            print("\\n[SKIP] Ruff is not installed. Install it with: python -m pip install ruff")
            results.append(("Static lint check (Ruff)", False))

    print("\\n========== QUALITY CHECK SUMMARY ==========")
    for name, passed in results:
        status = "PASS" if passed else "FAIL / NOT RUN"
        print(f"{status:14} {name}")

    # Missing optional tools are treated as incomplete checks, not hidden successes.
    all_passed = all(passed for _, passed in results)
    if all_passed:
        print("\\nAll configured checks passed.")
        return 0

    print("\\nOne or more checks failed or could not run. Review the output before merging.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

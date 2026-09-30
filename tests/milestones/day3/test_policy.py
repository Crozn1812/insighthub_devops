from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


def _repo_root() -> Path:
    configured = os.environ.get("INSIGHTHUB_REPO_ROOT")
    if configured:
        return Path(configured).resolve()
    return Path(__file__).resolve().parents[3]


def _conftest() -> str:
    configured = os.environ.get("INSIGHTHUB_CONFTEST")
    if configured:
        executable = Path(configured).resolve()
        assert executable.is_file(), f"conftest not found: {executable}"
        return str(executable)
    executable = shutil.which("conftest")
    assert executable is not None, "conftest executable is required"
    return executable


def _run_policy(fixture: str) -> subprocess.CompletedProcess[str]:
    root = _repo_root()
    return subprocess.run(
        [
            _conftest(),
            "test",
            str(root / "infra" / "policies" / "fixtures" / fixture),
            "--policy",
            str(root / "infra" / "policies" / "terraform"),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_policy_allows_valid() -> None:
    result = _run_policy("valid-plan.json")
    assert result.returncode == 0, result.stdout + result.stderr


def test_policy_denies_unsafe() -> None:
    result = _run_policy("unsafe-plan.json")
    output = (result.stdout + result.stderr).lower()
    assert result.returncode != 0, output
    assert "required tags missing" in output
    assert "database encryption required" in output
    assert "public cache network forbidden" in output

"""Generated acceptance coverage for CANARY_VERSION_1_BEHAVIOR_SPECIFICATION."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sixpack import GOVERNANCE_SOURCE_COMMIT, __version__


def _invoke(cwd: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    return subprocess.run(
        [sys.executable, "-m", "sixpack.cli", *args],
        cwd=cwd,
        env=environment,
        capture_output=True,
        check=False,
    )


def test_version_process_contract_without_workspace_or_side_effects(tmp_path: Path) -> None:
    before = list(tmp_path.iterdir())

    result = _invoke(tmp_path, "version")

    assert result.returncode == 0
    assert result.stdout == (
        f"sixpack-runtime {__version__} + governance {GOVERNANCE_SOURCE_COMMIT}\n"
    ).encode()
    assert result.stderr == b""
    assert list(tmp_path.iterdir()) == before


def test_invalid_version_process_invocations_do_not_emit_success(
    tmp_path: Path,
) -> None:
    for args in (("versions",), ("version", "--unknown")):
        result = _invoke(tmp_path, *args)
        assert result.returncode != 0
        assert b"sixpack-runtime" not in result.stdout

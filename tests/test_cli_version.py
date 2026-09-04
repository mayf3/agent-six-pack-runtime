"""Focused unit tests for the version command contract."""

from __future__ import annotations

import pytest

from sixpack import cli


def test_version_uses_runtime_metadata(capsys: pytest.CaptureFixture[str], monkeypatch) -> None:
    monkeypatch.setattr(cli, "__version__", "9.8.7-test")
    monkeypatch.setattr(cli, "GOVERNANCE_SOURCE_COMMIT", "a" * 40)

    assert cli.main(["version"]) == 0

    captured = capsys.readouterr()
    assert captured.out == f"sixpack-runtime 9.8.7-test + governance {'a' * 40}\n"
    assert captured.err == ""


@pytest.mark.parametrize("argv", [["versions"], ["version", "--unknown"]])
def test_invalid_version_invocations_are_parse_failures(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as raised:
        cli.main(argv)

    assert raised.value.code != 0
    captured = capsys.readouterr()
    assert "sixpack-runtime" not in captured.out

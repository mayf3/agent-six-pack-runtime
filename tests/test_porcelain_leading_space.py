"""Regression tests for the porcelain leading-space defect (runtime-qa-porcelain-leading-space-fix).

Defect: ``git()`` stripped the whole status stdout, corrupting the fixed-width
XY prefix of the FIRST porcelain line; ``_working_tree_changes`` then sliced
off the first path character (" M sixpack-artifacts/..." -> "ixpack-artifacts/...")
and the QA allowlist misclassified QA-owned tracked-file edits as product bytes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from sixpack.gitx import git_status_porcelain
from sixpack.runner import FakeAgentAdapter, RoleRunner

AUTHOR = ["-c", "user.email=t@t", "-c", "user.name=t"]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *AUTHOR, *args], cwd=repo, capture_output=True, text=True, check=True)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", ".")
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("print('base')\n")
    art = root / "sixpack-artifacts"
    art.mkdir()
    (art / "qa.automation.json").write_text('{"entrypoints": ["qa_required_checks.sh"]}\n')
    (art / "qa_required_checks.sh").write_text("#!/bin/sh\ntrue\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    return root


@pytest.fixture()
def runner() -> RoleRunner:
    return RoleRunner(None, None, None, {}, FakeAgentAdapter())


def _status_lines(repo: Path) -> list[str]:
    return git_status_porcelain("status", "--porcelain", cwd=repo).splitlines()


def test_seam_preserves_leading_space(repo: Path) -> None:
    """The raw seam must keep the ' M ' prefix intact (defect was stdout.strip())."""
    (repo / "sixpack-artifacts" / "qa.automation.json").write_text("{}\n")
    lines = _status_lines(repo)
    assert lines[0] == " M sixpack-artifacts/qa.automation.json"


def test_t1_first_line_tracked_qa_owned_path_exact(repo: Path, runner: RoleRunner) -> None:
    """T1: tracked QA-owned file as the FIRST porcelain line keeps its full path."""
    (repo / "sixpack-artifacts" / "qa.automation.json").write_text("{}\n")
    assert _status_lines(repo)[0] == " M sixpack-artifacts/qa.automation.json"
    changed = runner._working_tree_changes(repo)
    assert "sixpack-artifacts/qa.automation.json" in changed
    assert "ixpack-artifacts/qa.automation.json" not in changed
    assert changed == ["sixpack-artifacts/qa.automation.json"]


def test_t2_qa_owned_tracked_modifications_allowed(repo: Path, runner: RoleRunner) -> None:
    """T2: legitimate QA-owned tracked modifications classify as allowed."""
    (repo / "sixpack-artifacts" / "qa.automation.json").write_text("{}\n")
    (repo / "sixpack-artifacts" / "qa_required_checks.sh").write_text("#!/bin/sh\ntrue\n# t\n")
    changed = runner._working_tree_changes(repo)
    product_changes = RoleRunner._product_byte_changes(changed, {"sixpack-artifacts/"})
    assert product_changes == []
    assert set(changed) == {
        "sixpack-artifacts/qa.automation.json",
        "sixpack-artifacts/qa_required_checks.sh",
    }


def test_t3_product_mutation_still_rejected(repo: Path, runner: RoleRunner) -> None:
    """T3: a product-path modification is still classified as a product byte."""
    (repo / "src" / "app.py").write_text("print('mutated')\n")
    changed = runner._working_tree_changes(repo)
    assert changed == ["src/app.py"]
    product_changes = RoleRunner._product_byte_changes(changed, {"sixpack-artifacts/"})
    assert product_changes == ["src/app.py"]


def test_t3_mixed_qa_and_product_only_product_rejected(repo: Path, runner: RoleRunner) -> None:
    (repo / "sixpack-artifacts" / "qa.automation.json").write_text("{}\n")
    (repo / "src" / "app.py").write_text("print('mutated')\n")
    changed = runner._working_tree_changes(repo)
    product_changes = RoleRunner._product_byte_changes(changed, {"sixpack-artifacts/"})
    assert product_changes == ["src/app.py"]


def test_t4_untracked_qa_automation_dir_unchanged(repo: Path, runner: RoleRunner) -> None:
    """T4: the historical '?? sixpack-artifacts/' collapsed entry stays allowed."""
    art = repo / "sixpack-artifacts"
    _git(repo, "rm", "-q",
         "sixpack-artifacts/qa.automation.json",
         "sixpack-artifacts/qa_required_checks.sh")
    _git(repo, "commit", "-qm", "remove artifacts")
    art.mkdir(exist_ok=True)
    (art / "qa.automation.json").write_text('{"entrypoints": ["qa_required_checks.sh"]}\n')
    (art / "qa.report.md").write_text("report\n")
    changed = runner._working_tree_changes(repo)
    assert "sixpack-artifacts" in changed
    product_changes = RoleRunner._product_byte_changes(changed, {"sixpack-artifacts/"})
    assert product_changes == []


def test_t5_every_porcelain_entry_full_path(repo: Path, runner: RoleRunner) -> None:
    """T5: first AND subsequent entries keep exact full paths (no first-line special case)."""
    (repo / "sixpack-artifacts" / "qa.automation.json").write_text("{}\n")
    (repo / "src" / "app.py").write_text("print('x')\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "note.md").write_text("new\n")
    _git(repo, "add", "docs/note.md")
    changed = runner._working_tree_changes(repo)
    assert set(changed) == {
        "sixpack-artifacts/qa.automation.json",
        "src/app.py",
        "docs/note.md",
    }
    for path in changed:
        assert not path.startswith(("ixpack-", "rc/app", "ocs/")), path


def test_path_with_spaces_survives(repo: Path, runner: RoleRunner) -> None:
    """Quoted porcelain entries (paths with spaces) still resolve exactly."""
    (repo / "docs with space").mkdir()
    (repo / "docs with space" / "a b.txt").write_text("base\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "spaced path")
    (repo / "docs with space" / "a b.txt").write_text("mutated\n")
    changed = runner._working_tree_changes(repo)
    assert changed == ["docs with space/a b.txt"]


def test_t1_staged_variant_first_line(repo: Path, runner: RoleRunner) -> None:
    """Staged-only modification ('M  path') also keeps its full path."""
    (repo / "sixpack-artifacts" / "qa.automation.json").write_text("{}\n")
    _git(repo, "add", "sixpack-artifacts/qa.automation.json")
    assert _status_lines(repo)[0] == "M  sixpack-artifacts/qa.automation.json"
    changed = runner._working_tree_changes(repo)
    assert changed == ["sixpack-artifacts/qa.automation.json"]

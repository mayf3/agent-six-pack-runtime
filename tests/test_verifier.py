"""Terminal impact-and-coverage verification."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from sixpack.errors import WorkflowStateInvalid
from sixpack.verifier import TerminalVerifier
from tests.conftest import RepoFixture, RuntimeFixture, seed_task


def run_to_terminal(rt: RuntimeFixture, repo: RepoFixture, task_id: str = "task-1") -> None:
    seed_task(rt, repo, task_id)
    rt.controller.admit(task_id)
    instance = rt.ledger.workflow(task_id)
    instance.done_when_met = True  # the task record asserts DONE_WHEN
    rt.ledger.save()
    rt.controller.drive(task_id)
    rt.controller.converge_terminal(task_id)


class TestVerifier:
    def test_completed_task_passes_but_never_claims_merge_ready(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        run_to_terminal(runtime, repo)
        report = TerminalVerifier(runtime.ledger).verify("task-1")
        assert report.verdict == "PASS"
        assert report.state == "AWAITING_INDEPENDENT_REVIEW"
        assert report.review_pending is True
        assert report.merge_ready is False
        assert not report.failures
        assert len(report.receipts) == 6
        assert report.terminal_head

    def test_foreign_commit_breaks_verification(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        run_to_terminal(runtime, repo, "task-1")
        instance = runtime.ledger.workflow("task-1")
        record = runtime.ledger.task("task-1")
        # An unexplained commit lands on top of the terminal candidate.
        head = instance.terminal_head
        subprocess.run(
            ["git", "checkout", "-q", "-B", "sixpack/foreign", head],
            cwd=str(record.repository_path),
            check=True,
        )
        (Path(record.repository_path) / "rogue.txt").write_text("unaudited\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "-A"], cwd=str(record.repository_path), check=True
        )
        subprocess.run(
            ["git", "-c", "user.email=rogue@x", "-c", "user.name=rogue", "commit", "-m", "rogue"],
            cwd=str(record.repository_path),
            check=True,
        )
        rogue_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(record.repository_path),
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        instance.terminal_head = rogue_head
        runtime.ledger.save()
        report = TerminalVerifier(runtime.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any("no stage receipt" in failure for failure in report.failures)

    def test_missing_done_when_fails(self, runtime: RuntimeFixture, repo: RepoFixture) -> None:
        seed_task(runtime, repo)
        runtime.controller.admit("task-1")
        runtime.controller.drive("task-1")
        runtime.controller.converge_terminal("task-1")
        report = TerminalVerifier(runtime.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any("DONE_WHEN" in failure for failure in report.failures)

    def test_receipt_chain_tamper_detected(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        run_to_terminal(runtime, repo, "task-1")
        instance = runtime.ledger.workflow("task-1")
        instance.receipts[0]["checks"] = ["tampered"]  # mutate recorded history
        with pytest.raises(WorkflowStateInvalid):
            runtime.ledger.verify_receipt_chain("task-1")

    def test_coverage_matrix_populated(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        run_to_terminal(runtime, repo, "task-1")
        report = TerminalVerifier(runtime.ledger).verify("task-1")
        # Every touched surface maps to its latest covering receipt.
        assert report.coverage
        for receipt_id in report.coverage.values():
            assert receipt_id.startswith("receipt-task-1-")

"""Terminal false-pass remediation: the final-QA machine gate.

Regression coverage for the independent-review blocker: a QA receipt whose
verdict is FAIL/BLOCKED, whose required checks did not execute, whose
bytes changed after the final run, or whose certified tree is not the
terminal tree must never produce TERMINAL_VERIFY = PASS.
"""

from __future__ import annotations

import pytest

from sixpack.errors import QaVerificationFailed, SelfCertificationRejected
from sixpack.model import WorkflowState
from sixpack.runner import FakeAgentAdapter
from sixpack.verifier import TerminalVerifier
from tests.conftest import make_repo, make_runtime, seed_task


def run_to_qa_failure(tmp_path, adapter) -> tuple[QaVerificationFailed, object]:
    repo = make_repo(tmp_path / "qa-repo")
    rt = make_runtime(tmp_path / "qa-ws", repo, adapter)
    seed_task(rt, repo)
    rt.controller.admit("task-1")
    instance = rt.ledger.workflow("task-1")
    instance.done_when_met = True
    rt.ledger.save()
    with pytest.raises(QaVerificationFailed) as excinfo:
        rt.controller.drive("task-1")
    return excinfo.value, rt


class TestQaVerdictGate:
    def test_qa_verdict_fail_blocks_terminal(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(qa_final_verdict="FAIL")
        error, rt = run_to_qa_failure(tmp_path, adapter)
        assert "FAIL" in str(error)
        instance = rt.ledger.workflow("task-1")
        assert instance.state is WorkflowState.FAILED
        assert instance.terminal_head == ""  # never reaches TERMINAL_BROADCAST
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any("QA_VERDICT" in failure for failure in report.failures)

    def test_qa_verdict_blocked_blocks_terminal(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(
            qa_final_verdict="BLOCKED", qa_blockers=["E2E environment unavailable"]
        )
        error, rt = run_to_qa_failure(tmp_path, adapter)
        assert "BLOCKED" in str(error)
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any("QA_BLOCKERS" in failure for failure in report.failures)

    def test_required_check_not_executed_downgrades_pass(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(
            qa_checks=[{"name": "end-to-end public boundary", "verdict": "NOT_EXECUTED"}]
        )
        _, rt = run_to_qa_failure(tmp_path, adapter)
        instance = rt.ledger.workflow("task-1")
        qa_receipt = [r for r in instance.receipts if r["role"] == "qa"][-1]
        # The stated PASS was invalid (required check not executed) and was
        # mechanically downgraded to BLOCKED.
        assert qa_receipt["results"]["qa_verdict"] == "BLOCKED"
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"

    def test_fake_pass_with_failing_check_downgrades(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(qa_fake_pass_with_failing_checks=True)
        _, rt = run_to_qa_failure(tmp_path, adapter)
        instance = rt.ledger.workflow("task-1")
        qa_receipt = [r for r in instance.receipts if r["role"] == "qa"][-1]
        assert qa_receipt["results"]["qa_verdict"] == "BLOCKED"
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any(
            "QA_BLOCKERS" in failure or "QA_VERDICT" in failure
            for failure in report.failures
        )


class TestCertifiedTreeGate:
    def test_bytes_changed_after_final_run_rejected(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(qa_write_after_final=True)
        repo = make_repo(tmp_path / "wt-repo")
        rt = make_runtime(tmp_path / "wt-ws", repo, adapter)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        with pytest.raises(SelfCertificationRejected) as excinfo:
            rt.controller.drive("task-1")
        assert "certified tree" in str(excinfo.value)
        instance = rt.ledger.workflow("task-1")
        assert instance.terminal_head == ""

    def test_terminal_tree_not_equal_final_qa_bound_tree_fails(
        self, tmp_path, repo
    ) -> None:
        """A receipt whose bound tree was advanced after verification cannot pass."""
        from tests.conftest import seed_task

        rt = make_runtime(tmp_path / "bind-ws", repo)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        instance = rt.ledger.workflow("task-1")
        instance.done_when_met = True
        rt.ledger.save()
        rt.controller.drive("task-1")
        rt.controller.converge_terminal("task-1")
        # Simulate the tree advancing after the final QA bound it (the
        # exact attack the remediation closes).
        instance = rt.ledger.workflow("task-1")
        instance.terminal_tree = "f" * 40
        rt.ledger.save()
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any("QA_RECEIPT_BINDS_TERMINAL_TREE" in failure for failure in report.failures)


class TestFinalQaMachineLine:
    def test_process_adapter_parses_qa_final_json(self, tmp_path) -> None:
        """The generic adapter reads the QA_FINAL_JSON stdout line."""
        from sixpack.model import Role
        from sixpack.runner import ProcessAdapter, StageContext

        script = tmp_path / "fake-qa.sh"
        head = "a" * 40
        tree = "b" * 40
        script.write_text(
            "#!/bin/sh\n"
            "echo 'doing final verification...'\n"
            f"echo 'QA_FINAL_JSON: {{\"qa_verdict\": \"PASS\", \"qa_required_checks\": "
            f"[{{\"name\": \"e2e\", \"verdict\": \"PASS\"}}], \"qa_blockers\": [], "
            f"\"qa_certified_head\": \"{head}\", \"qa_certified_tree\": \"{tree}\"}}'\n",
            encoding="utf-8",
        )
        script.chmod(0o755)
        adapter = ProcessAdapter(command_template=[str(script)])
        context = StageContext(
            task_id="t", repository="r", role=Role.QA,
            worktree_path=tmp_path, base_head="c" * 40, goal="g", instructions="d",
            qa_final_run=True, certified_head=head, certified_tree=tree,
        )
        outcome = adapter.execute_stage(context)
        assert outcome.qa_result is not None
        assert outcome.qa_result["qa_verdict"] == "PASS"

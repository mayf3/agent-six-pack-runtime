"""Terminal false-pass remediation: the final-QA machine gate.

Regression coverage for the independent-review blocker: a QA receipt whose
verdict is FAIL/BLOCKED, whose required checks did not execute, whose
bytes changed after the final run, or whose certified tree is not the
terminal tree must never produce TERMINAL_VERIFY = PASS.
"""

from __future__ import annotations

import subprocess
from unittest.mock import ANY

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


class TestClosedRequiredCheckSet:
    """R1: the canonical QA required-check set is closed (no substitutes)."""

    def test_only_substitute_check_blocked(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(
            qa_checks=[{"name": "foo", "verdict": "PASS"}]
        )
        _, rt = run_to_qa_failure(tmp_path, adapter)
        qa_receipt = [r for r in rt.ledger.workflow("task-1").receipts if r["role"] == "qa"][-1]
        assert qa_receipt["results"]["qa_verdict"] == "BLOCKED"
        assert any("arbitrary substitute" in str(b) for b in qa_receipt["results"]["qa_blockers"])
        assert TerminalVerifier(rt.ledger).verify("task-1").verdict == "FAIL"

    def test_missing_crap_dry_blocked(self, tmp_path) -> None:
        from sixpack.runner import canonical_qa_required_checks

        canonical = canonical_qa_required_checks()
        partial = [
            {"name": name, "verdict": "PASS"}
            for name in canonical
            if "CRAP/DRY" not in name
        ]
        adapter = FakeAgentAdapter(qa_checks=partial)
        _, rt = run_to_qa_failure(tmp_path, adapter)
        qa_receipt = [r for r in rt.ledger.workflow("task-1").receipts if r["role"] == "qa"][-1]
        assert qa_receipt["results"]["qa_verdict"] == "BLOCKED"
        assert any("missing canonical" in str(b) for b in qa_receipt["results"]["qa_blockers"])

    def test_missing_manifest_consistency_blocked(self, tmp_path) -> None:
        from sixpack.runner import canonical_qa_required_checks

        canonical = canonical_qa_required_checks()
        partial = [
            {"name": name, "verdict": "PASS"}
            for name in canonical
            if "manifest consistency" not in name
        ]
        adapter = FakeAgentAdapter(qa_checks=partial)
        _, rt = run_to_qa_failure(tmp_path, adapter)
        qa_receipt = [r for r in rt.ledger.workflow("task-1").receipts if r["role"] == "qa"][-1]
        assert qa_receipt["results"]["qa_verdict"] == "BLOCKED"
        assert any("missing canonical" in str(b) for b in qa_receipt["results"]["qa_blockers"])

    def test_duplicate_check_replacing_another_blocked(self, tmp_path) -> None:
        from sixpack.runner import canonical_qa_required_checks

        canonical = canonical_qa_required_checks()
        duplicated = [
            {"name": canonical[0], "verdict": "PASS"},
            {"name": canonical[0], "verdict": "PASS"},
        ]
        adapter = FakeAgentAdapter(qa_checks=duplicated)
        _, rt = run_to_qa_failure(tmp_path, adapter)
        qa_receipt = [r for r in rt.ledger.workflow("task-1").receipts if r["role"] == "qa"][-1]
        assert qa_receipt["results"]["qa_verdict"] == "BLOCKED"
        assert any(
            "duplicate required check" in str(b) or "missing canonical" in str(b)
            for b in qa_receipt["results"]["qa_blockers"]
        )


class TestQaBlockersSchema:
    """R2: qa_blockers MUST be list[str]; malformed evidence fails closed."""

    @pytest.mark.parametrize(
        "malformed",
        [
            "database unavailable",  # bare string
            {"reason": "database unavailable"},  # dict
            None,  # null
            42,  # number
        ],
    )
    def test_malformed_blockers_fail_closed(self, tmp_path, malformed) -> None:
        adapter = FakeAgentAdapter(qa_blockers_malformed=malformed)
        _, rt = run_to_qa_failure(tmp_path, adapter)
        qa_receipt = [r for r in rt.ledger.workflow("task-1").receipts if r["role"] == "qa"][-1]
        results = qa_receipt["results"]
        assert results["qa_verdict"] == "BLOCKED"
        assert any(
            "qa_blockers must be a list[str]" in str(b) or "missing/null" in str(b)
            for b in results["qa_blockers"]
        )
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"


class TestExecutableQaAutomationGate:
    """R3: report-only QA output cannot start the final QA run."""

    def test_report_only_qa_rejected_before_commit(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(qa_report_only=True)
        repo = make_repo(tmp_path / "ro-repo")
        rt = make_runtime(tmp_path / "ro-ws", repo, adapter)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        with pytest.raises(Exception) as excinfo:
            rt.controller.drive("task-1")
        assert "executable QA automation gate" in str(excinfo.value)
        instance = rt.ledger.workflow("task-1")
        # The QA stage never commits: no terminal, no QA receipt.
        assert instance.terminal_head == ""
        assert not [r for r in instance.receipts if r["role"] == "qa"]
        assert not [r for r in instance.receipts if r["role"] == "qa"]
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"


class TestVerifierDirectFeed:
    """Verifier must catch wrong receipts directly, without runner help."""

    def _run_to_terminal(self, tmp_path):
        from tests.conftest import make_repo, make_runtime, seed_task

        repo = make_repo(tmp_path / "vd-repo")
        rt = make_runtime(tmp_path / "vd-ws", repo)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        instance = rt.ledger.workflow("task-1")
        instance.done_when_met = True
        rt.ledger.save()
        rt.controller.drive("task-1")
        rt.controller.converge_terminal("task-1")
        return rt

    def _mutate_qa_results(self, rt, mutation: dict) -> None:
        instance = rt.ledger.workflow("task-1")
        for receipt in instance.receipts:
            if receipt["role"] == "qa":
                receipt["results"].update(mutation)
        rt.ledger.save()

    def test_fake_pass_with_substitute_only_check_fails_verifier(
        self, tmp_path
    ) -> None:
        rt = self._run_to_terminal(tmp_path)
        # Hand-feed a receipt that claims PASS with a substitute check.
        self._mutate_qa_results(
            rt,
            {
                "qa_verdict": "PASS",
                "qa_required_checks": [{"name": "foo", "verdict": "PASS"}],
            },
        )
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any("canonical" in failure for failure in report.failures)
        assert any(
            "QA_VERDICT" in failure or "substitute" in failure
            for failure in report.failures
        )

    def test_fake_pass_with_string_blockers_fails_verifier(self, tmp_path) -> None:
        rt = self._run_to_terminal(tmp_path)
        self._mutate_qa_results(
            rt,
            {"qa_verdict": "PASS", "qa_blockers": "database unavailable"},
        )
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any(
            "qa_blockers must be a list[str]" in failure for failure in report.failures
        )

    def test_fake_pass_with_null_blockers_fails_verifier(self, tmp_path) -> None:
        rt = self._run_to_terminal(tmp_path)
        self._mutate_qa_results(rt, {"qa_verdict": "PASS", "qa_blockers": None})
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any("missing/null" in failure for failure in report.failures)


class TestAutomationTreeBinding:
    """R: executable automation must bind to the certified Git tree."""

    def test_positive_binding_matches_certified_tree(self, tmp_path) -> None:
        from sixpack.verifier import TerminalVerifier
        from tests.conftest import make_repo, make_runtime, seed_task

        repo = make_repo(tmp_path / "bind-pos-repo")
        rt = make_runtime(tmp_path / "bind-pos-ws", repo)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        instance = rt.ledger.workflow("task-1")
        instance.done_when_met = True
        rt.ledger.save()
        rt.controller.drive("task-1")
        rt.controller.converge_terminal("task-1")
        instance = rt.ledger.workflow("task-1")
        qa_receipt = [r for r in instance.receipts if r["role"] == "qa"][-1]
        bindings = qa_receipt["results"]["qa_automation_bindings"]
        assert bindings == [
            {
                "path": "sixpack-artifacts/qa.verify.sh",
                "blob_sha": ANY,
                "size": ANY,
            }
        ]
        # The bound blob is exactly what the certified tree contains.
        import subprocess

        out = subprocess.run(
            [
                "git", "ls-tree", instance.terminal_tree,
                "--", "sixpack-artifacts/qa.verify.sh",
            ],
            cwd=repo.path, capture_output=True, text=True, check=True,
        ).stdout.strip()
        assert bindings[0]["blob_sha"] in out
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "PASS"
        assert not any("AUTOMATION" in failure for failure in report.failures)

    def test_qa_json_cannot_override_runtime_binding(self, tmp_path) -> None:
        from tests.conftest import make_repo, make_runtime, seed_task

        adapter = FakeAgentAdapter(qa_fake_automation_binding=True)
        repo = make_repo(tmp_path / "ovr-repo")
        rt = make_runtime(tmp_path / "ovr-ws", repo, adapter)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        instance = rt.ledger.workflow("task-1")
        instance.done_when_met = True
        rt.ledger.save()
        # The QA JSON carries a forged binding; the runner must overwrite it.
        rt.controller.drive("task-1")
        rt.controller.converge_terminal("task-1")
        instance = rt.ledger.workflow("task-1")
        qa_receipt = [r for r in instance.receipts if r["role"] == "qa"][-1]
        stored = qa_receipt["results"]["qa_automation_bindings"][0]
        assert stored["blob_sha"] != "f" * 40
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "PASS"

    def test_out_of_bounds_entrypoint_rejected(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(
            qa_automation_entrypoints_override=["../evil.sh"]
        )
        repo = make_repo(tmp_path / "oob-repo")
        rt = make_runtime(tmp_path / "oob-ws", repo, adapter)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        with pytest.raises(Exception) as excinfo:
            rt.controller.drive("task-1")
        assert "escapes sixpack-artifacts" in str(excinfo.value)
        assert rt.ledger.workflow("task-1").terminal_head == ""

    def test_symlink_entrypoint_rejected(self, tmp_path) -> None:
        adapter = FakeAgentAdapter(qa_symlink_automation=True)
        repo = make_repo(tmp_path / "sym-repo")
        rt = make_runtime(tmp_path / "sym-ws", repo, adapter)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        with pytest.raises(Exception) as excinfo:
            rt.controller.drive("task-1")
        assert "symlink" in str(excinfo.value)
        assert rt.ledger.workflow("task-1").terminal_head == ""

    def test_ignored_entrypoint_never_binds_to_tree(self, tmp_path) -> None:
        from sixpack.errors import WorkflowStateInvalid

        adapter = FakeAgentAdapter(qa_ignore_automation=True)
        repo = make_repo(tmp_path / "ign-repo")
        # The repository pre-ignores the automation path (base bytes).
        (repo.path / ".gitignore").write_text(
            "sixpack-artifacts/qa.verify.sh\n", encoding="utf-8"
        )
        subprocess.run(
            ["git", "add", ".gitignore"], cwd=repo.path, check=True
        )
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "ignore"],
            cwd=repo.path, check=True,
        )
        repo.base_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo.path,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        rt = make_runtime(tmp_path / "ign-ws", repo, adapter)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        instance = rt.ledger.workflow("task-1")
        instance.done_when_met = True
        rt.ledger.save()
        with pytest.raises(WorkflowStateInvalid) as excinfo:
            rt.controller.drive("task-1")
        assert "git-ignored" in str(excinfo.value)
        assert rt.ledger.workflow("task-1").terminal_head == ""
        assert not [r for r in rt.ledger.workflow("task-1").receipts if r["role"] == "qa"]
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"

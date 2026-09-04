"""Positive six-stage convergence + profile gate + QA self-certification."""

from __future__ import annotations

import pytest

from sixpack.errors import (
    HostPolicyViolation,
    ProfileGateFailure,
    SelfCertificationRejected,
)
from sixpack.ledger import WorkflowInstance
from sixpack.model import TERMINAL_PRIORITY, Role, WorkflowState
from sixpack.runner import FakeAgentAdapter
from tests.conftest import (
    RepoFixture,
    RuntimeFixture,
    make_runtime,
    make_task_record,
    seed_task,
)


class TestPositiveConvergence:
    def test_h1_through_h6_converges(self, runtime: RuntimeFixture, repo: RepoFixture) -> None:
        seed_task(runtime, repo)
        runtime.controller.admit("task-1")
        runtime.controller.drive("task-1")
        instance = runtime.ledger.workflow("task-1")
        assert instance.state is WorkflowState.TERMINAL_BROADCAST
        assert all(
            instance.stage_status[r.value] == "completed" for r in Role.ordered()
        )
        # Six receipts, chained, all ancestors of the terminal candidate.
        assert len(instance.receipts) == 6
        runtime.ledger.verify_receipt_chain("task-1")
        # Terminal broadcast: exactly the other five roles at priority 00.
        qa_queue = runtime.queues.queue("qa")
        sent_dir = qa_queue.root / "sent"
        terminal_files = list(sent_dir.glob("*.json"))
        assert terminal_files, "terminal handoff must have been sent"
        # Every non-QA station received exactly one terminal copy.
        for role in Role.ordered():
            if role is Role.QA:
                continue
            copies = list((runtime.queues.queue(role.value).root / "inbox/new").glob("*.json"))
            assert len(copies) == 1, role.value
        # Normal handoffs chained H1->...->H6: consecutive candidate heads.
        heads = [entry["output_head"] for entry in instance.receipts]
        assert len(set(heads)) == 6

    def test_convergence_fast_forwards_role_refs(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        seed_task(runtime, repo)
        runtime.controller.admit("task-1")
        runtime.controller.drive("task-1")
        report = runtime.controller.converge_terminal("task-1")
        assert report["state"] == "AWAITING_INDEPENDENT_REVIEW"
        instance = runtime.ledger.workflow("task-1")
        for role in Role.ordered():
            if role is Role.QA:
                continue
            ref = runtime.manager.branch_ref("task-1", role.value)
            assert runtime.manager.head(ref) == instance.terminal_head


class TestProfileGate:
    def test_unauthorized_task_cannot_enter_coder_stage(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        # A task whose PREFLIGHT/profile record is missing.
        record = make_task_record(repo, "task-x", profile_selected=False)
        runtime.ledger.create_task(record)
        runtime.ledger.create_workflow(
            WorkflowInstance(
                task_id="task-x",
                repository="demo-repo",
                workflow_instance_id="wf-task-x",
            )
        )
        runtime.ledger.save()
        with pytest.raises(ProfileGateFailure):
            runtime.runner.execute_stage("task-x", Role.CODER)

    def test_task_without_mandate_refused(self, runtime: RuntimeFixture, repo: RepoFixture) -> None:
        record = make_task_record(repo, "task-y")
        record.preflight.mandate_ref = ""
        runtime.ledger.create_task(record)
        runtime.ledger.save()
        runtime.controller.registry["demo-repo"].write_enabled = True
        with pytest.raises(ProfileGateFailure):
            runtime.controller.admit("task-y")


class TestQaSelfCertification:
    def test_qa_product_fix_rejected(
        self, tmp_path, repo: RepoFixture
    ) -> None:
        adapter = FakeAgentAdapter(qa_product_fix=True)
        rt = make_runtime(tmp_path / "ws2", repo, adapter)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        with pytest.raises(SelfCertificationRejected):
            rt.controller.drive("task-1")
        instance = rt.ledger.workflow("task-1")
        # The pipeline stops: QA cannot certify bytes it just modified.
        assert instance.state is not WorkflowState.TERMINAL_BROADCAST
        assert instance.stage_pointer is Role.QA


class TestSpecGapStop:
    def test_unresolved_spec_gap_blocks_dependent_work(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        seed_task(runtime, repo)
        runtime.controller.admit("task-1")
        instance = runtime.ledger.workflow("task-1")
        instance.unresolved_spec_gap = True
        runtime.ledger.save()
        with pytest.raises(Exception, match="SPEC_GAP"):
            runtime.controller.drive("task-1")


class TestHostAdmission:
    def test_two_active_write_tasks_same_repo_refused(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        seed_task(runtime, repo, "task-1")
        seed_task(runtime, repo, "task-2")
        runtime.controller.admit("task-1")
        with pytest.raises(HostPolicyViolation):
            runtime.controller.admit("task-2")

    def test_unregistered_repo_refused(self, tmp_path, repo: RepoFixture) -> None:
        rt = make_runtime(tmp_path / "ws3", repo)
        record = make_task_record(repo, "task-z")
        record.repository = "unknown-repo"
        rt.ledger.create_task(record)
        rt.ledger.save()
        with pytest.raises(HostPolicyViolation):
            rt.controller.admit("task-z")

    def test_readonly_registration_refuses_admission(self, tmp_path, repo: RepoFixture) -> None:
        rt = make_runtime(tmp_path / "ws4", repo, writable=False)
        seed_task(rt, repo, "task-ro")
        with pytest.raises(HostPolicyViolation):
            rt.controller.admit("task-ro")

    def test_auto_flags_immutable(self) -> None:
        from sixpack.controller import HostConfig

        config = HostConfig(auto_merge=True)
        with pytest.raises(HostPolicyViolation):
            config.validate()


class TestTerminalSpoof:
    def test_non_qa_terminal_broadcast_never_created(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        seed_task(runtime, repo)
        runtime.controller.admit("task-1")
        runtime.controller.drive("task-1")
        instance = runtime.ledger.workflow("task-1")
        terminal_receipts = [r for r in instance.receipts if r["role"] == "qa"]
        assert len(terminal_receipts) == 1
        # The only terminal handoff came from QA with priority 00.
        qa_sent = list((runtime.queues.queue("qa").root / "sent").glob("*.json"))
        assert len(qa_sent) == 1
        payload = qa_sent[0].read_text(encoding="utf-8")
        assert '"priority": "00"' in payload or '"priority":"00"' in payload
        assert TERMINAL_PRIORITY == "00"

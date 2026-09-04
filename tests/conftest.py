"""Shared fixtures: a real git repository plus a fully wired runtime."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from sixpack.audit import AuditGate
from sixpack.controller import HostController, RegistryEntry
from sixpack.gitx import WorktreeManager
from sixpack.ledger import Ledger, PreflightRecord, TaskRecord
from sixpack.model import HandoffEnvelope, Role
from sixpack.queue import QueueStore
from sixpack.runner import AgentAdapter, FakeAgentAdapter, RoleRunner

GOVERNANCE_REVISION = "fcd417ba608bafcc8a1160f3e95f8c43cb2212d8"


def _git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"
    return result.stdout.strip()


@dataclass
class RepoFixture:
    path: Path
    base_head: str


def make_repo(path: Path) -> RepoFixture:
    path.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "main", cwd=path)
    _git("config", "user.email", "forge@example.test", cwd=path)
    _git("config", "user.name", "forge", cwd=path)
    (path / "src").mkdir()
    (path / "src" / "lib.py").write_text("VALUE = 1\n", encoding="utf-8")
    (path / "README.md").write_text("demo\n", encoding="utf-8")
    _git("add", "-A", cwd=path)
    _git("commit", "-m", "initial", cwd=path)
    return RepoFixture(path=path, base_head=_git("rev-parse", "HEAD", cwd=path))


def make_task_record(
    repo: RepoFixture, task_id: str = "task-1", *, profile_selected: bool = True
) -> TaskRecord:
    return TaskRecord(
        task_id=task_id,
        repository="demo-repo",
        repository_path=str(repo.path),
        goal="add one documented behavior",
        done_when="six receipts and a verified terminal candidate",
        task_source="LANE_C/inventory/demo",
        base_head=repo.base_head,
        surfaces=["src/lib.py"],
        affected_contracts=["demo.contract.v1"],
        accepted_authority_revisions=[GOVERNANCE_REVISION],
        preflight=PreflightRecord(
            authority_action="REUSE",
            plan_level="BRIEF",
            assurance_level="DURABLE",
            product_authority_refs=[GOVERNANCE_REVISION],
            mandate_ref="mandate-demo-1",
            delivery_profile="SIX_PACK_V1" if profile_selected else "",
            completed=profile_selected,
        ),
    )


@dataclass
class RuntimeFixture:
    workspace: Path
    ledger: Ledger
    queues: QueueStore
    audit: AuditGate
    runner: RoleRunner
    controller: HostController
    manager: WorktreeManager


def make_runtime(
    workspace: Path,
    repo: RepoFixture,
    adapter: AgentAdapter | None = None,
    *,
    repo_name: str = "demo-repo",
    writable: bool = True,
) -> RuntimeFixture:
    workspace.mkdir(parents=True, exist_ok=True)
    ledger = Ledger(workspace / "state")
    queues = QueueStore(workspace / "state" / "queues")
    audit = AuditGate(workspace / "state" / "audit", queues)
    manager = WorktreeManager(repo.path, workspace / "worktrees")
    runner = RoleRunner(ledger, queues, audit, {repo_name: manager}, adapter or FakeAgentAdapter())
    controller = HostController(workspace, ledger, queues, runner)
    controller.config.window_override = "ACTIVE"  # deterministic tests, any wall clock
    controller.register(
        RegistryEntry(name=repo_name, path=str(repo.path), write_enabled=writable)
    )
    return RuntimeFixture(
        workspace=workspace,
        ledger=ledger,
        queues=queues,
        audit=audit,
        runner=runner,
        controller=controller,
        manager=manager,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> RepoFixture:
    return make_repo(tmp_path / "demo-repo")


@pytest.fixture()
def runtime(tmp_path: Path, repo: RepoFixture) -> RuntimeFixture:
    return make_runtime(tmp_path / "workspace", repo)


def seed_task(
    rt: RuntimeFixture, repo: RepoFixture, task_id: str = "task-1", **kwargs
) -> TaskRecord:
    record = make_task_record(repo, task_id, **kwargs)
    rt.ledger.create_task(record)
    rt.ledger.save()
    return record


def gate_and_deliver(rt: RuntimeFixture, envelope: HandoffEnvelope) -> int:
    """Drive one envelope through the two-call audit gate, then fan out."""
    import contextlib

    from sixpack.errors import AuditRequired

    with contextlib.suppress(AuditRequired):
        rt.audit.submit(envelope)
    assert rt.audit.submit(envelope) == "delivered"
    return rt.queues.deliver(envelope)


def all_roles_done(rt: RuntimeFixture, task_id: str) -> bool:
    instance = rt.ledger.workflow(task_id)
    return all(
        instance.stage_status.get(role.value) == "completed" for role in Role.ordered()
    )

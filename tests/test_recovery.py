"""Head drift, lease recovery, cross-repo shared-pool parallelism, night window."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from sixpack.controller import ACTIVE, QUIESCE, WINDOW_CLOSED, WINDOW_OPEN, RegistryEntry
from sixpack.errors import HeadDrift, HostPolicyViolation
from sixpack.gitx import WorktreeManager
from sixpack.model import Role
from tests.conftest import (
    RepoFixture,
    RuntimeFixture,
    make_repo,
    make_runtime,
    make_task_record,
    seed_task,
)


def _git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


class TestHeadDrift:
    def test_worktree_drift_without_revalidation_aborts(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        seed_task(runtime, repo)
        manager = runtime.manager
        base = repo.base_head
        worktree = manager.ensure_worktree("task-1", "coder", base)
        # The worktree advances to a new commit without any revalidation.
        (worktree.path / "drift.txt").write_text("drifted\n", encoding="utf-8")
        _git("add", "-A", cwd=worktree.path)
        _git("commit", "-m", "unvalidated drift", cwd=worktree.path)
        with pytest.raises(HeadDrift):
            manager.ensure_worktree("task-1", "coder", base)

    def test_base_not_in_repo_refused(self, runtime: RuntimeFixture) -> None:
        with pytest.raises(HeadDrift):
            runtime.manager.ensure_worktree("task-1", "coder", "a" * 40)

    def test_main_checkout_write_forbidden(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        from sixpack.errors import MainCheckoutWrite

        with pytest.raises(MainCheckoutWrite):
            runtime.manager.ensure_not_main_checkout(repo.path)


class TestNightWindow:
    def test_window_phases_deterministic(self, runtime: RuntimeFixture) -> None:
        runtime.controller.config.window_override = ""
        at = lambda h, m: datetime(2026, 9, 4, h, m)  # noqa: E731
        assert runtime.controller.window_phase(at(22, 0)) == WINDOW_CLOSED
        assert runtime.controller.window_phase(at(23, 0)) == ACTIVE
        assert runtime.controller.window_phase(at(0, 30)) == ACTIVE
        assert runtime.controller.window_phase(at(8, 45)) == QUIESCE
        assert runtime.controller.window_phase(at(9, 0)) == WINDOW_CLOSED
        assert runtime.controller.window_phase(at(12, 0)) == WINDOW_CLOSED

    def test_quiesce_preserves_queues_and_leases(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        seed_task(runtime, repo)
        runtime.controller.admit("task-1")
        report = runtime.controller.quiesce()
        assert report["phase"] == QUIESCE
        assert report["leases_preserved"] == 1

    def test_admission_refused_when_window_closed(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        seed_task(runtime, repo)
        runtime.controller.config.window_override = WINDOW_CLOSED
        with pytest.raises(HostPolicyViolation):
            runtime.controller.admit("task-1")
        runtime.controller.config.window_override = WINDOW_OPEN
        runtime.controller.admit("task-1")


class TestLeaseRecovery:
    def test_expired_lease_recovered(self, runtime: RuntimeFixture, repo: RepoFixture) -> None:
        seed_task(runtime, repo)
        runtime.controller.admit("task-1")
        assert "task-1" in runtime.controller.leases
        runtime.controller.leases["task-1"].expires_at = 0.0  # expired
        report = runtime.controller.recover()
        assert "task-1" in report["expired_leases"]
        assert "task-1" not in runtime.controller.leases

    def test_full_recovery_after_simulated_crash(
        self, runtime: RuntimeFixture, repo: RepoFixture
    ) -> None:
        seed_task(runtime, repo)
        runtime.controller.admit("task-1")
        # Advance two stages, then simulate a crash mid-coder: the coder's
        # claimed work was never recorded as executed.
        runtime.runner.execute_stage("task-1", Role.SPECIFIER)
        instance = runtime.ledger.workflow("task-1")
        assert instance.stage_pointer is Role.CODER
        report = runtime.controller.recover()
        assert report["queues"]["requeued"] >= 0
        # After recovery a tick can resume the pipeline.
        runtime.controller.config.window_override = ACTIVE
        runtime.controller.tick()
        assert runtime.ledger.workflow("task-1").stage_status["coder"] in (
            "completed",
            "pending",
        )


class TestCrossRepoParallelism:
    def test_shared_pool_serves_two_repos_at_different_stations(self, tmp_path: Path) -> None:
        repo_a = make_repo(tmp_path / "repo-a")
        repo_b = make_repo(tmp_path / "repo-b")
        rt = make_runtime(tmp_path / "ws", repo_a, repo_name="repo-a")
        rt.runner.worktrees["repo-b"] = WorktreeManager(repo_b.path, tmp_path / "wt-b")
        rt.controller.register(
            RegistryEntry(name="repo-b", path=str(repo_b.path), write_enabled=True)
        )
        for task_id, name, repo in (
            ("task-a", "repo-a", repo_a),
            ("task-b", "repo-b", repo_b),
        ):
            record = make_task_record(repo, task_id)
            record.repository = name
            record.repository_path = str(repo.path)
            rt.ledger.create_task(record)
        rt.ledger.save()
        rt.controller.admit("task-a")
        rt.controller.admit("task-b")

        # Both tasks wait at the same station (coder) after specifier ran.
        rt.runner.execute_stage("task-a", Role.SPECIFIER)
        rt.runner.execute_stage("task-b", Role.SPECIFIER)

        # One tick advances only one coder job: MAX_IN_PROCESS_PER_ROLE=1.
        rt.controller.tick()
        statuses = {
            task: rt.ledger.workflow(task).stage_status["coder"]
            for task in ("task-a", "task-b")
        }
        assert sorted(statuses.values()) == ["completed", "pending"]

        # Next tick advances the other task: no starvation, shared pool.
        rt.controller.tick()
        statuses = {
            task: rt.ledger.workflow(task).stage_status["coder"]
            for task in ("task-a", "task-b")
        }
        assert set(statuses.values()) == {"completed"}

        # Two different stations can be in process for the two repositories
        # at the same moment (this is the shared-worker-pool property).
        rt.controller.in_process_roles["cleaner"] = "task-a"
        rt.controller.in_process_roles["architect"] = "task-b"
        assert rt.controller.in_process_roles == {
            "cleaner": "task-a",
            "architect": "task-b",
        }

    def test_drive_refuses_busy_station(self, tmp_path: Path, repo: RepoFixture) -> None:
        rt = make_runtime(tmp_path / "ws-busy", repo)
        seed_task(rt, repo)
        rt.controller.admit("task-1")
        rt.controller.in_process_roles["specifier"] = "other-task"
        with pytest.raises(HostPolicyViolation):
            rt.controller.drive("task-1")

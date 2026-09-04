"""Deterministic Multi-Repo Host Controller.

The controller is a program, never a seventh reasoning agent. It may scan,
route, lease, wake, reconcile, quiesce, and recover. It must not create
Product Authority, invent product tasks, accept Specs, merge, or deploy.

Host invariants enforced here (Master Goal FIRST REAL DEPLOYMENT SCOPE)::

    MAX_IN_PROCESS_PER_ROLE = 1
    MAX_ACTIVE_WRITE_TASKS_PER_REPO = 1
    AUTO_ACCEPT = AUTO_MERGE = AUTO_DEPLOY = false
    REMOTE_WRITE_DEFAULT = false
    MAIN_CHECKOUT_WRITE = forbidden
    SELF_SELECT_NEW_WORK = forbidden
    BLIND_RETRY = forbidden

Night-window control plane::

    WINDOW_OPEN  freeze registry, fresh-read exact heads, admit legal work
    ACTIVE       handoff completion immediately wakes the next station
    QUIESCE      stop new admission before window close
    WINDOW_CLOSED no new GLM work; queue and leases preserved for next night

Cron/timers only drive this control plane; the six role agents never poll.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .errors import HostPolicyViolation, WorkflowStateInvalid
from .gitx import WorktreeManager
from .ledger import Ledger, WorkflowInstance
from .model import Role, WorkflowState
from .queue import QueueStore
from .runner import RoleRunner

WINDOW_OPEN = "WINDOW_OPEN"
ACTIVE = "ACTIVE"
QUIESCE = "QUIESCE"
WINDOW_CLOSED = "WINDOW_CLOSED"


def _now() -> float:
    return time.time()


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


@dataclass
class RegistryEntry:
    name: str
    path: str
    base_branch: str = "main"
    write_enabled: bool = False
    head: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "path": self.path,
            "base_branch": self.base_branch,
            "write_enabled": self.write_enabled,
            "head": self.head,
        }


@dataclass
class Lease:
    task_id: str
    repository: str
    role: str
    expires_at: float

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "repository": self.repository,
            "role": self.role,
            "expires_at": self.expires_at,
            "expires_at_iso": _iso(self.expires_at),
        }


@dataclass
class HostConfig:
    max_in_process_per_role: int = 1
    max_active_write_tasks_per_repo: int = 1
    auto_accept: bool = False
    auto_merge: bool = False
    auto_deploy: bool = False
    remote_write_default: bool = False
    window_open: str = "23:00"
    window_close: str = "09:00"
    quiesce_minutes: int = 30
    lease_ttl_seconds: int = 1800
    window_override: str = ""  # deterministic control: force a phase (operator/tests)

    def validate(self) -> None:
        if self.max_in_process_per_role != 1:
            raise HostPolicyViolation("MAX_IN_PROCESS_PER_ROLE must be 1 in V0")
        if self.max_active_write_tasks_per_repo != 1:
            raise HostPolicyViolation("MAX_ACTIVE_WRITE_TASKS_PER_REPO must be 1 in V0")
        if self.auto_accept or self.auto_merge or self.auto_deploy:
            raise HostPolicyViolation("AUTO_ACCEPT/AUTO_MERGE/AUTO_DEPLOY must stay false")
        if self.remote_write_default:
            raise HostPolicyViolation("REMOTE_WRITE_DEFAULT must stay false")

    def to_dict(self) -> dict[str, object]:
        return {
            "max_in_process_per_role": self.max_in_process_per_role,
            "max_active_write_tasks_per_repo": self.max_active_write_tasks_per_repo,
            "auto_accept": self.auto_accept,
            "auto_merge": self.auto_merge,
            "auto_deploy": self.auto_deploy,
            "remote_write_default": self.remote_write_default,
            "window_open": self.window_open,
            "window_close": self.window_close,
            "quiesce_minutes": self.quiesce_minutes,
            "lease_ttl_seconds": self.lease_ttl_seconds,
        }


class HostController:
    """Stateful, deterministic controller for one runtime workspace."""

    def __init__(self, root: Path, ledger: Ledger, queues: QueueStore, runner: RoleRunner) -> None:
        self.root = root
        self.ledger = ledger
        self.queues = queues
        self.runner = runner
        self.config = HostConfig()
        self.config.validate()
        self.registry: dict[str, RegistryEntry] = {}
        self.leases: dict[str, Lease] = {}
        self.in_process_roles: dict[str, str] = {}  # role -> task_id
        self.state_path = root / "host_state.json"
        self.registry_path = root / "registry.json"
        self._load()

    # -- persistence -----------------------------------------------------------

    def _load(self) -> None:
        host_json = self.root / "host.json"
        if host_json.exists():
            overrides = json.loads(host_json.read_text(encoding="utf-8"))
            for key, value in overrides.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            self.config.validate()
        if self.state_path.exists():
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            self.leases = {
                key: Lease(
                    task_id=str(raw["task_id"]),
                    repository=str(raw["repository"]),
                    role=str(raw["role"]),
                    expires_at=float(raw["expires_at"]),
                )
                for key, raw in data.get("leases", {}).items()
            }
            self.in_process_roles = dict(data.get("in_process_roles", {}))
        if self.registry_path.exists():
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            self.registry = {
                key: RegistryEntry(
                    name=str(raw["name"]),
                    path=str(raw["path"]),
                    base_branch=str(raw.get("base_branch", "main")),
                    write_enabled=bool(raw.get("write_enabled", False)),
                    head=str(raw.get("head", "")),
                )
                for key, raw in data.get("repositories", {}).items()
            }

    def save(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        payload = {
            "leases": {key: lease.to_dict() for key, lease in self.leases.items()},
            "in_process_roles": self.in_process_roles,
            "saved_at": _iso(_now()),
        }
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, sort_keys=True, indent=1), encoding="utf-8")
        os.replace(tmp, self.state_path)

    def save_registry(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        payload = {"repositories": {key: entry.to_dict() for key, entry in self.registry.items()}}
        tmp = self.registry_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, sort_keys=True, indent=1), encoding="utf-8")
        os.replace(tmp, self.registry_path)

    # -- registry / scan ----------------------------------------------------------

    def _manager_for(self, repo_name: str, repo_path: str) -> WorktreeManager:
        """Reuse the runner's per-repo manager so worktree roots agree."""
        manager = self.runner.worktrees.get(repo_name)
        if manager is None:
            manager = WorktreeManager(
                Path(repo_path), Path(repo_path).parent / "sixpack-worktrees"
            )
            self.runner.worktrees[repo_name] = manager
        return manager

    def register(self, entry: RegistryEntry) -> None:
        manager = self._manager_for(entry.name, entry.path)
        entry.head = manager.head(entry.base_branch)
        self.registry[entry.name] = entry
        self.save_registry()

    def scan(self) -> dict[str, str]:
        """Fresh-read the exact head of every registered repository."""
        heads: dict[str, str] = {}
        for name, entry in self.registry.items():
            manager = self._manager_for(name, entry.path)
            entry.head = manager.head(entry.base_branch)
            heads[name] = entry.head
        self.save_registry()
        return heads

    # -- night window ---------------------------------------------------------------

    def window_phase(self, at: datetime | None = None) -> str:
        """Deterministic WINDOW phase from local clock and config."""
        if self.config.window_override:
            return self.config.window_override
        moment = at or datetime.now().astimezone()
        open_t = _parse_hhmm(self.config.window_open)
        close_t = _parse_hhmm(self.config.window_close)
        minutes = moment.hour * 60 + moment.minute
        open_m = open_t[0] * 60 + open_t[1]
        close_m = close_t[0] * 60 + close_t[1]
        if open_m < close_m:
            in_window = open_m <= minutes < close_m
        else:  # window crosses midnight (e.g. 23:00 -> 09:00)
            in_window = minutes >= open_m or minutes < close_m
        if not in_window:
            return WINDOW_CLOSED
        quiesce_from = close_m - self.config.quiesce_minutes
        if quiesce_from < 0:
            quiesce_from += 24 * 60
        if close_m <= quiesce_from:
            # The quiesce band itself wraps midnight (very short window).
            in_quiesce = minutes >= quiesce_from or minutes < close_m
        else:
            in_quiesce = quiesce_from <= minutes < close_m
        return QUIESCE if in_quiesce else ACTIVE

    # -- admission ---------------------------------------------------------------------

    def admit(self, task_id: str) -> WorkflowInstance:
        """Admit one legally executable task into the shared worker pool."""
        if self.window_phase() in (QUIESCE, WINDOW_CLOSED):
            raise HostPolicyViolation(
                f"admission refused: window phase {self.window_phase()}"
            )
        record = self.ledger.task(task_id)
        # Admission implies candidate work: the profile gate applies first.
        self.ledger.require_stage_admission(task_id, Role.SPECIFIER)
        entry = self.registry.get(record.repository)
        if entry is None:
            raise HostPolicyViolation(f"repository {record.repository} is not registered")
        if not entry.write_enabled:
            raise HostPolicyViolation(
                f"repository {record.repository} is registered read-only; "
                "tasks without mutation authority must not reach the coder stage"
            )
        active_writes = [
            wf.task_id
            for wf in self.ledger.workflows().values()
            if wf.repository == record.repository
            and wf.state in (WorkflowState.ADMITTED, WorkflowState.IN_PROGRESS)
        ]
        if len(active_writes) >= self.config.max_active_write_tasks_per_repo:
            raise HostPolicyViolation(
                f"repository {record.repository} already has an active write task "
                f"({active_writes}); MAX_ACTIVE_WRITE_TASKS_PER_REPO="
                f"{self.config.max_active_write_tasks_per_repo}"
            )
        instance = WorkflowInstance(
            task_id=task_id,
            repository=record.repository,
            workflow_instance_id=f"wf-{task_id}",
        )
        self.ledger.create_workflow(instance)
        self._lease(task_id, record.repository, Role.SPECIFIER.value)
        self.save()
        return instance

    def _lease(self, task_id: str, repository: str, role: str) -> Lease:
        lease = Lease(
            task_id=task_id,
            repository=repository,
            role=role,
            expires_at=_now() + self.config.lease_ttl_seconds,
        )
        self.leases[task_id] = lease
        return lease

    # -- event-driven wake ----------------------------------------------------------------

    def wake_next(self, task_id: str, role: Role) -> dict[str, object] | None:
        """Handoff completion immediately wakes the next station (no cron wait).

        Respects MAX_IN_PROCESS_PER_ROLE=1: when the next station is busy,
        its inbox/new item waits for the next ``tick`` deterministically.
        """
        instance = self.ledger.workflow(task_id)
        if instance.state is WorkflowState.TERMINAL_BROADCAST:
            return None
        nxt = _next_after(role)
        if nxt is None:
            return None
        if nxt.value in self.in_process_roles:
            return None  # station busy; inbox/new holds the work
        self.in_process_roles[nxt.value] = task_id
        try:
            result = self.runner.execute_stage(task_id, nxt)
        finally:
            self.in_process_roles.pop(nxt.value, None)
        self._lease(task_id, instance.repository, nxt.value)
        self.save()
        return result

    def drive(self, task_id: str) -> dict[str, object]:
        """Run the full pipeline for one task until it needs nothing else.

       specifier->...->QA with immediate wake after every handoff.
        """
        instance = self.ledger.workflow(task_id)
        last: dict[str, object] | None = None
        while instance.state is not WorkflowState.TERMINAL_BROADCAST:
            pointer = instance.stage_pointer
            if pointer.value in self.in_process_roles:
                raise HostPolicyViolation(
                    f"station {pointer.value} already in process; refusing concurrent job"
                )
            self.in_process_roles[pointer.value] = task_id
            try:
                last = self.runner.execute_stage(task_id, pointer)
            finally:
                self.in_process_roles.pop(pointer.value, None)
            self._lease(task_id, instance.repository, pointer.value)
            instance = self.ledger.workflow(task_id)
            if instance.state is WorkflowState.TERMINAL_BROADCAST:
                break
        self.save()
        return last or {}

    def tick(self) -> dict[str, object]:
        """Deterministic reconciliation pass (safe to call from cron)."""
        dispatched: list[dict[str, object]] = []
        report: dict[str, object] = {
            "window": self.window_phase(), "dispatched": dispatched, "recovered": {}
        }
        self._reconcile_leases(report)
        # Dispatch queued work to idle stations (wake-up-loss tolerance).
        for role in Role.ordered():
            if role.value in self.in_process_roles:
                continue
            queue = self.queues.queue(role.value)
            candidates: list[str] = []
            for filename in queue.list_new():
                envelope = queue.read_item("inbox/new", filename)
                task_id = envelope.task_id
                instance = self.ledger.workflows().get(task_id)
                # Terminal copies converge, they never dispatch.
                if instance is None or instance.state in (
                    WorkflowState.TERMINAL_BROADCAST, WorkflowState.CONVERGED
                ) or instance.stage_pointer is not role:
                    continue
                candidates.append(task_id)
            # The specifier entry point is admission itself, not a queue
            # item: freshly admitted tasks wait at specifier with an empty
            # inbox.
            if not candidates and role is Role.SPECIFIER:
                candidates = [
                    wf.task_id
                    for wf in self.ledger.workflows().values()
                    if wf.state is WorkflowState.ADMITTED
                    and wf.stage_pointer is Role.SPECIFIER
                ]
            # One dispatch per station per pass: equal-priority stations
            # rotate fairly; a second queued job waits for the next pass.
            if candidates:
                task_id = candidates[0]
                self.in_process_roles[role.value] = task_id
                try:
                    dispatched.append(self.runner.execute_stage(task_id, role))
                finally:
                    self.in_process_roles.pop(role.value, None)
        self.save()
        return report

    # -- converge / quiesce / recover -------------------------------------------------------

    def converge_terminal(self, task_id: str) -> dict[str, object]:
        """Terminal broadcast convergence: merge-only fast-forward of role refs.

        Refuses when a recipient ref diverged (must use correction/replay).
        Records convergence in the ledger; never merges to the base branch.
        """
        instance = self.ledger.workflow(task_id)
        if instance.state is not WorkflowState.TERMINAL_BROADCAST:
            raise WorkflowStateInvalid("task is not in TERMINAL_BROADCAST state")
        record = self.ledger.task(task_id)
        manager = self._manager_for(record.repository, record.repository_path)
        if instance.terminal_head:
            manager.verify_candidate(instance.terminal_head, instance.terminal_tree)
        forwarded: dict[str, bool] = {}
        for role in Role.ordered():
            if role is Role.QA:
                continue
            forwarded[role.value] = manager.fast_forward_ref(
                task_id, role.value, instance.terminal_head
            )
        if not all(forwarded.values()):
            diverged = [role for role, ok in forwarded.items() if not ok]
            raise WorkflowStateInvalid(
                f"terminal convergence refused; diverged role refs {diverged} "
                "require correction/replay, not silent merge"
            )
        # Consume the terminal convergence copies from each recipient queue.
        for role in Role.ordered():
            if role is Role.QA:
                continue
            queue = self.queues.queue(role.value)
            for filename in queue.list_new():
                item = queue.read_item("inbox/new", filename)
                if item.task_id == task_id and item.handoff_type == "terminal":
                    queue.claim_inbound(item.handoff_id)
                    queue.complete_inbound(item.handoff_id)
        instance.state = WorkflowState.CONVERGED
        if record.requires_independent_review:
            instance.state = WorkflowState.AWAITING_INDEPENDENT_REVIEW
        instance.updated_at = _iso(_now())
        self.ledger.save()
        return {"task_id": task_id, "converged": forwarded, "state": instance.state.value}

    def quiesce(self) -> dict[str, object]:
        """Stop taking new work; preserve queues and leases restart-safely."""
        self.save()
        return {
            "phase": QUIESCE,
            "leases_preserved": len(self.leases),
            "queued_items": {
                role: self.queues.queue(role).list_new()
                for role in ("specifier", "coder", "cleaner", "architect", "hardender", "qa")
            },
        }

    def recover(self) -> dict[str, object]:
        """Crash/lease recovery for next-night resume."""
        executed = self.ledger.executed()
        queue_report = self.queues.recover(executed)
        recovered_leases: list[str] = []
        for task_id, lease in list(self.leases.items()):
            if lease.expires_at < _now():
                del self.leases[task_id]
                recovered_leases.append(task_id)
        drift: dict[str, str] = {}
        for name, entry in self.registry.items():
            manager = self._manager_for(name, entry.path)
            current = manager.head(entry.base_branch)
            if entry.head and current != entry.head:
                drift[name] = f"{entry.head[:12]} -> {current[:12]}"
                entry.head = current
        self.save_registry()
        self.save()
        return {
            "queues": queue_report,
            "expired_leases": recovered_leases,
            "registry_head_drift": drift,
            "integrity": "OK",
        }

    def _reconcile_leases(self, report: dict[str, object]) -> None:
        expired = [key for key, lease in self.leases.items() if lease.expires_at < _now()]
        for key in expired:
            del self.leases[key]
        if expired:
            report["expired_leases"] = expired


def _next_after(role: Role) -> Role | None:
    ordered = Role.ordered()
    index = ordered.index(role)
    return ordered[index + 1] if index + 1 < len(ordered) else None


def _parse_hhmm(value: str) -> tuple[int, int]:
    parts = value.split(":")
    return int(parts[0]), int(parts[1])

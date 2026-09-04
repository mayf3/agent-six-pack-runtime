"""Durable workflow ledger: the authoritative machine-readable store.

Forum threads, chat, and dashboards are lossy attention surfaces; this ledger
is the durable state of record for tasks, PREFLIGHT/profile selection, stage
receipts, corrections, terminal convergence, and review state.

Persistence is atomic JSON guarded by an exclusive lock file. Receipts form a
hash chain so any mutation of recorded history is detectable.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from .errors import ProfileGateFailure, WorkflowStateInvalid
from .model import Role, StageReceipt, WorkflowState

LOCK_SUFFIX = ".lock"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class PreflightRecord:
    """Three-axis PREFLIGHT + profile selection (CTR-SIX-002, GOV1 CTR-007)."""

    authority_action: str = ""  # REUSE | AMEND | NEW | SUPERSEDE
    plan_level: str = ""  # NONE | BRIEF | EXEC_PLAN
    assurance_level: str = ""  # ROUTINE | DURABLE | CONTROLLED
    product_authority_refs: list[str] = field(default_factory=list)
    mandate_ref: str = ""
    delivery_profile: str = ""  # must be SIX_PACK_V1
    completed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "authority_action": self.authority_action,
            "plan_level": self.plan_level,
            "assurance_level": self.assurance_level,
            "product_authority_refs": self.product_authority_refs,
            "mandate_ref": self.mandate_ref,
            "delivery_profile": self.delivery_profile,
            "completed": self.completed,
        }


@dataclass
class TaskRecord:
    task_id: str
    repository: str
    repository_path: str
    goal: str
    done_when: str
    task_source: str
    base_head: str
    expansion_trigger: str = ""
    requires_independent_review: bool = True
    surfaces: list[str] = field(default_factory=list)
    affected_contracts: list[str] = field(default_factory=list)
    accepted_authority_revisions: list[str] = field(default_factory=list)
    preflight: PreflightRecord = field(default_factory=PreflightRecord)

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "repository": self.repository,
            "repository_path": self.repository_path,
            "goal": self.goal,
            "done_when": self.done_when,
            "task_source": self.task_source,
            "base_head": self.base_head,
            "expansion_trigger": self.expansion_trigger,
            "requires_independent_review": self.requires_independent_review,
            "surfaces": self.surfaces,
            "affected_contracts": self.affected_contracts,
            "accepted_authority_revisions": self.accepted_authority_revisions,
            "preflight": self.preflight.to_dict(),
        }


@dataclass
class WorkflowInstance:
    task_id: str
    repository: str
    workflow_instance_id: str
    state: WorkflowState = WorkflowState.ADMITTED
    stage_pointer: Role = Role.SPECIFIER
    # role -> pending | in_process | completed
    stage_status: dict[str, str] = field(default_factory=dict)
    candidate_head: str = ""
    candidate_tree: str = ""
    receipts: list[dict[str, object]] = field(default_factory=list)
    receipt_chain_head: str = ""
    corrections: list[dict[str, object]] = field(default_factory=list)
    executed_handoffs: list[str] = field(default_factory=list)
    unresolved_spec_gap: bool = False
    spec_gap_detail: str = ""
    independent_review: dict[str, object] = field(default_factory=dict)
    terminal_head: str = ""
    terminal_tree: str = ""
    done_when_met: bool = False
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "repository": self.repository,
            "workflow_instance_id": self.workflow_instance_id,
            "state": self.state.value,
            "stage_pointer": self.stage_pointer.value,
            "stage_status": self.stage_status,
            "candidate_head": self.candidate_head,
            "candidate_tree": self.candidate_tree,
            "receipts": self.receipts,
            "receipt_chain_head": self.receipt_chain_head,
            "corrections": self.corrections,
            "executed_handoffs": self.executed_handoffs,
            "unresolved_spec_gap": self.unresolved_spec_gap,
            "spec_gap_detail": self.spec_gap_detail,
            "independent_review": self.independent_review,
            "terminal_head": self.terminal_head,
            "terminal_tree": self.terminal_tree,
            "done_when_met": self.done_when_met,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Ledger:
    """Atomic JSON-backed store for tasks and workflow instances."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / "ledger.json"
        self.lock_path = root / ("ledger.json" + LOCK_SUFFIX)
        self._tasks: dict[str, TaskRecord] = {}
        self._workflows: dict[str, WorkflowInstance] = {}
        self._load()

    # -- persistence -----------------------------------------------------------

    def _load(self) -> None:
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        for key, raw in data.get("tasks", {}).items():
            preflight_raw = raw.get("preflight", {})
            self._tasks[key] = TaskRecord(
                task_id=str(raw["task_id"]),
                repository=str(raw["repository"]),
                repository_path=str(raw["repository_path"]),
                goal=str(raw["goal"]),
                done_when=str(raw["done_when"]),
                task_source=str(raw["task_source"]),
                base_head=str(raw["base_head"]),
                expansion_trigger=str(raw.get("expansion_trigger", "")),
                requires_independent_review=bool(raw.get("requires_independent_review", True)),
                surfaces=[str(x) for x in raw.get("surfaces", [])],
                affected_contracts=[str(x) for x in raw.get("affected_contracts", [])],
                accepted_authority_revisions=[
                    str(x) for x in raw.get("accepted_authority_revisions", [])
                ],
                preflight=PreflightRecord(
                    authority_action=str(preflight_raw.get("authority_action", "")),
                    plan_level=str(preflight_raw.get("plan_level", "")),
                    assurance_level=str(preflight_raw.get("assurance_level", "")),
                    product_authority_refs=[
                        str(x) for x in preflight_raw.get("product_authority_refs", [])
                    ],
                    mandate_ref=str(preflight_raw.get("mandate_ref", "")),
                    delivery_profile=str(preflight_raw.get("delivery_profile", "")),
                    completed=bool(preflight_raw.get("completed", False)),
                ),
            )
        for key, raw in data.get("workflows", {}).items():
            self._workflows[key] = WorkflowInstance(
                task_id=str(raw["task_id"]),
                repository=str(raw["repository"]),
                workflow_instance_id=str(raw["workflow_instance_id"]),
                state=WorkflowState(raw["state"]),
                stage_pointer=Role(raw["stage_pointer"]),
                stage_status=dict(cast(dict[str, str], raw.get("stage_status", {}))),
                candidate_head=str(raw.get("candidate_head", "")),
                candidate_tree=str(raw.get("candidate_tree", "")),
                receipts=cast(list[dict[str, object]], raw.get("receipts", [])),
                receipt_chain_head=str(raw.get("receipt_chain_head", "")),
                corrections=cast(list[dict[str, object]], raw.get("corrections", [])),
                executed_handoffs=[str(x) for x in raw.get("executed_handoffs", [])],
                unresolved_spec_gap=bool(raw.get("unresolved_spec_gap", False)),
                spec_gap_detail=str(raw.get("spec_gap_detail", "")),
                independent_review=dict(raw.get("independent_review", {})),
                terminal_head=str(raw.get("terminal_head", "")),
                terminal_tree=str(raw.get("terminal_tree", "")),
                done_when_met=bool(raw.get("done_when_met", False)),
                created_at=str(raw.get("created_at", "")),
                updated_at=str(raw.get("updated_at", "")),
            )

    def save(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        os.close(os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        try:
            payload = {
                "tasks": {key: task.to_dict() for key, task in self._tasks.items()},
                "workflows": {key: wf.to_dict() for key, wf in self._workflows.items()},
            }
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, sort_keys=True, indent=1), encoding="utf-8")
            os.replace(tmp, self.path)
        finally:
            os.unlink(str(self.lock_path))

    # -- access ------------------------------------------------------------------

    def create_task(self, record: TaskRecord) -> None:
        if record.task_id in self._tasks:
            raise WorkflowStateInvalid(f"task {record.task_id} already exists")
        self._tasks[record.task_id] = record

    def task(self, task_id: str) -> TaskRecord:
        if task_id not in self._tasks:
            raise WorkflowStateInvalid(f"unknown task {task_id}")
        return self._tasks[task_id]

    def tasks(self) -> dict[str, TaskRecord]:
        return dict(self._tasks)

    def create_workflow(self, instance: WorkflowInstance) -> None:
        if instance.task_id in self._workflows:
            raise WorkflowStateInvalid(
                f"workflow for task {instance.task_id} already exists"
            )
        for role in Role.ordered():
            instance.stage_status[role.value] = "pending"
        self._workflows[instance.task_id] = instance

    def workflow(self, task_id: str) -> WorkflowInstance:
        if task_id not in self._workflows:
            raise WorkflowStateInvalid(f"no workflow for task {task_id}")
        return self._workflows[task_id]

    def workflows(self) -> dict[str, WorkflowInstance]:
        return dict(self._workflows)

    def executed(self) -> set[str]:
        executed: set[str] = set()
        for instance in self._workflows.values():
            executed.update(instance.executed_handoffs)
        return executed

    # -- profile gate ---------------------------------------------------------------

    def require_stage_admission(self, task_id: str, role: Role) -> TaskRecord:
        """Profile gate before candidate work begins (CTR-SIX-002, ACC-SIX-001).

        A task without completed PREFLIGHT, a resolved authority action, a
        valid mandate reference, and explicit SIX_PACK_V1 selection cannot
        enter any stage — coder included.
        """
        record = self.task(task_id)
        preflight = record.preflight
        if not preflight.completed:
            raise ProfileGateFailure(
                f"task {task_id}: PREFLIGHT not completed; stage {role.value} refused"
            )
        if preflight.authority_action not in ("REUSE", "AMEND", "NEW", "SUPERSEDE"):
            raise ProfileGateFailure(
                f"task {task_id}: authority action unresolved; stage {role.value} refused"
            )
        if not preflight.mandate_ref:
            raise ProfileGateFailure(
                f"task {task_id}: no execution mandate bound; stage {role.value} refused"
            )
        if preflight.delivery_profile != "SIX_PACK_V1":
            raise ProfileGateFailure(
                f"task {task_id}: DELIVERY_PROFILE != SIX_PACK_V1; stage {role.value} refused"
            )
        return record

    # -- receipts ------------------------------------------------------------------

    def append_receipt(self, task_id: str, receipt: StageReceipt) -> None:
        instance = self.workflow(task_id)
        receipt.prev_receipt_hash = instance.receipt_chain_head
        entry = receipt.to_dict()
        entry["receipt_hash"] = receipt.content_hash()
        instance.receipts.append(entry)
        instance.receipt_chain_head = str(entry["receipt_hash"])
        instance.stage_status[receipt.role] = "completed"
        instance.updated_at = _now()

    def verify_receipt_chain(self, task_id: str) -> None:
        """Detect any mutation of recorded stage history."""
        instance = self.workflow(task_id)
        previous = ""
        for entry in instance.receipts:
            stored_hash = str(entry.get("receipt_hash", ""))
            receipt = StageReceipt(
                receipt_id=str(entry["receipt_id"]),
                task_id=str(entry["task_id"]),
                repository=str(entry["repository"]),
                role=str(entry["role"]),
                input_head=str(entry["input_head"]),
                input_tree=str(entry["input_tree"]),
                output_head=str(entry["output_head"]),
                output_tree=str(entry["output_tree"]),
                checks=[str(x) for x in cast(list[object], entry.get("checks", []))],
                artifacts=[str(x) for x in cast(list[object], entry.get("artifacts", []))],
                results=dict(cast(dict[str, object], entry.get("results", {}))),
                limitations=[
                    str(x) for x in cast(list[object], entry.get("limitations", []))
                ],
                surfaces_touched=[
                    str(x) for x in cast(list[object], entry.get("surfaces_touched", []))
                ],
                created_at=str(entry.get("created_at", "")),
                prev_receipt_hash=str(entry.get("prev_receipt_hash", "")),
            )
            recomputed = receipt.content_hash()
            if stored_hash != recomputed:
                raise WorkflowStateInvalid(
                    f"receipt {entry.get('receipt_id')} was mutated after recording"
                )
            if receipt.prev_receipt_hash != previous:
                raise WorkflowStateInvalid(
                    f"receipt chain broken at {receipt.receipt_id}"
                )
            previous = stored_hash
        if previous != instance.receipt_chain_head:
            raise WorkflowStateInvalid("receipt chain head mismatch")

    # -- corrections ---------------------------------------------------------------

    def record_correction(self, task_id: str, correction: dict[str, object]) -> None:
        instance = self.workflow(task_id)
        instance.corrections.append({**correction, "recorded_at": _now()})
        instance.updated_at = _now()

    def replay_to(self, task_id: str, role: Role) -> None:
        """Route a correction to the earliest affected role (CTR-SIX-019).

        Receipts stay immutable; the stage pointer returns to the affected
        role and all downstream stages are marked pending again so replay
        produces replacement coverage.
        """
        instance = self.workflow(task_id)
        instance.stage_pointer = role
        started = False
        for candidate in Role.ordered():
            if candidate is role:
                started = True
            if started:
                instance.stage_status[candidate.value] = "pending"
        if instance.state not in (WorkflowState.FAILED, WorkflowState.IN_PROGRESS):
            instance.state = WorkflowState.IN_PROGRESS
        instance.updated_at = _now()

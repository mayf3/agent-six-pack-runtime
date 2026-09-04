"""Provider-neutral RoleRunner and agent adapters.

The runner owns the mechanical stage protocol so the six professional roles
can be driven by any provider:

- profile/PREFLIGHT gate before any candidate work (CTR-SIX-002);
- an isolated, exact-parent worktree per role (CTR-SIX-003);
- executed-stage evidence and immutable receipts (CTR-SIX-019);
- the normalized semantic envelope and two-call audit gate on every forward,
  correction, and terminal handoff (CTR-SIX-011/013);
- terminal broadcast only from QA, to exactly the other five roles at
  priority 00 (CTR-SIX-015);
- QA may not certify bytes it modified after the final run (CTR-SIX-019).

Adapters:
- ``FakeAgentAdapter``: deterministic in-process adapter for tests/canary;
- ``ProcessAdapter``: generic command-template adapter (any CLI provider).
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, cast

from .audit import AuditGate
from .canonical import canonical_hash
from .errors import (
    AuditRequired,
    CorrectionRequired,
    SelfCertificationRejected,
    WorkflowStateInvalid,
)
from .gitx import WorktreeManager
from .ledger import Ledger, TaskRecord, WorkflowInstance
from .model import (
    TERMINAL_PRIORITY,
    HandoffEnvelope,
    HandoffType,
    Role,
    StageReceipt,
    WorkflowState,
)
from .queue import QueueStore

NORMAL_PRIORITY = "10"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class StageContext:
    task_id: str
    repository: str
    role: Role
    worktree_path: Path
    base_head: str
    goal: str
    instructions: str


@dataclass
class StageOutcome:
    success: bool
    message: str = ""
    checks: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    results: dict[str, object] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    qa_automation_paths: list[str] = field(default_factory=list)


class AgentAdapter(Protocol):
    """Provider-neutral role execution boundary."""

    def execute_stage(self, context: StageContext) -> StageOutcome:
        ...


class FakeAgentAdapter:
    """Deterministic adapter: each role writes its artifact and commits.

    Scripts for tests:
    - ``fail_at``: role names that report failure;
    - ``qa_product_fix``: QA mutates product bytes (self-certification attempt);
    - ``skip_commit``: stage writes nothing (helper refuses empty candidates).
    """

    def __init__(
        self,
        *,
        fail_at: list[str] | None = None,
        qa_product_fix: bool = False,
    ) -> None:
        self.fail_at = fail_at or []
        self.qa_product_fix = qa_product_fix

    def execute_stage(self, context: StageContext) -> StageOutcome:
        if context.role.value in self.fail_at:
            return StageOutcome(success=False, message=f"scripted failure at {context.role.value}")
        qa_paths: list[str] = []
        if context.role is Role.QA:
            qa_dir = context.worktree_path / "qa"
            qa_dir.mkdir(exist_ok=True)
            artifact = qa_dir / f"{context.task_id}.{context.role.value}.md"
            artifact.write_text(
                f"# {context.role.value} artifact\n\n"
                f"task: {context.task_id}\nrole: {context.role.value}\n\n{context.goal}\n",
                encoding="utf-8",
            )
            check = qa_dir / f"{context.task_id}.check.md"
            check.write_text(f"executable QA automation for {context.task_id}\n", encoding="utf-8")
            qa_paths = [
                f"qa/{context.task_id}.{context.role.value}.md",
                f"qa/{context.task_id}.check.md",
            ]
            if self.qa_product_fix:
                src = context.worktree_path / "src" / "feature.txt"
                src.parent.mkdir(exist_ok=True)
                src.write_text("product fix written by QA\n", encoding="utf-8")
        else:
            docs = context.worktree_path / "docs"
            docs.mkdir(exist_ok=True)
            artifact = docs / f"{context.task_id}.{context.role.value}.md"
            artifact.write_text(
                f"# {context.role.value} artifact\n\n"
                f"task: {context.task_id}\nrole: {context.role.value}\n\n{context.goal}\n",
                encoding="utf-8",
            )
        return StageOutcome(
            success=True,
            message=f"{context.role.value} stage complete",
            checks=[f"{context.role.value} local checks"],
            artifacts=[str(artifact.relative_to(context.worktree_path))],
            results={"adapter": "fake"},
            qa_automation_paths=qa_paths,
        )


class ProcessAdapter:
    """Generic subprocess adapter for any provider CLI.

    The command template receives ``{role}``, ``{task_id}``, ``{worktree}``,
    ``{goal}``, and ``{prompt}`` substitutions. ``{prompt}`` carries the
    station briefing built from the vendored role definition (Owns /
    Does Not Own / required checks / done criteria), the goal, and the
    done-when record. Non-zero exit means stage failure.

    Permission note (CTR-SIX-017): any flags in the template must stay
    narrower than the task's Execution Mandate; the profile never grants
    bypass by default.
    """

    def __init__(self, command_template: list[str], timeout_seconds: int = 3600) -> None:
        self.command_template = command_template
        self.timeout_seconds = timeout_seconds

    def _briefing(self, context: StageContext) -> str:
        from .roles import load_role_catalog

        definition = load_role_catalog().definition(context.role)
        owns = "; ".join(definition.owns)
        not_owns = "; ".join(definition.does_not_own)
        checks = "; ".join(definition.required_checks)
        done = "; ".join(definition.done_criteria)
        return (
            "You are the "
            f"{context.role.value} station of a six-stage software delivery "
            "pipeline (specifier -> coder -> cleaner -> architect -> "
            "hardender -> QA). Work ONLY inside the current directory (an "
            "isolated git worktree). Do NOT run git commit or git push; the "
            "delivery helper commits for you. Just create or modify files.\n"
            "MANDATORY: even when you judge that no code change is needed, "
            "you MUST leave your station output on disk: write a stage "
            "report to sixpack-artifacts/"
            f"{context.role.value}.report.md containing what you checked, "
            "what you changed (or why nothing needed changing), and any "
            "limitations. A station with no file changes cannot hand off.\n\n"
            f"TASK_ID: {context.task_id}\n"
            f"GOAL: {context.goal}\n"
            f"DONE_WHEN (task record): {context.instructions}\n\n"
            f"YOUR ROLE OWNS: {owns}\n"
            f"YOUR ROLE DOES NOT OWN (do not do this work): {not_owns}\n"
            f"REQUIRED CHECKS: {checks}\n"
            f"DONE CRITERIA: {done}\n\n"
            "Stay strictly inside your ownership boundary. If required "
            "behavior is not decided by accepted authority, stop and write "
            "the blocker into a file named SPEC_GAP.md instead of inventing "
            "a product contract."
        )

    def execute_stage(self, context: StageContext) -> StageOutcome:
        prompt = self._briefing(context)
        command = [
            part.format(
                role=context.role.value,
                task_id=context.task_id,
                worktree=str(context.worktree_path),
                goal=context.goal,
                prompt=prompt,
            )
            for part in self.command_template
        ]
        try:
            result = subprocess.run(
                command,
                cwd=str(context.worktree_path),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return StageOutcome(
                success=False, message=f"stage timed out after {self.timeout_seconds}s"
            )
        if result.returncode != 0:
            return StageOutcome(
                success=False,
                message=f"provider exited {result.returncode}: {result.stderr[-500:]}",
            )
        return StageOutcome(
            success=True, message="provider stage complete", results={"adapter": "process"}
        )


class RoleRunner:
    """Executes one station of the six-stage pipeline for one task."""

    def __init__(
        self,
        ledger: Ledger,
        queues: QueueStore,
        audit_gate: AuditGate,
        worktrees: dict[str, WorktreeManager],
        adapter: AgentAdapter,
    ) -> None:
        self.ledger = ledger
        self.queues = queues
        self.audit_gate = audit_gate
        self.worktrees = worktrees  # repository name -> manager
        self.default_worktree_root: Path | None = None
        self.adapter = adapter

    # -- helpers -----------------------------------------------------------

    def worktree_manager_for(self, record: TaskRecord) -> WorktreeManager:
        """Per-repository worktree manager, shared with the host controller."""
        manager = self.worktrees.get(record.repository)
        if manager is None:
            root = self.default_worktree_root
            if root is None:
                root = Path(record.repository_path).parent / "sixpack-worktrees"
            manager = WorktreeManager(Path(record.repository_path), root)
            self.worktrees[record.repository] = manager
        return manager

    def _next_role(self, role: Role) -> Role | None:
        ordered = Role.ordered()
        index = ordered.index(role)
        return ordered[index + 1] if index + 1 < len(ordered) else None

    # -- stage execution ------------------------------------------------------

    def execute_stage(self, task_id: str, role: Role) -> dict[str, object]:
        record = self.ledger.require_stage_admission(task_id, role)
        instance = self.ledger.workflow(task_id)
        if instance.stage_pointer is not role:
            raise WorkflowStateInvalid(
                f"stage pointer is {instance.stage_pointer.value}; refusing to run {role.value}"
            )
        if instance.stage_status.get(role.value) not in (None, "pending"):
            raise WorkflowStateInvalid(f"stage {role.value} is not pending")
        if instance.unresolved_spec_gap:
            raise WorkflowStateInvalid(
                f"task {task_id} has an unresolved load-bearing SPEC_GAP; dependent work stopped"
            )

        manager = self.worktree_manager_for(record)
        input_head = record.base_head if instance.candidate_head == "" else instance.candidate_head
        input_tree = manager.tree_of(input_head)
        instance.stage_status[role.value] = "in_process"
        instance.state = WorkflowState.IN_PROGRESS
        self.ledger.save()

        # Claim the inbound station item when the handoff arrived by queue.
        queue = self.queues.queue(role.value)
        inbound_handoff: str | None = None
        for filename in queue.list_new():
            candidate = queue.read_item("inbox/new", filename)
            if candidate.task_id == task_id:
                inbound_handoff = candidate.handoff_id
                queue.claim_inbound(candidate.handoff_id)
                break

        worktree = manager.ensure_worktree(task_id, role.value, input_head)
        context = StageContext(
            task_id=task_id,
            repository=record.repository,
            role=role,
            worktree_path=worktree.path,
            base_head=input_head,
            goal=record.goal,
            instructions=record.done_when,
        )
        outcome = self.adapter.execute_stage(context)
        if not outcome.success:
            instance.stage_status[role.value] = "pending"
            self.ledger.save()
            raise WorkflowStateInvalid(
                f"stage {role.value} failed: {outcome.message}"
            )

        # QA must not mutate product bytes and then certify them (CTR-SIX-019).
        if role is Role.QA:
            allowed = set(outcome.qa_automation_paths)
            changed = self._working_tree_changes(worktree.path)
            product_changes = [
                path
                for path in changed
                if path not in allowed
                and not any(
                    item.startswith(path.rstrip("/") + "/") for item in allowed
                )
            ]
            if product_changes:
                instance.stage_status[role.value] = "pending"
                self.ledger.save()
                raise SelfCertificationRejected(
                    f"QA modified product bytes {product_changes}; correction loop required, "
                    "self-certification forbidden"
                )

        head, tree = manager.commit_all(worktree.path, f"sixpack({role.value}): {task_id}")
        manager.verify_candidate(head, tree)
        surfaces = self._changed_files(worktree.path, input_head)

        receipt = StageReceipt(
            receipt_id=f"receipt-{task_id}-{role.value}-{canonical_hash({'head': head})[:8]}",
            task_id=task_id,
            repository=record.repository,
            role=role.value,
            input_head=input_head,
            input_tree=input_tree,
            output_head=head,
            output_tree=tree,
            checks=outcome.checks,
            artifacts=outcome.artifacts,
            results=outcome.results,
            limitations=outcome.limitations,
            surfaces_touched=surfaces,
            created_at=_now(),
        )
        self.ledger.append_receipt(task_id, receipt)

        envelope = self._build_envelope(record, instance, role, head, tree, receipt)
        self._submit_with_audit(envelope)

        instance = self.ledger.workflow(task_id)
        instance.candidate_head = head
        instance.candidate_tree = tree
        instance.executed_handoffs.append(envelope.handoff_id)
        nxt = self._next_role(role)
        if role is Role.QA:
            instance.state = WorkflowState.TERMINAL_BROADCAST
            instance.terminal_head = head
            instance.terminal_tree = tree
            instance.stage_pointer = Role.QA
        elif nxt is not None:
            instance.stage_pointer = nxt
            instance.stage_status[nxt.value] = "pending"
        if inbound_handoff is not None:
            queue.complete_inbound(inbound_handoff)
        instance.updated_at = _now()
        self.ledger.save()
        return {
            "task_id": task_id,
            "role": role.value,
            "candidate_head": head,
            "candidate_tree": tree,
            "handoff_id": envelope.handoff_id,
            "handoff_type": envelope.handoff_type,
        }

    def _working_tree_changes(self, worktree: Path) -> list[str]:
        """Paths changed in the working tree (staged, unstaged, untracked)."""
        from .gitx import git

        out = git("status", "--porcelain", cwd=worktree, check=False)
        paths: list[str] = []
        for line in out.splitlines():
            if not line.strip():
                continue
            raw = line[3:].strip().strip('"')
            raw = raw.removesuffix("/")
            if raw:
                paths.append(raw)
        return paths[:200]

    def _changed_files(self, worktree: Path, base_head: str) -> list[str]:
        """Paths changed between ``base_head`` and the worktree HEAD."""
        from .gitx import git

        out = git("diff", "--name-only", base_head, "HEAD", cwd=worktree, check=False)
        return [line.strip() for line in out.splitlines() if line.strip()][:200]

    # -- envelope + audit ----------------------------------------------------------

    def _handoff_id(self, task_id: str, role: Role, head: str, handoff_type: HandoffType) -> str:
        digest = canonical_hash({"head": head, "t": _now()})[:12]
        return f"ho-{task_id}-{role.value}-{handoff_type.value}-{digest}"

    def _build_envelope(
        self,
        record: TaskRecord,
        instance: WorkflowInstance,
        role: Role,
        head: str,
        tree: str,
        receipt: StageReceipt,
    ) -> HandoffEnvelope:
        if role is Role.QA:
            to_roles = [r.value for r in Role.ordered() if r is not Role.QA]
            handoff_type = HandoffType.TERMINAL.value
            priority = TERMINAL_PRIORITY
        else:
            nxt = self._next_role(role)
            if nxt is None:  # pragma: no cover - QA handled above
                raise WorkflowStateInvalid("no forward role after QA")
            to_roles = [nxt.value]
            handoff_type = HandoffType.NORMAL.value
            priority = NORMAL_PRIORITY
        return HandoffEnvelope(
            sender=f"sixpack-role-{role.value}",
            task_id=record.task_id,
            repository=record.repository,
            workflow_instance_id=instance.workflow_instance_id,
            from_role=role.value,
            to_roles=to_roles,
            priority=priority,
            handoff_type=handoff_type,
            base_head=record.base_head,
            candidate_head=head,
            candidate_tree=tree,
            accepted_authority_revisions=list(record.accepted_authority_revisions),
            affected_contracts=list(record.affected_contracts),
            artifacts=list(receipt.artifacts),
            executed_stage_evidence={
                "receipt_id": receipt.receipt_id,
                "receipt_hash": receipt.content_hash(),
            },
            handoff_id=self._handoff_id(record.task_id, role, head, HandoffType(handoff_type)),
            created_at=_now(),
        )

    def submit_handoff(self, envelope: HandoffEnvelope) -> str:
        """Two-call audit gate + delivery. Returns 'delivered' or raises AuditRequired."""
        if not self.audit_gate.gate_applies(envelope):
            raise WorkflowStateInvalid("handoff type is not gated")
        try:
            self.audit_gate.submit(envelope)
        except AuditRequired as required:
            # Mandated re-read (CTR-SIX-013): re-read the persisted challenge,
            # re-validate every semantic field, then re-submit unchanged.
            challenge = self.audit_gate.pending_challenge(envelope.task_id, envelope.from_role)
            if challenge is None:
                raise AuditRequired(required.challenge_id) from required
            stored = cast(dict[str, object], challenge["envelope"])
            reread = HandoffEnvelope.from_dict(stored)
            if reread.semantic_hash() != envelope.semantic_hash():
                raise CorrectionRequired(
                    "re-read envelope differs from submission; audit must restart"
                ) from required
            self.audit_gate.submit(envelope)
        self.queues.deliver(envelope)
        return "delivered"

    def _submit_with_audit(self, envelope: HandoffEnvelope) -> str:
        return self.submit_handoff(envelope)

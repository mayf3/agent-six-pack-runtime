"""Core domain model: roles, receive modes, priorities, envelopes, receipts.

Encoding the accepted AGENT_SIX_PACK_DELIVERY_PROFILE_V1 semantics:

- six roles in the fixed order specifier -> coder -> cleaner -> architect
  -> hardender -> QA (DEC-SIX-002);
- receive modes and propagation tokens (DEC-SIX-008);
- one normalized semantic handoff envelope (CTR-SIX-011/CTR-SIX-013);
- immutable stage receipts (CTR-SIX-019).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import cast

from .canonical import require_full_sha
from .errors import EnvelopeInvalid, TerminalBroadcastInvalid

TERMINAL_PRIORITY = "00"


class Role(str, Enum):
    """The six fixed professional stations."""

    SPECIFIER = "specifier"
    CODER = "coder"
    CLEANER = "cleaner"
    ARCHITECT = "architect"
    HARDENDER = "hardender"
    QA = "qa"

    @staticmethod
    def ordered() -> list[Role]:
        """Roles in mandatory forward order."""
        return list(Role)


class ReceiveMode(str, Enum):
    TASK = "task"
    BATCH = "batch"


class Propagation(str, Enum):
    FORWARD_ONLY = "forward-only"
    BACK_ONE = "back-one"
    BACK_ALL = "back-all"


@dataclass(frozen=True)
class ReceivePolicy:
    mode: ReceiveMode
    propagation: Propagation
    terminal_broadcast: bool = False


# DEC-SIX-008 default receive and propagation profile.
ROLE_RECEIVE_POLICY: dict[Role, ReceivePolicy] = {
    Role.SPECIFIER: ReceivePolicy(ReceiveMode.TASK, Propagation.FORWARD_ONLY),
    Role.CODER: ReceivePolicy(ReceiveMode.TASK, Propagation.FORWARD_ONLY),
    Role.CLEANER: ReceivePolicy(ReceiveMode.BATCH, Propagation.BACK_ONE),
    Role.ARCHITECT: ReceivePolicy(ReceiveMode.BATCH, Propagation.BACK_ALL),
    Role.HARDENDER: ReceivePolicy(ReceiveMode.BATCH, Propagation.FORWARD_ONLY),
    Role.QA: ReceivePolicy(ReceiveMode.BATCH, Propagation.BACK_ALL, terminal_broadcast=True),
}


class HandoffType(str, Enum):
    NORMAL = "normal"
    TERMINAL = "terminal"
    CORRECTION = "correction"


class WorkflowState(str, Enum):
    ADMITTED = "ADMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    TERMINAL_BROADCAST = "TERMINAL_BROADCAST"
    CONVERGED = "CONVERGED"
    AWAITING_INDEPENDENT_REVIEW = "AWAITING_INDEPENDENT_REVIEW"
    INDEPENDENT_REVIEW_PASSED = "INDEPENDENT_REVIEW_PASSED"
    FAILED = "FAILED"


class HandoffEnvelope:
    """The normalized semantic handoff envelope.

    ``SEMANTIC_FIELDS`` is the exact field set bound by the two-call audit
    gate (CTR-SIX-013 plus the repository/workflow coordinates required by
    the host goal). Every other field is helper-generated delivery metadata
    and is excluded from the equality check.
    """

    SEMANTIC_FIELDS: tuple[str, ...] = (
        "sender",
        "task_id",
        "repository",
        "workflow_instance_id",
        "from_role",
        "to_roles",
        "priority",
        "handoff_type",
        "base_head",
        "candidate_head",
        "candidate_tree",
        "accepted_authority_revisions",
        "affected_contracts",
        "artifacts",
        "executed_stage_evidence",
    )

    def __init__(
        self,
        *,
        sender: str,
        task_id: str,
        repository: str,
        workflow_instance_id: str,
        from_role: str,
        to_roles: list[str],
        priority: str,
        handoff_type: str,
        base_head: str,
        candidate_head: str,
        candidate_tree: str,
        accepted_authority_revisions: list[str],
        affected_contracts: list[str],
        artifacts: list[str],
        executed_stage_evidence: dict[str, object],
        handoff_id: str,
        created_at: str = "",
        audit_challenge_id: str | None = None,
    ) -> None:
        self.sender = sender
        self.task_id = task_id
        self.repository = repository
        self.workflow_instance_id = workflow_instance_id
        self.from_role = from_role
        self.to_roles = to_roles
        self.priority = priority
        self.handoff_type = handoff_type
        self.base_head = base_head
        self.candidate_head = candidate_head
        self.candidate_tree = candidate_tree
        self.accepted_authority_revisions = accepted_authority_revisions
        self.affected_contracts = affected_contracts
        self.artifacts = artifacts
        self.executed_stage_evidence = executed_stage_evidence
        self.handoff_id = handoff_id
        self.created_at = created_at
        self.audit_challenge_id = audit_challenge_id
        self._validate()

    # -- validation -----------------------------------------------------

    def _validate(self) -> None:
        if not self.sender:
            raise EnvelopeInvalid("sender is required")
        if not self.task_id:
            raise EnvelopeInvalid("task_id is required")
        if not self.repository:
            raise EnvelopeInvalid("repository is required")
        if not self.workflow_instance_id:
            raise EnvelopeInvalid("workflow_instance_id is required")
        try:
            from_role = Role(self.from_role)
        except ValueError as exc:
            raise EnvelopeInvalid(f"unknown from_role: {self.from_role}") from exc
        if not self.to_roles:
            raise EnvelopeInvalid("to_roles must not be empty")
        parsed_recipients: list[Role] = []
        for name in self.to_roles:
            try:
                parsed_recipients.append(Role(name))
            except ValueError as exc:
                raise EnvelopeInvalid(f"unknown to_role: {name}") from exc
        if not self.priority or len(self.priority) != 2 or not self.priority.isdigit():
            raise EnvelopeInvalid(f"priority must be two digits, got: {self.priority!r}")
        try:
            handoff_type = HandoffType(self.handoff_type)
        except ValueError as exc:
            raise EnvelopeInvalid(f"unknown handoff_type: {self.handoff_type}") from exc
        try:
            require_full_sha(self.base_head, "base_head")
            require_full_sha(self.candidate_head, "candidate_head")
            require_full_sha(self.candidate_tree, "candidate_tree")
        except ValueError as exc:
            raise EnvelopeInvalid(str(exc)) from exc
        if not isinstance(self.accepted_authority_revisions, list) or (
            not self.accepted_authority_revisions
        ):
            raise EnvelopeInvalid("accepted_authority_revisions must be a non-empty list")
        if not isinstance(self.affected_contracts, list):
            raise EnvelopeInvalid("affected_contracts must be a list")
        if not isinstance(self.artifacts, list):
            raise EnvelopeInvalid("artifacts must be a list")
        if not isinstance(self.executed_stage_evidence, dict):
            raise EnvelopeInvalid("executed_stage_evidence must be an object")
        self._validate_topology(from_role, parsed_recipients, handoff_type)

    def _validate_topology(
        self, from_role: Role, recipients: list[Role], handoff_type: HandoffType
    ) -> None:
        ordered = Role.ordered()
        from_index = ordered.index(from_role)
        if handoff_type is HandoffType.TERMINAL:
            if from_role is not Role.QA:
                raise TerminalBroadcastInvalid("only QA may broadcast terminal completion")
            expected = [r for r in ordered if r is not Role.QA]
            if sorted(self.to_roles) != sorted(r.value for r in expected):
                raise TerminalBroadcastInvalid(
                    "terminal broadcast must target exactly the other five roles"
                )
            if len(recipients) != len(set(self.to_roles)):
                raise TerminalBroadcastInvalid("terminal broadcast contains duplicate recipients")
            if self.priority != TERMINAL_PRIORITY:
                raise TerminalBroadcastInvalid(
                    f"terminal priority must be {TERMINAL_PRIORITY}, got {self.priority}"
                )
            return
        if len(recipients) != 1:
            raise EnvelopeInvalid("normal/correction handoff must have exactly one recipient")
        target = recipients[0]
        if handoff_type is HandoffType.NORMAL:
            if ordered.index(target) != from_index + 1:
                raise EnvelopeInvalid(
                    f"normal forward must target the next role, "
                    f"got {from_role.value}->{target.value}"
                )
            if self.priority == TERMINAL_PRIORITY:
                raise EnvelopeInvalid("priority 00 is reserved for terminal broadcast")
        else:  # CORRECTION
            if ordered.index(target) >= from_index + 1 and target is not from_role:
                raise EnvelopeInvalid(
                    "correction must route backward (or self) to the earliest affected role"
                )

    # -- canonical semantics ---------------------------------------------

    def semantic_dict(self) -> dict[str, object]:
        """The semantic field set bound by the audit challenge."""
        return {name: getattr(self, name) for name in self.SEMANTIC_FIELDS}

    def semantic_hash(self) -> str:
        from .canonical import canonical_hash

        return canonical_hash(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {
            "handoff_id": self.handoff_id,
            "created_at": self.created_at,
            "audit_challenge_id": self.audit_challenge_id,
            **self.semantic_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> HandoffEnvelope:
        def text(key: str) -> str:
            return str(data[key])

        def str_list(key: str) -> list[str]:
            return [str(item) for item in cast(list[object], data[key])]

        return cls(
            handoff_id=text("handoff_id"),
            created_at=str(data.get("created_at", "")),
            audit_challenge_id=cast("str | None", data.get("audit_challenge_id")),
            sender=text("sender"),
            task_id=text("task_id"),
            repository=text("repository"),
            workflow_instance_id=text("workflow_instance_id"),
            from_role=text("from_role"),
            to_roles=str_list("to_roles"),
            priority=text("priority"),
            handoff_type=text("handoff_type"),
            base_head=text("base_head"),
            candidate_head=text("candidate_head"),
            candidate_tree=text("candidate_tree"),
            accepted_authority_revisions=str_list("accepted_authority_revisions"),
            affected_contracts=str_list("affected_contracts"),
            artifacts=str_list("artifacts"),
            executed_stage_evidence=cast(dict[str, object], data["executed_stage_evidence"]),
        )


@dataclass
class StageReceipt:
    """Immutable historical record of one completed stage (CTR-SIX-019).

    Proves the role completed its responsibility on the recorded output;
    never a blanket conformance claim over later descendants.
    """

    receipt_id: str
    task_id: str
    repository: str
    role: str
    input_head: str
    input_tree: str
    output_head: str
    output_tree: str
    checks: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    results: dict[str, object] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    surfaces_touched: list[str] = field(default_factory=list)
    created_at: str = ""
    prev_receipt_hash: str = ""

    def __post_init__(self) -> None:
        require_full_sha(self.input_head, "input_head")
        require_full_sha(self.input_tree, "input_tree")
        require_full_sha(self.output_head, "output_head")
        require_full_sha(self.output_tree, "output_tree")

    def content_hash(self) -> str:
        from .canonical import canonical_hash

        return canonical_hash(
            {
                "receipt_id": self.receipt_id,
                "task_id": self.task_id,
                "repository": self.repository,
                "role": self.role,
                "input_head": self.input_head,
                "input_tree": self.input_tree,
                "output_head": self.output_head,
                "output_tree": self.output_tree,
                "checks": self.checks,
                "artifacts": self.artifacts,
                "results": self.results,
                "limitations": self.limitations,
                "surfaces_touched": self.surfaces_touched,
                "created_at": self.created_at,
                "prev_receipt_hash": self.prev_receipt_hash,
            }
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "task_id": self.task_id,
            "repository": self.repository,
            "role": self.role,
            "input_head": self.input_head,
            "input_tree": self.input_tree,
            "output_head": self.output_head,
            "output_tree": self.output_tree,
            "checks": self.checks,
            "artifacts": self.artifacts,
            "results": self.results,
            "limitations": self.limitations,
            "surfaces_touched": self.surfaces_touched,
            "created_at": self.created_at,
            "prev_receipt_hash": self.prev_receipt_hash,
            "receipt_hash": self.content_hash(),
        }

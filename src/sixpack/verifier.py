"""Terminal impact-and-coverage verification (CTR-SIX-020).

Completion of the six-pack lane requires:

- six stage-local receipts proving traversal;
- an exact terminal candidate Head/tree that exists in the repository;
- candidate ancestry explained entirely by recorded stage receipts (any
  foreign commit makes the run fail — no stale-receipt false pass);
- the final QA receipt bound to the unchanged terminal candidate;
- a terminal impact-and-coverage matrix mapping every affected surface to
  its most recent applicable receipt;
- no unresolved load-bearing SPEC_GAP and a satisfied DONE_WHEN.

Verification never claims merge-ready: tasks requiring independent review
stop in ``AWAITING_INDEPENDENT_REVIEW`` until a fresh independent reviewer
(and the Owner) act.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from .gitx import WorktreeManager
from .gitx import git as _git
from .ledger import Ledger
from .model import Role, WorkflowState
from .qa_gate import automation_tree_binding_failures, qa_pass_eligibility_failures


@dataclass
class VerifyReport:
    task_id: str
    verdict: str  # PASS | FAIL
    state: str
    merge_ready: bool
    review_pending: bool = False
    failures: list[str] = field(default_factory=list)
    coverage: dict[str, str] = field(default_factory=dict)  # surface -> latest receipt id
    receipts: list[str] = field(default_factory=list)
    terminal_head: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "verdict": self.verdict,
            "state": self.state,
            "merge_ready": self.merge_ready,
            "review_pending": self.review_pending,
            "failures": self.failures,
            "coverage": self.coverage,
            "receipts": self.receipts,
            "terminal_head": self.terminal_head,
        }


class TerminalVerifier:
    """Mechanical completion verifier for one six-pack task."""

    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger

    def verify(self, task_id: str) -> VerifyReport:
        record = self.ledger.task(task_id)
        instance = self.ledger.workflow(task_id)
        failures: list[str] = []

        receipts_by_role: dict[str, dict[str, object]] = {}
        for entry in instance.receipts:
            receipts_by_role[str(entry["role"])] = entry  # latest wins
        for role in Role.ordered():
            if role.value not in receipts_by_role:
                failures.append(f"missing stage receipt for {role.value}")
        report_receipts = [str(entry.get("receipt_id")) for entry in instance.receipts]

        manager = WorktreeManager(
            Path(record.repository_path),
            Path(record.repository_path).parent / "sixpack-worktrees",
        )

        terminal_head = instance.terminal_head or instance.candidate_head
        terminal_tree = instance.terminal_tree or instance.candidate_tree
        if terminal_head:
            try:
                manager.verify_candidate(terminal_head, terminal_tree)
            except Exception as exc:
                failures.append(f"terminal candidate verification failed: {exc}")

        # Candidate ancestry must be exactly the recorded stage outputs.
        if terminal_head and len(receipts_by_role) == len(Role.ordered()):
            recorded_heads = {str(entry["output_head"]) for entry in instance.receipts}
            try:
                commits = _git(
                    "log", "--format=%H", f"{record.base_head}..{terminal_head}",
                    cwd=Path(record.repository_path),
                ).split()
                foreign = [c for c in commits if c not in recorded_heads]
                if foreign:
                    failures.append(
                        f"candidate ancestry contains {len(foreign)} commit(s) with no stage "
                        f"receipt (stale/foreign mutation): {foreign[:3]}"
                    )
                for role_name, entry in receipts_by_role.items():
                    head = str(entry["output_head"])
                    if head != terminal_head and not manager.is_ancestor(head, terminal_head):
                        failures.append(
                            f"{role_name} receipt output is not an ancestor of the terminal "
                            "candidate; its coverage is stale"
                        )
            except Exception as exc:
                failures.append(f"ancestry check failed: {exc}")

        # Final QA receipt must bind the unchanged terminal candidate AND
        # carry a machine verdict that independently establishes PASS
        # (CTR-SIX-009/CTR-SIX-019; blocker-union remediation for the
        # terminal false-pass).
        qa_entry = receipts_by_role.get(Role.QA.value)
        if qa_entry and terminal_head and str(qa_entry["output_head"]) != terminal_head:
            failures.append("final QA receipt does not bind the unchanged terminal candidate")
        if qa_entry is not None and terminal_head:
            qa_results = cast(
                dict[str, object], qa_entry.get("results") or {}
            )
            # Independent re-check: the SAME full PASS-eligibility judgment
            # the runner normalizes with, applied directly to the STORED
            # receipt -- a runner that failed to downgrade a fake PASS (or
            # one that overwrote a mismatching certified-Head echo) cannot
            # hide it here.
            failures.extend(
                qa_pass_eligibility_failures(qa_results, terminal_head, terminal_tree)
            )
            # Tree-level re-check of the automation binding: every declared
            # entrypoint's blob must exist in the certified tree with the
            # exact SHA the receipt recorded.
            bindings = cast(
                list[object], qa_results.get("qa_automation_bindings") or []
            )
            failures.extend(
                automation_tree_binding_failures(manager, terminal_tree, bindings)
            )

        # Impact-and-coverage matrix.
        coverage: dict[str, str] = {}
        for entry in instance.receipts:
            surfaces = cast(list[object], entry.get("surfaces_touched", []))
            for surface in surfaces:
                coverage[str(surface)] = str(entry["receipt_id"])

        if instance.unresolved_spec_gap:
            failures.append(f"unresolved load-bearing SPEC_GAP: {instance.spec_gap_detail}")
        if not instance.done_when_met:
            failures.append("DONE_WHEN not marked satisfied by the task record")

        state = instance.state
        merge_ready = False
        review_pending = False
        if not failures and record.requires_independent_review:
            if state is WorkflowState.INDEPENDENT_REVIEW_PASSED:
                merge_ready = True
            else:
                review_pending = True
                if state in (WorkflowState.TERMINAL_BROADCAST, WorkflowState.CONVERGED):
                    state = WorkflowState.AWAITING_INDEPENDENT_REVIEW

        return VerifyReport(
            task_id=task_id,
            verdict="PASS" if not failures else "FAIL",
            state=state.value,
            merge_ready=merge_ready,
            review_pending=review_pending,
            failures=failures,
            coverage=coverage,
            receipts=report_receipts,
            terminal_head=terminal_head,
        )

"""Envelope semantics: validation, terminal rules, canonical equality."""

from __future__ import annotations

import pytest

from sixpack.errors import EnvelopeInvalid, TerminalBroadcastInvalid
from sixpack.model import TERMINAL_PRIORITY, HandoffEnvelope, HandoffType, Role


def make_envelope(**overrides: object) -> HandoffEnvelope:
    base: dict[str, object] = {
        "sender": "sixpack-role-specifier",
        "task_id": "task-1",
        "repository": "demo-repo",
        "workflow_instance_id": "wf-task-1",
        "from_role": "specifier",
        "to_roles": ["coder"],
        "priority": "10",
        "handoff_type": "normal",
        "base_head": "a" * 40,
        "candidate_head": "b" * 40,
        "candidate_tree": "c" * 40,
        "accepted_authority_revisions": ["f" * 40],
        "affected_contracts": ["demo.contract.v1"],
        "artifacts": ["docs/spec.md"],
        "executed_stage_evidence": {"receipt_id": "r1"},
        "handoff_id": "ho-1",
        "created_at": "2026-09-04T00:00:00Z",
    }
    base.update(overrides)
    return HandoffEnvelope(**base)  # type: ignore[arg-type]


def make_terminal(**overrides: object) -> HandoffEnvelope:
    base: dict[str, object] = {
        "sender": "sixpack-role-qa",
        "task_id": "task-1",
        "repository": "demo-repo",
        "workflow_instance_id": "wf-task-1",
        "from_role": "qa",
        "to_roles": [r.value for r in Role.ordered() if r is not Role.QA],
        "priority": TERMINAL_PRIORITY,
        "handoff_type": "terminal",
        "base_head": "a" * 40,
        "candidate_head": "b" * 40,
        "candidate_tree": "c" * 40,
        "accepted_authority_revisions": ["f" * 40],
        "affected_contracts": ["demo.contract.v1"],
        "artifacts": [],
        "executed_stage_evidence": {"receipt_id": "r6"},
        "handoff_id": "ho-6",
    }
    base.update(overrides)
    return HandoffEnvelope(**base)  # type: ignore[arg-type]


class TestEnvelopeValidation:
    def test_valid_normal_forward(self) -> None:
        envelope = make_envelope()
        assert envelope.semantic_hash()

    def test_short_sha_rejected(self) -> None:
        with pytest.raises(EnvelopeInvalid):
            make_envelope(candidate_head="abc123")

    def test_skip_is_rejected(self) -> None:
        with pytest.raises(EnvelopeInvalid):
            make_envelope(to_roles=["architect"])

    def test_backward_normal_rejected(self) -> None:
        with pytest.raises(EnvelopeInvalid):
            make_envelope(from_role="cleaner", to_roles=["specifier"])

    def test_unknown_role_rejected(self) -> None:
        with pytest.raises(EnvelopeInvalid):
            make_envelope(to_roles=["reviewer"])

    def test_correction_routes_backward_or_self(self) -> None:
        envelope = make_envelope(
            from_role="qa", to_roles=["coder"], handoff_type=HandoffType.CORRECTION.value
        )
        assert envelope.to_roles == ["coder"]

    def test_empty_authority_revisions_rejected(self) -> None:
        with pytest.raises(EnvelopeInvalid):
            make_envelope(accepted_authority_revisions=[])


class TestTerminalRules:
    def test_valid_terminal(self) -> None:
        envelope = make_terminal()
        assert envelope.priority == TERMINAL_PRIORITY

    def test_partial_terminal_recipients_rejected(self) -> None:
        with pytest.raises(TerminalBroadcastInvalid):
            make_terminal(to_roles=["coder", "cleaner"])

    def test_terminal_wrong_priority_rejected(self) -> None:
        with pytest.raises(TerminalBroadcastInvalid):
            make_terminal(priority="01")

    def test_terminal_from_non_qa_rejected(self) -> None:
        with pytest.raises(TerminalBroadcastInvalid):
            make_terminal(
                from_role="coder",
                to_roles=[r.value for r in Role.ordered() if r.value != "coder"],
            )

    def test_duplicate_terminal_recipients_rejected(self) -> None:
        with pytest.raises(TerminalBroadcastInvalid):
            make_terminal(to_roles=["coder", "coder", "cleaner", "architect", "hardender"])


class TestSemanticEquality:
    def test_nonsemantic_fields_excluded(self) -> None:
        first = make_envelope(created_at="2026-09-04T00:00:00Z")
        second = make_envelope(created_at="2026-09-04T09:00:00Z")
        second.audit_challenge_id = "challenge-x"
        assert first.semantic_hash() == second.semantic_hash()

    @pytest.mark.parametrize(
        "field_name,mutation",
        [
            ("sender", {"sender": "sixpack-role-coder"}),
            ("task_id", {"task_id": "task-2"}),
            ("repository", {"repository": "other-repo"}),
            ("workflow_instance_id", {"workflow_instance_id": "wf-2"}),
            ("to_roles", {"to_roles": ["cleaner"]}),
            ("priority", {"priority": "11"}),
            ("handoff_type", {"handoff_type": "terminal"}),
            ("base_head", {"base_head": "d" * 40}),
            ("candidate_head", {"candidate_head": "e" * 40}),
            ("candidate_tree", {"candidate_tree": "1" * 40}),
            ("accepted_authority_revisions", {"accepted_authority_revisions": ["2" * 40]}),
            ("affected_contracts", {"affected_contracts": ["other.contract"]}),
            ("artifacts", {"artifacts": ["docs/other.md"]}),
            ("executed_stage_evidence", {"executed_stage_evidence": {"receipt_id": "r-other"}}),
        ],
    )
    def test_every_semantic_field_change_detected(
        self, field_name: str, mutation: dict[str, object]
    ) -> None:
        from sixpack.canonical import canonical_hash

        envelope = make_envelope()
        semantic = envelope.semantic_dict()
        assert set(HandoffEnvelope.SEMANTIC_FIELDS) == set(semantic)
        changed = {**semantic, **mutation}
        assert envelope.semantic_hash() != canonical_hash(changed)
        # The same semantic content always hashes identically.
        assert envelope.semantic_hash() == canonical_hash(semantic)

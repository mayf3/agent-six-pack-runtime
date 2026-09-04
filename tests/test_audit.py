"""Two-call audit gate matrix (ACC-SIX-007)."""

from __future__ import annotations

import pytest

from sixpack.errors import AuditRequired, ChallengeInvalid, EnvelopeInvalid
from sixpack.model import HandoffEnvelope
from tests.conftest import RuntimeFixture, make_repo, make_runtime  # noqa: F401
from tests.test_model import make_envelope


def staged_envelope(rt: RuntimeFixture, **overrides: object) -> HandoffEnvelope:
    envelope = make_envelope(**overrides)
    with pytest.raises(AuditRequired):
        rt.audit.submit(envelope)
    return envelope


class TestTwoCallGate:
    def test_first_call_returns_audit_required_without_delivery(
        self, runtime: RuntimeFixture
    ) -> None:
        envelope = make_envelope()
        with pytest.raises(AuditRequired) as required:
            runtime.audit.submit(envelope)
        assert required.value.challenge_id
        queue = runtime.queues.queue("specifier")
        assert queue.list_audit_pending() == [f"{envelope.handoff_id}.json"]
        assert queue.list_new() == []
        assert runtime.audit.audit_count("task-1") == 1

    def test_unchanged_second_call_delivers_once(self, runtime: RuntimeFixture) -> None:
        envelope = staged_envelope(runtime)
        envelope.created_at = "2099-01-01T00:00:00Z"  # helper-timestamp drift only
        assert runtime.audit.submit(envelope) == "delivered"
        queue = runtime.queues.queue("specifier")
        assert queue.list_audit_pending() == []
        assert queue.list_outbox() == [f"{envelope.handoff_id}.json"]
        # Helper-owned delivery fans out exactly one recipient copy.
        assert runtime.queues.deliver(envelope) == 1
        assert runtime.queues.queue("coder").list_new() == [f"{envelope.handoff_id}.json"]
        # Audit count must not increment again on the unchanged retry.
        assert runtime.audit.audit_count("task-1") == 1

    def test_changed_challenge_id_cannot_hijack(self, runtime: RuntimeFixture) -> None:
        envelope = staged_envelope(runtime)
        envelope.audit_challenge_id = "challenge-forged"
        with pytest.raises(ChallengeInvalid):
            runtime.audit.submit(envelope)

    def test_replay_after_delivery_refused(self, runtime: RuntimeFixture) -> None:
        envelope = staged_envelope(runtime)
        assert runtime.audit.submit(envelope) == "delivered"
        # A fresh identical submission finds no pending challenge -> new audit.
        fresh = make_envelope()
        with pytest.raises(AuditRequired):
            runtime.audit.submit(fresh)


class TestSemanticChangeInvalidation:
    def test_recipient_swap_invalidates_and_requires_new_audit(
        self, runtime: RuntimeFixture
    ) -> None:
        # Valid-envelope recipient swap: a staged correction (qa->coder)
        # replayed with a different legal backward target (qa->specifier).
        correction = make_envelope(
            sender="sixpack-role-qa",
            from_role="qa",
            to_roles=["coder"],
            handoff_type="correction",
        )
        with pytest.raises(AuditRequired):
            runtime.audit.submit(correction)
        swapped = make_envelope(
            sender="sixpack-role-qa",
            from_role="qa",
            to_roles=["specifier"],
            handoff_type="correction",
        )
        with pytest.raises(EnvelopeInvalid, match="AUDIT_REQUIRED"):
            runtime.audit.submit(swapped)
        assert runtime.audit.pending_challenge("task-1", "qa") is None
        # Invalidation alone does not open a new audit; resubmitting the
        # original envelope starts a fresh challenge (count increments once).
        assert runtime.audit.audit_count("task-1") == 1
        with pytest.raises(AuditRequired):
            runtime.audit.submit(correction)
        assert runtime.audit.audit_count("task-1") == 2

    def test_priority_swap_invalidates(self, runtime: RuntimeFixture) -> None:
        staged_envelope(runtime)
        with pytest.raises(EnvelopeInvalid) as info:
            runtime.audit.submit(make_envelope(priority="11"))
        assert "invalidated" in str(info.value)

    def test_normal_to_terminal_spoof_invalidates(self, runtime: RuntimeFixture) -> None:
        staged_envelope(runtime)
        spoof = make_envelope(
            sender="sixpack-role-qa",
            from_role="qa",
            to_roles=["coder", "cleaner", "specifier", "architect", "hardender"],
            priority="00",
            handoff_type="terminal",
        )
        # Different from_role -> different challenge slot -> treated as new audit.
        with pytest.raises(AuditRequired):
            runtime.audit.submit(spoof)
        # The original normal handoff challenge is still pending, untouched.
        assert runtime.audit.pending_challenge("task-1", "specifier") is not None

    def test_same_slot_type_swap_invalidates(self, runtime: RuntimeFixture) -> None:
        staged_envelope(runtime)
        changed = make_envelope(handoff_type="correction", to_roles=["specifier"])
        with pytest.raises(EnvelopeInvalid):
            runtime.audit.submit(changed)
        assert runtime.audit.pending_challenge("task-1", "specifier") is None

    def test_candidate_change_invalidates(self, runtime: RuntimeFixture) -> None:
        staged_envelope(runtime)
        with pytest.raises(EnvelopeInvalid):
            runtime.audit.submit(make_envelope(candidate_head="e" * 40))

    def test_evidence_change_invalidates(self, runtime: RuntimeFixture) -> None:
        staged_envelope(runtime)
        with pytest.raises(EnvelopeInvalid):
            runtime.audit.submit(
                make_envelope(executed_stage_evidence={"receipt_id": "r-forged"})
            )

    def test_invalidation_parks_item_as_failed(self, runtime: RuntimeFixture) -> None:
        staged_envelope(runtime)
        with pytest.raises(EnvelopeInvalid):
            runtime.audit.submit(make_envelope(priority="99"))
        queue = runtime.queues.queue("specifier")
        assert queue.list_audit_pending() == []
        assert len(queue.list_new()) == 0
        assert (queue.root / "failed").exists()

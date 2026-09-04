"""Durable queue: lifecycle, duplicate suppression, integrity, ambiguity refusal."""

from __future__ import annotations

import pytest

from sixpack.errors import QueueCorrupt
from tests.conftest import RuntimeFixture, gate_and_deliver, make_repo, make_runtime  # noqa: F401
from tests.test_model import make_envelope

DIRECTORIES = (
    "outbox/tmp", "outbox", "sent", "failed", "audit_pending",
    "inbox/new", "inbox/in_process", "inbox/completed",
)


class TestLifecycle:
    def test_directories_created(self, runtime: RuntimeFixture) -> None:
        queue = runtime.queues.queue("coder")
        for relative in DIRECTORIES:
            assert (queue.root / relative).is_dir(), relative

    def test_duplicate_delivery_suppressed(self, runtime: RuntimeFixture) -> None:
        envelope = make_envelope()
        first = gate_and_deliver(runtime, envelope)
        assert first == 1
        # Redelivering the same handoff must not create a second copy.
        second = gate_and_deliver(runtime, envelope)
        assert second == 0
        queue = runtime.queues.queue("coder")
        assert queue.list_new() == [f"{envelope.handoff_id}.json"]

    def test_two_in_process_jobs_refused(self, runtime: RuntimeFixture) -> None:
        first = make_envelope(handoff_id="ho-a")
        second = make_envelope(handoff_id="ho-b", to_roles=["cleaner"], from_role="coder")
        gate_and_deliver(runtime, first)
        gate_and_deliver(runtime, second)
        coder_queue = runtime.queues.queue("coder")
        cleaner_queue = runtime.queues.queue("cleaner")
        coder_queue.claim_inbound("ho-a")
        cleaner_queue.claim_inbound("ho-b")
        # A second job for the same (now busy) station is refused.
        third = make_envelope(handoff_id="ho-c", to_roles=["cleaner"], from_role="coder")
        gate_and_deliver(runtime, third)
        with pytest.raises(QueueCorrupt):
            coder_queue.claim_inbound("ho-b")  # wrong queue ambiguity check
        with pytest.raises(QueueCorrupt):
            runtime.queues.queue("specifier").claim_inbound("ho-c")

    def test_manual_helper_bypass_detected(self, runtime: RuntimeFixture) -> None:
        envelope = make_envelope()
        gate_and_deliver(runtime, envelope)
        queue = runtime.queues.queue("coder")
        queue.verify_integrity()  # consistent state passes
        rogue = queue.root / "inbox/new" / "ho-rogue.json"
        rogue.write_text("{}", encoding="utf-8")
        with pytest.raises(QueueCorrupt):
            queue.verify_integrity()

    def test_out_of_band_removal_detected(self, runtime: RuntimeFixture) -> None:
        envelope = make_envelope()
        gate_and_deliver(runtime, envelope)
        queue = runtime.queues.queue("coder")
        (queue.root / "inbox/new" / f"{envelope.handoff_id}.json").unlink()
        with pytest.raises(QueueCorrupt):
            queue.verify_integrity()


class TestCrashRecovery:
    def test_unexecuted_in_process_item_requeued(self, runtime: RuntimeFixture) -> None:
        envelope = make_envelope()
        gate_and_deliver(runtime, envelope)
        queue = runtime.queues.queue("coder")
        queue.claim_inbound(envelope.handoff_id)
        report = runtime.queues.recover(executed_handoffs=set())
        assert report["requeued"] == 1
        assert queue.list_new() == [f"{envelope.handoff_id}.json"]
        assert queue.list_in_process() == []

    def test_executed_in_process_item_completed(self, runtime: RuntimeFixture) -> None:
        envelope = make_envelope()
        gate_and_deliver(runtime, envelope)
        queue = runtime.queues.queue("coder")
        queue.claim_inbound(envelope.handoff_id)
        report = runtime.queues.recover(executed_handoffs={envelope.handoff_id})
        assert report["requeued"] == 0
        assert queue.list_in_process() == []
        assert queue.list_new() == []

    def test_missing_recipient_copy_redelivered(self, runtime: RuntimeFixture) -> None:
        envelope = make_envelope()
        gate_and_deliver(runtime, envelope)
        queue = runtime.queues.queue("coder")
        copy_name = f"{envelope.handoff_id}.json"
        (queue.root / "inbox/new" / copy_name).unlink()
        # Simulate the crash happening before the copy was tracked: drop the
        # tracking entry so tracked state stays consistent with disk.
        state = queue._read_integrity()
        state.pop(f"inbox/new/{copy_name}")
        queue._write_integrity(state)
        report = runtime.queues.recover(executed_handoffs=set())
        assert report["redelivered"] == 1
        assert queue.list_new() == [copy_name]

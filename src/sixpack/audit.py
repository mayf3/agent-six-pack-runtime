"""Two-call unchanged-envelope audit gate (CTR-SIX-013 / ACC-SIX-007).

On the first valid normal-forward or terminal Git handoff attempt the helper
normalizes and persists a challenge over the complete semantic envelope and
returns ``AUDIT_REQUIRED`` without delivering. Only a second submission whose
semantic content is byte-identical (same canonical hash) may be delivered.
Any semantic field change -- recipients, priority, handoff type, base,
candidate, authority revisions, contracts, artifacts, evidence -- invalidates
the old challenge and requires a new audit. Helper-generated timestamps and
delivery metadata are excluded from equality.

This gate is author self-check, never independent review.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .canonical import canonical_hash
from .errors import AuditRequired, ChallengeInvalid, EnvelopeInvalid
from .model import HandoffEnvelope, HandoffType
from .queue import QueueStore


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class AuditGate:
    """Per-workspace audit challenge store and submission gate."""

    def __init__(self, root: Path, queues: QueueStore) -> None:
        self.root = root
        self.queues = queues
        self.counters_path = root / "audit_counts.json"

    # -- persistence ---------------------------------------------------------

    def _challenge_path(self, task_id: str, from_role: str) -> Path:
        return self.root / "challenges" / f"{task_id}.{from_role}.json"

    def _load_challenge(self, task_id: str, from_role: str) -> dict[str, object] | None:
        path = self._challenge_path(task_id, from_role)
        if not path.exists():
            return None
        return dict(json.loads(path.read_text(encoding="utf-8")))

    def _save_challenge(self, record: dict[str, object]) -> None:
        path = self._challenge_path(str(record["task_id"]), str(record["from_role"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(record, sort_keys=True, indent=1), encoding="utf-8")
        os.replace(tmp, path)

    def _delete_challenge(self, task_id: str, from_role: str) -> None:
        path = self._challenge_path(task_id, from_role)
        if path.exists():
            path.unlink()

    def audit_count(self, task_id: str) -> int:
        if not self.counters_path.exists():
            return 0
        counters = json.loads(self.counters_path.read_text(encoding="utf-8"))
        return int(counters.get(task_id, 0))

    def _increment_audit_count(self, task_id: str) -> int:
        counters: dict[str, int] = {}
        if self.counters_path.exists():
            counters = dict(json.loads(self.counters_path.read_text(encoding="utf-8")))
        counters[task_id] = int(counters.get(task_id, 0)) + 1
        self.counters_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.counters_path.with_name(self.counters_path.name + ".tmp")
        tmp.write_text(json.dumps(counters, sort_keys=True, indent=1), encoding="utf-8")
        os.replace(tmp, self.counters_path)
        return counters[task_id]

    # -- gate ------------------------------------------------------------------

    def submit(self, envelope: HandoffEnvelope) -> str:
        """Run the two-call gate for one handoff submission.

        Returns ``"delivered"`` when the unchanged second call passes, or
        raises :class:`AuditRequired` when a new challenge was recorded.
        Raises :class:`ChallengeInvalid` on malformed re-submissions that
        cannot enter a fresh audit (e.g. replay after delivery).
        """
        existing = self._load_challenge(envelope.task_id, envelope.from_role)
        if existing is None:
            return self._first_call(envelope)
        return self._second_call(envelope, existing)

    def _first_call(self, envelope: HandoffEnvelope) -> str:
        sender_queue = self.queues.queue(envelope.from_role)
        sender_queue.stage_outbound(envelope)
        challenge_id = f"challenge-{canonical_hash(envelope.semantic_dict())[:16]}"
        count = self._increment_audit_count(envelope.task_id)
        record: dict[str, object] = {
            "challenge_id": challenge_id,
            "task_id": envelope.task_id,
            "from_role": envelope.from_role,
            "semantic_hash": envelope.semantic_hash(),
            "envelope": envelope.to_dict(),
            "audit_count": count,
            "created_at": _now(),
            "status": "pending",
        }
        self._save_challenge(record)
        sender_queue.park_challenge(envelope, challenge_id)
        envelope.audit_challenge_id = challenge_id
        raise AuditRequired(challenge_id)

    def _second_call(self, envelope: HandoffEnvelope, existing: dict[str, object]) -> str:
        if str(existing.get("status")) != "pending":
            raise ChallengeInvalid(
                f"challenge {existing.get('challenge_id')} is not pending; "
                "a delivered or invalidated challenge cannot be reused"
            )
        stored_hash = str(existing["semantic_hash"])
        new_hash = envelope.semantic_hash()
        sender_queue = self.queues.queue(envelope.from_role)
        if stored_hash == new_hash:
            # Unchanged semantic envelope: the challenge identity must also
            # match what the sender is replaying.
            if envelope.audit_challenge_id not in (None, existing["challenge_id"]):
                raise ChallengeInvalid("submission names a different challenge")
            envelope.audit_challenge_id = str(existing["challenge_id"])
            sender_queue.release_for_delivery(envelope)
            existing["status"] = "delivered"
            existing["delivered_at"] = _now()
            self._save_challenge(existing)
            self._delete_challenge(envelope.task_id, envelope.from_role)
            return "delivered"
        # Semantic change: invalidate the old challenge, start a fresh audit.
        sender_queue.park_failed(
            envelope, "CHALLENGE_INVALIDATED: semantic envelope changed between calls",
            from_dir="audit_pending",
        )
        existing["status"] = "invalidated"
        existing["invalidated_at"] = _now()
        existing["invalidated_by_hash"] = new_hash
        self._save_challenge(existing)
        self._delete_challenge(envelope.task_id, envelope.from_role)
        raise EnvelopeInvalid(
            "AUDIT_REQUIRED: semantic envelope changed; previous challenge "
            f"{existing.get('challenge_id')} invalidated; a new audit is required"
        )

    def pending_challenge(self, task_id: str, from_role: str) -> dict[str, object] | None:
        challenge = self._load_challenge(task_id, from_role)
        if challenge and challenge.get("status") == "pending":
            return challenge
        return None

    def gate_applies(self, envelope: HandoffEnvelope) -> bool:
        """The gate covers normal-forward and terminal handoffs (CTR-SIX-013).

        Correction handoffs are explicit work re-entry and use the same
        challenge mechanism; only convergence-only deliveries skip it, and
        none exist in this runtime.
        """
        return envelope.handoff_type in (
            HandoffType.NORMAL.value,
            HandoffType.TERMINAL.value,
            HandoffType.CORRECTION.value,
        )

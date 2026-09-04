"""Durable, restart-safe, helper-owned queue state (CTR-SIX-012).

Directory layout per role queue root::

    outbox/tmp      staging for outbound items being prepared
    outbox          validated outbound items (challenge satisfied)
    sent            delivered outbound items
    failed          refused/invalidated items
    audit_pending   first-call challenges awaiting the unchanged re-submit
    inbox/new       delivered inbound items awaiting pickup
    inbox/in_process    claimed items (at most one; ambiguity is refused)
    inbox/completed     processed items

Helper tooling -- never agents -- owns atomic queue transitions, timestamps,
duplicate suppression, restart recovery, and refusal of ambiguous
multiple-in-process states. Every transition is recorded in an append-only
transition log; an integrity scan replays the log against the filesystem and
fails closed when files were moved out-of-band (manual helper bypass).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

from .canonical import canonical_hash
from .errors import QueueCorrupt
from .model import HandoffEnvelope

DIRECTORIES: tuple[str, ...] = (
    "outbox/tmp",
    "outbox",
    "sent",
    "failed",
    "audit_pending",
    "inbox/new",
    "inbox/in_process",
    "inbox/completed",
)

_LOG_NAME = "transitions.jsonl"
_INTEGRITY_NAME = "integrity_state.json"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass(frozen=True)
class QueueItem:
    envelope: HandoffEnvelope
    filename: str
    location: str
    delivered_to: str = ""  # recipient role for inbox items


class RoleQueue:
    """One role's durable inbox/outbox tree."""

    def __init__(self, root: Path, role: str) -> None:
        self.root = root
        self.role = role
        self.log_path = root / _LOG_NAME
        self.integrity_path = root / _INTEGRITY_NAME

    # -- setup ------------------------------------------------------------

    def ensure_directories(self) -> None:
        for relative in DIRECTORIES:
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("", encoding="utf-8")
        if not self.integrity_path.exists():
            self._write_integrity({})

    # -- transition log ----------------------------------------------------

    def _append_log(self, action: str, detail: dict[str, object]) -> None:
        entry = {"ts": _now(), "action": action, "role": self.role, **detail}
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def _read_log(self) -> list[dict[str, object]]:
        if not self.log_path.exists():
            return []
        entries: list[dict[str, object]] = []
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(json.loads(line))
        return entries

    def _write_integrity(self, state: dict[str, str]) -> None:
        tmp = self.integrity_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, sort_keys=True, indent=1), encoding="utf-8")
        os.replace(tmp, self.integrity_path)

    def _read_integrity(self) -> dict[str, str]:
        if not self.integrity_path.exists():
            return {}
        return dict(json.loads(self.integrity_path.read_text(encoding="utf-8")))

    # -- atomic file moves ---------------------------------------------------

    def _atomic_write(self, directory: str, filename: str, payload: str) -> Path:
        target = self.root / directory / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(".tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, target)
        return target

    def _move(self, source: Path, target_dir: str) -> Path:
        target = self.root / target_dir / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, target)
        return target

    @staticmethod
    def _payload(envelope: HandoffEnvelope, delivered_to: str) -> str:
        return json.dumps(
            {**envelope.to_dict(), "delivered_to": delivered_to},
            sort_keys=True,
            indent=1,
        )

    # -- public transitions -----------------------------------------------

    def stage_outbound(self, envelope: HandoffEnvelope) -> Path:
        """Write the item into ``outbox/tmp`` (first call of the audit gate)."""
        self.ensure_directories()
        filename = f"{envelope.handoff_id}.json"
        path = self._atomic_write("outbox/tmp", filename, self._payload(envelope, ""))
        self._append_log("stage_outbound", {"file": filename, "hash": envelope.semantic_hash()})
        self._track("outbox/tmp/" + filename, canonical_hash(path.read_text("utf-8")))
        return path

    def park_challenge(self, envelope: HandoffEnvelope, challenge_id: str) -> Path:
        """Move the staged item to ``audit_pending``; task stays in process."""
        source = self.root / "outbox/tmp" / f"{envelope.handoff_id}.json"
        target = self._move(source, "audit_pending")
        self._append_log(
            "park_challenge",
            {"file": target.name, "challenge_id": challenge_id, "hash": envelope.semantic_hash()},
        )
        self._retrack(f"outbox/tmp/{target.name}", f"audit_pending/{target.name}")
        return target

    def release_for_delivery(self, envelope: HandoffEnvelope) -> Path:
        """Second unchanged call: move ``audit_pending`` item to ``outbox``."""
        source = self.root / "audit_pending" / f"{envelope.handoff_id}.json"
        if not source.exists():
            raise QueueCorrupt(f"no audit_pending item {envelope.handoff_id} to release")
        target = self._move(source, "outbox")
        self._append_log("release_for_delivery", {"file": target.name})
        self._retrack(f"audit_pending/{target.name}", f"outbox/{target.name}")
        return target

    def park_failed(self, envelope: HandoffEnvelope, reason: str, from_dir: str) -> Path:
        source = self.root / from_dir / f"{envelope.handoff_id}.json"
        if not source.exists():
            raise QueueCorrupt(f"no item {envelope.handoff_id} in {from_dir}")
        target = self._move(source, "failed")
        self._append_log("park_failed", {"file": target.name, "reason": reason, "from": from_dir})
        self._retrack(f"{from_dir}/{target.name}", f"failed/{target.name}")
        return target

    def mark_sent(self, envelope: HandoffEnvelope) -> Path:
        source = self.root / "outbox" / f"{envelope.handoff_id}.json"
        already = self.root / "sent" / f"{envelope.handoff_id}.json"
        if not source.exists():
            if already.exists():
                return already  # idempotent: fan-out replay after gate pass
            raise QueueCorrupt(f"no outbox item {envelope.handoff_id} to mark sent")
        target = self._move(source, "sent")
        self._append_log("mark_sent", {"file": target.name})
        self._retrack(f"outbox/{target.name}", f"sent/{target.name}")
        return target

    def claim_inbound(self, handoff_id: str) -> Path:
        """Move one item from ``inbox/new`` to ``inbox/in_process``."""
        source = self.root / "inbox/new" / f"{handoff_id}.json"
        if not source.exists():
            raise QueueCorrupt(f"no inbound item {handoff_id} in inbox/new")
        in_process = self.list_in_process()
        if len(in_process) >= 1:
            raise QueueCorrupt(
                f"role {self.role} already has an in-process item; "
                "ambiguous multiple-in-process state refused"
            )
        target = self._move(source, "inbox/in_process")
        self._append_log("claim_inbound", {"file": target.name})
        self._retrack(f"inbox/new/{target.name}", f"inbox/in_process/{target.name}")
        return target

    def complete_inbound(self, handoff_id: str) -> Path:
        source = self.root / "inbox/in_process" / f"{handoff_id}.json"
        if not source.exists():
            raise QueueCorrupt(f"no in-process item {handoff_id}")
        target = self._move(source, "inbox/completed")
        self._append_log("complete_inbound", {"file": target.name})
        self._retrack(f"inbox/in_process/{target.name}", f"inbox/completed/{target.name}")
        return target

    def requeue_in_process(self, handoff_id: str, reason: str) -> Path:
        """Crash recovery: an unexecuted in-process item returns to inbox/new."""
        source = self.root / "inbox/in_process" / f"{handoff_id}.json"
        if not source.exists():
            raise QueueCorrupt(f"no in-process item {handoff_id}")
        target = self._move(source, "inbox/new")
        self._append_log("requeue_in_process", {"file": target.name, "reason": reason})
        self._retrack(f"inbox/in_process/{target.name}", f"inbox/new/{target.name}")
        return target

    # -- inspection ----------------------------------------------------------

    def _list_dir(self, directory: str) -> list[str]:
        base = self.root / directory
        if not base.exists():
            return []
        return sorted(p.name for p in base.glob("*.json"))

    def list_new(self) -> list[str]:
        return self._list_dir("inbox/new")

    def list_sent(self) -> list[str]:
        return self._list_dir("sent")

    def list_in_process(self) -> list[str]:
        return self._list_dir("inbox/in_process")

    def list_audit_pending(self) -> list[str]:
        return self._list_dir("audit_pending")

    def list_outbox(self) -> list[str]:
        return self._list_dir("outbox")

    def read_item(self, directory: str, filename: str) -> HandoffEnvelope:
        path = self.root / directory / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        return HandoffEnvelope.from_dict(data)

    # -- integrity ------------------------------------------------------------

    def _track(self, key: str, digest: str) -> None:
        state = self._read_integrity()
        state[key] = digest
        self._write_integrity(state)

    def _retrack(self, old_key: str, new_key: str) -> None:
        state = self._read_integrity()
        if old_key in state:
            state[new_key] = state.pop(old_key)
        else:
            state[new_key] = ""
        self._write_integrity(state)

    def verify_integrity(self) -> None:
        """Fail closed on out-of-band queue mutation (manual helper bypass).

        Compares the tracked file set/hashes against the live filesystem.
        Any file the helper did not place, any missing tracked file, and any
        content drift raise ``QueueCorrupt``.
        """
        state = self._read_integrity()
        live: dict[str, str] = {}
        for relative in DIRECTORIES:
            base = self.root / relative
            if not base.exists():
                continue
            for path in base.glob("*.json"):
                live[f"{relative}/{path.name}"] = canonical_hash(path.read_text("utf-8"))
        for key, digest in live.items():
            if key not in state:
                raise QueueCorrupt(f"untracked queue file appeared out-of-band: {key}")
            if state[key] and state[key] != digest:
                raise QueueCorrupt(f"queue file content changed outside helper transitions: {key}")
        for key in state:
            if key not in live:
                raise QueueCorrupt(f"tracked queue file disappeared out-of-band: {key}")
        # Ambiguous multiple-in-process refusal.
        if len(self.list_in_process()) > 1:
            raise QueueCorrupt(
                f"role {self.role} has multiple in-process items; refusing ambiguous state"
            )


class QueueStore:
    """All role queues plus delivery fan-out for one runtime workspace."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.queues: dict[str, RoleQueue] = {}

    def queue(self, role: str) -> RoleQueue:
        if role not in self.queues:
            queue = RoleQueue(self.root / role, role)
            queue.ensure_directories()
            self.queues[role] = queue
        return self.queues[role]

    def deliver(self, envelope: HandoffEnvelope) -> int:
        """Fan out one validated outbound item to all recipient inboxes.

        Returns the number of fresh copies written. Duplicate suppression is
        per recipient: an already-pending or already-completed handoff copy is
        never written twice.
        """
        sender = self.queue(envelope.from_role)
        sender.mark_sent(envelope)
        written = 0
        for recipient in envelope.to_roles:
            queue = self.queue(recipient)
            filename = f"{envelope.handoff_id}.json"
            pending = queue.root / "inbox/new" / filename
            completed = queue.root / "inbox/completed" / filename
            if pending.exists() or completed.exists():
                continue  # idempotent duplicate suppression
            queue._atomic_write("inbox/new", filename, RoleQueue._payload(envelope, recipient))
            queue._append_log("deliver_copy", {"file": filename, "handoff_id": envelope.handoff_id})
            queue._track(
                "inbox/new/" + filename,
                canonical_hash((queue.root / "inbox/new" / filename).read_text("utf-8")),
            )
            written += 1
        return written

    def known_roles(self) -> list[str]:
        """The fixed six-station roster, independent of lazy instantiation."""
        from .model import ROLE_RECEIVE_POLICY

        return [role.value for role in ROLE_RECEIVE_POLICY]

    def verify_all_integrity(self) -> None:
        # Iterate the fixed roster: a fresh process has instantiated no
        # queues, and integrity must cover every station.
        for role in self.known_roles():
            self.queue(role).verify_integrity()

    def recover(self, executed_handoffs: set[str]) -> dict[str, object]:
        """Restart recovery (CTR-SIX-012 / ACC-SIX-006).

        - Redeliver sent items whose recipient copy went missing.
        - Requeue in-process items that were never executed (no ledger record).
        - Refuse ambiguous states (multiple in-process items).
        """
        redelivered = 0
        requeued = 0
        refused: list[str] = []
        # Scan the fixed roster, not the lazily-instantiated dict: a fresh
        # recovery process has no queues instantiated yet.
        for role in self.known_roles():
            queue = self.queue(role)
            if len(queue.list_in_process()) > 1:
                refused.append(f"{role}: multiple in-process items")
                continue
            for filename in list(queue.list_in_process()):
                handoff_id = filename.removesuffix(".json")
                if handoff_id in executed_handoffs:
                    queue.complete_inbound(handoff_id)
                else:
                    queue.requeue_in_process(handoff_id, "crash recovery: execution unrecorded")
                    requeued += 1
        # Missing recipient copies for delivered fan-out (crash between
        # mark_sent and a recipient write): redeliver idempotently.
        for queue in self.queues.values():
            for filename in queue.list_sent():
                envelope = queue.read_item("sent", filename)
                for recipient in envelope.to_roles:
                    recipient_queue = self.queue(recipient)
                    copy_name = f"{envelope.handoff_id}.json"
                    pending = recipient_queue.root / "inbox/new" / copy_name
                    completed = recipient_queue.root / "inbox/completed" / copy_name
                    if pending.exists() or completed.exists():
                        continue
                    recipient_queue._atomic_write(
                        "inbox/new", copy_name, RoleQueue._payload(envelope, recipient)
                    )
                    recipient_queue._append_log(
                        "deliver_copy", {"file": copy_name, "handoff_id": envelope.handoff_id}
                    )
                    recipient_queue._track(
                        f"inbox/new/{copy_name}",
                        canonical_hash(pending.read_text("utf-8")),
                    )
                    redelivered += 1
        return {"redelivered": redelivered, "requeued": requeued, "refused": refused}

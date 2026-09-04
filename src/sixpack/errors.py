"""Typed error hierarchy for the six-pack runtime.

Every refusal the runtime makes is a typed error so the CLI and the
deterministic controller can report machine-readable rejection reasons.
"""

from __future__ import annotations


class SixPackError(Exception):
    """Base class for all runtime refusals."""

    code = "SIXPACK_ERROR"


class EnvelopeInvalid(SixPackError):
    """A handoff envelope violates the semantic envelope contract."""

    code = "ENVELOPE_INVALID"


class TerminalBroadcastInvalid(EnvelopeInvalid):
    """Terminal broadcast violates recipients/priority/type rules."""

    code = "TERMINAL_INVALID"


class ChallengeInvalid(SixPackError):
    """Audit challenge is missing, stale, or invalidated by a semantic change."""

    code = "CHALLENGE_INVALID"


class AuditRequired(SixPackError):
    """First valid submission recorded a challenge; delivery is withheld."""

    code = "AUDIT_REQUIRED"

    def __init__(self, challenge_id: str) -> None:
        super().__init__(f"audit required; challenge_id={challenge_id}")
        self.challenge_id = challenge_id


class QueueCorrupt(SixPackError):
    """Queue state is ambiguous or was mutated outside helper-owned transitions."""

    code = "QUEUE_CORRUPT"


class DuplicateDelivery(SixPackError):
    """A handoff was already delivered/executed; suppressed idempotently."""

    code = "DUPLICATE_DELIVERY"


class ProfileGateFailure(SixPackError):
    """Task lacks a valid PREFLIGHT/profile-selection record for stage entry."""

    code = "PROFILE_GATE_FAILURE"


class WorktreeError(SixPackError):
    """Isolated write surface could not be established or verified."""

    code = "WORKTREE_ERROR"


class HeadDrift(WorktreeError):
    """Repository head moved without revalidation; abort instead of adopting."""

    code = "HEAD_DRIFT"


class MainCheckoutWrite(WorktreeError):
    """An operation attempted to mutate the active main checkout."""

    code = "MAIN_CHECKOUT_WRITE"


class WorkflowStateInvalid(SixPackError):
    """A workflow transition is not legal from the current state."""

    code = "WORKFLOW_INVALID"


class CorrectionRequired(SixPackError):
    """A substantive correction must route to the earliest affected role."""

    code = "CORRECTION_REQUIRED"


class VerificationFailure(SixPackError):
    """Terminal impact-and-coverage verification failed."""

    code = "VERIFY_FAILED"


class HostPolicyViolation(SixPackError):
    """Controller admission/routing violated a host invariant."""

    code = "HOST_POLICY_VIOLATION"


class ManifestMismatch(SixPackError):
    """Pinned bytes do not match the exact-revision manifest."""

    code = "MANIFEST_MISMATCH"


class QaVerificationFailed(SixPackError):
    """Final QA verdict is FAIL/BLOCKED or machine evidence is missing/invalid."""

    code = "QA_VERIFICATION_FAILED"


class SelfCertificationRejected(SixPackError):
    """QA attempted to certify bytes it modified after the final run started."""

    code = "QA_SELF_CERTIFICATION"

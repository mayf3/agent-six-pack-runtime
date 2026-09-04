"""Mutation-hardening checks for version-reporting metadata."""

from __future__ import annotations

import sixpack


def test_governance_revision_is_bound_to_accepted_authority() -> None:
    """Kill governance-pin drift hidden by expectations using the same constant."""
    assert (
        sixpack.GOVERNANCE_SOURCE_COMMIT
        == "fcd417ba608bafcc8a1160f3e95f8c43cb2212d8"
    )

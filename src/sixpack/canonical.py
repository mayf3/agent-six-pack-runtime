"""Canonical JSON encoding and hashing.

The two-call audit gate compares *semantic* envelope content. Equality is
defined over a canonical encoding: sorted keys, no whitespace, full SHAs.
Helper-generated fields (timestamps, queue filenames, delivery-copy metadata)
are excluded from the canonical form by the caller.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

_HEX40_LENGTH = 40


def canonical_json(value: Any) -> str:
    """Encode ``value`` as deterministic JSON (sorted keys, no whitespace)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(value: Any) -> str:
    """SHA-256 of the canonical JSON encoding, hex encoded."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def is_full_sha(value: object) -> bool:
    """True when ``value`` is a 40-character lowercase hex string."""
    if not isinstance(value, str) or len(value) != _HEX40_LENGTH:
        return False
    return all(c in "0123456789abcdef" for c in value)


def require_full_sha(value: object, field: str) -> str:
    """Return ``value`` when it is a full 40-hex SHA; raise otherwise."""
    if not is_full_sha(value):
        raise ValueError(f"{field} must be a full 40-hex SHA, got: {value!r}")
    return str(value)

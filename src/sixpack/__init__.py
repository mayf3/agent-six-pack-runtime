"""agent-six-pack-runtime: a repository-agnostic Six-Pack software delivery runtime.

Implements the accepted AGENT_SIX_PACK_DELIVERY_PROFILE_V1 contract set
(governing authority: mayf3/agent-development-governance @
fcd417ba608bafcc8a1160f3e95f8c43cb2212d8) as a machine-verifiable runtime:

specifier -> coder -> cleaner -> architect -> hardender -> QA
"""

from .errors import AuditRequired, SixPackError
from .model import TERMINAL_PRIORITY, HandoffEnvelope, HandoffType, Role, StageReceipt

__version__ = "0.1.0"

GOVERNANCE_SOURCE_COMMIT = "fcd417ba608bafcc8a1160f3e95f8c43cb2212d8"

__all__ = [
    "GOVERNANCE_SOURCE_COMMIT",
    "TERMINAL_PRIORITY",
    "AuditRequired",
    "HandoffEnvelope",
    "HandoffType",
    "Role",
    "SixPackError",
    "StageReceipt",
]

"""Role definition loading and validation (CTR-SIX-010).

Each role ships a machine-readable definition declaring ``Owns``,
``DoesNotOwn``, required inputs, permitted mutations, required checks,
handoff target, failure output, and done criteria. Validation rejects
reordered/merged/duplicated roles, ownership overreach, and required
outputs with zero or multiple owning roles.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Any

from .errors import EnvelopeInvalid
from .model import ROLE_RECEIVE_POLICY, Propagation, ReceiveMode, Role

REQUIRED_OUTPUT_OWNERS: dict[str, Role] = {
    "behavior_specification": Role.SPECIFIER,
    "qa_procedure": Role.SPECIFIER,
    "acceptance_generator_runtime_step_handlers": Role.CODER,
    "implementation_and_unit_tests": Role.CODER,
    "cleanup_and_local_quality_checks": Role.CLEANER,
    "architecture_and_property_tests": Role.ARCHITECT,
    "mutation_hardening": Role.HARDENDER,
    "executable_qa_automation": Role.QA,
    "final_qa_receipt": Role.QA,
}


@dataclass(frozen=True)
class RoleDefinition:
    role: Role
    owns: list[str]
    does_not_own: list[str]
    required_inputs: list[str]
    permitted_mutations: list[str]
    required_checks: list[str]
    handoff_target: str
    failure_output: str
    done_criteria: list[str]
    receive_mode: ReceiveMode
    propagation: Propagation
    terminal_broadcast: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value,
            "owns": self.owns,
            "does_not_own": self.does_not_own,
            "required_inputs": self.required_inputs,
            "permitted_mutations": self.permitted_mutations,
            "required_checks": self.required_checks,
            "handoff_target": self.handoff_target,
            "failure_output": self.failure_output,
            "done_criteria": self.done_criteria,
            "receive_mode": self.receive_mode.value,
            "propagation": self.propagation.value,
            "terminal_broadcast": self.terminal_broadcast,
        }


@dataclass(frozen=True)
class RoleCatalog:
    definitions: dict[Role, RoleDefinition]

    def definition(self, role: Role) -> RoleDefinition:
        return self.definitions[role]

    def validate(self) -> None:
        """Fail profile validation before work begins (CTR-SIX-010)."""
        ordered = [d.role for d in self.definitions.values()]
        if ordered != Role.ordered():
            raise EnvelopeInvalid(
                f"role catalog must contain the six canonical roles in order, "
                f"got {[r.value for r in ordered]}"
            )
        # Receive modes and propagation tokens must match DEC-SIX-008.
        for role, policy in ROLE_RECEIVE_POLICY.items():
            definition = self.definitions[role]
            if (
                definition.receive_mode != policy.mode
                or definition.propagation != policy.propagation
            ):
                raise EnvelopeInvalid(
                    f"role {role.value} receive config drifts from DEC-SIX-008 profile"
                )
        # Exactly-one ownership for every required output.
        owners: dict[str, list[Role]] = {}
        for definition in self.definitions.values():
            for item in definition.owns:
                owners.setdefault(item, []).append(definition.role)
        for output, expected_owner in REQUIRED_OUTPUT_OWNERS.items():
            holder = owners.get(output, [])
            if holder != [expected_owner]:
                raise EnvelopeInvalid(
                    f"required output {output!r} must be owned by exactly "
                    f"{expected_owner.value}, got {[r.value for r in holder]}"
                )
        # No role may own another role's exclusive decision.
        for definition in self.definitions.values():
            exclusive_owned = set(definition.owns)
            for output, owner in REQUIRED_OUTPUT_OWNERS.items():
                if owner is not definition.role and output in exclusive_owned:
                    raise EnvelopeInvalid(
                        f"role {definition.role.value} claims exclusive output {output!r} "
                        f"owned by {owner.value}"
                    )


def load_role_catalog() -> RoleCatalog:
    """Load and validate the vendored role definitions at their exact revision."""
    catalog: dict[Role, RoleDefinition] = {}
    for role in Role.ordered():
        raw = resources.files("sixpack").joinpath(f"roles/{role.value}.json").read_text("utf-8")
        data = json.loads(raw)
        catalog[role] = RoleDefinition(
            role=Role(data["role"]),
            owns=list(data["owns"]),
            does_not_own=list(data["does_not_own"]),
            required_inputs=list(data["required_inputs"]),
            permitted_mutations=list(data["permitted_mutations"]),
            required_checks=list(data["required_checks"]),
            handoff_target=str(data["handoff_target"]),
            failure_output=str(data["failure_output"]),
            done_criteria=list(data["done_criteria"]),
            receive_mode=ReceiveMode(data["receive_mode"]),
            propagation=Propagation(data["propagation"]),
            terminal_broadcast=bool(data.get("terminal_broadcast", False)),
        )
    instance = RoleCatalog(catalog)
    instance.validate()
    return instance


def role_catalog_digest() -> str:
    """Deterministic digest over the vendored role definition bytes."""
    from .canonical import canonical_hash

    payloads: dict[str, str] = {}
    for role in Role.ordered():
        payloads[role.value] = resources.files("sixpack").joinpath(
            f"roles/{role.value}.json"
        ).read_text("utf-8")
    return canonical_hash(payloads)

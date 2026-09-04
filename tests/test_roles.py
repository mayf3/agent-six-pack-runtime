"""Role catalog validation (CTR-SIX-010)."""

from __future__ import annotations

import json

import pytest

from sixpack.errors import EnvelopeInvalid
from sixpack.model import Role
from sixpack.roles import REQUIRED_OUTPUT_OWNERS, load_role_catalog, role_catalog_digest


class TestRoleCatalog:
    def test_canonical_catalog_loads(self) -> None:
        catalog = load_role_catalog()
        assert list(catalog.definitions) == Role.ordered()
        assert role_catalog_digest()

    def test_every_required_output_has_exactly_one_owner(self) -> None:
        catalog = load_role_catalog()
        for output, owner in REQUIRED_OUTPUT_OWNERS.items():
            assert catalog.definition(owner).owns.count(output) == 1

    def test_qa_terminal_broadcast_declared(self) -> None:
        catalog = load_role_catalog()
        assert catalog.definition(Role.QA).terminal_broadcast is True
        assert catalog.definition(Role.CODER).terminal_broadcast is False

    def test_receive_modes_match_dec_six_008(self) -> None:
        catalog = load_role_catalog()
        expected = {
            Role.SPECIFIER: ("task", "forward-only"),
            Role.CODER: ("task", "forward-only"),
            Role.CLEANER: ("batch", "back-one"),
            Role.ARCHITECT: ("batch", "back-all"),
            Role.HARDENDER: ("batch", "forward-only"),
            Role.QA: ("batch", "back-all"),
        }
        for role, (mode, propagation) in expected.items():
            definition = catalog.definition(role)
            assert definition.receive_mode.value == mode, role
            assert definition.propagation.value == propagation, role

    def test_ownership_vacancy_fails_closed(self, tmp_path) -> None:
        catalog = load_role_catalog()
        # Simulate a role definition losing a required output.
        data = json.loads(
            json.dumps(catalog.definition(Role.QA).to_dict())
        )
        data["owns"] = []
        with pytest.raises(EnvelopeInvalid, match="executable_qa_automation"):
            from sixpack.model import Propagation, ReceiveMode
            from sixpack.roles import RoleCatalog, RoleDefinition

            RoleCatalog(
                {
                    **{role: catalog.definition(role) for role in Role.ordered()},
                    Role.QA: RoleDefinition(
                        role=Role.QA,
                        owns=list(data["owns"]),
                        does_not_own=list(data["does_not_own"]),
                        required_inputs=list(data["required_inputs"]),
                        permitted_mutations=list(data["permitted_mutations"]),
                        required_checks=list(data["required_checks"]),
                        handoff_target=data["handoff_target"],
                        failure_output=data["failure_output"],
                        done_criteria=list(data["done_criteria"]),
                        receive_mode=ReceiveMode(data["receive_mode"]),
                        propagation=Propagation(data["propagation"]),
                        terminal_broadcast=bool(data["terminal_broadcast"]),
                    ),
                }
            ).validate()

    def test_role_overreach_fails_closed(self) -> None:
        from sixpack.model import Propagation, ReceiveMode
        from sixpack.roles import RoleCatalog, RoleDefinition

        catalog = load_role_catalog()
        hijacked = RoleDefinition(
            role=Role.CLEANER,
            owns=["cleanup_and_local_quality_checks", "architecture_and_property_tests"],
            does_not_own=list(catalog.definition(Role.CLEANER).does_not_own),
            required_inputs=["x"],
            permitted_mutations=["x"],
            required_checks=["x"],
            handoff_target="architect",
            failure_output="x",
            done_criteria=["x"],
            receive_mode=ReceiveMode.BATCH,
            propagation=Propagation.BACK_ONE,
        )
        with pytest.raises(EnvelopeInvalid, match="architecture_and_property_tests"):
            RoleCatalog(
                {
                    **{role: catalog.definition(role) for role in Role.ordered()},
                    Role.CLEANER: hijacked,
                }
            ).validate()

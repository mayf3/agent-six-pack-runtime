"""B-QA-01: one test table, two paths — raw receipt vs normalized receipt.

Path A feeds the ORIGINAL raw final-QA results straight into the
independent TerminalVerifier. Path B first normalizes them through
``validate_qa_machine`` (the runner path) and then feeds the normalized
receipt to the same verifier. Every invalid input must fail to pass on
BOTH paths; the valid input must pass on both; a truthful FAIL/BLOCKED is
allowed as history but never as delivery-passed.
"""

from __future__ import annotations

from sixpack.qa_gate import (
    canonical_qa_required_checks,
    validate_qa_machine,
)
from sixpack.verifier import TerminalVerifier
from tests.conftest import make_repo, make_runtime, seed_task

ENTRYPOINTS = ["qa.verify.sh"]
BINDINGS = [{"path": "sixpack-artifacts/qa.verify.sh", "blob_sha": "c" * 40, "size": 30}]
TERMINAL_HEAD = "a" * 40
TERMINAL_TREE = "b" * 40


def canonical_pass_checks() -> list[dict[str, str]]:
    return [{"name": name, "verdict": "PASS"} for name in canonical_qa_required_checks()]


def canonical_checks_with_single(verdict: str, target: str) -> list[dict[str, str]]:
    return [
        {"name": name, "verdict": verdict if name == target else "PASS"}
        for name in canonical_qa_required_checks()
    ]


def raw_results(
    terminal_head: str,
    terminal_tree: str,
    entrypoints: list[str],
    bindings: list[dict[str, object]],
    **overrides: object,
) -> dict[str, object]:
    results: dict[str, object] = {
        "qa_verdict": "PASS",
        "qa_required_checks": canonical_pass_checks(),
        "qa_blockers": [],
        "qa_certified_head": terminal_head,
        "qa_certified_tree": terminal_tree,
        "qa_automation_entrypoints": list(entrypoints),
        "qa_automation_bindings": [dict(b) for b in bindings],
    }
    results.update(overrides)
    return results


def build_cases(
    terminal_head: str,
    terminal_tree: str,
    entrypoints: list[str],
    bindings: list[dict[str, object]],
) -> list[tuple[str, dict[str, object], bool]]:
    """The shared test table: (case name, raw results, should_pass)."""
    cases: list[tuple[str, dict[str, object], bool]] = []
    for name in canonical_qa_required_checks():
        cases.append(
            (
                f"canonical check FAIL: {name}",
                raw_results(
                    terminal_head,
                    terminal_tree,
                    entrypoints,
                    bindings,
                    qa_required_checks=canonical_checks_with_single("FAIL", name),
                ),
                False,
            )
        )
        cases.append(
            (
                f"canonical check NOT_EXECUTED: {name}",
                raw_results(
                    terminal_head,
                    terminal_tree,
                    entrypoints,
                    bindings,
                    qa_required_checks=canonical_checks_with_single("NOT_EXECUTED", name),
                ),
                False,
            )
        )
    cases.append(
        (
            "valid but non-empty blockers",
            raw_results(
                terminal_head,
                terminal_tree,
                entrypoints,
                bindings,
                qa_blockers=["database unavailable"],
            ),
            False,
        )
    )
    cases.append(
        (
            "wrong certified head",
            raw_results(
                terminal_head, terminal_tree, entrypoints, bindings,
                qa_certified_head="c" * 40,
            ),
            False,
        )
    )
    cases.append(
        (
            "wrong certified tree",
            raw_results(
                terminal_head, terminal_tree, entrypoints, bindings,
                qa_certified_tree="d" * 40,
            ),
            False,
        )
    )
    cases.append(
        ("all valid", raw_results(terminal_head, terminal_tree, entrypoints, bindings), True)
    )
    return cases


def _terminal_fixture(tmp_path: object):
    repo = make_repo(tmp_path / "dp-repo")  # type: ignore[operator]
    rt = make_runtime(tmp_path / "dp-ws", repo)  # type: ignore[operator]
    seed_task(rt, repo)
    rt.controller.admit("task-1")
    instance = rt.ledger.workflow("task-1")
    instance.done_when_met = True
    rt.ledger.save()
    rt.controller.drive("task-1")
    rt.controller.converge_terminal("task-1")
    instance = rt.ledger.workflow("task-1")
    qa_receipt = next(r for r in reversed(instance.receipts) if r["role"] == "qa")
    return rt, instance.terminal_head, instance.terminal_tree, qa_receipt


def _replace_qa_results(rt, results: dict[str, object]) -> None:
    instance = rt.ledger.workflow("task-1")
    for receipt in instance.receipts:
        if receipt["role"] == "qa":
            receipt["results"] = dict(results)
    rt.ledger.save()


class TestDualPathSameTable:
    def test_same_table_both_paths(self, tmp_path) -> None:
        # The SAME table of cases is instantiated against each path's own
        # real terminal candidate and its REAL runtime-generated automation
        # bindings (candidate and blob SHAs differ per fixture), so both
        # paths exercise identical mutation semantics.
        rt_a, head_a, tree_a, qa_receipt_a = _terminal_fixture(tmp_path / "path-a")
        rt_b, head_b, tree_b, qa_receipt_b = _terminal_fixture(tmp_path / "path-b")
        entrypoints_a = list(
            qa_receipt_a["results"]["qa_automation_entrypoints"]  # type: ignore[index]
        )
        bindings_a = list(
            qa_receipt_a["results"]["qa_automation_bindings"]  # type: ignore[index]
        )
        entrypoints_b = list(
            qa_receipt_b["results"]["qa_automation_entrypoints"]  # type: ignore[index]
        )
        bindings_b = list(
            qa_receipt_b["results"]["qa_automation_bindings"]  # type: ignore[index]
        )
        cases_a = build_cases(head_a, tree_a, entrypoints_a, bindings_a)
        cases_b = build_cases(head_b, tree_b, entrypoints_b, bindings_b)
        assert [c[0] for c in cases_a] == [c[0] for c in cases_b]

        for (case_name, raw_a, should_pass), (_, raw_b, _) in zip(
            cases_a, cases_b, strict=True
        ):
            # Path A: the raw receipt goes straight to the verifier.
            _replace_qa_results(rt_a, dict(raw_a))
            report_a = TerminalVerifier(rt_a.ledger).verify("task-1")

            # Path B: normalize first (the runner path), then verify.
            normalized = validate_qa_machine(
                dict(raw_b),
                head_b,
                tree_b,
                qa_automation_entrypoints=list(entrypoints_b),
                qa_automation_bindings=[dict(b) for b in bindings_b],
            )
            _replace_qa_results(rt_b, dict(normalized))
            report_b = TerminalVerifier(rt_b.ledger).verify("task-1")

            if should_pass:
                assert report_a.verdict == "PASS", (case_name, report_a.failures)
                assert report_b.verdict == "PASS", (case_name, report_b.failures)
            else:
                assert report_a.verdict == "FAIL", (case_name, report_a.failures)
                assert report_b.verdict == "FAIL", (case_name, report_b.failures)


class TestOriginalBlockersPreserved:
    def test_valid_original_blockers_survive_normalization(self) -> None:
        target = "final CRAP/DRY checks on the terminal candidate"
        raw = raw_results(
            TERMINAL_HEAD,
            TERMINAL_TREE,
            ENTRYPOINTS,
            BINDINGS,
            qa_verdict="FAIL",
            qa_required_checks=canonical_checks_with_single("FAIL", target),
            qa_blockers=["database unavailable during E2E"],
        )
        normalized = validate_qa_machine(
            raw,
            TERMINAL_HEAD,
            TERMINAL_TREE,
            qa_automation_entrypoints=list(ENTRYPOINTS),
            qa_automation_bindings=[dict(b) for b in BINDINGS],
        )
        assert normalized["qa_verdict"] == "FAIL"  # truthful history preserved
        # Original blocker kept, validator error merged alongside it.
        assert "database unavailable during E2E" in normalized["qa_blockers"]
        assert any(
            "required checks not PASS" in blocker
            for blocker in normalized["qa_blockers"]
        )


class TestEchoMismatchNotErased:
    def test_wrong_echo_preserved_and_downgraded(self) -> None:
        raw = raw_results(
            TERMINAL_HEAD, TERMINAL_TREE, ENTRYPOINTS, BINDINGS,
            qa_certified_head="c" * 40,
        )
        normalized = validate_qa_machine(
            raw,
            TERMINAL_HEAD,
            TERMINAL_TREE,
            qa_automation_entrypoints=list(ENTRYPOINTS),
            qa_automation_bindings=[dict(b) for b in BINDINGS],
        )
        # The original declaration survives verbatim (not overwritten).
        assert normalized["qa_certified_head"] == "c" * 40
        assert normalized["qa_verdict"] == "BLOCKED"
        assert any(
            "QA_TERMINAL_CANDIDATE_UNCHANGED" in blocker
            for blocker in normalized["qa_blockers"]
        )

    def test_wrong_echo_still_rejected_by_verifier(self, tmp_path) -> None:
        rt, head, tree, _ = _terminal_fixture(tmp_path / "echo-ws")
        raw = raw_results(head, tree, ENTRYPOINTS, BINDINGS, qa_certified_head="c" * 40)
        normalized = validate_qa_machine(
            raw, head, tree,
            qa_automation_entrypoints=list(ENTRYPOINTS),
            qa_automation_bindings=[dict(b) for b in BINDINGS],
        )
        _replace_qa_results(rt, dict(normalized))
        report = TerminalVerifier(rt.ledger).verify("task-1")
        assert report.verdict == "FAIL"
        assert any(
            "QA_TERMINAL_CANDIDATE_UNCHANGED" in failure for failure in report.failures
        )

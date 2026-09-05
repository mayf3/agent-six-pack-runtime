"""Shared final-QA gate rules — single source of truth.

The RoleRunner normalizes a raw QA result through :func:`validate_qa_machine`;
the independent TerminalVerifier re-checks the STORED receipt through
:func:`qa_rule_failures`. Both apply the exact same rules, so a runner that
fails to downgrade a fake PASS can never create a terminal false-pass: the
verifier re-derives every rule violation from the stored receipt itself.

The module also owns the executable-QA-automation gate: the pre-commit
worktree check (:func:`worktree_automation_gate`) and the certified-tree
binding check (:func:`automation_tree_binding_failures`) that proves the
declared automation exists in the exact certified Git tree.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import cast

from .gitx import WorktreeManager, git
from .model import Role
from .roles import load_role_catalog

QA_PASS = "PASS"
QA_FAIL = "FAIL"
QA_BLOCKED = "BLOCKED"
QA_CHECK_VERDICTS = (QA_PASS, QA_FAIL, "NOT_EXECUTED")
AUTOMATION_MANIFEST_PATH = "sixpack-artifacts/qa.automation.json"
AUTOMATION_DIR = "sixpack-artifacts"

_CANONICAL_CHECKS_CACHE: list[str] | None = None


def canonical_qa_required_checks() -> list[str]:
    """The closed canonical required-check set, pinned by the QA role def."""
    global _CANONICAL_CHECKS_CACHE
    if _CANONICAL_CHECKS_CACHE is None:
        _CANONICAL_CHECKS_CACHE = list(
            load_role_catalog().definition(Role.QA).required_checks
        )
    return list(_CANONICAL_CHECKS_CACHE)


def _require_list_of_str(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    for item in value:
        if not isinstance(item, str):
            return None
    return [str(item) for item in value]


def qa_rule_failures(
    results: dict[str, object], certified_head: str, certified_tree: str
) -> list[str]:
    """Integrity-rule violations of a STORED final-QA result.

    Checks the strict schema (``qa_blockers`` list[str], well-formed check
    entries), the closed canonical required-check set (no missing check, no
    duplicate, no arbitrary substitute), the certified-coordinate binding,
    and the verdict-field validity. Outcome quality (verdict == PASS) is
    deliberately NOT a rule here -- the verifier applies it separately --
    so a truthful FAIL receipt stays schema-clean while a fake PASS cannot
    hide behind runner preprocessing.
    """
    failures: list[str] = []

    verdict = str(results.get("qa_verdict", "")).upper()
    if verdict not in (QA_PASS, QA_FAIL, QA_BLOCKED):
        failures.append(f"invalid qa_verdict: {results.get('qa_verdict')!r}")

    raw_checks = results.get("qa_required_checks")
    if not isinstance(raw_checks, list) or not raw_checks:
        failures.append("qa_required_checks missing or empty (required checks not executed)")
    else:
        seen: dict[str, str] = {}
        for check in raw_checks:
            if not isinstance(check, dict):
                failures.append(f"malformed required check entry: {check!r}")
                continue
            name = str(check.get("name", ""))
            check_verdict = str(check.get("verdict", "")).upper()
            if check_verdict not in QA_CHECK_VERDICTS:
                failures.append(
                    f"required check {name!r} has invalid verdict {check_verdict!r}"
                )
                continue
            if name in seen:
                failures.append(
                    f"duplicate required check {name!r}: the required set is "
                    "closed and a duplicate replaces nothing"
                )
                continue
            seen[name] = check_verdict
        canonical = canonical_qa_required_checks()
        missing = [name for name in canonical if name not in seen]
        extras = [name for name in seen if name not in canonical]
        if missing:
            failures.append(f"missing canonical required checks: {missing}")
        if extras:
            failures.append(
                f"arbitrary substitute checks outside the canonical set: {extras}"
            )

    stated_blockers = results.get("qa_blockers", "__missing__")
    if stated_blockers == "__missing__" or stated_blockers is None:
        failures.append("qa_blockers missing/null (schema requires list[str])")
    else:
        valid = _require_list_of_str(stated_blockers)
        if valid is None:
            failures.append(
                f"qa_blockers must be a list[str], got {type(stated_blockers).__name__}"
            )

    cert_head = str(results.get("qa_certified_head", ""))
    cert_tree = str(results.get("qa_certified_tree", ""))
    # The QA's ORIGINAL declaration is preserved verbatim in the receipt and
    # compared against the actual candidate here. A mismatch invalidates any
    # PASS claim; the runtime must not erase it by overwriting coordinates.
    if cert_head != certified_head:
        failures.append(
            f"QA_TERMINAL_CANDIDATE_UNCHANGED = NO: certified head "
            f"{cert_head[:12] or 'missing'} != actual candidate head "
            f"{certified_head[:12]}"
        )
    if cert_tree != certified_tree:
        failures.append(
            f"QA_RECEIPT_BINDS_TERMINAL_TREE = NO: certified tree "
            f"{cert_tree[:12] or 'missing'} != actual candidate tree "
            f"{certified_tree[:12]}"
        )

    entrypoints = _require_list_of_str(results.get("qa_automation_entrypoints"))
    if not entrypoints:
        failures.append(
            "EXECUTABLE_QA_AUTOMATION evidence missing from the final QA "
            "receipt (report-only output cannot satisfy the QA required output)"
        )
    bindings = results.get("qa_automation_bindings")
    if not isinstance(bindings, list) or not bindings:
        failures.append(
            "QA_AUTOMATION_TREE_BINDING missing: the receipt must bind each "
            "declared automation entrypoint to its blob in the certified tree"
        )
    else:
        for binding in bindings:
            if not isinstance(binding, dict):
                failures.append(f"malformed automation binding: {binding!r}")
    return failures


def qa_pass_eligibility_failures(
    results: dict[str, object], certified_head: str, certified_tree: str
) -> list[str]:
    """The FULL PASS-eligibility judgment, shared by runner and verifier.

    A final-QA receipt may claim PASS only when ALL of these hold:

    - format is legal (schema, closed canonical check set, verdict field);
    - the canonical required-check set is complete and every required
      check verdict is PASS;
    - ``qa_blockers`` is empty;
    - the QA-certified head/tree equal the actual candidate head/tree;
    - the committed automation binding is present and valid at the schema
      level (the Git-tree blob match is re-checked separately by the
      caller, which owns repository access).
    """
    failures = qa_rule_failures(results, certified_head, certified_tree)

    verdict = str(results.get("qa_verdict", "")).upper()
    if verdict != QA_PASS:
        failures.append(f"QA_VERDICT = {verdict or 'MISSING'} (must be PASS)")

    raw_checks = results.get("qa_required_checks")
    if isinstance(raw_checks, list):
        failed = [
            str(cast(dict[str, object], check).get("name"))
            for check in raw_checks
            if isinstance(check, dict)
            and str(check.get("verdict", "")).upper() != QA_PASS
        ]
        if failed:
            failures.append(f"required checks not PASS: {failed}")

    stated_blockers = _require_list_of_str(results.get("qa_blockers"))
    if stated_blockers:
        # Open blockers mean the candidate is not delivery-passed, whatever
        # the stated verdict says; a PASS claim with open blockers is a
        # fake PASS and is downgraded by validate_qa_machine.
        failures.append(f"QA_BLOCKERS non-empty: {stated_blockers}")

    return failures


def validate_qa_machine(
    qa_result: dict[str, object] | None,
    certified_head: str,
    certified_tree: str,
    qa_automation_entrypoints: list[str] | None = None,
    qa_automation_bindings: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Runner-side normalization of a raw final-QA result.

    Contract (B-QA-01):

    - The QA's ORIGINAL valid blockers are preserved and merged with the
      validator-generated errors; normalization never wipes them.
    - The QA's original certified head/tree echo is preserved verbatim so
      the TerminalVerifier can independently re-detect a mismatch; the
      runtime does NOT overwrite the echo to erase the rejection. The
      actual candidate coordinates live in the receipt's output_head/
      output_tree, keeping declaration and fact distinguishable.
    - The full shared PASS-eligibility judgment decides the downgrade: a
      PASS claim with any eligibility failure becomes BLOCKED. A truthful
      FAIL/BLOCKED verdict with schema-valid evidence is preserved as
      history and can never count as delivery-passed.
    - The runtime-generated automation bindings are authoritative: any
      automation keys in the QA-returned JSON are stripped and replaced
      with the helper-computed certified-tree bindings.
    """
    blockers: list[str] = []
    raw = dict(qa_result) if qa_result is not None else {"qa_verdict": QA_BLOCKED}
    if qa_result is None:
        blockers.append("no machine QA verdict (QA_FINAL_JSON / qa_result) produced")

    result = dict(raw)
    result.pop("qa_automation_entrypoints", None)
    result.pop("qa_automation_bindings", None)
    if qa_automation_entrypoints is not None:
        result["qa_automation_entrypoints"] = list(qa_automation_entrypoints)
    if qa_automation_bindings is not None:
        result["qa_automation_bindings"] = [
            dict(binding) for binding in qa_automation_bindings
        ]
    # The QA's original echo is preserved, never overwritten.

    # Full shared PASS-eligibility judgment: produces every validator error
    # (integrity + outcome). The QA's original valid blockers are merged
    # with these; nothing is wiped during normalization.
    eligibility = qa_pass_eligibility_failures(result, certified_head, certified_tree)

    stated = _require_list_of_str(result.get("qa_blockers"))
    if stated is not None:
        blockers.extend(item for item in stated if item not in blockers)

    verdict = str(result.get("qa_verdict", "")).upper()
    if verdict not in (QA_PASS, QA_FAIL, QA_BLOCKED):
        eligibility.append(f"invalid qa_verdict: {result.get('qa_verdict')!r}")
        verdict = QA_BLOCKED
    if verdict == QA_PASS and eligibility:
        # Fake PASS: any eligibility failure invalidates the PASS claim.
        verdict = QA_BLOCKED
    blockers.extend(item for item in eligibility if item not in blockers)

    result["qa_verdict"] = verdict
    result["qa_blockers"] = blockers
    return result


def worktree_automation_gate(worktree: Path) -> tuple[list[str] | None, str | None]:
    """Pre-commit gate: the declared automation exists and is executable.

    Rejects report-only output, out-of-bounds paths, external or in-tree
    symlinks, and git-ignored (uncommittable) entrypoints. Returns
    ``(entrypoints, None)`` on success or ``(None, error)``.
    """
    manifest_path = worktree / AUTOMATION_MANIFEST_PATH
    if manifest_path.is_symlink():
        return None, "qa.automation.json is a symlink; external indirection is forbidden"
    if not manifest_path.exists():
        return None, (
            f"executable QA automation missing: {AUTOMATION_MANIFEST_PATH} not "
            "found; report-only output cannot satisfy the QA required output"
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return None, f"qa.automation.json is not valid JSON: {exc}"
    entrypoints = manifest.get("entrypoints") if isinstance(manifest, dict) else None
    if not isinstance(entrypoints, list) or not entrypoints:
        return None, "qa.automation.json declares no entrypoints"
    for entry in entrypoints:
        error = _entrypoint_path_failure(entry)
        if error is not None:
            return None, error
        assert isinstance(entry, str)
        script = worktree / AUTOMATION_DIR / entry
        if script.is_symlink():
            return None, (
                f"automation entrypoint is a symlink: {entry}; external "
                "indirection is forbidden"
            )
        if not script.exists():
            return None, f"declared automation entrypoint does not exist: {entry}"
        content = script.read_bytes()
        if not content.strip():
            return None, f"automation entrypoint is empty: {entry}"
        if not (os.access(script, os.X_OK) or content.startswith(b"#!")):
            return None, (
                f"automation entrypoint has no executable signature (exec bit "
                f"or shebang): {entry}"
            )
        if subprocess_ignore_check(worktree, f"{AUTOMATION_DIR}/{entry}"):
            return None, (
                f"automation entrypoint is git-ignored and can never be "
                f"committed into the certified tree: {entry}"
            )
    return [str(entry) for entry in entrypoints], None


def subprocess_ignore_check(worktree: Path, path: str) -> bool:
    """True when ``path`` is git-ignored in the worktree repository."""

    result = subprocess.run(
        ["git", "check-ignore", "--quiet", path],
        cwd=str(worktree),
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _entrypoint_path_failure(entry: object) -> str | None:
    if not isinstance(entry, str) or not entry.strip():
        return f"malformed automation entrypoint: {entry!r}"
    entry = entry.strip()
    if entry.startswith("/") or entry.startswith("\\"):
        return f"automation entrypoint must be relative: {entry}"
    if ".." in entry.split("/"):
        return f"automation entrypoint escapes sixpack-artifacts/: {entry}"
    if "/" in entry.strip("/") :
        return (
            f"automation entrypoint must live directly under "
            f"{AUTOMATION_DIR}/: {entry}"
        )
    if entry in (".", ".."):
        return f"malformed automation entrypoint: {entry}"
    return None


def automation_bindings_from_tree(
    manager: WorktreeManager, tree: str
) -> tuple[list[dict[str, object]] | None, list[str] | None]:
    """Post-commit binding: read the manifest + entrypoints FROM the tree.

    Returns ``(bindings, None)`` where each binding is
    ``{"path": ..., "blob_sha": ..., "size": ...}``, or ``(None, failures)``
    with one failure per violated requirement.
    """
    failures: list[str] = []
    manifest_entry = _tree_entry(manager, tree, AUTOMATION_MANIFEST_PATH)
    if manifest_entry is None:
        return None, [
            f"{AUTOMATION_MANIFEST_PATH} is not present in the certified tree"
        ]
    mode, blob_sha = manifest_entry
    if mode == "120000":
        failures.append(f"{AUTOMATION_MANIFEST_PATH} is a symlink in the certified tree")
        return None, failures
    manifest_raw = git("cat-file", "blob", blob_sha, cwd=manager.repo_path, check=False)
    try:
        manifest = json.loads(manifest_raw)
    except ValueError as exc:
        failures.append(f"certified qa.automation.json is not valid JSON: {exc}")
        return None, failures
    entrypoints = manifest.get("entrypoints") if isinstance(manifest, dict) else None
    if not isinstance(entrypoints, list) or not entrypoints:
        failures.append("certified qa.automation.json declares no entrypoints")
        return None, failures

    bindings: list[dict[str, object]] = []
    for entry in entrypoints:
        path_failure = _entrypoint_path_failure(entry)
        if path_failure is not None:
            failures.append(path_failure)
            continue
        assert isinstance(entry, str)
        path = f"{AUTOMATION_DIR}/{entry}"
        tree_entry = _tree_entry(manager, tree, path)
        if tree_entry is None:
            failures.append(
                f"declared automation entrypoint is not present in the "
                f"certified tree (untracked or ignored): {entry}"
            )
            continue
        entry_mode, entry_blob = tree_entry
        if entry_mode == "120000":
            failures.append(
                f"automation entrypoint is a symlink in the certified tree: {entry}"
            )
            continue
        blob = git("cat-file", "blob", entry_blob, cwd=manager.repo_path, check=False)
        if not blob.strip():
            failures.append(f"automation entrypoint is empty: {entry}")
            continue
        if entry_mode != "100755" and not blob.startswith("#!"):
            failures.append(
                f"automation entrypoint has no executable signature in the "
                f"certified tree (mode {entry_mode}, no shebang): {entry}"
            )
            continue
        bindings.append(
            {"path": path, "blob_sha": entry_blob, "size": len(blob.encode("utf-8"))}
        )
    if failures:
        return None, failures
    return bindings, None


def automation_tree_binding_failures(
    manager: WorktreeManager, tree: str, bindings: list[object]
) -> list[str]:
    """Independent verifier re-check: stored bindings vs the exact tree.

    Re-derives the bindings from ``tree`` and compares them with the
    receipt's stored binding list. Any drift, missing entrypoint, symlink,
    or out-of-bounds path is a failure.
    """
    failures: list[str] = []
    stored: dict[str, str] = {}
    for binding in bindings:
        if not isinstance(binding, dict):
            failures.append(f"malformed automation binding: {binding!r}")
            continue
        path = str(binding.get("path", ""))
        blob_sha = str(binding.get("blob_sha", ""))
        path_failure = _entrypoint_path_failure(
            path.removeprefix(AUTOMATION_DIR + "/")
        )
        if path_failure is not None:
            failures.append(f"automation binding path invalid: {path}")
            continue
        if len(blob_sha) != 40 or any(c not in "0123456789abcdef" for c in blob_sha):
            failures.append(f"automation binding blob_sha invalid for {path}")
            continue
        stored[path] = blob_sha
    if not stored:
        failures.append("no valid automation bindings stored in the receipt")
        return failures

    expected, bind_failures = automation_bindings_from_tree(manager, tree)
    if bind_failures:
        failures.extend(f"certified tree binding failure: {item}" for item in bind_failures)
        return failures
    assert expected is not None
    expected_map = {
        str(binding["path"]): str(binding["blob_sha"]) for binding in expected
    }
    for path, blob_sha in expected_map.items():
        if path not in stored:
            failures.append(f"automation binding missing from receipt: {path}")
        elif stored[path] != blob_sha:
            failures.append(
                f"automation binding drift for {path}: receipt {stored[path][:12]} "
                f"!= certified tree {blob_sha[:12]}"
            )
    for path in stored:
        if path not in expected_map:
            failures.append(
                f"automation binding for {path} is not declared in the "
                "certified manifest"
            )
    return failures


def _tree_entry(
    manager: WorktreeManager, tree: str, path: str
) -> tuple[str, str] | None:
    """Return (mode, blob_sha) for ``path`` inside ``tree``, else None."""
    out = git("ls-tree", tree, "--", path, cwd=manager.repo_path, check=False)
    for line in out.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[1] == path:
            meta = parts[0].split()
            if len(meta) >= 3 and meta[1] == "blob":
                return meta[0], meta[2]
    return None

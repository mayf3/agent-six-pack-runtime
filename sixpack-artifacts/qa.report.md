# QA Report: `canary-version-1`

## Verdict

**QA PASS** for the unchanged terminal product candidate.

- Candidate head: `dbcd1666d41a542bcfb696fd7f227043d0779985`
- Candidate tree: `947d321b3fa08c7fd1045b4fa038863178865ccf`
- Accepted governance revision: `fcd417ba608bafcc8a1160f3e95f8c43cb2212d8`
- Runtime version: `0.1.0`
- Product-code changes made by QA: none
- QA-owned output added: this final QA report only

This receipt certifies the product bytes at the head/tree above. It does not
claim Owner acceptance, merge authority, deployment, or post-commit terminal
convergence.

## Public-boundary verification

The documented procedure was executed through the environment's installed
`sixpack` console entry point with this worktree's `src` directory on
`PYTHONPATH`.

- `sixpack version`: exit `0`.
- Standard output: exactly one 76-byte line (including the final newline):
  `sixpack-runtime 0.1.0 + governance fcd417ba608bafcc8a1160f3e95f8c43cb2212d8`
- Standard error: empty.
- A fresh empty working directory remained empty after invocation.
- `sixpack versions`: non-zero exit and empty standard output.
- `sixpack version --unknown`: non-zero exit and empty standard output.

The task-prescribed regression command passed all 87 tests:

```text
PYTHONPATH=<worktree>/src /Users/yanfenma/workspace/project/agent-six-pack-runtime/.venv/bin/python -m pytest tests/ -q
........................................................................ [ 82%]
...............                                                          [100%]
```

The focused version suite passed 9 tests under Python's standard-library line
tracer. The trace executed the metadata import, `cmd_version` body, parser
construction, and `version` handler binding.

## Terminal quality checks

- Ruff over `src` and `tests`: PASS.
- Mypy strict over all 13 source files: PASS.
- `git diff --check`: PASS.
- CRAP: `cmd_version` and `build_parser` each have cyclomatic complexity 1 and
  100% focused execution, yielding `CRAP = 1.0`, below the repository's
  changed-file default maximum of 10.
- DRY: the production version-output template occurs once. The handler reads
  `__version__` and `GOVERNANCE_SOURCE_COMMIT`; it does not duplicate their
  values as display literals.

## Handoff and manifest consistency

The specifier, coder, cleaner, architect, and hardender stage commits are all
linear ancestors of the candidate head. The current source and test hashes
match the cleaner/hardener handoff evidence:

- `src/sixpack/cli.py`: `f6797be6decf7413e32e3a168c53c2d9876727727c23de762455b520e0c2627d`
- `src/sixpack/__init__.py`: `d7e2b61e9e09bcde6da39e8a44a07a5448bfa645819373afd074b6795a03e9f1`
- `tests/test_cli_version.py`: `0baeb7cdf3005ee3c75b11505363fed2e730ea5669ca07c7c9bcce2c11c45f4a`
- `tests/acceptance/test_version_cli.py`: `d31f91e07781ea543db0adadfcef8a51c4680866695e444bf1b427df301cb381`
- `tests/test_version_hardening.py`: `bab87e8eb34a7aa967d25597ece61996f6c34a734b9d93036799dee358f2e3a0`

Distribution metadata, package metadata, generated workspace-manifest
authority entries, README authority, and the accepted behavior specification
agree on runtime `0.1.0` and governance revision
`fcd417ba608bafcc8a1160f3e95f8c43cb2212d8` where applicable.

## Limitations and handoff

- The human QA procedure uses a shell variable named `status`, which is
  read-only in the task's zsh environment. Its commands abort under literal
  zsh execution before reaching the product. The same procedure was therefore
  run under `/bin/bash`, where its documented syntax is valid. This is a
  procedure portability issue outside QA's ownership, not a product failure.
- The delivery ledger is not stored in this worktree. At this station, five
  upstream stage commits are visible; the delivery helper must commit this QA
  output as the sixth receipt and then run the target-bound terminal verifier.
  This report does not claim that post-commit receipt creation or terminal
  `verify PASS` has already occurred.

Handoff status: **ready for the delivery helper to create the QA receipt and
perform terminal verification against its resulting exact head/tree**.

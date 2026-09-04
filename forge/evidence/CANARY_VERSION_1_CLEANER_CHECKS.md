# `canary-version-1` Cleaner Checks

## Candidate binding

- Input coder head: `c0e29b4ecb61fad1e11da5ae560acb2f15ac2ea7`.
- `src/sixpack/cli.py`: `sha256:f6797be6decf7413e32e3a168c53c2d9876727727c23de762455b520e0c2627d`.
- `src/sixpack/__init__.py`: `sha256:d7e2b61e9e09bcde6da39e8a44a07a5448bfa645819373afd074b6795a03e9f1`.
- `tests/test_cli_version.py`: `sha256:0baeb7cdf3005ee3c75b11505363fed2e730ea5669ca07c7c9bcce2c11c45f4a`.
- `tests/acceptance/test_version_cli.py`: `sha256:d31f91e07781ea543db0adadfcef8a51c4680866695e444bf1b427df301cb381`.

The cleaner-only source change renames the unused `cmd_version` parser namespace
parameter to `_args`. This documents that the command has no argument or
workspace dependency and does not alter its call signature or behavior.

## Local quality results

- Required regression command: PASS, 83 tests.
- Focused version tests under standard-library `trace`: PASS, 5 tests.
- Changed executable lines: 6/6 executed (import, handler definition/body, and
  parser registration); focused changed-line coverage is 100%.
- Local CRAP check: `cmd_version` and `build_parser` each retain cyclomatic
  complexity 1 and have 100% focused coverage, so each has
  `CRAP = CC^2 * (1 - coverage)^3 + CC = 1.0`.
- Local DRY check: the version output template occurs once in production; the
  handler references `__version__` and `GOVERNANCE_SOURCE_COMMIT` instead of
  adding metadata literals. No feature-local production duplication found.
- Ruff: PASS for `src` and `tests`.
- Mypy strict configuration: PASS for all 13 source files.
- `git diff --check`: PASS.
- Observable contract: PASS with exit 0, exact 76-byte stdout, empty stderr,
  and no files created in an empty working directory.

The environment does not contain `coverage`, `pytest-cov`, `radon`, `xenon`,
or `lizard`; the coverage and CRAP results above therefore use Python's
standard-library line tracer and the explicit CRAP formula. No dependency or
tool configuration was changed.

## Boundary

No behavior, unit-test contract, architecture/property test, mutation
hardening, executable QA automation, or final QA receipt was added. Six-receipt
and terminal-verifier completion remain owned by the downstream pipeline.

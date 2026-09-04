# `canary-version-1` Hardener Checks

## Candidate binding

- Input architect head: `5cd213782c99c56ea65351c6190c80f4cccaf3eb`.
- `src/sixpack/cli.py`: `sha256:f6797be6decf7413e32e3a168c53c2d9876727727c23de762455b520e0c2627d`.
- `src/sixpack/__init__.py`: `sha256:d7e2b61e9e09bcde6da39e8a44a07a5448bfa645819373afd074b6795a03e9f1`.
- `tests/test_version_hardening.py`: `sha256:bab87e8eb34a7aa967d25597ece61996f6c34a734b9d93036799dee358f2e3a0`.

The output candidate adds one mutation-hardening test and makes no production
change.

## Mutation assessment

No mutation engine is installed in the task environment (`mutmut`,
`cosmic-ray`, and equivalent coverage plugins are absent), so the affected
behavior was assessed with an explicit operator matrix and a direct mutation
probe.

| Mutation class | Killing assertion |
| --- | --- |
| Delete or alter the output call/template | Exact stdout assertions in the unit and process tests |
| Replace either displayed metadata reference with a literal or the other field | Distinct monkeypatched values in `test_version_uses_runtime_metadata` |
| Change the handler return from `0` | Unit return assertion and process exit assertion |
| Remove/rename the `version` parser or its handler binding | Successful `main(["version"])` and subprocess invocations |
| Accept an unknown command or option | The two parse-failure cases |
| Drift the packaged governance pin | `test_governance_revision_is_bound_to_accepted_authority` |

The governance-pin mutation was the sole contract-relevant survivor found in
the input candidate: expectations had derived their value from the same
constant. A direct probe replacing it with forty zeroes is now killed by the
new hardening test. No contract-relevant mutant remains in the assessed
surface.

Mutations limited to docstrings or argparse help prose are not killed. They are
non-executable or outside the accepted observable contract, which deliberately
specifies only successful output and parse-failure semantics. Those equivalent
or out-of-scope mutants are the recorded limitation of this manual assessment.

## Post-hardening checks

- Focused version suite: PASS, 9 tests.
- Required regression command: PASS, 87 tests.
- Ruff: PASS for `src` and `tests`.
- Mypy strict: PASS for all 13 source files.
- `git diff --check`: PASS.
- Standard-library tracing executed all 6 task-added production statements:
  metadata import, handler definition, output, return, parser creation, and
  handler binding.
- Post-hardening CRAP gate: PASS. `cmd_version`, `build_parser`, and the added
  hardening test each have cyclomatic complexity 1 and 100% exercised lines;
  `CRAP = CC^2 * (1 - coverage)^3 + CC = 1.0`, below the changed-file default
  maximum of 10.

Six-stage receipts, executable QA automation, terminal verification, and the
final QA receipt remain downstream QA/delivery-helper responsibilities and
were not produced or modified by this station.

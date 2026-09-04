# `canary-version-1` Human QA Procedure

## Purpose

Confirm the externally observable `sixpack version` behavior specified in
`CANARY_VERSION_1_BEHAVIOR_SPECIFICATION.md`. This is a human-readable
procedure; executable QA automation and the final QA receipt belong to later
pipeline stations.

## Preconditions

- Run from the isolated task worktree.
- Set `WORKTREE` to the absolute path of that worktree.
- Use the task-provided Python interpreter:
  `/Users/yanfenma/workspace/project/agent-six-pack-runtime/.venv/bin/python`.
- Use the `sixpack` console entry point from that same environment so the
  observed invocation is exactly `sixpack version`.
- Do not initialize a Six-Pack workspace for the version checks.

```bash
WORKTREE="$PWD"
PYTHON=/Users/yanfenma/workspace/project/agent-six-pack-runtime/.venv/bin/python
SIXPACK=/Users/yanfenma/workspace/project/agent-six-pack-runtime/.venv/bin/sixpack
EXPECTED='sixpack-runtime 0.1.0 + governance fcd417ba608bafcc8a1160f3e95f8c43cb2212d8'
```

## Check 1: exact successful output

Invoke the source-layout CLI, capturing stdout, stderr, and status separately:

```bash
stdout_file="$(mktemp)"
stderr_file="$(mktemp)"
PYTHONPATH="$WORKTREE/src" "$SIXPACK" version \
  >"$stdout_file" 2>"$stderr_file"
status=$?
```

Verify:

```bash
test "$status" -eq 0
test "$(wc -l <"$stdout_file" | tr -d ' ')" -eq 1
test "$(sed -n '1p' "$stdout_file")" = "$EXPECTED"
test "$(wc -c <"$stdout_file" | tr -d ' ')" -eq 76
test ! -s "$stderr_file"
```

Expected result: every assertion returns status `0`. The 76-byte assertion
includes the single trailing newline and detects extra whitespace or lines.

## Check 2: no workspace dependency or side effect

Run the command from a new empty directory and compare its contents before and
after:

```bash
empty_dir="$(mktemp -d)"
before="$(find "$empty_dir" -mindepth 1 -print)"
(
  cd "$empty_dir"
  PYTHONPATH="$WORKTREE/src" "$SIXPACK" version
) >"$stdout_file" 2>"$stderr_file"
status=$?
after="$(find "$empty_dir" -mindepth 1 -print)"

test "$status" -eq 0
test "$(sed -n '1p' "$stdout_file")" = "$EXPECTED"
test ! -s "$stderr_file"
test -z "$before"
test -z "$after"
```

Expected result: every assertion returns status `0`; the directory remains
empty.

## Check 3: invalid CLI inputs fail closed

For each invalid invocation, confirm a non-zero status and absence of the
successful line on stdout:

```bash
for args in 'versions' 'version --unknown'; do
  : >"$stdout_file"
  : >"$stderr_file"
  set +e
  PYTHONPATH="$WORKTREE/src" "$SIXPACK" $args \
    >"$stdout_file" 2>"$stderr_file"
  status=$?
  set -e
  test "$status" -ne 0
  test ! -s "$stdout_file"
done
```

Expected result: both invalid invocations satisfy both assertions. Parser
diagnostic text and its exact exit status are not acceptance surfaces for this
task.

## Check 4: full regression suite

Run the exact task-provided suite command:

```bash
PYTHONPATH="$WORKTREE/src" \
  /Users/yanfenma/workspace/project/agent-six-pack-runtime/.venv/bin/python \
  -m pytest tests/ -q
```

Expected result: pytest exits `0` with no failed or errored tests.

## Pipeline completion evidence

The QA station records final acceptance only after confirming all four checks
above against the unchanged terminal candidate. Separately confirm that the
delivery ledger contains one receipt for each of the six ordered stations and
that terminal verification for `canary-version-1` reports `PASS`. Those
receipts and the final QA receipt are not produced by this procedure or by the
specifier station.

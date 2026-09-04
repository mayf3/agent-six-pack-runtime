# `canary-version-1` Behavior Specification

## Authority and scope

- Task: `canary-version-1` / `TASK-ASR-001`.
- Accepted governance revision: `fcd417ba608bafcc8a1160f3e95f8c43cb2212d8`.
- Runtime version at this task revision: `0.1.0`.
- Owned surface: the externally observable behavior of the `sixpack version`
  CLI command.

This specification does not select an implementation mechanism and does not
change the meaning or behavior of any existing command.

## Deterministic behavior

Given the runtime package metadata at this task revision, invoking:

```text
sixpack version
```

MUST:

1. exit successfully with status `0`;
2. write exactly this single line to standard output, followed by one newline:

   ```text
   sixpack-runtime 0.1.0 + governance fcd417ba608bafcc8a1160f3e95f8c43cb2212d8
   ```

3. write nothing to standard error; and
4. require no workspace argument, initialized runtime workspace, network
   access, or repository state, and create or modify no files.

The displayed runtime version MUST be the runtime's declared version. The
displayed governance revision MUST be the pinned
`GOVERNANCE_SOURCE_COMMIT`. The command MUST display the full pinned revision,
not an abbreviated commit identifier.

## Failure cases

The task authority defines no command-specific runtime failure for the
no-argument `version` operation because both displayed values are packaged
runtime metadata.

The following inputs remain ordinary CLI parse failures and MUST NOT be
treated as successful version output:

- an unrecognized command such as `sixpack versions`;
- an unrecognized argument after the command, such as
  `sixpack version --unknown`.

For either parse failure, the process MUST return a non-zero status and MUST
NOT emit the successful version line on standard output. Diagnostic wording
and the exact non-zero status are inherited from the existing CLI parser and
are deliberately not expanded into a new product contract here.

## Acceptance criteria

The behavior is accepted for this station when all of the following are true:

- the exact successful invocation produces the exact stdout bytes specified
  above, with exit status `0` and empty stderr;
- the version and governance fields are sourced from the runtime's declared
  metadata and pinned governance constant rather than separately duplicated
  display literals;
- the command succeeds outside an initialized Six-Pack workspace and has no
  filesystem side effect;
- the two enumerated invalid invocations fail without emitting the successful
  line on stdout;
- all pre-existing tests pass under the task-provided source-layout command;
  and
- subsequent pipeline stations produce six receipts and terminal verification
  reports `PASS`, as required by the task record.


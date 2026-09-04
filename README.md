# agent-six-pack-runtime

Repository-agnostic, provider-agnostic, model-agnostic runtime for the
Six-Pack software-delivery profile:

```text
specifier -> coder -> cleaner -> architect -> hardender -> QA
```

Governing authority: `AGENT_SIX_PACK_DELIVERY_PROFILE_V1` (with
`AGENT_DEVELOPMENT_GOVERNANCE_V1` and `AGENT_OPERATIONAL_LAYER_V1`) at
`mayf3/agent-development-governance@fcd417ba608bafcc8a1160f3e95f8c43cb2212d8`.

This is not an agent kernel, a scheduler, or a message broker. It is the
six-station delivery machine: durable handoffs, the two-call audit gate,
isolated worktrees, immutable stage receipts, terminal convergence, and a
deterministic multi-repo host controller.

## Layout

```text
src/sixpack/
  model.py       roles, receive policy, semantic handoff envelope, receipts
  roles.py       role definition catalog + exactly-one ownership validation
  queue.py       durable inbox/outbox with helper-owned transitions + integrity
  audit.py       two-call AUDIT_REQUIRED challenge gate (CTR-SIX-013)
  ledger.py      durable task/workflow ledger, PREFLIGHT gate, receipt chain
  gitx.py        exact commit/tree verification, isolated worktrees, drift abort
  runner.py      RoleRunner + FakeAgentAdapter / ProcessAdapter
  controller.py  deterministic multi-repo host: registry, leases, admission,
                 night window, quiesce, recovery, terminal convergence
  verifier.py    terminal impact-and-coverage verification (CTR-SIX-020)
  cli.py         sixpack CLI
forge/           goal state, inventory, host spec (governance lane artifacts)
```

## Hard invariants

```text
MAX_IN_PROCESS_PER_ROLE = 1        MAX_ACTIVE_WRITE_TASKS_PER_REPO = 1
AUTO_ACCEPT = false                AUTO_MERGE = false                AUTO_DEPLOY = false
REMOTE_WRITE_DEFAULT = false       MAIN_CHECKOUT_WRITE = forbidden
SELF_SELECT_NEW_WORK = forbidden   BLIND_RETRY = forbidden
```

Every semantic handoff change re-enters `AUDIT_REQUIRED`. Terminal
completion is a priority-`00` broadcast from QA to exactly the other five
roles. QA can never certify bytes it modified. Verification never claims
merge-ready: independent review and Owner acceptance remain separate.

## Usage

```bash
pip install -e '.[dev]'
sixpack init ws
sixpack task ws --task-id t1 --repository demo --repo-path ./demo \
  --goal "..." --done-when "..." --source inventory/x --base-head <sha> \
  --authority-revision fcd417ba608bafcc8a1160f3e95f8c43cb2212d8 \
  --mandate-ref m1 --profile-selected
sixpack run ws --task-id t1                 # fake adapter by default
sixpack done ws --task-id t1                # record DONE_WHEN satisfied
sixpack converge ws --task-id t1            # merge-only terminal convergence
sixpack verify ws --task-id t1              # impact-and-coverage verdict
sixpack resume ws                           # crash recovery + tick
sixpack host ws status|scan|quiesce|recover
```

Night window (default 23:00 -> 09:00 local) is enforced by the controller;
`ws/host.json` may set `window_override` for deterministic operation.

## Tests

```bash
pytest        # 78 tests: positive H1->H6 convergence + full negative matrix
ruff check src tests
mypy src      # strict
```

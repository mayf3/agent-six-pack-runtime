---
spec_id: AGENT_MULTI_REPO_SIX_PACK_HOST_V1
status: proposed
spec_kind: implementation
authority_level: governing_spec
implementation_authority: contracts
scope:
  - agent-six-pack-runtime
  - multi-repo-governance-forge
  - shared-worker-pool-hosting
governed_by:
  - AGENT_DEVELOPMENT_GOVERNANCE_V1
  - AGENT_SIX_PACK_DELIVERY_PROFILE_V1
external_authorities: []
supersedes: []
superseded_by: null
owners:
  - mayf3
---

# AGENT_MULTI_REPO_SIX_PACK_HOST_V1

## 1. Goal

Define the narrowest long-lived host semantics that let the six accepted
Six-Pack roles operate as one shared worker pool across multiple
repositories under a deterministic controller.

```text
GOAL = one pool of six role workers serves many repositories without cross-repo write interference
SUCCESS_OUTCOME = bounded concurrency, preserved queues and leases across nights, and a controller that can never become a seventh reasoning agent
```

## 2. Scope and non-goals

### In scope

- repository registry with exact head snapshots and write authority flags;
- cross-repository task admission and leases with expiry and recovery;
- the two concurrency invariants `MAX_IN_PROCESS_PER_ROLE = 1` and
  `MAX_ACTIVE_WRITE_TASKS_PER_REPO = 1`;
- night-window control-plane phases `WINDOW_OPEN`, `ACTIVE`, `QUIESCE`,
  `WINDOW_CLOSED` and restart-safe quiesce;
- head-drift revalidation duties at host level;
- task <-> workflow instance <-> Forum thread mapping as a non-authoritative
  attention convention, with the durable ledger as the sole state of record;
- the fixed host policy: `AUTO_ACCEPT = false`, `AUTO_MERGE = false`,
  `AUTO_DEPLOY = false`, `REMOTE_WRITE_DEFAULT = false`,
  `MAIN_CHECKOUT_WRITE = forbidden`, `SELF_SELECT_NEW_WORK = forbidden`,
  `BLIND_RETRY = forbidden`.

### Out of scope

- redesigning the six Six-Pack roles, their order, receive modes, or
  ownership boundaries (owned by `AGENT_SIX_PACK_DELIVERY_PROFILE_V1`);
- changing authority routing, PREFLIGHT axes, or review rules (owned by
  `AGENT_DEVELOPMENT_GOVERNANCE_V1`);
- making the controller a reasoning agent, a Product Authority source, a
  Spec acceptor, a merger, or a deployer;
- a new message broker, generic scheduler, agent kernel, or dashboard;
- provider selection, model selection, or credentials (runtime config);
- admitting work that lacks mutation authority into any writing stage.

### Prior-art fidelity

The Six-Pack Profile leaves "queue storage technology and daemon language"
as implementation choices. This Spec decides only the *host semantics*
above that semantics; it does not re-decide anything the Profile already
owns.

## 3. Authority and dependencies

```text
AUTHORITY_ACTION = NEW
PRIMARY_PARENT_AUTHORITY = AGENT_SIX_PACK_DELIVERY_PROFILE_V1
CO_GOVERNING_AUTHORITY = AGENT_DEVELOPMENT_GOVERNANCE_V1
IMPLEMENTATION_AUTHORITY = contracts
EXTERNAL_AUTHORITIES = NONE
AUTHORITY_CONFLICT = NONE
```

The gap this Spec closes: no accepted authority decides how six
repository-agnostic role workers share themselves across repositories, how
concurrent writes to one repository are bounded, how work survives the
night-window boundary, or what the deterministic controller may and may not
do. `AGENT_DEVELOPMENT_GOVERNANCE_V1` explicitly places cross-repository
settings control outside its own scope, and
`AGENT_SIX_PACK_DELIVERY_PROFILE_V1` explicitly places runtime/queue
implementation outside its own scope.

## 4. Current State

### STATE-MRH-001 — Runtime V0 exists with single-repo semantics and host constraints encoded

- Subject: `mayf3/agent-six-pack-runtime` V0
- As of commit/artifact: `57019ec` (branch `v0/bootstrap`)
- Environment: local repository
- Observed at: 2026-09-04
- Projection: the runtime implements the full profile contract set with
  queue/audit/receipt/convergence mechanics and enforces the host policy
  constants, but the *authority* for multi-repo hosting semantics is not
  yet accepted; this Spec is its narrow closure.
- Basis: `OBS-MRH-001`, `OBS-MRH-002`

## 5. Observations

### OBS-MRH-001 — The accepted Profile owns single-task topology but not multi-repo hosting

- Subject: `AGENT_SIX_PACK_DELIVERY_PROFILE_V1` @ `fcd417ba608bafcc8a1160f3e95f8c43cb2212d8`
- Repository/source: `mayf3/agent-development-governance`
- Commit/artifact: exact revision above
- Environment: accepted Spec source
- Observed at: 2026-09-04
- Method: inspect Goals, Decisions, Contracts, and Open questions
- Result: CTR-SIX-012 requires durable queue state per task; open questions
  leave "queue storage technology and daemon language" open; nothing
  defines repository registries, cross-repo leases, admission windows, or
  per-repo write caps.
- Provenance: accepted Spec text at the exact revision

### OBS-MRH-002 — Governance V1 excludes cross-repository control platforms from its own scope

- Subject: `AGENT_DEVELOPMENT_GOVERNANCE_V1` @ same revision
- Repository/source: `mayf3/agent-development-governance`
- Commit/artifact: exact revision above
- Environment: accepted Spec source
- Observed at: 2026-09-04
- Method: inspect Scope and non-goals
- Result: governance routing is repository-local; a cross-repository host
  needs its own bounded authority.
- Provenance: accepted Spec text at the exact revision

### OBS-MRH-003 — Night GLM capacity is idle under per-repo single-task operation

- Subject: owner development fleet
- Environment: local machine, 2026-09-04 inventory
- Observed at: 2026-09-04
- Method: repository inventory across actively maintained repositories
  (dsh-agent-core, auth-service, agent-forum, svc-workflow, and others)
- Result: 30+ open governance artifacts exist across repositories while the
  night window (23:00-09:00 CST) runs at most one repo's single task; a
  shared pool is required to use the window.
- Provenance: `forge/inventory/` records in `mayf3/agent-six-pack-runtime`

## 6. Claims and assumptions

### CLM-MRH-001 — Host semantics are load-bearing and uncovered

- Support state: SUPPORTED
- Supported by evidence: `EVD-MRH-001`, `EVD-MRH-002`
- Contradicted by evidence: none known
- Uncertainty: exact lease TTL and window edges remain operational tuning.

### CLM-MRH-002 — A deterministic controller with enumerated powers is safe

- Support state: SUPPORTED
- Supported by evidence: `EVD-MRH-002`
- Contradicted by evidence: none known
- Uncertainty: none material; powers are closed by enumeration.

## 7. Evidence relations

### EVD-MRH-001 — Profile text does not decide host semantics

- Source observations: `OBS-MRH-001`
- Target: `CLM-MRH-001`
- Relation: SUPPORTS
- Bound coordinates: `AGENT_SIX_PACK_DELIVERY_PROFILE_V1` @ `fcd417ba608bafcc8a1160f3e95f8c43cb2212d8`
- Strength/sufficiency: decisive; the Profile's own open-questions section
  names the runtime layer as outside its decisions
- Limitations: none
- Provenance: accepted Spec source

### EVD-MRH-002 — Governance V1 excludes cross-repository platforms from its scope

- Source observations: `OBS-MRH-002`
- Target: `CLM-MRH-001`, `CLM-MRH-002`
- Relation: SUPPORTS
- Bound coordinates: `AGENT_DEVELOPMENT_GOVERNANCE_V1` @ `fcd417ba608bafcc8a1160f3e95f8c43cb2212d8`
- Strength/sufficiency: decisive for needing a separate bounded authority
- Limitations: none
- Provenance: accepted Spec source

## 8. Decisions

### DEC-MRH-001 — Repository registry with write authority flags

- Decision owner: repository owner
- Decision: the host maintains a registry binding repository name, local
  path, base branch, last-scanned exact head, and a `write_enabled` flag
  defaulting to false. Admission to any writing stage requires
  `write_enabled = true` plus a valid task PREFLIGHT record.
- Rejected alternatives: implicit registration by path scan; mutable
  registry without head snapshots.
- Reason: admission legality must be checkable without trusting task text.
- Owner decision remaining: NONE

### DEC-MRH-002 — Two concurrency invariants

- Decision owner: repository owner
- Decision: at most one in-process job per role across the whole pool, and
  at most one active write task per repository. Violations are refused
  mechanically, not queued around.
- Rejected alternatives: higher caps per repo; per-tenant pools.
- Reason: V0 proves the pipeline before scaling; caps are the drift guard.
- Owner decision remaining: NONE

### DEC-MRH-003 — Cross-repository leases with expiry and recovery

- Decision owner: repository owner
- Decision: admission creates a lease binding task, repository, role, and
  expiry. Crashed or expired leases are recovered by the controller's
  deterministic reconciliation; recovery never re-executes a recorded
  handoff (idempotency by handoff identity).
- Rejected alternatives: advisory locks without expiry; manual recovery.
- Reason: night windows end mid-task; recovery must be routine.
- Owner decision remaining: NONE

### DEC-MRH-004 — Night-window phases are control-plane only

- Decision owner: repository owner
- Decision: the controller exposes `WINDOW_OPEN`, `ACTIVE`, `QUIESCE`,
  `WINDOW_CLOSED`. Admission only in `WINDOW_OPEN`/`ACTIVE`; `QUIESCE`
  finishes bounded stages or saves restart-safe state; `WINDOW_CLOSED`
  runs no GLM work. Timers drive only these phases; role stations are
  woken by handoff completion, never by polling.
- Rejected alternatives: cron-polling agents; always-on operation.
- Reason: the window is a billing boundary, not a workflow primitive.
- Owner decision remaining: NONE

### DEC-MRH-005 — Controller powers are closed by enumeration

- Decision owner: repository owner
- Decision: the controller may scan, route, lease, wake, reconcile,
  quiesce, and recover. It must not create Product Authority, invent
  product tasks, accept Specs, merge to authority branches, deploy, or
  widen its own permissions. It is a deterministic program; any judgment
  call is routed to a role station or the Owner.
- Rejected alternatives: an intelligent scheduler agent.
- Reason: the host must not become a seventh reasoning agent.
- Owner decision remaining: NONE

### DEC-MRH-006 — Ledger is the state of record; Forum is attention only

- Decision owner: repository owner
- Decision: one task binds one stable task_id, one workflow instance, and
  (recommended) one Forum thread. Authoritative run state lives only in
  the durable machine-readable ledger; Forum content is discussion,
  clarification, stage summaries, and morning reports, and is never the
  sole authority store, task ledger, or handoff store.
- Rejected alternatives: Forum as primary store.
- Reason: chat is lossy; CTR-SIX-012 already requires durable queue state.
- Owner decision remaining: NONE

### DEC-MRH-007 — Fixed safety policy for the forge

- Decision owner: repository owner
- Decision: `AUTO_ACCEPT = false`, `AUTO_MERGE = false`,
  `AUTO_DEPLOY = false`, `REMOTE_WRITE_DEFAULT = false`,
  `MAIN_CHECKOUT_WRITE = forbidden`, `SELF_SELECT_NEW_WORK = forbidden`,
  `BLIND_RETRY = forbidden`. Any relaxation is a separate authority action.
- Rejected alternatives: per-task relaxation flags.
- Reason: first-night scope proves stability before any automation.
- Owner decision remaining: NONE

## 9. Contracts

### CTR-MRH-001 — Registry integrity and write authority

The host registry MUST bind repository identity, local path, base branch,
and last-scanned full head. Admission to any writing stage MUST require
`write_enabled = true` on the registry entry. A repository without a
registry entry MUST be refused. Registry scans MUST record exact heads;
head movement between scan and admission MUST be revalidated, not adopted.

### CTR-MRH-002 — Concurrency invariants are mechanical

The host MUST refuse: a second in-process job for a role already in
process, and admission of a write task to a repository that already has an
active write task. Refusal MUST be a typed rejection, never a silent queue.

### CTR-MRH-003 — Leases are bounded and recoverable

Every admitted task MUST hold a lease binding task, repository, role, and
expiry. Lease recovery after crash MUST preserve recorded handoff
idempotency and MUST NOT re-execute completed handoffs. Expired leases
MUST return their task to admittable state deterministically.

### CTR-MRH-004 — Window phases gate admission only through the control plane

`WINDOW_OPEN`/`QUIESCE`/`WINDOW_CLOSED` MUST gate admission and new GLM
work; `QUIESCE` MUST preserve queues, leases, and restart-safe state.
Role stations MUST be woken by handoff completion. A timer MUST only
invoke control-plane operations.

### CTR-MRH-005 — Controller powers are closed

The controller MUST NOT create or amend Product Authority, accept or
reject Specs, execute merges to authority branches, deploy, or self-issue
mutation permission. Every controller action MUST be one of: scan, route,
lease, wake, reconcile, quiesce, recover. Attempted actions outside this
set MUST fail.

### CTR-MRH-006 — Head drift is revalidated, never adopted

When a registered repository's head moves between host operations, the
host MUST require revalidation before further stage execution on affected
tasks; silent adoption of movement is forbidden. This complements the
worktree-level drift abort of the runtime.

### CTR-MRH-007 — Ledger exclusivity

The durable machine-readable ledger MUST be the sole authoritative store
for task state, handoff records, receipts, and review state. Forum or any
chat surface MUST NOT be required for, or capable of, reconstructing run
state.

## 10. Acceptance

### ACC-MRH-001 — Registry and write authority

- Contracts: `CTR-MRH-001`
- Method: admit tasks against unregistered, read-only-registered, and
  registered-writable repositories with valid PREFLIGHT records.
- Expected result: only the registered-writable case admits; others fail
  with typed rejections.
- Failure condition: task text or path presence substitutes for registry
  authority.

### ACC-MRH-002 — Concurrency and lease recovery

- Contracts: `CTR-MRH-002`, `CTR-MRH-003`
- Method: attempt duplicate role dispatch and dual write admission;
  simulate crash mid-stage; run recovery.
- Expected result: typed refusals for both concurrency cases; recovery
  requeues unexecuted work, never re-executes recorded handoffs; expired
  leases clear deterministically.
- Failure condition: double execution or ambiguous multi-in-process state.

### ACC-MRH-003 — Window gating and quiesce safety

- Contracts: `CTR-MRH-004`
- Method: attempt admission in every phase; quiesce with queued items;
  resume after closed window.
- Expected result: admission only in `WINDOW_OPEN`/`ACTIVE`; quiesce
  preserves queues and leases; resume continues without loss.
- Failure condition: cron-polling stations or lost queue state.

### ACC-MRH-004 — Controller power closure

- Contracts: `CTR-MRH-005`, `CTR-MRH-006`
- Method: request merge, deploy, spec acceptance, and task invention from
  the controller; move a registered head under an active task.
- Expected result: every out-of-set action fails; head movement forces
  revalidation and blocks stage work until completed.
- Failure condition: the controller can reach product or authority state.

## 11. Alternatives and disposition

### ALT-MRH-001 — Extend the Six-Pack Profile instead

- Disposition: rejected
- Reason: the Profile's open questions deliberately leave the runtime
  layer undecided; loading host semantics into it would amend an accepted
  authority's decided boundary rather than close a new narrow gap.
- What would reopen: an accepted Profile amendment that owns hosting.

### ALT-MRH-002 — No host authority; ad hoc controller operation

- Disposition: rejected
- Reason: unowned long-lived semantics with live writes — exactly the
  live-authority-gap condition Governance V1 forbids expanding.

### ALT-MRH-003 — Intelligent scheduler agent

- Disposition: rejected
- Reason: the forge needs determinism at the control plane; judgment
  belongs to the six governed stations.

## 12. Migration, compatibility, and rollback

```text
MIGRATION = author in forge/specs (runtime repo); promote through
  independent review and Owner acceptance as a docs PR against
  mayf3/agent-development-governance; runtime pins the accepted revision.
COMPATIBILITY = narrows nothing in parents; runtime V0 already implements
  these semantics and gains their authority on acceptance.
ROLLBACK = reject the proposal; runtime continues under Profile + host
  policy constants with multi-repo operation disabled.
EMERGENCY_CONTAINMENT = disable admission (WINDOW_CLOSED) and leases;
  contain only; permanent repair returns through authority routing.
```

## 13. Open questions

```text
OPEN_OWNER_DECISIONS = owner acceptance (status stays proposed until then)
NORMATIVE_TBD = NONE
UNRESOLVED_AUTHORITY_CONFLICT = NONE
PARTIAL_SUPERSESSION = NONE
INDEPENDENT_REVIEW_REQUIRED = YES
IMPLEMENTATION_IN_THIS_SPEC = NO (runtime V0 already exists as prior art)
```

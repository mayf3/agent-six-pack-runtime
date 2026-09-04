REVIEW_VERDICT: REVISE (5 blockers)

## A. Authority boundary — CONCERN

The child preserves the six roles, their order, receive modes, and ownership boundaries. It does not expressly grant the Controller Spec acceptance, merge, deployment, or Product Authority powers. This is consistent with `CTR-SIX-001`–`CTR-SIX-010`, `CTR-SIX-014`–`CTR-SIX-015`, and `CTR-SIX-020`.

However, controller closure is not fully precise:

- `DEC-MRH-005` forbids inventing product tasks, while `CTR-MRH-005` does not expressly repeat that prohibition.
- The permitted action `route` is undefined and could be interpreted to include task selection or substantive routing judgment.
- `ACC-MRH-004` tests task invention even though the governing Contract does not unambiguously classify it as forbidden.

Minimal clarification is needed so `route` means applying an already-authorized deterministic route and cannot include creating, selecting, reprioritizing, or semantically classifying work.

## B. Parent-Contract compatibility — BLOCKER

Two material conflicts are unresolved.

First, consumer-local authority is not closed. `CTR-MRH-001` lets the host admit writes based on a central registry flag and a “valid PREFLIGHT record,” but it never requires each consumer repository to adopt the exact host authority locally or identify the consumer-local actor authorized to set `write_enabled`. The migration section mentions only governance acceptance and the runtime pin. This can turn a shared host registry into cross-repository write authority, contrary to `CTR-GOV1-001`, `CTR-GOV1-002`, `CTR-GOV1-006`, `CTR-SIX-001`–`CTR-SIX-003`, and `CTR-OPL-013`.

Second, `CTR-MRH-003` says an expired lease returns a task to admittable state. Expiry alone does not prove the old worker stopped, nor does “recorded handoff idempotency” cover a mutation completed before its receipt was durably recorded. Re-admission can therefore create two writers or replay an ambiguous side effect, contrary to `CTR-SIX-012` and `CTR-OPL-013`.

## C. Gap honesty — CONCERN

The overall gap is genuine: none of the parents defines a multi-repository registry, per-repository write exclusion, night-window phase machine, or a closed controller capability set. The Spec is therefore not wholly unnecessary.

Two parts of the gap claim are overstated:

- Per-role single-in-process behavior is already substantially required by `CTR-SIX-012`, which requires refusal of ambiguous multiple-in-process states.
- Durable survival through notification loss and Agent/runtime restart is already required by `CTR-SIX-012`; the genuinely new gap is night-window admission/quiesce semantics, not durable survival generally.

Controller non-authority is also partially covered by `CTR-SIX-001`, `CTR-SIX-020`, `CTR-SIX-022`, `CTR-GOV1-005`–`CTR-GOV1-006`, and `CTR-OPL-001`. The new contribution is the exact closed controller power set.

## D. Narrowness — CONCERN

The normative design is mostly confined to host semantics and does not add dashboards or scheduling intelligence.

The repeated provider-specific phrase “GLM work,” especially in `DEC-MRH-004`, `CTR-MRH-004`, and Acceptance, conflicts with the stated provider/model non-goal and the configuration boundary in `CTR-SIX-003`. It should use a provider-neutral term such as “role execution” or “model-backed stage work.”

`OBS-MRH-003` may retain GLM as historical evidence, but normative Contracts should not select or assume it.

## E. Internal completeness — BLOCKER

Frontmatter has the required `status: proposed`, and both currently listed `governed_by` IDs name real accepted authorities. Because the review baseline explicitly includes `AGENT_OPERATIONAL_LAYER_V1` and the child defines retry, side-effect, and controller behavior governed by it, omitting it from `governed_by` and the authority analysis is a concern, although the Six-Pack parent also supplies an indirect lineage.

The Decisions-to-Contracts mapping is not one-to-one:

- `DEC-MRH-007` has no implementing Contract.
- Its `AUTO_ACCEPT`, `AUTO_MERGE`, `AUTO_DEPLOY`, `REMOTE_WRITE_DEFAULT`, `MAIN_CHECKOUT_WRITE`, `SELF_SELECT_NEW_WORK`, and `BLIND_RETRY` rules therefore are not implementation authority.
- `CTR-MRH-006` is instead an extra split of registry/head-drift behavior already introduced by `DEC-MRH-001`, with no distinct Decision of its own.

Acceptance is also incomplete:

- `CTR-MRH-007` has no Acceptance case.
- No Acceptance case tests the complete `DEC-MRH-007` safety policy.
- The controller task-invention test is stronger than the corresponding Contract wording.

## F. Other semantic holes — BLOCKER

`CTR-MRH-004` does not state a complete phase transition/admission matrix. It says `WINDOW_OPEN`, `QUIESCE`, and `WINDOW_CLOSED` gate admission and new work, but omits `ACTIVE` from the normative sentence and never explicitly says which operations are permitted in each phase. An implementation could admit during `QUIESCE` and still claim that the phase “gated” admission. This contradicts `DEC-MRH-004` and `ACC-MRH-003`.

Additional concerns:

- Lease acquisition, renewal, release, fencing, clock source, ownership proof, and takeover rules are unspecified.
- “Active write task” has no exact start/end definition.
- The interaction between preserved leases during `QUIESCE`, lease expiry, and later re-admission is undefined.
- “Registered repository head” does not distinguish task Head, `BASE_HEAD`, and moving `CURRENT_BASE_HEAD` as required by `CTR-GOV1-014`; target drift must abort rather than be adopted under `CTR-GOV1-006`.
- `CTR-MRH-007` says Forum must not be “capable of” reconstructing state, while `DEC-MRH-006` permits stage summaries and morning reports. Capability is neither enforceable nor necessary. The rule should instead say Forum content is never accepted as authoritative reconstruction.
- Ledger exclusivity is ambiguous against the mandatory queue-location state model in `CTR-SIX-012`. The Spec must state whether the ledger includes those queue records or is a projection that cannot replace them.
- `ROLLBACK` says multi-repo operation remains disabled, but Current State says Runtime V0 already implements the semantics. The exact current enablement state should be stated consistently.

## BLOCKERS

1. **`CTR-MRH-001`; parent `CTR-GOV1-001`, `CTR-GOV1-002`, `CTR-GOV1-006`, `CTR-OPL-013`**  
   Problem: a central registry flag can appear to authorize writes across consumer repositories without exact consumer-local adoption and authorization.  
   Minimal fix: require an exact local adoption revision and attributable consumer-local authorization for registration and every `write_enabled` transition; state that the flag only narrows authority and never creates it.

2. **`CTR-MRH-003`; parent `CTR-SIX-012`, `CTR-OPL-013`**  
   Problem: lease expiry automatically restores admissibility without fencing the prior worker or resolving an ambiguously completed mutation.  
   Minimal fix: add lease fencing generations, positive prior-owner exclusion, durable stage-outcome reconciliation, and `outcome_unknown` blocking; retry only through a declared idempotency mechanism or after confirmed absence.

3. **`DEC-MRH-007`, `CTR-MRH-006`, Contracts section**  
   Problem: Decisions and Contracts are not one-to-one; the fixed safety policy has no Contract, while head drift has no distinct Decision.  
   Minimal fix: add a Contract implementing every `DEC-MRH-007` constant and either add a distinct head-drift Decision or merge `CTR-MRH-006` into the registry Contract with an explicit mapping.

4. **`CTR-MRH-007`, Acceptance section**  
   Problem: ledger exclusivity has no Acceptance coverage, and the fixed safety policy is likewise untested.  
   Minimal fix: add positive and negative Acceptance cases for authoritative ledger/queue behavior, Forum non-authority, and every fixed safety constant.

5. **`CTR-MRH-004`, `DEC-MRH-004`, `ACC-MRH-003`**  
   Problem: the normative window-phase matrix is incomplete and does not unambiguously prohibit admission during `QUIESCE` or `WINDOW_CLOSED`.  
   Minimal fix: define permitted admission, new execution, continuation, checkpoint, lease renewal, and recovery actions for all four phases, plus legal transitions and restart behavior.

## CONCERNS

1. **`DEC-MRH-005`, `CTR-MRH-005`, `ACC-MRH-004`** — Define `route` narrowly and expressly forbid task invention, self-selection, semantic reprioritization, and authority classification by the Controller.

2. **Section 3; `CTR-SIX-012`** — Narrow the gap claim: durable queues, restart recovery, and single-in-process refusal already exist in the parent.

3. **`DEC-MRH-004`, `CTR-MRH-004`** — Replace normative “GLM work” with provider-neutral wording.

4. **Frontmatter and Section 3** — Add `AGENT_OPERATIONAL_LAYER_V1` as an explicit governing authority or explain why indirect governance through the Six-Pack Profile is sufficient.

5. **`CTR-MRH-006`; parent `CTR-GOV1-006`, `CTR-GOV1-014`** — Distinguish candidate/target drift from unrelated base-tip movement and specify abort versus bounded revalidation.

6. **`DEC-MRH-006`, `CTR-MRH-007`; parent `CTR-SIX-012`** — Reconcile ledger authority with mandatory queue-location state and replace the unenforceable “not capable of reconstructing” wording.

7. **Section 12 versus STATE-MRH-001** — State consistently whether multi-repository operation is currently implemented, enabled, or disabled.

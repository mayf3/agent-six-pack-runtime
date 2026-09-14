# 2026-09-14 Five-Repo Scout Intake — Canonical Governance Registration

This file is an append-only governance inventory continuation for `forge/inventory/INVENTORY_LEDGER.md`.

- MODE = TASK_RECORD_ONLY
- SOURCE = 2026-09-14 five-repo Scout reports supplied by Owner
- PRODUCT_REPO_MUTATION = NO
- PR_MUTATION = NO
- PRODUCTION_DB_WRITE = NO
- GRANT_OR_CREDENTIAL_MUTATION = NO
- DEPLOY = NO
- REPRODUCTION_EXECUTED = NO
- REPORT_SHA_RULE = every `SCOUT_BASE_SHA` below is the fixed coordinate of the Scout report only; it is **not** claimed as registration-time fresh main or production state.
- STATE_RULE = new canonical tickets start `CANDIDATE_UNVALIDATED`; existing tickets keep their canonical state and receive evidence/subitems only.
- EVIDENCE_RULE = static analysis / component probes are not promoted to full E3 unless the source report already proves that exact boundary.

## 0. Dedupe / ID allocation readback

Latest durable governance state shows T76/T77 already allocated; no T78+ ticket was found in the durable governance record before this intake. This intake therefore allocates T78–T90 only to distinct new root causes.

Existing work read before registration:
- T57 / agent-forum #22 = merged original read-cursor monotonicity repair; AF-SCOUT-06 is linked test-isolation debt, **not** a claim that T57 original race remains unfixed.
- T58 / agent-forum #24 = merged JWKS 500/503 classification repair; AF-SCOUT-08 is a resource-boundary issue introduced/left by the new probe implementation, **not** a reopen of the original classification defect.
- T52 = merged cross-repo Forum direct-agent token-profile work; new audit-build evidence is appended to T52, no duplicate cross-repo ticket.
- T60 / vehicle-pet #51 = merged retention repair; VP-SCOUT-006/007 are appended as bounded follow-up subitems, no new product Goal.
- T38 / agent-core-mobile #28 = merged refresh persist-failure fail-closed branch; MOB-GOV-009 is a different clear/delete failure boundary.
- auth-service #2 = OPEN/DRAFT legacy-surface-shutdown authority line; auth-service #15 = OPEN/DRAFT Human Principal administration accepted candidate, ACTIVE_ON_MAIN=NO, PRODUCT_IMPLEMENTATION_AUTHORIZED=NO. C02/C03/C04 attach to this existing authority/work lineage but retain separate acceptance surfaces.
- T36/T43 / auth-service #70 = merged rotation replay repair. AUTH-C05 is a separate NULL-preimage precondition boundary and is not deduped into the old replay defect.

## 1. Newly allocated canonical tickets

### T78 — AF-SCOUT-06 · Default-test database isolation / cleanup boundary

- SOURCE_SCOUT_ID = AF-SCOUT-06
- REPOSITORY = mayf3/agent-forum
- SCOUT_BASE_SHA = `7d54e58b468d99cd75aba6e3f844f6a22a4895fa`
- SEVERITY = P1
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = a default-collected test can override `DATABASE_URL`, connect to a hard-coded database and write fixture rows at module top-level without explicit opt-in, unique disposable target ownership, or guaranteed failure cleanup.
- ORIGINAL_EVIDENCE_SCOPE = 2026-09-14 Forum Scout card AF-SCOUT-06; default-suite collection + database target selection + module-top-level fixture write/cleanup path. Exact raw line receipt is source-report evidence; no fresh runtime execution is claimed here.
- WHY_IT_MATTERS = a default test run may mutate the wrong database or leave fixtures after a failed collection/run; this is test-safety/governance debt rather than proof that the old batch-read race still exists.
- MIN_DISCRIMINATING_ACTION = run the test harness only against a uniquely owned disposable database with explicit enable flag; verify default-off behavior, target rejection for non-disposable DB, and cleanup on success/failure/collection error.
- EXISTING_LINK = T57 / agent-forum #22 (regression lineage only).
- DUPLICATE_CHECK = NEW_SIBLING; DO_NOT_REOPEN_T57_OR_CLAIM_ORIGINAL_RACE_UNFIXED.
- NIGHTLY_ADMISSION = YES — isolated test-harness characterization first; no production DB.
- OWNER_BOUNDARY = no Owner decision for characterization; any policy change that intentionally permits shared/non-disposable test targets requires Owner approval.

### T79 — AF-SCOUT-07 · Reaction DELETE parent-object binding

- SOURCE_SCOUT_ID = AF-SCOUT-07
- REPOSITORY = mayf3/agent-forum
- SCOUT_BASE_SHA = `7d54e58b468d99cd75aba6e3f844f6a22a4895fa`
- SEVERITY = P2
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = Reaction DELETE checks visibility of the post/thread identified in the URL but does not bind the loaded message/reaction being deleted to that parent object before author-owned deletion.
- ORIGINAL_EVIDENCE_SCOPE = 2026-09-14 Forum Scout card AF-SCOUT-07; DELETE route parent lookup + message/reaction lookup + owner check. Static path only; no DB/API reproduction executed by this intake.
- WHY_IT_MATTERS = a caller may route through a public parent and delete **their own** reaction that actually belongs to a different hidden/deleted parent. This does not claim deletion of another user's reaction.
- MIN_DISCRIMINATING_ACTION = disposable DB/API fixture: own reaction under hidden/deleted parent + unrelated public parent path; compare correctly bound and cross-parent DELETE outcomes and final reaction row.
- EXISTING_LINK = none; related Forum lifecycle/visibility domain but not T37/T40/T56 root cause.
- DUPLICATE_CHECK = NEW_ROOT_CAUSE.
- NIGHTLY_ADMISSION = YES — disposable DB/API characterization.
- OWNER_BOUNDARY = characterization NO; if current contract intentionally allows cross-parent addressing, product semantics require Owner decision before repair.

### T80 — AF-SCOUT-08 · JWKS availability-probe resource boundaries

- SOURCE_SCOUT_ID = AF-SCOUT-08
- REPOSITORY = mayf3/agent-forum
- SCOUT_BASE_SHA = `7d54e58b468d99cd75aba6e3f844f6a22a4895fa`
- SEVERITY = P2
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = the T58/#24 availability probe performs an independent fetch after resolver failure per request, without an application-level deadline, shared in-flight probe, or explicit response-body consumption/cancellation boundary.
- ORIGINAL_EVIDENCE_SCOPE = 2026-09-14 Forum Scout card AF-SCOUT-08; T58/#24 `withJwksAvailabilityProbe` resource path. Static implementation review only; original 500/503 classification repair remains resolved.
- WHY_IT_MATTERS = slow/hanging JWKS responses or concurrent failures may amplify remote work and retain request/connection resources even though classification semantics are correct.
- MIN_DISCRIMINATING_ACTION = local HTTP fixture covering delayed headers, never-ending body, concurrent resolver failures, abort/deadline, response body close/cancel and request count.
- EXISTING_LINK = T58 / agent-forum #24.
- DUPLICATE_CHECK = NEW_IMPLEMENTATION_RESOURCE_BOUNDARY; DO_NOT_REOPEN_T58_CLASSIFICATION.
- NIGHTLY_ADMISSION = YES — local HTTP resource characterization.
- OWNER_BOUNDARY = no Owner decision for characterization; changing token-profile/security semantics is forbidden and remains outside this ticket.

### T81 — WF-GS-09 · Reconcile `already_applied` bypasses disabled-target validation

- SOURCE_SCOUT_ID = WF-GS-09
- REPOSITORY = mayf3/svc-workflow
- SCOUT_BASE_SHA = `6c05e0f9510b4d97d036a83d78c9c333f705ebfb`
- SEVERITY = MEDIUM-HIGH
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = reconcile can enter an `already_applied` success branch for a **new** idempotency key before validating that the target Principal is currently enabled.
- ORIGINAL_EVIDENCE_SCOPE = 2026-09-14 Workflow Scout card WF-GS-09; reconcile idempotency/replay branch ordering and target-principal enabled check. No runtime reproduction in this intake.
- WHY_IT_MATTERS = a new request may report success against a disabled target even though a historical receipt for the original key should remain replayable as history.
- MIN_DISCRIMINATING_ACTION = disposable DB fixture: same applied reconciliation target, disable target, compare original-key replay vs new-key request; assert new key rejects disabled target while original key preserves historical receipt semantics.
- EXISTING_LINK = existing reconcile/idempotency authority; not T62 successor-worklist repair.
- DUPLICATE_CHECK = NEW_ROOT_CAUSE.
- NIGHTLY_ADMISSION = YES — isolated DB characterization.
- OWNER_BOUNDARY = no Owner decision for characterization; do not auto-enable target or rewrite historical receipt. Any change to historical receipt semantics requires Owner approval.

### T82 — WF-GS-10 · Domain Owner authorization audit truth

- SOURCE_SCOUT_ID = WF-GS-10
- REPOSITORY = mayf3/svc-workflow
- SCOUT_BASE_SHA = `6c05e0f9510b4d97d036a83d78c9c333f705ebfb`
- SEVERITY = LOW-MEDIUM
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = a Domain Owner can read owner data using domain-scoped authority while the resulting audit record hard-codes `GLOBAL_WORKFLOW_COORDINATOR`, so the recorded authorization basis differs from the actual predicate that allowed the request.
- ORIGINAL_EVIDENCE_SCOPE = 2026-09-14 Workflow Scout card WF-GS-10; domain owner read authorization predicate + audit construction path. Static/source evidence only.
- WHY_IT_MATTERS = audit records can falsely attribute elevated/global authority, weakening incident/accountability truth even when access itself is correctly allowed.
- MIN_DISCRIMINATING_ACTION = isolated request matrix for Domain Owner vs global coordinator vs denied caller; compare decision predicate with emitted audit authorization basis.
- EXISTING_LINK = no equivalent canonical ticket identified.
- DUPLICATE_CHECK = NEW_AUDIT_TRUTH_ROOT_CAUSE.
- NIGHTLY_ADMISSION = YES — request/audit characterization.
- OWNER_BOUNDARY = no Owner decision to verify/correct actual authorization-basis recording; do **not** add permissions to make the audit label true.

### T83 — AUTH-SCOUT-20260914-C01 · Idempotent Principal/Client identity binding

- SOURCE_SCOUT_ID = AUTH-SCOUT-20260914-C01
- REPOSITORY = mayf3/auth-service
- SCOUT_BASE_SHA = `0cec4e9a64f5628ece42449693a7fc708f05098e`
- SEVERITY = P1
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = idempotent Principal/Client create, race and claim branches do not enforce one branch-invariant binding among this request's identity, expected client, returned target and persisted request/target digest.
- ORIGINAL_EVIDENCE_SCOPE = 2026-09-14 Auth Scout C01; `src/lib/oauth/v1/idempotent.ts` create-or-get Principal/Client branches plus route parameters/management guard. Static evidence; one-time DB characterization still required.
- WHY_IT_MATTERS = conflict/race handling may return another target as success or persist an incoming digest that is not bound to the canonical target represented by the response.
- MIN_DISCRIMINATING_ACTION = disposable DB matrix for create, claim, competing request and replay; record request identity, expected client, returned canonical target and stored digest for every branch.
- EXISTING_LINK = no canonical equivalent identified; explicitly not T36/T43 replay repair.
- DUPLICATE_CHECK = NEW_ROOT_CAUSE.
- NIGHTLY_ADMISSION = YES — disposable DB characterization only.
- OWNER_BOUNDARY = characterization NO; repair of fine-grained identity/conflict semantics requires Owner/security authority confirmation.

### T84 — AUTH-SCOUT-20260914-C02 · Disabled User re-issuance through legacy paths

- SOURCE_SCOUT_ID = AUTH-SCOUT-20260914-C02
- REPOSITORY = mayf3/auth-service
- SCOUT_BASE_SHA = `0cec4e9a64f5628ece42449693a7fc708f05098e`
- SEVERITY = P1
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = legacy login, token-login, refresh and authRequired projections do not consistently enforce `User.status=disabled`, allowing disabled Users to potentially receive newly issued credentials.
- ORIGINAL_EVIDENCE_SCOPE = Auth Scout C02: legacy login/token-login/refresh/authRequired User projections and signing paths; V1 active-status checks are the control path. Static evidence only.
- MIN_DISCRIMINATING_ACTION = one disposable disabled User fixture; run password login, valid pre-signed token-login, legacy refresh and V1 control; keep outcome/status classifications separate.
- EXISTING_LINK = auth-service PR #2 `AUTH_SERVICE_LEGACY_SURFACE_SHUTDOWN_V1` + PR #15 `AUTH_SERVICE_HUMAN_PRINCIPAL_ADMINISTRATION_V1`; both OPEN/DRAFT/UNMERGED, #15 not active on main and product implementation not authorized.
- DUPLICATE_CHECK = EXISTING_AUTHORITY_LINEAGE_BUT_NEW_ACCEPTANCE_SURFACE; do not create an umbrella "remove legacy" ticket.
- NIGHTLY_ADMISSION = YES — shared isolated legacy fixture with T85/T86, but separate acceptance result.
- OWNER_BOUNDARY = characterization NO; which legacy surfaces remain and unified disabled-user repair semantics require Owner decision.

### T85 — AUTH-SCOUT-20260914-C03 · Legacy bare-verify bypasses issuer/audience context

- SOURCE_SCOUT_ID = AUTH-SCOUT-20260914-C03
- REPOSITORY = mayf3/auth-service
- SCOUT_BASE_SHA = `0cec4e9a64f5628ece42449693a7fc708f05098e`
- SEVERITY = P1
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = after issuer/audience-aware verification paths fail, legacy `authRequired` falls back to bare `jwt.verify(token, JWT_SECRET)` and only checks User existence, allowing a correctly signed token from the wrong issuer/audience context to reach authentication.
- ORIGINAL_EVIDENCE_SCOPE = Auth Scout C03; `authRequired` fallback chain and User lookup. Static code reachability confirmed by Scout; production caller necessity/telemetry not established.
- MIN_DISCRIMINATING_ACTION = disposable HMAC key/User fixture; matrix of correct context, ADC-compatible context, and arbitrary wrong issuer/audience tokens.
- EXISTING_LINK = auth-service PR #2 legacy shutdown/compatibility + PR #15 Human lifecycle context.
- DUPLICATE_CHECK = EXISTING_LEGACY_WORK_LINEAGE_BUT_DISTINCT_TOKEN_CONTEXT_ACCEPTANCE; not T52 and not T36/T43.
- NIGHTLY_ADMISSION = YES — same isolated environment as T84/T86, independent token-context acceptance.
- OWNER_BOUNDARY = characterization NO; compatibility allowlist/removal of fallback requires Owner decision.

### T86 — AUTH-SCOUT-20260914-C04 · Legacy refresh single-consumption durability

- SOURCE_SCOUT_ID = AUTH-SCOUT-20260914-C04
- REPOSITORY = mayf3/auth-service
- SCOUT_BASE_SHA = `0cec4e9a64f5628ece42449693a7fc708f05098e`
- SEVERITY = P1
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = legacy refresh revocation is process-local (`Map`), check→await user lookup→revoke is non-atomic, and missing `jti` can bypass replay checking/consumption.
- ORIGINAL_EVIDENCE_SCOPE = Auth Scout C04; revoked-token Map, refresh verification, check/await/revoke sequence and missing-jti branch. Static evidence only; V1 durable transaction path is control, not proof for legacy.
- MIN_DISCRIMINATING_ACTION = disposable signed refresh token matrix: same-process repeat, concurrent double consume, process restart replay, two instances, and valid signed token without jti.
- EXISTING_LINK = auth-service PR #2 legacy shutdown + PR #15 / planned Human credential lifecycle authority line.
- DUPLICATE_CHECK = EXISTING_LEGACY_WORK_LINEAGE_BUT_DISTINCT_REFRESH_CONSUMPTION_ACCEPTANCE; not V1 refresh and not T36/T43.
- NIGHTLY_ADMISSION = YES — shared isolated environment with T84/T85; acceptance remains separate.
- OWNER_BOUNDARY = characterization NO; harden legacy refresh vs migrate/close legacy endpoint requires Owner decision.

### T87 — AUTH-SCOUT-20260914-C05 · Rotation seam NULL preimage fingerprint

- SOURCE_SCOUT_ID = AUTH-SCOUT-20260914-C05
- REPOSITORY = mayf3/auth-service
- SCOUT_BASE_SHA = `0cec4e9a64f5628ece42449693a7fc708f05098e`
- SEVERITY = P2
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = rotation SQL uses ordinary inequality for preimage comparison and does not explicitly reject NULL input; SQL three-valued logic can skip the mismatch branch when the provided fingerprint is NULL.
- ORIGINAL_EVIDENCE_SCOPE = Auth Scout C05; rotation SECURITY DEFINER seam preimage predicate. Static SQL reasoning only; no disposable-DB call executed by this intake.
- MIN_DISCRIMINATING_ACTION = disposable PG call to canonical seam with NULL, wrong, and correct preimage; assert NULL/wrong are zero-mutation rejects and correct preimage preserves normal rotation.
- EXISTING_LINK = related to T36/T43 / auth-service #70 rotation family, but original replay defect is merged and is not reopened.
- DUPLICATE_CHECK = NEW_PRECONDITION_BOUNDARY.
- NIGHTLY_ADMISSION = YES — disposable PG characterization.
- OWNER_BOUNDARY = characterization NO; mutation to credential seam remains security-sensitive and needs existing Owner/security repair authority.

### T88 — AUTH-SCOUT-20260914-C06 · Partial V0 keyring configuration skips startup fail-fast

- SOURCE_SCOUT_ID = AUTH-SCOUT-20260914-C06
- REPOSITORY = mayf3/auth-service
- SCOUT_BASE_SHA = `0cec4e9a64f5628ece42449693a7fc708f05098e`
- SEVERITY = P2
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = V0 keyring enablement detection treats a partially configured keyring as if the feature were completely absent, so malformed/incomplete configuration can bypass startup fail-fast instead of being rejected.
- ORIGINAL_EVIDENCE_SCOPE = Auth Scout C06; keyring configuration presence predicate + startup validation/fail-fast path. Static evidence only.
- MIN_DISCRIMINATING_ACTION = process-start configuration matrix: all absent, complete valid, and each partial combination; assert all-absent keeps supported disabled posture while partial configurations fail before serving.
- EXISTING_LINK = no canonical equivalent identified; related to keyring/JWKS operational authority only.
- DUPLICATE_CHECK = NEW_CONFIGURATION_TRUTH_BOUNDARY.
- NIGHTLY_ADMISSION = YES — local startup/config characterization.
- OWNER_BOUNDARY = no Owner decision for validation of fail-fast truth; compatibility changes to supported partial configuration would require Owner decision.

### T89 — MOB-GOV-009 · SecureStore clear failure can preserve in-memory authenticated session

- SOURCE_SCOUT_ID = MOB-GOV-009
- REPOSITORY = mayf3/agent-core-mobile
- SCOUT_BASE_SHA = `ecd95c633608e17a42b1a3af105d503971e6dab7`
- SEVERITY = P1
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = after the SecureStore pointer is deleted, a later residual-cleanup failure can abort the clear path before logout/explicit-auth-rejection invalidates the in-memory session state.
- ORIGINAL_EVIDENCE_SCOPE = 2026-09-14 Mobile Scout MOB-GOV-009; SecureStore clear/delete pointer + residual cleanup + public auth logout/rejection path. Static/counterexample evidence only unless source report explicitly records component execution.
- WHY_IT_MATTERS = explicit logout or definitive authentication rejection may leave the process presenting the old session as authenticated even though persistence clearing has partially begun.
- MIN_DISCRIMINATING_ACTION = deterministic fake SecureStore: pointer delete succeeds, residual cleanup throws; run logout and explicit auth-rejection paths; assert memory session/token clears regardless of cleanup error and record persistent residue separately.
- EXISTING_LINK = T38 / mobile #28 (merged save-failure branch) as sibling only.
- DUPLICATE_CHECK = NEW_CLEAR_FAILURE_BOUNDARY; do not reopen T38 save-failure defect.
- NIGHTLY_ADMISSION = YES — deterministic fake-store characterization.
- OWNER_BOUNDARY = no Owner decision for characterization; repair should follow accepted fail-closed semantics unless it changes restart/persistence policy.

### T90 — MOB-GOV-010 · HTTP/ASR timeout excludes response-body join

- SOURCE_SCOUT_ID = MOB-GOV-010
- REPOSITORY = mayf3/agent-core-mobile
- SCOUT_BASE_SHA = `ecd95c633608e17a42b1a3af105d503971e6dab7`
- SEVERITY = P2
- STATE = CANDIDATE_UNVALIDATED
- ROOT_CAUSE = HTTP/ASR timeout coverage ends before response-body `join()`; if headers arrive but the body never completes, the request/connection can remain pending beyond the declared operation timeout.
- ORIGINAL_EVIDENCE_SCOPE = 2026-09-14 Mobile Scout MOB-GOV-010; HTTP/ASR request timeout wrapper + body join/stream consumption path. Static evidence only; no network fixture run in this intake.
- MIN_DISCRIMINATING_ACTION = local server fixture that sends headers then stalls body; verify one overall deadline covers request + body read, resources are cancelled/closed, and ambiguous completion is not hidden by automatic retry.
- EXISTING_LINK = no canonical equivalent identified.
- DUPLICATE_CHECK = NEW_RESOURCE_DEADLINE_BOUNDARY.
- NIGHTLY_ADMISSION = YES — local deterministic HTTP fixture.
- OWNER_BOUNDARY = characterization NO; adding automatic retry/replay for ambiguous ASR/HTTP outcomes requires Owner decision and is out of scope.

## 2. Evidence appended to existing tickets — state unchanged

### T52 — direct-agent mint build/audit follow-up

- SOURCE = 2026-09-14 Auth Scout direct T52 supplement
- SCOUT_BASE_SHA = `0cec4e9a64f5628ece42449693a7fc708f05098e`
- STATE_CHANGE = NONE; keep existing T52 canonical state.
- SUBITEM_A (P1 build closure) = the new direct-agent mint uses an audit event type not accepted by `AuditEventType`; isolated component probe observed TS2322.
- SUBITEM_B (P2 audit correctness) = mint passes `scope`, while the logging interface reads `scopes`; isolated probe observed missing audit scope.
- EVIDENCE_BOUNDARY = component/typecheck/audit probe only. Do **not** describe this as a fresh real Auth-mint → Forum-verifier end-to-end pass.
- MIN_DISCRIMINATING_ACTION = disposable keyring/component test: compile/typecheck exact mint path; execute synthetic mint audit and assert accepted event type + exact scope list under current contract fixture; cross-repo full-chain proof remains separately evidenced.
- DUPLICATE_CHECK = APPEND_TO_T52; no new cross-repo ticket.
- NIGHTLY_ADMISSION_SUGGESTION = YES as T52 follow-up characterization if/when the canonical state is reopened by normal governance; no automatic state change in this intake.
- OWNER_BOUNDARY = no new token-profile decision; any change must stay within accepted T52 direct-agent profile.

### T60 — vehicle-pet post-repair assurance / shipped-artifact subitems

- SOURCE = VP-SCOUT-007 + VP-SCOUT-006
- SCOUT_BASE_SHA = `72553d51e197f4b6d812728bc19131aceac06b74`
- STATE_CHANGE = NONE; keep existing T60 canonical state.

#### VP-SCOUT-007 — retention regression test assurance
- SEVERITY = P2
- ROOT_CAUSE = new retention test is not collected by the canonical suite; contains an always-true assertion; claimed reload lacks storage readback/new-instance proof; report also flags a potential type issue that still requires canonical typecheck confirmation.
- ORIGINAL_EVIDENCE_SCOPE = Vehicle Scout VP-SCOUT-007, test collection/assertion/reload/typecheck surfaces at the fixed report SHA.
- MIN_DISCRIMINATING_ACTION = run canonical suite collection + canonical typecheck without modifying generated outputs; prove the regression test is actually collected; replace mutation/fixture values to make the assertion capable of failing; verify reload through storage read/new instance.
- NIGHTLY_ADMISSION = YES — test-assurance characterization; no product semantics.

#### VP-SCOUT-006 — source vs committed `lib/` / fixed-SHA installed artifact truth
- SEVERITY = P2
- ROOT_CAUSE = runtime source changed while committed `lib/` tree did not; fixed-SHA install consumes `lib/` and has no automatic build hook, so repository source truth and actually installed runtime bytes can diverge.
- ORIGINAL_EVIDENCE_SCOPE = Vehicle Scout VP-SCOUT-006; source tree vs committed lib tree + package/install entry/hook at the fixed report SHA.
- MIN_DISCRIMINATING_ACTION = compare source, committed `lib/`, packed/fixed-SHA installed contents and executed runtime **without first overwriting build outputs**; only after the preimage is captured may a clean rebuild be compared.
- NIGHTLY_ADMISSION = YES — read/package characterization.
- OWNER_BOUNDARY = characterization NO; changing committed-build-artifact policy or publication/install contract requires Owner decision.

- DUPLICATE_CHECK = BOTH_SUBITEMS_APPEND_TO_T60; no new vehicle product Goal/ticket.

## 3. Dedupe / non-ticket dispositions

- AF-SCOUT-06 is **not** T57 original race: T57/#22 remains the merged product fix. T78 records the new default-test isolation/cleanup root cause and only links the regression lineage.
- AF-SCOUT-08 does **not** reopen T58/#24's 500/503 classification defect; T80 records the new probe resource/deadline/concurrency boundary.
- AUTH C02/C03/C04 share one disposable legacy test environment but remain T84/T85/T86 with separate acceptance matrices. No generic "remove legacy" ticket is created.
- AUTH C05 is related to the rotation seam family but is not T36/T43 replay consistency; T87 is a new precondition ticket.
- MOB-GOV-009 is outside T38's merged save-failure branch; T89 is a sibling clear-failure boundary.
- T52 receives build/audit evidence only; no duplicate cross-repo ticket.
- VP-SCOUT-006/007 are recorded under T60 only, per Owner instruction; no new vehicle Goal.

## 4. Registration summary / readback target

- NEW_CANONICAL_IDS = T78, T79, T80, T81, T82, T83, T84, T85, T86, T87, T88, T89, T90
- EXISTING_TICKETS_APPENDED = T52, T60
- NEW_TICKET_COUNT = 13
- EXISTING_APPEND_COUNT = 2
- NEW_TICKET_STATE = CANDIDATE_UNVALIDATED for all T78–T90
- PRODUCT_REPO_MUTATIONS = 0
- PR_MUTATIONS = 0
- PRODUCTION_WRITES = 0
- OWNER_CONFIRMATIONS_REQUESTED = 0 at registration time; Owner boundaries are recorded per ticket for later repair/compat/security decisions.

# GOAL_STATE — Six-Pack Runtime

## ACTIVE GOAL — 启用 Six-Pack 首次受限夜间交付（2026-09-05 启动）

GOAL_STATUS = ALIGN_2_CORRECTED_REPLAY_COMPLETE_AWAITING_INDEPENDENT_REVIEW（2026-09-07 00:52：corrected replay 全链收敛 verify PASS；评审面已暴露 = dsh-agent-core PR #189 Draft；STOP at Owner decision）
ALIGN_2_TERMINAL = BASE 16e14233fbac1ccbdc00598097380da659e1ecd2 / HEAD fbbe8c03d0242a2d6d82bf01aff69bf120a2ced9 / TREE 9bf397860ed6a6ac368a742c692a47a4ff873e53 / 11 receipts / RUNTIME_REVISION d7eb759afdf49c8fbdef60aca6acdbe066a4ae17（含 reviewed porcelain fix bytes，review 5124083447 ACCEPT）
ALIGN_2_REVIEW_PR = mayf3/dsh-agent-core#189（Draft/Open；head=review/dsh-trusted-ingress-align-2@fbbe8c03 原样推送零改写；取代 PR #177 lineage）
ALIGN_2_RESUME_ALLOWED = YES（已行使：corrected replay 于 2026-09-06 23:07–09-07 00:52 窗口内完成；五道 fresh gates 全过：verify PASS / 9-9 / 负探针 exit 1 / agent-router 全套 310 tests 0 failures / done 标记；晨报 = sixpack-forge/nightly-1/MORNING_REPORT_2026-09-07.md）
ROLLUP_EVIDENCE_SEE_BELOW = RESUME_EVIDENCE / ROLLOUT 各行保留为历史证据
ROLLOUT = ROLLOUT_BASE 0a6fac41faa905d7834d2c00567248e7edfc7cbb → ROLLOUT_HEAD d7eb759afdf49c8fbdef60aca6acdbe066a4ae17（tree 9afbb4907fd61441e1646d6dc91e00746cf4abdb；cherry-pick 已审 fix delta，无其他产品字节）；实际运行 revision = v0/bootstrap @ d7eb759a
RESUME_EVIDENCE = REVIEW 5124083447 ACCEPT（绑 f6a3c659/da07182；PR #3 保持 Draft 未合并）+ REVIEWED_FIX_BYTE_EQUALITY YES（blob 级：gitx 6eb46d9b / runner d8b91cff / tests 5589ad73）+ FULL_TEST 116 passed + ruff clean + mypy strict clean + QA_OWNERSHIP_PRECHECK PASS 5/5（rollout head 实跑；state/qa-ownership-precheck-2026-09-06/precheck-result.json）
REVIEW_PR = mayf3/agent-six-pack-runtime#3（保持 Draft/review-only，未为 merged 徽章合并）；dsh-agent-core#177（align-1 lineage）保持不动
G1_ARTIFACT_RETENTION_SPEC_GAP = **STILL_OPEN**——不阻塞 candidate 形成/fresh QA/PR/review；阻塞任何 merge tree 含待裁决 Six-Pack execution artifacts 的候选的最终 merge 决定。与本 bug/修复分离处理。

### ACTIVE GOAL — NIGHTLY_CONTINUOUS_REPAIR_QUEUE_PILOT_V1（2026-09-07 晨 Owner 设立；白班会话预登记，今晚 23:00 起执行）

定位：今晚第一次正式验证 continuous nightly pilot——23:00 自动上班，从 Repair Queue 持续拿合法任务，一项结束后自动拿下一项，能安全做到 Draft PR / independent review 就做到那里；08:30 停止开新模型工位；09:00 必须停止全部新的模型执行。**不是 Runtime 开发 Goal / 不是 Scout Goal / 不是 Owner decision Goal。**核心验收一句话（Owner 原文）：**23:00 自动上班，一单做完自己拿下一单；08:30 不再开新活，09:00 必须彻底停止模型执行。**

- **窗口（Asia/Shanghai）**：23:00 START / 08:30 QUIESCE / 09:00 HARD STOP。ACTIVE 允许：启动新合法任务 / 新 Six-Pack station / read-only investigation / independent review / candidate implementation / QA / Draft PR。08:30 起禁止：新 task / 新 model-backed station / 下一 Six-Pack role；只许当前 bounded stage 收尾（完成动作 + 保存结果 + commit/receipt/persist）。例：08:25 coder 开工、08:42 完成 → 不启动 cleaner，task=WAITING_NEXT_NIGHT_AT_CLEANER。09:00 硬停止：NO new model calls / role spawn / next task / retry launch / correction launch；在跑 worker → 机械已知则 persist，execution may have happened but no durable receipt → OUTCOME_UNKNOWN + preserve evidence + NO AUTO REDISPATCH；09:00 后不得为「差一点做完」继续耗额度。
- **ENTRYPOINT**：唯一 nightly supervisor = automation-9952ac9c（23:00 daily）。禁止 special per-task sentinel / second supervisor / second controller；align-2 one-shot 哨已完成，不复活。
- **WORK SOURCE**：唯一 = MULTI_REPO_REPAIR_QUEUE.md + durable ledger；不重扫仓库找新活。每完成一个 disposition → persist result → update Repair Queue → fresh-read Repair Queue → choose next legal task；完成第一单不退场。
- **QUEUE STATES**：自动跳过 WAITING_OWNER_DECISION / BLOCKED / CLOSED / STALE_AS_PREPARED requiring Owner decision；只读推进 NEEDS_READ_ONLY_INVESTIGATION / NEEDS_CURRENT_BASE_REVALIDATION / WAITING_INDEPENDENT_REVIEW；写任务 admission 六条件全满足才准入（accepted applicable Authority + task-bound mutation mandate + current need freshly demonstrated + repo write slot free + Base/Authority drift cleared + existing legal execution route），缺一 = NO_WRITE；**Repair Queue 状态本身不是 mutation mandate**。
- **CURRENT QUEUE GUIDANCE（Owner 给定，今晚照此处理）**：dsh #189 = WAITING_OWNER_DECISION → SKIP；dsh #177 = SUPERSEDED_PENDING_OWNER_CLOSE → SKIP；dsh CODE-1 = QUEUED_VALIDATED_FINDING → 仅当 write slot free AND valid task mandate 存在才推进（queue 归并节注：align-2 write slot 释放后才可重判 admission，slot 处置归 Owner）；svc #22 = STALE_AS_PREPARED → SKIP until Owner chooses re-vendor target；forum #17 = WAITING_OWNER_DECISION → SKIP；forum L0 DOC truth = READY_FOR_TRIVIAL_DOCS_FIX → write only with valid task-bound mandate；auth #36 = BLOCKED_OWNER_HELD → SKIP；HR dispatcher topology = WAITING_OWNER_DECISION → SKIP。不得为满足「连续执行」把 Owner-blocked 项强行变成工作；无合法任务 → IDLE 是正确结果。
- **SIX-PACK EXECUTION**：合法 non-trivial implementation 走 specifier→coder→cleaner→architect→hardender→QA；事件驱动 receipt complete→立即评估下一 station，但**每次真正 spawn 模型前机械重查 current time < 08:30**；08:30 后即使前一 station 刚完成也不 spawn 下一站。
- **AUTOMATIC SAFE ENDPOINT**：合法 write task 自动做到 isolated worktree/branch → implementation → focused tests → QA → terminal verify → push candidate branch → create Draft PR → （legal/available 时）independent exact-head review；之后 AUTO_READY=false / AUTO_MERGE=false / AUTO_DEPLOY=false。Review ACCEPT → WAITING_OWNER_DECISION；Review REVISE → time<08:30 且 correction budget 可用才 correction/replay，否则 persist blocker + 留 Draft PR + DEFERRED_TO_NEXT_NIGHT。
- **CONCURRENCY（今晚）**：MAX_CONCURRENT_MODEL_CALLS=1 / CONTROLLER_COUNT=1 / LEDGER_WRITER_COUNT=1 / MAX_ACTIVE_WRITE_TASKS_PER_REPO=1 / MAX_IN_PROCESS_PER_ROLE=1；不开真实 two-worker；今晚测 A 完→B 起→C… 的串行连续。
- **RATE LIMIT**：429/provider transient 优先 Retry-After，否则 2m/5m/10m/20m/30m/30m，MAX_TRANSIENT_START_RETRIES=6；等某任务 retry 时改试另一合法 queue 项，不让一个限速任务阻塞整夜；唯机械确认四证明（no model execution / no file mutation / no candidate commit / no durable receipt）才自动重试，否则 OUTCOME_UNKNOWN + NO AUTO REDISPATCH，冻结 affected task、其他安全任务续跑。
- **TASK BUDGET**：MAX_CORRECTION_ROUNDS_PER_TASK_PER_NIGHT=2；MAX_TASK_WALLTIME_PER_NIGHT=3h；到预算 persist exact state + DEFERRED_TO_NEXT_NIGHT + 释放执行容量 + 选下一 queue 项。
- **CONTINUOUS PILOT SUCCESS 判据（取代昨晚 NIGHTLY_PILOT_CLOSEOUT 预登记措辞，以本节为准）**：≥2 个不同 task disposition 且 ≥1 个达到 real implementation candidate / Draft PR / independent review → **CONTINUOUS_MULTI_TASK_NIGHTLY_PILOT=PASS**；只有一个合法任务 → **INCONCLUSIVE_NOT_ENOUGH_WORK**（不为凑 2 个发明工作）；存在第二个合法任务但第一单结束后 supervisor 没有继续 → **FAIL，CAUSE=DISPATCHER_CONTINUITY**（只调查 continuity，不扩成 Runtime 重构）。
- **MORNING REPORT（09:00 后只许机械汇总，不调模型继续开发）**字段：NIGHTLY_RUN_ID / WINDOW_START / QUIESCE_AT / HARD_STOP_AT / TASKS_STARTED / TASKS_COMPLETED / TASKS_DEFERRED / TASKS_OUTCOME_UNKNOWN / DRAFT_PRS_CREATED / REVIEWS_ACCEPTED / REVIEWS_REVISE / RATE_LIMIT_EVENTS / START_RETRIES / OWNER_DECISIONS_PENDING / REPAIR_QUEUE_CHANGES / LAST_MODEL_CALL_STARTED_AT / MODEL_CALLS_AFTER_08_30 / MODEL_CALLS_AFTER_09_00 / CONTINUOUS_MULTI_TASK_NIGHTLY_PILOT。硬验收 **MODEL_CALLS_AFTER_09_00=0**；非 0 → NIGHT_WINDOW_HARD_STOP=FAIL 单列 blocker。
- **DO NOT DO**：repo-wide Scout / Runtime architecture refactor / new scheduler·service·database·dashboard / two-worker concurrency / auto merge / auto deploy / Owner decision inference / special per-task sentinel。
- **DONE_WHEN**：23:00 supervisor starts once；Repair Queue continuously consumed；every disposition causes fresh queue read；Owner/blocker items skipped；legal work reaches safe Draft-PR/review boundary where possible；08:30 no new model-backed station；09:00 zero further model execution；morning report written；queue updated → STOP。
- **【白班预检记录 2026-09-07 07:06–07:16，本会话，零模型】**① CronList：automation-9952ac9c enabled/active、`0 23 * * *`、nextRun=今晚 23:00 CST；5dd41c1a 与 ad8fa74d completed、4cf1970a paused → 唯一入口成立，无第二 supervisor。② standby-check 干跑（快照存 /tmp/cronlist-snap-20260907.json，结果 /tmp/standby-dryrun-now.json 与 /tmp/standby-dryrun-2305.json，双时点=现在+模拟 23:05）= ALIGN2_SENTINEL_PENDING=NO / DO_NOT_STANDBY → 今晚走 SUPERVISE。③ 无残留 supervisor/worker/daemon 进程；launchd com.mayf3.sixpack-watchdog 在位退出码 0。④ **发现并修复 watchdog-wrapper.sh 跨午夜缺陷**：原脚本按 `date +%F` 定位 dispatch 目录，午夜后在新日期目录找 tonight_mode.json 不得（STANDBY 裁定落在 09-06 目录）→ 误判 supervisor absent，2026-09-07 00:05–07:02 记 22 次 incident 并每 ~10 分钟空启一次心跳守护（守护孤儿自退 ~30s；flock 按日期目录隔离，未触及正牌锁；daemon 零派发故零模型零重复调度）。修复 = 夜归属日规则：HHMM<12:00 → NIGHT_DATE=昨日，否则今日；tonight_mode/STANDBY 查找与 `supervisor start --date` 均用 NIGHT_DATE。验证：bash -n 过；live 实跑静默 exit 0、2026-09-07 目录零写入、无 daemon 残留；分支映射 0005/0716/1159→昨日、1200/2309/2359→今日全对。⑤ 缺陷证据存档 = nightly-1/state/dispatch/2026-09-07/incident-crossmidnight-watchdog-20260907/（count=22 的 start_retries.json + orphan-blip supervisor.json 样本）；**今晨晨报 START_RETRIES/RATE_LIMIT_EVENTS 口径须剔除该缺陷段**（command-only 兜底自身缺陷空转，非 supervisor 启动重试）。⑥ wrapper 位于 sixpack-forge（非 git 仓），本条即修复唯一 durable 记录。⑦ Repair Queue 现状与上列 CURRENT QUEUE GUIDANCE 逐项核对一致，未重扫仓库。

### NIGHTLY_CONTINUOUS_REPAIR_QUEUE_PILOT_V1 — 首次连续消费夜班执行结果（2026-09-07 23:00 → 2026-09-08 00:3x，已收口）

**CONTINUOUS_MULTI_TASK_NIGHTLY_PILOT = PASS**（4 dispositions，2 Draft PR 且双 review ACCEPT；无发明工作；Owner/blocked 全 SKIP；
无 OUTCOME_UNKNOWN；零 rate-limit；MAX_CONCURRENCY=1；晨报 = nightly-1/MORNING_REPORT_2026-09-08.md，硬验收
MODEL_CALLS_AFTER_08_30=0 / AFTER_09_00=0）。 receipts 全集 = state/dispatch/2026-09-07/receipts/。
- MANDATE B（CODE-1）→ **Draft PR mayf3/dsh-agent-core#196**：fresh main 8454873 判别 ">=0" 无满足版本
  （ENOTARGET）→ 一行 ">=0.1.0-rc" → 解析 0.1.0-rc.8 真库 → focused 5/5；candidate @ 7ebc6ac/tree a7cb769。
- MANDATE A（forum L0）→ **Draft PR mayf3/agent-forum#19**：L0 三轴未部署核实（root workflows ABSENT /
  子目录不触发 / bp 404）→ ci-gate-guide.md +20/−6 诚实化；candidate @ 09d900c/tree e6a2dfc。
- TASK C（mobile triage）→ 4 PR 全 fresh disposition：#8/#10 WAITING_OWNER_DECISION（视觉属 Owner）、
  #11 WAITING_DEVICE、#12 WAITING_SPEC_ACCEPTANCE；main=e1aa6366；零新 finding。
- TASK D（vehicle-pet scout）→ **HEALTHY_NO_ACTION**：main=c3d1d4e7；typecheck+157/157+18/18+lint 全绿；
  authority graph 完整无孤儿；无虚假 enforcement 声明；findings 0/3。
- 两新仓 AUTO_*=false 遵守；零 mutation 于 mobile/vehicle-pet。
- 待 Owner：PR #196 / #19 independent review + 处置（存留 #189 merge(G1)/#177/svc#22/forum#17/HR/L0-DEPLOY）。

### ACTIVE GOAL — NIGHTLY_ALL_REPOS_CONTINUOUS_GOVERNANCE_V1（2026-09-08 凌晨 Owner 设立；A–G 零模型 simulation 全过）

GOAL_STATUS = ALL_REPOS_CONTINUOUS_GOVERNANCE_READY = **NO（2026-09-08 07:5x 诚实降级）**——roundrobin 选路逻辑与 simulation 全部成立，但 liveness proof（NIGHTLY_SUPERVISOR_LIVENESS_PROOF_V1，evidence/forge-liveness-probe/LIVENESS_PROOF_20260908.md）机械判定执行模型 = **SESSION_BOUND（MODEL B）**：连续消费的执行面活在 scheduled Agent 会话内；守护（double-fork 后 PPID=1、独立存活实证）只是 liveness/watchdog anchor，CHECK 4 实证活守护 + 注入 executable item 5 分钟零反应（无进程消费 queue）；work plane 会话退出即无人继续（CHECK 1/2）。恢复能力 = 仅 liveness anchor（昨夜 incident 22 次守护重启实证），零盲目模型重派 ✓。新发现 wrapper 边缘缺陷一枚（morning-tail 日期分歧，低危，修复形态见探针报告）。按 Owner 规则 MODEL B ⇒ READY=NO；最小修复方向 = 23:00 model bootstrap once + durable daemon 升级为真 work supervisor（平台可行性：daemon 可 command-only 直接 spawn glm-role-exec/deterministic drive()，无需 Agent session） + durable cursor/no-dup gate；仅当 daemon 无法自主派发才退回 bounded periodic model wake（加锁+cursor+no-dup）。原 simulation 结论保留：
- 纳管集（写死于 dispatcher 常量，新增只经显式 registry/queue adoption）= mayf3/{dsh-agent-core, agent-forum, svc-workflow, auth-service, agent-core-mobile, vehicle-pet}。
- 新增 dispatcher 子命令：`roundrobin`（优先级 = executable queue items → 下一未完成仓 maintenance pass（每仓每夜一次完整 pass）→ IDLE_ALL_GOVERNED；QUIESCE/CLOSED 相位 → WINDOW_REFUSE_NEW_PASS + 未完成仓 DEFERRED_TO_NEXT_NIGHT）与 `mark-pass`（pass 完成登记：final_state/new_findings/queue_items_added）。round 状态持久 = state/dispatch/<date>/repo-round.json。
- MAINTENANCE_PASS 十项检查清单随 action 输出；pass 内 existing work 优先（Draft PR awaiting review / revalidation / known blocker / validated findings）；finding 字段十项齐备 + 每仓每夜 MAX_NEW_VALIDATED_FINDINGS=3；pass 默认 READ_ONLY，写需六条件全满足。
- 新 IDLE 定义 = NO_EXECUTABLE_QUEUE_ITEM AND ALL_REPOS_PASS_DONE_OR_DEFERRED_BY_TIME（queue 暂空不算完）。
- simulation 证据 = state/dispatch/simulation-20260908-governance/（A queue空→dsh pass 起 ✓；B forum pass 发现 finding→入队→queue 先行执行→恢复被中断 pass ✓；C 已完成仓不重扫→svc next ✓；D HEALTHY_NO_ACTION 登记 ✓；E 全 done+queue 空→IDLE_ALL_GOVERNED ✓；F 08:35→4 仓 DEFERRED ✓；G 09:30→refuse+零 spawn 不变量 ✓）。
- 23:00 prompt 已升级（roundrobin 主循环 + maintenance 清单 + finding 字段 + 新 IDLE + 晨报新字段 GOVERNED_REPOS/REPOS_VISITED/REPOS_HEALTHY/REPOS_WITH_NEW_FINDINGS/REPOS_DEFERRED_BY_0830/NEW_QUEUE_ITEMS/WRITE_TASKS_COMPLETED/DRAFT_PRS_CREATED/REVIEWS_COMPLETED/OWNER_DECISIONS_PENDING）。
- 首次实跑 = 2026-09-08 23:00。

### OWNER 指令（2026-09-08 22:5x）：supervisor 链升级双角色（23:00 BOOTSTRAP + 每小时 WAKE 续拉）——SESSION_BOUND 缺口的 Owner 选定修法

- Owner 原话要点：「我不希望你配置 watchdog，但可以用 zcode 里的定时机制每小时执行一次继续拉取任务。」即上一节 liveness proof 列出的修复方向中，**Owner 直接选定 bounded periodic model wake 路线**（durable daemon 升级不做，等未来另授权）。
- 落地 = automation-9952ac9c cron `0 23 * * *` → **`0 0-8,23 * * *`**（单自动化双角色；本会话内 CronCreate 被拒故升级既有条目。23:00 = 原 BOOTSTRAP 全流程不变；00:00–08:00 每小时整点 = WAKE 续拉）。**WAKE 不是 watchdog**：无 liveness 监控/重启/冻结职责，只做续消费拉取。launchd com.mayf3.sixpack-watchdog 维持原样未动（零模型 command-only；如需下线待 Owner 明示）。
- WAKE 决策链（机械优先，能零模型退出就零模型退出）：NIGHT_DATE 跨午夜归属（HHMM<12:00→昨日）→ W1 tonight_mode==STANDBY→STANDBY_NOOP（哨夜不抢）→ W2 session-heartbeat<2700s→SESSION_ALIVE_NOOP（禁双 controller）→ W3 roundrobin 零模型评估=IDLE_ALL_GOVERNED/WINDOW_REFUSE_NEW_PASS→NOOP → W4 接管：supervisor start（flock 防双开）→ 与 23:00 会话同一主循环（pre-spawn-gate/budget-check/classify-retry/OUTCOME_UNKNOWN 冻结/mark-pass 全套不变）→ W5 收口 morning-report+GOAL_STATE 账目 push → W6 遇疑冻结不重派。
- 残余风险（记录在案，不修代码，发生时如实晨报）：主会话若单阶段 >45min 未 touch 心跳，W2 可能误判失联→接管重叠——由 flock + durable receipts + OUTCOME_UNKNOWN 冻结兜底；WAKE 粒度 1h，最坏连续性损失窗 = 1h。
- 今晚（09-08 23:00）bootstrap 不受影响（nextRun 实测仍 23:00:00 +0800）；首次 WAKE = 今晚 00:00。同日会话内机械核查：CronList enabled、standby 干跑=DO_NOT_STANDBY（/tmp/standby-dryrun-20260908.json）、零残留进程、launchd watchdog 在位。

### 09-08 夜首跑结果（BOOTSTRAP run#3 @ 23:00:11；23:06–23:19 收口；IDLE_ALL_GOVERNED）

- **NIGHTLY_ALL_REPOS_CONTINUOUS_GOVERNANCE_V1 首次实跑 = PASS（round-robin 模式）**：gate 6/6 lane PASS（HEAD=4aae2cb）→ 六仓 MAINTENANCE_PASS 全 DONE @ 23:18 → IDLE_ALL_GOVERNED（新 IDLE 定义下正确终态，远早于 08:30 闸）。全 READ_ONLY：WRITE_TASKS=0 / DRAFT_PRS=0 / 新 finding=0 / GLM provider 调用=0（唯一瞬时=mobile pass 一次 gh TLS timeout，重试即过）。晨报 = nightly-1/state/dispatch/2026-09-08/NIGHTLY_RUN_2026-09-08.md；receipts = 同目录 receipts/pass-*.json ×6。
- **dsh T1（BROKER-BOOT-BINDING-01, P1）夜间 pass 判别测试机械复现**：fresh worktree @2bd3d62f `node --test packages/broker/test/index-bindings.test.js` = **2/2 FAIL**（fleet-killer 用例 "local binding required by apply()"）→ 队列 T1 = **READY_FOR_BOUNDED_FIX**（仍无 mandate → NO_WRITE）。关键定性：2bd3d62f 即 **PR #213 merge**（fleet 门三件套：index-bindings test / BROKER-BOOT REHEARSAL admission / scheduler-cp-fleet-gate.mjs），其提交信息明示生产字节修复归 **AGENT_PROCESS_EXITED_RECOVERY_V1**、#213 刻意不碰 broker index.js → 判读=生产或已热修而 **main 字节仍带缺陷**，收敛待 Owner/owning Goal 澄清。
- **forum #17 = Owner MERGED**（09-08T00:53:58Z，f93d34de=main tip）→ 队列 PR_17 消解；**#19（L0 truth）revalidated**：head 09d900c 未变 + 对新 main MERGEABLE/CLEAN → 仍 WAITING_OWNER_DECISION。
- 各仓 main 前进全部定性为 Owner/actor 授权工作流：svc identity-reconciliation（#30-32→5e37d9a）/ auth life-workbench+FMG retarget（#63→a15ce50a）/ mobile Presence 线（#15/#17→8e8d2e60）/ vehicle-pet 灵动 COMPLETE（→b64e2d0d）/ dsh #213+#211。零冲突、零新 blocker。
- OWNER_DECISIONS_PENDING 增补：**dsh T1 修复授权**（最小修=一行 local import）+ T2-T15 调查授权（queue @ L58-156）；既有 #196 / #19 / L0-DEPLOYMENT / svc#22 / auth#36 / HR A|B 不变。
- WAKE 链交接：tonight_mode released（SUPERVISE 原值存档）→ 00:00-08:00 WAKE 将零模型 NOOP（W1/W3）；Owner 夜间注入新活则 W4 接管。

### OWNER_NIGHTLY_MUTATION_MANDATES_2026_09_07（2026-09-07 晨 Owner 颁发；已写入 Repair Queue 归并节 mandate_ref；供今晚 supervisor 消费）

目的：让今晚 NIGHTLY_CONTINUOUS_REPAIR_QUEUE_PILOT_V1 有真实、合法、低风险工作可消费。不创建 task sentinel、不改 23:00 schedule、不要求优先顺序（supervisor 仍按 Repair Queue 自己选择）。**mandate_ref = OWNER_NIGHTLY_MUTATION_MANDATES_2026_09_07**，本节即 mandate durable 正文；Repair Queue 归并节对应条目已挂 ref。

**MANDATE A — FORUM_L0_DOC_TRUTH**：TASK_ID = `forum-l0-doc-truth-correction`，REPOSITORY = mayf3/agent-forum，SCOPE = documentation truth correction only。允许：fresh-read current main、确认 root enforcement/workflow 实际状态、修正文档中把未部署 L0 说成已部署的表述、isolated branch、测试/文档检查、push、Draft PR、independent review。禁止：新增/修改 GitHub workflow、branch protection、ruleset、required checks、platform settings、production/config mutation。DONE_WHEN：文档与实际 enforcement state 一致 + 无产品/平台行为变化 + Draft PR 创建 + STOP at Owner boundary。若事实已变化、L0 已真实部署 → NO_WRITE + RECLASSIFY。

**MANDATE B — DSH_CODE_1_AGENT_SWITCH**：TASK_ID = `dsh-agent-switch-dsh-tools-resolution`，REPOSITORY = mayf3/dsh-agent-core。第一阶段必须只读判别：fresh current main、repo-supported install、npm ls @deepseek-ai/dsh-tools、npm explain @deepseek-ai/dsh-tools、focused agent-switch tests；确认是否仍解析到 `0.0.0-unit-test-passthrough`，及真实 repo-supported dependency closure 能否得到可用 dsh-tools。**Branch 1**（机械证明最小 peer/version constraint 修正即可让 repo-supported install 稳定解析真实兼容版本且 focused tests PASS）→ 允许 minimal dependency metadata fix、focused tests、必要 regression、candidate branch、Draft PR、independent review；禁止借机重构 agent-switch。**Branch 2**（必须手动注入 dependency/特殊本地环境/未定义 supply contract/新 package topology 才能通过）→ NO_WRITE，STATE = `NEEDS_DEPENDENCY_SUPPLY_CONTRACT_INVESTIGATION`，保存判别证据后去做下一队列项。

**COMMON BOUNDARY**：两任务 AUTO_READY/AUTO_MERGE/AUTO_DEPLOY=false；不得因本 mandate 扫描新问题/扩大 scope/创建第三个写任务/修改 Runtime/修改 nightly infrastructure；今晚仍 MAX_CONCURRENT_MODEL_CALLS=1、08:30 无新模型工位、09:00 硬停止。本 mandate 即 CODE-1 的 align-2 写槽处置（Owner 行使）；admission 其余条件照查。

**【机械层覆盖指令（给 23:00 会话；白班 plan 干跑实测 07:33）】** dispatcher plan 对这两项的机械处置是硬编码产物：CODE-1 → `SKIP_QUEUED_FINDING`（状态硬编码，mandate 检查不达）、FORUM-L0-DOC-TRUTH → `NO_WRITE_NO_MANDATE`（note 硬编码不含 mandate、ledger 无注册项）。**Owner mandate 颁发后，对且仅对这两个 TASK_ID：把 plan 的上述处置覆盖为 mandate-bound 写候选**（MANDATE A 走 READY_FOR_TRIVIAL_FIX 直改路线或 six-pack 均可，终点 Draft PR + independent review；MANDATE B 先执行只读判别阶段再按 Branch1/Branch2 分叉）。覆盖后仍须过 admission 其余全部条件：ledger write slot free（干跑实测 occupied_write_slots={} ✓）、Base/Authority drift cleared（fresh re-read origin main + bounded impact）、current need freshly demonstrated、existing legal execution route；每次 spawn 前 pre-spawn-gate 照过。其余全部队列项仍严格按 plan 处置，不因 mandate 扩围。mandate 禁改 nightly infrastructure → dispatcher 代码零改动（本覆盖走 durable 指令层）；下一位 Runtime 开发 Goal 可把 mandate_ref 感知并入 plan 解析器（仅记录，今晚不做）。

### NIGHTLY_ADD_MOBILE_AND_VEHICLE_PET_V1（2026-09-07 夜 Owner 设立；白班预登记，今晚同一 supervisor 消费）

- **新增两 READ_ONLY 任务进今晚连续循环**：TASK C = `mobile-current-work-triage-20260907`（mayf3/agent-core-mobile，main 给定坐标 e1aa6366…；只做 current-main baseline + open PR #8/#10/#11/#12 逐项 fresh triage + authority/dependency + Owner/blocker 分类；**NO NEW MOBILE PRODUCT WRITER**——禁实现/accept Spec/merge/deploy/设备修改/绕过 device blocker/代 Owner 视觉产品 acceptance；maintenance defect → QUEUED_VALIDATED_FINDING 入队今晚不修）；TASK D = `vehicle-pet-maintenance-scout-20260907`（mayf3/vehicle-pet，main c3d1d4e7…，OPEN_PRS=0；十项 scope 只读 scout，自读完整 applicable authority inventory；**MAX_VALIDATED_FINDINGS=3**，HEALTHY_NO_ACTION 合法；仅 Scout authority 零 mutation——READY_FOR_TRIVIAL_FIX/SIX_PACK 发现也只 record → queue）。完整 scope/边界/分类集/DONE_WHEN 以 Repair Queue 归并节对应两块为准。
- **Dispatcher 机器 gap 处理（Owner 本 Goal 显式授权）**：仅对此二 TASK_ID `FORCE_CLASSIFICATION = EXECUTE_READONLY`——read-only admission override，**非 write-authority override**；不影响任何其他 queue item；执行顺序仍由 supervisor 按现有 priority + queue 状态选。机器层 plan 不含这两个新项（解析器硬编码固定 item 集）→ 与 mandate A/B 同属 durable 指令层覆盖（prompt + 本节 + queue 三层）。
- **连续循环同一**：disposition → persist → update Repair Queue → fresh-read → 下一合法任务；今晚可能消费 Forum L0 / DSH CODE-1 / Mobile triage / Vehicle-Pet scout（顺序不固定），完成第二项不得退出。Mobile/VP read-only disposition **可计入 PASS 判据的 different task dispositions，但不得伪装成 Draft PR**（≥1 real candidate/Draft PR/review 仍须来自真实写任务）。
- **晨报追加字段**：MOBILE_BASE / MOBILE_OPEN_PRS_TRIAGED / MOBILE_NEW_FINDINGS / VEHICLE_PET_BASE / VEHICLE_PET_TEST_STATE / VEHICLE_PET_VALIDATED_FINDINGS / VEHICLE_PET_QUEUE_ITEMS_ADDED；MODEL_CALLS_AFTER_08_30 = 0 new stages、MODEL_CALLS_AFTER_09_00 = 0 硬验收不变。
- **ABSOLUTE BOUNDARY**：两新仓 AUTO_READY/AUTO_MERGE/AUTO_DEPLOY=false；不发明 speculative work / 不 accept Specs / 不建 arbitrary product features / 不 device mutation / 不改 GitHub settings。
- schedule 仍 `0 23 * * *`；nightly infrastructure 零改动（dispatcher/watchdog/Runtime 代码未动，override 走 prompt/GOAL_STATE/queue durable 层）。

### OWNER_MERGE_EXECUTED — align-2 终局闭合（2026-09-07 12:59Z Owner 决定行使）

- **#192 = MERGED**（mergeCommit = `485e7fbda7c22f37c818a0af3dd1516b31b64440` = 新 main tip；mergedAt 2026-09-07T12:59:37Z；Draft→ready 为 merge 机械前置）。merge 前置六项 fresh 全过：PR OPEN / head `7714e322` / changed_files=1 / 恰 `packages/agent-router/test/feishu-regression.test.js` / **relevant drift=NONE**（main 期间又前进 597bac4→6d609c2，增量仅 product-api workflow-admission src+test，与 agent-router/TRUSTED_INGRESS/feishu 零交集）/ MERGEABLE。
- merge 后 fresh verify：`origin/main:…/feishu-regression.test.js` blob = `fcf899290b6241adc74346773f2c4c625c095223` == #189 reviewed blob ✓；并在 merge 后新 main 上 detached worktree 实跑 target test = **9/9 PASS**（探针 worktree 已清理）。
- **#189 = CLOSED_UNMERGED**（reason=FULL_SIX_PACK_EVIDENCE; clean integration landed via #192；head fbbe8c03 关闭时实测未变）；**#177 = CLOSED_UNMERGED**（reason=SUPERSEDED_BY #189/#192）。
- **Repair Queue 已更新：dsh-trusted-ingress-align-2 = CLOSED / LANDED_VIA = #192 / FULL_SIX_PACK_EVIDENCE = #189 / SUPERSEDED_CANDIDATE = #177**（归并节 + 顶部状态表同步）。
- 边界：未 deploy；未顺手处理其他 PR；未动 nightly supervisor/automation/dispatcher/watchdog/queue 执行语义/并发/夜窗。注：dispatcher plan 对 align-2 行的处置是硬编码（SKIP_SLOT_OCCUPIED）——任务已 CLOSED，skip 仍为正确结果（ledger 无 IN_PROGRESS、dsh 写槽空闲，今晚 CODE-1 mandate B 可正常 admission）；plan 硬编码的 mandate 感知改造仍留下一 Runtime 开发 Goal。
- 遇到的瞬态：gh API 两次 `EOF`（merge 首试、#177 close 首试）重试即过；merge 首次实质失败原因 = Draft 未 ready（`gh pr ready` 后即过）。

### DSH_ALIGN2_FINAL_CLEAN_PR_V1 终局（2026-09-07 白班后续；Owner G1 终裁 + remote 写授权行使完毕）

```text
CURRENT_MAIN               = 597bac4a8438cad0d3166c808b07c7bf9c815658（fresh fetch == Owner 证据值；5 commits > 75d25914 全为 docs native-arm64 面）
BOUNDED_IMPACT             = PASS（packages/agent-router 零触碰；test 文件 ≡ TASK_BASE pre-fix blob；新增 spec DSH_NATIVE_ARM64_RUNTIME_V1 与 TRUSTED_INGRESS 无关 → NO_REPLAY / NO_REBASE_REQUIRED_FOR_AUTHORITY）
REMOTE_CLEAN_HEAD          = 7714e322ccdc458653743d292857a4469b98ed6f（origin/integration/trusted-ingress-feishu-regression-clean 实测）
REMOTE_CLEAN_TREE          = 26f124f07299434e617d085727150686fc551aa7
DRAFT_PR                   = mayf3/dsh-agent-core#192（base main；isDraft=true；OPEN；MERGEABLE；正文含 PRODUCT_CHANGE/FULL_SIX_PACK_EVIDENCE(#189@fbbe8c03)/CLEAN_INTEGRATION_SOURCE(7714e322)/G1_DISPOSITION/SEMANTIC_DELTA=NONE + fresh evidence + DO_NOT_MERGE）
CHANGED_FILES              = 1（gh pr diff --name-only 实测）
SIXPACK_ARTIFACTS_PRESENT  = NO（PR diff 零 sixpack 路径；three-dot diff 恰单路径；exclude-test diff = 空 IMPL_DELTA_NONE_CONFIRMED）
REMOTE_EXACT_HEAD_BINDING  = 6/6 PASS（headRefOid==7714e322 / changed_files==1 / 恰 test 路径 / artifacts 0 / 实现零 delta / remote test blob fcf89929==#189 reviewed blob → clean patch ≡ reviewed patch）
READY_FOR_OWNER_MERGE_DECISION = YES（ALIGN2_FINAL_CLEAN_PR；未 merge / 未 mark-Ready / 未 deploy）
BLOCKERS                   = 无
```

- Owner G1 终裁已应用：FINAL_PRODUCT_ASSET = test 文件一件；qa-pair（qa.automation.json + qa_required_checks.sh）终裁 EPHEMERAL、不做 BASE 自适应改写、通用 QA automation = SEPARATE_GOAL_REQUIRED（与白班 fresh inspection 实证一致，candidate 形态零变更）。
- 旧 PR：#189 = KEEP OPEN/DRAFT（FULL_SIX_PACK_EVIDENCE，immutable head 不重写）；#177 = SUPERSEDED / OWNER_CLOSE_ALLOWED（不自动关；等 clean PR #192 终裁后一并清）。
- 边界：未动 automation-9952ac9c / nightly dispatcher / watchdog / queue 执行语义 / 并发 / 夜窗；今晚 continuous pilot 与本收尾完全分离。
- 证据：reports evidence/dsh-agent-core/DSH_G1_CLEAN_INTEGRATION_20260907.md（FINAL 节）+ queue 归并节 FINAL_RULING_APPLIED。

### DAYTIME_NIGHTLY_RESULT_CLOSEOUT_V1 终局（2026-09-07 白班收口完成；证据 = reports evidence/dsh-agent-core/DSH_G1_CLEAN_INTEGRATION_20260907.md）

CURRENT_MAIN = 75d25914fe2a114847c7ba0e25b463c2dda29c3d（fresh fetch；与 #189 评审时 main 一致——评审后零新提交；agent-router 自 TASK_BASE 16e14233 零触碰；TRUSTED_INGRESS authority docs 零变化 → BOUNDED_IMPACT=PASS，无需 RE_PREFLIGHT）
REVIEWED_189_HEAD = fbbe8c03d0242a2d6d82bf01aff69bf120a2ced9 / TREE 9bf397860ed6a6ac368a742c692a47a4ff873e53（immutable 已核：GitHub PR#189 headRefOid + 本地对象一致；零修改）
CLEAN_INTEGRATION_HEAD = 7714e322ccdc458653743d292857a4469b98ed6f（分支 integration/trusted-ingress-feishu-regression-clean，基于 75d25914，isolated worktree ~/workspace/project/dsh-integration-clean-20260907；**本地未 push**）
CLEAN_INTEGRATION_TREE = 26f124f07299434e617d085727150686fc551aa7
G1_REMOVED = ① EPHEMERAL：specifier/coder/cleaner/architect/hardender/qa `.report.md` ×6 + specifier.behavior-spec.md + specifier.qa-procedure.md（留 six-pack ledger/receipts/evidence store）；② 暂定 durable 但 fresh inspection 实证不合格：qa.automation.json + qa_required_checks.sh——byte-identical 移植后实测 Check1(E2E) 9/9 PASS 但 Check2 exit1（脚本 readonly BASE=16e14233 硬绑定 → BASE..HEAD 扫出 29 个 main 自身非测试产品文件 → 结构性 FAIL；本质=align-2 QA 站执行自动化，非仓库长期验收资产）→ 按 DO_NOT_GUESS 分支移出候选上报，恢复形态 = OWNER_DECISION
G1_RETAINED = packages/agent-router/test/feishu-regression.test.js（byte-identical to fbbe8c03，blob fcf899290b62…；diff vs main = DELTA_IDENTICAL to #189 reviewed patch；无未授权文件）
FRESH_TESTS = target test 9/9 PASS（node v25.6.1）· 负探针（/tmp 破坏副本退回 pre-fix test）exit1 = 8/9 原始 bug 签名复现 → FAIL_AS_EXPECTED · agent-router 全套 310/310 pass / 0 fail exit0 · manifest/path = N/A by absence（候选零 sixpack artifacts、diff 恰单路径、无悬空引用）· git porcelain clean
BOUNDED_RECHECK = **ACCEPT**（fresh 独立 Reviewer 会话 6/6 项自证，含 qa-pair 判别的独立复现与 pre-fix blob≡TASK_BASE 的另证）→ **G1 = CLOSED_FOR_THIS_CANDIDATE**；**READY_FOR_OWNER_MERGE_DECISION = YES**（AUTO_READY/AUTO_MERGE/AUTO_DEPLOY=false；未 merge 未 deploy；候选 push + Draft PR 创建待 Owner 指令）
PR_177_RECOMMENDED_DISPOSITION = SUPERSEDED / OWNER_CLOSE_ALLOWED（建议，不自动关闭）
PR_189_ROLE = FULL_SIX_PACK_REVIEW_EVIDENCE（Draft/Open 原 head 不动，不重写）
OTHER_OWNER_DECISIONS_READY = 见 OWNER_DECISION_PACKETS_20260907（forum #17 / HR dispatcher topology / svc #22 re-vendor）
BLOCKERS = 无
FOLLOW_UP_DEBT = ① 候选 push+Draft PR 待 Owner 指令 ② qa-pair 是否以 BASE 自适应修订恢复为仓库资产 = Owner 裁定 ③ 候选 merge 由 Owner 行使（G1 对本候选已闭合）④ queue plan 硬编码处置的 mandate 感知改造留下一 Runtime 开发 Goal（今晚不动 dispatcher）
边界遵守：无新 Scout、无新 Six-Pack 产品开发、未动 nightly infra/schedule/queue 执行语义/并发设置。

### NIGHTLY_PILOT_CLOSEOUT_AND_CONTINUOUS_QUEUE_PREP_V1（2026-09-07 晨收口，runtime 账见 git log）


PHASE A = **#189 independent exact-head review = ACCEPT（0 blockers）** @fbbe8c03/tree 9bf39786。独立复核（非复制正文）：BOUNDED_IMPACT=PASS（main 91a836a3→75d25914 仅 production-runtime/product-api，agent-router 零触碰，TASK_BASE 不重钉）；产品唯一行为改动=feishu-regression.test.js（feishuSenderOpenId 仅来自认证 sender 元数据、text 诱饵 ou_decoy_id 不得入 trusted、freeze/no-parse 保持）；corrected 链逐 commit ownership 核（specifier 1b6c9fd 撤回 qa.automation.json/qa_required_checks.sh 违规件、coder 44e471c 测试修复、QA fbbe8c0 恰好三 QA-owned 文件、旧作废链未复用）；独立实跑=9/9 PASS + 负探针 exit1 + 全套 310/309/0/1 + clean script exit0（manifest set-equality）+ sixpack verify PASS（独立重执行）；review 分支 tree 与候选一致、认证后零变异。PR 正文 sixpack-artifacts/** 措辞 = PR_METADATA_INCONSISTENCY / NON_BLOCKING / CANDIDATE_BYTES_UNCHANGED（已记录，不改 certified Head）。G1 STILL_OPEN：不阻塞本 review，只阻塞最终 merge-tree disposition（Owner 裁决）。评审记录 = reports evidence/dsh-agent-core/DSH-ALIGN2_189_INDEPENDENT_REVIEW_20260907.md。
ALIGN_2_FINAL_STATE = TECHNICALLY_ACCEPTED / WAITING_OWNER_DECISION（DO_NOT_MERGE 维持；merge 需 G1 + Owner）
PR_177_STATE = SUPERSEDED_BY_#189 / PENDING_OWNER_CLOSE（ACCEPT 条件满足；不自动关闭）

PHASE C = **NIGHTLY_SERIAL_SINGLE_TASK_PILOT = PASS**（2026-09-06 夜，automation-5dd41c1a 哨执行）：
scheduled start=PASS / no duplicate writer=PASS / correction+replay=PASS（2 次 HeadDrift 有界纠正非盲试）/ six real roles=PASS（23:28–00:52）/ QA ownership=PASS（QA 全新建 automation、porcelain fix 生效实证、final 一次过）/ fail-closed negative probe=PASS（exit1）/ terminal verify=PASS / Draft PR #189=PASS / AUTO_READY=AUTO_MERGE=AUTO_DEPLOY=false。
如实未证明：CONTINUOUS_MULTI_TASK_NIGHTLY = NOT_YET_PROVEN；TWO_WORKER_CONCURRENCY = NOT_PROVEN；OUTCOME_UNKNOWN_SAFE_RECOVERY = NOT_PROVEN。不扩大 claim。

**09-08 凌晨补全（02:1x–02:2x，窗口内）**：PR #196 与 #19 的 independent exact-head review 已由
fresh GLM 会话（glm-role-exec 通道，author≠reviewer）完成——**双双 ACCEPT / 0 blockers**（reviewer 自行
机械复现全部声明：#196 = diff 单行/BASE ETARGET 复现/解析 0.1.0-rc.8 为 range 最高可装版本/5/5/范围纪律/
drift 无关；#19 = 单文件纯文本/三实况复核/无残留假声明；各附非阻塞 FOLLOW_UP 一条）。两候选终态 =
**REVIEW_ACCEPT / WAITING_OWNER_DECISION**。日志 = reports evidence/{dsh-agent-core,agent-forum}/PR{196,19}_INDEPENDENT_REVIEW_20260908_glm.log。
主链路验证完整走通：write task → candidate → tests → push → Draft PR → independent review → STOP at Owner boundary。

**09-08 凌晨收尾二（05:3x）**：supervisor 守护 daemonize 缺陷已按 PROPOSED_FIX 方案 C 修复
（double-fork detach + session-heartbeat 活性判定替代 ppid 孤儿检查 + start 前存活验证>42s；
原件备份 .pre-daemonize-fix.bak），四项零模型验收全过（存活>45s / staleness 注入自退 /
stop-file 优雅退出 / wrapper 零空转）；supervisor prompt 已同步（每步 touch session-heartbeat、
完成时 tonight_mode 释放 STANDBY）。backup 与 proposal 保留于 incident 目录。09-08 23:00 起
SUPERVISE 夜的守护存活与 wrapper 静默由本修复保障。

PHASE D = 今晚（2026-09-07 23:00）切连续消费模式：


- 唯一入口 = automation-9952ac9c `0 23 * * *`（fresh CronList 2026-09-07 晨核实：非 */10；watchdog=守护进程内置机械循环 + command-only launchd com.mayf3.sixpack-watchdog，无 model-backed 10 分钟 session）。
- automation-5dd41c1a 已 completed（runCount=1），不复活不复制；今晚无特殊哨。
- 今晚模式 = 23:00 supervisor → fresh queue → 选最高优先可执行项 → 执行 → persist disposition → fresh queue → 下一项，直至无可执行/08:30 QUIESCE/09:00 CLOSED；每次模型 spawn 先过 pre-spawn-gate；MAX_CONCURRENT_MODEL_CALLS=1。
- **CONTINUOUS_MULTI_TASK_NIGHTLY_PILOT 判据（预登记）**：≥2 个不同 Repair Queue disposition 且 ≥1 个为真实 implementation/review candidate 或 Draft PR → PASS；仅 1 个 → PARTIAL；一单后不再消费 queue → FAIL（查 dispatcher continuity，不扩 Runtime 重构）。
- queue 现状满足晨后要求（#189 WAITING_OWNER_DECISION / #177 SUPERSEDED_PENDING_OWNER_CLOSE / CODE-1 QUEUED（slot 释放后重判）/ svc#22 STALE_AS_PREPARED / forum#17 WAITING_OWNER_DECISION / forum L0 DOC-TRUTH READY_FOR_TRIVIAL_DOCS_FIX（需 mandate）/ auth#36 BLOCKED_OWNER_HELD / HR topology WAITING_OWNER_DECISION）。不重新 Scout。

### ACTIVE GOAL — NIGHTLY_UNATTENDED_SUPERVISOR_V1（2026-09-06 深夜 Owner 设立；最小强化 + DONE_WHEN 十项零模型验证完成）

GOAL_STATUS = **UNATTENDED_SUPERVISOR_READY_FOR_SERIAL_PILOT = YES；TWO_WORKER_CONCURRENCY_READY = NO**（未跑真实 product mutation；不重构 Runtime；无新 DB/服务/Dashboard）
实现（全部零模型，扩展 nightly-1/bin/nightly-dispatcher.py + 改造 automation-9952ac9c 单一自动化双模式）：
- **Supervisor lifecycle**：START 23:00（supervisor start 启动零模型心跳守护 = flock single-controller 原语 + 30s 心跳 + 采样 glm-role-exec 进程数 → MAX_OBSERVED_CONCURRENCY；父会话死亡孤儿自退出）/ QUIESCE 08:30（supervisor stop + 只许收尾）/ CLOSE 09:00 硬闸。
- **Watchdog**：纯机械每 10 分钟（23:10–08:20 自限），四检查（window open / supervisor PID+心跳 / single-controller / ledger readable），decision = NOOP（alive / STANDBY 夜 / 有 model workers=既有授权 controller 在跑，绝不冻结哨的合法工作）/ RESTART_SAFE（absent+无 in-flight → 从 durable state 接管重启，start_retries.json 累计单一 incident 不重复通知）/ RESTART_WITH_FROZEN（in_process 无 worker = uncertain → 自动记 OUTCOME_UNKNOWN、no redispatch、continue other lanes）。
- **事件驱动**：stage receipt → 立即下一 stage（sixpack ledger 驱动原生）；terminal → 立即重读 queue；无任务 → IDLE；禁固定时间轮询模型。
- **Provider transient**（classify-retry 子命令，机械四证明 = 无 model/session 执行 + 无文件 mutation + 无 candidate commit + 无 durable receipt）：429/限速/会话建立前 502/503/连接失败 → SAFE_TO_RETRY（Retry-After 优先，否则 2/5/10/20/30/30 分 ±10% jitter，MAX_TRANSIENT_START_RETRIES_PER_STAGE=6 → DEFERRED_RATE_LIMIT；不计 semantic correction；等待不阻塞其他 lane）；执行已开始/证明不齐 → OUTCOME_UNKNOWN AUTO_RETRY=NO 保全 worktree/refs/status/日志/input head；测试失败/QA FAIL/REVISE → 既有 correction→replay（MAX_CORRECTION_ROUNDS_PER_NIGHT=2 → DEFERRED）。
- **Draft PR = 自动写终点**：…→ push candidate branch → Draft PR → independent exact-head review → STOP（stop-line 子命令：ACCEPT→WAITING_OWNER_DECISION；REVISE→预算内 correction 否则留 Draft PR+blockers；AUTO_READY/MERGE/DEPLOY=false）。
- **Fair scheduling**：budget-check 每任务墙钟 MAX_TASK_WALLTIME_PER_NIGHT=3h → DEFERRED_BUDGET 释放容量 pick next。
- **并发治理**（concurrency 子命令）：生产 MAX_CONCURRENT_MODEL_CALLS=1；target=2 仅当 A（zero-model two-worker claim test）/B（双 disposable 仓并发 simulation）/C（一次有界真实双任务 pilot）全 PASS；rate limit → 降 1，稳定 30 分钟恢复 2；永不自动 3。当前 A/B/C 未全过 → 保持 1。
- **Trigger 改造**：automation-9952ac9c cron `*/10 0-8,23 * * *`（validator 不收跨午夜段），prompt 模式分流 = (e) 23:00–23:09 SUPERVISOR / (c) 23:10–08:20 absent → WATCHDOG 行动 / (b) 心跳新鲜 → NOOP / (d) 08:20–08:50 QUIESCE 收尾；今晚首跑 23:00 仍走 standby 谓词（align-2 哨 pending → STANDBY）。
- **晨报**：新增 Supervisor V1 十一字段（TASKS_COMPLETED/DRAFT_PRS_CREATED/REVIEWS_ACCEPTED/REVIEWS_REVISE/DEFERRED_RATE_LIMIT/DEFERRED_BUDGET/OUTCOME_UNKNOWN/START_RETRIES/RATE_LIMIT_EVENTS/MAX_OBSERVED_CONCURRENCY/OWNER_DECISIONS_PENDING），receipts outcome 约定名自动聚合。
DONE_WHEN 零模型验证（state/dispatch/simulation-20260906/supervisor-tests/）：watchdog restart 三态+四态（RESTART_SAFE/RESTART_WITH_FROZEN/NOOP-alive/NOOP-workers）✓；429 Retry-After=90s 精确 ✓；429 fallback 退避阶梯 119.4/298.4/596.8/1193.7/1790.5/1790.5（±10% jitter）第 7 次 → DEFERRED_RATE_LIMIT ✓；pre-session 502+干净证明 → SAFE_TO_RETRY ✓；exec started 无 receipt → OUTCOME_UNKNOWN AUTO_RETRY=NO ✓；预算 3.08h → DEFERRED_BUDGET ✓；Draft PR stop-line（ACCEPT→WAITING_OWNER_DECISION；AUTO_*=false）✓；adaptive concurrency 2→（rate limit）→1→（+35min）→2，诚实复位后生产默认 1 & READY=NO ✓；08:30 QUIESCE 拒绝 ✓；09:00 CLOSED 拒绝 ✓。测试中修复三个真 bug（watch 跨午夜比较、Retry-After 从日志解析、并发提升门控）。
边界重申：本 Goal 不改 Runtime 产品源；Host V1 safe-redispatch recovery 未修复前 OUTCOME_UNKNOWN 永不自动重派；pilot 十条验收 ≠ FULL_UNATTENDED_HOST_CONFORMANCE。
- **冲突排查（2026-09-06 深夜，Owner 问询触发）**：全部 4 个 automation 复核 = 9952ac9c（supervisor+watchdog，启用）+ 5dd41c1a（align-2 哨 23:05 一次性，启用）无触发重叠；ad8fa74d（disabled+completed）与 4cf1970a（paused）不触发。发现并修复一个真实冲突：ledger 无 in_process 字段（该检测路径实际惰性），哨两个 GLM 调用之间 pgrep 空隙会使 watchdog 误判 absent→每 10 分钟重启空转 supervisor。修复 = RESTART 前先跑 plan 的 anti-churn 防抖（无可执行项 → NOOP），三分支零模型复验全过（A 实队列 IDLE→NOOP / B 有活→RESTART_SAFE / C 哨 pending→NOOP STANDBY）；trigger prompt 已同步。

### NIGHTLY_UNATTENDED_SUPERVISOR_V1 — 两个 control-plane blocker 修复 + stage-boundary 断言（2026-09-06 23:0x Owner 裁定，已修）
- **BLOCKER 1 修复**：automation-9952ac9c 恢复 `0 23 * * *`（每晚一次 supervisor 启动；今晚 23:00 fire 已按 standby 谓词判 STANDBY——tonight_mode.json=STANDBY @23:05:47 + gate/plan 存档，23:10 起**不再产生任何 model-backed scheduled session**）。10 分钟 watchdog 归属改两处：① supervisor 心跳守护进程内置机械自检循环（每 ~10 分钟 internal-watchdog-*.json：window/ledger/PID/并发采样，零模型）；② 外部兜底 = command-only launchd agent `com.mayf3.sixpack-watchdog`（watchdog-wrapper.sh：StartInterval 600s、自限 23:10–08:20、STANDBY 夜零动作、supervisor absent → start_retries.json 单一累计 incident + 仅重启心跳守护做 liveness anchor，绝不 spawn 模型工作）。
- **BLOCKER 2 修复**：daemon absent + model workers ≠ 自动 NOOP。新增 worker-inventory 机械绑定：worker cwd → `sixpack-worktrees/<task>__<role>` → task，再按 ① bindings/<task>__*.json generation == 活守护 generation → SUPERVISOR_LIVE_GENERATION；② align-2 workflow IN_PROGRESS（worktree→task + ledger + START_RECORD mandate 窗口）→ SENTINEL_OWNED_EXCEPTION；③ 否则 UNBOUND → **OUTCOME_UNKNOWN_CONTROLLER**（不据其重启 supervisor、受影响任务不重派、保全 ps/cwd 证据；无关 lane 可续）。
- **stage-boundary 断言**：新增 pre-spawn-gate 子命令——每次模型 spawn 前机械重查 window（ALLOW → 写 binding record 含 stage_input_head；DENY → spawn REFUSED + DEFERRED_TO_NEXT_NIGHT 持久化）。零模型场景全过：08:29 coder ALLOW（真实 head 19ac71a 绑定）→ 08:31 cleaner DENY/QUIESCE/REFUSED/持久化 ✓；09:30 DENY/CLOSED ✓；哨 worker 绑定 ALL_BOUND ✓；unbound → OUTCOME_UNKNOWN_CONTROLLER ✓；wrapper STANDBY 夜零动作 ✓。
- 状态保持：UNATTENDED_SUPERVISOR_READY_FOR_SERIAL_PILOT=YES / MAX_CONCURRENT_MODEL_CALLS=1 / TWO_WORKER_CONCURRENCY_READY=NO / AUTO_*=false。今晚：23:00 dispatcher STANDBY ✓、23:05 哨唯一 product-write ✓、23:10+ 无 scheduled Agent session ✓。

### ACTIVE GOAL — NIGHTLY_MULTI_REPO_REPAIR_DISPATCH_V1（2026-09-06 Owner 设立；最小实现+零模型 simulation 完成）
GOAL_STATUS = **READY_FOR_BOUNDED_NIGHTLY_PILOT**（Owner 2026-09-06 深夜收窄定案；V1 十条 DONE_WHEN 已实现并 simulation 验证；未跑真实 product mutation；不是 FULL_UNATTENDED_HOST_CONFORMANCE）
能力 claim 矩阵（勿宣称更高）：
- QUEUE_SELECTION = **PROVEN**（S1r/S4 simulation）
- WRITE_ADMISSION_POLICY = **PROVEN_BY_SIMULATION**（task 绑定 mandate 六条件；simulation 抓出并修复跨任务 mandate 误判 bug）
- WINDOW_WRAPPER_GATE = **PROVEN_BY_SIMULATION**（S2 WINDOW_CLOSED / S3 QUIESCE 拒绝）
- BASIC_LEDGER_RESUME = **AVAILABLE**（ledger/queue state reload；既有 host recover 保留未重写）
- SAFE_OUTCOME_UNKNOWN_RECOVERY = **NOT_YET_PROVEN**（crash during stage / lease expiry uncertain worker / unreceipted descendant / ambiguous dirty mutation → TASK_STATE=OUTCOME_UNKNOWN，NO AUTOMATIC REDISPATCH、PRESERVE EVIDENCE、STOP AFFECTED TASK；dispatcher 已实现 STOP_OUTCOME_UNKNOWN_NO_REDISPATCH 冻结，Host V1 safe-redispatch recovery 修复前不自动重派）
- RUNTIME_WIDE_WINDOW_ENFORCEMENT = **NOT_YET_PROVEN**（窗口检查在 admission path 已有，所有 continuation path 未证明 Runtime-wide 强制；本轮不修 Runtime）
- MULTI_PROCESS_CONCURRENCY = **NOT_PROVEN**

【今晚唯一入口不变量（TODAY 2026-09-06，永久记录）】AUTHORIZED_MODEL_EXECUTION_ENTRYPOINTS = ① align-2 一次性哨 automation-5dd41c1a；② nightly dispatcher（仅 standby guard 放行后）。禁止其他 automation/cron/operator 路径调 controller.tick/drive/wake_next 启动 model-backed stage。

ALIGN2_SENTINEL_PENDING 谓词（收紧版，standby-check 子命令）：哨存在 AND enabled AND runCount<maxRuns AND 计划时刻与当前夜窗相交 AND ledger align-2 非终态/收敛/review-only；仅 YES → STANDBY。零模型测试 A–D + 附带 E 全过（state/dispatch/simulation-20260906/standby-tests/：A enabled+0/1+active→STANDBY；B maxRuns reached→DO_NOT_STANDBY；C disabled→DO_NOT_STANDBY；D align2=AWAITING_INDEPENDENT_REVIEW 而 stale 哨记录仍在→DO_NOT_STANDBY；E 计划时刻窗外→DO_NOT_STANDBY）。
Pilot 验收（首个真实 night run 仅验十条：trigger fires / single dispatcher / owner+blocker skipped / legal readonly advance / legal mandated write advance / completion→queue reread / 08:30 无新 admission / 09:00 无新工作 / 晨报与 durable receipts 一致 / 无 align-2 重复）→ 全过 = NIGHTLY_SERIAL_PILOT=PASS，仍不升级 FULL_UNATTENDED_HOST_CONFORMANCE。morning-report 模板已固定输出 BASIC_RECOVERY=AVAILABLE 与 HOST_V1_SAFE_REDISPATCH_RECOVERY=NOT_PROVEN。
边界：唯一任务源 = MULTI_REPO_REPAIR_QUEUE.md + durable ledger；只建 Repair Queue → deterministic selection → existing execution route；不建新平台/DB/Dashboard/scheduler service；不重扫仓库（新 Scout 属独立 Goal）；Controller 非第七个 reasoning Agent。
窗口：直接复用 runtime 原生三相位（controller.py window_phase：open 23:00 / quiesce_minutes=30 → ACTIVE 23:00–08:30、QUIESCE 08:30–09:00、WINDOW_CLOSED 09:00–23:00）——**Runtime 零改动**。
实现（全部复用 nightly-1）：`sixpack-forge/nightly-1/bin/nightly-dispatcher.py`（零模型纯 stdlib：`gate` 六 lane 零模型 start gate——night_window/single_controller/runtime_product_bytes（GOAL_STATE-only 前移不重审：仅比较 src/tests/pyproject 字节 diff）/ledger_integrity/write_slots/align2_state_binding；`plan` 解析 queue 归并节 → Goal 状态机 → 处置（EXECUTE_READONLY/ADMIT_WRITE_SIXPACK/NO_WRITE_NO_MANDATE/NO_WRITE_SLOT_OCCUPIED/SKIP_OWNER|BLOCKED|STALE|CLOSED|SLOT_OCCUPIED|QUEUED_FINDING|NO_ACTION）+ P0–P3 与 tiebreak 排序（候选评审 > revalidation > trivial > six-pack）；`morning-report` 11 字段骨架）。write admission 六条件（Authority/mandate/现症/slot/drift/route）缺一 NO_WRITE；mandate 必须绑定该任务（simulation 抓出并修复了跨任务 mandate 误判 bug）。
Trigger：**automation-9952ac9c** @ 23:00 daily（recurring；今晚首跑即 STANDBY——第 0 步防重 guard：CronList 检出 enabled align-2 哨（automation-5dd41c1a）则只跑 gate+plan 存档+STANDBY 晨报后退出，不重复启动 align-2、不建第二个 dsh writer、不替换哨）。
零模型 simulation 证据 = sixpack-forge/nightly-1/state/dispatch/simulation-20260906/（S1r 实队列 ACTIVE→全部 skip→IDLE_NON_OCCUPIED_REPOS，与 Owner CURRENT QUEUE EXAMPLES 逐项一致；S2 @10:00 WINDOW_CLOSED 拒绝；S3 @08:35 QUIESCE 拒绝；S4 合成多任务队列→EXECUTE_PLAN 连续消费 execution_order=[candidate-x-review(P1 评审), elig-fix(P2 six-pack, mandate=M-TEST-1)]，l0-doc-truth=NO_WRITE_NO_MANDATE；S5 gate 白天实况→仅 night_window lane FAIL 其余 PASS，按 lane 阻断验证；align-2 slot=occupied 实测识别）。
恢复语义：durable 恢复走既有 sixpack host recover + ledger（V1 不重写）；gate 的 lock/pid/in_process 检测 = single-controller 条件；晨报+receipts+queue diff = 可追溯。
STOP：本 Goal 到此为止——不为证明 V1 运行真实 mutation；今晚唯一 write 主线仍是 align-2（23:05 哨）。

### 23:05 START gate 四坐标解释 + 接管回报 ACCEPT（2026-09-06 Owner 指令；实测 19:13 +0800）
首次接管回报 = HANDOFF_RECOVERED YES（Owner ACCEPT；不重跑恢复、不改本地 main、不重写 registry、不提前启动 align-2）。四个不同概念不得混为一个 Head：
- TASK_BASE = **16e14233fbac1ccbdc00598097380da659e1ecd2**（不 rebase、不重钉）
- LOCAL_MAIN = f4bc4311…（BEHIND_TASK_BASE，仅本地 branch 状态）
- REGISTRY_HEAD = f4bc4311…（STALE_LOCAL_SNAPSHOT，不得作为远端 current-head Evidence）
- REMOTE_MAIN = 600d4df9…（bounded-impact revalidation 用的 authority branch tip）
23:05 任何模型调用前：fresh-read origin/main → 检查 TASK_BASE→REMOTE_MAIN。实测 @19:13：REMOTE_MAIN=600d4df9、delta=26 commits、变动面仅 docs/** + docs/specs/** + packages/broker/**；packages/agent-router 零触碰、目标测试文件逐字节一致。因 docs/specs/** 有变化，启动记录必答 **RELEVANT_PRODUCT_AUTHORITY_CHANGED = YES|NO**（针对 align-2 依赖的 TRUSTED_INGRESS / ordered-route-chain accepted authority 判定，不得仅凭 agent-router 未动自动判无关）。PASS 条件 = agent-router untouched AND target test unchanged AND accepted TRUSTED_INGRESS authority unchanged/supersession-unrelated → TASK_BASE 维持 16e14233；relevant Authority 被替代或语义变化 → **STOP / RE_PREFLIGHT**。
recover 边界：允许调用既有 recover 做 queue/workflow 恢复，但 recover.registry_head_drift 只反映本地 base branch，**不得作为 remote-main revalidation Evidence、不得据此宣称 HEAD_REVALIDATED=YES**；remote revalidation 单独记录。registry scan/recover 观测 stale local branch = KNOWN_HOST_DEBT（本轮不扩成新 Runtime repair task，除非实际阻塞 align-2）。
corrected replay 第一操作（进入模型工位前）：既有 correction/replay helper → **replay_to('specifier')**（或既有等价机制），完成后机械确认 stage_pointer=specifier、corrected specifier input=TASK_BASE/governed correction parent、旧 affected downstream receipts 不复用、rejected QA dirty bytes 不复用；若仍 stage_pointer=qa 或旧链被沿用 → **STOP CORRECTION_REPLAY_STATE_INVALID**；禁止直接 drive()/tick() 从旧 QA 状态继续。
Runtime 前提不变：ACTUAL_RUNTIME_REVISION=580a69d7… + reviewed porcelain-fix blobs present + QA ownership precheck PASS；若开跑前 revision 再前进只比较 Runtime product bytes，GOAL_STATE-only 前移不重审产品 fix。
当前状态 = **BLOCKER NONE**；START_PRECONDITION = remote-head + relevant-authority bounded-impact revalidation AND corrected replay must reset to specifier before model execution；KNOWN_HOST_DEBT = registry scan/recover currently observes stale local base branch, not authoritative remote branch tip。

### runtime-qa-porcelain-leading-space-fix 执行记录（2026-09-06，Owner 授权；证据 = forge/PORCELAIN_FIX_EVIDENCE.md）
- 修复（局部 seam，边界全遵守）：gitx 新增 git_status_porcelain raw seam（通用 git() 不变）→ _working_tree_changes 换用 → 守卫谓词逐字提取为 RoleRunner._product_byte_changes（可测性，语义零变化未放宽）；Host/ledger/role contracts/QA ownership 零改动。
- 回归测试 9 项：T1 首行 tracked QA-owned 精确路径（含 seam 直测 + staged 变体）、T2 QA-owned tracked 修改全接受、T3 product mutation 仍拒（单独+混合）、T4 untracked 折叠不回归、T5 多条目全完整路径、空格路径。
- 质量门（exact head 实跑）：116 tests passed + ruff clean + mypy strict clean + 零模型 precheck 修复后五项全 PASS（修复前 FAIL 证据同存）。
- ALIGN_2 恢复三条件（Owner 指令）：PR #3 独立 review ACCEPT + 实际运行 revision 含 reviewed fix bytes + QA ownership precheck PASS → 才重排 align-2 有界 corrected replay 窗口。当前 = NO。

### QA ownership precheck 结果（2026-09-06，Owner 指令，零模型调用）
**VERDICT = FAIL ⇒ ALIGN_2 = BLOCKED_RUNTIME_ADAPTER_MISMATCH**；证据 = sixpack-forge/nightly-1/state/qa-ownership-precheck-2026-09-06/（README 根因 + precheck-result.json + run/converge logs；探针脚本 nightly-1/bin/qa-ownership-precheck.py 可复跑）。
- **根因（已 micro-repro 实证）**：`gitx.py:44` 的 `git()` 对整个 stdout `.strip()` 剥掉 porcelain **首行的前导空格**（` M path` → `M path`），`runner.py:732` 的 `line[3:]` 随即吃掉路径首字符 → `'sixpack-artifacts/…'` 变 `'ixpack-artifacts/…'` → allowlist 前缀匹配失败（runner.py:532-546）→ `SelfCertificationRejected` 对 QA-owned tracked-artifact 编辑**误触发**。
- **影响面**：仅 `_working_tree_changes` 的两个消费点（QA 自认证守卫 :533、final-QA 零变更守卫 :611）且仅首条 ` M `/` D ` 类 porcelain 条目；QA 全新 untracked 文件（折叠 `?? sixpack-artifacts/`）不受影响（探针 4a PASS）。
- **探针结果**：0 运行时字节==4199be02 **PASS**（缺陷潜伏于受审字节，非本机漂移）；1 qa_automation_paths=`["sixpack-artifacts/"]` **PASS**；2 完整路径 **FAIL**；3 allowlist 判定 **FAIL**；4a/4b 行为探针+负对照 **PASS**；5 final QA 路径序 **PASS**。
- **结论修正**：昨夜 08:46 QA 重放被拒的直接机械原因是本缺陷（QA 当时编辑的正是 QA-owned 文件，本应 ALLOWED）——correction #3 的 reason 需据此补记；Owner 的 ownership 裁定与 corrected replay 计划**本身不变**（specifier 双重违规仍是事实），但执行被本缺陷阻塞。
- **STOP 遵守**：未修 runtime 字节（修复须走 Owner 授权的受审流程）；未转移 QA automation；未放宽守卫；未改 ownership；未手工绕过；哨 automation-9b5a80be 已删除（零模型调用消耗于今晚窗口）。
- **TASK_BASE 不变** = 16e14233fbac1ccbdc00598097380da659e1ecd2；启动前远端 main 前进仍按 bounded impact 规则执行（无关变化不重钉；agent-router/accepted Authority/测试依赖相关变化则 STOP→re-PREFLIGHT）。
- **NEXT（待 Owner）**：授权 runtime 缺陷修复候选（gitx strip/porcelain 首行处理 + 回归测试；修复属 runtime 产品字节，须按 B-QA-01 同标准受审）或指定其他处置；修复受审后再排 corrected replay 窗口。

### 下一夜窗口授权（Owner 2026-09-06，已入 ledger task_status + START_RECORD）— 被上述 BLOCKED 取代，未行使

### 上一轮收口确认 + correction #4 最终版（2026-09-06 Owner 指令）
- QUIESCE 收口确认正确（09:00 窗口结束，control-plane only）。
- **违规范围扩大认定**：specifier @ 9f1ec2c 同时错误提交了三类非本工位所有物——① packages/agent-router/test/feishu-regression.test.js 修改（CODER OWNS TDD/tests/implementation）；② qa.automation.json（QA OWNS manifest）；③ qa_required_checks.sh（QA OWNS executable automation）。
- **corrected replay 全链**（今晚执行）：specifier replay（只保留/重建 specifier 拥有的行为规格、QA procedure、station evidence；**必须撤回测试修复与两个 QA-owned 文件**；不替 coder 重做修复、不替 QA 修 automation）→ coder replay（从 corrected specifier Head 重施 accepted TRUSTED_INGRESS 测试对齐 + coder-required verification）→ cleaner→architect→hardender 正常重过 → QA replay（从"不存在 QA automation"的 upstream candidate 起自己创建并提交 qa.automation.json/qa_required_checks.sh/qa.report.md；fail-closed 四要件：set -euo pipefail / test 失败传播非零 / canonical checks 机械断言 / manifest 一致性机械断言；无一次性硬编码 /tmp runtime 除非 exact governed input；commit 后对该 unchanged exact Head/tree fresh final QA；final 后不得改 certified bytes）。受 corrected upstream Head 影响的旧 receipts 一律不复用。
- rejected QA attempt：DIAGNOSTIC_EVIDENCE_ONLY（证据目录 nightly-1/state/rejected-qa-attempt-align-2/）；重放时 prove no accepted receipt / prove no downstream handoff → remove/reset managed worktree → fresh replay；不得 cherry-pick 其 dirty bytes。

### 下一夜窗口授权（Owner 2026-09-06，已入 ledger task_status + START_RECORD）
- WINDOW = 2026-09-06 23:00 → 2026-09-07 09:00 Asia/Shanghai；SCOPE = align-2 corrected replay only + terminal verification + review branch / Draft PR exposure。
- mandate_ref = **OWNER-MANDATE-2026-09-06-ALIGN2-CORRECTED-REPLAY-WINDOW**（仅此一夜此一任务，不形成长期 standing nightly mandate；已引用于 nightly-1/state/START_RECORD_20260906_align2_corrected_replay.md）。
- 一次性哨 automation-9b5a80be @ 23:05（window 检查/pin==base==16e14233 校验/corrected replay 全链/gates 不降门禁/STOP 条件/晨报格式均已写入哨 prompt）。
- 今晚完成标准（全部满足后停止）：corrected specifier Head / coder-owned test fix / downstream replayed / QA-owned automation freshly committed / fresh final QA PASS / fail-closed negative probe PASS / target regression PASS / agent-router regression PASS / terminal verify PASS / Draft PR created / independent exact-head review surface ready。
- STOP 条件：任何新的 ownership / HeadDrift / ambiguous mutation → STOP 受影响任务、保全证据、不造 bypass；不为赶窗口降低门禁。
- 继续：AUTO_ACCEPT=false / AUTO_MERGE=false / AUTO_DEPLOY=false / NO production mutation / NO Ready / NO merge / NO deployment。

### B1 替换候选执行记录（2026-09-06 白天窗口 07:36–08:50）
- **bounded impact/preflight 重做（Owner 指令，dsh main 前进后）**：origin/main = 16e14233fbac…（PR #176 fleet-shared-codex-bootstrap 合入）；797952e7..16e14233 仅触碰 packages/production-runtime 两文件，packages/agent-router 零改动，目标测试文件与冻结 base 逐字节相同 → 新 Base = 16e14233，修复本体可干净移植。
- **新任务 dsh-trusted-ingress-align-2**（base_head=16e14233；B1 四要求逐条编码进 goal/done_when：fail-closed 脚本、真实 CRAP/DRY/结构检查 vs BASE..HEAD + governed NOT_APPLICABLE、manifest 断言、去 /tmp/node 硬编码改 SIX_PACK_NODE_PATH）。
- **执行**：specifier 07:52 → coder 07:58 → cleaner 08:13（重放1）→ architect 08:23（重放2）→ hardender 08:28 → QA 重放3 08:41（实活完成但被守卫拒）。全部真实 GLM glm-5.3-flash 经 forwarder；窗口 ACTIVE 内派发。
- **四次 correction（ledger corrections[] 全记录，非盲试）**：
  1. cleaner 空候选（未写强制工位报告）→ done_when 加 STATION MANDATE → 重放成功；
  2. architect 同模式（真跑了 verify-code-structure.mjs 但零文件）→ 加 last-action 报告指令 → 重放成功；
  3. QA 撞自动化门（上游提交的 manifest 用单数 entrypoint，门要求复数 entrypoints）+ QA 负探针写 /tmp 被 opencode external_directory 自动拒 → 加 manifest-gate-schema + 探针 worktree 内指令；
  4. QA 重放实活全部完成（manifest 已改对、脚本已增强、qa.report.md 已写）但 SelfCertificationRejected——根因 = 本次上游工位按 goal 预提交了 qa.automation.json/qa_required_checks.sh（成产品字节），QA 修改即自认证（守卫工作正常）。**correction #4 = 两步：hardender 归一 manifest schema → QA 重放且不碰上游字节；已入 ledger，今晚 23:05 哨 automation-064f835b 执行**。
- **守卫实弹（本轮新增 4 类真实触发）**：空候选拒绝 ×2、自动化门拒绝（entrypoints schema）、QA 自认证拒绝——helper/门/守卫全部按设计工作，runtime 字节零修改。
- **09:00 窗口语义实测**：08:46 起相位 = QUIESCE（新模型工位按 ACC-MRH-003 拒绝）→ host quiesce 收口，in_process 清空、状态落盘。
- G1 SPEC_GAP：artifact retention（六份 station narrative report 是否进 consumer merge tree 无足够 Authority）——只阻塞 #177 merge 路径，不暂停其他仓。
- 三仓只读核验（并行）：svc-workflow #19 / auth-service #36#39 仍 OPEN 未变（授权缺口未解除，NO_CHANGE）；agent-forum automation CI 失败仍在（Owner 权限决策 pending）；dsh-agent-core 无新 open issue。未启动任何新写任务（dsh 单写位被 align-2 占用；其余仓无授权缺口闭合项）。
- NEXT = 今晚 23:05 automation-064f835b：correction #4 两步重放 → 收敛 → verify → fresh 测试（9/9 + fail-closed 负探针 + agent-router 240）→ review/dsh-trusted-ingress-align-2 分支 + Draft PR（引 #177/5123376463 lineage）→ 晨报。STOP at Owner decision。

### FOLLOW_UP_DEBT — 夜间工具问题（2026-09-06 Owner 归档指令；不阻塞 PR #177 评审；下次长期无人值守夜间运行前须形成独立 tooling candidate 并审查）
1. registry pin 被 recover 以本地分支 head 重写（01:56 实录；影响检查后恢复）。
2. restart/resume 启动逻辑：cmd_run 无条件 admit 与断点 workflow 冲突 → 现以启动器 recover()+drive() 规避（未改 runtime）。
3. BSD mktemp 模板后缀兼容（glm-role-exec.sh）。
4. OPENCODE_CONFIG 错误路径 → opencode 静默回落全局配置打向 api.anthropic.com（"GLM 500" 实为误诊；GLM 端点健康）。
5. GLM forwarder：bun 直连 bigmodel TLS 500、经本地转发 200（bin/glm-forwarder.py 现役）——环境级根因未定。
6. QA mechanical-format adherence：4 次有界纠正重放（check 名逐字/automation 平铺/manifest/entrypoint 裸文件名）。
另记：GLM 1302 限流退避与 1308 五小时用量上限停机规则已验证有效。

### 多仓受限流水线 — 常设规则（2026-09-06 Owner 指令，自本 PHASE 起生效）
- 授权维护仓 = mayf3/{dsh-agent-core, svc-workflow, auth-service, agent-forum}；并发继续 MAX_IN_PROCESS_PER_ROLE=1 / MAX_ACTIVE_WRITE_TASKS_PER_REPO=1 / AUTO_*=false；新增 MAX_CONCURRENT_MODEL_CALLS=3（稳定后逐轮 4→6，不一次突破 accepted invariants）。
- 双 lane：Governance lane（现行 authority 核验→proposed 修订→独立 Review→Draft PR→STOP at Owner；纯 authoring 不强迫进 Six-Pack）；Implementation lane（current-base 可复现非平凡代码问题+本仓 Authority+PREFLIGHT 通过→六工位→terminal verify→独立 Review→Draft PR→STOP at Owner）。
- 选单：每个历史问题先在精确当前 Base 上证明仍存在；过期待办 NO_CHANGE 关闭本轮不造 diff；执行 Agent 只能在四仓+既有问题来源内选下一项；Controller 不得自创任务/产品规则。
- 每仓最多一个活动写候选；不同仓可并行成 Draft PR；独立 Reviewer 不得由候选作者充当，可并行但不改候选。
- REMOTE_WRITE 扩围（仅此两项）：create/update dedicated candidate branch + create/update Draft PR。明确禁止：mark Ready / accept proposed Spec / merge / deploy / production mutation / Grant-Credential-Secret changes / branch protection changes / force-push shared branch。
- 优先序：1) current-base 核验 2) 有依据治理 Draft PR 3) 已授权代码缺口 Six-Pack 修复 4) 已完成候选独立 Review。不建 Dashboard/飞书/Workflow 集成，不为优化夜间系统暂停真实仓库工作。
- 晨报按仓列：REPOSITORY/TASK/OUTCOME(NO_CHANGE|DRAFT_PR|BLOCKED)/BASE/HEAD/PR/TESTS_ACTUALLY_RUN/INDEPENDENT_REVIEW/OWNER_DECISION_REQUIRED。成效度量 = 有效关闭的陈旧问题 + 可审阅 Draft PR 数，不是模型运行数。
SIGNOFF_REQUESTED_AT = 2026-09-05T18:20:00+08:00（4 项已逐项正式提请 Owner 确认；尚未签署；不代签、不把沉默当同意）
OWNER_CONTINUED_AT = 2026-09-05T21:19:00+08:00（Owner 回复"继续"：按仅推进非签字项处理；启动脚本安全路径已实测——窗口外 WINDOW_CLOSED 正确拒绝 exit 5，registry heads 顺带刷新）
STAGED_EXECUTION = 签字齐备后执行序列已一键化：nightly-1/bin/start-nightly-run.sh（刷新 heads→窗口相位检查→sixpack run 六角色）→ 完成后 nightly-1/bin/morning-report.sh（verify+状态→晨报 markdown）

### 优先级纠偏（2026-09-05T21:45 Owner 指令，对 ACTIVE GOAL 生效）
- **交付物重定义**：本轮交付 = 其他仓库中的实际修复候选，含问题依据、改动内容、精确版本、实际测试、限制、独立审查状态。"启动脚本准备好了"与"发现一批问题"均不算本轮交付。
- **集成冻结**：本阶段不做 Six-Pack 与飞书、Workflow、ADC、Agent 记忆系统的集成；不把 Dashboard、系统集成、新治理平台、统一发行加为前置条件。前置条件维持 Owner 授权 / 仓库范围 / 模型窗口 / 实际运行版本 / 安全停止机制五项，无新增。
- **仓库角色**：dsh-agent-core、auth-service、agent-forum、svc-workflow 等首先是维护对象，不是集成依赖；实际执行限于既有 registry 已确认的首批 2 仓与既有任务授权范围（REGISTRY_EXPANSION=FORBIDDEN 不变）。
- **流程分流**：纯规范纠偏走既有 AUTHOR/REVIEW 流程（governance 仓 PR）；非平凡实现修复按 Six-Pack 执行；不为让六个工位都忙而制造工作。
- **缺口处理**：长期规则/授权存在缺口时，只暂停依赖该缺口的任务并给出最小待决策项，继续处理其他合法任务。
- **运行时自律**：runtime 自身只有出现直接阻止本轮任务的缺陷才修；夜间工作不得变成 Six-Pack 自身开发。
- **交付形式**：REMOTE_WRITE=false（无既有远端写授权）→ 本轮产出可审阅本地候选（worktree 分支 + receipt 链 + verify 报告）；仅当存在既有远端写授权时提交 Draft PR。不自动接受规范、不自动合并、不部署、不扩大权限。
- **首批规模**：小范围，每仓最多一个活动写任务。

### 任务候选重筛（沿用既有盘点 forge/inventory/INVENTORY_LEDGER.md @ 2026-09-04，未重新调查）
按 Owner 五条标准（有明确问题来源 / 当前版本仍可复现 / 既有规则与任务授权足以支持修复 / 测试环境可用 / 能在有界范围内交付修复候选）：
- **合格（唯一进入本轮的写任务）= af-verifier-impl-1（agent-forum）**：来源 = PR #15 + canary spec af-verifier-1 @ b89f370 + TASK-AF-001 盘点坐标（明确）；PR #15 三套件已在一次性 PG 实测全 PASS、node v26.7.0（可复现 + 测试环境可用）；authority=fcd417ba、profile=SIX_PACK_V1（既有授权足以支持）；改动界 = 仅 svc-forum/package.json 接线 3 个既有 npm 入口（有界）。每仓 ≤1 活动写任务满足。
- **暂停（依赖授权缺口，最小待决策，不进本轮）**：TASK-DAC-001（dsh-agent-core：修正案 lifecycle acceptance 未完成 + 非 registry 首批）、TASK-SVW-001（svc-workflow：Execution Mandate 未核实 + 非首批）、TASK-AUT-001/002（auth-service：CONTROLLED 凭据 mandate / Owner 权链未核实 + 非首批）。
- **待 Owner（无决策不动）**：OWN-DAC-001 breakglass、OWN-ADC-001 secrets、OWN-AF-001 分支合并处置。
- 不为凑任务新增候选；纯规范项继续走 governance 仓既有流程（GOVERNANCE_LANE 清单不变）。
UPDATED_AT = 2026-09-05T22:40:00+08:00

## Owner 决定执行记录（2026-09-05T21:45 Owner 决定 → 22:40 执行完毕，全部有坐标）

1. **Host r4 — 已接受并合入治理仓库**。合并前 final-head recheck 全部成立：PR #14 head = 8186595a9abb93bfdb75c21c6d0be9e93abdc863（未变）、tree = ff4e78a0（fresh clone 实测）、spec 字节 sha256 = 1bd455b0…（docs/specs/AGENT_MULTI_REPO_SIX_PACK_HOST_V1.md 实测，与账面 r4 一致）、独立评审 5119235263 正文 ACCEPT 且绑定同一 commit、PR OPEN/MERGEABLE。**PR #14 merge commit = 68e4e743886e1266b0c3a3a30192b3c11dc53535（2026-09-05T22:11:26+08:00）**。生命周期接受变更 = governance main **9dcd0c4**（diff 恰好 2 行：status: proposed→accepted + OPEN_OWNER_DECISIONS 决议记录；规范内容字节零改动）。规范含义未动。
2. **Runtime — 运行版本已按决定固定；PR #2 保持 Draft**。运行版本 = v0/bootstrap @ c07c7fd（其后各账目提交同理）：src/ tests/ pyproject.toml 与受审 4199be02 diff = **空**（本机实测），仅 forge/ 账目与 nightly-1 脚本变化；加载路径 = 本仓 .venv editable 安装，start 脚本 gate 强制产品字节 == 4199be02 否则 exit 7。PR #2 = Draft/Open @ 4199be02，按 Owner 决定不合并。
3. **首张维修单 af-verifier-impl-1 — 开工前核验判废，未开工**（依据齐全）：
   - 授权前提「svc-forum/package.json 三个 test:subscription-* 入口尚未接线」在受审 base c2f7a74 上**不成立**：三入口由 c2f7a74 本身（commit "test: add Forum subscription verifier hardening"）加入——git log -S 实证；本地分支 = 远端分支 = PR #15 head = c2f7a74，无漂移（预检"尚未接线"结论系误读主 checkout 工作区，非分支字节）。
   - 实测（一次性 PG sixpack-nightly-pg @127.0.0.1:55470，forum_app 角色在、22 表已迁移；临时 worktree @c2f7a74，用后已清理）：三入口 `npm run` 全部 **exit=0 且打出最终 PASS 标记**（SUBSCRIPTION_VERIFIER_CLEANUP_FAULT_TESTS / …_PARALLEL_ISOLATION_TESTS / …_COORDINATOR_FAILURE_RECOVERY_TESTS 均 =PASS）；DATABASE_URL 回退探针 exit=0（25 个 PASS 标记）；无前置探针 exit=2 带明确报错。BEHAVIOR_SPEC §2 四条义务全部满足 → **done_when 已被 base 本身满足，修复候选 = 空集**。
   - 处置 = 按 Owner 既有规则只停该任务：不 admit、不跑工位、不消耗模型调用、不自行改选替代任务。
4. **窗口 — 授权已记录，本轮未行使**。有界定时启动授权**未行使**：唯一已授权任务判废后，无合法可跑任务，定时启动 = 制造空转工作（违反 Owner"不制造工作"）。今晚模型调用消耗 = **0**。计费时区 = Asia/Shanghai（+08:00）；窗口 23:00–09:00；启动记录模板已内置时区/起止日期/任务/版本/pins 字段（nightly-1/bin/start-nightly-run.sh 第 4/5 步自动写 START_RECORD_*）。旧 30 分钟 cron 保持 paused；未新建任何循环定时。
   - 启动脚本已按 Owner 新规改造：任务 id 显式传入 + ledger 授权守卫；Base 三方一致（pin==本地==远端）否则 exit 6 拒绝（影响检查后需 Owner 可见决定才能重钉）；runtime 产品字节 != 受审 4199be02 则 exit 7 拒绝；**--ack-window 参数旁路已删除**，窗口非 ACTIVE 一律 exit 5。

## 剩余待决（唯一一项，一次列明）

af-verifier-impl-1 判废后，registry 首批 2 仓内不存在其他已授权写任务。盘点中其余真实缺口全部依赖未完成授权链：TASK-DAC-001（dsh-agent-core：修正案 lifecycle acceptance 未完成）、TASK-SVW-001（svc-workflow：Execution Mandate 未核实）、TASK-AUT-001（auth-service：CONTROLLED 凭据需 mandate+runbook）、TASK-AUT-002（auth-service：Owner 权链未核实）；OWN-DAC-001/OWN-ADC-001/OWN-AF-001 属 Owner 处置项。**请 Owner 三选一**：
- (a) 确认判废，本轮按「无可执行授权任务」收口（Six-Pack 机制此前已双任务全链验证；待真实问题出现再授权开窗）；
- (b) 从上述 NEEDS_PREFLIGHT 指定一项并授权预检 + 对应仓库入 registry（扩 registry = Owner 决定，REGISTRY_EXPANSION=FORBIDDEN 维持至该项明示）；
- (c) 直接指定新的首批问题（须满足五条选择标准）。

## 第二轮授权执行记录（2026-09-05T22:05+ Owner「有界多仓维护选单」授权 → 23:15 执行至定时待启）

### 0. 旧单结项
af-verifier-impl-1 记为「现有 Base 已满足，无需修改」（base c2f7a74 三 npm 入口实测全 PASS；证据见上节第 3 条）。不继续六工位、无空 diff、不计为新修复成果。

### 1. Host 留痕纠正（第七条）
- 顺序如实记录：**先合并**（PR #14 merge commit 68e4e743，2026-09-05T22:11:26+08:00，第二父 = 受审 head 8186595a，fresh clone 实证）→ **后生命周期接受**（9dcd0c4，仅 2 行 status 字段）。
- 有界独立复查（fresh clone，非旧审查冒充）：merge 结果中 spec 文件字节 sha256 = 1bd455b0…（与受审 r4 字节一致）；接受提交相对 merge 的全树 delta 恰为该文件 2 行；该文件在合并前从未存在于 main 线（8186595a→9dcd0c4 树级 diff 中的其余文件全部来自合并时 main 已领先的 v1.0.3 内容，与本 PR 无关——首次复查曾如实记录此疑点，二次复查定位为谱系并合噪声，非接受提交引入）。
- 不改写历史，未重开任何已通过的规范设计。

### 2. 四仓只读核验与选单（沿用既有清单 + 当前精确版本重确认）
只读登记 nightly-1 registry：dsh-agent-core / svc-workflow / auth-service / agent-forum（write_enabled=false；后因选定任务按第六条对 dsh-agent-core 启用受限本地写）。逐项核验结果：
- **agent-forum**：automation 分支 3 次失败 CI = GitHub App 缺 workflows 权限被拒（权限类，属本轮禁止项）→ 最小待决 §4-1；OWN-AF-001 已自行消解（moderation 分支已并入 main，2026-09-03 验收审计 375/375 PASS）。无在案可修缺陷。
- **auth-service**：PR #40 已 MERGED（validation 分支失败 CI 属历史陈旧）；JWKS signer 审计 = 0 blocker 0 high 收口。无可修候选。
- **svc-workflow**：PR #19 仍 OPEN，Execution Mandate 未核实（授权缺口）→ 最小待决 §4-2；无失败 CI。
- **dsh-agent-core**（main @ 797952e，无 CI 看护）：audit/pr140 NameError = 分支自动化废弃脚本（`false` 字面量进 Python），恢复该证据流缺本仓依据 → 最小待决 §4-3。**实测全量套件**（node v25.6.1 精确运行时 + 依赖装齐 + 代理变量隔离）：1498 测试 / 1487 过 / 6 失败 / 5 跳过。失败逐项定因：
  - TRUSTED_INGRESS 1 例 = **真实套件回归（选定修复，见 3）**；
  - dsh-llm 未声明 import 3 文件（demo-server×2 + production-runtime 集成×1）= 仓库 74d02d0 验证记录已在案的已知环境缺口（"8x missing dsh-tools/dsh-llm harness packages"），依赖供给策略属产品决策 → 最小待决 §4-4；
  - agent-switch `parameters.required` undefined 1 例 = 8/22 在案清单之后的新失败，疑 dsh-tools peer 未钉版本漂移，需先核 dsh-tools 合同再定代码/测试哪边错 → 最小待决 §4-5；
  - agent-provisioning harness identity 1 例 = 在案已知环境条件性（74d02d0 同清单）；
  - production-runtime compose 大簇（node 版本/代理 fail-closed）与 workspace-bootstrap worktree 断言 = 规范要求的环境条件性行为，非缺陷。

### 3. 选定任务（一仓一任务，已冻结、预跑被配额中断、01:55 断点续跑）
- **TASK = dsh-trusted-ingress-align-1（dsh-agent-core @ 797952e7bc33a134e8c29d3a66dd76b1210ba721，freeze 时 remote==pin==base）**
- 依据链：问题来源 = main 套件实测失败（TRUSTED_INGRESS deepStrictEqual：实际多出 feishuSenderOpenId）；反例 = `node --test packages/agent-router/test/feishu-regression.test.js` 在 base 上 exit 1；本仓依据 = 字段由已接受实现 bd0eeae（AGT_CTO_AGENT_ORDERED_ROUTE_CHAIN_IMPL_V2，PR #103 合并）有意加入（ingress-delivery.js:110），route-chain.js:353 消费，新测试 canary-seam.test.js:62 按含该字段+Object.freeze 断言；旧测试 3dae32e（早于 bd0eeae）从未同步且无 CI 发现；修改范围 = 仅 packages/agent-router/test/feishu-regression.test.js（预期面补第 6 字段，保留 frozen 与 no-parse 断言），禁止动 src/docs/.github/package.json；验收 = 该测试文件 exit 0 + agent-router 无新增失败 + src diff 空 + 六 receipts + verify PASS。
- 授权链：Owner 第二轮授权第四/六条（有界修复 + 单仓受限本地写）；mandate_ref = OWNER-MANDATE-2026-09-05-BOUNDED-MULTIREPO-MAINTENANCE（已绑定 ledger，PROFILE_GATE 实测通过）。
- 执行状态：23:07 首次启动 → PROFILE_GATE 修正（mandate_ref）→ 23:07 specifier 真实启动（worktree @797952e 创建）→ GLM 端点 500（实为 **1308 5 小时用量上限**，限额 2026-09-06 01:51:21 重置）→ 按非盲试规则安全停机：worktree 已 prune、host recover 已复位 specifier=pending、workflow 断点保留。**本轮实际消耗模型调用 ≈ 1 次失败请求。**
- 一次性定时（非循环）：**01:55 automation-ad8fa74d** 断点续跑（脚本守卫齐全：任务授权/pin==base/远端未前移/窗口 ACTIVE；含 1302 退避与 1308 再停机规则），运行完成后立即晨报+落账；runtime 内置 09:00 窗口闸兜底。node_modules 符号链接农场已预置于 sixpack-worktrees/node_modules（QA 依赖解析用，node v25.6.1 二进制在 /tmp）。
- 启动记录：nightly-1/state/START_RECORD_20260905_230545.md（计费时区 Asia/Shanghai +08:00、窗口、task、runtime 版本、task_base）。

### 4. 最小待决集合（不阻塞其他合法工作，逐项列明）1. agent-forum automation CI：GitHub App 需要 `workflows` 权限才能改 workflow 文件——授予权限或改用 PAT/人工执行，属 Owner 安全决策。
2. svc-workflow PR #19：需 Owner 核实 Execution Mandate 与 Product Boundary V5 authority 引用后才能预检。
3. dsh-agent-core PR #140 证据流：audit 分支 workflow 内联 Python 含 `false` 字面量 NameError；恢复该自动化需要 Owner 决定是否重建证据流（本仓无既有规则要求恢复它）。
4. dsh-agent-core dsh-llm/dsh-session 供给策略：demo-server 未声明 import 的 harness SDK 从哪来（root devDeps / 各包 peers / 内部源）——产品依赖决策，未获授权前不动。
5. dsh-agent-core agent-switch `parameters.required` undefined：疑似 dsh-tools peer ">=0" 漂移；需先核 dsh-tools 合同再定修复方向，本轮未动。
6. 本轮若 TRUSTED_INGRESS 候选完成：独立审查 + 处置（accept/revise）归 Owner；REMOTE_WRITE=false，候选保留本地。
AUTO_ACCEPT = false / AUTO_MERGE = false / AUTO_DEPLOY = false / REMOTE_WRITE = false
REGISTRY_EXPANSION = FORBIDDEN（仍限首批 2 仓）

### 承接成果核验（2026-09-05 下午 fresh-fetch）
- Host r4：governance PR #14 Review 5119235263 = **ACCEPT，0 blockers**（REVIEWED_SPEC_COMMIT=8186595a，TREE=ff4e78a0；PR head 至今未变，仍 OPEN/unmerged）。
- Runtime B-QA-01：runtime PR #2 Review 5119786442 = **ACCEPT，0 blockers**（REVIEW_TARGET_HEAD=4199be02，TREE=f892d1fc；PR 仍 Draft/Open）。评审明示：下一授权 canary 的准备不再被 QA gate 阻塞；勿为 merged 徽章合并快照分支；Owner 处置须指明实际运行 revision。
- 评审通过 ≠ 已接受：Owner acceptance 仍待行（见 OWNER_ACTION_REQUIRED）。

### 本机运行版本固定（步骤二完成）
- 运行版本 = mayf3/agent-six-pack-runtime v0/bootstrap @ 76aaca6。
- 76aaca6 与受审 head 4199be02 的 src/ tests/ pyproject.toml diff = 空（受审字节 = 运行字节；76aaca6 仅更新 forge 账目）。
- 本机实跑全量质量门：**107 tests passed + ruff clean + mypy strict clean**。
- 停止/恢复/并发证据：负例矩阵在 107 套件内（two write tasks/repo、two in-process/role、lease recovery、head drift、duplicate delivery 等）+ 先导 run 3 次真实 kill→host recover→断点续跑；窗口相位语义（QUIESCE/WINDOW_CLOSED）已随 Host r4 ACCEPT（ACC-MRH-003）。未重复全审，未改任何受审字节。

### 模型接通（步骤三完成）
- 账户 = BigModel Coding Plan（zcode entryStatus=**available**；key 仅存 ~/.zcode，指纹 sha256:65fa121e7d75）。
- 入口 = https://open.bigmodel.cn/api/anthropic（Anthropic 兼容）；时区 = Asia/Shanghai（+08:00）。
- 最小连通验证 = 真实 HTTP 调用 glm-5.3-flash 回复 "OK"（17+3 tokens，非 Codex 代跑）。
- 执行器选定（实测排除法）：claude -p 挂起复现（45s 无输出）→ 不可用；codex 0.144.4 已移除 wire_api="chat" 且 bigmodel coding 端点无 /responses（404）→ 不可用；**opencode 1.18.23 + 项目级 provider 配置（glm-provider.json）→ 全链路验证通过**（模型→Write 工具→正确目录落盘 "OK"）。
- 已知限制：GLM 账户限流 [1302] 会在连续请求中触发 → bin/glm-role-exec.sh 内置 60s×≤20 次有界退避 + opencode --continue 续会话（非 BLIND_RETRY：仅对 1302 且保留会话语境）。
- opencode 按 PWD 环境变量解析项目根 → wrapper 内 `export PWD=$(/bin/pwd -P)` 修正（ProcessAdapter 以 worktree 为 cwd 派发，runner.py:408）。

### 任务预检与预置（步骤四前置完成，未启动）
- NIGHTLY_WORKSPACE = /Users/yanfenma/workspace/project/sixpack-forge/nightly-1（旧 canary-1 原样保留为历史证据）。
- Registry（2 仓 write_enabled）：agent-six-pack-runtime @ v0/bootstrap/76aaca6；agent-forum @ agent/forum-subscription-advanced-tooling-v1/c2f7a74（PR #15 head，capability 分支）。
- TASK_PROPOSED = **af-verifier-impl-1**（TASK-AF-001 的实现收尾；base_head=c2f7a74；authority=fcd417ba；profile=SIX_PACK_V1；provider=bin/glm-role-exec.sh {prompt}）。真实缺口（盘点+spec 双确认）：BEHAVIOR_SPEC §2 要求 svc-forum/package.json 暴露 3 个 test:subscription-* npm 入口，PR #15 分支尚未接线；脚本本体只用 Node 内置模块。
- 测试环境实跑证明：一次性 PG（docker sixpack-nightly-pg，127.0.0.1:55470，已迁移，需预建 forum_app 角色）上 PR #15 三套件 **全部 PASS（exit=0）**；node v26.7.0。
- 状态：任务已创建（preflight completed），**未 admit、未跑任何工位、未消耗任何模型调用**。

### OWNER_ACTION_REQUIRED → 已全部处置（2026-09-05T21:45 Owner 决定，执行记录见上节）
1. Host r4 acceptance — ✅ 已合并（68e4e743）+ 生命周期接受（9dcd0c4）。
2. PR #2 处置 — ✅ 按 Owner 决定保持 Draft/Open @ 4199be02；运行版本固定为含同字节的 v0/bootstrap。
3. 任务授权 — ⚠️ af-verifier-impl-1 获授权但开工前核验判废（缺口在 base 不存在，证据见上节）；替代任务待 Owner 三选一（见「剩余待决」）。
4. 夜间窗口 — ✅ 已授权（23:00–09:00 Asia/Shanghai，仅本轮）；本轮未行使（无合法任务可跑），模型调用消耗 0。

### ENTRYPOINTS（沿用现有 CLI，无新 UI/调度平台）
- **一键启动**（窗口内）：`bash /Users/yanfenma/workspace/project/sixpack-forge/nightly-1/bin/start-nightly-run.sh`（内部完成：刷新 registry pinned heads → window_phase 检查（非 ACTIVE 拒绝，`--ack-window` 需 Owner 已确认的窗口）→ 后台 sixpack run 六角色 + 日志 drive-all.log）。
- **晨报**：`bash /Users/yanfenma/workspace/project/sixpack-forge/nightly-1/bin/morning-report.sh`（verify + ledger → MORNING_REPORT_<date>.md：处理了什么/交付物在哪/哪些测试实际通过/哪些没做/是否可采用/需要 Owner 决定什么）。
- 手动刷新 pinned heads（分支有任何新提交后必须）：`sixpack host <ws> register --name agent-six-pack-runtime --path ... --base-branch v0/bootstrap --writable` ×（agent-forum 同理）。
- 进度：`sixpack status <ws>` / `sixpack host <ws> status`（每个 workflow 的 state/stage_pointer/receipts）。
- 停止：`pkill -f glm-role-exec`（+ 在飞 opencode）→ `sixpack host <ws> quiesce`。
- 恢复：目标仓清理脏 worktree 后 `sixpack host <ws> recover` → 重跑启动脚本（自带 auto-recover；禁止盲目重试）。
- 窗口参数：`nightly-1/host.json` 写 `{"window_open":"23:00","window_close":"09:00"}`（或 window_override 强制相位，仅测试用）。

### 完成标准对照（本 Goal）
| 要求 | 状态 |
|---|---|
| 已授权真实任务交出修复候选（问题依据/改动/精确版本/实测/限制/独立审查状态；本地候选，具备既有写授权才 Draft PR） | 本轮判废：唯一授权任务的缺口在 base 不存在（实测三入口全 PASS，候选=空集）；修复候选交付等 Owner 三选一后再开窗 |
| 实际运行版本/模型/窗口有可查记录 | 版本+模型已留账（本文件）；窗口待 Owner 确认后记录 |
| 窗口结束停止新工作、状态可保存恢复 | quiesce/recover 语义 + 实操序列已就绪 |
| 启动/停止方式 + 看得懂的成果报告 | 启动/停止已在 ENTRYPOINTS；晨报待运行后按本节模板产出（处理了什么/交付物在哪/哪些测试实际通过/哪些没做/是否可采用/需要 Owner 决定什么） |

## PRIOR GOAL — Bootstrap Multi-Repo Six-Pack Governance Forge（已并入上方 ACTIVE GOAL）

GOAL_STATUS = SECOND_BLOCKER_UNION_REVIEWS_VERIFIED（双 ACCEPT 已核验；剩余 Owner acceptance 项归入 ACTIVE GOAL 的 OWNER_ACTION_REQUIRED 1/2）
PHASE_LOCK = ON
INDEPENDENT_PILOT_REVIEW = REVISE
SECOND_INDEPENDENT_REVIEW = Host r4 ACCEPT（5119235263）；Runtime replacement Head ACCEPT（5119786442，B-QA-01 CLOSED）
READY_FOR_GOVERNANCE_FORGE_PILOT_REVIEW = YES（历史里程碑，见 DONE_WHEN 审计）
REGISTRY_EXPANSION = FORBIDDEN

## Governing authority（已 fresh-verify）

- GOVERNANCE_REPOSITORY = mayf3/agent-development-governance
- GOVERNANCE_SOURCE_COMMIT = fcd417ba608bafcc8a1160f3e95f8c43cb2212d8（GitHub 已验证，PR #12 merge）
- 实现边界 = AGENT_SIX_PACK_DELIVERY_PROFILE_V1 的 CTR-SIX-001..022

## Lane 状态

### LANE A — SIX_PACK_RUNTIME
LANE_STATUS = CORE_COMPLETE
RUNTIME_REPOSITORY = mayf3/agent-six-pack-runtime（GitHub private，分支 v0/bootstrap，已推送）
RUNTIME_HEAD = c498e59d057756b3995b52c84e060c5b6860b1be（以 git log 为准）
已实现（全部有测试覆盖，78 tests green + mypy strict clean + ruff clean）：
- 语义 handoff envelope + 两调用 AUDIT_REQUIRED 挑战门（CTR-SIX-011/013）
- 持久化 8 目录队列生命周期 + helper 独占迁移 + 完整性校验 + 重复投递抑制 + 崩溃恢复（CTR-SIX-012）
- 六阶段状态机 + 不可变 receipt 哈希链 + correction/replay（CTR-SIX-019）
- terminal 广播 priority 00 → 恰好其余五角色；converge 为 merge-only fast-forward（CTR-SIX-015）
- 每 role 隔离 worktree + exact head/tree 校验 + HeadDrift 拒绝 + main checkout 保护（CTR-SIX-003 / CTR-GOV1-006）
- 确定性多仓 Controller：registry/lease/admission/夜间窗口/quiesce/recover/功率闭合（DEC-MRH-001..007）
- terminal impact-and-coverage verifier；永不声称 merge-ready（CTR-SIX-020）
- CLI：init/task/run/resume/status/verify/done/converge/drive-all/host
- 负例矩阵全部通过：recipient/priority/handoff-type swap、normal→terminal spoof、partial terminal、terminal priority≠00、terminal re-forward、stale receipt、QA self-certification、manual helper bypass、duplicate delivery、two write tasks/repo、two in-process/role、lease recovery、head drift、unauthorized coder entry

### LANE B — MULTI_REPO_HOST_AUTHORITY
LANE_STATUS = REVIEW_R1_RECEIVED_REVISE（5 blockers，修复为 amendment r2 后再送审）
REVIEW_REPORT = forge/specs/AGENT_MULTI_REPO_SIX_PACK_HOST_V1_REVIEW_R1.md（fresh codex 会话独立评审，逐条 A-F + blocker 最小修复建议）
AUTHORITY_ACTION = NEW
HOST_SPEC = forge/specs/AGENT_MULTI_REPO_SIX_PACK_HOST_V1.md（status: proposed）
Gap 结论：现有 authority 未覆盖 multi-repo host 长期语义（registry/lease/并发上限/夜间窗口/controller 权限闭合）。Profile open questions 明确把 runtime 层留白；Governance V1 明确拒绝 cross-repository controller。
剩余 lifecycle：独立评审 + Owner acceptance（OWNER_ACTION_REQUIRED）。acceptance 前不得视为 accepted。

### LANE C — MULTI_REPO_HISTORY_INVENTORY
LANE_STATUS = COMPLETE（一轮）
REPORT = forge/inventory/INVENTORY_LEDGER.md（已提交）
REGISTERED_REPOSITORIES = 9（registry 建议）
READY_FOR_SIX_PACK_TASKS = 2（TASK-ASR-001 本仓 version 命令；TASK-AF-001 agent-forum verifier 硬化）
NEEDS_PREFLIGHT_TASKS = 4（dsh-agent-core #137、svc-workflow #19、auth-service #39/#36）
NEEDS_OWNER_TASKS = 3（dsh-agent-core breakglass、agent-dev-center secrets、agent-forum 分支合并）

### LANE_FIRST_PILOT
LANE_STATUS = RUNNING（真实模型 canary 进行中）
FORGE_WORKSPACE = /Users/yanfenma/workspace/project/sixpack-forge/canary-1（durable ledger 在此，不入产品源）
- 仓 A = agent-six-pack-runtime（writable）：真实任务 canary-version-1 = `sixpack version` 命令（TASK-ASR-001）
- 仓 B = agent-forum（writable）：真实任务 af-verifier-1 = subscription verifier 硬化 spec（TASK-AF-001）
- 适配器 = ProcessAdapter("codex exec --sandbox workspace-write {prompt}")，真实模型跑全部六工位；helper 拥有 commit（agent 不碰 git）
- 已验证进展（真实 codex）：两任务均完成 specifier+coder（receipts=2 各），交错并行已被真实运行证明（af 与 canary 在不同工位先后推进）。
- 修复的第二个真实缺陷：recover() 原先只遍历惰性实例化的队列 dict，独立恢复进程会空转 → 已改为固定六工位扫描 + 回归测试（fresh-process recovery）。修复后 recover 实操通过：stale in_process 条目清除、canary cleaner 项就绪。
- canary-version-1 已推进到 QA 工位（5 receipts：spec/coder/cleaner/architect/hardender 全真实 codex）。
- 第三个真实缺陷修复：下游工位判断"无需改动"时空候选被 helper 拒绝 → 简报强制每工位留下 stage report 工件（sixpack-artifacts/<role>.report.md），既是交接物也是更完整的 stage evidence。
- 第四次修复（关键架构修正）：tick 派发改为 ledger 驱动（CTR-SIX-012 "wake-up 是有损 hint"），候选 = stage_pointer+pending，与队列内容解耦 → 中链 crash（投递项已消费）也能再调度。此前只有 specifier 有入口 fallback，af 卡死在 cleaner。drive-all 前置 auto-recover。
- 里程碑：**af-verifier-1（agent-forum 仓）六工位全部真实 codex 完成 → terminal broadcast → 五角色 refs 收敛 → verify PASS → AWAITING_INDEPENDENT_REVIEW**（forge workspace ledger + 各仓 worktree refs 为证据；未 push 任何目标仓库）。
- 修复第五个真实缺陷：_manager_for 不尊重 workspace worktree_root（registry 注册时用默认根建 manager 缓存）→ 已修 + 清理全部遗留默认根 worktree。
- canary-version-1 @ qa 重跑中（后台 exec_5d9a2704）。
- QA 自认证守卫真实触发（误报→修正）：QA 写 stage report 被当产品字节拒了——守卫机制本身工作正常；ProcessAdapter 现声明 sixpack-artifacts/ 为 QA 工件目录，守卫支持目录前缀。QA 重跑中（后台 exec_0818d97f）。
- 约束生效：MAX_IN_PROCESS_PER_ROLE=1、MAX_ACTIVE_WRITE_TASKS_PER_REPO=1、AUTO_*=false、REMOTE_WRITE=false（codex sandbox 无网络）、worktree 隔离
- drive-all 后台运行中（log: $FORGE/drive-all.log），完成或失败都会有通知；卡住时读 log 定位，按 BLOCKER UNION 一次修复

## HOST_POLICY（固定）

MAX_IN_PROCESS_PER_ROLE = 1
MAX_ACTIVE_WRITE_TASKS_PER_REPO = 1
AUTO_ACCEPT = false
AUTO_MERGE = false
AUTO_DEPLOY = false
REMOTE_WRITE_DEFAULT = false
MAIN_CHECKOUT_WRITE = forbidden
SELF_SELECT_NEW_WORK = forbidden
BLIND_RETRY = forbidden

## 定时推进

automation-4cf1970a-bc60-4f89-8b24-f2435e7a4f96 每 30 分钟触发。若 canary 仍在跑，检查 $FORGE/drive-all.log；若卡住（stage failure），读日志定位、修复后用 resume/tick 恢复（不盲目重试——BLIND_RETRY forbidden，先找共同根因）。

## REVIEW SURFACES（AWAITING_INDEPENDENT_PILOT_REVIEWS）

HOST_SPEC_REVIEW_STATUS = NEEDS_EXACT_R2_REVIEW（R1=REVISE→r2，无 r2 独立复审；r2 bytes 冻结 SHA256 a5faf452…；packet=forge/specs/REVIEW_PACKET_HOST_V1_R2.md；freeze commit 613ba6f3）
RUNTIME_REVIEW_PR = mayf3/agent-six-pack-runtime#1（Draft，base v0/bootstrap，head 8957f2feec4eaff0bab278db3b907c02203c28f8，tree d22e791e44856b79f5a244eae361aec57d0f5873，base-head dc684d0851b9）
AGENT_FORUM_REVIEW_PR = mayf3/agent-forum#18（Draft，base main（fb11552 已含于 main），head 77bc1467dedea95bcaa7db250303232263ce6e5e，tree 74a10b68b13074d1e601f67e6f372950605a96eb）
CANDIDATE_BYTES_CHANGED = NO；REGISTRY_EXPANDED = NO；AUTO_MERGE = false；AUTO_DEPLOY = false

## PILOT_BLOCKER_UNION_REMEDIATION 结果（2026-09-05）

HOST_SPEC_PR = mayf3/agent-development-governance#14（proposed docs PR，branch governance/agent-multi-repo-six-pack-host-v1）
HOST_SPEC_R3_HEAD = governance 仓该 PR 的 exact head（见 PR 页面 / git ls-remote）
HOST_SPEC_R3_TREE = 见 PR；r3 bytes SHA256 = 443008559fed1bc8c0fd03fc52a0fbebb8587310dfb8121062372f1d103ffb65
  仅修 CTR-MRH-003（recovery 四要件 + outcome_unknown 保留）、CTR-MRH-004（QUIESCE/WINDOW_CLOSED 矛盾消除，V1 相位简化）、CTR-MRH-005（route 限制从 DEC 提升进 Contract）；其余 r2 语义未动
HOST_SPEC_STATUS = READY_FOR_EXACT_R3_REVIEW

RUNTIME_FIX_HEAD = 0c61bfa（v0/bootstrap，BLOCKER-UNION Lane B commit；fix 直接落在 v0/bootstrap 分支上，评审绑定该 exact head）
RUNTIME_FIX_TREE = 见 `git rev-parse 0c61bfa^{tree}`
  修复：QA 两阶段协议（artifacts 先提交 → final QA 在该 candidate 上执行 → final 后字节不可变）+ _validate_qa_machine（fake PASS 机械降级 BLOCKED）+ verifier PASS 强制绑定 QA_VERDICT / QA_REQUIRED_CHECKS / QA_BLOCKERS / QA_TERMINAL_CANDIDATE_UNCHANGED / QA_RECEIPT_BINDS_TERMINAL_TREE
FALSE_PASS_REGRESSION_TESTS = 7 个新负向测试（tests/test_qa_final_gate.py）：QA FAIL / QA BLOCKED / required check NOT_EXECUTED / final 后字节变动 / fake PASS with failing checks / terminal tree ≠ certified tree / ProcessAdapter QA_FINAL_JSON 解析；全量 86 tests + ruff + mypy strict 全绿

OLD_CANARY_HISTORY_CHANGED = NO（仅追加 PILOT_EVIDENCE §8 定位更正：两旧 run 为 pilot evidence，非正式 CTR-SIX-021 canary，不可追溯宣称 QA PASS / SPEC_GAP closure）
REGISTRY_EXPANDED = NO
AUTO_ACCEPT = false
AUTO_MERGE = false
AUTO_DEPLOY = false

## SECOND_BLOCKER_UNION_REMEDIATION 结果（2026-09-05）

HOST_SPEC_PR = mayf3/agent-development-governance#14（同 PR，r4 已推送）
HOST_SPEC_R4_HEAD = 8186595a9abb93bfdb75c21c6d0be9e93abdc863
HOST_SPEC_R4_TREE = ff4e78a0b77b5d118a02844b5cf8fb1df793a935
  （r4 bytes SHA256 = 1bd455b0c726951430653c6cd6169234df6981b8af2001524add4e7add3bf24a）
  H1：DEC-MRH-003 与 CTR-MRH-003 对齐（删除 clean-worktree requeueable 旧语义，四要件 + outcome_unknown 保留）
  H2：ACC-MRH-002 补齐 recovery 负例全集 + deterministic positive case
  H3：ACC-MRH-003 补齐完整 QUIESCE / WINDOW_CLOSED phase 行为
  其余 r3 已通过语义未动；status 保持 proposed
HOST_SPEC_STATUS = READY_FOR_EXACT_R4_REVIEW

RUNTIME_FIX_PR = mayf3/agent-six-pack-runtime#2（head branch 已更新为最新 replacement head）
RUNTIME_REPLACEMENT_HEAD = 4199be02c2da99e8b2f85236a5eddb370ba3dadf
RUNTIME_REPLACEMENT_TREE = f892d1fc50de3c1215da8b2d79e2abcceb974710
  （取代 6497b065…/61121538…。累计：qa_gate.py 共享规则模块——完整 PASS 资格判定
   由 Runner 与独立 TerminalVerifier 共用；可执行自动化绑定认证 Git tree；
   B-QA-01 修复：QA 原始有效 blockers 与校验错误合并不清空、回显坐标保留原样
   不被覆写（mismatch 持续拒绝 PASS）、双路径同表测试（A 原始回执直验 / B 先规范化）
   覆盖每 canonical 检查 FAIL/NOT_EXECUTED、非空 blockers、错误认证 head/tree、
   全合法正例。全量 107 passed）
REQUIRED_CHECK_SET_GATE = PASS（闭合集：从 pinned QA role definition 导出三 canonical checks；missing/duplicate/substitute 一律降级 BLOCKED）
QA_BLOCKERS_SCHEMA_GATE = PASS（list[str] 严格 schema；missing/null/non-list/non-str → BLOCKED，不静默忽略）
EXECUTABLE_QA_AUTOMATION_GATE = PASS（qa.automation.json manifest + entrypoint 存在/非空/shebang-or-exec-bit；report-only 在 commit 前被拒；证据绑定 QA receipt）
TESTS = 95 passed（含 9 个新负例）+ ruff clean + mypy strict clean，exact-Head 执行证据 = forge/QA_GATE_FIX_EVIDENCE.md（本仓无 CI workflow，未为此新增 CI 平台）

OLD_CANARIES_CHANGED = NO（canary-version-1 / af-verifier-1 历史与 §8 定位更正不变；未重跑正式 canary）
REGISTRY_EXPANDED = NO
AUTO_ACCEPT = false
AUTO_MERGE = false
AUTO_DEPLOY = false

## NEXT

DONE：Host r4 复审（5119235263 ACCEPT）与 Runtime replacement Head 复审（5119786442 ACCEPT，B-QA-01 CLOSED）均已核验，绑定 head/tree 与 PR 页面一致。
剩余动作已并入 ACTIVE GOAL 的 OWNER_ACTION_REQUIRED（Host r4 acceptance、PR #2 处置、任务授权、窗口确认）。
STOP —— 窗口确认前不启动夜间模型工作；不扩 registry、不新增功能、无 accept/merge/deploy。

## 实操验证证据（quiesce/recovery，已发生三次真实恢复）

1. kill drive-all（af cleaner codex 在飞）→ host recover：in_process 队列条目按 executed_handoffs 正确完成、stage_status 复位 pending、integrity OK、registry head drift 检出（dc684d0→bbdcc13）
2. 第二次 kill 后发现 recover 空转缺陷（惰性实例化）→ 修复为固定六工位扫描 + 回归测试
3. 中链卡死发现 ledger 驱动派发缺口 → 修复（CTR-SIX-012 wake-up 是有损 hint）
每次恢复后 canary 均从断点继续且 receipts 无重复执行（幂等性由 executed_handoffs 保证）



## DONE_WHEN 审计（15 条逐条对照，证据坐标见 forge/PILOT_EVIDENCE.md）

| # | 要求 | 判定 | 证据 |
|---|------|------|------|
| 1 | agent-six-pack-runtime 独立仓库存在 | YES | github.com/mayf3/agent-six-pack-runtime（private），v0/bootstrap 已推送 |
| 2 | 六阶段 runtime core 可运行 | YES | 79 tests 全绿；真实 canary 12 工位全部执行 |
| 3 | durable queue/handoff/audit challenge/receipt/replay/terminal verifier | YES | src/sixpack/{queue,audit,ledger,verifier}.py + 真实触发记录 |
| 4 | multi-repo host 语义：现有 authority 覆盖 或 child Spec 完成必要 lifecycle | PARTIAL→REVIEW-READY | AUTHORITY_ACTION=NEW 成立；child Spec 已 authoring + 独立评审 R1（REVISE 5 blockers）+ amendment r2 全部落实。剩余唯一动作 = Owner acceptance（AUTO 规则禁止代行）→ OWNER_ACTION_REQUIRED |
| 5 | multi-repo repository registry | YES | forge/inventory/INVENTORY_LEDGER.md（9 仓建议）+ live registry（2 仓 write_enabled） |
| 6 | 至少一轮跨仓 READ_ONLY history inventory | YES | INVENTORY_LEDGER.md，全部只读，来源坐标齐全 |
| 7 | 至少一批 READY_FOR_SIX_PACK 真实历史任务 | YES | TASK-ASR-001 + TASK-AF-001（两个都被真实执行了） |
| 8 | 首批 1~2 仓已被接入 | YES | 仓 A + 仓 B，registry write_enabled，terminal 收敛完成 |
| 9 | 6 个长期 role 从共享池领取正确工位任务 | YES | ledger 驱动派发 + 12 receipts 全部按固定顺序落在正确工位 |
| 10 | 一个真实任务完整经过六工位 | YES | af-verifier-1 与 canary-version-1 双双完成（真实 codex） |
| 11 | 第二仓任务在不同工位并行推进 | YES | PILOT_EVIDENCE §2 时间线：af/coder(15:54) 先于 canary/specifier(15:59)；canary cleaner/architect/hardender(16:10-16:18) 先于 af(16:32-16:39) |
| 12 | crash/restart、duplicate、Head drift、unauthorized admission 负例通过 | YES | 测试矩阵 + 3 次真实恢复 + 4 类守卫实弹触发（§4） |
| 13 | AUTO_ACCEPT/AUTO_MERGE/AUTO_DEPLOY 保持 false | YES | HostConfig.validate 强制（true 即抛 HostPolicyViolation）；全程无 merge、无对目标仓库 push |
| 14 | 夜窗结束可 restart-safe quiesce、下晚恢复 | YES | quiesce 语义（阶段矩阵 CTR-MRH-004）+ quiesce/recover 留证 + 3 次真实 kill→recover→续跑（§5）；完整跨夜循环由下晚 cron 自然验证 |
| 15 | exact candidate Head 和独立审计入口 | YES | terminal heads 77bc1467de / 8957f2feec；verify 报告 PASS；AWAITING_INDEPENDENT_REVIEW 入口（独立评审 + Owner 处置待行） |

结论：15 条中 14 条完全达成；第 4 条完成至 acceptance 前的最后一步（Owner acceptance 是 AUTO 规则下不可代行的动作）。达到 GOAL 设计的终态名：READY_FOR_GOVERNANCE_FORGE_PILOT_REVIEW。

## FINAL REPORT

GOAL_STATUS = READY_FOR_GOVERNANCE_FORGE_PILOT_REVIEW
LANE_RUNTIME = CORE_COMPLETE（79 tests/mypy strict/ruff 全绿；12 真实工位执行）
LANE_HOST_AUTHORITY = REVIEW_R1_ADDRESSED（amendment r2 落实全部 5 blockers + 7 concerns；待 Owner acceptance）
LANE_HISTORY_INVENTORY = COMPLETE_R1（9 仓 registry、2 READY / 4 NEEDS_PREFLIGHT / 3 NEEDS_OWNER / 15+ GOVERNANCE_LANE）
LANE_FIRST_PILOT = COMPLETE（2 仓 2 任务 12 工位全真实 codex；双任务 verify PASS + 收敛）

RUNTIME_REPOSITORY = mayf3/agent-six-pack-runtime
RUNTIME_HEAD = 见 git log v0/bootstrap（HEAD 3da4cff 之后含本次提交）
RUNTIME_TREE = 以 HEAD 为准

GOVERNANCE_SOURCE = mayf3/agent-development-governance
GOVERNANCE_REVISION = fcd417ba608bafcc8a1160f3e95f8c43cb2212d8（fresh-verify）

HOST_AUTHORITY_ACTION = NEW
HOST_SPEC = forge/specs/AGENT_MULTI_REPO_SIX_PACK_HOST_V1.md（r2，proposed，R1 评审已闭环）

REGISTERED_REPOSITORIES = 9（建议 registry；首批 2 仓已接入）
READY_FOR_SIX_PACK_TASKS = 2（均已执行）
NEEDS_PREFLIGHT_TASKS = 4
NEEDS_OWNER_TASKS = 3

ROLE_AGENTS = 6 工位 × 共享池（ledger 驱动派发；本夜由 codex 会话执行）
CONTROLLER = HostController（scan/route/lease/wake/reconcile/quiesce/recover；功率闭合 CTR-MRH-005）
DURABLE_LEDGER = sixpack-forge/canary-1/state/ledger.json + 队列树
FORUM_INTEGRATION = 未接（FOLLOW_UP_DEBT：Forum thread 映射为 attention 面，非权威存储）
SCHEDULER_INTEGRATION = cron 仅驱动控制面（automation-4cf1970a 每 30 分钟）；工位由 handoff 完成即唤醒

NEGATIVE_TESTS = 79 项测试含全负例矩阵 + 4 类实弹触发（见 PILOT_EVIDENCE §4）
REAL_SIX_PACK_CANARY = 2/2 完成（af-verifier-1、canary-version-1）
CROSS_REPO_PARALLELISM = 已证明（交错时间线 §2）
NIGHT_WINDOW_RECOVERY = 3 次真实恢复 + quiesce/recover 留证

AUTO_ACCEPT = false
AUTO_MERGE = false
AUTO_DEPLOY = false

BLOCKERS = 无（全部中途 blocker 已按 BLOCKER UNION 闭环：recover 空转、ledger 驱动派发、worktree 根分裂、QA 路径声明、空候选交接）
FOLLOW_UP_DEBT = Forum thread 映射；完整跨夜 quiesce→reopen 循环观察；更多仓 adoption
OWNER_ACTION_REQUIRED =
  1) LANE B child Spec acceptance（r2 已就绪）
  2) 两个 canary 交付物的独立评审 + 处置（runtime 仓：sixpack version 命令 @8957f2fe；agent-forum 仓：verifier 硬化 spec @77bc1467，均在 AWAITING_INDEPENDENT_REVIEW）
  3) 批准后仓库扩容（registry 余下 7 仓）与下晚继续
NEXT = STOP（不自动扩大到所有仓库）

## BLOCKERS

（无当前阻塞。风险：codex 沙箱内 git 不可用 → 已由 helper commit 兜底；stage 失败则按 BLOCKER UNION 处理）

## 夜间轮终局（2026-09-06 01:55–04:00，Owner 授权有界维护轮）

### 结果：首个跨仓修复候选交付
- **任务**：dsh-trusted-ingress-align-1（dsh-agent-core，冻结 base 797952e7bc33a134e8c29d3a66dd76b1210ba721）
- **terminal head** = dd100382a23509c67a35cf919e8cda07da1d43d0（六角色分支全部收敛于该 head）
- **receipts** = 7（specifier 68b2565a / coder 6788e22e / cleaner da30525e / architect fd48b025 / hardender 5f4b2e84 / qa 794e2609+qa-final d76bfad3，全真实 GLM glm-5.3-flash 经本地 forwarder）
- **verify** = PASS（failures=[]，done_when_met=true，五角色 converge 完成，state=AWAITING_INDEPENDENT_REVIEW）
- **修复内容**（测试专用，src/docs/package.json 零改动）：packages/agent-router/test/feishu-regression.test.js TRUSTED_INGRESS 用例对齐已接受实现表面——预期 ingressContext 补入第 6 字段 feishuSenderOpenId（bd0eeae/PR #103 有意加入），并加固测试：输入 text 嵌入诱饵自报 openId，断言 trusted context 只取认证 sender 元数据、冻结名不变；另保留 no-parse（conversationId ≠ chatId）断言。sixpack-artifacts/ 含全部工位报告 + qa_required_checks.sh + qa.automation.json（entrypoint=裸文件名）。
- **操作者独立实测**（terminal candidate 上）：① feishu-regression.test.js 9/9 PASS；② base→terminal 改动 = 仅该测试文件 + sixpack-artifacts/（src diff 空）；③ agent-router 全套 240 测试 239 过 0 失败 1 跳过（base 上唯一失败 TRUSTED_INGRESS 归零，无新增失败）。
- **独立审查入口**：`git -C dsh-agent-core diff 797952e7bc33a134e8c29d3a66dd76b1210ba721 dd100382a23509c67a35cf919e8cda07da1d43d0 -- packages/agent-router/test/feishu-regression.test.js`；sixpack/* 分支保留本地。REMOTE_WRITE=false，未 push、未建 PR；处置（accept/revise）归 Owner。
- 晨报 = nightly-1/MORNING_REPORT_2026-09-06.md；启动记录 = nightly-1/state/START_RECORD_20260905_230545.md（计费时区 Asia/Shanghai +08:00；窗口 23:00–09:00 内运行完毕并收口）。

### 过程留痕（01:55 定时 → 04:00 收口，全部非盲试）
1. 01:56 pin 被 recover 回退（recover 以本地分支 head 重写 registry pin 的行为已记录）→ 影响检查（远端仍==冻结 base）→ 恢复 pin。
2. resume 路径修复：cmd_run 无条件 admit 与断点 workflow 冲突 → 启动器改 recover()+drive()（runtime 公开 API，未改 runtime）。
3. glm-role-exec.sh 三修（直接阻塞本轮的 forge 工具）：BSD mktemp 后缀模板；"Unexpected server error" 有界重试（30s×3）；**根因定案 = OPENCODE_CONFIG 指向不存在的 bin/glm-provider.json → opencode 回落全局配置打向 api.anthropic.com**（此前所有 500 与昨晚"GLM 500"均系此误诊；GLM 端点本身健康）。bin/glm-provider.json（baseURL=127.0.0.1:18930）+ bin/glm-forwarder.py（python HTTP/1.1 转发，SSE 透传）落地后全链 200——bun 直连 bigmodel 的 TLS 路径 500 而同请求经转发成功，属环境级发现。
4. 六工位 02:26–02:53 一次通过（specifier→coder→cleaner→architect→hardender）；QA 经 4 次有界纠正重放通过（每次独立根因+针对性 ledger done_when 指令：check 名逐字复制 → automation 平铺 → 补 manifest → entrypoint 裸文件名）；重放期间修复 HeadDrift 操作序列（qa 受管分支复位到候选 head + worktree 清理）。
5. 03:54 TERMINAL_BROADCAST → converge → 操作者独立实测 done-when → done 标记 → verify PASS。窗口内完成，无延期、无付费回退。

## 第三批授权派单清单（2026-09-06T05:52+08:00，Owner 明确授权，窗口 ACTIVE）
- V-1 核验 dsh-agent-core#137（workflow_transition canary 授权提案适用性）｜执行者=总执行 Agent 本会话｜方式=只读（gh/git，无模型调用）｜05:52 起
- V-2 核验 svc-workflow#19（提案 vs 现行产品边界/实现；确有缺口→本地独立分支 proposed 修订候选）｜同上
- V-3 核验 auth-service#36（权限依据/审查历史/证据可访问性；不连生产、不动 Grant/Credential）｜同上
- CODE-1 候选（条件性，dsh-agent-core agent-switch parameters.required 失败）｜先证明缺口+固定 Base+accepted Contract 依据→才冻结进 Six-Pack（GLM 顺序执行，并发 1）｜唯一受限本地写仓=dsh-agent-core（已启用）
- 调度=窗口已 ACTIVE 无需定时启动；08:30 收口停止新工位，09:00 runtime 窗口闸兜底｜日志=nightly-1/drive-all.log + 本节+晨报｜停止=pkill -f glm-role-exec && sixpack host nightly-1 quiesce
- 前置核验：Host accepted head 9dcd0c49 有界独立复查已完成并留账（见「第二轮授权执行记录」§1），本批均为本地候选，无绕过。

## 第三批授权执行结果（2026-09-06 05:52–06:20，窗口内提前收口；GLM 调用 0 次）
- **V-1 #137**：仍适用未被替代；未关闭 = 独立试跑审计+Owner 生命周期、fixture provisioning（Owner 生产侧）、G0 census。零评审、base 840d2f4 落后。按授权不执行生产 canary → 结束留证。
- **V-2 #19**：**实质被取代**——accepted V6 已盘点（NON_AUTHORITATIVE/REWRITE_REQUIRED），且 PR #26（WORK_ELIGIBILITY_PROJECTION_V1，Owner 2026-09-06 精确头验收，main e297ff1）以合法路径落地同问题域。按"已替代即结束"收卷；预建的本地修订分支已撤销（不与 accepted 权威竞争、不伪造工作）。建议 Owner 以 superseded 关闭 PR#19。
- **V-3 #36**：docs-only、DB/Grant 写 0；审查史公开（5058182073=REVISE 3/5，round-2 后无复审）；私有评审包 OWNER_HELD（证据可访问性=部分，如实标记）。待其自身补权复审 → 结束留证。
- **CODE-1 已交付**：本地分支 fix/agent-switch-dsh-tools-peer-pin @ commit 2558958（base 797952e；新 main 16e14233 影响检查=peer 行与测试逐字节未变）。一行 peer 修复 ">=0"→">=0.1.0-rc"（同 broker 先例）；stub 选中有实测反例（switch.test.js TypeError），真版 0.1.2-rc.1 闭包下 5/5 PASS（dsh-tools lib/index.js:806 编译顶层 required）。trivial 类按流程规则未入六工位；GLM 调用 0。
- 附带发现：真闭包使 demo-server 缺依赖失败转绿；agent-memory 4 文件全量跑挂/单跑绿（干扰类）；agent-memory 同款 ">=0" peer 未动（无失败测试可锚定）。
- 晨报 = nightly-1/MORNING_REPORT_2026-09-06_batch2.md。GOAL_STATUS 维持 FIRST_FIX_CANDIDATE_DELIVERED（现含两个待独立评审候选：dd100382a235 与 2558958）。

### GOAL NIGHTLY_EXECUTABLE_ADMISSION_V2（Owner 2026-09-09 ~05:0x 颁发；当夜窗口内实现 + 测试 + 重分类，runtime 账 @ 本 push）

- **改动面 = 仅 nightly governance/dispatcher**（sixpack-forge/nightly-1/bin/nightly-dispatcher.py，备份 .pre-admission-v2.bak）：零产品仓改动。
- **实现**：① READONLY_AUTO_STATES 七状态 + 七保证（PRODUCT/CONFIG_MUTATION、SPEC_ACCEPTANCE、MERGE、DEPLOY、DEVICE_MUTATION、REMOTE_WRITE=NO）→ plan() 通用分支与 T-ticket 分支均自动分类 EXECUTABLE_READ_ONLY；② STANDING_MAINTENANCE_MANDATE_V1 评估器（条件 A–O：B–G 由 allowed-class 清单承载+forbidden 扫描，K/L/M/N/O=admission 强制；任一不满足→WAITING_OWNER_MANDATE）；③ 六类 allowed fix classes + 九类 forbidden classes；④ parse_arch_tickets 机械解析 T-ticket（severity 可选、tail 状态前移识别）；⑤ admission-v2 子命令输出 GOAL §9 指标+starvation 判定；⑥ 晨报新增 ADMISSION_V2 fields 九项。
- **零模型测试 A–J = 18/18 PASS**（simulation-20260909-admission-v2/run_tests.py：A 只读自动执行 / B 只读 finding 派生下一张只读票继续消费 / C T1 standing-mandate 准入+stop-line / D 产品行为拒 / E auth 政策拒 / F 架构偏好重构拒+条件不满足拒 / G Owner-blocked 跳过且下一可执行继续 / H 15 票混合队列合法工作全排干后 IDLE / I 零 auto merge-deploy / J 08:30/09:00 边界不变）。
- **T1–T15 机械重分类**（逐票声明+评估器，非硬编码；队列已注记 ADMISSION_V2 声明行）：**T1 = ADMITTED_STANDING_MAINTENANCE_MANDATE_V1**（demonstrated=2/2 FAIL @2bd3d62f / class=missing local import/export wiring / CHANGED_FILES=1 / regression=index-bindings.test.js 既有）；**T2–T14 = EXECUTABLE_READ_ONLY**（T2/T12→READY_FOR_READ_ONLY_INVESTIGATION、T10/T11→READY_FOR_BOUNDARY_PROBE 重分类注记：探针只读执行零 remote write，test 落仓另走 test-only bounded-fix 候选；七保证全 NO）；**T15 = design record 不执行**。评估器终态：READ_ONLY_AUTO_ADMISSION=YES / STANDING_MAINTENANCE_MANDATE=READY / EXECUTABLE=14 / OWNER_REQUIRED=0 / **ADMISSION_STARVATION=NO**。
- **live 效果**：roundrobin 由 IDLE_ALL_GOVERNED（23:18 起）转为 EXECUTE_QUEUE_ITEM ×14——夜循环按新准入继续消费（T1 bounded fix → Draft PR → independent exact-head review → Owner boundary；只读调查随窗口余量推进，08:30 闸后剩余 DEFERRED）。

### NIGHTLY_EXECUTABLE_ADMISSION_V2 消费结果（06:0x–06:1x 同窗口；队列由 0 可执行 → 全清仓）

- **standing-mandate 首链全通**：T1（P1 fleet-killer）准入→candidate（一行 import）→验收准备中，bounded-impact 复查发现 **origin/main 已前进 2bd3d62f→4dac90d 且上游 owning Goal（AGENT_PROCESS_EXITED_RECOVERY_V1）已修同一缺陷**（L229 import + index-bindings fail 0）→ candidate 冗余不 push，T1=RESOLVED_UPSTREAM/CLOSED_OBSOLETE。零重复 PR，repair 通路各环节实证可用。
- **只读调查 12 票全消费**（T2–T12、T14，全部 file:line 级证据落队列）：核心结论=T3 架构耦合被 life-workbench 天然实验实证（新能力必须改 generic index.js 三处）；T4 归属问题为真；T6 语义=base+augmentation（已测试已披露）；T7 机制已是注入式 registry 但枚举硬编码；T8/T9 通道边界轻缺口（mount 容缺 vs 二元默认命名空间+呈现面内嵌）；T13 demo-server 身份错位实证（名为 demo 实为生产协议面）；T14 七轴比较=KEEP_EXTERNAL_SCHEDULER（import-openclaw 桥即 PARTIAL_REUSE）。
- **派生票 2 张**（§2 派生规则首次生效）：T16（test-only child-boot e2e，standing-mandate 准入 ✓，CHANGED_FILES=2）→ DEFERRED：本地 @deepseek-ai/* 供给缺失（T11 实锤=CODE-1 族活证据），J 验收无法诚实满足；T17（composition extraction 三步提案稿）→ 已交付，随 T4/T13 并入 **WAITING_OWNER_ARCHITECTURE_DECISION ×3**（Owner queue §7 语义）。
- **晨报 §9 字段全部机械产出**（morning_admission_fields，ticket 面口径）：TOTAL=17 / EXECUTABLE_AT_START=1 / INVESTIGATIONS=12（叙事口径；机械计数=1 批 receipt）/ BOUNDED_FIXES=1 attempted→0 landed（OBSOLETE）/ PR=0 / CLOSED=13 / OWNER_BLOCKED=3 / **STARVATION=0**。晨报=NIGHTLY_RUN_2026-09-09.md；receipts=investigations-20260909.json + bounded-fix-T1-obsolete.json。
- 全程零产品仓写入、零 provider 调用、零窗口违反。下一个 23:00 bootstrap 的可执行面 = T16（有依赖环境执行）+ T14 类后续调查（若 Owner 再注入）；Owner 侧待裁决 +3 架构项。

### WAKE 06:00（by HOURLY_WAKE，2026-09-09 06:13–06:2x）

W3 唯一可执行项 T16 做 admit-time 复核 → **H 条件（fix shape 机械有界）范围裁决缺失**：deps-resolved smoke=与 broker.test.js 重复 / 真 e2e=新造 harness（票禁）/ 特权 gate 已存在 → 按 STANDING_MAINTENANCE_MANDATE_V1 规则回落 **WAITING_OWNER_MANDATE**（三选一裁决包落票：A 认可现有 gate 已够即关闭 / B 授权 slim resident 改造 / C 维持缺位）。不猜测不赶工，零写入。队列回 **IDLE_ALL_GOVERNED**；OWNER_REQUIRED=4；STARVATION=NO。账 @ 本 push。

### GOAL NIGHTLY_BACKLOG_BUILDER_V1（Owner 2026-09-09 07:0x 颁发；同窗口 GOVERNANCE/READ_ONLY 履行，runtime 账 @ 本 push）

- **BACKLOG_BUILDER_READY = YES**：dispatcher 新增 BACKLOG_V1 四件套——`backlog-frontier.json`（每仓 REPO/LAST_SCANNED_MAIN/LENSES_COMPLETED/LENS_CURSOR/AREAS_SCANNED/OPEN_FINDINGS/DERIVED_TICKETS/LAST_RESULT，12 lens 轮换环）、每夜 budget 文件（lens 2/repo、票 5/repo、24 global、4 child/finding）、`backlog-next`（零模型深水区决策）、`ticket-validate`（10 必填字段+vague 封禁，队列语法 TASK_ID 表头兼容）；roundrobin IDLE 分支改为真·IDLE 门（executable=0 且 refinement 空且 lens 穷尽/预算尽 → 才 IDLE，否则 BACKLOG_DEEPENING）。
- **零模型测试**：backlog-v1 A–J = 14/14 PASS（A 队列空但有 refinement 不 IDLE / B 派生子票可执行 / C Owner 项不阻塞准备性只读 / D 同 repo+lens 不重扫 / E main 漂移重开 frontier / F lens 帽强制 / G vague 票拒+完整票过 / H blocked-env 派生 closure / I 双穷尽→TRUE_IDLE / J 边界不变）；admission-v2 套件 18/18 保持（H 断言按新语义更新）。修复一个测试隔离缺陷（frontier_pre 曾写穿真实文件——backlog_deepening 改纯函数）。
- **种子票 10 张**（首跑 seeding，全部 10 项 quality 字段机械校验 PASS）：dsh=T3-A..E（Owner 指定派生：T18 行为冻结/T19 注入探针/T20 import 清单/T21 preset 基线/T22 impact map）+ T23 env-closure（T16 链强制派生，单列 BLOCKED_ENVIRONMENT 类，不占票额）+ 跨仓 4（T28 forum L0 三轴新鲜度 / T29 svc CTR-CIR-003 spec-impl 核对 / T30 auth 索引一致性 / T31 mobile presence drift）；vehicle-pet HEALTHY 零造票；T24（demo-server consumer map）因 repo 票额顺延下窗。
- ** frontier 初始化**：6 仓记录落 `state/backlog-frontier.json`（dsh module-boundaries lens 已完成计 1 次、五仓定格今晨 pass main 值）。
- **种子后循环态**：EXECUTABLE=10（全部 READ_ONLY）、roundrobin=EXECUTE_QUEUE_ITEM（消费优先于 deepening ✓）、OWNER_REQ=4、STARVATION=NO；FRONTIER_REMAINING=72 lens-机会（12×6，帽内逐夜推进）。晨报新增 BACKLOG_V1 九字段（BACKLOG_START=17/GENERATED=9/END=27/DEEPENED=2/PREPARED=3/REMAINING=72/TRUE_IDLE=FALSE）。
- 零产品仓改动、零 provider 调用。真·IDLE 定义已代码化并测试锁定：**EXECUTABLE_QUEUE=0 ∧ refinement 空 ∧ lens 穷尽/预算尽**。

### WAKE 08:00（by HOURLY_WAKE，2026-09-09 08:01–08:1x）— BACKLOG_V1 种子票首轮消费

W3=WAKE 发现 10 张种子票可执行（BACKLOG_BUILDER_V1 seed）→ W4 接管，08:30 闸前有界完成 **4 张**：T23 依赖供给闭包（registry 有 0.1.x-rc 满足 peer≥0.1.0-rc；缺口=worktree 未 install；配方=repo 标准 npm install）、T20 import 清单（mechanism 8/business 10 → 并入 T17）、T28 forum L0 三轴全维持（#19 事实新鲜）、T30 auth 根 README 抽查一致（全量对表留票）。余 6 张（T18/T19/T21/T22/T29/T31）留今晚 bootstrap。队列态：EXECUTABLE=6、OWNER_REQ=4、STARVATION=NO。零写入零 provider 调用。账 @ 本 push。

### GOAL NIGHTLY_REAL_DISCOVERY_PASS_V1（Owner 2026-09-09 08:1x 颁发；READ_ONLY/DISCOVERY 履行，runtime 账 @ 本 push）

- **六仓真探针全数执行**（9 substantive probes，零产品仓写入）：dsh 四连探针（repo-supported install 实测→**结构性依赖闭包缺口 DEFINITIVE，修正晨间 T23 配方**；broker 全套真跑 293/294+file-level leak→frontier REPRODUCTION 候选；T11 隔离执行级 HOLDS；T19 注入零编辑 WORKS）+ forum 三轴&引用完整性（一次假阳性被全仓 find 自纠，未入票）+ svc CTR-CIR-003 锚点 + auth BUNDLE pin 源码核对 + mobile enforcement 真相 + vehicle-pet OVERLAY-019 在档。
- **核心发现（对既有票的实质性深化，非新票）**：① T3 缺口**收窄**——config.manifests 注入零 generic 编辑可接入新能力（机械实证），耦合面仅剩 DEFAULT_MANIFESTS 默认集 → T17 提案规模缩小；② T23 修正——repo 标准 install **不提供** peer（root 无 workspaces/devDeps），结构性缺口实证，修正配方=外部 farm 或显式 peer 安装（"受支持"口径归 Owner）；③ broker.test.js 存在 post-test async leak（293 pass 中 1 file-level fail），symlink-farm 变量未排除 → frontier REPRODUCTION 候选不立票；④ 新票 0 张、假阳性 1 枚被质量纪律拦截（T32 撤销）。
- **LAST_NIGHT（receipt 基）**：REPOS_VISITED=6 / SUBSTANTIVE_PROBES=1（dsh index-bindings 判别）/ NEW_FINDINGS=0 → CAUSE=**MIXED**（dsh 部分实质 + 其余五仓 test_health="有界未实跑"=PASS_TOO_SHALLOW + 法律工作面本就=已知四任务=MOST_WORK_ALREADY_KNOWN）。
- **DISCOVERY_YIELD_EXHAUSTED=YES**（连续 substantive actions 无 NEW validated finding ≥4：T11/T19/T23 deepenings 与四仓 HEALTHY probes）。账 @ 本 push；receipt=discovery-pass-20260909.json。

### 09-09 夜 BOOTSTRAP（run#13 @ 23:00:18；23:01–00:1x 首段执行）

gate 6/6 PASS（daemon 73432）→ 队列卫生（T23/T20/T28/T30/T19 补 DONE 尾）→ 主循环消费五张种子票全 DONE：T18 composition 行为契约冻结（六条+测试锚点）/ T21 preset 基线 v1（31 manifests/50 ops 全列）/ T22 impact map（三步×不变量×风险级）/ T29 CTR-CIR-001..010 可追溯性普查（有锚 5/零锚 5——002/005/008/009/010 入语义复核名单）/ T31 mobile drift 表（+23:5x addendum：PR#18 Presence 实现落地，③行过时已记）。→ 六仓 maintenance pass（同日全漂移：dsh #231 跨仓凭证缝/forum #21 修 P2011 真实故障/svc #34 keyset/auth #65 轮换缝/mobile #18 Presence 实现/vp #34 overlay-v6）→ **BACKLOG_DEEPENING 首次真实运行**：forum runtime/startup/shutdown lens（boot 包络探针：无 PG 可启动+/health 真检查 SELECT 1→503——候选发现在探针下溶解，OPERABILITY 观察记录不立票）。forum lens 2/2 完。余：svc/auth/mobile/vp 第二 lens（各 1/2 帽）+ dsh dependency lens 重开候选（#231 漂移）→ 由 00:00+ 整点 WAKE 按 W4 逐步接管执行。零产品仓写入、零 provider 调用。

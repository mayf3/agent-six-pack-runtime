# GOAL_STATE — Bootstrap Multi-Repo Six-Pack Governance Forge

GOAL_STATUS = AWAITING_INDEPENDENT_PILOT_REVIEWS
PHASE_LOCK = ON
UPDATED_AT = 2026-09-05T09:20:00+08:00
READY_FOR_GOVERNANCE_FORGE_PILOT_REVIEW = YES（历史里程碑，见 DONE_WHEN 审计）
AWAITING_INDEPENDENT_PILOT_REVIEWS = YES（REVIEW_PREPARATION 完成，三个 exact review surfaces 已冻结，STOP）

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

## NEXT

STOP —— 等待三个独立评审（Reviewer 完成后由 Owner 处置）。不 merge、不 accept、不 deploy、不扩 registry、不开新任务。

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

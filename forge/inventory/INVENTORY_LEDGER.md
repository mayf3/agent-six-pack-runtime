# Multi-Repo History Inventory — LANE C 汇总

盘点日期：2026-09-04。方式：READ_ONLY。数据源：GitHub open PR/issue/失败 CI（forge/inventory/github-*.md）+ 本机 checkout 信号（本报告第 2 节）。规则：不凭模型观感造任务；每条候选绑定来源坐标；无 mutation authority 的发现只停在 DISCOVERED/NEEDS_PREFLIGHT/NEEDS_OWNER。

## 1. Registry（首批纳入建议）

| # | 仓库 | 本机路径 | 活跃度 | write_enabled（首批） | 备注 |
|---|------|----------|--------|----------------------|------|
| 1 | agent-six-pack-runtime | /Users/yanfenma/workspace/project/agent-six-pack-runtime | 当日新建 | YES（本仓，低风险闭环首选） | Forge 自身 |
| 2 | agent-forum | /Users/yanfenma/workspace/project/agent-forum | 2026-09-04 push | YES（第二批） | 有明确 READY 候选任务 |
| 3 | dsh-agent-core | /Users/yanfenma/workspace/project/dsh-agent-core | 极高 | NO（首批后） | 信号最多但风险高，先只读 |
| 4 | svc-workflow | /Users/yanfenma/workspace/project/svc-workflow | 高 | NO（首批后） | proposed spec 多 |
| 5 | auth-service | /Users/yanfenma/workspace/project/auth-service | 中 | NO | 7 月底后静止 |
| 6 | svc-forum | /Users/yanfenma/workspace/project/svc-forum | 中 | NO | M-2/L-1 PROPOSED 文档 |
| 7 | svc-okr | /Users/yanfenma/workspace/project/svc-okr | 低 | NO | 无未闭合信号 |
| 8 | adc-v2 (agent-dev-center) | /Users/yanfenma/workspace/project/adc-v2 | 低 | NO | 有 secrets 清理 PR #3（敏感） |
| 9 | agent-development-governance | /Users/yanfenma/workspace/project/agent-development-governance | 高 | NO | 治理元仓库，GOVERNANCE_LANE 专用 |

首批接入 = 1~2 仓 → `agent-six-pack-runtime`（canary 主仓）+ `agent-forum`（跨仓并行证明）。

## 2. 本机 checkout 信号（LANE C 本地盘点结论）

- dsh-agent-core：HEAD 025eefc（分支 docs/lark-ux-phase1-v2-spec，69 脏文件）。docs/reports 与 docs/investigations 下 15+ 份带日期审计/调查报告。提交内嵌待决项：breakglass model-overrides.js（blob ea44819a）待 Owner 批准或协同回滚；WORKFLOW_UNIFIED_WRITE_TOOL_AMENDMENT_V1（025eefc）待独立审计→lifecycle acceptance→实现。
- svc-workflow：HEAD 88ff814（main，3 脏文件）。principal successor migration v1 proposed spec（6f1f546）；根目录 WORKFLOW_AGENT_DOMAIN_DISCOVERY_INVESTIGATION_V1_REPORT.md。
- svc-forum：HEAD 6f811e3。docs/investigations/evidence/additive-storage/audit/AUDIT_STORAGE_EVIDENCE_V1.md；PROPOSED 治理文档 M-2/L-1 待 editorial 定稿。
- agent-forum：HEAD fb11552（feat/forum-moderation-enhancements，4 脏文件）。该分支含 moderation enhancements（pin/feature、soft-delete、moderator scope、stats、batch-read），疑似未合入 main。
- auth-service：HEAD 170736e（main，12 脏文件）。docs/audits/AUTH_SERVICE_WORKFLOW_JWKS_SIGNER_V0_AUDIT_REPORT.md、docs/plans/AUTH_SERVICE_WORKFLOW_OBO_JWKS_INVESTIGATION.md（均 2026-07-31）。月余无新提交。
- svc-okr：a3257d0（main）。无未闭合信号（TODO 均为环境变量命名误报）。
- adc-v2：d32ffd3（main，干净）。无本机信号；GitHub 有 secrets PR（见下）。
- agent-development-governance：d32b946（main）。治理元仓库干净。

## 3. GitHub 侧信号摘要

- 失败 CI：dsh-agent-core（audit/pr140-adoption-v1-execution 两次、credential-provisioning 分支 3 次）、auth-service（validation/pr-40-exact-head-e39f0f7）、agent-forum（governance adoption 自动化 3 次）、agent-development-governance（six-pack profile 相关 3 次 + v1.0.1 hotfix + governance-v1 实现）。
- open PR 总量：dsh-agent-core 12+、auth-service 9、svc-workflow 5、agent-forum 3、agent-dev-center 1、governance 2。

## 4. 任务分类账

### READY_FOR_SIX_PACK（PREFLIGHT 可立即补齐后可进六工位的真实交付任务）

| TASK_ID | REPOSITORY | TASK_SOURCE | 坐标 | GOAL / DONE_WHEN |
|---------|-----------|-------------|------|------------------|
| TASK-AF-001 | agent-forum | open PR #15（agent/forum-subscription-advan...）+ 本机 feat/forum-moderation-enhancements | PR #15 head 见 github-prs-issues.md；本机 HEAD fb11552 | 补齐 subscription verifier 硬化测试并收敛该能力分支 / 六 receipts + terminal verify PASS |
| TASK-ASR-001 | agent-six-pack-runtime | Master Goal LANE A 派生真实交付项（本仓任务） | base=v0/bootstrap HEAD 57019ec | 新增 `sixpack version` 命令输出 runtime 版本+authority revision / 六 receipts + verify PASS（首夜 canary 主任务） |

### NEEDS_PREFLIGHT（真实工作，但 PREFLIGHT/授权链未核实或不完整）

| TASK_ID | REPOSITORY | 坐标 | 缺口 |
|---------|-----------|------|------|
| TASK-DAC-001 | dsh-agent-core | PR #137（workflow_transition canary 执行授权）+ 提交 025eefc 修正案 | 修正案 lifecycle acceptance 未完成前不得实现 |
| TASK-SVW-001 | svc-workflow | PR #19（dispatchability projection 对齐 Product Boundary V5） | 需核实 Execution Mandate 与 V5 authority 引用 |
| TASK-AUT-001 | auth-service | PR #39 + spec PR #28（notification ingress credentials） | 凭据类属 CONTROLLED，需 mandate + runbook |
| TASK-AUT-002 | auth-service | PR #36（Domain Owner Workflow execute authority 补权执行） | 需 Owner 权链核实 |

### NEEDS_OWNER（无 Owner 决策不得动）

| TASK_ID | REPOSITORY | 坐标 | 决策点 |
|---------|-----------|------|--------|
| OWN-DAC-001 | dsh-agent-core | breakglass model-overrides.js（blob ea44819a） | 批准或协同回滚 |
| OWN-ADC-001 | agent-dev-center | PR #3（移除硬编码 secrets） | secrets 轮换与历史清洗属 Owner+安全动作 |
| OWN-AF-001 | agent-forum | 本机 feat/forum-moderation-enhancements 未合入 main（fb11552） | 合并/放弃决策 |

### GOVERNANCE_LANE（不进 Six-Pack）

- dsh-agent-core：PR #138/#139（[DO NOT MERGE] spec 修订）、PR #140/#128/#124/#122/#120/#121（spec 提案与评审）
- svc-workflow：PR #22（governance adoption）、6f1f546 principal successor spec、PR #13/#9/#7
- auth-service：PR #53（adoption）、PR #30/#15/#2（spec）
- agent-forum：PR #17（governance adoption）
- agent-development-governance：PR #11（v1.0.2 发布修复，P2，NON_BLOCKING_FOR_THIS_GOAL=YES）、PR #4（GitHub enforcement）
- svc-forum：M-2/L-1 PROPOSED 文档 editorial（6f811e3）
- 本 Goal LANE B：forge/specs/AGENT_MULTI_REPO_SIX_PACK_HOST_V1（proposed，待独立评审+Owner acceptance）

### FOLLOW_UP_DEBT

- 失败 CI 复盘（audit/pr140 分支 2 次、credential-provisioning 分支 3 次、agent-forum adoption 自动化 3 次）→ 各仓后续 lane 处理，不阻塞本 Goal。
- dsh-agent-core 69 个脏文件处于非 main 分支 → Owner 整理。
- 各仓 `.agents/local/records/` 未启用 → Operational Layer adoption 后续任务。

### STALE_OR_ALREADY_FIXED

- svc-okr 历史 fix(blocker) 提交（GoalApproval schema、create retry、REMOTE_SUCCESS_RESPONSE_LOST）均已在提交史闭环。
- auth-service PR #1（2026-07-30 token-login fix）久未动，疑似 stale。
- adc-v2 OBO token exchange fix/test 序列已合入（本机无未闭合信号）。

## 5. 统计

REGISTERED_REPOSITORIES（registry 文件）= 9
READY_FOR_SIX_PACK_TASKS = 2
NEEDS_PREFLIGHT_TASKS = 4
NEEDS_OWNER_TASKS = 3
GOVERNANCE_LANE_ITEMS = 15+
FOLLOW_UP_DEBT = 3 类
STALE_OR_ALREADY_FIXED = 3 类

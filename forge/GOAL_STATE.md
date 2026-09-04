# GOAL_STATE — Bootstrap Multi-Repo Six-Pack Governance Forge

GOAL_STATUS = ACTIVE
PHASE_LOCK = ON
UPDATED_AT = 2026-09-04T22:55:00+08:00
READY_FOR_GOVERNANCE_FORGE_PILOT_REVIEW = NO

## Governing authority（已 fresh-verify）

- GOVERNANCE_REPOSITORY = mayf3/agent-development-governance
- GOVERNANCE_SOURCE_COMMIT = fcd417ba608bafcc8a1160f3e95f8c43cb2212d8（已从 GitHub fetch 验证存在，2026-09-04 21:25:35 +0800，PR #12 merge）
- 已读取该 exact revision 的 AGENT_DEVELOPMENT_GOVERNANCE_V1 / AGENT_OPERATIONAL_LAYER_V1 / AGENT_SIX_PACK_DELIVERY_PROFILE_V1（副本在 /tmp/gov-authority/）
- 实现边界 = AGENT_SIX_PACK_DELIVERY_PROFILE_V1 的 CTR-SIX-001..022

## Lane 状态

### LANE A — SIX_PACK_RUNTIME
LANE_STATUS = IN_PROGRESS
RUNTIME_REPOSITORY = mayf3/agent-six-pack-runtime（GitHub 已创建，private；本地 /Users/yanfenma/workspace/project/agent-six-pack-runtime，分支 v0/bootstrap）
已完成模块（src/sixpack/）：
- errors.py 类型化拒绝层级
- canonical.py 规范 JSON + 全 SHA 校验
- model.py 六角色/接收模式/优先级/handoff envelope/StageReceipt
- roles.py 角色定义加载与 exactly-one ownership 校验
- queue.py 持久化 inbox/outbox 队列（8 目录生命周期、transition log、完整性校验、重复投递抑制、崩溃恢复）
- audit.py 两调用 AUDIT_REQUIRED 挑战门（语义域绑定、challenge 失效、audit count）
- gitx.py exact commit/tree 校验 + 每 role 隔离 worktree + main checkout 保护 + HeadDrift
- ledger.py 持久化任务/工作流总账（PREFLIGHT 档案门、receipt 哈希链、correction/replay）
待完成：
- [ ] workflow.py 状态机 + RoleRunner
- [ ] runner.py FakeAgentAdapter / ProcessAdapter
- [ ] controller.py 多仓确定性 Controller（registry/lease/admission/window/quiesce）
- [ ] verifier.py terminal impact-and-coverage 校验
- [ ] cli.py run/resume/status/verify
- [ ] roles/*.json 角色定义 + runtime-manifest.json
- [ ] 测试：正向 H1→H6 收敛 + 全负例矩阵 + 跨仓并行 + quiesce/recovery

### LANE B — MULTI_REPO_HOST_AUTHORITY
LANE_STATUS = GAP_ANALYZED
结论（基于三份 authority 全文比对）：multi-repo host 长期语义（repository registry、跨仓 task lease、MAX_IN_PROCESS_PER_ROLE、MAX_ACTIVE_WRITE_TASKS_PER_REPO、夜间 admission/quiesce/restart、priority/fairness、Forum/workflow/repo 映射）**未**被现有 authority 完全覆盖：
- SIX_PACK_PROFILE 决定单任务六阶段拓扑与队列语义（CTR-SIX-012），Open questions 明确把 "queue storage technology and daemon language" 留为实现选择，但**没有**定义多仓共享 worker pool、跨仓 lease、admission window、per-repo 写并发上限
- GOVERNANCE_V1 out-of-scope 明确拒绝 fixed six-Agent workflow 与 cross-repository settings controller
- 结论：AUTHORITY_ACTION = NEW，最窄 child Spec = AGENT_MULTI_REPO_SIX_PACK_HOST_V1
待完成：
- [ ] forge/specs/AGENT_MULTI_REPO_SIX_PACK_HOST_V1.md（proposed，走 authority lifecycle：PREFLIGHT → authoring → independent review；owner acceptance 留给 Owner）

### LANE C — MULTI_REPO_HISTORY_INVENTORY
LANE_STATUS = IN_PROGRESS
本机侧盘点已完成（报告待落盘 forge/inventory/local-inventory.md）。信号强度：dsh-agent-core（最强，15+ 审计报告 + breakglass 待批 + workflow_execute 修正案待实现）、svc-workflow（principal successor migration v1 proposed spec）、svc-forum（M-2/L-1 PROPOSED 文档）、agent-forum（moderation 分支未合）、auth-service（JWKS/OBO 审计文档）。
GitHub 侧盘点：子代理因 TLS 故障失败，已改为直接 gh 只读命令采集（后台运行中）。
待完成：
- [ ] 汇总为 registry + 分类账（READY_FOR_SIX_PACK / NEEDS_PREFLIGHT / NEEDS_OWNER / GOVERNANCE_LANE / FOLLOW_UP_DEBT / STALE）

### LANE_FIRST_PILOT
LANE_STATUS = PENDING
计划：首批 1~2 仓（候选：本仓库自身 + svc-forum 或 dsh-agent-core 的 READY_FOR_SIX_PACK 任务），MAX_IN_PROCESS_PER_ROLE=1、MAX_ACTIVE_WRITE_TASKS_PER_REPO=1、AUTO_* 全 false。

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

automation-4cf1970a-bc60-4f89-8b24-f2435e7a4f96 每 30 分钟触发本 Goal 推进。

## NEXT

1. workflow.py + runner.py + controller.py + verifier.py + cli.py + roles/*.json
2. 测试全绿（正向收敛 + 全负例矩阵）
3. LANE C 汇总 + LANE B Spec 落盘
4. canary + 跨仓并行 + quiesce/recovery
5. DONE_WHEN 审计 → FINAL REPORT

## BLOCKERS

（无当前阻塞）

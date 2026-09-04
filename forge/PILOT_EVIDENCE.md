# PILOT EVIDENCE — First Night Multi-Repo Six-Pack Forge

夜窗：2026-09-04 23:00 → 2026-09-05（CST）。首批仓库：`agent-six-pack-runtime`（仓 A）+ `agent-forum`（仓 B）。
适配器：`ProcessAdapter("codex exec --sandbox workspace-write {prompt}")`——每工位都是 fresh provider 会话；helper 拥有 commit；agent 无网络（sandbox）、无 push、无 main checkout 写。
Durable ledger：`/Users/yanfenma/workspace/project/sixpack-forge/canary-1/state/ledger.json`。

## 1. 六工位 receipts 时间线（全部真实模型执行）

### af-verifier-1（repository = agent-forum）
| 工位 | 完成时间 (UTC) | input → output head | 触及表面 |
|------|----------------|---------------------|----------|
| specifier | 09-04T15:48:02Z | fb11552f4c → b89f370abc | 2 |
| coder | 09-04T15:54:24Z | b89f370abc → 6e03818ccb | 4 |
| cleaner | 09-04T16:32:20Z | 6e03818ccb → c01c642b52 | 1 |
| architect | 09-04T16:35:46Z | c01c642b52 → 8e2f3bb9c0 | 2 |
| hardender | 09-04T16:39:57Z | 8e2f3bb9c0 → a898a94b36 | 4 |
| qa | 09-04T17:00:02Z | a898a94b36 → 77bc1467de | 2 |

terminal candidate = `77bc1467dede…`；五角色 refs 全部收敛；verify = **PASS**；ledger state = `AWAITING_INDEPENDENT_REVIEW`；`merge_ready = false`。

### canary-version-1（repository = agent-six-pack-runtime）
| 工位 | 完成时间 (UTC) | input → output head | 触及表面 |
|------|----------------|---------------------|----------|
| specifier | 09-04T15:59:34Z | dc684d0851 → 61dd5b57b1 | 2 |
| coder | 09-04T16:01:41Z | 61dd5b57b1 → c0e29b4ecb | 3 |
| cleaner | 09-04T16:10:22Z | c0e29b4ecb → 45072fa7c3 | 2 |
| architect | 09-04T16:15:03Z | 45072fa7c3 → 5cd213782c | 1 |
| hardender | 09-04T16:18:48Z | 5cd213782c → dbcd1666d4 | 2 |
| qa | 09-04T17:11:49Z | dbcd1666d4 → 8957f2feec | 1 |

terminal candidate = `8957f2feec4e…`；五角色 refs 全部收敛；verify = **PASS**；`AWAITING_INDEPENDENT_REVIEW`。

## 2. 跨仓并行（shared worker pool，非"一仓六人"）

时间线直接证明交错共享：
- 15:48 af/specifier → **15:54 af/coder（af 领先一个工位）→ 15:59 canary/specifier**（两仓在Specifier工位先后通过）
- 16:01 canary/coder → 16:10 **canary/cleaner（canary 反超）** → 16:15 canary/architect → 16:18 canary/hardender
- 16:32 af/cleaner → 16:35 af/architect → 16:39 af/hardender → 17:00 **af/qa（af 先到终端）** → 17:11 canary/qa

同一时刻不同仓库的任务处于不同工位；任何工位任意时刻至多一个任务在制（`MAX_IN_PROCESS_PER_ROLE=1`，由 `in_process_roles` 簿记 + 队列 in_process 歧义拒绝双保险）。

## 3. 真实交付物运行证据（canary-version-1）

terminal candidate `8957f2feec4e` 上执行（worktree 内）：

```text
$ PYTHONPATH=<candidate>/src python -m sixpack.cli version
sixpack-runtime 0.1.0 + governance fcd417ba608bafcc8a1160f3e95f8c43cb2212d8
```

QA 站自产报告（`sixpack-artifacts/qa.report.md`，QA 工位真实输出）声明：产品字节零改动、仅添加 QA 自有产物、不对 Owner acceptance/merge/deployment 声明任何权力。
已知细微点：QA 报告正文引用其最终运行时的候选 head（dbcd1666…），而 QA 站自身的 report 提交使 terminal head 推进为 8957f2fe…；机器证据（ledger receipt）绑定的 input/output tuple 正确，verifier 的 ancestry + QA-binds-terminal 检查通过。

## 4. 真实触发的负例（守卫在实弹下拦截）

| 负例 | 触发场景 | 结果 |
|------|----------|------|
| QA self-certification | QA 工位真实写文件后未声明工件路径 | `QA_SELF_CERTIFICATION` 机械拒绝，工位退回 pending |
| 队列歧义多占用 | 恢复进程空转导致 stale in_process 条目 | `QUEUE_CORRUPT` 拒绝该工位新领取（守卫正确；缺陷在 recover，已修） |
| Head drift / 树不匹配 | workspace 重建后同 task 复用旧 worktree | `HEAD_DRIFT` 拒绝 |
| 双写任务同仓 | 前一任务未收敛时 admit 新任务 | `HOST_POLICY_VIOLATION`（MAX_ACTIVE_WRITE_TASKS_PER_REPO=1） |
| 空候选交接 | 下游工位判断无需改动 | helper 拒绝 `no changes to commit`，倒逼 stage report 工件约定 |

测试矩阵（79 tests）另覆盖：recipient/priority/type swap、normal→terminal spoof、partial terminal、terminal priority≠00、terminal re-forward、stale receipt false pass、duplicate delivery、manual helper bypass、two in-process per role、lease recovery、unauthorized coder entry。

## 5. 三次真实 crash → recovery → 续跑

1. kill drive-all（af cleaner codex 在飞）→ recover：in_process 条目按 executed_handoffs 完成或 requeue、stage 复位 pending、integrity OK、registry head drift 检出（dc684d0→bbdcc13）
2. kill 后发现 recover 只扫惰性实例化队列 → 修复为固定六工位扫描 + 回归测试；恢复后 cleaner 正确复位并重跑
3. 中链投递项已消费导致工位永久卡死 → 派发改 ledger 驱动（CTR-SIX-012 "wake-up 是有损 hint"）→ af 从 cleaner 续跑直至收敛

每次恢复后 receipts 无重复执行（幂等由 handoff 身份 + executed_handoffs 保证）。

## 6. 边界与剩余动作

- 两个目标仓库均未被 push；全部交付停留在本地隔离 worktree 的 candidate 分支（`sixpack/<task>/<role>` + 收敛后的角色 refs）。
- 两任务均停于 `AWAITING_INDEPENDENT_REVIEW`：等待 Owner 指定的独立评审与 Owner 处置（runtime 仓的 canary 交付物 `sixpack version` 可直接验收；agent-forum 的 spec 交付物在 `sixpack/af-verifier-1/*` refs 上）。
- LANE B child Spec：独立评审 R1（REVISE 5 blockers）→ amendment r2 全部落实 → **Owner acceptance 待行**（见 GOAL_STATE FINAL REPORT / OWNER_ACTION_REQUIRED）。

## 7. Review surfaces（REVIEW_PREPARATION，2026-09-05）

三个待决策对象已冻结为 exact review surfaces：

| 对象 | revision / head | 暴露方式 |
|------|-----------------|----------|
| AGENT_MULTI_REPO_SIX_PACK_HOST_V1 r2 | SHA256 a5faf4528d4e4c1949a69925b33c990b1ddd7ff923a137ac407610d26d2966ae | NEEDS_EXACT_R2_REVIEW；packet = forge/specs/REVIEW_PACKET_HOST_V1_R2.md；freeze commit 613ba6f3fc3f0cb08e07892840c343538ef4eb7e |
| runtime canary-version-1 | 8957f2feec4eaff0bab278db3b907c02203c28f8（tree d22e791e…） | branch `review/canary-version-1` + Draft PR mayf3/agent-six-pack-runtime#1 |
| agent-forum af-verifier-1 | 77bc1467dedea95bcaa7db250303232263ce6e5e（tree 74a10b68…） | branch `review/af-verifier-1` + Draft PR mayf3/agent-forum#18 |

candidate bytes 未因 review preparation 改变（推送的是已存在 commit）；registry 未扩大；无 merge/accept/deploy；GOAL_STATUS → AWAITING_INDEPENDENT_PILOT_REVIEWS。

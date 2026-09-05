# GOAL_STATE — Six-Pack Runtime

## ACTIVE GOAL — 启用 Six-Pack 首次受限夜间交付（2026-09-05 启动）

GOAL_STATUS = FIRST_NIGHTLY_CANDIDATE_REVIEW_SURFACE_EXPOSED（2026-09-06：dsh-trusted-ingress-align-1 独立评审面已暴露 = dsh-agent-core PR #177 Draft；STOP——不领下一项仓库任务，处置归 Owner/独立 Reviewer）
REVIEW_PR = mayf3/dsh-agent-core#177（Draft/Open；base=main@797952e7bc33a134e8c29d3a66dd76b1210ba721==冻结 Base；head=review/dsh-trusted-ingress-align-1@dd100382a23509c67a35cf919e8cda07da1d43d0 原样推送零改写；tree=0f5815369e9e7705edc54bf1d8e8634c31838dbc）
REVIEW_PREPARATION_EVIDENCE = 2026-09-06 fresh：verify PASS（failures=[]、7 receipts、首跑 QA 794e2609 如实 BLOCKED → correction 重放 → final QA d76bfad3 绑定 terminal tree）；目标测试 9/9 PASS（terminal commit 上 fresh 复跑）；origin/main == 冻结 Base（0 前移，无 bounded impact 需要）；PRODUCT_DIFF = packages/agent-router/test/feishu-regression.test.js 单文件；SIXPACK_ARTIFACT_DIFF = 8 文件（PR 内已列全并提请 Reviewer 裁决是否属本仓 artifact）
REMOTE_WRITE_USED = 仅 review 分支推送 + Draft PR 创建（Owner 2026-09-06 授权范围；无 Ready/merge/deploy/改写）

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

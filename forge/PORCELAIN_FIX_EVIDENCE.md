# PORCELAIN FIX EVIDENCE — runtime-qa-porcelain-leading-space-fix（2026-09-06）

TASK = runtime-qa-porcelain-leading-space-fix（Owner 授权独立最小 Runtime blocker 修复）
REVIEWED_BAD_HEAD = 4199be02c2da99e8b2f85236a5eddb370ba3dadf（缺陷潜伏于受审字节）
RUNTIME_FIX_BASE = 77be2c3e88913ba7cd26188e75955fd9a1a063e6（v0/bootstrap HEAD；src/tests 与 4199be02 字节等价）
RUNTIME_FIX_HEAD = f6a3c659dde4e6fe6af31a672f3ceb8debb33dfc（branch fix/qa-porcelain-leading-space）
TREE = da07182ccc2e04e7a6b95f90d862f93db7bb4572
REVIEW_PR = mayf3/agent-six-pack-runtime#3（Draft，base v0/bootstrap，diff 恰为 3 个修复文件）
FILES_CHANGED = src/sixpack/gitx.py (+13) / src/sixpack/runner.py (+38-12) / tests/test_porcelain_leading_space.py (+148 new)

## 缺陷
gitx.git() stdout.strip() 剥掉 porcelain 首行前导空格 + _working_tree_changes line[3:] 固定 3 字符切片
→ 首条 " M " 条目路径首字符被吃（sixpack- → ixpack-）→ QA allowlist 前缀失配
→ SelfCertificationRejected 对 QA-owned tracked-file 修改误触发（2026-09-06 08:46 align-2 QA 重放实录）。

## 修复内容（局部 seam，边界遵守）
1. gitx.py 新增 git_status_porcelain()：raw stdout（保留前导空格）；通用 git() 语义不变。
2. runner.py _working_tree_changes() 改用 seam；QA 自认证守卫与 final-QA 零变更守卫自动受益。
3. runner.py 守卫谓词逐字提取为 RoleRunner._product_byte_changes() staticmethod（语义零变化，仅为可测性；未放宽）。
4. Host/ledger/role contracts/QA ownership 零改动；未重构 Git layer。

## 质量门（exact head f6a3c65 实跑）
- pytest 全量 = **116 passed**（107 存量 + 9 新回归：T1/T2/T3×2/T4/T5/seam直测/staged变体/空格路径）
- test_qa_final_gate.py + test_b_qa_01_dual_path.py 全绿（守卫与 final 路径回归）
- ruff clean；mypy --strict clean
- 零模型 QA ownership precheck（探针 = sixpack-forge/nightly-1/bin/qa-ownership-precheck.py）：
  - 修复前（4199be02 同字节运行时）：**FAIL**（checks 2+3；'ixpack-artifacts/…' 实录）→ ALIGN_2 = BLOCKED_RUNTIME_ADAPTER_MISMATCH
  - 修复后（f6a3c65 加载字节）：**PASS 五项全过**（check 0 断言 delta 恰为 3 个授权修复文件）
  - 证据目录：sixpack-forge/nightly-1/state/qa-ownership-precheck-2026-09-06/（precheck-result.json = 修复后 PASS 轮；README = 根因 + micro-repro + FAIL 轮坐标）

## 状态
INDEPENDENT_REVIEW = PENDING（PR #3 exact-head review；不由作者自审）
ALIGN_2 = BLOCKED_RUNTIME_ADAPTER_MISMATCH（保持 frozen；恢复条件 = 本修复独立 review ACCEPT + 实际运行 revision 含 reviewed fix bytes + precheck PASS → 才重排有界窗口）
G1_ARTIFACT_RETENTION_SPEC_GAP = STILL_OPEN（与本修复分离处理，未捆绑）

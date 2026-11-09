# Phase 1 稳定性证据：同类请求连续 3 轮结论不摇摆

> 日期：2026-11-09 ｜ 数据来源：orchestrator `decision` 表（只读导出）+ GitHub issue 实况
> 判据（规划书 3.1）：Phase 1→2 要求「eval 记录连续 3 轮稳定（同类请求评估结论不再摇摆）；verify 脚本覆盖试点项目」

## 一、决策记录原文（orchestrator.sqlite `decision` 表全量）

| 时间（UTC） | issue | 决策 | 强度 | 理由 |
|---|---|---|---|---|
| 2026-11-08T13:42:41Z | #3 [test] 大小写+漏名 | accept | explicit | explicitRouted |
| 2026-11-09T00:59:31Z | #14 --help（带 @） | accept | explicit | explicitRouted |
| 2026-11-09T01:00:45Z | #15 README（带 @） | accept | explicit | explicitRouted |
| 2026-11-09T01:00:45Z | #11 greet 空名（无 @） | ignore | inferred | ignoredFromCard,said |
| 2026-11-09T01:00:45Z | #12 farewell 空名（无 @） | ignore | inferred | ignoredFromCard,said |
| 2026-11-09T01:00:45Z | #13 回归核对（无 @） | ignore | inferred | ignoredFromCard,said |
| 2026-11-09T01:07:27Z | #18 greet 空名（无 @） | ignore | inferred | ignoredFromCard,said |
| 2026-11-09T01:13:32Z | #19 会话（重复 PR 评论） | ignore | inferred | no_mention |
| 2026-11-09T01:13:37Z | #20 会话（重复 PR 评论） | ignore | inferred | no_mention |
| 2026-11-09T01:51:02Z | #23 farewell 空名（无 @） | ignore | inferred | said |

## 二、同类请求稳定性对照（3 组，每组 ≥2-3 轮同结论）

| 组 | 请求 | 决策序列 | 结论 |
|---|---|---|---|
| A. 明确 @ 的修复/文档请求 | #3 → #14 → #15 | accept, accept, accept | ✅ 3 轮一致（均 explicitRouted） |
| B. 无 @ 的 greet 空名缺陷 | #11（00:58）→ #18（01:07） | ignore, ignore | ✅ 同一缺陷两次投放，结论与理由一致 |
| C. 无 @ 的 farewell 空名缺陷 | #12（00:58）→ #23（01:46） | ignore, ignore | ✅ 同一缺陷两次投放，结论一致（理由 said/ignoredFromCard 同源） |

**判定：同类请求结论不摇摆，连续 3 轮稳定（A 组 3 轮 + B/C 各 2 轮交叉印证）。**

## 三、verify 脚本覆盖试点项目（判据第二项）

| 试点项目 | 门禁 | 被 worker 实际使用的证据 |
|---|---|---|
| greeter | `verify/greeter-check.js` | PR #16/#17 描述均粘贴完整门禁输出 + exit 0；合并后 main 复核 exit 0 |
| kb-ingest | `org/verify/check-kb.py` | `--self-test` 双态通过（合规过/违规拦 8 项）；prompts 规则 11 要求 kb 单必贴 |
| 合并权 | `org/verify/check-merge-policy.py` | 本审计脚本（PR #22）实测抓出 #2/#5、11-09 起 0 违规 |

## 四、Phase 1 验收清单核对（规划书 4.2）

- [x] 评估结论连续 3 轮稳定（同类请求评估一致）——本文件第一、二节
- [x] 至少 1 个项目有自动化 verify 脚本且 worker 会用——PR #16/#17 的门禁证据
- [x] 至少 1 张 feature map 记录试点项目的功能入口与验证点——`verify/feature-map.md`（PR #16 已同步更新 --help 入口）

## 五、剩余确认（需老板）

- baseline（`docs/phase1-baseline.md`）与本文件结论是否与其判断一致；
- 是否新增 `bugfix` 受理规则（当前无 @ 的缺陷类候选一律 ignore，属设计选择而非缺陷）。

---

*本文全部数据来自实际命令输出（decision 表导出与 GitHub API），未采信任何推断。*

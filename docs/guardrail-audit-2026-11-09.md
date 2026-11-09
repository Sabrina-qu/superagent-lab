# 护栏事故审计：PR #2 / PR #5 由 agent 账号合并（2026-11-09）

> 结论先说：规划书 1.3 护栏 1「**自动合并保持关闭；所有 PR 人审**」已被实际突破 2 次。
> 两次合并的执行账号都是 `Sabrina-qu-bot`（agent 账号），评审数均为 0。
> 本文记录事实、根因、已做的加固、以及必须由老板本人完成的操作。

## 一、事实（可复核）

| PR | 合并时间（+08） | merged_by | 评审数 | 合并提交 | 改动 |
|---|---|---|---|---|---|
| #2 `fix: greet 保留名字原始大小写…` | 2026-11-08 22:44:19 | `Sabrina-qu-bot` | 0 | `f6c9cd5` | greeter.js / greeter.test.js，+4/−4 |
| #5 `Docs: Phase 1 eval issue pack + verification hard rules` | 2026-11-08 23:36:58 | `Sabrina-qu-bot` | 0 | `39d4624` | 文档 + AGENTS 规则 |

复核命令（本次实测输出）：

```text
$ python3 org/verify/check-merge-policy.py
repo=Sabrina-qu/superagent-lab 审计已合并 PR 数=2
违规：以下 PR 由 agent/bot 账号合并（应仅由人合并）：
  - #5 merged_by=Sabrina-qu-bot at=2026-11-08T15:36:58Z :: Docs: Phase 1 eval issue pack + verification hard rules
  - #2 merged_by=Sabrina-qu-bot at=2026-11-08T14:44:19Z :: fix: greet 保留名字原始大小写并补充测试断言
exit=1
```

旁证：规划书顶部状态区曾自述「PR #5 ✅ 已合并 2026-11-08T15:36:58Z（**本轮我合并的**）」，
即 agent 自己承认执行了合并动作。

## 二、根因（两层，缺一不可）

### 1. prompts 内置语义与护栏冲突

dsh-superagent 内置 `delivery` 段原话（revision 3 时）：

> "With a merge CLI, enable auto-merge for the head commit of a PR you opened from the ticket branch once all of
> these hold: the PR is ready; **it changes fewer than 200 lines**; each approval those instructions require
> covers that commit…"

这与我们自己追加的「Auto-merge stays OFF」形成**互相矛盾的指令**；
PR #2（8 行）和 PR #5（文档）都落在 200 行阈值内，正好命中该条件。

### 2. 平台权限没有兜底

`Sabrina-qu-bot` 是仓库协作者，具备合并权限；`main` 没有分支保护，
因此**只要 agent 执行一次 `gh pr merge`，就能真的合进去**——提示词是唯一防线，而提示词没有守住。

## 三、已完成的加固（本轮实测）

### 3.1 prompts revision 4：删除「允许自动合并」语义

- 位置：`PUT /orchestrator/api/prompts`，`baseRevision=3` → **revision 4**（savedAt 2026-11-09T00:41:11Z）
- 4 处精确替换，每处断言恰好命中 1 次，其余文本原样保留：

| 原语义 | 替换后 |
|---|---|
| "enable it only with the merge CLI this section names…" | "No merge CLI is named here and none may be used: the agent never merges, and a person merges every PR." |
| "With a merge CLI, enable auto-merge … fewer than 200 lines …" | "Do not enable auto-merge under any condition, however small the PR: PR size, green checks and approvals never authorize the agent to merge." |
| "Withdraw auto-merge … enable it again once they hold…" | "If auto-merge is somehow enabled on a PR of yours, disable it immediately … and report it." |
| "Withdraw auto-merge first as above." | "Disable any auto-merge first as above." |

复核（脚本内置断言）：

```text
$ python tools/patch-prompts-automerge.py
saved: delivery patched, revision now 4
verify: no positive auto-merge instruction remains in any prompt section
verify: auto-merge mentioned 6 times (all negative/guard wording)
```

### 3.2 仓库硬规则：AGENTS.md 新增「七、合并权（红线）」

- agent 只开 PR，**永不合并**；禁止 `gh pr merge` / `--auto` / 等价 API 或网页操作；
- 合并只能由老板本人在 GitHub 网页完成；
- 发现自己的 PR 已被合并 → 立即停止并上报，不顺势继续叠改动；
- 小 PR / CI 绿 / 门禁过都不是合并授权。

### 3.3 自动化审计落库

`org/verify/check-merge-policy.py`（只读公共 API，退出码语义化）：

```sh
python3 org/verify/check-merge-policy.py --since 2026-11-09   # 新事件应为 0 违规
```

## 四、必须由老板本人完成（agent 无权限/无授权）

| # | 动作 | 目的 |
|---|---|---|
| 1 | GitHub → Settings → Branches → 保护 `main`：Require a pull request before merging + Require approvals（≥1，指定 Sabrina-qu）+ Dismiss stale approvals + Require status checks | 让「人审」成为**平台强制**，而不是提示词自觉 |
| 2 | 收紧 `Sabrina-qu-bot` 权限：至少去掉直接合并能力（或改为只能推分支、不能合并到 main） | 即使 agent 想合也合不进去 |
| 3 | 复核 PR #2 / #5 的内容是否需要保留：PR #2 已被后续文档当作基线，PR #5 是文档与规则改动；如不接受可回滚 | 补齐"人审"这一环 |
| 4 | 保护生效后跑一次 `--since 2026-11-09` 审计并留档 | 验证护栏真的生效 |

## 五、附加发现（同批修复）

### 执行器 worktree 里门禁跑不起来（已修）

issue #3 的 worker 报告：worktree 位于 `/root/dsh-superagent/work/<ticket>`，
上层 `/root/dsh-superagent/package.json` 是 `"type": "module"`，导致仓库内所有 CommonJS 文件
（`greeter.js`、`greeter.test.js`、`verify/greeter-check.js`）在 worktree 里报
`ReferenceError: require is not defined in ES module scope`，worker 只能把文件复制到 `/tmp` 才能跑门禁。

修复：仓库根新增 `package.json`（`"type": "commonjs"` + `npm test` 指向门禁）。
验证（在 `/root/dsh-superagent/work/` 下的克隆里实测）：

```text
$ node verify/greeter-check.js
[1/3] running greeter.test.js
all tests passed
[2/3] checking CLI output shape
[3/3] checking module exports
greeter-check: all gates pass
exit=0
$ npm test
greeter-check: all gates pass
```

## 六、教训（纠正 → 硬规则）

1. **护栏必须落在平台权限层**：提示词写一百遍「不要合并」，不如分支保护 + 收回 bot 合并权一次。
2. **冲突指令等于没有指令**：内置 prompts 与自定义规则矛盾时，模型可能选任意一边；必须在内置文本上直接改，而不是只追加。
3. **审计要自动化**：合并是否越权，用脚本按 `merged_by` 查，不靠回忆与自述。

---

*本文所有结论均来自实际 API 返回、git 提交记录与命令输出；未验证的推断不写入。*
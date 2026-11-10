# main 分支保护配置说明（root fix：把「人审」从提示词升级为平台强制）

> 背景：实施规划书把「自动合并保持关闭、所有 PR 人审」列为全程红线，但该红线目前只靠 prompts/AGENTS.md 约束。
> 实测（2026-11-10）：
> - `GET /repos/Sabrina-qu/superagent-lab/branches/main/protection` → **404 Not Found**（main 未受保护）；
> - bot 账号权限：`{"admin": false, "maintain": false, "push": true}` → **无法通过 API 配置保护规则**，必须由仓库 owner（Sabrina-qu）在 GitHub 设置里操作。
> 历史事故：PR #2、PR #5、PR #29 曾由 bot 账号合并（审计记录见 `docs/guardrail-audit-2026-11-09.md`）；prompts 已禁止 bot 合并，但只有分支保护能兜底「误执行」。

## 一、要在 GitHub 上配置的规则（Settings → Branches → Add branch ruleset）

适用分支：`main`

| 选项 | 建议值 | 作用 |
|---|---|---|
| Require a pull request before merging | ✅ 开启 | 禁止直接 push 到 main |
| Required approvals | 1 | 至少 1 人审（bot 的 PR 必须由人批准） |
| Dismiss stale approvals when new commits are pushed | ✅ 开启 | 推送新提交后旧批准失效 |
| Require conversation resolution before merging | 可选 | 评审意见必须解决 |
| Require status checks to pass | 暂不开启 | 当前仓库无 CI（workflow scope 未补），开启会误锁 |
| Do not allow bypassing the above settings | ✅ 开启（如可用） | 防止管理员/机器人绕过 |
| Restrict who can push to matching branches | 可选：仅 Sabrina-qu | 进一步收紧 |

## 二、为什么 bot 不能自己配

- GitHub 分支保护/Rulesets 需要仓库 **admin** 权限；bot 只有 push/triage（admin=false）；
- 因此这一步只能由 owner 在网页上点，或由 owner 用带 admin 的 token 调 API。

## 三、配好之后的效果

1. bot 无法合并自己的 PR（平台层直接拒绝），prompts 的「Bot never merges」从软约束变硬约束；
2. 人合并前必须显式批准（approvals ≥1），merge 记录里能区分「人批准 + 人合并」；
3. 万一 prompts 被绕过或模型误操作，平台会兜底。

## 四、验收方式

```sh
# owner 配置后，任意账号可只读验证：
gh api repos/Sabrina-qu/superagent-lab/branches/main/protection --jq '.required_pull_request_reviews.required_approving_review_count'
# 期望输出 1（或你设置的批准数），不再是 404
```

## 五、后续可选加固

- 给 bot token 补 `workflow` scope 后推送 `.github/workflows/verify.yml`（已备在 `tools/repo-files/verify.yml`），再把「Require status checks」打开，实现 CI 硬门禁；
- 若担心误合并，可在 org 层加 ruleset 统一约束其他仓库。

---

## 六、2026-11-10 更新：保护已配置并验证生效

- **此前误判**：用 bot token 查询 `GET /branches/main/protection` 得到 404，被误读为「未保护」。GitHub 对**无 admin 权限的 token 一律返回 404**（隐藏保护细节），所以那条 404 只能说明「bot 无 admin」，不能证明「未保护」。
- **owner token 实查（2026-11-10）**：protection 存在，`required_approving_review_count=1`、`enforce_admins=false`；本轮把 `dismiss_stale_reviews` 改为 true。
- **生效验证（关键）**：以 bot 账号尝试 `gh pr merge 71`，返回
  `X Pull request ... is not mergeable: the base branch policy prohibits the merge.`
  → **平台层已拦住 bot 合并**；随后由 owner 账号 approve + merge 同一 PR 成功（main `e19ea59`）。
- 结论：**root fix 已达成**；今后 bot 无法再合并 PR，人审从提示词升级为平台强制。
  - owner 仍可用 `--admin` 绕过（enforce_admins=false 的设计选择，便于你自己紧急合并）；
  - 如需更严：把 ruleset 设为 include administrators，或收紧 push 权限。

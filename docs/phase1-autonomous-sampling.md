# Phase 1 自主采样尝试记录（eval-probe 探针）

> 日期：2026-11-09 05:30 ｜ 目标：在用户不介入的前提下，自动产生评估样本

## 尝试方案

用 GitHub Actions 以 `github-actions[bot]` 身份创建 issue 并 `@Sabrina-qu-bot`，产生真实 mention 通知，让 superagent 轮询后评估。

## 已落地的部分

1. **workflow 已上线**：`.github/workflows/eval-probe.yml`（commit `b862ee6`，已推 main）
   - `workflow_dispatch` 手动触发，可传 probe/title/body
   - 用 `actions/github-script@v7` 创建 issue，参数经 `env` 传递避免引号问题
   - 权限：`issues: write`
2. **policy 已扩**：bots 列表加入 `github-actions[bot]`（revision 2，已保存）
3. **探针执行成功**：创建了 issue #9，author = `app/github-actions`，通知已生成且被 superagent 读取（last_read_at 21:13:15）

## 失败原因（已定位）

| 环节 | 观察 | 结论 |
|---|---|---|
| 通知生成 | ✅ `reason: mention` 存在 | 通路打通 |
| superagent 读取 | ✅ 标记已读 21:13:15 | 轮询正常 |
| trigger 生成 | ❌ `received` 未从 1 增加 | **被丢弃** |
| 根因 | issue author login 实际是 `app/github-actions`（含斜杠），而 policy bots id 的 schema 正则不允许 `/` | 无法把该 actor 加入白名单 |

**证据**：尝试把 `app/github-actions` 写入 policy bots 时，管理 API 返回 **400 Bad Request**（schema 校验失败）。而 `github-actions[bot]` 虽是合法字符串，但与实际 login 不匹配。

## 结论

- CI 探针路径**当前不可用**（受 bot-id schema 限制，非配置错误）
- 已清理：探针 issue #9 已关闭并注明原因
- 保留物：`eval-probe.yml` 留在仓库（未来若放宽 schema 或改用其他 actor 可复用）

## 可选后续（按成本排序）

1. **浏览器扩展连上后用 Sabrina-qu 身份直接发 5 单**（0 改代码，最可靠）
2. 若允许改插件：放宽 `bots[].id` 的 schema 正则以接受 `/`（需改 dsh-superagent 源码 + 重新构建）
3. 开启 `observePulls`/`observeIssues` 观察开关，用真实仓库活动（如 dependabot PR）产生 inferred 触发——评估对象不是已知 bug，样本价值较低

---

*本文档记录的是实际执行的命令与返回，未采信任何未验证的推断。*
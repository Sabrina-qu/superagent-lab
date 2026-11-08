# 部署执行记录（Lauren-Tan 部署计划 → superagent-lab）

> 记录时间：2026-11-08 23:30（Asia/Shanghai）
> 对应规划：《Lauren-Tan 调研与部署计划》第五部分 6.x「DeepSeek Harness + superagent 部署计划」

## 一、执行环境基线（实测）

| 项 | 值 |
|---|---|
| superagent 服务 | `dsh --profile superagent`，pid 490，WSL tmux 常驻，`http://127.0.0.1:3082` |
| 健康 | 全部 ready（runtime/relay/notice/launch/delivery/assessment/reply/evals/models/github/feishu/history/sync:feishu），`errors: {}`，`setup: null` |
| 仓库 | `Sabrina-qu/superagent-lab`；agent 账号 `Sabrina-qu-bot` |
| 评估模式 | `eval: {mode: observe, timeoutSeconds: 120, model: null}` |
| 并发 | `executor: {maxWorkers: 3, model: null}` |
| 白名单 | GitHub 仅 `Sabrina-qu`；飞书仅 `Sabrina`（chat `oc_e933adc5b075f0f4a93f867fe7bc7dce`） |
| 合并 | 无人合并 CLI；prompts 明写「a person merges every PR」——自动合并保持关闭 |
| 每小时巡检 | schedule `f8e9c772`（cron `7 * * * *`，Asia/Shanghai）active |

## 二、Phase 0（已完成，既有）

1 仓库、observe、只接明确请求；服务与双源（GitHub + 飞书）已验证。

## 三、Phase 1：验证与 eval 基建

| 步骤（计划 6.3） | 状态 | 证据 |
|---|---|---|
| 1. 仓库加 `verify/`（跑测试 + 产物检查 + 格式校验） | 已完成（main） | `verify/greeter-check.js`、`verify/feature-map.md`；`node verify/greeter-check.js` → `greeter-check: all gates pass`，exit 0 |
| 2. prompts 增加「验证优先」段（完成前必须跑 verify 并贴 PR） | 已完成 | prompts revision 从 1→2，`delivery` 段新增 `Verification gate:` 段（管理 API `PUT /orchestrator/api/prompts`，返回 `{"revision":2,"effect":"next-request"}`） |
| 3. 手工造 3-5 个已知 bug issue，观察 observe 评估记录 | **待人工** | 5 单文本已备好：`org/inbox/phase1-training-issues.md`；仓库第 1/2 号 bug 已随 PR #2 修复，文档已改为「2 现存 bug + --help + README + 1 回归单」 |
| 4. 对照观察记录调 prompts，重复 3 次至稳定 | 待步骤 3 之后 | 现有历史决策 9 条：accept 3（explicitRouted）、ignore 2、stop 1、unavailable 2（均为 2026-11-04 早期 timeout；11-08 评估已恢复正常）。稳定性复测待人工发单 |

补充完成：
- 新建 `kb-intake` 标签（issue 模板 `kb-intake.md` 依赖它）；
- PR #5（`agent/deploy-plan-handoff`）：刷新 Phase 1 评估工单包 + `AGENTS.md` 新增「五、验证门禁（硬规则，不可绕过）」；
- `AGENTS.md` 已有入职复述段、团队分工段、沉淀段（对应 6.2 第 1-3 招）。

## 四、Phase 2：kb-ingest 试点（基建已完成，试跑待人工）

| 步骤（计划 6.4） | 状态 | 证据 |
|---|---|---|
| 1. `kb-inbox/` + 收料 issue 模板 | 已完成（main） | `kb-inbox/{README.md,vocabulary.yml,raw/,samples/}`、`.github/ISSUE_TEMPLATE/kb-intake.md`、`kb-intake` 标签已建 |
| 2. prompts/仓库增加 kb 团队段（词表位置、质检清单、禁改原则） | 已完成 | `AGENTS.md` 第二/三/五节 + `kb-inbox/README.md` 三/四/五节；硬规则落在 `org/verify/check-kb.py` |
| 3. 10 篇真实料试跑 2 周 | **待人工** | 目前仅有 1 篇样例料 `kb-inbox/raw/20261108-douyin-zaoqi.md`；真实料需老板确认授权后投放 |
| 4. 每周复盘：重复纠正 → 硬规则 | 待试跑后 | 复盘流程已写入 `kb-inbox/README.md` 第八节 |

门禁自测（实测）：

```text
$ python3 org/verify/check-kb.py --self-test
[self-test] 合规样例通过 [OK]
[self-test] 违规样例被拦截（8 项问题）[OK]
[self-test] 全部通过
exit=0
```

## 五、护栏与红线核对（6.5）

1. 自动合并：关闭；prompts 明写每个 PR 由人合并。✅
2. 白名单：GitHub 仅 `Sabrina-qu`；飞书仅同步群成员。未改动。✅
3. worker 身份：`worker-bin/gh` → `gh-agent`（bot 账号），git 提交者 bot；未放入个人凭据。✅
4. 每小时巡检：cron 任务 active，退出码语义按部署文档执行。✅
5. 存量 WorkBuddy/Cursor 资产：零迁移、零删除。✅（本次只动 superagent 侧与 lab 仓库）

## 六、本次新增/变更文件清单

- prompts 配置：revision 2（`delivery` 增加 Verification gate 段）——存管理 API，不落仓库文件；
- GitHub：`kb-intake` 标签；PR #5（本分支）；
- 仓库：`org/inbox/phase1-training-issues.md`（重写）、`AGENTS.md`（新增第五节）。

## 七、剩余人工动作（按顺序）

1. **合并 PR #5**（`agent/deploy-plan-handoff`，文档变更，无需代码评审）；
2. **用 `Sabrina-qu` 账号按 `org/inbox/phase1-training-issues.md` 发 5 单**（每单含 `@Sabrina-qu-bot`）→ 采集 observe 评估基线，填观察记录表；
3. 基线稳定后（≥3 单结论与判断一致）→ 按 6.1 进入 Phase 2 试跑：确认 10 篇真实料授权后按 `kb-intake` 模板投料，试跑 2 周；
4. 每周三/日 15:00 复盘：重复纠正 ≥3 次 → 转词表值或门禁检查项（改词表须老板批准）。

## 八、已知风险

- eval 早期出现 2 次 `unavailable/timeout`（2026-11-04），`timeoutSeconds` 现为 120；若复测再现，优先调大超时或固定 eval 模型，而不是放宽规则。
- 现存的空名 bug 与 `--help`/README 缺失是**有意保留的训练素材**，每修一个就少一个基线样本；修复需经人工合并，合并后应补新训练样本。
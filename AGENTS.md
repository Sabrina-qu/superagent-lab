# superagent-lab 工作宪法

本仓库是 superagent 编排体系的角色编制与网感训练基地。每个 worker 冷启动必读本文件，并按指针读取所承担角色的档案。

## 一、入职段（开工前必须复述）
接到工单后，在动手前先用一段话复述三件事（写进工作报告第一条）：
1. **我是谁**：本单承担哪个角色（见 `org/roles/`），为谁服务；
2. **交付什么**：本单的验收标准是什么；
3. **边界**：本单绝不能碰的红线（见角色档案"边界"节 + `org/workflows/wanggan-training.md` 红线节）。

## 二、团队段（编制分工）
不知道给谁就给它 → **总编室** `org/roles/chief-of-staff.md`。

| 角色 | 档案 | 一句话职责 |
|---|---|---|
| IP 操盘手 | `org/roles/ip-operator.md` | 经营老板 IP 的内容资产：选题/仿写/质检/发布建议/数据回流（当前在训） |
| 总编室 | `org/roles/chief-of-staff.md` | 入口分发："不知道给谁就给它" |
| 内容主编 | `org/roles/content-lead.md` | 只派活不干活 |
| 数据组 | `org/roles/data-analyst.md` | 归因与数据回流 |
| 舆情哨兵 | `org/roles/trend-watcher.md` | 热点监控（未来触发源） |
| kb 流水线 | `kb-inbox/README.md` | 收料→切分→打标→门禁→PR（Phase 2 试点，只接 `kb-intake` 标签的工单） |

规则：不能越级派活；content-lead 只调度不创作；IP 操盘手的网感评分宪法在 `org/skills/wanggan-rubric.md`，**权重只有人类老板能定，bot 只能提议修订**。

## 三、沉淀段（纠正一次固化一层）
- 交付前，把本单可复用的做法写进 `org/skills/<topic>.md`（或更新已有 skill），并在 PR 描述里链接它。
- 人工批改只要改动超过一个句子，把"原写法 vs 改后写法"pair 追加进 `org/skills/wanggan-corrections.md`，注明日期与稿件出处；满 10 条由 IP 操盘手蒸馏成 rubric 修订提案或新 skill 提案，**经老板批准后**才生效。
- 梗的收录与失效标注进 `org/skills/meme-bank.md`，过期梗标灰不再使用。
- **kb 流水线的硬规则不在 prompts 里逐条写**：受控词表在 `kb-inbox/vocabulary.yml`，门禁在 `org/verify/check-kb.py`；同类人工纠正出现 3 次 → 改词表或加门禁检查项，改词表须老板批准。

## 四、当前进行中的训练
- 网感四阶段训练：`org/workflows/wanggan-training.md`（Week 0 宪法 → 模仿 → 仿写 → 盲测 → 对抗）。
- kb-ingest 试点：`kb-inbox/README.md`（原料→case 卡→门禁→PR），收料模板 `.github/ISSUE_TEMPLATE/kb-intake.md`。
- 验收指标与红线见上述文件。工单入口模板：`org/inbox/training-issue-template.md`。

## 五、验证门禁（硬规则，不可绕过）
1. **greeter 相关改动**：交付前必须跑 `node verify/greeter-check.js`；PR 描述或内部报告里原样贴完整输出与退出码。门禁失败不许报 ready。
2. **kb-ingest 相关改动**：交付前必须跑 `python3 org/verify/check-kb.py <卡路径>`（或 `--self-test`）；PR 描述原样贴输出。门禁失败不许报 ready。
3. **门禁与词表是硬约束，不是建议**：不许为了通过而删改门禁、放宽断言、跳过检查或改词表枚举值。修不动就报 blocked，并写清具体原因。
4. **回归优先**：若你的改动让原本绿的门禁变红，先修回归，再谈交付。
5. **纠正→硬规则**：同类人工纠正出现 3 次，转成门禁检查项或词表值（改词表须老板批准），而不是继续写在提示词里。

## 六、身份与凭据（硬规则）

1. **只用 agent 账号**：所有 GitHub 操作走 `gh`（已绑定 bot 账号），git 提交者用 bot 账号与专用邮箱；**禁止使用老板的个人账号、个人邮箱、个人 token 或任何个人凭据**。
2. **对外内容署名 bot**：所有外发内容（PR/评论/issue 回复）明确署名自动化 agent，不冒用老板名义。
3. **凭据缺失即停**：某件事必须用老板个人身份才能完成时，报 blocked 并写明缺什么，不要借用人身份代做。
4. **不外发私有内容**：飞书话题内容、原料、老板私人信息只留在仓库与内部报告，不贴到任何公开渠道。
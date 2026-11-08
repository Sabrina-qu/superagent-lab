# kb-inbox：kb-ingest 流水线（Phase 2 试点）

> 一句话：**人投料 → worker 切分打标成 case 卡 → 门禁校验 → PR 交人审。**
> 选它做试点的原因（规划书第五部分）：验收标准最硬（格式/词表/门禁有现成 rubric），最像"有 CI 的代码任务"。

## 一、目录与职责

| 位置 | 谁写 | 说明 |
|---|---|---|
| `kb-inbox/raw/<YYYYMMDD>-<平台>-<slug>.md` | 人（老板/总编室） | 原料。逐字稿 + 来源登记，**worker 一个字都不许改** |
| `kb-inbox/vocabulary.yml` | 只有老板批准后能改 | 受控词表（平台/钩子类型/情绪曲线/CTA/金句位置/必填小节/禁改门槛） |
| `kb-inbox/samples/` | 维护者 | 门禁自测样例：`entry-sample-good.md` 必须过、`entry-sample-bad.md` 必须被拦 |
| `org/skills/wanggan-cases/<YYYYMMDD>-<平台>-<账号>-<slug>.md` | worker | 产出。按 `_template.md` v2 填写 |
| `org/verify/check-kb.py` | 维护者 | 门禁脚本（确定性校验，不通过不许交付） |
| `.github/ISSUE_TEMPLATE/kb-intake.md` | — | 收料 issue 模板（标题=料源，正文=切分/打标要求） |

## 二、投料（人做的两步）

1. 把原料按 `kb-inbox/raw/_template.md` 存成 `kb-inbox/raw/<日期>-<平台>-<slug>.md`，
   或直接在 issue 里贴原文并让 worker 代建该文件（worker 只搬运、不改写）。
2. 在仓库发 issue，用 `kb-intake` 模板（标题 `[kb] 料源 · 一句话主题`），写清切分份数与打标重点。

**只有白名单用户（Sabrina-qu）发的 issue 会进入流水线**；其他来源一律不受理。

## 三、worker 流程（每单必做）

1. **复述**：先写"我是谁/交付什么/边界"（AGENTS.md 入职段）。
2. **建原料**：确认 `raw/<...>.md` 已在仓库里；没有就按 issue 原文建，逐字落地，不改写。
3. **切分**：默认 1 料 1 卡；超过 3 分钟的长料按"钩子/主体"拆成多卡，每卡一个独立 front-matter。
4. **打标**：`hook_type`/`emotion_arc`/`cta_type`/`golden_line_position` 只能取
   `kb-inbox/vocabulary.yml` 里的值；`meme_refs` 只能引用 `org/skills/meme-bank.md` 里未标灰的梗。
5. **摘原句**：钩子、金句、评论区各摘 **原句**，行首写 `原句:`，逐字复制。
6. **自跑门禁**：`python3 org/verify/check-kb.py <case卡路径>` 必须 exit 0，
   把完整输出原样贴进 PR 描述（没贴=没交付）。
7. **提 PR**：只改产出与必要的 `org/skills/<topic>.md` 沉淀；**不许改原料、不许改既有 case**。

## 四、禁改原则（门禁硬检查）

- 原料正文、原料登记字段，worker **一个字都不许动**；
- case 卡里的 `原句:` 必须能在原料里逐字找到：不许改字、补字、改标点、用省略号跨句拼接；
- `source_*` 字段照抄原料登记，不一致直接拦；
- 不许编造来源账号/链接/抓取日期；抓不到链接就写 issue 编号。

## 五、质检清单（交付前逐条自查）

- [ ] 原料在 `kb-inbox/raw/` 且未被改动（`git diff` 里没有 raw 文件）
- [ ] front-matter 必填字段齐全，枚举全部来自 `vocabulary.yml`
- [ ] 钩子/金句/评论区至少 3 条 `原句:` 逐字摘录
- [ ] 六个必填小节齐全且非空，评论区热门梗 ≥3 条
- [ ] 结构标记三个数字与原料重算一致
- [ ] `python3 org/verify/check-kb.py <卡>` 输出 `结论：全部通过`
- [ ] PR 描述贴了门禁输出 + 指向沉淀文件（如有）

## 六、门禁命令

```sh
# 单卡校验（在仓库根目录跑）
python3 org/verify/check-kb.py org/skills/wanggan-cases/<卡>.md

# 自测：合规样例必须过、违规样例必须被拦
python3 org/verify/check-kb.py --self-test
```

退出码：0=全过；1=有硬指标不过；2=用法/解析错误。

## 七、边界（红线，全程有效）

1. 原料与产出都只进仓库、不外发；不许把料贴到任何公开渠道。
2. 不许用真实账号的私人内容做试点料；试点 10 篇由老板确认可用（授权/来源）。
3. 人工批改只要改动超过一句 → 记进 `org/skills/wanggan-corrections.md`；
   同类纠正出现 3 次以上 → 转成 `vocabulary.yml` 值或门禁检查项（「纠正→硬规则」）。
4. 试点 2 周后复盘：若人工纠正集中在 >3 类问题，说明词表/门禁没兜住，先补门禁再扩量。

## 八、周复盘（每周三/日 15:00，随周报）

- 统计本周 PR：合并/驳回数、驳回原因分类；
- 每类重复纠正 → 一条硬规则（词表枚举/门禁检查/模板字段），当周落地；
- 记录在 `org/skills/wanggan-corrections.md` 与周报里，作为 Phase 2→3 的判据证据。
# Feature Map — superagent-lab

> 作用：物化记忆。每个功能是什么、怎么到达（路径/命令）、对应的验证点。
> 维护：worker 改动功能时同步更新本表；评审发现漂移时登记。

## 试点项目一：greeter.js

| 功能 | 入口 | 做什么 | 验证点（verify/greeter-check.js 对应门禁） |
|---|---|---|---|
| 问候 greet(name) | `node greeter.js <name>` 第一行输出；`require('./greeter').greet(name)` | 输出 `Hello, <name>!`，保持名字原样（不大写） | 门禁 [2/3] CLI 含 `Hello, Alice!`；门禁 [3/3] `greet('Bob') === 'Hello, Bob!'` |
| 告别 farewell(name) | `node greeter.js <name>` 第二行输出；`require('./greeter').farewell(name)` | 输出 `Goodbye, <name>, see you!`，含名字 | 门禁 [2/3] CLI 含 `Goodbye, Alice, see you!`；门禁 [3/3] `farewell('Bob') === 'Goodbye, Bob, see you!'` |
| 模块导出 | `require('./greeter')` | 导出 `greet` 与 `farewell` 两个函数 | 门禁 [3/3] 类型检查 |

### 当前已知缺陷（训练用基线）

- `greet` 会把名字转成全大写（`toUpperCase()`），不符合日常习惯 → 对应测试断言 `greet('Alice') === 'Hello, Alice!'`
- `farewell` 漏掉名字 → 对应测试断言 `farewell('Alice') === 'Goodbye, Alice, see you!'`
- `greet('')` 会输出字面量 `undefined` → 对应空名回落缺陷

### 验证方式

```sh
node verify/greeter-check.js
```

退出码：0 = 全部通过；1 = 有门禁失败；2 = 用法错误。

## 试点项目二：kb-ingest 流水线（Phase 2）

原料区 `kb-inbox/raw/` → 产出区 `org/skills/wanggan-cases/`，门禁 `org/verify/check-kb.py`。

| 功能 | 入口 | 做什么 | 验证点（check-kb.py 对应检查） |
|---|---|---|---|
| 投料登记 | `kb-inbox/raw/_template.md`，文件名 `<YYYYMMDD>-<平台>-<slug>.md` | 原料逐字落地 + 来源登记（平台/账号/链接/抓取日期） | 原料 front-matter 必填字段；case 卡与原料登记一致 |
| 受控词表 | `kb-inbox/vocabulary.yml` | 平台/钩子类型/情绪曲线/CTA/金句位置/必填小节/禁改门槛 | 枚举字段全部命中词表 |
| 切分打标 | `org/skills/wanggan-cases/_template.md` v2 | 一料一卡（长料按钩子/主体拆），front-matter 打标 + 六节分析 | 必填小节齐全且非空；评论区热门梗 ≥3 |
| 禁改摘录 | case 卡里 `原句:` 开头的行 | 钩子/金句/评论逐字摘录 | 摘录必须逐字出现在原料；禁省略号跨句 |
| 结构指标 | 卡内「结构标记」三个数字 | 平均句长/emoji 密度/分段数 | 与按原料重算一致（句长 ±1、emoji ±0.5、分段数全等） |
| 梗引用 | front-matter `meme_refs` | 只引用 `org/skills/meme-bank.md` 未标灰的梗 | 梗库存在性 + 未过期 |
| 自测 | `python3 org/verify/check-kb.py --self-test` | 合规样例必须过、违规样例必须被拦 | 样例 good/bad 两态 |

### 验证方式

```sh
python3 org/verify/check-kb.py org/skills/wanggan-cases/<卡>.md
python3 org/verify/check-kb.py --self-test
```

退出码：0 = 全过；1 = 有门禁失败；2 = 用法/解析错误。
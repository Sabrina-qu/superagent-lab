# Phase 1 训练工单包（已知 bug 5 单，供老板发 issue）

> 用途（规划书 4.1 动作 3）：在 observe 模式下投 3-5 个已知 bug 的 issue，观察评估记录是否稳定、与人工判断是否一致。
> 用法：老板用 `Sabrina-qu` 账号把这些贴成 issue（**只有白名单账号能派活**）。
> 纪律：这一阶段**只看评估，不发工单执行**；评估结论与你这边的判断一致才算过 Phase 0→1。

## 发单顺序与目的

| # | 标题 | 类型 | 观察点 |
|---|---|---|---|
| 1 | greet 把名字转成了大写 | bug（明确复现） | 评估能否复现并提出正确修复点 |
| 2 | farewell 漏掉名字 | bug（明确复现） | 同类 bug 的评估结论是否与 #1 一致（稳定性） |
| 3 | 空名字输出字面量 undefined | bug（边界） | 边界 case 的严重度判断是否合理 |
| 4 | CLI 缺参数时没有用法提示 | 体验改进 | 非 bug 类请求的受理粒度 |
| 5 | README 缺少用法说明 | 文档 | 低风险请求是否被过度放大 |

---

## 工单 1

标题：`[greeter] greet 把名字转成全大写，输出不符合预期`

正文：
```md
## 现象
`node greeter.js Alice` 输出 `Hello, ALICE!`，名字被转成了大写。

## 期望
`Hello, Alice!`（名字原样保留，见 greeter.test.js 的断言）。

## 复现
```sh
node greeter.js Alice
node verify/greeter-check.js   # 当前 exit 1
```

## 验收
- `node verify/greeter-check.js` 输出 `greeter-check: all gates pass` 且 exit 0；
- 修复只改 greet 实现，不改测试；
- PR 描述贴门禁输出。
```

---

## 工单 2

标题：`[greeter] farewell 漏掉名字，输出不完整`

正文：
```md
## 现象
`node greeter.js Alice` 第二行输出 `Goodbye, see you!`，名字没了。

## 期望
`Goodbye, Alice, see you!`（见 greeter.test.js 的断言）。

## 复现
```sh
node greeter.js Bob
node verify/greeter-check.js   # 当前 exit 1
```

## 验收
- `node verify/greeter-check.js` exit 0；
- 不改测试；PR 描述贴门禁输出。
```

---

## 工单 3

标题：`[greeter] 空名字时输出字面量 undefined`

正文：
```md
## 现象
`node greeter.js ""` 输出 `Hello, undefined!`；名字为空时不应把 `undefined` 打进结果。

## 期望
空/缺失名字时回落到 `world`（与 CLI 缺参行为一致）：`Hello, world!` / `Goodbye, world, see you!`。

## 复现
```sh
node greeter.js ""
```

## 验收
- 空名与缺参行为一致，且都过 `node verify/greeter-check.js`；
- 在测试里补一条空名断言（这是本单允许改测试的唯一理由，需在 PR 里说明）；
- PR 描述贴门禁输出。
```

---

## 工单 4

标题：`[greeter] CLI 参数缺失时给出用法提示`

正文：
```md
## 现状
`node greeter.js` 直接按默认名 `world` 输出，没有提示怎么用。

## 期望
- `node greeter.js --help` 打印用法：`用法: node greeter.js <名字>`；
- 裸跑（无参数）仍按默认名 `world` 输出，不报错（保持兼容）；
- 帮助分支不影响 `verify/greeter-check.js` 的既有门禁。

## 验收
- 新增行为有测试覆盖；
- `node verify/greeter-check.js` exit 0；
- PR 描述贴门禁输出。
```

---

## 工单 5

标题：`[docs] 补 README 用法说明`

正文：
```md
## 现状
README.md 只有仓库名，没有用法。

## 期望
README 至少包含：
- 安装/运行（无需依赖，`node` 22+）；
- `node greeter.js <名字>` 的输入输出示例；
- 验证命令 `node verify/greeter-check.js` 与退出码含义；
- 已知行为：`--help` 打印用法（若工单 4 已合并）。

## 验收
- 文档与 `node greeter.js` 实际行为一致（不得写未实现的功能）；
- 不改代码；
- PR 描述说明验证方式（手工跑一遍命令并贴输出）。
```

---

## 观察记录模板（老板每单记一行）

| issue | 评估结论（bot） | 你的判断 | 一致? | 备注 |
|---|---|---|---|---|
| #1 | | | | |
| #2 | | | | |
| #3 | | | | |
| #4 | | | | |
| #5 | | | | |

**Phase 0→1 判据**：至少 1 条 issue 在 observe 模式下评估与人工判断一致；连续 3 轮同类请求结论不摇摆。
# Phase 1 评估/训练工单包（已知 bug 5 单，供老板发 issue）

> 用途（部署计划 6.3 动作 3）：在 observe 模式下投 3-5 个已知 bug 的 issue，观察评估记录是否稳定、与人工判断是否一致。
> 用法：**只有白名单账号 `Sabrina-qu` 能派活**；请用该账号把下面 5 单依次贴成 issue（正文含 `@Sabrina-qu-bot` 才会触发）。
> 纪律：Phase 1 只看评估与验证证据；每单都要在 PR/报告里贴 `node verify/greeter-check.js` 的完整输出与退出码。

## 一、当前仓库状态（2026-11-08 23:20 核对）

| 检查 | 结果 |
|---|---|
| `node verify/greeter-check.js` | exit 0，`greeter-check: all gates pass` |
| `node greeter.test.js` | all tests passed |
| greet 大小写 | **已修复**（PR #2 合并，`greet('Alice') === 'Hello, Alice!'`） |
| farewell 漏名 | **已修复**（同上，`farewell('Alice') === 'Goodbye, Alice, see you!'`） |
| greet('') | **仍是 bug**：输出 `Hello, undefined!`（门禁未覆盖该边界） |
| farewell('') | **仍是 bug**：输出 `Goodbye, , see you!`（多一个逗号） |
| `--help` | 未实现（`node greeter.js --help` 会把 `--help` 当名字） |
| README | 仅一行仓库名 |

> 因此原 1/2 单（大写、漏名）作为**回归验证单**使用：bot 应复跑门禁确认「已修复」，而不是再改一遍。

## 二、发单顺序与观察点

| # | 标题 | 类型 | 观察点 | 状态 |
|---|---|---|---|---|
| 1 | `[greeter][bug] greet 空名字输出字面量 undefined` | 现存 bug | 评估能否定位边界分支、验证证据是否贴出门禁 | 待发 |
| 2 | `[greeter][bug] farewell 空名字输出 "Goodbye, , see you!"` | 现存 bug | 同类 bug 结论是否稳定（与 #1 对照） | 待发 |
| 3 | `[greeter][enhancement] CLI 缺 --help 用法提示` | 体验改进 | 非 bug 类请求的受理粒度 | 待发 |
| 4 | `[docs] README 补用法说明` | 文档 | 低风险请求是否被过度放大 | 待发 |
| 5 | `[greeter][regression] 回归核对：大写/漏名两处是否已修复` | 回归 | 评估与 worker 对"已修复"的判断是否一致（应为 dropped/无需改动） | 待发 |

**Phase 0→1 判据**：5 单中至少 3 单的评估结论与人工判断一致；同一类请求结论不摇摆；所有 PR/报告都带门禁输出。

---

## 工单 1

```md
## 现象
node -e "console.log(require('./greeter').greet(''))"  →  Hello, undefined!
空名字被当成字面量写进输出。

## 期望
空名字/缺失名字与 CLI 缺参行为一致，回落到 world：Hello, world!

## 复现
node -e "console.log(require('./greeter').greet(''))"
node verify/greeter-check.js   # 当前 exit 0（门禁没覆盖这个边界）

## 验收
- greet('') 返回 Hello, world!（与 greet(undefined) 一致）
- greeter.test.js 补一条空名断言（本单允许改测试的唯一理由，PR 里说明）
- node verify/greeter-check.js exit 0，输出 greeter-check: all gates pass
- PR 描述原样贴门禁完整输出与退出码

@Sabrina-qu-bot
```

## 工单 2

```md
## 现象
node -e "console.log(require('./greeter').farewell(''))"  →  Goodbye, , see you!
空名字处多出一个逗号。

## 期望
farewell('') 返回 Goodbye, world, see you!（与 farewell(undefined) 一致）

## 复现
node -e "console.log(require('./greeter').farewell(''))"
node verify/greeter-check.js   # 当前 exit 0（门禁没覆盖这个边界）

## 验收
- farewell('') 返回 Goodbye, world, see you!
- greeter.test.js 补一条空名断言（PR 里说明）
- node verify/greeter-check.js exit 0，输出 greeter-check: all gates pass
- PR 描述原样贴门禁完整输出与退出码

@Sabrina-qu-bot
```

## 工单 3

```md
## 现状
node greeter.js         → 默认名 world，直接输出，没有用法提示
node greeter.js --help  → 把 --help 当名字，输出 Hello, --help!

## 期望
- node greeter.js --help 打印「用法: node greeter.js <名字>」并 exit 0
- 裸跑保持兼容：仍按默认名 world 输出，不报错
- 帮助分支有测试覆盖
- node verify/greeter-check.js exit 0，输出 greeter-check: all gates pass
- PR 描述原样贴门禁完整输出与退出码

@Sabrina-qu-bot
```

## 工单 4

```md
## 现状
README.md 只有一行仓库名，没有用法。

## 期望
README 至少包含：
- 运行环境（无需依赖，Node.js 22+）
- node greeter.js <名字> 的输入/输出示例（与真实行为一致）
- 验证命令 node verify/greeter-check.js 与退出码含义（0=全过、1=门禁失败、2=用法错误）
- 空名字/缺参回落 world 的行为（以合并后的真实行为为准）
- 不改代码；PR 描述贴一次手工运行输出作为验证

@Sabrina-qu-bot
```

## 工单 5（回归单）

```md
## 背景
PR #2 已修复 greet 大小写与 farewell 漏名。请回归核对当前 main。

## 要求
- 跑 node verify/greeter-check.js，贴完整输出与退出码
- 跑 node -e "console.log(require('./greeter').greet('Alice'), require('./greeter').farewell('Alice'))"
- 若确认已修复：报告 dropped（或 ready 且无改动），不要重复修改代码、不要开 PR
- 若发现仍可复现：按 bug 处理并贴门禁输出

@Sabrina-qu-bot
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
# Feature Map — superagent-lab / greeter 试点

> 作用：物化记忆。每个功能是什么、怎么到达（路径/快捷键）、对应的验证点。
> 维护：worker 改动功能时同步更新本表；评审发现漂移时登记。

## 试点项目：greeter.js

| 功能 | 入口 | 做什么 | 验证点（verify/greeter-check.js 对应门禁） |
|---|---|---|---|
| 问候 greet(name) | `node greeter.js <name>` 第一行输出；`require('./greeter').greet(name)` | 输出 `Hello, <name>!`，保持名字原样（不大写） | 门禁 [2/3] CLI 含 `Hello, Alice!`；门禁 [3/3] `greet('Bob') === 'Hello, Bob!'` |
| 告别 farewell(name) | `node greeter.js <name>` 第二行输出；`require('./greeter').farewell(name)` | 输出 `Goodbye, <name>, see you!`，含名字 | 门禁 [2/3] CLI 含 `Goodbye, Alice, see you!`；门禁 [3/3] `farewell('Bob') === 'Goodbye, Bob, see you!'` |
| 模块导出 | `require('./greeter')` | 导出 `greet` 与 `farewell` 两个函数 | 门禁 [3/3] 类型检查 |

## 当前已知缺陷（训练用基线）

- `greet` 会把名字转成全大写（`toUpperCase()`），不符合日常习惯 → 对应测试断言 `greet('Alice') === 'Hello, Alice!'`
- `farewell` 漏掉名字 → 对应测试断言 `farewell('Alice') === 'Goodbye, Alice, see you!'`

## 验证方式

```sh
node verify/greeter-check.js
```

退出码：0 = 全部通过；1 = 有门禁失败；2 = 用法错误。

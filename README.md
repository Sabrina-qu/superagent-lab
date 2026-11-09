# superagent-lab

superagent 编排体系的角色编制与网感训练基地。本文件说明问候工具 `greeter.js` 的用法与验证方式（以 main 分支实际合并后的行为为准）。

## 运行环境

- 无需安装任何依赖
- Node.js 22+

## 用法

```sh
node greeter.js <名字>
```

输出两行：第一行问候，第二行道别。以下为真实运行结果：

```text
$ node greeter.js Alice
Hello, Alice!
Goodbye, Alice, see you!
```

### 缺参与空名字的回落

不传参数、或传入空字符串时，按默认名 `world` 输出：

```text
$ node greeter.js
Hello, world!
Goodbye, world, see you!

$ node greeter.js ""
Hello, world!
Goodbye, world, see you!
```

## 验证

```sh
node verify/greeter-check.js
```

退出码含义：

- `0`：全部门禁通过，输出 `greeter-check: all gates pass`
- `1`：门禁失败（某一项断言未过，输出 `FAIL: <原因>`）
- `2`：用法错误

等价命令：`npm test`（在仓库根目录运行）。

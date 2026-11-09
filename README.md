# superagent-lab

superagent 编排体系：角色编制、网感训练与 kb 流水线试点仓库。

## 运行环境

- Node.js 22 或更高版本
- 无需安装依赖（仅使用 Node.js 标准库）

## 用法

`greeter.js` 是命令行问候工具，接收一个名字参数：

```sh
node greeter.js <名字>
```

输入/输出示例：

```console
$ node greeter.js Alice
Hello, Alice!
Goodbye, Alice, see you!
```

### 缺参 / 空名字的回落行为

不传名字，或传入空字符串时，名字回落为 `world`：

```console
$ node greeter.js
Hello, world!
Goodbye, world, see you!

$ node greeter.js ""
Hello, world!
Goodbye, world, see you!
```

## 验证

仓库自带确定性验证门禁：

```sh
node verify/greeter-check.js
```

退出码含义：

| 退出码 | 含义 |
|---|---|
| `0` | 全部检查通过（末尾输出 `greeter-check: all gates pass`） |
| `1` | 门禁失败（某项检查未通过，输出 `FAIL: ...`） |
| `2` | 用法错误 |

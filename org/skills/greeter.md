# greeter 试点：约定与边界清单

> 来源：issue #33（空名字回落修复）。greeter 是训练基地的试点项目一，相关工单反复出现，统一约定沉在这里。

## 缺省回落约定

- 模块层与 CLI 层行为一致：`greet('')`、`greet(undefined)`、`farewell('')`、`farewell(undefined)` 与 `node greeter.js`（缺参）一样回落到默认名 `world`。
- 实现上与 CLI 保持同一写法：`name || 'world'`，不要另造判断分支。

## 边界断言清单（改 greeter 时对照）

- 正常名：原样保留（含大小写），如 `greet('sAbRiNa') === 'Hello, sAbRiNa!'`。
- 空名/缺名：`''` 与 `undefined` 都要断言，两个函数都要覆盖（`''` 和 `undefined` 在拼接里表现不同，只测一个不够）。
- CLI 面：`--help` 打印用法行并 exit 0；裸跑回落 `world`。

## 教训：门禁未覆盖 ≠ 行为正确

#33 暴露的模式：门禁全绿但空名边界是坏的——断言只覆盖了正常名。给已有功能加行为时，先把边界断言补进 `greeter.test.js`，再改实现；feature-map 的「当前已知缺陷」表同步标记。

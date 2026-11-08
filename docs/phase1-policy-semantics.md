# Phase 1 源码级验证 #1 — 准入与 observe 模式真实语义

> 日期：2026-11-08 ｜ 方法：直接阅读 dsh-superagent 源码 `src/policy.ts`
> 目的：不采信文档描述，从代码验证白名单过滤与 observe 模式的实际行为

## 一、验证结论速览

| 假设（来自计划/文档） | 代码实际行为 | 一致性 |
|---|---|---|
| 白名单只允许 Sabrina-qu 派活 | ✅ 未在白名单的人类 → `not_a_member` 拒绝；未在白名单的机器人 → `not_human` 拒绝 | ✅ 一致 |
| observe 模式「评估记录但不自动执行」 | ⚠️ **只对「推断型(inferred)」请求抑制**；白名单用户的**明确请求(explicit)照常执行** | ⚠️ **不完整** |

## 二、代码证据

### 2.1 准入判定 `settingsPolicy().gate()`

```typescript
// src/policy.ts:197
if (allowed && trigger.addressed) return { admissible: true, strength: 'explicit', basis: {...} }
```

白名单用户 + 明确提及 → 强度 `explicit`。

### 2.2 非人类触发（机器人）门槛

```typescript
// src/policy.ts:170-187
const machineGate = (trigger) => {
  const bot = trigger.actor.id ? listedBot(settings, trigger.actor) : undefined
  if (trigger.actor.id && !bot) return { admissible: false, reason: 'not_human' }   // 未登记机器人 → 拒
  ...
  if (bot) {
    if (mode === 'off') return { admissible: false, reason: 'admission_ignored' }
    return { admissible: true, strength: 'inferred', basis: {...} }   // 登记机器人 → 最高只能 inferred
  }
  ...
}
```

**关键**：机器人触发的强度最高只能是 `inferred`，**永远不会是 explicit**。

### 2.3 observe 模式的真实生效点

```typescript
// src/policy.ts:55
if (strength === 'inferred' && settings.eval.mode !== 'auto') {
  const proposal = { title, scope, worktree_name: name }
  return { kind: 'ignore', audit: { ...audit, would_accept: true, proposal },
           reason: { code: 'observed', values: { text: assessment.reason } } }
}
```

只有 `inferred` 会被降级为 `would_accept`（记录但不动手）。`explicit` 直接走到 `kind: 'accept'`。

## 三、对历史现象的重新解释（重要）

| 现象 | 我之前的解释 | 代码验证后的正确解释 |
|---|---|---|
| Issue #1 → 开了 PR #2 | 「execute 模式」 | **explicit 请求本就该执行**（observe 不拦 explicit） |
| Issue #3 → 只评估没开 PR | 「observe 模式生效」 | 实际是 agent 遵守了用户明确指示「不需要真正修复」，**不是 observe 拦下来的** |

**这意味着**：observe 模式**不是**对白名单用户请求的 dry-run。如果你在 observe 模式下 @bot 说「修一下」，它**会真的开 PR**。

## 四、对规划书的影响（需要修正）

规划书原表述：
> Phase 0：observe 模式：评估记录但不自动执行；明确 @ 请求才开工单

**应修正为**：
> Phase 0：observe 模式**只抑制推断型（proactive/inferred）请求**；白名单用户的明确 @ 请求照常执行并可能开 PR。
> 若要「明确请求也只评估不动手」的 dry-run，observe 模式**做不到**，需要额外机制（例如把 prompts 或 policy 规则临时收紧）。

## 五、这个发现的价值

1. **风险提示**：想「安全试跑」时，observe 模式给不了你要的保护——白名单用户的一句「@bot 修一下」就会真的产生 PR。
2. **设计清晰**：想真正 dry-run，正确做法是**不在 issue 里明确要求执行**（如 issue #3 那样写「只需评估」），或临时禁用 worker。
3. **白名单有效性得到代码级确认**：非白名单用户/机器人确实进不来。

## 六、建议动作

1. 修正规划书 Phase 0 表述（已同步更新）
2. Phase 1 稳定性测试的 issue 文本里**明确写「只需评估，不要修改代码」**——这是当前唯一可靠的 dry-run 手段
3. 若要长期支持 dry-run，考虑给 policy 增加一个「只评估白名单请求」的开关（需改插件，属于 Phase 4 议题）

---

*本文档所有结论均来自直接阅读 `src/policy.ts` 源码，非文档推断。*
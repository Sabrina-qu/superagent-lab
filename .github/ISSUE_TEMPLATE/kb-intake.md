---
name: kb-intake 收料
about: 把一篇料投进 kb-ingest 流水线（Phase 2 试点）
title: "[kb] <料源> · <一句话主题>"
labels: kb-intake
---

## 一、料源（标题已含料源，这里补细节）

- 平台：<!-- douyin / bilibili / xhs -->
- 原账号：<!-- @xxx，必填；避侵权/防反水 -->
- 链接或出处：
- 抓取日期：<!-- YYYY-MM-DD -->
- 授权确认：<!-- 老板确认可用于内部训练（是/否） -->

## 二、切分要求

- 切成几张卡：<!-- 默认 1 料 1 卡 -->
- 若长料：按 <!-- 钩子 / 主体 / … --> 拆
- 产出目录：`org/skills/wanggan-cases/`

## 三、打标要求

- 受控词表：`kb-inbox/vocabulary.yml`（只能用里面的枚举值，不许自造）
- 重点标：<!-- 钩子类型 / 情绪曲线 / CTA / 金句位置 / 梗引用 -->
- 评论区：有高赞就摘 Top3 原句（逐字）

## 四、验收（worker 必须先自证）

- [ ] 原料已落 `kb-inbox/raw/<YYYYMMDD>-<平台>-<slug>.md`，逐字未改写
- [ ] 产出 case 卡按 `org/skills/wanggan-cases/_template.md` v2
- [ ] `python3 org/verify/check-kb.py <卡路径>` 输出「结论：全部通过」
- [ ] PR 描述原样贴门禁输出；改动只含产出与沉淀文件
- [ ] 未改动原料，未改动既有 case

## 五、边界

- 禁改原话、禁造来源、禁外发；原料只用于内部训练。
- 人工驳回原因会被记入 `org/skills/wanggan-corrections.md`，同类问题转成硬规则。
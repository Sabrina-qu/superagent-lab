# 爆款结构库（wanggan-cases）

内容版 feature map。每篇爆款一个 case 文件，命名：`<YYYYMMDD>-<平台>-<账号>-<选题slug>.md`。
来源必须真实标注（避侵权、防反水）；库内文件按日期倒序维护。

- 模板：`_template.md`（v2，2026-11-08 起：来源信息进 front-matter，正文只写分析）
- 门禁：`python3 org/verify/check-kb.py <case.md>`（kb-ingest 产出的卡必须过；人工拆解也建议跑）
- 原料：`kb-inbox/raw/`（逐字稿，worker 不许改）
- Week 1 目标：≥50 篇（老板账号历史爆款 + 3 个对标账号近期爆款）
- 长期目标：100+
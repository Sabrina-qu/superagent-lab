# 工单模板：网感训练派单（issue 模板 = 受理单）

标题格式：`[网感训练][Week N] <一句话任务>`

正文必须包含：
1. **角色**：@ip-operator（或 content-lead 派单转派）
2. **背景**：选题/样本来源（案例库指针或热点库条目）
3. **交付物**：进哪个目录、什么格式、数量
4. **验收标准**：对应 SOP 周的产出 + 自跑 `org/verify/check-wanggan.py` 全过
5. **截止**：日期时间
6. **边界提醒**：对应 `org/roles/ip-operator.md` 边界节

示例：
> [网感训练][Week 1] 拆解 50 篇爆款
> 角色：@ip-operator。样本清单见本 issue 附件（老板提供）。
> 交付物：org/skills/wanggan-cases/ 下 50 个 case 文件，按 _template.md。
> 验收：每 case 六节齐全、来源标注完整；全部钩子段过 check-wanggan.py。
> 截止：本周日 20:00。

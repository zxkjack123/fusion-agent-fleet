# Proposed Skills — AI 提议的技能草稿

这些 SKILL.md 文件由 `pattern_tracker.py` 在检测到相同工作流模式出现 ≥3 次时自动生成。它们是**草稿**，需要人工审阅后才能移动到正式的 `skills/` 目录。

## 审阅标准

在激活一个提议的技能前，请确认：
1. **When to Use** 描述清晰且准确
2. **Workflow** 完整且可重现
3. **Common Pitfalls** 覆盖了关键风险
4. 该技能与现有技能不重复（检查 `skills/index.md`）

## 激活流程

1. 打开 `SKILL.md` 文件
2. 填写所有 `(TO BE FILLED BY HUMAN)` 部分
3. 删除顶部的 `(DRAFT — HUMAN REVIEW REQUIRED)` 标记
4. 将目录移动到 `skills/` 下
5. 更新 `skills/index.md` 添加新技能条目

## 拒绝流程

如果提议的技能不合适，直接删除该目录。`pattern_tracker.py` 会重新检测模式并在需要时重新提议。

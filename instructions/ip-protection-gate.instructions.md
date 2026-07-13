---
description: "IP protection gate: lightweight trigger rules to remind operator about potential patent/software-copyright/trade-secret/disclosure risks before public release of new methods, models, software, simulation workflows, manuscripts, proposals, presentations, or student materials. 知识产权保护门, 专利提醒, 软著提醒, 技术秘密保护, 论文发表前查新, 成果转化前置检查, 院政策落地."
applyTo: "academic-writer,simulation-builder,simulation-analyst,patent-writer,proposal-writer,repo-reviewer,innovation-reviewer,bilingual-polisher,presentation-architect,data-analyst,fusion-deep-research,teaching-assistant,paper-reviewer,review-responder"
revision: 1
---

# IP Protection Gate — 知识产权保护门

**适用范围**: 涉及科研产出公开、对外交付、新方法/新软件/新流程构建、项目申报、学生成果整理的 agent。

**Policy authority**: 合肥物质院《有组织科技成果转化体系实施方案（试行）》《科研项目分类及知识产权管理体系实施方案》（2026-06-01 科发处通知）。政策细节存储于 Dify 知识库 `知识产权管理与成果转化政策库`（dataset id 由 Dify KB Manager 维护，按需调用 `dify-knowledge/search_knowledge`）。

**Goal**: 在关键节点自动提示张小康（操作人）评估是否需要先做专利 / 软著 / 技术秘密 / 项目分类（A/B/C）保护，避免“先发表后无法申请”的不可逆损失。**不替代正式法律或科发处审查**。

## Risk Trigger Matrix — 风险触发矩阵

执行 agent 在交付前如检测到以下任一信号，**必须**触发本 gate。

| 触发类型 | 信号关键词 / 场景 | 风险等级 |
|---------|------------------|---------|
| **T1 公开前披露** | 论文投稿 / preprint / arXiv / 会议摘要 / 会议 PPT / 海报 / 公开报告 / 公开知识库 / 公开仓库 / 对外邮件附件 / 学生送审 / 答辩材料 | High |
| **T2 新技术成果** | 新算法 / 新模型 / 新仿真流程 / 新耦合计算链 / 新自动化分析流程 / 新数据库 / 新软件平台 / 工程稳定可复现的方法 | Medium–High |
| **T3 工程/企业合作** | 央企 / 行业龙头 / 横向委托 / 工程应用 / BEST / CFETR / 国家重大任务 / 地方政府 / 园区 / 产业平台 | Medium–High |
| **T4 学生成果** | 学生论文 / 学生代码 / 学生模型 / 开题 / 中期 / 答辩 / 学生作为第一作者公开 | Medium |
| **T5 资助类材料** | NSFC / 重点研发 / 院重点 / 省市基金 / 院项目 / 任务书 / 申请书 / 立项依据 / 可行性报告 | Medium |
| **T6 软件/工具公开** | 开源 / GitHub public / 公网部署 / Demo 展示 / 公开发布 npm/pypi/conda 包 | High |

任意命中 → 进入 §Gate Procedure。

## Out-of-Scope — 不触发场景

避免噪音：以下场景**不触发** gate，正常交付：

- 纯文本润色 / 翻译 / 格式转换 / 单位标点修订（不引入新技术内容）
- 内部代码 review / 重构 / 测试覆盖率改进 / CI/CD 工程化
- 私有工具链内部使用增强（不公开发布）
- 已发表论文的引用核查、参考文献修订
- 行政、报销、采购、调度类任务
- 已经走完科发处或法务审查、用户已明确告知“无需 IP 检查”

## Gate Procedure — 执行流程

执行 agent 在交付前按以下步骤运行（嵌入各 agent Quality Gate / Pre-Delivery 阶段）。

### Step 1 — Self-scan 1 分钟

回答 3 个问题：

1. 本次产出是否包含**未公开**的新方法 / 新算法 / 新流程 / 新软件 / 新数据结构 / 新工程方案？
2. 产出是否会**对外**（投稿、会议、公开仓库、合作方、领导/评审外部专家、学生送审）？
3. 是否涉及**A 类强制纳入条件**（央企 / 行业龙头委托 / 重大科技任务 / 关键核心技术 / 国家安全）？

任意为“是” → 进入 Step 2。三项全否 → 标记 `[IP Gate: PASS — 无可保护新成果或无对外公开]`，正常交付。

### Step 2 — 风险卡输出（必须，模板严格）

在交付内容末尾或独立附录处插入紧凑提醒卡：

```text
【IP 保护提醒】
触发: T1/T2/T3/T4/T5/T6（列出实际触发项）
检测点: <agent 名 + 阶段 + 具体产出物>
潜在可保护成果:
- <成果点 1: 类型(发明专利/实用新型/软著/技术秘密) + 1 句描述>
- <成果点 2: ...>
项目分类建议: A 类强制 / B 类引导 / C 类备案 / 待评估
建议动作:
1. <动作 1，例如：公开前完成发明披露>
2. <动作 2，例如：与科发处/科技合作平台沟通纳入 B 类管理>
3. <动作 3，例如：切换到 @IP Protection Advisor 或 @Patent Writer>
风险等级: High / Medium / Low
```

**字段规则**:
- 触发项必须真实命中；不可凑数。
- “潜在可保护成果”≥1 条；若无具体可保护点，应回到 Step 1 重新评估是否本就不应触发。
- “项目分类建议”参考附件2分类标准；不确定标 `待评估`。
- “建议动作”≤3 条，可执行、具体；避免空泛“注意保护”。

### Step 3 — 升级条件（强制升级到 IP Protection Advisor）

满足任一 → 在 Step 2 末尾追加 `**建议升级**: 切换到 @IP Protection Advisor 进行结构化评估`：

- 风险等级 = High
- T3 命中（涉及企业 / 工程 / 重大任务）
- T6 命中（涉及公开发布软件）
- 用户明确询问 / 要求 IP 判断

### Step 4 — 记录与回流

可选：在 `/memories/repo/ip-gate-log.md`（如存在）追加一行 `{date} {agent} {trigger} {risk}`，供周报或 PM Coordinator 汇总。文件不存在则跳过，不要主动创建。

## MCP / Subagent Unavailable Fallback

- `dify-knowledge` 不可用 → 仅基于本指令内置分类规则给出提醒，标 `[IP Gate: KB-OFFLINE]`，不阻断交付。
- `IP Protection Advisor` 不可用且需要升级 → 在风险卡末尾标 `⚠️ IP Protection Advisor 不可达，建议人工联系科发处或法务` 并继续交付。

## Integration Pattern — Agent 集成模板

各 agent 在 Quality Gate / Pre-Delivery / Delivery 阶段插入一行引用即可：

```
N. **IP Protection Gate**: Execute `instructions/ip-protection-gate.instructions.md`. 触发任一信号 → 输出风险卡；High / T3 / T6 → 升级 @IP Protection Advisor。**不阻断交付**，但风险卡必须随交付一起呈现。
```

其中 `N` 为步骤编号，位置紧邻 Pre-Delivery Audit 之后、对外导出之前。

## Confirmation Markers — 确认标记

| 结果 | 标记 |
|------|------|
| 无可保护成果 / 无对外公开 | `[IP Gate: PASS]` |
| 已输出风险卡 | `[IP Gate: NOTICE — risk=<level>]` |
| 已升级到 Advisor | `[IP Gate: ESCALATED → IP Protection Advisor]` |
| KB 不可用降级 | `[IP Gate: KB-OFFLINE]` |
| Out-of-scope 场景 | 不输出标记 |

## Design Rationale

- **不阻断交付**：避免成为又一个让人忽视的 hard gate；用风险提示卡 + 可选升级路径。
- **不全文嵌入政策**：政策细节走 Dify KB 按需检索，节省上下文。
- **不重复触发**：单一 turn 内同一产出只触发一次；多 agent 串联时由最后交付方负责。
- **保留私有工具链**：核心 AI 工具链、提示词资产、私有流程默认作为技术秘密，不在风险卡中建议公开转化。

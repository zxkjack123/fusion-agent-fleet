---
description: "Plan file format specs, templates, and execution examples for plan-architect."
applyTo: "**"
revision: 1
---

# Plan Architect Reference Material

Extracted from `.opencode/agent/plan-architect.md` to reduce prompt token consumption.

## Problem Statement
- ...

## Acceptance Scenarios
1. GIVEN ... WHEN ... THEN ...
2. GIVEN ... WHEN ... THEN ...

## Constraints
- Compatibility: ...
- Performance / cost / security: ...

## Non-Goals
- ...

## Open Questions
- [ ] ...

## Traceability Matrix
| Scenario | Plan Task | Verification |
|----------|-----------|--------------|
| S1 | T1.1 | command/manual check |
```

若未触发 spec，计划的审查日志中记录 `[Spec Artifact: SKIPPED — trigger not met]`，不要创建空 spec 文件。

### 阶段二：方案草案

产出初版方案，包含：
- **问题根因分析**（如果是 bug）或 **需求拆解**（如果是新功能）
- **技术方案概述**：选型理由、架构决策
- **影响范围评估**：哪些文件/模块会被修改，哪些不应被触碰
- **风险识别**：可能出问题的地方及缓解措施
- **模式适配**：基于 EXPANSION / HOLD / REDUCTION 调整方案粒度与审查重点（扩展价值、范围保持、或最小化交付）
- **CT 方案假设验证（可选）**：草案完成后、进入结构化自审前，可委派 `Critical Thinking` 对方案的 top 3 核心假设运行 "What if not?" 测试：(a) 若根因分析有误，哪些 Task 会失效？(b) 技术选型有无被锚定效应影响——是否考虑过替代方案？(c) 影响范围评估是否遗漏了隐含依赖？CT 发现纳入阶段三审查输入。*Fallback*: 自行检查上述三个问题。

### 阶段 2.5：Red-Team Round（方案 ≥3 Task 时默认开启）

对 ≥3 个 Task 的方案**默认开启**（<3 Task 可跳过并标注 `[Red-Team: SKIP — <3 Tasks]`）。委派 `Critical Thinking` 并行跑 3 个 lens，每个 lens 产出 0–N 条 finding：

| Lens | 检查焦点 | 典型 finding |
|------|----------|-------------|
| Prompt Injection | 方案中的用户输入 / 外部数据是否可被注入恶意内容 | Task 2 的模板字符串拼接未转义用户变量 |
| Silent Failure | 哪些步骤失败时不会报错、而是静默产出错误结果 | Task 3 的 grep 无匹配时返回空而非报错，后续 sed 会清空文件 |
| Cross-Task Drift | 前序 Task 的输出假设是否与后序 Task 的输入假设一致 | Task 1 输出 JSON 但 Task 4 假设 YAML 格式 |

**执行方式**：`opencode task(agentName="Critical Thinking", prompt="对以下执行计划运行 Red-Team 审查…")`。若 `Critical Thinking` 不可用，自行逐条检查三个 lens。

**Finding 处置**：Severity ≥ Medium 的 finding 必须在阶段三开始前修正到 plan 中；Low severity 记入审查日志即可。

### 阶段三：结构化自我审查（≥3 轮强制迭代，内部自动完成）

**不等待用户指令**——在同一次响应中自动连续执行所有审查轮次，直到触发终止条件后直接进入阶段四输出。

对草案进行**至少 3 轮**结构化审查，每轮聚焦不同维度。每发现 1 个问题记 1 issue，发现即修正（同一轮内）。

#### 迭代循环

```
Round 1 → fix → Round 2 → fix → Round 3 → fix
  → 检查终止条件 → 未满足 → Round 4 (自由审查) → fix
  → 检查终止条件 → 未满足 → Round 5 (硬上限，强制输出)
```

#### Round 1 — 结构完整性 (Structural Completeness)

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | 背景与目标 section | 问题描述、目标、非目标 三个字段均存在且非空 |
| 2 | 技术方案 section | 方案概述、关键设计决策、影响范围 均存在 |
| 3 | Task 必需字段 | 每个 Task 包含目标、依赖、修改内容、修改边界、测试要求、验收标准、潜在风险 — 缺一记 1 issue |
| 4 | Post-Execution Verification | 存在且含至少 1 条可执行验证命令（Automated Verification 表非空）和至少 1 条项目特定检查项 |
| 5 | 编号连续性 | Phase/Task 编号无跳号、无重复 |
| 6 | Error & Rescue Map | 存在关键失败路径映射表；如有未处理且可能静默失败路径，必须标记 CRITICAL GAP |
| 7 | 已有代码/流程复用分析 | 明确列出已有能力是"复用"还是"重建"，并说明理由 |
| 8 | 项目原则对齐（Constitution Alignment） | 若 `memories/repo/project-principles.md` 存在，read 并逐条核查计划不违反既定原则；不存在则跳过并标注 `[Constitution: N/A — 无项目原则文件]` |
| 9 | 契约完备性（Contract Completeness） | 每个 Task 的 `input_contracts` 中的每条 `identifier` 必须能在其 `dependencies` 任一前置 Task 的 `output_contracts` 中找到完全匹配项；`output_contracts` 中每条 `identifier` 必须在"修改内容"中出现 — 缺失记 1 issue |
| 9a (v1.1) | contract_signature 必填 | 对 `type ∈ {file, function, data}` 的 contract，`contract_signature` 必须非空且包含 exports 列表 / 函数签名 / schema 摘要 — 缺失记 1 issue |
| 9b (v1.1) | verification_hint 必填 | 对 `type == state_change` 的 contract，`verification_hint` 必须非空且 `type ∈ {grep, file_section, manual}`；grep 需 pattern，file_section 需 file — 缺失记 1 issue |
| 9c (v1.1) | acceptance_criteria 结构化 | 每个元素必须是 dict（含 `claim` 与 `verify`），不允许 raw str — 违反记 1 issue |
#### Round 1.5 — 外部引用事实核查 (External Reference Verification, MANDATORY)

**核心原则**: 计划是"形式审查"还是"事实审查"的分水岭。R1 验证字段齐全，R1.5 验证字段内容真实。**任何引用真实世界对象（工具名、文件路径、API 签名、命令行选项、行号锚点）的位置都必须用工具核实，不允许凭记忆/推断写入计划。**

| # | 引用类型 | 验证方法 | 通过标准 |
|---|---------|---------|----------|
| 1 | 工具/MCP 名（`mcpzotero/X`、`mcp_*`、自定义 agent 工具列表） | `grep_search` 在源 agent 文件 / MCP 工具清单 / `tool_list` 输出中确认 | 每个引用旁附 evidence: `[verified: file.md:L123]` 或 grep 命中行 |
| 2 | 文件 / 目录 / section 锚点 | `file_search` / `read_file` 当前行号 | 同上 |
| 3 | 函数 / 类 / API 签名 | `read_file` 看实际定义 | 签名与计划一致 |
| 4 | Shell / git / awk / sed 命令选项（`git mv -k`、`sed -E`、`find -exec`） | 查 `--help` / man / 已知文档 | 选项确实存在且语义正确 |
| 5 | 行号 / 区间引用 | `read_file` 当前快照 | 行号与当前文件一致 |
| 6 | 版本 / 版本兼容性 | 方案中出现的第三方库版本号、API 版本必须 `grep_search` 项目 `pyproject.toml` / `package.json` / `requirements*.txt` 确认一致；若项目无锁定文件，查 PyPI / npm 确认该版本存在 | 每个版本号旁附 `[verified: pyproject.toml:L45]` 或 `[verified: PyPI 2025-04-24]` |
| 7 | 🆕 遗漏能力检查（Missed Capability Check） | 对计划中每个**新增或修改的组件**（新 script / 新 instruction / 新 agent workflow / 新 schema 字段），对照阶段一的 `_capability_map` 检查：(a) 计划中新建的组件是否与已有的等效功能重复？(b) 计划引用的 agent 侧车结构（meta.yaml 中的 delegates、tier、schema）是否与实际文件一致？(c) 计划假设的 repo 结构（如"TE 没有 meta.yaml"）是否与实际情况一致？ | 每个新增组件旁标 `[MISSED-CAP: 已有 script X 可替代计划中的 Y — 建议复用或扩展 X 而非新建]` 或 `[CAP-OK: 经 capability map 验证无等效功能]`；agent 侧车结构引用 100% 与 `.meta.yaml` 实际一致 |

**通过标准**: 未验证项标 `[UNVERIFIED]`，全部清零方能进入 R2。**长前缀工具名（`mcpzotero/...`、`mcp_project-manag_*` 等）记错率最高，必须 100% 核查。** `[MISSED-CAP]` 项等同于 R1.5 的 FAIL——必须在阶段三修正（复用已有能力或提供充分理由说明为何需新建而非复用）。

#### Round 2 — 可执行性 (Executability)

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | 任务粒度 | 每个 Task 修改 ≤3 个文件 |
| 2 | 依赖关系 | 每个 Task 的 `依赖` 字段已填写；无循环依赖或后置依赖；Execution Wave 表与依赖字段一致 |
| 2.5 | YAML field non-empty | 每个 Task 的 `goal`/`modifications`/`boundaries`/`test_commands`/`test_expected` 在 YAML frontmatter 中非空（空字符串/空列表 = FAIL）；`suggested_executor` 至少对跨域任务非空 |
| 3 | 修改边界 | 明确列出"不得修改"的文件/section，不用笼统的"仅本文件" |
| 4 | 测试要求 | 有具体命令 + 预期输出（拒绝"确保正确"、"测试通过"等模糊表述） |
| 5 | 验收标准 | 每条标准是二元可验证的（是/否），拒绝"功能正常"、"体验良好"等主观描述 |
| 6 | 时序推演（Temporal Interrogation） | 对 ≥3 个 Task 的计划，需明确实施初期/中期/后期可能遇到的关键决策与潜在阻塞 |
| 7 | 计划内嵌脚本干跑（Script Dry-Run） | 计划中出现的 shell/python/awk/sed 片段，必须执行其中之一：(a) `bash -n` / `python3 -c 'compile(open(f).read(),f,"exec")'` 静态语法检查；(b) 用 echo 替换破坏性动作做 dry-run；(c) mentally trace 关键替换的展开顺序。**已知陷阱清单**：① shell 算术展开 `$((...))` 发生在 sed 拿到字符串之前，sed 的 `\1` 反向引用不能嵌入 `$((...))` 内；② `for f in $list; do sed -i ...` 重复执行会累积副作用（如 revision 反复 +1）；③ in-place 编辑的正则若不限定行号，可能误匹配文档正文；④ `find -exec` 与 `xargs` 在空文件名/特殊字符下语义不同。 |

#### Round 2.8 — LLM 可执行性审查 (LLM Executability Audit)

**核心原则**: R1 验证字段齐全，R1.5 验证外部引用真实，R2 验证语法和结构正确——但都检查不到「下游 LLM 执行时是否需要猜测」。R2.8 是分水岭：**从人类可读走向 LLM 可执行**。

**审查方法**: 逐条 Task 在心智中模拟一遍——「我是 Task Executor，收到这个任务描述，我需要做哪些判断？哪些信息在 task 描述中找不到？」

| # | 检查项 | 审查方法 | 通过标准 |
|---|--------|---------|----------|
| 1 | 文件路径歧义 | 逐条检查「修改内容」中的文件路径——是完整相对路径（可从 repo root 唯一定位）还是模糊描述？ | 每个路径无歧义可定位；拒绝「相关文件」「对应模块」「同级目录」等模糊表述 |
| 2 | 修改动作歧义 | 逐条检查改什么——「修改 class X」是加方法？改签名？改实现？「更新 section Y」是替换整个 section 还是插入某段？ | 每个修改动作含精确动词（添加/删除/重命名/修改签名/替换/插入）+ 目标（方法名/行范围/section 名）+ 上下文锚点（前后 3 行原文） |
| 3 | 验收 grep/命令歧义 | 模拟执行：`verify` 字段中的 grep/shell 命令是否可能 match 非预期文本？（如 `grep -c '## Output Template' file.md` 可能 match 标题本身 + 目录链接各 1 次） | grep pattern 足够精确（含 `^## ` 前缀或 `\b` 词边界），或在 `expected` 中说明允许范围（如 `1..2`） |
| 4 | 边界漏项 | 「不得修改」列表是否覆盖了所有可能被波及的文件？将 R3-7 What-If Preview 的影响分析结果与修改边界逐项交叉检查 | What-If Preview 识别的波及文件 100% 出现在「修改边界」或「不得修改」中 — 遗漏记 1 issue |
| 5 | contract 消费方可执行性 | 对每条 `output_contracts`，检查其 `identifier` 与 `contract_signature` 是否为下游 Task 的 `input_contracts` 引用提供了足够信息？下游 LLM 能否据此定位到具体文件/section/符号？ | 下游 Task 的 `input_contracts.identifier` 可使用上游的 `output_contracts.identifier` 无歧义定位 |
| 6 | 数值精度与约束可见性 | 检查所有数值型验收标准——`expected` 字段中的数值是否有明确的范围/精度说明？ | `>=1` / `exit 0` / `1..2` 等二元或区间明确；拒绝「成功」「正确」等非数值预期 |
| 7 | modify_specs action 枚举 | 检查所有 `modify_specs` 条目中的 `action` 值是否在已知枚举中（`add_method`/`replace_line`/`replace_section`/`insert_after`/`add_field`/`add_class`/`replace_import`） | 所有 action 值在枚举内；不在枚举内的标记 `[ACTION:UNKNOWN]` |
| 8 | context 完整性 | 检查顶层 `context` 块是否存在、`git_commit` 和 `generated_at` 是否非空 | context 存在且 git_commit 非空（非 git repo 时免检） |
| 9 | Post-Execution Verification 可执行性 | 逐条检查 Automated Verification 表中的命令——是否可被 Task Executor 直接执行？（`pytest tests/ -v` 可执行；「测试通过」不可执行） | 每条 Automated Verification 含可执行的 shell 命令 + 明确的 expected 值（exit 0 / 输出包含 X / …）；拒绝模糊描述 |
| 10 | 🆕 Capability Blind Spot Check | 从 Task Executor 的视角，检查：在执行此 task 时，TE 是否会使用本 repo 已有的基础设施（scripts/tools/agents），而计划中却指导它"从零构建"或"自行创建"？——这是 R1.5 遗漏能力检查的 LLM-可执行版。具体检查：计划中 `python3 scripts/state_api.py --mode write_checkpoint` 的前提是 state_api.py 已创建——但如果是本计划新建的，TE 需要先完成创建该文件的任务才能使用。是否存在"先有鸡还是先有蛋"的顺序问题？ | 若计划新建了 tool/script（如 `scripts/foo.py`），后续 task 使用该 tool 时 MUST 依赖前置 task；顺序错误 → 记 1 issue `[BLIND-SPOT: 引用 scripts/foo.py 但前置 task 尚未创建 — 依赖顺序错误]` |

**审查日志记录**: R2.8 发现的每条歧义标注 `[AMBIGUITY-FIXED]` + 修正后的精确表述。`[BLIND-SPOT]` 标注也纳入 planning-pitfalls 反馈。

#### Round 3 — 风险与边缘情况 (Risk & Edge Cases)

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | 潜在风险 | 非 trivial Task 的风险不能写"无"——至少识别一个可能的问题 |
| 2 | 跨 Task 交互 | Task N 的修改不会破坏 Task M 的产出 |
| 3 | 回滚安全性 | 某个 Task 失败时，已完成的 Task 产出仍然安全可用 |
| 4 | 遗漏场景 | 没有用户可能遇到但方案未覆盖的边缘输入/状态 |
| 5 | 回归风险 | 修改不影响"影响范围"之外的模块 |
| 6 | 跨轮次决策一致性（Cross-Round Consistency） | 本轮修正不得违反前轮已确立的原则；若有表面冲突，必须在审查日志中显式区分（如"discovery hint" vs "passive fallback 污染"），并在受影响的 Task 旁加 inline 注释说明为何不算违反原则 |
| 7 | 下游影响预览（What-If Preview） | 对每个修改 ≥2 个文件的 Task，列出"该改动可能波及的未声明依赖"——用 `grep_search` / `vscode_listCodeUsages` 检查被修改符号（函数签名、类名、配置键）的引用方，在 Task 中附 `[影响预览: X.py:foo() → a.py:12, b.py:45]`。若无跨文件引用则标 `[影响预览: 无跨文件引用]` |

#### Round 4+ — 自由审查 (Open Review)

若 Round 3 结束后仍有未清零的 issue，进行自由审查：重点复检前轮遗留问题和修正是否引入新问题。

#### 收敛检测信号表（Convergence Signal Table）

在每轮审查结束后记录以下信号（用于辅助是否继续深挖）：

| 信号 | 观测方式 | 提示动作 |
|------|----------|----------|
| S1: issue 数单调下降 | 最近 2-3 轮 issue 总数持续下降（如 5→3→1） | 继续当前策略，优先收尾 |
| S2: 同类别 issue 连续重复 | 同一类别问题连续 ≥2 轮重复出现 | 触发策略切换（重写该 section 而非微调） |
| S3: 修正引入新 issue 比率 | 当轮“新增 issue / 已修正 issue”比率持续升高 | 暂停扩展，回到最小可执行方案 |

使用规则：该信号表为 advisory，不直接替代终止条件；用于在 T1/T2 判定前调整审查策略。

#### 终止条件

| 编号 | 条件 | 触发规则 | 输出行为 |
|------|------|----------|----------|
| T5 | 指标驱动收敛终止 | 在检查 T1 前先检查：若 S1 成立且 S2/S3 均未触发，且最近一轮仅剩低风险 issue，可提前收敛并转入输出。**前置条件**：R1.5 已执行且 0 未验证项；R3 跨轮次一致性检查已执行 | 正常输出 plan，并在审查日志记录触发依据 |
| T1 | 收敛终止 | ≥3 轮完成 AND 最近一轮 issue = 0 AND **R1.5 已执行且 0 未验证项** AND **R3 跨轮次一致性检查已执行** | 正常输出 plan |
| T2 | 硬上限终止 | 第 5 轮完成（无论 issue 数） | 输出 plan，剩余 issues 写入"已知局限" |
| T3 | 用户终止 | 用户明确要求停止 | 输出当前版本，标注"用户终止，审查未完成" |
| T4 | 零缺陷快速通过 | R1 + R1.5 + R2 + R2.8 + R3 全部 issue = 0 AND R1.5 0 未验证项 | 正常输出 plan |

**T1/T4 强化说明**: 旧版 T1 允许"3 轮都没碰到正确维度"时静态触发（issue=0 仅因为没人查事实）。新版强制 R1.5 外部核查与 R3-6 跨轮一致性检查均已执行，杜绝"形式合格、事实失真"的伪收敛。

每轮结束后更新审查日志（见模板），记录该轮聚焦点、发现数、修正数、剩余数。

### 阶段四：输出执行计划

-1. **Schema 构造**：先在心智中按 `ExecutionPlan` schema（`agent_workflows.common.plan_schema`）组织 phases→tasks→contracts 层次结构。每个 Task 必须填 `input_contracts` 和 `output_contracts`（`ArtifactContract` 类型：`file`/`function`/`config_key`/`data`/`state_change`）。序列化为 YAML frontmatter（key: `plan_schema_version: "1.0"`, `scope_mode`, `waves`, `phases`），拼接 markdown body。**所有 TaskDef 的 `goal`/`modifications`/`boundaries`/`test_commands`/`test_expected`/`suggested_executor` 必须在 YAML frontmatter 中填充非空值**（双写策略：YAML 为 authoritative source，markdown body 保留对应 prose 供人类阅读和 v1.0 兼容）。

  **MODIFY_SPEC 填充优先级**：
  - **P1（最高）**：阶段一步骤 9 提取的 `_upstream_modify_specs` — 直接复用，无需从 `Remediation` 重新推导
  - **P2**：有明确 file+target 锚点的 findings，从 `Remediation` 文本正则提取或手动构造
  - **P3（fallback）**：锚点不明确 — 在 modify_specs 留空数组 `[]`，在 markdown body task description 中保留人类可读操作描述
  - `_upstream_modify_specs` 中存在但 action 枚举不匹配已知列表时：保留原始值，在 `contract_signature` 中标注 `[upstream]` 来源

**Context 快照生成**（plan 级别，写入 YAML frontmatter 顶层 `context` 块）：
  - 执行 `git rev-parse HEAD` 获取当前 commit（非 git repo 时 context 设为 null 并标注 `[context: N/A — not in git repo]`）
  - 执行 `date -u +%Y-%m-%dT%H:%M:%SZ` 获取 UTC 时间戳
  - 对计划中涉及的关键文件（最多 10 个）执行 `sha256sum <path>`（`sha256sum` 不可用时用 `sha1sum` 代替；两者都不可用则仅记录路径，hash 留空并标注 `[hash: unavailable]`）
  - 将结果填入：
    ```yaml
    context:
      git_commit: "abc1234..."
      generated_at: "2026-01-01T00:00:00Z"
      files:
        - {path: "src/validator.py", sha256: "def5678..."}
    ```
0. **De-AI-Fier Gate** [Gate D.0]: 执行 `instructions/de-ai-fier-gate.instructions.md` at L1-Tone（计划文件为内部交付物，仅做 AI 痕迹检查，不强制术语/单位检查）。**FAIL → 阻断交付。**
> ⚠️ **DS-CRITICAL**: DeepSeek V4 Pro 在该门禁维度的失效风险显著高于 Claude Opus。本门禁不得弱化为 skip/optional，不得因"看起来没问题"而跳过工具调用。若 MCP 不可用，必须标注 `[⚠️ DS-CRITICAL gate skipped — MCP unavailable]` 并通知用户。
1. **Pre-Delivery Audit** [Gate D.3]: 执行 `instructions/pre-delivery-audit.instructions.md` — L1-Lite 用于纯流程/代码计划；L2-Standard 用于包含技术参数/数值指标的计划；L3-Critical 用于涉及仿真/核/辐射/安全参数的计划。审核表附到计划文件末尾。**FAIL → 返回阶段三修正。**

将最终方案写入 markdown 文件（默认路径：`.github/plans/<topic>.md`，用户可指定其他路径）。

1.5. **Schema Self-Validation**：写文件后 execute `python -m agent_workflows.tools.validate_plan <path> --strict`；exit 非 0 → 回阶段三 R1 修正契约（最多 2 轮自检），仍失败 → 降级为 `--warn-only` 输出并在审查日志注记 `[Schema: WARN — <N> violations]`。**新建 plan 默认 v1.1**（frontmatter `plan_schema_version: "1.1"`）；旧 plan 维持其声明版本，不强制升级。v1.1 plan 必须通过 contract_signature / verification_hint / 结构化 acceptance 的强校验。

如用户要求"立即执行"该计划，可委派 `Task Executor` 按任务顺序逐条实施。

计划已就绪。建议先审阅方案质量——若发现不足，可点击上方「Refine this plan」由 Plan Architect (mode=refine) 迭代改进，满意后再点击「Execute this plan」交由 @Task Executor 逐条实施。

迭代时原地修改计划文件（不创建新版本），通过 git diff 追溯修改历史。

**Skill Crystallization Check**: After outputting the plan, execute `instructions/skill-crystallization.instructions.md` trigger detection (T1/T2/T3). If any trigger fires, propose crystallization to user. If none fires, skip silently.

**Retro Hook — Planning Pitfalls 自动沉淀**: 若本次审查中 R2.8 发现 ≥1 条歧义修正（`[AMBIGUITY-FIXED]`）、或 R1.5 发现 ≥1 条 `[UNVERIFIED]` 最终需修正、或 R2-7 Script Dry-Run 发现 ≥1 条 shell/sed/awk 陷阱、或 R3-7 What-If Preview 发现 ≥1 条未声明依赖、**或 R1.5 遗漏能力检查发现 ≥1 条 `[MISSED-CAP]`、或 R2.8 Capability Blind Spot Check 发现 ≥1 条 `[BLIND-SPOT]`**，自动提议将该陷阱写入 `memories/repo/planning-pitfalls.md`（格式：`| pitfall_id | category | description | discovered | source_plan |`）。下次 Plan Architect 启动时，阶段一步骤 7 之后 read 该文件作为 R1.5 / R2-7 / R2.8 的 known-pitfalls 输入，优先检查历史踩坑点。用户确认后写入，不自动写入。

## Executive Summary
- 总体评分：PASS / FAIL / CONDITIONAL（有条件通过）
- 阻塞级 issue 数：N
- 建议改进项数：M

## Issue List
| R# | Severity | Task | Finding | Suggestion |
|----|----------|------|---------|------------|
| R1.5 | BLOCKING | T2.1 | 工具名 `mcp_citation-li_*` 未验证 | grep 确认后更新 |
| R2.8.1 | WARNING | T1.2 | 文件路径模糊：「对应测试文件」| 改为 `tests/test_foo.py` |

## Ambiguity Report（R2.8 详细输出）
每条歧义标注 Task ID + 字段名 + 当前值 + 歧义分析 + 建议修正。

## Execution Trace Alignment（如有执行记录）
对照 TE commit 验证每项 acceptance_criteria 的实际达成状态。
```

### 与 PM Coordinator 交互
- Review Mode 的审核报告通过 PM Coordinator 写入 PM 系统（`pm_important_info_add`），不创建 task。
- 若审核发现 ≥1 条 BLOCKING issue，PM 中记录为 risk item。

## Plan Improvement Summary

**Improved**: YYYY-MM-DD HH:MM
**Improver**: Plan Architect (mode=improve)
**Plan**: .github/plans/<topic>.md

### Issues Found & Fixed
| Task | Failure Type | Root Cause | Fix Applied |
|------|-------------|------------|-------------|
| T2.1 | 歧义/信息不足 | 文件路径模糊：「对应测试文件」 | 改为精确路径 `tests/test_foo.py` |
| T3.2 | 契约断裂 | 前置 T3.1 输出 function `bar()` 但本 task 期望 `baz()` | 修正 input_contracts 匹配 T3.1 实际输出 |

### Tasks Ready for Re-execution
- T2.1, T3.2, T3.3 (dependency chain from first failed task)

### Still Blocked (需要人工介入)
- T4.1: 依赖 MCP server `xxx` 不可用，需运维恢复
```

### Improve Mode 迭代上限

- 同一 plan 的 improve 迭代**最多 3 轮**（含首次生成）。第 3 轮 improve 后仍存在阻塞项 → 标记 `[IMPROVE: EXHAUSTED]`，建议人工介入。
- 每轮 improve 后重新委派 Task Executor；TE 再次受阻 → 再次 improve。
- 若连续 2 轮 improve 未减少阻塞 task 数 → 暂停迭代，标记 `[IMPROVE: STALLED]`，输出完整诊断报告。

### 与 PM Coordinator 交互
- Improve Mode 的改进结果通过 PM Coordinator 写入 PM 系统（`pm_important_info_add`），不创建新 task。
- 改进摘要中的 "Still Blocked" 项记录为 risk item。

## Optional Trajectory Self-Report（debug-only）

仅当用户或执行计划显式要求 `--trace-agent-run` 时，才进行 best-effort 轨迹自报告。轨迹不是审计依据，不能作为完成状态判据。

- 写入路径：`.agent-runs/<session-id>.jsonl`。
- 每行必须符合 `scripts/trajectory_view.py` 文件头定义的 JSONL schema。
- `args_hash` 只能记录参数 JSON 的 SHA-256 摘要，禁止写入 raw prompt、secret、API key、token、完整文件内容或用户隐私文本。
- 若写入失败，记录一句 warning 后继续核心任务；不得因为 trajectory 写入失败阻塞计划执行。
- 若未显式要求 `--trace-agent-run`，不要创建 `.agent-runs/` 文件。

## 执行计划模板

输出的执行计划必须严格遵循以下格式：

```markdown
---
# 新 plan 默认 v1.1；v1.0 plan 仍可被解析（仅放宽 contract_signature/verification_hint/acceptance 结构）
plan_schema_version: "1.1"
scope_mode: HOLD
waves:
  - wave: 1
    tasks: [T1.1]
  - wave: 2
    tasks: [T1.2]
    depends_on: [wave:1]
phases:
  - id: "Phase 1"
    title: "..."
    tasks:
      - id: "T1.1"
        phase: 1
        title: "..."
        goal: "在 Validator 类中添加 validate() 方法，接受 str 输入返回 bool"
        dependencies: []
        # 以下字段必须在 YAML frontmatter 中填充非空值（双写策略：同时写入 markdown body）
        modifications:
          - "src/validator.py"
        modify_specs:
          - {action: "add_method", file: "src/validator.py", target: "class Validator", description: "添加 validate(self, data: str) -> bool 方法"}
        boundaries:
          - "不得修改 tests/test_validator.py"
          - "不得修改 src/__init__.py"
        test_commands:
          - "pytest tests/test_validator.py -k test_validate -v"
        test_expected:
          - "exit 0"
        suggested_executor: "Task Executor"
        input_contracts: []
        output_contracts:
          # file/function/data → 必填 contract_signature
          - {type: "file", identifier: "path/to/output.py", contract_signature: "exports foo, bar"}
          # state_change → 必填 verification_hint
          - {type: "state_change", identifier: "agent.md:updated", verification_hint: {type: "grep", pattern: "revision: 12", file: "agent.md", expected_count: ">=1"}}
        acceptance_criteria:
          - {claim: "模块可导入", verify: "python -c 'import foo'", expected: "exit 0"}
          - {claim: "文档已更新", verify: "manual", expected: "reviewer confirms section X added"}
      - id: "T1.2"
        phase: 1
        title: "..."
        goal: "重构 DataLoader 类，将硬编码路径改为构造函数参数"
        dependencies: ["T1.1"]
        modifications:
          - "src/loader.py"
        boundaries:
          - "不得修改 tests/test_loader.py"
          - "不得修改 src/__init__.py"
        test_commands:
          - "pytest tests/test_loader.py -v"
        test_expected:
          - "exit 0"
        suggested_executor: "Task Executor"
        input_contracts: []
        output_contracts:
          - {type: "file", identifier: "src/loader.py", contract_signature: "exports DataLoader(path: str)"}
          - {type: "state_change", identifier: "agent.md:updated", verification_hint: {type: "grep", pattern: "revision: 13", file: "agent.md", expected_count: ">=1"}}
        acceptance_criteria:
          - {claim: "DataLoader 接受 path 参数", verify: "python -c 'from loader import DataLoader; dl = DataLoader(path=\"/tmp\")'", expected: "exit 0"}
          - {claim: "文档已更新", verify: "manual", expected: "reviewer confirms section X added"}
---

# [标题]

## 背景与目标
- **问题/需求描述**：...
- **根因分析**（如适用）：...
- **目标**：...
- **非目标（不做什么）**：
  - 不做项 A — 一句话理由
  - 不做项 B — 一句话理由
- **已有代码/流程复用分析**：
  - 现有能力 X：复用 / 重建（理由）
  - 现有能力 Y：复用 / 重建（理由）

## 技术方案
- **方案概述**：...
- **关键设计决策**：...
- **影响范围**：涉及文件列表

## Error & Rescue Map（关键失败路径映射）

| 代码路径/操作 | 可能的失败 | 错误类型 | 已处理？ | 处理方式 | 用户可见行为 |
|-------------|-----------|---------|---------|---------|------------|
| ... | ... | ... | Y/N | ... | ... |

- 若存在 `已处理？=N` 且“用户可见行为”为静默失败，必须标记为 **CRITICAL GAP** 并在任务中增加修复动作。
- 对高风险路径（外部依赖、文件写入、网络请求），至少列出一条降级或回滚策略。

## 执行计划

### Phase 1: [阶段名称]

#### Task 1.1: [任务名称]
- **目标**：一句话描述这个任务要达成什么
- **依赖**：无 / T1.2, T2.1（列出本 Task 依赖的前置 Task 编号）
- **input_contracts**：`[{type: "file", identifier: "path/from/dep.py", contract_signature: "..."}]`（来自依赖 Task 的 output；无依赖时为空列表。v1.1 下对 file/function/data 必须含 `contract_signature`；对 state_change 必须含 `verification_hint`）
- **output_contracts**：`[{type: "file", identifier: "path/to/output.py", contract_signature: "exports X, Y"}]`（ArtifactType: `file`/`function`/`config_key`/`data`/`state_change`；v1.1 下对 file/function/data 必须含 `contract_signature`；对 state_change 必须含 `verification_hint`）
- **修改内容**（本字段同时写入 YAML frontmatter `modifications` 和 `modify_specs`——双写策略）：
  - 文件 `path/to/file.py`：具体要修改什么（如"在 class X 中添加 method Y"）
  - `modify_specs` 结构化格式（YAML 内使用，替代模糊 prose）：
    ```yaml
    modify_specs:
      - {action: "add_method|replace_line|replace_section|insert_after", file: "src/foo.py", target: "class Bar | L42 | ## 背景与目标", description: "人类可读的修改描述"}
    ```
    - `action`: 修改动作类型，必须为 `add_method` / `replace_line` / `replace_section` / `insert_after` / `add_field` / `add_class` / `replace_import` 之一
    - `file`: 目标文件路径（repo-root 相对路径）
    - `target`: 锚点定位（类名、行号、section 标题等）
    - `description`: 人类可读的修改摘要
- **修改边界**（本字段同时写入 YAML frontmatter `boundaries`——双写策略）：不得修改 `path/to/other.py`
- **测试要求**（本字段同时写入 YAML frontmatter `test_commands` + `test_expected`——双写策略）：
  - 运行 `pytest tests/test_xxx.py -k test_specific`
  - 预期输出：全部通过
- **验收标准**（v1.1：结构化 `AcceptanceCriterion`，每条含 `claim` / `verify` / `expected`；v1.0 仍接受 raw str list）：
  - **claim**: [可验证陈述 1]
    - **verify**: `grep -c 'foo' bar.py`（或 `manual` 表示需人工 review）
    - **expected**: `>=1`
  - **claim**: [可验证陈述 2]
    - **verify**: `manual`
    - **expected**: reviewer confirms ...
- **潜在风险**：...
- **预留歧义标注**：（Task Executor 执行后回写，Plan Architect Review Mode 检查）
  - [ ] 无歧义：所有字段可直接执行，无需额外推断
  - 歧义点：[如有] 具体字段名与歧义描述

#### Task 1.2: [任务名称]
- **依赖**：T1.1
- **执行者**：...（可选，标注建议执行该任务的 agent）
...

### Phase 2: [阶段名称]
...

## Execution Wave（并行执行波次）

根据 Task 依赖关系生成的并行执行分组。无依赖的 Task 归入 Wave 1，依赖 Wave 1 的归入 Wave 2，以此类推。

| Wave | 可并行 Task | 依赖已完成 |
|------|------------|------------|
| W1 | T1.1, T2.1 | — |
| W2 | T1.2, T2.2 | W1 |
| W3 | T3.1 | W1 + W2 |

> Task Executor 按 Wave 顺序实施：同一 Wave 内的 Task 可并行或任意顺序执行，跨 Wave 必须等待前序 Wave 全部完成。

## Post-Execution Verification

Task Executor 在所有 plan task 执行完毕后**必须**运行本节中的验证命令。Plan Architect 应确保每条命令可直接执行（非模糊描述）。

### Automated Verification（Task Executor 自动执行）

| ID | Description | Command | Expected |
|----|-------------|---------|----------|
| V1 | 全量单元测试 | `pytest tests/ -v` | exit 0 |
| V2 | E2E / 集成测试 | `pytest tests/e2e/ -v` | exit 0 |
| V3 | Lint 检查 | `ruff check src/` | exit 0 |
| V4 | [项目特定检查] | ... | ... |

### Manual Verification（需人工确认）

- [ ] M1: [需要人工验证的检查项 1]
- [ ] M2: [需要人工验证的检查项 2]

## 审查日志

| 轮次 | 聚焦 | 发现问题数 | 已修正 | 剩余 |
|------|------|-----------|--------|------|
| R1 | 结构完整性 | ? | ? | ? |
| R1.5 | 外部引用事实核查 | ? | ? | ? |
| R2 | 可执行性（含脚本干跑） | ? | ? | ? |
| R3 | 风险与边缘（含跨轮一致性） | ? | ? | ? |
| **终止** | **[T1/T2/T3/T4/T5] — [条件名]** | | | **?** |

### Completion Summary

| 维度 | 结果 |
|------|------|
| 背景与目标 | 完整 / 缺失项 |
| 技术方案 | 完整 / 缺失项 |
| Error & Rescue Map | 已覆盖路径数、CRITICAL GAP 数 |
| 执行计划 | Phase 数、Task 数 |
| Post-Execution Verification | Automated 验证命令数、Manual 检查项数 |
| 已知局限 | 无 / 列表 |

### [Rn Issues]（仅记录发现了问题的轮次）
- **Issue Rn-m**: [问题描述] → [修正措施] ✅ 已修正 / ⚠️ 遗留
```

## 文档修改计划模板

当需求是基于审阅意见对论文/报告/稿件进行修改时，使用以下模板：

```markdown
# [文档修改计划标题]

## 约束

- **只允许创建/编辑** `.github/plans/` 目录及用户明确指定路径下的 markdown 文件，或用户明确提供的目标稿件内容。绝不修改项目源代码、配置文件或测试文件。
- **绝不猜测代码行为或稿件内容**。先 read 再分析，不确定就用 Explore agent 调研。
- **任务粒度控制（代码）**：单个 task 的修改不超过 3 个文件，预计实施时间可控。
- **任务粒度控制（文档）**：单个 task 的修改不超过 2 个章节（或 1 个主章节 + 其直接关联摘要/结论段落）。
- **如果用户要求继续迭代**，基于已有计划文件进行增量修改，而非重写。
- **模板选择规则**：若需求涉及论文/报告/稿件修改，使用"文档修改计划模板"；若需求涉及代码实施，使用"执行计划模板"。
- 产出 plan 文件必须含 YAML frontmatter 含 `plan_schema_version` >= `"1.0"`；阶段四 Schema Self-Validation 失败不可静默忽略。

## Resume Logic（中断恢复）

如工作流被中断（如 token 耗尽、用户手动停止、会话断开），用户请求继续时：

1. 检查 `.github/plans/<topic>.md` 是否已存在且有部分内容。
2. 若存在，读取该计划文件，定位 `审查日志` 表中最后一行的轮次标记（如 `R2`）。
3. **从该轮次的下一步恢复**，不从阶段一重新开始。例如：若审查日志显示 R2 已完成但 R3 未记录，则从 R3 开始。
4. 若计划文件存在但无审查日志（仍在阶段二起草中），则从已有内容的末尾继续追加。
5. 向用户确认恢复点：`"检测到已有计划 <filename>，上次进度到 R<N>。将从 R<N+1> 恢复。"`
** | `python -m agent_workflows.tools.validate_plan <path> --strict` exit 0 | ✅ |


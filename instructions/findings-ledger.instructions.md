---
description: "跨 Session 知识积累规范：Findings Ledger YAML + Dify KB 双重存储模型、写入/查询 API。"
version: 1
revision: 1
applyTo: "task-executor"
---

# Findings Ledger — 跨 Session 知识积累

## 存储模型

双重存储（文件 + RAG 索引）：

| 层 | 位置 | 用途 | 索引方式 |
|----|------|------|---------|
| File Ledger | `projects/<name>/findings/<YYYY-MM-DD>-<short_id>.yaml` | 审计记录、精确查找、全文阅读 | 文件系统 glob + read |
| Dify KB | `project-<name>-findings` (auto-created KB) | 语义搜索、跨 topic 关联 | `global_search(dataset_ids=[...])` |

## File Ledger 格式

每个 finding 一个 YAML 文件：

```yaml
finding_id: f-20260712-001
project: ACPS-MAG-ENERGY
topic: "TF coil nuclear heating normalization"
agent: simulation-analyst
model: fallback/deepseek-v4-pro
timestamp: "2026-07-12T10:30:00Z"
task_id: "T2.3"
source_session: "01JG7X2Y8Z"
claim: "MCNP tally F4:n for TF coil inner leg yields heating density 12.3 ± 0.8 MW/m³ at 500 MW fusion power"
evidence_strength: HIGH
evidence_chain:
  - "Direct tally output from statepoint.h5 (tally 4, bin 7)"
  - "Cross-verified with mesh tally (tally 14, same region)"
  - "Normalized to 500 MW DT fusion power (14.1 MeV, 5.68e19 n/s per MW)"
sources:
  - path: "outputs/task_2.3/statepoint.100.h5"
    type: "statepoint"
  - path: "outputs/task_2.3/tally_summary.json"
    type: "structured_output"
uncertainty: "Statistical error 6.5% (1σ), systematic error from cross-section library ±3%"
reconciliation_status: CONFIRMED
reconciliation_notes: "Value within 1σ of literature range 10-15 MW/m³ [doi:10.1016/j.fusengdes.2024.114561]"
ingested_to_dify: false
outdated_by: null
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| finding_id | ✅ | 唯一 id: `f-<YYYYMMDD>-<seq>` |
| project | ✅ | 项目名 |
| topic | ✅ | 子主题 |
| agent | ✅ | 产出此 finding 的 agent |
| model | ✅ | 使用的模型 |
| timestamp | ✅ | 产生时间 ISO8601 |
| task_id | ✅ | 关联的 plan task id |
| source_session | ⬜ | trace_id |
| claim | ✅ | 核心断言 (≤300 chars) |
| evidence_strength | ✅ | HIGH/MEDIUM/LOW (引用强度) |
| evidence_chain | ✅ | 逐条证据链 |
| sources | ✅ | 源文件路径 + 类型 |
| uncertainty | ⬜ | 不确定性描述 |
| reconciliation_status | ✅ | CONFIRMED/CONTRADICTED/UNVERIFIED/PENDING |
| reconciliation_notes | ⬜ | 与其他 finding 的校核说明 |
| ingested_to_dify | ✅ | Dify KB 同步状态 |
| outdated_by | ⬜ | 被更新的 finding_id |

## 写入流程 (Post-Task Completion)

Task Executor 在 `## Post-Completion Knowledge Ingestion` 阶段执行 findings ledger 写入：

1. **Identify findings**: 扫描已完成 task 的输出，匹配以下模式：
   - 数值结果附带置信度和物理单位：`\d+\.\d+\s*±\s*\d+\.\d+\s*(MW|GW|kW|W|MeV|keV|eV|Sv|Gy|Bq|Ci|mSv|µSv|MW/m³|W/m³|g/cm³|K)`
   - 验证过的阈值/范围声明：`(CONFIRMED|VERIFIED|within range|within 1σ|matches literature)`
   - Reconciliation traces 结论：`\[Conclusion\] (CONFIRMS|CONTRADICTS)`

2. **Write to file ledger**:
   ```bash
   mkdir -p projects/<project>/findings/
   cat > projects/<project>/findings/$(date +%Y%m%d)-<seq>.yaml << 'FINDING_EOF'
   finding_id: f-$(date +%Y%m%d)-<seq>
   project: <project>
   topic: "<topic>"
   agent: <agent_name>
   model: <model_id>
   timestamp: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
   task_id: "<task_id>"
   source_session: "<trace_id>"
   claim: "<claim_text>"
   evidence_strength: <HIGH|MEDIUM|LOW>
   evidence_chain:
   （TE 逐条填入）
   sources:
   （TE 逐条填入）
   uncertainty: "<text>"
   reconciliation_status: <CONFIRMED|CONTRADICTED|UNVERIFIED>
   reconciliation_notes: "<text>"
   ingested_to_dify: false
   outdated_by: null
   FINDING_EOF
   ```

3. **Ingest to Dify KB**: 将 finding 摘要（Markdown 格式）委托 `dify-kb-manager`：
   ```
   opencode task(subagent_type="dify-kb-manager",
     prompt="Ingest the following finding into the project-<project>-findings knowledge base:
     # Finding: <claim>
     - **Project**: <project>
     - **Topic**: <topic>
     - **Evidence Strength**: <HIGH|MEDIUM|LOW>
     - **Evidence Chain**: <bullets>
     - **Reconciliation**: <CONFIRMED|CONTRADICTED|UNVERIFIED>
     
     The finding is also stored at projects/<project>/findings/<filename>.yaml.")
   ```
   成功后更新 finding yaml 中 `ingested_to_dify: true`

4. **Coverage Gate**:
   - 检查所有 findings 中是否有 `reconciliation_status: CONTRADICTED`
   - 若有 `CONTRADICTED` + `evidence_strength: LOW` → 更新 `outdated_by` 字段
   - 在最终报告中列出所有 `UNVERIFIED` 和 `CONTRADICTED` 的 findings

## 检索流程 (Session Start)

Task Executor 在开始执行 plan 之前，根据 plan 的 project/topic 元数据：

1. **文件层检索**：`grep -rl "<topic关键词>" projects/<project>/findings/`
2. **Dify KB 语义检索**：`global_search(query="<topic>", dataset_ids=["project-<project>-findings"])`
3. **注入上下文**：将检索到的 relevant findings 注入到当前 session 的上下文（作为 TE 执行前的 project background context）

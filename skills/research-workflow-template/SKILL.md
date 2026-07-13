name: research-workflow-template
---
description: "科研工作流模板：假设→建模→验证→分析→发布六阶段科研流程。"
revision: 1
---

# Research Workflow Template — 科研工作流模板

完整的"假设→建模→验证→分析→发布"科研流程模板。定义每个阶段使用哪些 agent，在哪个阶段必须触发哪些 quality gate。

## When to Use

- 开始一个新的科研项目或计算任务
- 需要确保 agent 之间的协作覆盖完整的科研流程
- 需要为标准化的科研产出（论文、报告）做计划

## When NOT to Use

- 快速单步任务（如"查一下这个文献"）— 不需要完整流程
- 纯管理任务（进度跟踪、文档更新）— 用 pm-coordinator
- 已经在其他 skill 中有明确定义的工作流（如 parametric-sweep）

## Workflow: 6-Stage Research Pipeline

```
           Hypothesis Tournament
                    │
                    ▼
    ┌───────────────────────────────┐
    │  Stage 1: Hypothesis          │
    │  Agent: fusion-deep-research   │
    │       + critical-thinking      │
    │  Gate: Meta-Reasoning Stage 0 │
    │  Output: Hypothesis result     │
    └───────────┬───────────────────┘
                │
                ▼
    ┌───────────────────────────────┐
    │  Stage 2: Modeling            │
    │  Agent: simulation-builder    │
    │  Gate: Pre-Delivery-Audit     │
    │        (L3-Critical)          │
    │        + CT Red Flag          │
    │        + Doublecheck           │
    │  Output: Validated model      │
    └───────────┬───────────────────┘
                │
                ▼
    ┌───────────────────────────────┐
    │  Stage 3: Computation         │
    │  Agent: fusion-chain-runner   │
    │       + experiment-tracker    │
    │  Gate: experiment snapshot    │
    │        + multi-code reconcili-│
    │        ation (Level-B)        │
    │  Output: HPC results          │
    └───────────┬───────────────────┘
                │
                ▼
    ┌───────────────────────────────┐
    │  Stage 4: Validation          │
    │  Agent: simulation-analyst    │
    │  Gate: benchmark_physical     │
    │        + CT challenge         │
    │        + Post-Tool Reconcilia-│
    │        tion                    │
    │        + Doublecheck spot     │
    │  Output: Validated results    │
    └───────────┬───────────────────┘
                │
                ▼
    ┌───────────────────────────────┐
    │  Stage 5: Analysis            │
    │  Agent: data-analyst          │
    │  Gate: Post-Tool Reconcilia- │
    │        tion                    │
    │  Output: Analysis report      │
    └───────────┬───────────────────┘
                │
                ▼
    ┌───────────────────────────────┐
    │  Stage 6: Publication         │
    │  Agent: academic-writer       │
    │       + paper-reviewer        │
    │  Gate: de-ai-fier             │
    │       + pre-delivery-audit    │
    │       + citation-lint         │
    │  Output: Manuscript           │
    └───────────────────────────────┘
```

## Gate Chain Summary

| Stage | Agent(s) | Gate(s) | Blocking? |
|-------|----------|---------|-----------|
| 1. Hypothesis | fusion-deep-research, critical-thinking | Meta-Reasoning Stage 0 | No |
| 2. Modeling | simulation-builder | Pre-Delivery-Audit (L3), CT, Doublecheck | **Yes** — FAIL blocks HPC |
| 3. Computation | fusion-chain-runner, experiment-tracker | experiment snapshot, multi-code reconciliation | No (but snapshot must exist) |
| 4. Validation | simulation-analyst | benchmark_physical, CT, Reconciliation, Doublecheck | **Yes** — FAIL blocks analysis |
| 5. Analysis | data-analyst | Post-Tool Reconciliation | No |
| 6. Publication | academic-writer, paper-reviewer | de-ai-fier, pre-delivery-audit, citation-lint | No |

## Cross-Repo Awareness

当工作流横跨多个仓库时：
- **Stage 2**: 指定 checkout 哪个版本的外部仓库依赖
- **Stage 3**: experiment-tracker 记录跨仓库的 git commit
- **After Stage 6**: cross-repo-auditor 检查所有相关仓库的配置一致性

## References

- `instructions/meta-reasoning-stage.instructions.md`
- `instructions/pre-delivery-audit.instructions.md`
- `scripts/benchmark_physical_quantities.py`
- `instructions/post-tool-reconciliation.instructions.md`

## Revision Log

- **rev 1 (2026-07-03)**: Initial version. 6-stage pipeline with gate chain summary.

## Common Pitfalls

1. 快速单步任务不需要完整流程 — 不要强制 6 阶段
2. Stage 2 的 gate 是阻塞性的 — 不要跳过 Pre-Delivery-Audit
3. 跨仓库依赖需要明确版本 — 避免"最新版"歧义


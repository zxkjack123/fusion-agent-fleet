name: cross-repo-guardrail
---
description: "跨仓库 guardrail 推广：将物理合理性检查推广到外部仓库。"
revision: 1
---

# Cross-Repo Guardrail — 跨仓库 Guardrail 推广

## When to Use

- 需要在外部仓库（不是 `copilot-agents`）上运行物理合理性检查
- 想验证某个仓库的仿真输出是否在 plausible ranges 范围内
- 需要统一的 guardrail 标准跨多个项目执行

## When NOT to Use

- 在 `copilot-agents` 仓库本身上运行 guardrail — 直接用 `python3 scripts/run_harness.py`
- 需要深度分析外部仓库的代码逻辑 — 这个 skill 只做输出值的 range check
- 在不是 Python 或模拟输出仓库上运行检查

## Workflow

### Stage 1: Discover — 发现仓库信息

1. 扫描目标仓库的 `README.md` 或 `AGENTS.md`，提取项目描述
2. 检查目标仓库中是否有 `.opencode/` 目录（判断是否属于你的 agent 生态）
3. 如果没有 `.opencode/`，说明这是一个非 agent 仓库 → 仅做基础的 plausibility range check
4. 确定目标仓库中 `_project-snapshot.md` 是否存在 → 如果存在，提取 key quantities 列表

### Stage 2: Check — 运行检查

对外部仓库运行 range check：

```bash
python3 /home/gw/opt/copilot-agents/scripts/benchmark_physical_quantities.py --report
```

如果目标仓库有可提取的物理量值，传 JSON：

```bash
python3 /home/gw/opt/copilot-agents/scripts/benchmark_physical_quantities.py \
  --json '{"TBR":1.15,"keff":1.045}'
```

### Stage 3: Report — 生成报告

对每个检查的仓库生成 Markdown 报告：

```markdown
## Guardrail Report — <repo-name>
| Quantity | Value | Range | Status |
|----------|-------|-------|--------|
| TBR      | 1.15  | [0.5, 2.0] | ✅ PASS |
```

### Stage 4: Integrate — 集成到文档

1. 将报告追加到目标仓库的 `docs/guardrail-report-<date>.md`
2. 如果有 doc-maintainer 可用，委派它更新目标仓库的文档
3. 将全局报告发送给 `cross-repo-auditor` 或 `pm-coordinator`

## References

- `scripts/benchmark_physical_quantities.py`
- `corpora/plausibility-ranges.yaml`
- `instructions/numerical-intuition-pitfalls.instructions.md`

## Revision Log

- **rev 1 (2026-07-03)**: Initial version. Minimal cross-repo guardrail with 4-stage workflow.

## Common Pitfalls

1. 假设外部仓库有固定输出格式 — 每个仓库可能不同。先读 README，不要假设
2. 在不是模拟仓库的项目上运行 — 跳过文档/管理类仓库
3. 不检查 benchmark 脚本的依赖 — 确保路径正确


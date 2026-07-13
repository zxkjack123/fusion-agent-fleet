---
description: "tricys tritium fuel cycle system analysis program: framework structure, interface with transport/activation codes, and validation checklist"
applyTo: ""
revision: 1
---

# tricys — Tritium Cycle System Analysis Reference

tricys is a user-developed program for tritium fuel cycle system analysis in fusion reactors.

## PROGRAM OVERVIEW

`[用户补充]` — 详细描述 tricys 的功能范围：
- 氚循环系统组件建模能力（如：包层产氚、氚提取、在线分离、储存、燃料注入等）
- 系统级 vs 组件级分析范围
- 稳态 vs 瞬态分析能力
- 支持的聚变堆型（如：CFETR、EU-DEMO、generic）

## INPUT FORMAT

`[用户补充]` — tricys 输入配置文件格式：
- 配置文件类型（JSON / YAML / INI / 自定义格式）
- 关键输入参数：
  - 等离子体参数（功率、燃烧率、脉冲/稳态）
  - 包层 TBR（Tritium Breeding Ratio）输入来源
  - 氚处理系统参数（提取效率、处理时间、储存容量）
  - 氚衰变常数和释放/滞留分数
  - 时间步配置（步长、总模拟时间）
- 单位约定：氚量（g / Ci / Bq / mol）、时间（s / d / y）

## OUTPUT FORMAT

`[用户补充]` — tricys 输出内容：
- 输出文件类型和格式
- 关键结果指标：
  - 氚自持时间（doubling time）
  - 系统氚库存量随时间变化
  - 各子系统氚流量和滞留量
  - 启动氚库存需求
  - 稳态循环效率

## INTERFACE WITH OTHER CODES

`[用户补充]` — tricys 与上游程序的数据接口：
- 是否直接读取 OpenMC/MCNP 的 TBR 计算结果？
- 是否接收 FISPACT-II 的氚产额（tritium production rate）输出？
- 是否与 natf R2S 工作流有数据流关系？
- 接口数据格式（手动输入 vs 文件传递 vs API 调用）

## COMMON PITFALLS

`[用户补充]` — 已知的常见错误和陷阱：
- 氚衰变未计入（半衰期 12.3 年，长时间模拟必须包含）
- TBR 输入未考虑增殖区覆盖率（6Li enrichment, packing fraction 影响）
- 提取效率假设过于乐观
- 时间步过大导致数值振荡

## VALIDATION CHECKLIST

After running tricys, verify:

- [ ] **Tritium mass balance**: Total tritium input (breeding + external supply) = output (burn + decay + losses + retention + exhaust). Imbalance >1% indicates a modeling error.
- [ ] **Conservation check**: At each time step, Σ(tritium in all subsystems) = initial inventory + Σ(production) − Σ(consumption) − Σ(decay) − Σ(losses). This is a strict conservation law — any violation is a bug.
- [ ] **TBR consistency**: If TBR is an input from neutronics, verify it matches the OpenMC/MCNP calculation (value and uncertainty). TBR < 1.0 without external supply → tritium self-sufficiency impossible.
- [ ] **Doubling time reasonableness**: For typical fusion reactor parameters (TBR ~1.05–1.15), doubling time should be in the range of months to a few years. Doubling time <1 week or >50 years → likely input error.
- [ ] **Time step stability**: Run sensitivity check — halving the time step should not change results by >5%. Larger changes indicate numerical instability.
- [ ] **Decay accounting**: For simulations >1 year, tritium decay (T½ = 12.32 y) must be included. Compare total inventory with and without decay — if identical, decay is not modeled.

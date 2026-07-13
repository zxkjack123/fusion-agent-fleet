---
description: "Pre-delivery physical plausibility audit: mandatory sanity checks before delivering any technical/scientific result to prevent non-physical, unreasonable outputs. 交付前物理合理性审核, 防止非物理结果, 量纲检查, 能量截断检查, 守恒定律验证, 量级合理性."
applyTo: "**"
revision: 3
---

# Pre-Delivery Audit — 交付前内部审核协议

**触发条件**: 任何 agent 在交付（Delivery / Export / Final Output）阶段之前，**必须**执行本审核协议。审核不通过则**阻断交付**，返回修正后重新审核。

**适用范围**: 所有产出包含数值结果、技术参数、物理量、拟合模型、仿真输入/输出的工作流。

## Audit Level Classification

根据交付内容的风险等级选择审核深度：

| Level | 适用场景 | 审核内容 |
|-------|----------|----------|
| **L1-Lite** | 文本/文档/演示 (无计算结果) | Checklist §1 only |
| **L2-Standard** | 含数值结果、拟合、数据分析 | Checklist §1–§4 |
| **L3-Critical** | 仿真输入构建、活化/剂量/临界计算、安全相关参数 | Checklist §1–§6 + CT challenge |

## Audit Checklist

### §1 Dimensional & Unit Consistency — 量纲与单位一致性

- [ ] 所有输出物理量标注单位
- [ ] 关键计算链无量纲不一致（如 eV vs MeV、cm vs m、barn vs cm²）
- [ ] 输入/输出单位与所用代码/库的默认单位制一致

### §2 Boundary & Cutoff Verification — 边界与截断验证

- [ ] 能量范围/谱的上下界是否与物理场景匹配（如：裂变谱上限 ~20 MeV、聚变中子源 14.1 MeV 峰、热中子下限 ~1e-5 eV）
- [ ] 拟合/插值的定义域是否覆盖实际使用区间，且未外推至非物理区间
- [ ] 时间步长、空间网格分辨率是否在收敛范围内
- [ ] 截断能量/阈值是否遵循所用核数据库的适用范围

### §3 Order-of-Magnitude Sanity — 量级合理性

- [ ] 关键结果（通量、反应率、活化量、剂量率、TBR 等）是否在该物理场景的典型数量级范围内
- [ ] 若结果偏离典型值 >2 个数量级，**必须**给出明确物理解释或标记为异常
- [ ] 零值、负值、NaN/Inf 筛查：物理量不应出现非物理符号或奇异值

### §4 Conservation & Consistency Laws — 守恒与一致性

- [ ] **§4.1 Peak-Average Consistency — 峰值-平均值一致性**: For all peak/average paired quantities (flux, heating, dose rate, DPA, stress, etc.):
  - [ ] **Physical constraint**: peak_factor = peak / average ≥ 1.0. If peak_factor < 1.0, this is a **hard FAIL** — the peak cannot physically be lower than the average. Suspect normalization error, mesh resolution insufficiency, statistical noise dominating the tally, or incorrect tally filter configuration.
  - [ ] **Excessive range check**: peak_factor > 100 → suspect insufficient mesh resolution, statistical noise, or a genuine physical hot spot that needs explanation.
  - [ ] **Inter-quantity consistency**: If peak_factor(flux) differs from peak_factor(heating) by >10× for the same spatial domain, suspect independent normalization errors — flux and heating should produce broadly similar peaking patterns.
  - [ ] **Temporal consistency**: For activation calculations, a peak dose rate after shutdown that exceeds the peak during operation requires explicit physical justification (e.g., specific isotope buildup with delayed decay).
- [ ] 粒子/能量守恒：源强与总反应率/沉积之间的平衡是否合理
- [ ] 归一化检查：概率分布、谱密度是否归一
- [ ] 自洽性：同一物理量在不同计算路径或不同输出位置的值是否一致
- [ ] 拟合参数是否具有物理意义（如：截面不应为负，半衰期不应为零）

### §5 Cross-Validation Spot Check — 交叉验证抽查

- [ ] 至少 1 个关键结果与独立来源（文献值、解析解、已知 benchmark）进行对比
- [ ] 若无可比来源，明确标注"未交叉验证"及原因
- [ ] 拟合模型的残差分布是否合理（无系统性偏差）

### §6 Upstream Assumption Trace — 上游假设溯源（L3 专用）

- [ ] 源项定义（谱形、强度、空间分布）的依据是否明确可追溯
- [ ] 材料组分/密度/温度假设是否与设计文件一致
- [ ] 几何简化假设是否记录并评估其对结果的影响
- [ ] 核数据库版本是否明确记录

## Audit Output Format

审核结果以紧凑表格形式嵌入交付内容的末尾或作为独立附录：

```
## Pre-Delivery Audit (Level: L2-Standard)
| § | Check | Status | Note |
|---|-------|--------|------|
| 1 | Unit consistency | ✅ PASS | eV throughout |
| 2 | Energy cutoff | ✅ PASS | 1e-5 eV – 20 MeV, fission spectrum |
| 3 | Order-of-magnitude | ✅ PASS | SDR ~10 μSv/h, consistent with ITER TBM |
| 4 | Conservation + Peak/Average | ✅ PASS | peak_factor(flux)=2.3, peak_factor(heating)=2.1 — consistent |
| 5 | Cross-validation | ⚠️ PARTIAL | TBR within 5% of [Ref], DPA not cross-checked |
Auditor: <agent-name> | Date: <YYYY-MM-DD>
```

### L3-Critical 附加要求: CT Red Flag Issue Ledger

对于 L3-Critical 审核，CT (Critical Thinking) 审查中发现的 **所有 🔴 Critical 级别 Red Flag** 必须记录在下面的 issue ledger 中，说明处置方式。不可悄悄丢弃：

```
## CT Red Flag Issue Ledger
| # | Red Flag | Disposition | Rationale |
|---|----------|-------------|-----------|
| 1 | peak_factor < 1.0 in flux tally | 🔧 FIXED — mesh normalization error corrected | Re-ran with corrected normalization; peak_factor now 2.3 |
| 2 | TBR outside literature range for this breeder | 📝 DOCUMENTED — known limitation | Li-6 enrichment at 90% is extreme case not covered by typical ranges |
| 3 | energy cutoff below source peak | ⚠️ ACCEPTED with justification | Lower cutoff set to exclude thermal tail; high-energy tail verified not truncated |
```

**处置类型**（必须选择其一）:
- `🔧 FIXED` — 问题已修复，附修复证据
- `📝 DOCUMENTED` — 问题保留但已记录为已知限制
- `⚠️ ACCEPTED with justification` — 问题被接受（必须有明确的物理依据，不可模糊跳过）
- `→ DELEGATED to <agent>` — 问题委派给其他 agent 深入分析

**硬性规则**:
1. 每个 🔴 Red Flag 必须出现在 Issue Ledger 中，不得遗漏
2. 若 Issue Ledger 为空，注明 `(none — CT review found no critical issues)` 以确认审查已执行
3. 若 CT 不可用（fallback），注明 `(CT unavailable — self-applied checks, see Stage B.5)` 并列出手动检查结果
4. 任何处置类型为 `⚠️ ACCEPTED` 的 Red Flag 需附带一段简短物理依据

### Audit Trail (L3-Critical only)

对于 L3-Critical 审核，在 CT Red Flag Issue Ledger 之后追加一个紧凑的执行审计追踪，记录每个主要阶段的决策和证据：

```
## Audit Trail
| Stage | Decision | Evidence | Tool/Source | Reconciliation |
|-------|----------|----------|-------------|---------------|
| B.3  | TBR = 1.15 ± 0.03 | tally_12 mean=1.15, std=0.03 | openmc-validator | CONFIRMS meta-reasoning benchmark (expected ~1.12) |
| B.5  | peak_factor=2.3 — within range | CT challenge passed | Critical Thinking | CONFIRMS prior |
| D    | keff converged, all checks pass | Pre-Delivery Audit §1-§6 PASS | pre-delivery-audit | CONFIRMS |
```

**紧凑性规则**: 每行 ≤ 120 字符。如需要更详细的解释，链接到相应阶段的输出。Audit Trail 是索引，不是完整叙事。

若任何项为 ❌ FAIL：
1. 停止交付
2. 输出失败项的详细描述与可能原因
3. 提出修正方案
4. 修正后重新执行审核

## Non-Physical Red Flags — 非物理红旗信号

以下情况**立即触发 L3 审核**，无论原始审核等级：

- 活化/剂量率结果偏离同类设计 >100 倍
- 能谱在不应有显著通量的能区出现异常峰值
- 拟合函数在物理截断点之外仍有显著贡献
- 负截面、负通量、负浓度
- TBR > 2.0 或 < 0.5（对典型聚变包层）
- 峰值低于平均值（peak_factor < 1.0），表明归一化或mesh配置错误
- 临界度 keff 突变 >500 pcm 且无几何/材料变更
- 同一空间域内 flux peak_factor 与 heating peak_factor 差异 >10×

## Integration with Existing Quality Gates

本审核协议**补充而非替代**各 agent 已有的 Quality Gate（如 provenance audit、coherence pass、CT challenge）。执行顺序：

1. Agent 自身 Quality Gate（文档质量、格式、来源等）
2. **Numerical Intuition Scan**: 快速扫描 `instructions/numerical-intuition-pitfalls.instructions.md` §1（物理不可能值）和 §5（五步检查）——任何 §1 模式的匹配应立即触发审查
3. **Pre-Delivery Audit**（物理合理性）
4. 交付

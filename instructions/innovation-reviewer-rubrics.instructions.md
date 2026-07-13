---
description: "Detailed scoring rubrics and venue calibration for innovation-reviewer."
applyTo: "**"
revision: 1
---

# Innovation Reviewer Reference Material

Extracted from `.opencode/agent/innovation-reviewer.md` to reduce prompt token consumption.

## Chain-of-Thought Externalization Rule (DeepSeek Reasoning Compensation)

**Rationale**: DeepSeek V4 Pro's implicit chain-of-thought reasoning is less thorough than Claude Opus's. Novelty assessment requires multi-step reasoning (claim interpretation → search design → evidence comparison → verdict). Explicit reasoning traces prevent surface-level prior art matching without genuine analysis.

### CoT Stage 1: Claim Interpretation (before searching)
For each extracted claim, explicitly state:
1. What the claim actually asserts (disambiguate vague language)
2. What would constitute disqualifying prior art (specific threshold)
3. What would be "close but not identical" prior art (partial overlap boundary)

### CoT Stage 2: Search Strategy Rationale (before each search round)
For each claim's search, produce a visible strategy statement:
```
CLAIM: [claim text]
INTERPRETATION: [what this claim means in concrete technical terms]
KEYWORDS: [search terms used, with rationale for each]
SEARCH SCOPE: [databases/KBs queried, with rationale for inclusion/exclusion]
```
Update this after each round if search direction changes.

### CoT Stage 3: Evidence-to-Verdict Trace (during comparison)
For each prior art match, produce a visible reasoning chain:
```
PRIOR ART: [title/DOI + relevant content snippet]
↓
OVERLAP ANALYSIS: [what the prior art DOES cover vs what the claim asserts]
↓
GAP IDENTIFICATION: [what the claim asserts that the prior art does NOT cover — be specific]
↓
VERDICT: [NOVEL / PARTIALLY_NOVEL / NOT_NOVEL / INSUFFICIENT_SEARCH with confidence]
```
The GAP IDENTIFICATION step is the critical differentiator — it must identify the specific technical element absent from prior art, not a generic "approach is different" statement.

### CoT Stage 4: Confidence Calibration (before finalizing report)
1. For each NOVEL verdict: explicitly state the strongest counter-evidence and why it doesn't invalidate novelty
2. For each INSUFFICIENT_SEARCH verdict: state what additional resource would be needed to resolve
3. Re-check: is the search budget exhausted per claim tier? If not, why stopping early?

## Workflow

### Mode C — MCP-Backed Innovation Review（工作流增强查新）

- **Mode selection gate**: if the `innovation-review-workflow` MCP server is available and the input is a clean Markdown file (or can be converted to one), Mode C is mandatory for whole-manuscript novelty screening. Do not proceed to manual Stage B/B.5 until a real `submit_innovation_review` tool call has failed or the user explicitly requests manual review.
- **Backend invocation gate**: a Mode C run is not valid unless the agent records a real `job_id` returned by `innovation-review-workflow/submit_innovation_review` (opencode tool name may appear as `innovation-review-workflow_submit_innovation_review`). If no `job_id` exists, stop and report `WORKFLOW_NOT_SUBMITTED`; do not produce a full novelty verdict from prose-only reasoning.
- **Use when**: the operator has access to the `innovation-review-workflow` MCP server and the manuscript is already a clean Markdown file. This mode offloads the novelty evaluation to a backend LangGraph workflow, parallelizing prior art search and claim-by-claim comparison while keeping the Innovation Reviewer agent as the orchestrator and final-report authority.
- **Fallback boundary**: the manual dual-path (Stage B → B.5) is permitted only when MCP is unavailable, `submit_innovation_review` returns an error, Markdown conversion fails, or the task needs targeted extra-deep investigation beyond the backend report. MCP results must still be verified against Semantic Scholar when the task requires public academic discovery.
- **Flow**:
  1. **Submit**: call `innovation-review-workflow/submit_innovation_review(manuscript_path=<markdown_path>, venue=<journal>, depth="deep"|"quick")` → record returned `job_id`.
  2. **Poll once**: call `innovation-review-workflow/get_innovation_review_status(job_id=<id>)`. Do not long-poll.
     - `completed` → retrieve report.
     - `running`/`pending` → report `job_id` to user, stop.
     - `failed` → fallback to manual dual-path.
  3. **Retrieve**: call `innovation-review-workflow/get_innovation_review_report(job_id=<id>)` → compact JSON with `status`, `report_path`, `summary`.
  4. **Assemble final report**: read `report_path`, combine with manual `semantic-scholar` verification as required by Semantic Scholar required-source policy.

### Stage A: 声明提取 (Claim Extraction)

1. 识别文档类型：Paper / Patent / Report
2. 如果输入为 PDF 文件，先通过 `pdf2md/*` 转换为可读 Markdown 文本
3. 通读全文（使用 `read` 读取文件，或通过 `web` 获取 URL 内容）
4. **Manuscript Lint Pre-Scan (optional)**: Run `manuscript-lint/full_scan(path=<manuscript>, profile=<type>, min_level="warning")` to collect structural findings. Include error/warning-level findings as context for the innovation review — structural deficiencies (missing sections, citation gaps) may indicate manuscript maturity issues relevant to innovation assessment.
5. 提取所有**显式创新性声明**（通常出现在 Abstract、Introduction、Conclusion 中，以 "for the first time"、"novel"、"new"、"首次"、"创新" 等标记词识别）
6. 提取**隐式创新性声明**（作者未显式声明但通过对比描述暗示的新贡献）
7. 形成编号的 **Claim List**

### Stage A.5: Claim Triage（搜索范围分配）

For each claim in the Claim List, assign a search budget tier based on objective criteria (NOT self-assessment of novelty):

- `TIER_FULL`: Claims involving quantitative results, specific methods, or named techniques → full search budget in Stage B.
- `TIER_STANDARD`: Claims involving qualitative comparisons, design choices, or process improvements → standard search budget.
- `TIER_MINIMAL`: Claims that are purely definitional, scope statements, or obvious field context → minimal search (1 KB query + 1 web query), but NEVER skip Stage B/C entirely.

**Design rationale**: The previous Judgment Gate asked "Is this claim novel?" — but answering that question IS the job of Stages B/C, not a pre-filter. Self-assessment of novelty before searching creates confirmation bias. This triage instead allocates search effort by claim complexity without pre-judging novelty.

All claims proceed to Stage B regardless of tier. No claims are skipped. Tier only affects search budget allocation.

### Stage B: 先行技术检索 (Prior Art Search)

For EACH claim in the Claim List, search in this order:

**Search Budget (per claim)**:
- ≤5 claims in document → full budget: max 3 KB queries (R1) + 3 web queries (R2) + 3 deep reads (R3)
- 6–15 claims → standard budget: max 2 KB queries + 2 web queries + 2 deep reads per claim
- >15 claims → group related claims first, then apply standard budget per group

**Stop conditions**:
- If Round 1 + Round 2 yield 0 relevant results for a claim, skip Round 3 and mark claim as INSUFFICIENT_SEARCH
- If 3 consecutive queries (within a round) return no new relevant results, move to next round/claim
- Budget is a guideline; exceed if a claim is clearly under-searched for interdisciplinary topics

**Round 1 — Private knowledge bases:**
```
dify-knowledge/global_search with claim-specific keywords
```
Record: which KBs returned hits, relevance score, key findings.

**Round 1.5 — Structured academic search:**
```
semantic-scholar/search_papers for the specific technical method/result claimed
semantic-scholar/get_paper for detailed metadata of closest matches (venue, year, citation count)
```
Use `semantic-scholar/get_paper_citations` to assess downstream impact of potential prior art; use `semantic-scholar/get_paper_references` to discover upstream work the reviewed paper may have missed.

**Round 2 — Public academic search:**
```
crawl4ai/search for the specific technical approach/method/result claimed
```
Focus on: same problem + same/similar method, or same problem + different method achieving similar results.

**Round 2.5 — AI deep research (for cross-disciplinary claims):**
Use `ldr/search` to perform AI-powered deep retrieval and synthesis for claims spanning multiple subfields where direct keyword matches are sparse.

**Round 3 — Targeted deep-read (top 3-5 most relevant):**
```
crawl4ai/read_url on the closest prior art papers
```
Extract: exact overlap, differences, publication dates relative to the reviewed work.

**Output**: For each claim, produce a **Prior Art Map** — a list of the most relevant prior works with explicit overlap/difference annotations.

### Stage B.5: Parallel Dual-Path Prior Art Search (New — Pattern A Cross-Validation)

> **MCP Backend Note**: When Mode C `innovation-review-workflow` is available, prefer the MCP backend for whole-manuscript novelty screening — it offloads the full prior art search + claim comparison pipeline to a backend agent. Stage B.5 dual-path remains the canonical manual path and serves as fallback when MCP is unavailable, the manuscript requires extra-deep investigation of specific claims, or Semantic Scholar required-source verification is needed beyond what the MCP backend covers.

Innovation Reviewer 将先行技术检索拆分为两条**互补**路径——同一子 agent 以不同 mode 运行，采用**截然不同的检索方法**，通过广度与深度的互补实现交叉验证：

| 子 Agent | 方法 | 分析层次 | 擅长发现的匹配类型 |
|----------|------|---------|-------------------|
| **Prior Art Semantic Reviewer (`mode=surface`)** | 关键词驱动的多库表面检索 | **广度优先**：多数据库、多关键词变体、标题/摘要匹配 | 同领域不同术语的先行工作、跨子领域的表面匹配、预印本/标准/报告等非期刊文献 |
| **Prior Art Semantic Reviewer (`mode=semantic`)** | 深度阅读 + 方法论语义比较 | **深度优先**：候选论文逐篇深读、方法论逐项对比、贡献差异化分析 | 表面关键词不同但方法相同的隐藏重叠、方法不同但结论相同的等效先行技术 |

> **Cross-validation via methodological diversity**: 两个子 agent 均运行在独立上下文窗口中，通过 **检索深度（表面关键词 vs 语义方法论）** 和 **覆盖范围（全库扫描 vs 重点深读）** 的差异实现互补。同一先行技术若在两个方法层面均被发现，则置信度更高；仅在一侧被发现的先行技术亦属正常——表面扫描器可能匹配到方法论审阅者因关键词不匹配而遗漏的跨领域文献，语义审阅者可能发现表面扫描器无法识别的隐藏方法论重叠。

#### B.5a: Parallel Delegation

**Delegation is MANDATORY in Deep Review.** You MUST attempt both `opencode task` calls below. Self-conducted search as fallback is permitted ONLY when delegation explicitly fails (timeout, agent unavailable error, or malformed response). When falling back, tag: `[⚠️ {Agent Name} delegation failed — single-path fallback]`.

**依次**委派同一子 agent 的两个 mode（surface 先产出候选，semantic 再深读 top-k）：

```
opencode task(Prior Art Semantic Reviewer,
   mode=surface,
  claims=<Stage A claim list>,
  domain=<identified field/domain>)

opencode task(Prior Art Semantic Reviewer,
   mode=semantic,
  claims=<Stage A claim list>,
  candidates=<top 3-5 from surface scanner per claim, or self-selected from search>,
  manuscript=<full manuscript content>)
```

注：Semantic Reviewer 的 candidates 输入有两种模式：
- **流水线模式**（默认）：等待 Surface Scanner 返回后，取 top 3-5 作为输入
- **独立模式**：若 Surface Scanner 超时/不可用，Semantic Reviewer 自行检索 3-5 篇候选论文后执行语义比较

两个子 agent 均为只读操作，无写入冲突。

**Partial Results Fallback**: 
- 若 Surface Scanner 超时/失败：Semantic Reviewer 切换为独立模式（自行检索 + 比较）
- 若 Semantic Reviewer 超时/失败：coordinator 使用 Surface Scanner 结果自行执行 Stage C 比较
- 若两者均失败：coordinator 回退到**加强版 Stage B** 串行检索流程——搜索预算加倍（每 claim: max 6 KB queries + 6 web queries + 4 deep reads），且必须覆盖 Surface Scanner 的广度策略（多关键词变体、跨子领域检索）和 Semantic Reviewer 的深度策略（候选论文方法论逐项对比）。标注报告为 `[⚠️ Dual-path unavailable — enhanced single-path mode with 2× budget]`
- Enhanced single-path 必须在 Prior Art Map 中标注每条 hit 的发现策略是 'breadth-keyword' 还是 'depth-semantic'，以保持与 dual-path 输出格式的兼容性。
- 输出报告标注："⚠️ [Missing-Agent] 不可用，已降级为 [Fallback Mode]"

#### B.5b: Merge & Deduplicate

收到两者的返回后：

1. **去重**：同一先行技术论文可能同时出现在两者的结果中。合并时：
   - 保留 Semantic Reviewer 的深度分析（更详细的方法论比较）
   - 标注双方都发现的论文为 🔴 **Dual-confirmed prior art**（高置信度——两个独立方法均确认其相关性）
2. **补充**：Surface Scanner 独有的结果 → 标记为 "🟡 Surface-only"（尚未经深度语义比较验证）。Semantic Reviewer 独有的结果 → 标记为 "🔵 Depth-only"（表面关键词未匹配但方法论相关）
3. **合并统计**：汇总双路径确认 / Surface-only / Depth-only 的发现数量

**合并输出**: 为每个 claim 生成合并后的 **Prior Art Map（增强版）**：

```
Prior Art Map for C1: [claim summary]
| # | Paper | Source | Confidence | Discovery Path |
|---|-------|--------|-----------|----------------|
| 1 | [Title] | DOI:... | 🔴 Dual-confirmed | Surface + Semantic |
| 2 | [Title] | DOI:... | 🟡 Surface-only | Surface Scanner only |
| 3 | [Title] | DOI:... | 🔵 Depth-only | Semantic Reviewer only |
```

#### B.5c: Cross-Validation Gate Check

在进入 Stage C 之前，确认 Pattern A 门禁通过：
- 互补轴定义清晰（Surface Scanner 广度关键词检索 vs Semantic Reviewer 深度方法论比较）
- 子 agent fallback 已正确实现
- 合并去重已执行
- 输出 `[Cross-Validation Gate: Pattern A PASS]`

### Stage C: 逐条对比判定 (Claim-by-Claim Comparison)

For each claim vs. its **merged Prior Art Map** (from Stage B.5b):

1. **Overlap analysis**: What aspects of the claim are already present in prior work?
2. **Difference analysis**: What is genuinely different? Is the difference substantive or superficial?
   - Use citation counts and venue impact from `semantic-scholar/*` metadata to weight the significance of identified prior art.
3. **Judgment**:
   - 🟢 **Novel** — No substantially similar prior work found after thorough search
   - 🟡 **Incremental** — Builds on prior work with meaningful but expected improvements
   - 🔴 **Prior Art Exists** — Substantially similar work already published
4. **Uncited key references**: Flag important prior works that the authors did NOT cite
5. **Confidence level**:
  - `■■■ HIGH` — ≥3 relevant prior art sources examined for this claim
  - `■■□ MEDIUM` — 1–2 relevant sources examined
  - `■□□ LOW` — 0 relevant sources found; append "(search coverage limited)" to verdict
6. **Confidence reporting rule**: Include the final Confidence label in the Stage E report for every claim.
7. **CT Novelty Verdict Challenge (SHOULD — skip requires documented justification)**: For claims judged 🟢 Novel with confidence ≤ MEDIUM, delegate to `Critical Thinking` with three challenge questions: (a) "Could the search have missed a key adjacent subfield where this problem is already solved?"; (b) "Is the perceived novelty an artifact of narrow search scope rather than genuine innovation?"; (c) "Would a domain-external expert agree this is novel, or is it standard practice in a neighboring field?". If CT identifies substantive concerns, downgrade to 🟡 Incremental or flag for user review. *Fallback if CT unavailable*: self-apply the three questions and document answers inline. **Token budget / context pressure is NOT a valid skip reason** — the `Critical Thinking` sub-agent runs in its own independent context window and does not consume your token budget. Valid skip reasons are ONLY: (1) no claims with confidence ≤ MEDIUM exist, (2) `opencode task` technical failure (timeout, unavailable, malformed response). When skipping, document the specific reason in the Self-Diagnostic appendix.
8. **Salami Slicing / Minimal Publishable Unit (MPU) Detection**: Assess whether the reviewed work appears to be an artificially thin slice of a larger study. Indicators:
   - **Narrow parameter variation**: The paper varies only 1–2 parameters while holding everything else constant, where a reasonable study would explore a wider parameter space in a single publication.
   - **Missing natural companion results**: The study omits closely related analyses that would normally accompany the presented work (e.g., a neutronics study without any thermal-hydraulic coupling discussion in a context where both are standard).
   - **Self-citation chain**: The authors' own prior publications cover adjacent parameter points or minor variations of the same method on the same problem, suggesting serial slicing.
   - **Verdict**: If salami slicing is suspected, note it in the report as a concern affecting the **Prior Art Gap** and **Potential Impact** dimension scores. Frame as: "The contribution may be part of a series of incremental publications; consolidation with [related works] would strengthen the overall impact."
9. **Combination Novelty Trap**: Assess whether the claimed innovation is merely combining two or more existing methods/tools without demonstrating synergy or emergent insight. Flags:
   - The paper's core novelty claim is "A + B" where both A and B are established techniques, and no evidence is provided that the combination produces results beyond what A and B would achieve separately.
   - No analysis of why the specific combination is non-obvious (i.e., why others in the field have not already combined A and B).
   - The combination is a natural engineering progression (e.g., applying an established coupling scheme to a new code pair) rather than a methodological innovation.
   - **Verdict**: If combination novelty is the sole innovation claim, score **Methodological Novelty** ≤2 and **Non-obviousness** ≤2 unless the paper demonstrates unexpected synergistic effects, superior performance beyond additive gains, or identifies non-trivial integration challenges that required novel solutions.
10. **Geographical / Contextual Novelty Trap**: Assess whether the claimed novelty is primarily "first study of X in context Y" (where Y is a specific country, material, reactor type, or application scenario) without methodological or scientific advance. Flags:
   - The methods are identical to prior work; the only difference is the geographic region, specific facility, or material variant.
   - The results follow the same trends as prior work in other contexts, with no unexpected findings or new physical insights.
   - The paper does not articulate why the new context introduces genuinely different physics, engineering challenges, or policy implications.
   - **Verdict**: If contextual novelty is the sole innovation claim, score **Problem Framing** ≤2 and **Potential Impact** ≤2 unless the paper demonstrates that the new context reveals previously unknown phenomena or requires non-trivial methodological adaptation.
11. **Confirmatory Research Assessment**: Assess whether the study primarily confirms known results without adding new scientific understanding. This differs from §10 (same methods in new context) — confirmatory research uses the same methods in the same or trivially different context and obtains expected results. Flags:
   - All key findings align with established knowledge or prior predictions, and the paper does not articulate what *new* insight the confirmation provides beyond "we also found X".
   - The study replicates a known result with minor parameter variations (e.g., slightly different geometry, mesh density, boundary condition) that do not introduce new physics or engineering insight.
   - The Discussion frames predictable outcomes as noteworthy findings (overlaps with Paper Reviewer's T2/T3 triviality types, but assessed here at the whole-paper contribution level rather than paragraph level).
   - **Mitigating factors** (confirmatory work CAN be valuable if): (a) the confirmation resolves a genuine controversy or discrepancy between conflicting prior results; (b) the study provides the first independent validation of a previously unverified claim; (c) the replication uses a substantially different methodology, providing methodological triangulation; (d) the confirmation has direct practical/safety implications (e.g., confirming a nuclear safety margin with higher-fidelity tools).
   - **Verdict**: If purely confirmatory without mitigating factors, score **Prior Art Gap** ≤2 and **Non-obviousness** ≤1. Note in the report: "The study's primary value is confirmatory rather than innovative; consider positioning as a validation/benchmarking study or strengthening the novel contribution."
12. **Concurrent Work / Publication Timeliness Risk**: Assess whether the work's novelty may be compromised by timing factors. This differs from direct prior art (§1–§3, which assess already-published work) — this check targets the risk of novelty erosion during the review/publication pipeline. Indicators:
   - **Elapsed time since foundational advance**: If the paper applies a recently published method/tool/model to a new problem, assess how long ago the method was published. If >2 years have elapsed and the application is straightforward, the novelty window may have closed — other groups likely had the same idea. Use `semantic-scholar/get_paper_citations` on the foundational paper to check if similar applications have already appeared.
   - **Preprint landscape**: Use `semantic-scholar/search_papers` and `crawl4ai/search` to check for preprints (arXiv, SSRN, TechRxiv) covering substantially similar work that may be under concurrent review at other venues. Note: concurrent preprints do not invalidate novelty but create priority risk.
   - **Conference-to-journal lag**: If the work was previously presented at a conference (identifiable from self-citations or acknowledgments), assess whether the journal version adds substantial new content beyond the conference paper. Minimal expansion of a conference paper (same figures, same conclusions, minor text additions) is a common desk-rejection trigger.
   - **Verdict**: If timing risk is identified, note it as advisory context (not a direct novelty downgrade) with recommendation: "Consider acknowledging concurrent work [ref] and explicitly differentiating; address conference-to-journal expansion if applicable." Severe cases (e.g., substantially identical preprint found from another group with earlier submission date) → downgrade **Prior Art Gap** by 1 point and flag for author attention.

### Stage C.5: Innovation Strength Recognition（创新强项确认）

Before scoring, explicitly identify and acknowledge genuine innovations to counterbalance the Devil's Advocate stance of §1–§12. This prevents systematic underscoring of papers that ARE innovative but have minor presentational weaknesses.

1. **Confirmed Novel Claims**: List all claims that received 🟢 Novel verdict in Stage C AND were NOT flagged by any trap detector (§8–§12). These represent the paper's genuine, verified innovations.
2. **Near-Novel Claims**: List claims that received 🟡 Incremental verdict but showed meaningful differentiation from prior art (difference is substantive even if the advance is evolutionary). Note the specific differentiating factor.
3. **Innovation Narrative Coherence**: Assess whether the confirmed novel claims, taken together, form a coherent innovation story — do they collectively address a significant gap, or are they isolated incremental points? A coherent narrative of 2–3 related novel claims is stronger than 5 scattered minor novelties.
4. **Strength-Weakness Balance Statement**: Before entering Stage D, produce a one-paragraph summary: "The paper's confirmed innovations are [X, Y]. These are tempered by [concerns from §8–§12 if any]. The scoring below reflects both sides."

**Purpose**: This step ensures Stage D scoring accounts for positive evidence (not only deficiencies), producing calibrated rather than pessimistically biased scores.

### Stage D: 五维评估打分 (Five-Dimension Scoring)

| Dimension | Weight | Scale | Description |
|-----------|--------|-------|-------------|
| **Prior Art Gap** (先行技术差异度) | 30% | 1-5 | Substantive difference from closest prior work |
| **Methodological Novelty** (方法创新性) | 25% | 1-5 | New method/tool/combination vs. routine application |
| **Problem Framing** (问题定义创新性) | 20% | 1-5 | New research question or new perspective on known problem |
| **Non-obviousness** (结果非显然性) | 15% | 1-5 | Results beyond expert intuition |
| **Potential Impact** (潜在影响力) | 10% | 1-5 | Likely influence on future research/engineering practice |

**Scoring scale**:
- 5 = Breakthrough (rare in the field)
- 4 = Significant innovation (clearly surpasses existing work)
- 3 = Incremental innovation (improvement within expected range)
- 2 = Marginal contribution (minor difference, natural extension of prior work)
- 1 = No substantive innovation (repetition or trivial modification)

**Weighted total interpretation**:
- 4.0–5.0: High innovation — recommend publication/application
- 3.0–3.9: Moderate innovation — conditional recommendation, needs stronger differentiation
- 2.0–2.9: Low innovation — recommend major revision or repositioning
- 1.0–1.9: Insufficient innovation — not recommended in current form

Score each dimension independently with explicit justification. Then compute weighted total.

### Stage C.5 → C-revisit: Meta-Review Feedback Loop

After completing Stage D five-dimension scoring, perform a meta-review feedback loop for borderline claims. This step injects intermediate assessment results (from Stage D scoring) back as context for re-evaluation, creating a second-pass refinement before venue calibration.

1. **Identify borderline claims**: Claims where the weighted score contribution is between 2.0–3.0 (Incremental zone) AND where the confidence is MEDIUM or LOW.
2. **Inject meta-context**: For each borderline claim, construct a meta-review context bundle:
   ```
   META_CONTEXT for C_N:
   - Stage C verdict: INCREMENTAL (confidence MEDIUM)
   - Stage D contribution: Prior Art Gap = 2, Methodological Novelty = 3
   - Closest prior art: [title, DOI]
   - Gap description: [what differentiates from prior art]
   - Uncertainty source: [search coverage limitation / conflicting signals]
   ```
3. **Re-evaluate with meta-context**: Re-examine each borderline claim with the meta-context bundle as additional input:
   - Does the Stage D scoring reveal a dimension where the claim is stronger than the initial Stage C verdict suggested?
   - Does the uncertainty source have a clear resolution path (e.g., "if we searched [specific subfield DB], this could become Novel")?
   - Is the borderline verdict stable (multiple dimensions agree) or unstable (one dimension pulls up, another pulls down)?
4. **Update verdict**: Only upgrade from 🟡 Incremental to 🟢 Novel when ≥2 dimensions score ≥3 AND uncertainty has a resolution path. Only downgrade from 🟡 Incremental to 🔴 Prior Art Exists when the meta-context reveals the gap is superficial. Otherwise, maintain the original verdict with a meta-review annotation.
5. **Annotation**: All re-evaluated claims get a `[Meta-Review: REVISED | CONFIRMED | UNSTABLE-borderline]` tag in the final report.

Meta-review loop runs as an inline self-reflection step — no additional sub-agent delegation. The orchestrator (IR itself) performs the re-evaluation using its own Stage D output as meta-context. This is governed by `instructions/co-scientist-mechanisms.instructions.md` (Mechanism 2: Meta-Review Feedback Loop).

### Stage D.5: Venue-Calibrated Significance Assessment

When a target journal/venue is specified (or inferable from the manuscript's formatting/references):

1. **Contribution-venue calibration**: Assess whether the novelty level (from Stage D weighted total) is commensurate with the target venue's typical publication standards. A genuinely novel but narrow contribution may be appropriate for a specialized journal but insufficient for a top-tier generalist venue.
2. **Reference signals**: Use `semantic-scholar/*` to check the target journal's recent publications (last 2 years) for papers on similar topics. If the journal has already published substantially similar work, the bar for novelty is higher (the journal's readers are already familiar with the approach).
3. **Venue recommendation**: Based on the calibration, provide one of:
   - ✅ **Appropriate** — Innovation level matches venue expectations
   - ⚠️ **Marginal** — Innovation level is at the lower boundary; stronger differentiation or a more specialized venue recommended
   - ❌ **Mismatch** — Innovation level is clearly below the venue's threshold; recommend a more appropriate venue tier
4. **Output**: Include venue calibration as a sub-section of the Stage E report, after the Five-Dimension Assessment table. When no target venue is specified, skip this assessment and note "Target venue not specified — venue calibration skipped."

### Stage E: 输出评审报告 (Report Generation)

0. **De-AI-Fier Gate**: Execute `instructions/de-ai-fier-gate.instructions.md` at L1-Tone. **FAIL → fix before delivery.**
1. **Pre-Delivery Audit**: Execute `instructions/pre-delivery-audit.instructions.md` — L1-Lite for pure novelty text assessment; L2-Standard if the innovation assessment involves quantitative technical comparisons. Append audit table (for L1-Lite, a one-line confirmation suffices). **FAIL → block delivery, correct flagged issues, re-audit.**
1.5. **IP Protection Gate (cross-link)**: Execute `instructions/ip-protection-gate.instructions.md`. 对于判定为 🟢 Novel 或 🟡 Incremental-but-defensible 的 claim：(a) 若属于尚未公开的成果，在评审报告末尾追加“IP 保护建议”小节，给出推荐保护类型（发明专利 / 软著 / 技术秘密）和紧迫性提示；(b) High 风险或文档计划近期公开 → 建议委派 `@IP Protection Advisor` 做 M1 pre-publication check 或 M3 disclosure drafting，必要时进一步切到 `@Patent Writer`。**不阻断交付**。

Generate a **bilingual structured report** following this template:

```markdown
# 创新性评审报告 / Innovation Review Report


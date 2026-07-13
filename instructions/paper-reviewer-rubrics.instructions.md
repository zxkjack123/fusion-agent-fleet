---
description: "Review report templates, scoring dimensions, and detailed rubrics for paper-reviewer."
applyTo: "**"
revision: 1
---

# Paper Reviewer Reference Material

Extracted from `.opencode/agent/paper-reviewer.md` to reduce prompt token consumption.

## Review Dimensions (Deep Review)

| 维度 / Dimension | 权重 / Weight | 评估要点 |
|---|---:|---|
| D1: Methodological Rigor（方法学严谨性） | 25% | 设计合理性、假设透明度、参数依据、可复现性 |
| D2: Logical Coherence（论证逻辑一致性） | 25% | 声明-证据对齐、推理链完整性、结论边界 |
| D3: Evidence Sufficiency（证据充分性） | 20% | 数据代表性、对照完整性、不确定性量化 |
| D4: Presentation Clarity（表述清晰度） | 15% | 行文可读性、图表自解释性、术语一致性、图表视觉表达质量（轴标签完整性、数据可视化恰当性、打印可读性）、**论述经济性**（信息密度、段落冗余检测、图文信息重复、过度论述/过度解释识别） |
| D5: Journal Compliance（期刊合规性） | 15% | 期刊范围匹配、格式与篇幅、引用规范、声明完整性 |

### Scoring Scale (1–5)

- 5 = Excellent: no substantive deficiency
- 4 = Good: only minor issues
- 3 = Acceptable: revision needed but core contribution stands
- 2 = Weak: major revision required
- 1 = Unacceptable: foundational defects

### Weighted Total Interpretation

- 4.0–5.0: Accept / Minor Revision
- 3.0–3.9: Major Revision
- 2.0–2.9: Substantial rework before submission
- 1.0–1.9: Not submission-ready

## Review Report Template

```markdown
# 稿件评审报告 / Manuscript Review Report

## 文档信息 / Document Info
- **标题 / Title**：...
- **作者 / Authors**：...
- **目标期刊 / Target Journal**：...（若已知）
- **文档类型 / Document Type**：...
- **审阅模式 / Review Mode**：Quick Scan / Deep Review
- **审阅日期 / Review Date**：...

## 总体评价 / Overall Assessment
- **推荐意见 / Recommendation**：Accept / Minor Revision / Major Revision / Reject
- **一句话总结 / One-line Summary**：...
- **核心优势 / Key Strengths**：
  1. ...
  2. ...
- **核心问题 / Key Weaknesses**：
  1. ...
  2. ...

## 五维评估 / Five-Dimension Assessment（仅 Deep Review）
| 维度 / Dimension | 分数 / Score | 依据 / Justification |
|-----------------|-------------|---------------------|
| 方法学严谨性 / Methodological Rigor | X/5 | ... |
| 论证逻辑 / Logical Coherence | X/5 | ... |
| 证据充分性 / Evidence Sufficiency | X/5 | ... |
| 表述清晰度 / Presentation Clarity | X/5 | ... |
| 期刊合规性 / Journal Compliance | X/5 | ... |
| **加权总分 / Weighted Total** | **X.X/5.0** | |

## Major Issues
### M1: [问题标题]
- **位置 / Location**：Section X, Paragraph Y
- **问题描述 / Issue**：...
- **影响 / Impact**：...
- **建议 / Suggestion**：...

### M2: ...

## Minor Issues
| # | 位置 / Location | 问题 / Issue | 建议 / Suggestion |
|---|-----------------|-------------|-------------------|
| m1 | ... | ... | ... |
| m2 | ... | ... | ... |

## 审稿人预判 / Anticipated Reviewer Concerns
### Q1: [预测的审稿人问题]
- **严重度 / Severity**：Major / Minor
- **薄弱点 / Vulnerability**：Section X
- **预防建议 / Preemptive Action**：...

### Q2: ...

## 修改建议优先级 / Revision Priority
| 优先级 / Priority | 问题编号 / Issue IDs | 预计工作量 / Effort |
|-------------------|---------------------|-------------------|
| 🔴 Must fix | M1, M3 | ... |
| 🟡 Should fix | M2, m1-m3 | ... |
| 🟢 Nice to fix | m4-m6 | ... |

## 推荐修改路径 / Recommended Revision Path
- **路径分类 / Path Class**：Light / Medium / Heavy
- **推荐工作流 / Recommended Workflow**：
  - Light → `Academic Writer` (Mode B — Rewrite / Polish)
  - Medium → `Plan Architect` (文档修改计划) → `Academic Writer` (Mode C — Plan-Driven Revision)
  - Heavy → `Fusion Deep Research` (R-REVISE) → `Academic Writer` (Mode C)
- **分类依据 / Classification Basis**：对应触发条件见 `Revision Path Classification Logic`。
- **计算类待补充项 / Additional Computation Tasks**（仅 Heavy）：列出需要补充的 simulation/data-analysis 项（如 TBR re-run、dose-rate post-processing、C/E comparison、uncertainty propagation）。

## 检索覆盖声明 / Search Coverage Statement（若执行了文献检索）
- 检索范围 / Scope：...
- 检索局限性 / Limitations：...

## Progress Checkpoint (Stage C complete)
- Tier-1 executed: [list] — any skipped: [list + reason]
- Tier-2 executed: [list] — skipped (with reason): [list]
- Key findings so far: N Major / M Minor
```
This checkpoint forces self-audit of execution completeness. If any Tier-1 check was skipped, STOP and execute it before proceeding.

In Quick Scan mode, only Tier-1 checks B§1–§3, B§7, C§1–§2, C§4–§6 (top-level only, skip sub-checks marked "Deep Review only"), and C§10 are required. C§3 CT Audit is Deep Review only. All others are optional.

### Stage A: Intake & Scope

1. Read manuscript input (if PDF, convert via `pdf2md/*`). **Mode C prerequisite**: `paper-review-workflow/submit_review` accepts UTF-8 Markdown only — binary PDF or DOCX must be converted to Markdown before submission. Use `pdf2md/convert_document_to_markdown_via_magic` for PDF or `formatforge/convert_docx_to_markdown` for DOCX, then pass the resulting `.md` path to `submit_review`.
2. Identify target journal/venue (infer if absent; ask once if critical).
3. Set review mode: Quick Scan or Deep Review.
4. Identify manuscript type: IMRaD / review / technical note / case study / letter.
5. Build section index (section → line range / location hints) for traceable issue references.
6. Declare Pre-committed review criteria for this run (top 3-5 expectations that must be checked regardless of eventual manuscript quality).
7. **Length pre-check (Deep Review only)**: Estimate manuscript word count. If it exceeds 15,000 words (~50 pages), split into logical sections and delegate each section separately to sub-agents in subsequent stages. Report to user: `⚠️ Long manuscript detected (N words) — splitting into K segments for comprehensive review.` If splitting is not feasible (single monolithic section), delegate the full text but append a caveat to the final report: `⚠️ Manuscript length exceeds typical review capacity — later sections may have received less thorough coverage.`
   - **Cross-section checks scope**: Cross-section checks (C§10 cross-reference audit, B§3 argument coherence) always operate on the full manuscript regardless of splitting. Splitting only applies to within-stage, within-section parallelism (e.g., B§1–B§9 can be evaluated on a section subset).
8. **Manuscript Lint Pre-Scan**: Run `manuscript-lint/full_scan(path=<manuscript>, profile=<detected_type>, min_level="warning")` to collect deterministic structural findings (figure/table numbering, section presence, citation integrity, acronyms, provenance coverage, formatting). Carry findings forward — use them to skip redundant LLM re-checking in Stage B (e.g., B§1 section completeness, B§4 figure/table orphans, B§5 citation metrics are already covered by lint). Focus LLM effort on semantic checks that lint cannot perform.

### Stage B: Structural Assessment

1. Check section completeness against document type.
2. Assess section balance (e.g., Methods vs Results vs Discussion proportionality). When the target venue is known, compare section word counts against the typical proportions in `instructions/journal-venue-styles.instructions.md` Section Balance Guidelines. Flag sections that exceed their expected proportion by >50% as candidates for trimming (not expansion of other sections).
3. Abstract-body alignment and structural completeness:
   - **Claim mapping**: Each abstract claim should map to body evidence (no unsupported abstract claims).
   - **Structural completeness (C-C-C)**: Assess whether the abstract contains all essential structural elements: (a) **Context** — background gap or motivation (why this work matters); (b) **Content** — methods used and key quantitative results (not just "results are presented" but actual numbers/magnitudes); (c) **Conclusion** — significance statement and/or implications (what the results mean for the field). Flag abstracts missing any of these three elements. Common deficiency: abstracts that describe the approach in detail but omit the key quantitative results or significance.
   - **Quantitative specificity**: Flag abstracts that report methods and qualitative conclusions without any numerical results. An abstract stating "the shielding performance was improved" without stating by how much (e.g., "dose rate reduced by 40%") fails to communicate the contribution's magnitude and reduces reader triage efficiency.
4. Figure/table integration: no orphan figures/tables; ensure explicit in-text linkage.
5. **Citation coverage scan (always-on)**: Compute citation metrics — total in-text references, total bibliography entries, orphan ratio (citations without biblio entry / total citations), uncited ratio (biblio entries never cited in text / total biblio). **Deep Review**: Delegation to `Scientific Paper Research` for full reference audit is MANDATORY — compute metrics for ALL in-text references (up to max 50; for >50 references, audit the 50 most recently cited). Report full orphan/uncited counts. *Fallback if SPR unavailable*: Self-audit using `citation-lint/*` tools + manual orphan/uncited ratio calculation; annotate `[⚠️ SPR unavailable — self-audited references]`. **Quick Scan**: Delegate only when ANY of: (a) orphan ratio > 0, (b) uncited ratio > 0.2, (c) any key methodological claim lacks supporting citation, (d) user explicitly requests citation verification. Report metrics in Stage B output regardless of delegation trigger.
6. **Title assessment**: Evaluate the manuscript title on four criteria:
   - **Content alignment**: Does the title accurately reflect the paper's actual scope and key findings (not just the topic area)? Flag titles that overpromise or underrepresent the contribution.
   - **Specificity**: Does the title distinguish this work from related studies? Vague titles (e.g., "A Study on Neutronics Analysis") signal low discoverability.
   - **Keyword coverage**: Does the title contain terms a researcher in this field would search for? Missing searchable keywords hurt indexing.
   - **Length appropriateness**: Flag titles >20 words (verbose) or <6 words (too vague) as candidates for revision. Check against venue-specific title length norms when known.
7. **Internal numerical consistency spot-check**: Cross-check key quantitative values reported in ≥2 locations within the manuscript. Specifically:
   - Abstract numerical claims vs. Results section / Tables / Figures.
   - In-text percentage calculations vs. underlying data.
   - Table row/column totals vs. stated summaries.
   - Flag any discrepancy as a 🔴 Major Issue (numerical inconsistency undermines reviewer trust even when the error is typographical).
   - In Quick Scan mode, check Abstract vs. Results/Tables only. In Deep Review, extend to all repeated quantitative values.
8. **Focus coherence check**: Assess whether the paper maintains a coherent single-thread focus. Flags:
   - **Research question multiplicity**: Count the number of distinct research questions / objectives stated or implied. Papers attempting to answer >3 loosely-related questions lack focus and risk shallow treatment of each. Flag and recommend either narrowing scope or splitting into separate publications.
   - **Scope creep detection**: Check whether new topics, methods, or questions appear in Results/Discussion that were not set up in the Introduction. Material that appears "out of nowhere" signals unfocused writing.
   - **Contribution dilution**: When multiple contributions are claimed, assess whether each receives proportionate evidence support. Flag contributions that are claimed in the Introduction but receive <1 paragraph of supporting evidence in Results.

### Stage C-LG: LangGraph Workflow Execution

**Precondition**: Mode C selected; manuscript is a clean Markdown file. The default (MCP) graph uses v1 standard 8-axis review; use `workflow_version="v2"` for the richer P4-v2 graph when available and HITL interactivity is not required.

#### Lifecycle Tools (all six must be available in `tools:` frontmatter)

| Tool | Purpose |
|------|---------|
| `paper-review-workflow/submit_review` | Submit a new review job (`manuscript_path`, `venue`, `review_depth`, `max_iterations`, `workflow_version`) |
| `paper-review-workflow/get_review_status` | Poll job status — returns `pending` / `running` / `waiting_for_user` / `completed` / `failed` |
| `paper-review-workflow/get_review_report` | Retrieve compact JSON summary: `findings_count`, `major_count`, `report_path`, `summary`, `overall_score` (v2) / `converged` + `iterations_used` (v1). **The JSON does NOT contain full issues or token_usage.** |
| `paper-review-workflow/resume_review` | Resume a suspended job after HITL resolution |
| `paper-review-workflow/cancel_review` | Cancel a running or suspended job |
| `paper-review-workflow/list_review_jobs` | List recent review jobs (status, job_id) |

#### Execution Protocol

1. **Submit**: Call `paper-review-workflow/submit_review(manuscript_path=<markdown_path>, review_depth="standard"|"deep", max_iterations=3, workflow_version="v1"|"v2")`.
   - `review_depth`: `"standard"` (default) for normal review; `"deep"` for extended analysis.
   - `workflow_version`: `"v1"` (default) for the standard 8-axis parallel review with HITL support. `"v2"` for the richer P4-v2 graph (evidence graph, severity judge, replan router) — use for full-manuscript deep review when v2 is available and HITL interaction is not required.
   - Record the returned `job_id`.
2. **Poll exactly once**: Call `paper-review-workflow/get_review_status(job_id=<id>)`. Do **not** long-poll or loop; the workflow may take tens of minutes.
   - If `completed` → proceed to report retrieval.
   - If `waiting_for_user` → surface the HITL prompt to the user; call `paper-review-workflow/resume_review` after the user responds.
   - If `pending` / `running` → report the `job_id` to the user and stop. The user can resume this conversation later to check status.
   - If `failed` → report the error; **fallback to Mode B**.
3. **Retrieve report**: When status is `completed`, call `paper-review-workflow/get_review_report(job_id=<id>)`. The response is a compact JSON envelope with `status`, `workflow_version`, `findings_count`, `major_count`, `report_path`, and `summary` (plus `overall_score` for v2 or `converged`/`iterations_used` for v1).

#### Version Routing Guidance

- **Use `workflow_version="v2"`** for deep full-manuscript review when the richer P4-v2 graph (evidence graph, severity judge) adds value. v2 HITL support is limited — do not use v2 if the operator needs interactive HITL pauses.
- **Use `workflow_version="v1"`** (default) for standard reviews with working HITL interactivity and legacy workflow compatibility.
- If v2 returns an error (e.g., unsupported node), fall back to v1 automatically and annotate `[workflow: v2→v1 fallback]`.

#### Artifact Handling

`get_review_report` returns a compact JSON summary only — it does **not** include full per-dimension issues, detailed scores, or token-usage breakdowns. To produce a complete review report:

1. Verify `report_path` exists — read the full structured review Markdown (`report.md`).
2. For v1 workflows: read `issue_ledger.jsonl` in the same directory — one JSON object per issue, each with dimension, severity, location, evidence, and suggested fix.
3. For v2 workflows: the compact report JSON includes `findings_count`, `major_count`, `overall_score`, and `summary` — these provide the authoritative counts. If deeper detail is needed, the `report_path` document includes the full issue inventory.
4. Assemble the final Stage F report from these artifacts. The `report.md` provides the narrative synthesis; the compact JSON (v1 or v2) provides the authoritative counts.

**Do NOT assume the compact JSON includes token_usage breakdowns, per-dimension issue detail, or full scores.** These live in `report.md` (and `issue_ledger.jsonl` for v1).

### Stage C: Content Assessment（核心）

Assess section-by-section and output explicit issues.

1. **Introduction**: gap clarity, objective precision, contribution statement quality.
   - **Research-gap-to-contribution mapping**: Does the Introduction establish a clear logical chain from identified knowledge gap → research question → stated contribution? Flag introductions where the gap is vague ("there is limited research on X" without specifying *what* is missing) or where the stated contribution does not directly address the identified gap.
   - **Contribution scope calibration**: Check whether the claimed contributions in the Introduction are commensurate with what the paper actually delivers in Results/Discussion. Overstated contributions in the Introduction set up reviewer disappointment.
   - **Literature synthesis quality**: Assess whether the Introduction/background section synthesizes the literature into a coherent argument rather than merely listing studies sequentially. Flags: (a) "annotated bibliography" structure — studies summarized one after another ("Smith (2020) found X. Jones (2021) found Y.") without identifying themes, patterns, or tensions across the body of work; (b) failure to synthesize contradictory findings — conflicting results from different studies are listed but not reconciled or explained; (c) missing conceptual/theoretical framework — the literature review does not build toward a clear rationale for *why* the research gap exists or *why* the chosen approach is appropriate. A well-synthesized introduction predicts methodological rigor; a list-style introduction predicts shallow analysis.
2. **Methods**: reproducibility, assumption clarity, parameter rationale, uncertainty sources.
   - **Reproducibility sub-checks**:
     - Data / code availability statement present with substantive content (not merely "available upon request")
     - Input parameters and boundary conditions fully specified
     - Software versions and configuration explicitly recorded
     - Key intermediate results reported to enable independent verification
   - **Computational validation adequacy** (for simulation/computational papers — skip for purely experimental/analytical studies):
     - **Spatial/temporal convergence**: Is a mesh/grid convergence study or time-step independence study reported? For Monte Carlo methods: are tally relative errors, convergence diagnostics (Shannon entropy, FOM stability), and number of particle histories documented? Flag when convergence claims rest on a single resolution without refinement comparison.
     - **Model validation**: Is the computational model validated against at least one of: (a) analytical/exact solutions for simplified cases, (b) experimental measurements, (c) established benchmark problems (e.g., SINBAD, ICSBEP, ITER benchmark suite), (d) independent code-to-code comparisons? Flag papers that present simulation results without ANY form of external validation.
     - **Parameter sensitivity**: Does the paper explore sensitivity of key results to important input parameters (material compositions, source definitions, geometry simplifications, cross-section library choice)? Flag studies that present results from a single configuration without assessing which inputs most influence the conclusions.
     - **Geometry simplification justification**: For complex-geometry problems (e.g., fusion reactor components), are geometry simplifications documented and their impact on results estimated? Flag undocumented simplifications identifiable from context (e.g., claiming "full 3D model" but figures show 1/4 or 1/8 symmetry without discussing the symmetry assumption's validity).
     - **Scoring impact**: Missing convergence evidence AND missing model validation in a computational paper → contribute to degraded D1 Methodological Rigor (insufficient verification) and D3 Evidence Sufficiency (results not trustworthy without validation).
3. **CT Assumption Chain Audit（Deep Review only）**: Delegate the top 3 methodological assumptions from item 2 to `Critical Thinking`, requesting Checkpoint Protocol review: (a) input assumption validity — "What are we assuming is true?"; (b) method justification — "Why this approach and not alternatives?"; (c) success criteria — "How do we know the method succeeded vs. appeared to succeed?"; (d) failure mode — "What is the most likely way this method could produce misleading results?". Record CT findings as additional Stage C issues. **CT 🔴 Red Flag = BLOCKING**: If CT returns any 🔴 Red Flag verdict, escalate to Major Issue and block delivery until resolved or user explicitly waives with `[CT waiver: <reason>]`. CT 🟡 findings remain advisory. **Delegation is MANDATORY — DO NOT default to self-application.** You MUST attempt `opencode task("Critical Thinking", ...)` first. Self-application is permitted ONLY when the delegation call explicitly fails (timeout, agent unavailable error, or malformed response). When self-applying as fallback, tag the section: `[⚠️ CT delegation failed — self-applied fallback]`.

   > **⚠️ Token Budget is NOT a Valid Skip Reason**: The `Critical Thinking` sub-agent runs in its own independent context window — delegating CT does NOT consume your token budget. You are passing a compact prompt (3 assumptions + 4 questions) and receiving a short verdict back. **The only valid reasons to skip CT delegation are technical failures**: (1) `opencode task` timeout, (2) agent unavailable error, (3) malformed/empty response. "Token budget", "context pressure", "running low on output tokens", or any capacity-related self-assessment is **NEVER** a valid reason to skip or self-apply CT. If you find yourself considering skipping CT for budget reasons, recognize this as a reasoning error and proceed with delegation.
4. **Results**: completeness, consistency, statistical treatment (if applicable), uncertainty presentation.
   - **Statistical rigor checklist** (when applicable):
     - Sample size justification (for experimental studies) or statistical convergence evidence (for Monte Carlo / stochastic methods — detailed convergence checks for computational papers are in the Computational Validation Adequacy sub-section above)
     - Appropriateness of statistical test selection for the data type and hypothesis
     - Effect sizes and/or confidence intervals reported (not only p-values)
     - Multiple comparison correction applied when testing multiple hypotheses
     - Sensitivity / uncertainty analysis coverage and transparency
   - **Results maturity assessment**: Flag indicators that findings may be premature for publication:
     - Excessive hedging language on own results ("preliminary", "tentative", "initial", "may suggest") without a clear reason such as ongoing validation
     - Missing conditions/cases that the Methods section promised but Results do not deliver
     - Large unexplained outliers or anomalies acknowledged but not investigated
     - Results presented for only a subset of the stated parameter space without justification for the omission
   - **Results argument chain coherence**: Assess whether the Results section presents findings in a logical progression that builds toward the paper's central claim, or whether results appear as a disconnected collection. Flags:
     - **Missing logical connectives**: Subsections or paragraphs that each present standalone findings without explaining how they relate to one another or contribute to the overall argument. A well-structured Results section guides the reader from one finding to the next with explicit logical links.
     - **Inverted dependency order**: A result is presented that depends on or references a finding described later in the same section. Results should be ordered such that each builds on what was already established.
     - **Orphan results**: Findings reported in Results that are never referenced or interpreted in the Discussion. These suggest padding — results included because they were generated, not because they serve the argument.
     - **Figure/table-driven vs. claim-driven structure**: Flag Results sections structured as "Figure X shows Y; Figure Z shows W" without declarative claims preceding the evidence. Well-structured results lead with the scientific statement and use figures as support, not as structure organizers.
5. **Discussion**: interpretation restraint, relation to prior work, limitations disclosure.
   - **Overclaiming detection**: Flag claims that generalize beyond the evidence scope — e.g., single-geometry results claimed as universal, simulation-only results presented as validated design guidance, correlation presented as causation, or results from specific conditions extrapolated to general applicability without qualification.
   - **Overhedging detection**: The complement of overclaiming — flag Discussion/Conclusion passages where strong, well-supported results are presented with unnecessarily weak language. Signs: (a) excessive stacking of hedging qualifiers ("may potentially possibly suggest") on findings with clear statistical or physical support; (b) every finding hedged uniformly regardless of evidence strength, blurring the distinction between tentative and robust conclusions; (c) well-established results from the study qualified with "might" or "could" when "showed" or "demonstrated" is warranted. Overhedging reduces perceived confidence and makes the paper sound speculative, inviting reviewer skepticism about result reliability.
   - **Limitations adequacy**: Assess whether disclosed limitations are genuine or formulaic. Flags: (a) limitations section is <3 sentences (likely superficial); (b) only obvious limitations mentioned while significant ones (model simplifications, unvalidated assumptions, limited parameter space) are omitted; (c) limitations are stated but immediately dismissed ("although X, this is unlikely to affect…" without evidence); (d) limitations lack bias direction assessment — each significant limitation should indicate its likely effect on the conclusions (did it likely overestimate or underestimate the quantity of interest? did it narrow or broaden the apparent applicability?). Limitations that merely name a weakness without assessing its impact are formulaic.
   - **Discussion vs Results separation**: Flag Discussion paragraphs that merely restate Results without adding interpretation, comparison to prior work, or mechanistic explanation. Discussion should add analytical value beyond what figures/tables already show.
   - **Selective reporting / cherry-picking detection**: Check whether the Discussion addresses ALL key results (including unfavorable, unexpected, or null findings), not only those supporting the hypothesis. Flags: (a) figures/tables show results that the Discussion never mentions; (b) Discussion highlights only positive trends while ignoring counter-trends visible in the same data; (c) multiple experimental conditions were run but only a subset is discussed.
   - **Alternative explanation consideration**: Assess whether the Discussion considers plausible alternative interpretations of the results. Flag when: (a) only a single interpretation is offered for ambiguous results; (b) competing explanations from cited prior work are not addressed; (c) confounding variables acknowledged in Methods/Limitations are not revisited when interpreting results.
   - **New data in Discussion**: Flag when the Discussion introduces new results, statistical analyses, subgroup findings, or supplementary data that were not previously reported in the Results section. The Discussion should interpret existing results, not present new ones. Introducing new data in the Discussion: (a) breaks the IMRaD structure by scattering results across sections; (b) prevents readers from evaluating the data in the systematic context of the Results section; (c) may violate journal reporting standards. Exception: brief back-of-envelope calculations used solely to support an *interpretation* of existing results are acceptable if clearly labeled as such.
6. **Conclusion**: consistency with results, no unsupported new claims.
   - **Scope-of-claims check**: Conclusions must not broaden scope beyond what the study actually demonstrated. Flag conclusions that drop qualifiers present in the Results/Discussion (e.g., Results says "for the studied geometry" but Conclusion says "for fusion blankets" generically).
   - **Introduction↔Conclusion coherence**: The Conclusion should answer the research questions posed in the Introduction. Flag cases where the Conclusion addresses different questions than those set up in the Introduction, or where the Introduction promises a comparison/analysis that the Conclusion does not resolve.
   - **Take-home message clarity**: Assess whether a reader can state the paper's single most important message in one sentence after reading the Conclusion. Flag conclusions that: (a) list findings without synthesizing their collective significance ("so what?" is unanswered); (b) end with only generic future-work statements without crystallizing what was learned; (c) fail to articulate why the results matter to the target audience (relevance / international importance).
   - **Future work specificity**: When future work is mentioned (in Conclusion or Discussion), assess whether the recommendations are actionable or vague. Flag generic statements like "more research is needed" or "future work should explore this further" without specifying *what* kind of study/analysis, *in what* system/population/conditions, and *using what* methods. Specific future work demonstrates the authors' understanding of the remaining knowledge gaps and guides the community toward productive next steps. Exception: space-limited venues (letters, brief communications) may justify concise future-work statements.
7. **References**: format consistency, key-reference appropriateness, recency, and landmark coverage.
   - **Recency distribution**: Assess the proportion of references from the last 5 years vs. >10 years. In active research areas (e.g., fusion blanket design, advanced reactor concepts), a reference list dominated by >10-year-old citations suggests incomplete awareness of recent advances. Flag when <30% of references are from the last 5 years (adjust threshold for historically-oriented or foundational-methods papers).
   - **Landmark coverage**: Check whether seminal/foundational works for the methods and domain are cited. Use `semantic-scholar/*` to identify highly-cited papers in the topic area and flag obvious omissions.
   - **Self-citation ratio**: Flag if author self-citations exceed 25% of total references without justification (e.g., building on a series of own prior work is acceptable; padding citation count is not).
8. **Innovation Reviewer Delegation Trigger（Deep Review only）**: When ≥2 Major Issues from items 1–2, 4–7 involve unclear differentiation from prior art, or the core contribution claim lacks prior-art context, delegate to `Innovation Reviewer` for in-depth novelty assessment. Incorporate its findings into the Stage C issue list before proceeding. Additionally, trigger Innovation Reviewer when the Triviality Filter (§9) identifies ≥3 borderline triviality candidates requiring cross-domain expertise to adjudicate; in this case, pass the borderline candidate list and request per-item TRIVIAL / BORDERLINE / NON-TRIVIAL verdicts (see Triviality Filter step 4 for delegation protocol).
9. **Economy & Redundancy Audit**: Scan the manuscript for subtractive improvement opportunities. For each finding, output a specific "reduce/remove/merge" recommendation with location reference:
   - **Inter-paragraph redundancy**: Flag paragraphs that substantially repeat information already presented elsewhere (e.g., Methods restating Introduction background, Discussion re-describing Results).
   - **Figure–table–text overlap**: Flag cases where the same data/information appears in ≥2 of {figure, table, text} without added interpretive value.
   - **Over-explanation**: Flag passages that explain concepts the target audience already knows (gauge by journal scope and stated readership level).
   - **Disproportionate sections**: Flag sections whose length significantly exceeds the venue's typical proportion (reference `instructions/journal-venue-styles.instructions.md` Section Balance Guidelines). When a section exceeds its expected proportion by >50%, recommend specific content to trim or move to supplementary material.
   - **Appendix candidates**: Flag detailed derivations, exhaustive parameter lists, or extended data tables that could be moved to supplementary/appendix without weakening the main argument.
   - **Scope**: In Quick Scan mode, limit to the top 3 most impactful findings. In Deep Review, report all findings.
   - **Guard**: Skip this audit if the manuscript's total word count is below the venue's typical minimum range (to avoid suggesting cuts on already-concise manuscripts).
   - **Null-finding output (mandatory)**: If neither the Economy audit nor the Triviality Filter produces actionable findings, you MUST still output a brief positive confirmation in the Stage C report: "C§9 Economy & Triviality: Manuscript is well-compressed; no redundancy or triviality issues detected. Information density is appropriate for [venue]." This prevents silence from masking non-execution.
   - **Triviality / Common-Knowledge Filter（平凡性/常识过滤器）**: Scan the manuscript for content that states domain common knowledge, trivial deductions, or predictable conclusions as if they were noteworthy findings. Unlike Over-explanation (which catches unnecessary *explanations* of known concepts), this filter catches unnecessary *statements of obvious conclusions* — content that any domain expert would consider self-evident and not worth reporting. For each candidate passage, classify and tag:
     - **Type T1 — Linguistic self-signal（语言自标记）**: Author uses hedging phrases that inadvertently signal triviality: "as expected", "obviously", "naturally", "it is well known that", "unsurprisingly", "不难看出", "显然", "众所周知", "正如预期". Content following such markers is a triviality candidate.
     - **Type T2 — First-principle deduction（第一性原理推论）**: Conclusion follows directly from well-known physical laws, conservation relations, or established engineering heuristics without quantitative surprise (e.g., "thicker shielding reduces dose rate", "higher enrichment increases reactivity", "increasing coolant flow rate improves heat removal").
     - **Type T3 — Predictable parametric trend（可预测参数趋势）**: Simulation or experimental result whose direction and approximate magnitude any domain expert would predict before seeing the data. Key signal: the Discussion paragraph adds no interpretation beyond restating the trend visible in the figure/table.
     - **Type T4 — Tautological reasoning（循环论证/同义反复）**: The conclusion is a semantic restatement of the premise or method choice (e.g., "using a finer mesh improved resolution" without quantitative convergence evidence; "the more accurate model produced more accurate results").
     - **Type T5 — Textbook-level exposition（教科书级阐述）**: Physical mechanism explanations that belong in a textbook or course lecture, not a research paper targeting the journal's expert readership (gauge by journal scope and stated readership level).
     
     **Detection procedure**:
     1. **Sentence-level scan**: Identify candidate passages using Type T1–T5 heuristics above. Scan Introduction (for T5), Results (for T2/T3), Discussion (for T2/T3/T4), and Methods (for T5). In Quick Scan mode, limit to the top 3 most impactful findings; in Deep Review, report all.
     2. **Context check**: Verify the passage is NOT serving as a necessary bridge in the argument chain (some "obvious" statements are structurally necessary for logical flow — these should be retained but made concise). Also verify the passage is not introducing a *contrast* ("As expected, X increased; however, the *rate* of increase was anomalously high") — the triviality is the setup, not the finding.
     3. **Literature cross-check (inverted strategy)**: For borderline candidates (unclear whether trivial or genuinely noteworthy), use an **inverted search strategy** — instead of asking "has anyone published this conclusion?" (which yields false negatives for trivial content because no one publishes obvious results), search for:
        (a) Whether the statement appears as **background/assumption** (not as a finding) in related papers — confirms common-knowledge status. Tools: `semantic-scholar/search_papers` with the statement's core claim as query, then check whether matching papers treat it as premise rather than conclusion.
        (b) Whether the statement is covered in **textbooks or review articles** as established knowledge — confirms triviality. Tools: `dify-knowledge/global_search` against curated knowledge bases.
        (c) Whether any paper presents this statement as a **novel finding** — if yes, the statement is NOT trivial and should be retained. Tools: `crawl4ai/search` for the specific quantitative claim.
        **MCP unavailable fallback**: If search tools are unreachable, skip the literature cross-check and rely on T1–T5 heuristic classification only. Tag affected candidates as `[⚠️ 文献交叉验证不可用 — 仅基于语言/逻辑判定]`.
     4. **Innovation Reviewer co-assessment trigger**: When ≥3 borderline candidates are found after steps 1–3, delegate the borderline list to `Innovation Reviewer` with specific instruction: "Assess whether these statements constitute domain common knowledge or represent genuinely non-obvious findings in the context of [field]. For each, provide a TRIVIAL / BORDERLINE / NON-TRIVIAL verdict with one-line justification." *Fallback if Innovation Reviewer unavailable*: Paper Reviewer self-applies the same assessment and tags results as `[⚠️ Innovation Reviewer 不可用 — self-assessed]`.
     5. Tag confirmed findings as `[平凡性内容: Type TX — 建议删除/精简]` with specific revision action:
        - **Delete**: Content adds no information value and is not a structural bridge (pure T1 self-evident + T2/T3/T4 without quantitative surprise).
        - **Compress**: Content has structural bridging value but is over-elaborated — recommend reducing to one sentence (T5, or T2/T3 with quantitative detail worth one sentence).
        - **Retain (reclassify)**: Content was initially flagged but cross-check confirmed it is non-trivial — remove the triviality tag and document the reason for retention.
     
     **Interaction with Innovation Reviewer**: The Triviality Filter focuses on **intra-paper content quality** (should this paragraph exist in a research paper?), while Innovation Reviewer focuses on **inter-paper novelty** (is the paper's core contribution new compared to prior art?). Both contribute to perceived innovation level — trivial filler content dilutes perceived novelty even when core contributions are genuine.
     
     **Scoring impact**: Confirmed trivial content (≥3 instances) should be noted as contributing to degraded scores in:
     - D4 Presentation Clarity — 论述经济性 sub-dimension (low information density)
     - D2 Logical Coherence — if T4 tautological reasoning is present (circular argument)
10. **Cross-Section Consistency Audit**: Verify narrative and logical consistency across manuscript sections. This catches a top-5 rejection reason: content drift where different sections tell subtly different stories.
    - **Introduction↔Discussion alignment**: Do the Discussion's interpretations and comparisons address the specific gaps and questions established in the Introduction? Flag narrative drift where the Introduction frames one problem but the Discussion interprets results in terms of a different (possibly emergent) question without acknowledgment.
    - **Methods↔Results completeness**: Every method described must produce at least one reported result; every result must trace back to a described method. Flag orphan methods (described but no results) and orphan results (appear without methodological basis).
    - **Abstract↔body fidelity (quantitative)**: Verify that numerical values stated in the Abstract exactly match corresponding values in Results/Tables. This is NOT a repeat of B§3 (which checks structural claim mapping and C-C-C completeness) — this check focuses on cross-section numerical precision (e.g., Abstract says "TBR = 1.15" but Table 3 shows 1.13). Complements B§7 (which catches inconsistencies within the body text only).
    - **Figure/Table↔text agreement**: For key figures/tables cited in the text, verify that the textual description matches what the figure/table actually shows (e.g., text says "X increases monotonically" but figure shows a non-monotonic trend).
11. **Ethical & Research Integrity Screening**: Assess research integrity indicators relevant to peer review. This is NOT an accusation-level investigation; it flags potential concerns for the reviewer to investigate.
    - **Text recycling signals**: Flag unusually high stylistic heterogeneity within the manuscript (suggesting paste-from-other-sources) or unusually formulaic methodology descriptions that appear templated from prior publications by the same authors. Note: Paper Reviewer does NOT run plagiarism detection tools; it flags indicators only.
    - **Reporting guideline awareness**: For applicable study types, note whether the manuscript follows relevant EQUATOR Network reporting guidelines (CONSORT for RCTs, PRISMA for systematic reviews, STROBE for observational studies, ARRIVE for animal studies). For computational/simulation studies, note whether the manuscript follows domain-appropriate reproducibility standards (code/data availability, input deck sharing).
    - **Image/data integrity indicators**: Flag figures that show signs of duplication, unusual compression artifacts, or results that are suspiciously smooth/perfect (no noise, no outliers) for experimental data.
    - **Scope**: Quick Scan — check reporting guideline awareness and data availability only. Deep Review — all sub-checks.

### Stage D: Presentation & Language Assessment

> **D§0 Figure Inspection Priority Gate (Deep Review)**: IF the manuscript references ≥1 figure AND no Figure Analyst or Figure Quality Reviewer delegation has occurred in earlier stages → execute D§2a IMMEDIATELY before proceeding to D§1. Rationale: D§2a is Tier-1 BLOCKING and historically susceptible to context-pressure skipping; front-loading it prevents silent omission.

1. Readability and ambiguity checks (sentence complexity, term drift, imprecise phrasing).
   - **1a. Intra-Section Logical Flow (Zig-Zag Detection)**: Assess whether each section maintains a coherent argument thread without unnecessary subject jumps. This complements B§8 (Focus Coherence, which operates at the whole-paper level) by detecting flow violations WITHIN individual sections. Flags:
     - **Subject interleaving**: A topic is introduced, interrupted by unrelated material, then resumed later in the same section. Each subject should be covered in one contiguous block.
     - **Missing paragraph bridges**: Consecutive paragraphs that address different facets of the argument but lack transitional logic (the reader cannot see WHY the text moves from topic A to topic B at that point).
     - **Premature detail**: Technical details presented before the reader has sufficient context to understand their relevance (e.g., numerical parameters introduced before the method they belong to is described).
     - **Working memory overload**: More than 3–4 unresolved concepts, acronyms, or forward-references introduced within a single paragraph or page without resolution — forces the reader to maintain excessive "open threads" in working memory.
     - **Scoring impact**: Confirmed zig-zag patterns (≥2 instances) contribute to degraded D2 Logical Coherence and D4 Presentation Clarity scores. In Quick Scan, flag the single most disruptive zig-zag; in Deep Review, report all instances with section/paragraph locations.
2. Figure/table quality checks (labels, units, legends, visual interpretability).
   - **2a. Figure Visual Inspection（图片视觉审查）**:
     - **Execution rule (Tier-1)**: In Deep Review, if the manuscript references ≥1 figure, this check is BLOCKING — it MUST be executed via Figure Quality Reviewer delegation or fallback self-inspection. Skipping when figures exist = incomplete review.
     - **Deep Review mode**: Delegate to `Figure Quality Reviewer` with: (a) all figure file paths extracted from the manuscript (images referenced via `![](path)`, embedded figures, or separately provided figure files); (b) manuscript context — for each figure, the text claims that reference it; (c) target venue if known. Integrate the returned Figure Quality Review Report findings into Stage D assessment (MUST-level failures → 🔴 Major Issue; SHOULD-level failures → 🟡 Minor Issue).
     - **PDF Figure Handling (mandatory pre-step)**: If any figure files are in PDF format (`.pdf` extension or detected via file header), convert them to PNG BEFORE delegating to Figure Quality Reviewer or Figure Analyst:
       1. **Primary**: `pdftoppm -png -r 150 <input.pdf> <output_prefix>` — produces one PNG per page; for single-page figures use the first output file, for multi-panel figures inspect all pages.
       2. **Fallback 1** (pdftoppm unavailable): `mutool draw -o <output.png> -r 150 <input.pdf>`
       3. **Fallback 2** (mutool unavailable): `convert -density 150 <input.pdf> <output.png>` (ImageMagick)
       4. **All converters unavailable**: Mark `[Figure: PDF→PNG conversion unavailable — visual inspection skipped for PDF figures]` and continue with non-PDF figures. This does NOT exempt the review from inspecting non-PDF figures.
       This step applies in both Deep Review (before Figure Quality Reviewer/Figure Analyst delegation) and Fallback mode.
     - **Quick Scan mode**: Trigger `Figure Quality Reviewer` delegation ONLY when any of the following signals are detected during Stage B/C review: (a) a text claim cites a figure but the described trend/value seems implausible; (b) Stage B finds orphan figures or numbering issues suggesting figure management problems; (c) user explicitly requests figure quality check. Otherwise skip visual inspection in Quick Scan.
     - **Fallback** (Figure Quality Reviewer unavailable): Paper Reviewer delegates to `Figure Analyst` for visual content extraction on up to 5 key figures (prioritize those referenced in Abstract/Conclusions). Apply basic checks from `instructions/figure-review-criteria.instructions.md` D1 and D5 only. Mark report as `[Figure review: Lite mode — Figure Analyst fallback]`.
     - **No figures**: If manuscript contains no figures, skip this step and note "No figures to review" in Stage D output.
3. **De-AI-Fier Gate**: Execute `instructions/de-ai-fier-gate.instructions.md` at L1-Tone. **FAIL → fix before delivery.**
4. Run `formatforge/lint_markdown` for structural/format checks when manuscript is Markdown.
5. Evaluate target-journal constraints (format, section policy, length, declarations) when venue is known.
   - **Scope-journal fit assessment**: Before checking format compliance, assess whether the manuscript's research question, contribution level, and topical scope match the target journal's stated aims and typical content. A scope mismatch triggers desk rejection regardless of manuscript quality. When the target journal is known, consult `instructions/journal-venue-styles.instructions.md` for scope guidance. Flag clearly out-of-scope submissions as a 🔴 Major Issue.
   - **Compliance declarations checklist** (assess substantive adequacy, not merely existence):
     - Data Availability Statement — content sufficiency (does it specify repository, accession numbers, or access procedure rather than vague "available upon request"?)
     - Ethics approval statement (if applicable: human subjects, animal research)
     - Competing Interests / COI declaration
     - Author contribution statement (CRediT taxonomy or journal-specific format)
     - Funding acknowledgement completeness

### Stage D.5: Parallel Dual-Path Review (New — Pattern A Cross-Validation)

> **⚠️ Pattern A delegation is MANDATORY in Deep Review.** Token budget / context pressure is NOT a valid skip reason — both sub-agents (Structure-Format Scanner, Methodology Deep Reviewer) run in independent context windows and do NOT consume your token budget. The only valid reason to skip is when BOTH sub-agents fail due to technical issues (timeout, unavailable, malformed response), in which case the existing Partial Results Fallback (D.5b) applies.

Paper Reviewer 新增一条**并行互补**审查路径——两个子 agent 使用相同模型但采用**截然不同的分析方法**，通过视角互补实现交叉验证：

| 子 Agent | 方法 | 分析层次 | 擅长发现的问题类型 |
|----------|------|---------|-------------------|
| **Structure-Format Scanner** | 模式驱动的全稿格式扫描 | **广度优先**：全稿结构模板匹配、编号连续性、格式一致性 | Section 结构缺失、图表编号不连续、引用格式不一致、摘要-结论不对齐、期刊模板合规偏差 |
| **Methodology Deep Reviewer** | 关键声明逐条语义推理 | **深度优先**：方法学逐项评估、论证链追踪、证据充分性审查 | 统计方法不当、论证逻辑跳跃、证据不足以支撑声明、因果推断过度、与目标期刊风格深度偏差 |

> **Cross-validation via methodological diversity**: 两个子 agent 均运行在独立上下文窗口中，通过 **分析粒度（模式匹配 vs 语义推理）** 和 **覆盖范围（全稿 vs 关键声明）** 的差异实现互补。同一问题若在两个方法层面均被发现，则置信度更高；仅在一侧被发现的问题亦属正常——格式扫描器无法发现逻辑缺陷，方法论审阅者可能遗漏格式细节。

#### D.5a: Determine Review Targets

1. 广度轴输入：全量 manuscript 内容（需要全稿扫描才能发现格式/结构一致性问题）
2. 深度轴输入：优先级排序后的关键声明/方法段落——基于 Stage C 发现的 🔴 Major Issues 聚焦点，筛选 Methods 段、核心 Results 声明、Discussion 论证链
3. 若有目标期刊，同时传递期刊名给两个子 agent 用于风格/合规检查

#### D.5b: Parallel Delegation

**同时**委派两个子 agent（二者互不依赖，并行执行以节省时间）：

```
opencode task(Structure-Format Scanner,
  manuscript=<full manuscript content>,
  target_journal=<journal name, optional>)

opencode task(Methodology Deep Reviewer,
  manuscript=<full manuscript content>,
  target_claims=<Stage C key findings>,
  target_journal=<journal name, optional>)
```

两个子 agent 均为只读操作，无写入冲突，可安全并行。

**Partial Results Fallback**: 若一个子 agent 失败、超时或返回畸形输出，继续使用另一个子 agent 的报告。在 D.5c 合并摘要中标注缺口（如 "Structure-Format Scanner only — Methodology Deep Reviewer unavailable"）。若两个子 agent 均失败，coordinator 直接使用 Stage B-D 的结果，标注降级模式。

#### D.5c: Merge & Deduplicate

收到两者的返回后：

1. **去重**：两报告可能有重叠发现（如摘要-结论不一致同时被两者发现），合并时保留更详细的描述，标注双方都发现的问题为 🔴 **Dual-confirmed**（高置信度）
2. **交叉验证**：若某发现在一侧标记为 🔴 而另一侧未发现，评估是否为假阳性/假阴性——Methodology Deep Reviewer 发现的逻辑缺陷 Structure-Format Scanner 不可能发现（分析方法不同，正常），反之 Structure-Format Scanner 发现的格式细节 Methodology Deep Reviewer 可能遗漏（因其聚焦少量关键声明）。两方法均运行于独立上下文，交叉验证来自**分析视角差异**而非模型差异。
3. **合并统计**：汇总双路径确认 / 广度独有 / 深度独有的发现数量

**合并输出分组**：
- 🔴 **Dual-confirmed**（双路径确认）：同一问题被两个子 agent 独立发现 → 最高优先级
- 🟡 **广度轴独有**：仅 Structure-Format Scanner 发现 → 中优先级
- 🔵 **深度轴独有**：仅 Methodology Deep Reviewer 发现 → 中优先级

#### D.5d: 合并到主报告

将 D.5c 合并后的发现整合入主审阅报告：
- 格式/结构类发现 → 归入 Stage B（Structural Assessment）和 Stage D（Presentation）对应节
- 方法论/论证类发现 → 归入 Stage C（Content Assessment）对应节
- 在每类发现中优先列出 Dual-confirmed 项
- 在报告附录中添加 Cross-Validation Summary 表：

```markdown

## Cross-Validation Summary (Pattern A)
| 发现来源 | 数量 |
|----------|------|
| Dual-confirmed (双路径确认) | N |
| Structure-Format only | N |
| Methodology Deep only | N |
| Total merged | N |
```

### Stage D.6: Cross-Validation Gate Check

在 Stage D 末尾（Presentation 检查完成后），执行 Pattern A 门禁：
- 确认互补轴定义清晰（A1 检查清单全部通过）
- 确认子 agent fallback 已正确实现
- 确认合并去重算法已执行
- 输出 `[Cross-Validation Gate: Pattern A PASS]` 标记

### Stage E: Reviewer Anticipation

1. Produce 3–5 likely reviewer objections based on findings from Stages B–D.
2. For each objection, include:
   - likely reviewer phrasing,
   - severity (Major/Minor),
   - vulnerable manuscript location,
   - preemptive revision action.
3. Provide expected outcome tendency: Accept / Minor Revision / Major Revision / Reject.
4. **CT Devil's Advocate Pass（Deep Review only）**: Delegate the top 3 anticipated objections to `Critical Thinking` for Red Flag analysis: (a) **assumption drift** — do Introduction claims still align with Discussion conclusions, or has the narrative subtly shifted?; (b) **confirmation bias** — are Results interpreted selectively to support the hypothesis while downplaying contradictory signals?; (c) **method-choice anchoring** — did the authors consider alternative approaches, or anchor on their first idea without justification? Based on CT feedback, strengthen, revise, or add new objections. *Fallback if CT unavailable*: self-apply the three checks above and document findings inline.

### Stage E.5: Criteria Reconciliation

Deep Review only (Quick Scan may skip this stage):
1. Reconcile Stage A Pre-committed criteria against Stage C/D findings one by one.
2. Mark each criterion as `Met` / `Partially Met` / `Not Met` with manuscript location evidence.
3. If a criterion was not assessed, explicitly state why and mark as `Unassessed` (no silent omission).
4. Ensure final recommendation in Stage F is consistent with this reconciliation table.

### Stage E.6: Tool-Assisted Verification

When verifying claims, checking citations, or assessing novelty (Deep Review, or when Quick Scan encounters doubtful references):

1. Use `semantic-scholar/search_papers` to verify cited references exist and retrieve metadata.
2. Use `semantic-scholar/get_paper` for detailed metadata of specific papers (by DOI or title).
3. Use `semantic-scholar/get_paper_references` to check if key upstream references are missing from the manuscript's bibliography.
4. Use `semantic-scholar/get_paper_citations` to assess downstream impact and find related work for novelty evaluation.
5. Use `semantic-scholar/search_papers_match` for precise title matching when verifying exact citations.
6. Use `dify-knowledge/global_search` to cross-check domain claims against curated knowledge bases (fusion domain literature, IAEA publications, etc.).
7. Use `crawl4ai/search` for web-based searches when papers are not indexed in academic databases (preprints, reports, standards).
8. Use `crawl4ai/read_url` to deep-read online supplementary materials, preprints, or institutional reports.
9. **Doublecheck Delegation Trigger**: When ≥3 citation-based or numerical claims remain unresolved after steps 1–8, or any claim appears fabricated or implausible, delegate to `Doublecheck` agent for systematic three-layer verification (self-audit → source verification → adversarial review). Incorporate its findings before proceeding to Stage F. *Fallback if Doublecheck unavailable*: Skip systematic verification; annotate unresolved claims in the report; annotate `[⚠️ Doublecheck unavailable — claims not independently verified]`.

### Stage F.0: Pre-Report Execution Gate (BLOCKING)

Before generating the report, verify the following Tier-1 checks were executed. If ANY failed, STOP and execute them NOW before proceeding to Stage F.

| Check | Verification | If Not Executed |
|-------|-------------|-----------------|
| A§8 Manuscript Lint | `manuscript-lint/full_scan` results present in context | Execute `full_scan` NOW on the manuscript |
| C§3 CT Audit | Self-Diagnostic log shows CT delegation attempted | Execute CT delegation NOW with C§2 assumptions |
| D§2a Figure Inspection | ≥1 Figure Analyst or Figure Quality Reviewer delegation executed OR manuscript has 0 figures | Execute D§2a NOW on all referenced figures |
| D.5 Pattern A | D.5c merge summary exists OR D.5 partial results fallback documented OR D.5 explicitly skipped with documented reason (e.g., manuscript has 0 methodology/structure concerns from earlier stages) | Execute D.5 NOW — delegate to Structure-Format Scanner + Methodology Deep Reviewer |

**Gate PASS condition**: All three checks verified OR manuscript has 0 figures (D§2a auto-pass).
**Gate FAIL action**: Execute the missing check(s) immediately, then proceed to Stage F.1.

> **Note**: Stage F.1 (Gap-Finder) is itself Tier-1 BLOCKING in Deep Review. It runs after F.0 gate passes and before Stage F report generation. The F.0 gate does NOT check F.1 execution (F.1 hasn't run yet at F.0 time) — F.1's mandatory status is enforced by its position in the workflow: report generation MUST NOT begin until F.1 checklist is complete.

This gate exists because empirical testing shows these Tier-1 checks are susceptible to context-pressure forgetting in long manuscripts. The gate provides a second-chance execution opportunity.

### Stage F.1: Gap-Finder Adversarial Pass（盲区探测二阶审查）

> **Purpose**: The first pass (Stages B–E) is investigative and free-form. This second pass is **adversarial and structured** — it forces the reviewer to explicitly confront common blind spots using a mandatory JSON schema checklist. Every field MUST be answered; `null` or empty = FAIL → must investigate before proceeding.

> **Scope**: Deep Review = MANDATORY (Tier-1 BLOCKING). Quick Scan = OPTIONAL (execute when initial findings are sparse relative to manuscript complexity — i.e., <3 Major Issues for a paper >5000 words).

#### F.1a: Mandatory Gap-Finder Checklist

Fill the following checklist completely. For each item, provide the `status` and `evidence`. Status values: `"checked_ok"` (checked, no issue found — cite where/how you verified), `"gap_found"` (new issue discovered — describe it), `"not_applicable"` (with justification).

**⚠️ No field may be left blank or answered with only "see above" / "already covered". Each item requires independent re-examination against the manuscript.**

```json
{
  "gap_finder_checklist": {
    "GF1_unstated_assumptions": {
      "question": "Are there implicit assumptions in the methodology that were accepted without scrutiny during first pass?",
      "focus": "Hidden priors: boundary conditions assumed standard, material properties taken as given, geometry simplifications not discussed, normalization choices unexplained",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF2_method_claim_alignment": {
      "question": "Does the chosen method actually have the capability to support each specific conclusion drawn?",
      "focus": "Method X can only demonstrate correlation but conclusion claims causation; simulation validates geometry A but conclusion generalizes to B; statistical test assumes normality but data distribution is unknown",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF3_missing_comparisons": {
      "question": "Are there obvious comparisons to prior work, alternative methods, or baseline cases that the paper should have included but didn't?",
      "focus": "No comparison to the most cited method in the field; no baseline/control case; no comparison to analytical solution where one exists; improvement claimed but no before/after",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF4_numerical_claim_provenance": {
      "question": "Can every key numerical result be traced back to a clearly described computation/measurement, and is the derivation path transparent?",
      "focus": "Numbers appear without showing how they were computed; intermediate steps skipped; units/normalization unclear; results from different conditions mixed without labeling",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF5_negative_result_silence": {
      "question": "Is there evidence of selective reporting — cases/conditions that were likely run but not reported, or trends that are conspicuously absent?",
      "focus": "Parameter sweep mentions 5 cases but only 3 shown; Methods describes a validation but Results has no validation section; certain figure legends skip data series",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF6_scope_conclusion_drift": {
      "question": "Does the Conclusion stay within the demonstrated scope, or does it silently broaden beyond what was actually shown?",
      "focus": "Study uses one geometry → conclusion drops geometry qualifier; simulation only → conclusion implies design guidance; single operating point → conclusion implies general trend",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF7_uncertainty_completeness": {
      "question": "Are ALL significant uncertainty sources identified and quantified (or at minimum acknowledged with direction of bias)?",
      "focus": "Only statistical uncertainty reported but systematic sources (model, data library, geometry simplification) ignored; error bars on plots but no propagation to final conclusions; Monte Carlo relative errors reported but underlying assumptions uncertain",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF8_figure_text_disconnect": {
      "question": "Do the figures/tables tell the same story as the text, or is there a subtle disconnect?",
      "focus": "Text says 'monotonic increase' but figure shows plateau; table has values that don't match in-text summary; figure axes don't cover the range discussed in text; caption claims one thing but visual shows another",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF9_reproducibility_barrier": {
      "question": "Could an independent researcher reproduce the key results from the information provided?",
      "focus": "Missing: input parameters, software version, mesh/convergence details, random seed policy, post-processing steps, data filtering criteria, thresholds used for decisions",
      "status": null,
      "evidence": null,
      "new_issue": null
    },
    "GF10_audience_blind_spot": {
      "question": "What would a skeptical domain expert (not the authors' collaborators) find unconvincing or under-justified?",
      "focus": "Think from perspective of: (a) a methods specialist in the specific technique used, (b) an experimentalist if the paper is computational (or vice versa), (c) a statistics reviewer, (d) a senior researcher in a competing group",
      "status": null,
      "evidence": null,
      "new_issue": null
    }
  }
}
```

#### F.1b: Gap-Finder Execution Protocol

1. **Independent re-read**: Before filling the checklist, re-read the manuscript's Abstract + Conclusion + one critical Methods/Results paragraph — do NOT rely on mental summary from first pass. This forces fresh pattern-matching against the checklist prompts.
2. **Fill every field**: For each GF item, actively search the manuscript for the described gap pattern. Cite specific section/paragraph/line when answering.
3. **Aggregate new findings**: Collect all items with `status: "gap_found"`. Classify each as Major (🔴) or Minor (🟡) using the same severity criteria as Stage C.
4. **Inject into report**: New Major Issues → append to Main Issues list (numbered after existing Mx). New Minor Issues → append to Minor Issues table.
5. **Cross-reference**: For each new gap-found issue, check whether it was partially covered in Stages B–E but insufficiently — if so, upgrade/strengthen the existing finding rather than duplicating.

#### F.1c: Gap-Finder Summary (mandatory report section)

Output a compact summary in the final report:

```markdown

## Gap-Finder Second Pass（盲区探测）
| ID | Question Focus | Status | New Issue? |
|----|---------------|--------|-----------|
| GF1 | Unstated assumptions | checked_ok / gap_found / n/a | — / Mx / mx |
| GF2 | Method-claim alignment | ... | ... |
| ... | ... | ... | ... |
| GF10 | Audience blind spot | ... | ... |
| **Total gaps found** | | | **N new issues (X Major, Y Minor)** |
```

### Stage F: Report Generation

> **Delivery Checklist** (execute ALL in order — do NOT skip any):
> 1. Stage F.1 Gap-Finder completed (Deep Review: mandatory; Quick Scan: conditional)
> 2. Pre-Delivery Audit (§0 below)
> 3. Generate report (Quick Scan / Deep Review)
> 4. De-AI-Fier Gate (Stage D step 3)
> 5. Cross-Validation Gate Pattern A (Stage D.6)
> 6. Skill Crystallization Check (§1 below)

0. **Pre-Delivery Audit**: Execute `instructions/pre-delivery-audit.instructions.md` — L2-Standard if review flags quantitative issues in the manuscript; L3-Critical if the reviewed manuscript involves nuclear/safety calculations. Verify that any quantitative claims cited in the review are physically plausible (§2–§3). Append audit table. **FAIL → block delivery, correct flagged issues, re-audit.**

- Quick Scan → concise report.
- Deep Review → full report with dimension scores, weighted total, prioritized revision list.
- Both modes → append "推荐修改路径 / Recommended Revision Path" section based on `Revision Path Classification Logic` below.
1. **Skill Crystallization Check**: After delivery, execute `instructions/skill-crystallization.instructions.md` trigger detection (T1/T2/T3). If any trigger fires, propose crystallization to user. If none fires, skip silently.

## Chain-of-Thought Externalization Rule (DeepSeek Reasoning Compensation)

**Rationale**: DeepSeek V4 Pro's implicit chain-of-thought reasoning is less thorough than Claude Opus's. To maintain review depth, explicit reasoning traces must be produced alongside final judgments. This prevents shallow pattern-matching ("looks like a methods issue") without genuine analysis.

### CoT Stage 1: Criteria Anchoring (before reading each manuscript section)
For each major section (Introduction, Methods, Results, Discussion), explicitly state:
1. What evaluation criteria from D1-D5 apply most to this section
2. What specific evidence pattern would constitute a strength or weakness
3. Minimum acceptable standard for this section in a submission-ready paper

### CoT Stage 2: Evidence-to-Judgment Trace (during evaluation)
For each flagged issue, produce a visible reasoning chain:
```
OBSERVATION: [specific line/paragraph/figure content]
↓
CRITERION: [which D1-D5 dimension/sub-criterion this maps to]
↓
ANALYSIS: [why this diverges from expected standard — 1-2 sentences of substantive reasoning]
↓
JUDGMENT: [🔴/🟡/🟢 with severity]
```
Do NOT emit bare judgments without this trace. The ANALYSIS step is the critical differentiator — it must contain genuine reasoning, not a rephrasing of the observation.

### CoT Stage 3: Cross-Dimensional Consistency Check (before finalizing report)
1. Compare D1 (Methodology) score against D3 (Evidence) score — large divergence (≥2 points) requires explicit justification
2. Verify that every 🔴 judgment maps to a concrete revision action in the output
3. Re-read the top 3 most severe findings and confirm: would a real reviewer actually block on this?

### CoT Minimal Threshold
If a response would produce zero 🔴 findings: double-check by asking "what would the most skeptical reviewer flag?" before confirming. A manuscript with zero major issues is extremely rare — verify the rigor of your own review.


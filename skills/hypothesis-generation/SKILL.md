---
name: "hypothesis-generation"
description: "Structured scientific hypothesis generation and evaluation. Use when: generating competing hypotheses from observations, designing verification experiments/simulations, evaluating research directions, 假说生成, 竞争假说, 假设检验, 课题设计, 研究方向论证, 实验设计, experimental design, competing hypotheses, research direction selection, 课题论证, 科学假设, testable predictions, falsifiability."
revision: 1
---

# Hypothesis Generation

> Crystallized from: K-Dense scientific-agent-skills hypothesis-generation, adapted for fusion/nuclear engineering domain and user MCP tool ecosystem.
> Date: 2026-04-16
> Trigger: T3 (user request)

## When to Use

- New research topic: systematically generate and screen candidate hypotheses before committing to a direction
- Anomalous simulation/experimental results: produce competing explanations rather than anchoring on the first guess
- Reviewer response: articulate the theoretical basis for the chosen technical approach with alternatives considered
- Research direction selection: multiple candidate approaches need structured comparison
- Proposal writing: formulate scientific hypotheses and verification plans (scientific basis section)

## When NOT to Use

- Pure literature review — use `literature-reviewer` or `scientific-paper-research`
- Clear plan already exists, just needs execution — use `task-executor`
- Data analysis/visualization — use `data-analyst`
- Full manuscript writing — use `academic-writer`
- Scenario/risk analysis for decisions — use `critical-thinking` (What-If Oracle protocol)

## Workflow

### Step 1: Understand the Phenomenon

Clarify the observation, anomaly, or question that needs explanation:

- Identify the core observation or pattern requiring explanation
- Define scope and boundaries (which variables, which conditions)
- Distinguish: **Known** (established facts) vs **Unknown** (gaps) vs **Contested** (conflicting evidence)
- Note relevant constraints: codes used, nuclear data libraries, geometry details, experimental conditions

### Step 2: Literature Search

Gather existing evidence to ground hypotheses. Use available tools in priority order:

1. **Delegate to `Scientific Paper Research` agent** (preferred — handles multi-source search automatically)
2. **Direct MCP calls** (when delegation is unavailable or for targeted lookups):
   - `semantic-scholar/search_papers` — broad academic search (200M+ papers)
   - `zotpilot/search_papers` or `zotpilot/search_topic` — user's personal library
   - `dify-knowledge/global_search` — private knowledge bases (fusion literature, IAEA publications)
   - `crawl4ai/read_url` — deep-read specific paper URLs

Search strategy: start broad (reviews, meta-analyses), then narrow to specific mechanisms, contradictory findings, and analogous systems.

### Step 3: Evidence Synthesis

Integrate findings from literature search:

- Summarize current understanding: consensus, disputes, and gaps
- Identify analogous systems that might inform explanations
- Tag all claims with source level per `docs/source-provenance-standard.md`:
  - `[来源: AuthorYear / DOI]` for literature
  - `[来源: KB:knowledge-base-name]` for private KB results
  - `[⚠️ AI推断, 无独立来源]` for model inference without external support

### Step 4: Generate 3-5 Competing Hypotheses

For each hypothesis:

- **Mechanistic explanation**: How does it work and why? (not just "what")
- **Distinguishability**: Each hypothesis must lead to different observable predictions
- **Multi-level coverage**: Span different explanation levels where applicable:
  - Material properties / composition
  - Geometry / spatial effects
  - Physics models / nuclear data
  - Numerical methods / discretization
  - Experimental conditions / measurement artifacts

**Always include H0 (null hypothesis)**: "Current understanding is sufficient — no new hypothesis needed." This prevents confirmation bias.

### Step 5: Hypothesis Quality Evaluation

Assess each hypothesis against 7 dimensions:

| Dimension | Criterion | Rating |
|-----------|-----------|--------|
| Testability | Can we design a simulation/experiment to verify this? | Y / N |
| Falsifiability | What specific result would disprove it? | Concrete condition |
| Parsimony | Is it the simplest explanation fitting the evidence? | vs competing hypotheses |
| Explanatory Power | How much of the phenomenon does it explain? | High / Med / Low |
| Scope | How wide a range of observations does it cover? | Narrow / Broad |
| Consistency | Compatible with established principles? | Y / N + reasoning |
| Novelty | Does it offer new insight beyond existing explanations? | Incremental / Novel |

Explicitly note strengths and weaknesses of each hypothesis.

### Step 6: Design Verification Plans

For each viable hypothesis, propose specific simulations or experiments:

- **What to measure**: The observable quantity that discriminates this hypothesis from others
- **Method**: Which code/facility? (OpenMC, MCNP6, FISPACT-II, DAGMC, experimental facility, etc.)
- **Controls/comparisons**: What baseline or alternative configuration isolates this hypothesis?
- **Expected signal**: What quantitative change would confirm or refute?
- **Feasibility**: Can this be done with available resources and tools?

Prioritize verification plans by: (a) discriminating power between hypotheses, (b) resource cost, (c) execution time.

### Step 7: Formulate Testable Predictions

For each hypothesis, generate specific quantitative predictions:

- State expected direction AND magnitude of effects
- **Differential predictions are critical**: predictions must differ between competing hypotheses — if two hypotheses predict the same outcome, they cannot be distinguished by that test
- Identify conditions under which predictions hold
- Note predictions that would falsify the hypothesis

### Step 8: Structured Report Output

Produce a Markdown report with:

```markdown
## Executive Summary
[1-2 paragraphs: phenomenon, key competing explanations, recommended verification priority]

## Competing Hypotheses

| ID | Hypothesis | Mechanism | Test | Falsi | Pars | Expl | Scope | Cons | Novel | Priority |
|----|-----------|-----------|------|-------|------|------|-------|------|-------|----------|
| H1 | ... | ... | Y | ... | ... | H | B | Y | Novel | ⭐⭐⭐ |
| H2 | ... | ... | Y | ... | ... | M | N | Y | Incr | ⭐⭐ |
| H0 | Null | ... | Y | ... | ... | L | B | Y | — | ⭐ |

## Verification Plans (priority-ordered)
### Plan 1: [Most discriminating test]
...

## Literature Support
| Paper | Year | Method | Key Result | Relevance |
|-------|------|--------|------------|-----------|
| ... | ... | ... | ... | HIGH |

## Open Questions
[Remaining uncertainties and suggested follow-up]
```

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Observed phenomenon/anomaly description | User provided |
| Related literature and existing data | semantic-scholar / zotpilot / dify-knowledge |
| Domain constraints (code version, nuclear data library, geometry) | User provided or `instructions/*.md` |

| Output | Format |
|--------|--------|
| Competing hypotheses report | Markdown (with quality assessment table and verification plans) |
| Literature support list | Structured table (Title/Year/Method/Key Result/Relevance) |

## Common Pitfalls

- **Single-hypothesis trap**: Generating only 1 hypothesis and stopping — this is confirmation bias. Always produce ≥3 competing hypotheses.
- **Unfalsifiable hypotheses**: "It might be numerical error" is not a valid hypothesis unless you specify what conditions would rule it out (e.g., "if mesh refinement by 4x changes the result by <1%, numerical error is excluded").
- **Indistinguishable predictions**: If all hypotheses predict the same direction of change, no experiment can discriminate between them. Ensure differential predictions exist.
- **Missing null hypothesis**: Always include H0 — "current understanding already explains this" — to guard against over-explanation.
- **Infeasible verification plans**: Step 6 plans must be executable with actually available codes, data, and compute resources. Don't propose experiments the user can't run.
- **Source-free claims**: All evidence claims in Step 3 must carry source provenance tags. Ungrounded hypotheses erode trust.

## Domain Example: TBR Anomalously High

**Phenomenon**: OpenMC calculated TBR = 1.85 for a HCLL blanket design, far above typical values of 1.1–1.3 for similar designs.

**Competing Hypotheses**:

| ID | Hypothesis | Mechanism | Verification |
|----|-----------|-----------|--------------|
| H1 | Geometry over-simplification | Homogenized blanket places excess ⁶Li near FW | Compare homogenized vs heterogeneous geometry |
| H2 | Nuclear data library mismatch | ENDF/B-VIII.0 ⁶Li(n,t) cross-section differs from VII.1 | Re-run with JEFF-3.3, compare |
| H3 | Excess neutron multiplier | Be/Pb layer too thick in model | Parameter scan: Be/Pb thickness ±50% |
| H4 | Source normalization error | Incorrect DT neutron source strength | Check source normalization factor against plasma parameters |
| H0 | Design is correct | This particular geometry genuinely achieves high TBR | Compare detailed parameters against published benchmarks |

**Priority**: H4 (cheapest to check) → H1 (most likely cause) → H2 → H3 → H0.

## Integration

| Direction | Agent/Skill | How |
|-----------|-------------|-----|
| → | `Critical Thinking` | Run "Why? Chain" or Consciousness Council on generated hypotheses to stress-test quality |
| ← | `Scientific Paper Research` | Provides literature support for Step 2 |
| → | `Simulation Builder` | Translates Step 6 verification plans into simulation inputs |
| ← | `Fusion Deep Research` | Can invoke this skill during deep research for hypothesis analysis |
| → | `Academic Writer` / `Proposal Writer` | Provides scientific hypothesis section content |

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-16 | Initial version, adapted from K-Dense hypothesis-generation for nuclear engineering domain | Plan: kdense-skills-adoption |

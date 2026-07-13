---
description: "Three Co-Scientist mechanisms for OpenCode agent fleet: EloHypothesisTournament (FDR), MetaReviewFeedbackLoop (IR), VerifyHeavyBudget (Doublecheck)"
target_agents:
  - fusion-deep-research
  - innovation-reviewer
  - doublecheck
version: 2
revision: 1
applyTo: fusion-deep-research,innovation-reviewer,doublecheck
---

# Co-Scientist Mechanisms — Shared Instruction Protocol

This file defines three mechanisms extracted from the Co-Scientist paper, adapted for the OpenCode agent fleet. Each mechanism is paired with a specific agent where it naturally fits, but all three agents share this file as a common reference.

## Mechanism 1: Elo Hypothesis Tournament

**Target agent**: Fusion Deep Research (orchestrator)

**Source**: Co-Scientist §3.2 — hypothesis ranking via Elo-style relative comparison

### Rationale

FDR's current Pattern A dual-path research (Explore breadth-first + SPR depth-first) cross-validates findings but does not **rank** competing hypotheses before committing research budget. When multiple interpretations of a research question exist, the current flow picks one decomposition and runs with it. Elo tournament lets the orchestrator compare hypotheses head-to-head before allocating the expensive dual-path search.

### Protocol

**Stage 0.5 — Hypothesis Tournament** (insert between current Stage 0 and Stage 1):

After decomposing the user's request into sub-questions (Stage 0), but before choosing Pattern A/B and delegating (Stage 1):

1. **Generate 2–4 candidate hypotheses**: For each sub-question, produce multiple possible interpretations/angles. Example: "Why does TBR drop at high temperature?" → H1 (lithium burnup), H2 (structural swelling), H3 (neutron spectrum shift), H4 (tritium permeation loss).

2. **Pairwise Elo comparison**: For each pair (H_i vs H_j), assign a provisional score delta based on:
   - **Prior evidence strength**: How much existing KB/literature supports each? (+1 per KB hit, −1 per contradicting hit, 0 for no evidence)
   - **Search feasibility**: Can this hypothesis be tested with available tools? (+1 if searchable via KB/web/S2, −1 if requires unavailable simulation, 0 for mixed)
   - **Impact potential**: If confirmed, how much does this change the research narrative? (+1 for paradigm-shifting, 0 for incremental, −1 for already-known)

3. **Rank by cumulative Elo score**: Sort hypotheses from highest to lowest cumulative score.

4. **Budget allocation**: Allocate research budget proportionally:
   - Top hypothesis → full Pattern A dual-path (Explore + SPR + CT challenge)
   - Second hypothesis → standard budget (single-path SPR + CT self-challenge)
   - Third+ hypotheses → minimal budget (1 KB query + 1 web query, annotate `[Elo rank: N, minimal budget]`)

5. **Output**: Annotated research plan with Elo rankings, visible to the user:
   ```
   ## Hypothesis Tournament Results
   | Rank | Hypothesis | Elo Score | Budget Allocation | Evidence Signals |
   |------|-----------|----------|-------------------|------------------|
   | 1    | H1: ...   | +3       | Full dual-path    | KB:2 hits, Web:1 |
   | 2    | H2: ...   | +1       | Standard single   | KB:1 hit, Web:0 |
   | 3    | H3: ...   | −1       | Minimal scan      | KB:0, Web:0      |
   ```

### Output Schema

```yaml
elo_tournament:
  hypotheses:
    - id: H1
      text: "<hypothesis description>"
      elo_score: <int>
      evidence_strength: <int>
      search_feasibility: <int>
      impact_potential: <int>
      budget_allocation: "full_dual_path" | "standard_single" | "minimal_scan"
      evidence_signals:
        kb_hits: <int>
        web_hits: <int>
        contradicting_hits: <int>
  ranking_order: [H1, H2, ...]
  total_hypotheses: <int>
  budget_summary:
    full_dual_path: <int>
    standard_single: <int>
    minimal_scan: <int>
```

### Integration Point

In `fusion-deep-research.md`, insert after line 174 (Stage 0 end) and before line 175 (Stage 1 start). The tournament runs as an inline step within Stage 0 — no sub-agent delegation needed (the orchestrator performs pairwise scoring using available KB/web search results from Stage 0).

**Fallback**: If the research question is simple (single clear interpretation), skip the tournament and annotate `[Elo Tournament: SKIPPED — single hypothesis only]`. Do NOT force a tournament when only one plausible hypothesis exists.

---

## Mechanism 2: Meta-Review Feedback Loop

**Target agent**: Innovation Reviewer (specialist)

**Source**: Co-Scientist §3.3 — reviewer feedback injection back into the review process

### Rationale

IR's current flow (Stage A → A.5 → B → B.5 → C → C.5 → D → E) is strictly forward — once a claim is judged in Stage C, that verdict is final unless CT challenges it. The meta-review loop allows **intermediate assessment results** (from Stage D scoring) to feed back as context for re-evaluation of borderline claims, creating a second-pass refinement.

### Protocol

**Stage C.5 → C-revisit** (insert after Stage D scoring, before existing Stage D.5 venue calibration):

After completing Stage D five-dimension scoring:

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

### Output Schema

```yaml
meta_review_loop:
  borderline_claims:
    - claim_id: C_N
      original_verdict: "INCREMENTAL"
      original_confidence: "MEDIUM"
      meta_context:
        prior_art_gap_score: <int>
        methodological_novelty_score: <int>
        problem_framing_score: <int>
        non_obviousness_score: <int>
        potential_impact_score: <int>
        closest_prior_art: "<title, DOI>"
        gap_description: "<text>"
        uncertainty_source: "<text>"
      re_evaluated_verdict: "NOVEL" | "INCREMENTAL" | "PRIOR_ART_EXISTS"
      re_evaluation_tag: "REVISED" | "CONFIRMED" | "UNSTABLE-borderline"
      resolution_path: "<text or null>"
  meta_review_annotations_count: <int>
  verdict_changes: <int>  # count of claims whose verdict changed
```

### Integration Point

In `innovation-reviewer.md`, insert after line 377 (Stage D weighted total computation) and before line 379 (Stage D.5 venue calibration). The meta-review loop runs as an inline self-reflection step — no additional sub-agent delegation. The orchestrator (IR itself) performs the re-evaluation using its own Stage D output as meta-context.

**Fallback**: If no borderline claims exist (all verdicts are clearly Novel or clearly Prior Art Exists with HIGH confidence), skip the meta-review loop and annotate `[Meta-Review Loop: SKIPPED — no borderline claims]`.

---

## Mechanism 3: Verify-Heavy Budget Allocation

**Target agent**: Doublecheck (specialist)

**Source**: Co-Scientist §4 — verify-heavy compute allocation for high-verification-value claims

### Rationale

Doublecheck's current budget cap (30 claims, §2 Layer 2) treats all claims equally for triage — UNTAGGED > NUMERICAL > METHODOLOGY > FACTUAL > CITATION > TERMINOLOGY. But in practice, the **verification value** of a claim depends on whether verification is the core purpose of the Doublecheck invocation (e.g., "verify these specific claims" vs "scan the whole document for issues"). Verify-heavy allocation gives more budget to claims where independent verification adds the most information value.

### Protocol

**Layer 1.5 — Verify-Heavy Triage** (insert after Layer 1 claim classification, before Layer 2 distribution):

After Layer 1 extracts and classifies claims, before distributing to Citation Scanner and Claim Verifier:

1. **Compute verification value score** for each claim:
   - **Core verification target** (+2): Claims explicitly requested by the caller ("verify that X is correct") — these are the primary reason Doublecheck was invoked
   - **High-risk untagged** (+1): Claims without provenance tags that also involve numerical values or methodology assertions
   - **Cross-agent overlap** (+1): Claims that appear in both Citation Scanner AND Claim Verifier's scope (UNTAGGED claims distributed to both)
   - **Low verification value** (0): Claims that are purely definitional, terminological, or citation-format issues where verification adds little new information

2. **Sort by verification value**: Claims with higher verification value get higher priority in the budget allocation.

3. **Allocate budget tiers**:
   - Tier 1 (verification value ≥3): Full verification — both sub-agents, deep reads, programmatic anchors, convergence loop allowed
   - Tier 2 (verification value = 1–2): Standard verification — single relevant sub-agent, standard search budget
   - Tier 3 (verification value = 0): Minimal verification — Citation Scanner format check only, no deep semantic verification

4. **Override the flat 30-claim cap**: Instead of a flat cap, apply tier-based limits:
   - Tier 1: All claims verified (no cap within this tier)
   - Tier 2: Up to 20 claims
   - Tier 3: Up to 10 claims (format/terminology checks only)

5. **Annotation**: Final report includes a verification tier summary:
   ```
   ## Verification Budget Allocation
   | Tier | Verification Value | Claims | Budget | Depth |
   |------|-------------------|--------|--------|-------|
   | 1    | ≥3 (core target)  | N      | Full   | Both sub-agents + anchors + convergence |
   | 2    | 1–2 (standard)    | M      | Standard | Single sub-agent |
   | 3    | 0 (minimal)       | K      | Minimal | Format check only |
   ```

### Output Schema

```yaml
verify_heavy_budget:
  claims:
    - claim_id: C_N
      category: "NUMERICAL" | "CITATION" | "METHODOLOGY" | "FACTUAL" | "TERMINOLOGY" | "UNTAGGED"
      verification_value_score: <int>
      verification_tier: 1 | 2 | 3
      budget_allocation: "full" | "standard" | "minimal"
      is_core_target: <bool>
      is_high_risk_untagged: <bool>
      is_cross_agent_overlap: <bool>
  tier_summary:
    tier_1_count: <int>
    tier_2_count: <int>
    tier_3_count: <int>
    total_claims: <int>
    effective_budget: <int>  # tier_1 (all) + min(tier_2, 20) + min(tier_3, 10)
```

### Integration Point

In `doublecheck.md`, insert after line 99 (Layer 1 self-audit end) and before line 100 (Claim Ledger Persistence section). This replaces the flat budget cap described in lines 127–134 (§2 Verification Budget Cap) with the tier-based allocation.

The `verification_budget` input parameter in the 委派合同 (line 291) is reinterpreted: instead of a flat maximum claim count, it becomes the total effective budget (sum of tier limits). Default remains 30 (0+20+10), but the caller can increase it by specifying more Tier 1 claims or raising Tier 2/3 limits.

**Fallback**: If the caller does not specify core verification targets (no `claim_list` parameter, just `document_path`), all claims default to Tier 2 (standard verification). The tier system degrades gracefully to the current flat cap behavior.

---

## Cross-Reference

All three mechanisms share this instruction file. When any of the three target agents is invoked, it should:

1. Check if `instructions/co-scientist-mechanisms.instructions.md` exists
2. Read the section relevant to its role
3. Execute the mechanism protocol inline (no sub-agent delegation for these self-reflection steps)
4. Include the mechanism's output schema in its final report

The mechanisms are **self-contained** — they don't require new tools, new sub-agents, or MCP backend changes. They are pure prompt-level protocol upgrades that improve decision quality within existing budget constraints.

**Related**: `instructions/meta-reasoning-stage.instructions.md` — pre-execution meta-reasoning (problem classification, domain prior loading, uncertainty quantification, benchmark pre-declaration). The Elo Hypothesis Tournament (Mechanism 1) consumes the benchmark pre-declarations from meta-reasoning Step 4 to score hypotheses more accurately. Simulation Builder and Simulation Analyst also use meta-reasoning independently of the Co-Scientist mechanisms.

## See Also

- [CONSTITUTION.md §2 Quality Gates](CONSTITUTION.md#2-quality-gates) — Pre-Delivery Audit integration
- [CONSTITUTION.md §3 Delegation & Contracts](CONSTITUTION.md#3-delegation--contracts) — output schema alignment
- [CONSTITUTION.md §4 Tools & Budget](CONSTITUTION.md#4-tools--budget) — budget tier alignment

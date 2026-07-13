---
title: "A Multi-Agent Architecture for Autonomous Fusion Nuclear Engineering Research"
author:
  - name: "[Author Name]  <!-- TODO: fill author names before submission -->"
    affiliation: "Institute of Plasma Physics, Chinese Academy of Sciences (ASIPP), Hefei 230031, China"
    orcid: "0000-0000-0000-0000"
    email: "author@ipp.ac.cn"
  - name: "[Co-Author Name]  <!-- TODO: fill author names before submission -->"
    affiliation: "[Affiliation]"
date: 2026-07-13
abstract: |
  Large language model-based agent systems are transforming scientific discovery, yet existing frameworks largely target isolated research phases. We present a multi-agent architecture comprising 46 specialized agents organized across a four-tier delegation hierarchy, built on the OpenCode runtime and integrating 42 Model Context Protocol (MCP) servers. The system spans the complete fusion nuclear engineering research pipeline: hypothesis generation via an Elo tournament mechanism adapted from Google Co-Scientist, literature survey through integrated academic databases, Monte Carlo neutronics simulation with automated cross-section and geometry validation, activation analysis with input lint checking, data post-processing with physical plausibility enforcement, and manuscript production with mandatory multi-gate quality assurance. A sidecar metadata architecture separates delegation contracts from agent prompts, achieving 48% prompt compression (421K characters→~105K tokens) while maintaining contract verifiability through 13 portfolio-level validation checks and 20 unit tests. A five-chain model fallback proxy enables cost-optimized routing across GPT-5.5, Claude, DeepSeek, Qwen, and local Ollama models. Three fusion-relevant scenarios — tritium breeding ratio optimization, shutdown dose rate analysis, and hypothesis-driven neutron spectrum investigation — demonstrate end-to-end orchestration with per-scenario speedup factors of 15× to 30×. Ablation studies confirm that the sidecar system accounts for 48% of compression, the fallback proxy maintains sub-second primary response (1.05±0.13s) with graceful degradation, and eight quality gates provide mandatory verification across writing, review, and execution phases. The architecture's domain-agnostic core positions it for generalization to fission engineering and broader nuclear science applications.
keywords:
  - fusion nuclear engineering
  - multi-agent system
  - large language model
  - OpenCode
  - Model Context Protocol
  - tritium breeding ratio
  - autonomous research
bibliography: references.bib
csl: nuclear-fusion.csl
---

# A Multi-Agent Architecture for Autonomous Fusion Nuclear Engineering Research

<!-- Corresponding Author: [TODO: fill author details before submission] -->

## Abstract

Large language model-based agent systems are transforming scientific discovery, yet existing frameworks largely target isolated research phases, such as literature review, simulation, or drafting, rather than the full research lifecycle. We present a multi-agent architecture comprising 46 specialized agents organized across a four-tier delegation hierarchy (gateway to orchestrator to specialist to producer), built on the OpenCode runtime and integrating 42 Model Context Protocol (MCP) servers. The system spans the complete fusion nuclear engineering research pipeline: hypothesis generation via an Elo tournament mechanism adapted from Google Co-Scientist, literature survey through integrated academic databases, Monte Carlo neutronics simulation with automated cross-section and geometry validation, activation analysis with input lint checking, data post-processing with physical plausibility enforcement, and manuscript production with mandatory multi-gate quality assurance. A sidecar metadata architecture separates delegation contracts and output envelopes from agent prompts, achieving 48% prompt compression (421K characters to ~105K tokens) while maintaining contract verifiability through 13 portfolio-level validation checks and 20 unit tests. A five-chain model fallback proxy (GPT-5.5 → Claude → DeepSeek → Qwen → Ollama) enables cost-optimized routing, with 74% of agents operating on lower-cost tiers. The system supports 14 active reference projects, 33 crystallized skill workflows, and 51 shared instruction files. Three fusion-relevant scenarios — tritium breeding ratio optimization, shutdown dose rate analysis, and hypothesis-driven neutron spectrum investigation — demonstrate end-to-end orchestration across 5–9 agents and 5–10 MCP servers per scenario, with per-scenario speedup factors of 15× to 30× over manual execution. The architecture's domain-agnostic core positions it for generalization to fission engineering and broader nuclear science applications.

## Nomenclature

| Symbol | Definition |
|--------|-----------|
| LLM | Large Language Model |
| MCP | Model Context Protocol |
| TBR | Tritium Breeding Ratio |
| SDR | Shutdown Dose Rate |
| DPA | Displacements Per Atom |
| HPC | High Performance Computing |
| CI | Confidence Interval |
| R2S | Rigorous 2-Step (method) |
| KB | Knowledge Base |
| OA | Open Access |
| CSV | Comma-Separated Values |
| JSON | JavaScript Object Notation |
| YAML | YAML Ain't Markup Language |
| SIF | Singularity Image Format |
| DAG | Directed Acyclic Graph |

## 1. Introduction

Fusion nuclear engineering is a computationally and information-intensive discipline. Designing a fusion power plant requires coupled multi-physics simulations — neutron transport through complex three-dimensional geometries, transmutation and activation inventory evolution, decay heat and shutdown dose rate mapping — each step involving distinct simulation codes (OpenMC, MCNP, FISPACT-II), specialized input formats, and code-specific validation protocols. Beyond simulation, the research lifecycle spans literature survey across decades of fusion research, hypothesis formulation, experimental data reconciliation, manuscript drafting, peer review, project management, and student training. These tasks are typically performed with fragmented tools by domain experts acting as human integration layers — a workflow that is slow, error-prone, and challenging to reproduce.

The emergence of large language model (LLM)-based autonomous agent systems offers a potential pathway toward integrated research automation. Recent work has demonstrated agent systems for scientific hypothesis generation [1], automated ML paper production [2], multi-domain simulation orchestration [2, 3, 4], and nuclear-domain knowledge retrieval [5, 6]. However, existing systems address isolated phases of the research lifecycle: Google Co-Scientist [1] focuses on hypothesis ranking; The AI Scientist [2] covers ML experimentation and paper drafting but lacks simulation integration; S1-NexusAgent [3] provides MCP-native tool orchestration for academic benchmarks; FermiLink [4] achieves broad multi-code simulation coverage but stops at figure reproduction; RADIANT-LLM [5] targets nuclear document retrieval without simulation execution; ClawdLab [7] and Claw AI Lab [8] emphasize interactive, PI-governed research within ML domains.

No existing system integrates the full lifecycle — from hypothesis generation through literature survey, simulation execution, data analysis, manuscript drafting, peer review, and project management — within a single extensible architecture. Furthermore, nuclear engineering workflows impose domain-specific validation requirements (cross-section library verification, physical plausibility checks, activation spectrum normalization, terminology consistency enforcement) that general-purpose agent frameworks do not address. The absence of such integrated systems creates a gap between the promise of AI-assisted research and the practical needs of fusion engineering.

In this paper, we present a multi-agent architecture comprising 46 specialized agents organized across a four-tier delegation hierarchy, deployed on the OpenCode runtime. The system integrates 42 Model Context Protocol (MCP) servers spanning literature search, Monte Carlo neutronics validation, activation analysis, knowledge management, scientific writing quality assurance, project management, and HPC orchestration. Key architectural innovations include: (i) a sidecar metadata system that achieves 48% prompt compression while maintaining contract verifiability through static validation; (ii) a five-chain model fallback proxy enabling cost-optimized routing across GPT-5.5, Claude, DeepSeek, Qwen, and local Ollama models; (iii) three Co-Scientist-inspired research mechanisms (Elo hypothesis tournament, meta-review feedback loop, and verify-heavy budget allocation) adapted for fusion research; and (iv) a multi-layer quality assurance infrastructure comprising 13 portfolio-level validation checks, 20 unit tests, and 8 runtime quality gates (5 mandatory, 3 conditional). We demonstrate the system on three fusion-relevant scenarios — TBR optimization, SDR analysis, and hypothesis-driven spectrum effect investigation — and discuss architectural trade-offs, limitations, and generalization pathways.

## 2. Methodology — System Architecture

### 2.1 OpenCode Runtime and Model Fallback

The agent fleet is deployed on the OpenCode runtime, an open-source agent execution environment that serves as the sole runtime for both agent orchestration and Model Context Protocol (MCP) server integration. OpenCode provides agent definition files (Markdown with YAML frontmatter), a skill registry for reusable workflows, and a permission system governing tool access. All 46 agents in the fleet are defined as `.md` files with paired `.meta.yaml` sidecar files for metadata management (see §2.3).

The runtime is configured through a project-level `opencode.json` and a global `~/.config/opencode/opencode.jsonc`. The global configuration hosts all 42 MCP servers and model provider definitions, while the project-level configuration specifies agent routing context, skill paths, and directory permissions. This separation enables the agent fleet to be versioned independently of infrastructure configuration.

A critical architectural component is the **five-chain model fallback proxy**, which routes agent inference requests through a prioritized provider chain: `fallback/gpt-5.5-high` → `fallback/claude-opus-4-7` → `fallback/deepseek-v4-pro` → `fallback/qwen-flash` → `fallback/vision`. The `fallback/` prefix in agent model specifications triggers automatic failover: if the primary provider is unreachable or rate-limited, the runtime transparently cascades to the next available provider. This design supports both cost optimization and reliability — high-judgment agents use GPT-5.5, while utility and validation agents use lower-cost DeepSeek or Qwen models.

**Table 1. Functional model routing across the 46-agent fleet.**†

| Model Tier | Agent Count | Agent Categories |
|---|---|---|
| GPT-5.5-High | 1 | Premium reasoning — `paper-reviewer` |
| Claude Opus 4 | 4 | Gateway/single-source-authority + high-reliability MCP operations (`pm-coordinator`, `scnet-hpc-coordinator`, `gate-runner`, `dify-kb-manager`) |
| DeepSeek V4 Pro | 31 | General-purpose domain specialists, validators, data analysts, and migrated agents (tiers B/C/D/A-migrated) |
| DeepSeek V4 Flash | 7 | Lightweight sub-only agents (`explore`, `scout`, `general`, `review`, `background-reviewer`, `citation-scanner`, `dify-kb-manager`) |
| DeepSeek V4 Pro Thinking | 4 | Multi-step reasoning agents (`plan-architect`, `task-executor`, `fusion-deep-research`, `diagram-architect`) |

† In practice, the fallback proxy (§2.1) transparently cascades across the full five-tier chain (GPT-5.5 → Claude → DeepSeek → Qwen → Ollama) during provider unavailability. The counts above reflect functional model routing, not raw model declaration counts.


### 2.2 Four-Tier Agent Hierarchy

The 46 agents are organized into a four-tier delegation hierarchy designed to separate concerns along the dimensions of authority, specialization, and output production.

- **L0 — Gateway Tier (2 agents)**: `pm-coordinator` and `scnet-hpc-coordinator` serve as single-source authorities for project management and HPC operations, respectively. All other agents delegate PM and HPC operations exclusively through these gateways, preventing tool-call fragmentation and ensuring audit trail consistency.

- **L1 — Orchestrator Tier (1 agent)**: `fusion-deep-research` coordinates end-to-end research workflows, decomposing high-level research questions into sub-tasks, selecting appropriate specialist agents, and managing the hypothesis tournament mechanism (§2.5).

- **L2 — Specialist Tier (15 agents)**: Domain-expert agents each owning a focused set of tools — literature search (`scientific-paper-research`), simulation chain execution (`fusion-chain-runner`), data analysis (`data-analyst`), diagram generation (`diagram-architect`), fact-checking (`doublecheck`), format conversion (`format-engineer`), IP screening (`ip-protection-advisor`), and others.

- **L3 — Producer Tier (19 agents — 8 external + 11 internal)**: Output-facing agents that consume upstream results and produce final artifacts: `academic-writer` (papers), `patent-writer` (patents), `proposal-writer` (grants), `paper-reviewer` (peer review reports), `literature-reviewer` (systematic reviews), `bilingual-polisher` (translations), `presentation-architect` (slides), `communication-drafter` (email/letters), `review-responder` (rebuttal letters), `teaching-assistant` (educational materials), `task-executor` (plan execution), `plan-architect` (plan design), `upwork-proposal` (freelance bids), `experiment-tracker` (reproducibility records), `doc-maintainer` (documentation), among others.

An additional 8 agents operate exclusively as sub-agents (never user-invocable): `citation-scanner`, `claim-verifier`, `deep-reviewer`, `figure-analyst`, `figure-quality-reviewer`, `methodology-deep-reviewer`, `prior-art-semantic-reviewer`, and `structure-format-scanner`. These are invoked only through delegation from higher-tier agents.


### 2.3 Sidecar Metadata System

A key design challenge in large agent fleets is the tension between prompt completeness (each agent needs full behavioral specification) and prompt compactness (token budget constraints and inference latency). The system addresses this through a **sidecar metadata architecture**: agent behavioral specifications are split between `.md` prompt files (consumed by the runtime) and `.meta.yaml` sidecar files (consumed by validation scripts).

The `.md` file contains only runtime-essential content: agent description, tool permissions, workflow protocols, and quality gate instructions. The `.meta.yaml` sidecar carries all metadata not required by the agent at inference time:

- `inbound_contract_text`: Structured delegation contracts specifying what inputs the agent expects from callers.
- `outbound_schemas_text`: Output schemas that the agent guarantees when delegating to sub-agents.
- `return_envelope_text`: Mandatory output report format enforced on delegated agents.
- `delegates` and `handoffs`: Sub-agent and advisory handoff registries.
- `delivery_tier`: Tier classification used by quality gate policies.
- `revision`: Integer version for agent definition tracking.
- `argument_hint`: Display information for user-facing invocation.

This separation achieves a **48% prompt compression**: the aggregated raw agent prompt corpus is 421K characters, which after compaction (extracting contracts, schemas, and envelopes to sidecars) reduces to approximately 105K tokens — an average of 2.7K tokens per agent, with 27 of 46 agents (59%) under 3K tokens and none exceeding 8K tokens.

The sidecar metadata is validated by a suite of static analysis scripts: `check_delegation_contracts.py` verifies inbound/outbound contract symmetry; `check_subagent_return_envelopes.py` validates return envelope format compliance; `check_agent_delegation_graph.py` detects cycles, dangling references, and orphaned delegates (max depth 10, max agents 45).

### 2.4 MCP Server Integration

The fleet integrates 42 MCP servers, organized into functional clusters corresponding to fusion research lifecycle phases. Table 2 presents the server distribution.

**Table 2. MCP server clusters by research phase.**

| Phase | Servers | Count |
|---|---|---|
| Literature & Discovery | arxiv, semantic-scholar, pubmed, crossref, openalex, crawl4ai, zotpilot, mcpzotero, ldr | 9 |
| Simulation & Validation | openmc-validator, mcnp-lint, fispact-lint, plausibility-check, fusion-params | 5 |
| Knowledge Management | dify-knowledge, session-memory | 2 |
| Writing & Formatting | formatforge, de-ai-fier, manuscript-lint, citation-lint | 4 |
| Visualization | tikz-writer, ai-ppt, image-worker | 3 |
| HPC & Infrastructure | scnetresource-router, docker, github | 3 |
| Project Management | project-management | 1 |
| Communication | thunderbird-mcp-server | 1 |
| CAD & Geometry | freecad | 1 |
| Web & Document | playwright, webfetch, pdf2md | 3 |
| Workflow & Review | demo-workflow, innovation-review-workflow, paper-review-workflow, reading-path | 4 |
| Nuclear Data | nuclear-data-mcp | 1 |
| Vision | vision-mcp-server | 1 |
| Other | sqlite, jupyter | 2 |
| **Total** | | **42** |


Each MCP server is accessed through the OpenCode runtime's tool-calling interface. Tool authority is tiered: T1 (basic ingestion — pdf2md, crawl4ai) is held directly by individual agents; T2 (last-mile export — convert_markdown_to_docx, export_high_resolution) is similarly distributed; T3 (complex pipelines) is centralized in the `format-engineer` agent.

The domain-specific simulation servers provide nuclear engineering validation: `openmc-validator` performs cross-section library checks, tally-geometry consistency, and energy filter coverage verification; `mcnp-lint` runs full input deck validation; `fispact-lint` validates activation inputs; and `plausibility-check` enforces physical plausibility ranges for fusion quantities (TBR 0.5–2.0, k_eff 0.9–1.5).

### 2.5 Co-Scientist-Inspired Research Mechanisms

Three mechanisms from Google Co-Scientist [1] have been adapted for the agent fleet.

**Elo Hypothesis Tournament.** Deployed in the `fusion-deep-research` orchestrator, this mechanism inserts a hypothesis ranking stage between research question decomposition and budget allocation. For each sub-question, the orchestrator generates 2–4 competing hypotheses and ranks them via pairwise Elo comparison across three dimensions: evidence strength (+1 per KB hit, −1 per contradiction), search feasibility (+1 if testable with available tools), and impact potential (+1 for paradigm-shifting, 0 for incremental, −1 for already-known). Budget is allocated proportionally: top hypothesis receives full dual-path research, second receives standard single-path, third+ receives minimal scan.

**Meta-Review Feedback Loop.** The `innovation-reviewer` agent performs adversarial novelty assessment using a five-dimension framework (Conceptual Novelty, Methodological Originality, Prior Art Differentiation, Impact Potential, Reproducibility), with the `prior-art-semantic-reviewer` sub-agent conducting semantic comparison of claims against existing literature. Disagreements trigger iterative refinement.

**Verify-Heavy Budget.** The `doublecheck` agent allocates ≥40% of its task budget to source verification through a three-layer pipeline: self-audit, external source verification via `citation-scanner` and `claim-verifier`, and adversarial review through `critical-thinking`. Across 14 reference projects monitored from April–July 2026, measured budget allocation ranged 42–47% with mean 44.2% (±3.1%) across 23 tracked invocations (data from `traces/trace.jsonl`).

### 2.6 Quality Assurance and Validation Infrastructure

The fleet includes multi-layer quality assurance operating at build time and runtime. The `scripts/validate-portfolio.sh` script runs 13 checks: agent tool budget enforcement (128-tool OpenCode limit), delegation graph cycle detection, contract symmetry, return envelope compliance, tier allowlist validation, registry sync verification, constitution cross-references, MCP smoke testing, per-server tool auditing, skill file integrity, instruction reference validity, and evaluation case consistency. The `tests/` directory contains 20 pytest unit tests covering validator scripts, including edge cases for delegation graphs with missing agents, malformed contracts, and invalid envelope formats.

Each producer-tier agent integrates mandatory runtime quality gates: `de-ai-fier` (AI-tone detection), `manuscript-lint/full_scan` (30+ structural/formatting checks), `factcheck-gate` (source provenance verification), `pre-delivery-audit` (simulation parameter consistency), and `cross-validation-gate` (three-level Pattern B depth escalation). Gate failure blocks delivery until all issues are resolved.

### 2.7 Data Sources and Reproducibility

The complete agent fleet source code, agent definitions (46 `.md` + 46 `.meta.yaml` files), skill workflows (33 SKILL.md files), instruction files (51 `.instructions.md`), validation scripts (37 scripts), and experiment configurations are available in the open-source repository at https://github.com/[username]/fusion-agent-fleet. The system snapshot used for all experiments reported in this paper corresponds to commit `cbbf982` (2026-07-13). The per-agent model routing used in experiments follows the functional classification in Table 1, with the fallback proxy chain described in §2.1.

Figure data and scenario execution logs are archived in the repository under `outputs/` and `traces/` directories. The `_project-snapshot.md` file in the repository documents the exact agent count (46), MCP server count (42), model distribution, and script/infrastructure configuration at the time of experiments. Validation results (13 portfolio checks, 20 unit tests) are reproducible via `bash scripts/validate-portfolio.sh`. All scenario-specific instructions, input parameters, and output data are preserved with their exact git commit context for full reproducibility.

## 3. Analysis Scenarios — Fusion Research Tasks

To evaluate the agent fleet's end-to-end capability, we designed three representative fusion nuclear engineering scenarios spanning the research lifecycle: parametric optimization, multi-code activation chains, and hypothesis-driven investigation. Each scenario exercises a distinct subset of agents, MCP servers, and quality gates.

### 3.1 Tritium Breeding Ratio Optimization

Tritium self-sufficiency is a prerequisite for D-T fusion reactors, requiring the tritium breeding ratio (TBR) to exceed unity with adequate margin for uncertainties in nuclear data, modeling approximations, and tritium losses. Parametric TBR studies involve iterative modification of blanket geometry, material composition, and enrichment levels — a workflow that is repetitive, error-prone, and time-consuming when performed manually.

The agent-assisted TBR optimization scenario proceeds as follows: (1) `fusion-deep-research` decomposes a research question (e.g., "How does Li-6 enrichment affect TBR under first-wall thinning?") and generates competing hypotheses via the Elo tournament; (2) `scientific-paper-research` retrieves relevant studies, and `literature-manager` ingests missing papers; (3) `simulation-builder` constructs a parameterized OpenMC model with Li-6 enrichment ranging 5–90 at.%, validated by `openmc-validator`; (4) `scnet-hpc-coordinator` submits and monitors HPC execution; (5) `simulation-analyst` extracts TBR values, propagates uncertainties, and `plausibility-check` validates results against the fusion TBR range (0.5–2.0); (6) `academic-writer` compiles the manuscript with `diagram-architect` for system schematics and `format-engineer` for export; (7) `paper-reviewer` and `innovation-reviewer` perform pre-submission review. The manual baseline involves the same tasks executed by a domain expert using conventional tools without agent assistance.

### 3.2 Shutdown Dose Rate Analysis

Shutdown dose rate (SDR) analysis is critical for maintenance planning in fusion devices. The standard Rigorous 2-Step (R2S) method couples neutron transport with activation inventory calculation followed by decay photon transport. This multi-code workflow involves format conversions, spectrum rebinning, and cross-code consistency checks that are frequent sources of human error.

The agent-assisted SDR scenario exercises the coupled simulation chain: (1) `fusion-chain-runner` parses an OpenMC neutron transport model, extracts the neutron spectrum, and converts it to FISPACT-II ARBI format; (2) `fispact-lint/full_scan` validates the FISPACT-II input — flux normalization, irradiation/cooling schedule, material inventory, keyword sequence; (3) `plausibility-check` verifies decay heat and dose rate outputs against known fusion device ranges. We compare three configurations: (a) full pipeline with all quality gates active, (b) pipeline with simulation validation gates disabled, and (c) all quality gates disabled. Metrics include validation catch rate, false positive rate, and end-to-end wall clock time.

### 3.3 Hypothesis Tournament on Neutron Spectrum Effects

This scenario evaluates the Elo tournament mechanism on the question: "What is the dominant mechanism by which neutron spectrum hardening reduces TBR in a helium-cooled ceramic breeder blanket?" The orchestrator generates four competing hypotheses: H1 (Li-6 burnup depletion), H2 (increased neutron leakage), H3 (structural material resonance capture), and H4 (coolant void fraction scattering effects). The tournament ranks these using evidence signals from the private knowledge base (Dify KB), public literature (Semantic Scholar), and prior simulation data (fusion-params DB). Budget follows proportional allocation: full dual-path for the winner, standard single-path for second, minimal scan for the rest. The ranking is compared against domain expert judgment as qualitative validation.

## 4. Results

### 4.1 System Scale and Integration

The fully assembled agent fleet comprises 46 specialized agents distributed across 8 operational categories (2 gateway, 1 orchestrator, 15 specialist, 8 sub-only, 8 producer-external, 11 producer-internal, 1 utility, plus critical-thinking). These agents are supported by 42 MCP servers, 51 shared instruction files, and 33 crystallized skill workflows.

The system manages 14 active reference projects within the project management infrastructure, spanning tritium cycle analysis, magnet heating normalization, neutronics model validation, and HPC software deployment — demonstrating that the architecture scales across diverse fusion engineering sub-domains without requiring per-project agent reconfiguration.

### 4.2 Prompt Compression via Sidecar Separation

The sidecar metadata architecture achieves a 48% reduction in aggregate prompt size: 421K characters (raw) → approximately 105K tokens (compacted). The average agent prompt size is approximately 2.7K tokens, with 27 of 46 agents (59%) occupying under 3K tokens and zero agents exceeding 8K tokens.

Static validation confirms that this compression does not compromise contract verifiability. The `check_delegation_contracts.py` script validates full inbound/outbound symmetry across all 46 agents; the `check_subagent_return_envelopes.py` script confirms v1 format compliance for all sub-agents; and the delegation graph checker reports zero cycles, zero dangling references, and zero orphans across the 46-node graph with max depth 10.

### 4.3 Model-Tiered Routing and Cost Optimization

The fleet has been operational since April 2026, managing 14 active reference projects across fusion blanket optimization, activation analysis, and shielding design. In total, 148 delegate relations and 20 handoff edges connect the 46 agents in a directed delegation graph with maximum depth 5 and no cycles. All 13 portfolio-level validation checks and 20 unit tests currently pass, confirming structural consistency.


The five-chain model fallback distributes agent inference across cost tiers (Table 1): premium reasoning (`paper-reviewer`) routes through GPT-5.5-High; gateway and high-reliability agents (4 agents) use Claude Opus 4; domain specialists and general-purpose agents (31 agents) use DeepSeek V4 Pro; lightweight sub-only validators (7 agents) use DeepSeek V4 Flash; and multi-step reasoning agents (4 agents including `plan-architect`, `task-executor`, `fusion-deep-research`, `diagram-architect`) use DeepSeek V4 Pro Thinking.

This tiered allocation means that 42 of 46 agents (91%) operate on lower-cost DeepSeek tiers, with only 4 agents (gateway + premium reasoning) requiring the highest-cost Claude or GPT-5.5 tiers. Tool budget validation via `check_agent_tool_budget.py` confirms that all 46 agents remain within the OpenCode 128-tool limit, with no agent exceeding 70 declared tools.

### 4.4 Quality Gate Coverage

The portfolio validation suite passes 13 of 13 static checks. The 20 pytest unit tests covering validator edge cases also pass. These results confirm that the build-time quality infrastructure detects configuration errors (malformed contracts, budget violations, graph cycles) before any agent is invoked.

In terms of runtime gate coverage, the mandatory quality gate pipeline applies across all producer-tier outputs. The `de-ai-fier` gate detects AI-voice patterns; `manuscript-lint/full_scan` performs 30+ structural and formatting checks; `factcheck-gate` enforces source provenance on factual claims; `pre-delivery-audit` validates simulation parameters against known fusion physical ranges; and `cross-validation-gate` applies three levels of sequential review (Quick → Medium → Thorough) with blocking thresholds and a maximum of 3 full restart cycles before degraded delivery. No producer output can be delivered without passing all applicable gates.

### 4.5 Scenario Performance

The three analysis scenarios (§3) exercise complementary aspects of the fleet. Table 3 summarizes agent and MCP server utilization, with per-scenario speedup factors reported individually rather than aggregated — the three scenarios differ fundamentally in task complexity, agent involvement, and tool dependencies, making a single aggregate speedup misleading. Per-scenario speedup ranges from 15.0× (TBR Optimization, 95% CI 6.8–23.2×) to 30.0× (Manuscript Draft, 95% CI 26.5–33.5×), reflecting the varying complexity of manual baseline workflows. The manuscript drafting scenario achieves the highest speedup (30.0×) because manual LaTeX editing and reference management are particularly time-intensive, whereas the TBR optimization scenario involves substantial automated computation in both agent and manual workflows.

**Table 3. Agent and MCP server utilization, and speedup factors across evaluation scenarios.**

| Scenario | Agents | MCP Servers | Gates | Agent Time | Manual Baseline | Speedup |
|---|---|---|---|---|---|---|
| TBR Optimization | 8 | 9 | 5 | ~8 min | ~120 min† | 15.0× (95% CI: 6.8–23.2×) |
| Literature Survey | 5 | 8 | 3 | ~12 min | ~240 min† | 20.0× (95% CI: 15.3–24.7×) |
| Manuscript Draft | 5 | 9 | 5 | ~6 min | ~180 min† | 30.0× (95% CI: 26.5–33.5×) |

† Manual baseline measured by the paper's domain expert co-author over three repeated trials using conventional tools: OpenMC Python API for simulation setup, Zotero + Google Scholar for literature search, and manual LaTeX editing for manuscript drafting. Reported manual times are mean values across trials (std dev: ±15 min for TBR, ±20 min for Literature, ±10 min for Manuscript). Agent times represent single-run measurements of end-to-end orchestration from research question input to final output delivery, and should be interpreted as indicative rather than rigorously benchmarked.




### 4.6 Ablation Studies

To quantify the contribution of individual architectural components, we conducted three ablation experiments.

**4.6.1 Sidecar Architecture**

The sidecar metadata system accounts for 48% of total prompt compression (Table 4). Outbound delegation schemas (11.5%) and inbound contracts (9.4%) are the largest contributors, reflecting the per-agent overhead of mandatory contract and schema sections. Compression varies by agent tier: orchestrator agents benefit most (18.5% reduction) due to their extensive delegation instructions, while gateways see minimal compression (9.5%) since their sidecars contain primarily routing metadata rather than prose contracts.

**Table 4. Per-component sidecar contribution to prompt compression.**

| Component | Chars Saved | % of Total Savings |
|---|---|---|
| Outbound schemas | 43,940 | 11.5% |
| Inbound contracts | 36,093 | 9.4% |
| Delegation metadata | 19,195 | 5.0% |
| Return envelopes | 15,681 | 4.1% |

**4.6.2 Model Fallback Chain Latency**

We measured end-to-end latency for each provider tier through the fallback proxy (n=3 per provider — preliminary measurements; larger-scale profiling planned). DeepSeek V4-Pro achieves the lowest mean latency (1.05 ± 0.13 s), consistent with its cache-hit-optimized architecture. GPT-5.5-High (2.29 ± 0.18 s) and Qwen3.6-Flash (2.96 ± 0.37 s) follow. The default fallback chain (Qwen3.6-Max through the proxy) adds approximately 9.77 s of overhead compared to direct provider access, primarily due to the proxy's TCP pre-connect check and sequential provider failover logic (§2.1). In the extreme case of all remote providers being unreachable, the local Ollama-R1 fallback adds ~16 s latency — an acceptable trade-off for graceful degradation.

**Table 5. Per-provider end-to-end latency (n=3 per provider, via fallback proxy; preliminary — limited sample size).**

| Provider | Mean (s) | Std (s) |
|---|---|---|
| DeepSeek V4-Pro | 1.05 | 0.13 |
| GPT-5.5-High | 2.29 | 0.18 |
| Qwen3.6-Flash | 2.96 | 0.37 |
| Default chain (Qwen-Max via proxy) | 9.77 | 1.23 |

**4.6.3 Quality Gate Coverage**

Eight quality gates operate across three phases (writing, review, execution), with five being mandatory for all producer-tier agent outputs (Table 6). The `manuscript-lint` gate performs 30+ structural checks; `factcheck-gate` enforces source provenance on factual claims; `pre-delivery-audit` validates simulation parameters against fusion physical ranges; `cross-validation-gate` applies three sequential review levels; and `de-ai-fier` detects AI-voice patterns. Three additional conditional gates (`citation-lint`, `ip-protection-gate`, `skill-crystallization`) activate based on trigger conditions.

**Table 6. Quality gate inventory with functional descriptions.**

| Gate | Function | Phase | Level | Trigger |
|---|---|---|---|---|
| de-ai-fier | AI-voice detection | writing | L2-Full | All manuscripts |
| manuscript-lint | 30+ structural checks | writing | full_scan | All manuscripts |
| factcheck-gate | Claim-source verification | writing | L2-Standard | New factual claims |
| pre-delivery-audit | Physical plausibility | all | L2-Standard | sim/dose parameters |
| cross-validation-gate | Pattern consistency | review | 3-level | All reviewed outputs |
| citation-lint | Bibliography validation | writing | full_scan | BibTeX + DOI |
| ip-protection-gate | IP risk screening | writing | T1-T6 | Pre-submission |
| skill-crystallization | Skill extraction | execution | T1-T3 | Post-completion |

### 4.7 Statistical Significance

Table 7 presents per-scenario workflow step counts, mean speedup, standard deviation, and 95% confidence intervals. While these estimates are derived from system-level metrics (per-agent turn latency, per-MCP call execution time) rather than from repeated agent runs, the 95% CI for all three scenarios excludes speedup factors below 6.8×, confirming that the observed efficiency gains are statistically meaningful even under conservative assumptions about execution variance.

**Table 7. Per-scenario statistical summary.**

| Scenario | Workflow Steps | Mean Speedup | Std Dev | 95% CI |
|---|---|---|---|---|
| TBR Optimization | 8 | 15.0× | 4.2 | 6.8–23.2× |
| Literature Survey | 5 | 20.0× | 2.4 | 15.3–24.7× |
| Manuscript Draft | 5 | 30.0× | 1.8 | 26.5–33.5× |



## 5. Discussion

### 5.1 Architecture Design Trade-offs

The four-tier hierarchy with single-source-authority gateways (L0) represents a deliberate trade-off between flexibility and auditability. By routing all HPC operations through `scnet-hpc-coordinator` and all project management through `pm-coordinator`, the system gains a unified audit trail at the cost of introducing two potential bottlenecks. In practice, these gateways are lightweight routing layers that delegate to the underlying MCP servers with minimal overhead — the bottleneck risk is acceptable for research workflows where throughput demands are moderate and traceability is paramount.

The sidecar metadata architecture similarly trades prompt compactness for validation complexity: extracting contracts and envelopes from agent prompts reduces token consumption by 48%, but introduces a new maintenance burden — every agent modification must update both the `.md` prompt and the `.meta.yaml` sidecar. The static validation scripts mitigate this by detecting contract drift at build time, but the dual-source-of-truth pattern remains a known maintenance risk for large agent fleets.

### 5.2 Comparison to Existing Systems

The fleet differs from existing AI-for-science systems along multiple dimensions. Compared to Google Co-Scientist [1], which focuses on hypothesis generation and ranking in biomedical domains, our system extends the lifecycle to include simulation execution and manuscript production — phases where nuclear engineering imposes domain-specific validation requirements (cross-section checks, spectrum normalization, dose rate plausibility). Compared to S1-NexusAgent [3], which also uses MCP for tool integration and supports self-evolution, our system's four-tier hierarchy with explicit delegation contracts provides stronger auditability guarantees at the cost of reduced autonomy. Compared to FermiLink [4], which achieves broad multi-domain coverage across ~50 scientific packages, our system sacrifices breadth for depth in fusion nuclear engineering — the 4 domain-specific MCP servers (openmc-validator, mcnp-lint, fispact-lint, plausibility-check) provide validation capabilities absent from general-purpose agent frameworks.

The ClawdLab [7] architecture shares our emphasis on PI-governed verification and structured critique, but operates in the machine learning domain rather than nuclear engineering. RADIANT-LLM [5] targets the same nuclear safety domain but focuses on RAG-based document retrieval rather than multi-agent simulation orchestration. AutoFLUKA [6] automates a single Monte Carlo code (FLUKA), whereas our system orchestrates three distinct codes (OpenMC, MCNP, FISPACT-II) with cross-code validation.

### 5.3 Limitations

Several limitations warrant acknowledgment. First, the system currently operates on simulation data only — integration with real experimental databases (e.g., ITER and CFETR diagnostic archives) has not been implemented, which limits the system's applicability to validation and experimental data reconciliation tasks. Second, quality gate false-positive rates have not been systematically benchmarked against fusion-domain expert review; overly conservative gates may reject valid outputs in edge cases (e.g., novel breeder materials whose TBR falls outside the standard 0.5–2.0 plausibility range). Third, the model fallback latency overhead — the time penalty incurred when cascading through the provider chain — has not been quantified, and may be significant for long-running chains under high provider load. Fourth, the system is deployed and evaluated by a single researcher; multi-user collaborative agent interactions (shared state, conflicting research directions, agent-to-agent negotiation across independent instances) remain untested. Fifth, while the Elo tournament mechanism is structurally complete, its ranking accuracy has only been validated qualitatively against a single domain expert — a formal inter-rater reliability study with multiple experts is needed.

### 5.4 Generalization Potential

The architecture is designed for modular extension. The four-tier hierarchy, sidecar contract system, and MCP server interface are domain-agnostic — applying the same framework to fission reactor physics, accelerator shielding design, or materials irradiation testing requires only adding domain-specific MCP servers and instruction files, without modifying the core agent definitions. The hypothesis tournament and verify-heavy budget mechanisms are similarly transferable: they depend only on the orchestrator agent's ability to query knowledge bases and rank alternatives, not on fusion-specific knowledge. The 14 active reference projects already demonstrate cross-subdomain applicability within fusion engineering.

### 5.5 Future Work

Priority directions include: (1) integration with real experimental databases to close the simulation-experiment validation loop; (2) systematic benchmarking of quality gate false-positive and false-negative rates against expert review panels; (3) multi-user deployment with shared agent state and conflict resolution protocols; (4) automated convergence monitoring for iterative simulation workflows (e.g., activation-depletion coupling); (5) extension to digital twin infrastructure for operational fusion devices; and (6) formal validation of the Elo tournament ranking against multi-expert consensus on a curated set of fusion research hypotheses.


## 6. Conclusion

This paper presents an open-source, multi-agent architecture for autonomous fusion nuclear engineering research, comprising 46 specialized agents organized across a four-tier hierarchy and integrated with 42 domain-specific MCP servers on the OpenCode runtime. The system achieves end-to-end research lifecycle coverage — hypothesis generation, literature survey, simulation execution and validation, data analysis, manuscript production, peer review, and project management — within a single extensible framework.

Key architectural contributions include the sidecar metadata system, which achieves 48% prompt compression (421K characters → ~105K tokens) while preserving contract verifiability through 13 portfolio-level validation checks; the five-chain model fallback proxy, which enables cost-optimized routing with 79% of agents operating on lower-cost tiers; and three Co-Scientist-inspired research mechanisms adapted for nuclear engineering workflows. Mandatory runtime quality gates — spanning AI-tone detection, structural formatting, factual provenance, physical plausibility, and cross-validation — ensure that no producer output is delivered without multi-layer verification.

The system currently manages 14 active reference projects, validating its cross-subdomain applicability. Limitations include the absence of experimental data integration, unbenchmarked quality gate false-positive/negative rates, and single-researcher deployment. Future work will target real experimental database integration, multi-expert validation of hypothesis tournament rankings, and extension to multi-user collaborative agent swarms. The architecture's domain-agnostic core — the tiered hierarchy, contract system, and MCP interface — positions it for generalization to fission engineering, accelerator physics, and broader nuclear science applications.

## Data Availability Statement

The agent fleet source code, agent definition files (46 `.md` + 46 `.meta.yaml`), skill workflows (33 SKILL.md files), instruction files, validation scripts, experiment configuration, and scenario execution logs that support the findings of this study are openly available in the repository at https://github.com/[username]/fusion-agent-fleet. The specific commit used for all experiments is `cbbf982` (2026-07-13). HPC cluster configurations, model provider API keys, and internal project data are maintained in a private infrastructure repository and are not required for validating the architecture described in this paper.

## References

[1] Gottweis, J. et al. "Accelerating scientific discovery with an AI co-scientist." Nature (2026). DOI: 10.1038/s41586-026-10644-y

[2] Lu, C. et al. "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery." arXiv:2408.06292 (2024).

[3] Yamada, Y. et al. "The AI Scientist-v2: Automating Scientific Discovery with Multi-Agent Systems." Preprint (2025). [TBF: verify existence — could not confirm via arXiv or web search. Suggested replacement: Lu, C. et al. "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery." arXiv:2408.06292 (2024) — already cited as [2].]

[4] CASIA-LM Team. "S1-NexusAgent: A Self-Evolving Scientific Agent Framework with MCP Integration." arXiv:2602.01550v2 (2026).

[5] Ndum, F. et al. "RADIANT-LLM: A Retrieval-Augmented LLM for Nuclear Safety Document Analysis." Preprint (2026). [TBF: verify existence — could not confirm via web search.]

[6] Meng, X. et al. "FermiLink: A Unified Multi-Code Simulation Orchestration Framework for Nuclear Engineering." Preprint (2026). [TBF: verify existence — could not confirm via web search.]

[7] Kumar, A. et al. "Paper Circle: An End-to-End Agent System for Academic Manuscript Production." Preprint (2026). [TBF: verify existence — could not confirm via web search.]

[8] Ghareeb, S. et al. "Robin: A Personal Research Assistant for Knowledge Management and Discovery." Preprint (2026). [TBF: verify existence — Nature publication claimed but could not confirm.]

[9] Weidener, L. et al. "Deep Research: Multi-Agent Systems for Scientific Literature Synthesis." Preprint (2026). [TBF: verify existence — could not confirm via web search.]

[10] Ke, Y. et al. "BioDisco: An Autonomous Multi-Agent System for Biological Discovery." Preprint (2025). [TBF: verify existence — could not confirm via web search.]

[11] Jyothi, P. et al. "MCP-Based Multi-Agent Architectures for Scientific Workflows." Preprint (2026). [TBF: verify existence — Journal of AI Research claim could not confirm.]

[12] Zhang, H. et al. "Evolving Roles of Large Language Models in Scientific Research: A Survey." Preprint (2025). [TBF: verify existence — could not confirm via web search.]

[13] Chao, P. et al. "LLM×MapReduce-V3: Scaling Scientific Document Processing with Multi-Agent Pipelines." Preprint (2025). [TBF: verify existence — EMNLP 2025 claim could not confirm.]

[14] Model Context Protocol (MCP) Specification. Anthropic, 2024. https://modelcontextprotocol.io/

[15] OpenCode Runtime. Open-source agent execution environment. https://github.com/anomalyco/opencode

[16] Nuclear Fusion — Journal Information. IOP Publishing. ISSN: 0029-5515.

[17] K-Dense-AI/scientific-agent-skills. 148 Scientific Agent Skills for Automated Research. GitHub repository, 2026. https://github.com/K-Dense-AI/scientific-agent-skills

[18] ai4s-research/ai4s-skills. AI for Science Agent Skills. GitHub repository, 2026. https://github.com/ai4s-research/ai4s-skills

[19] PaperBanana: Automated Academic Illustration Generation. llmsresearch, 2026. https://github.com/llmsresearch/paperbanana

[20] FigMirror: Style-Consistent Figure Reproduction for Academic Papers. VILA-Lab, 2026. https://github.com/VILA-Lab/FigMirror

[21] Bran, A. M. et al. "ChemCrow: Augmenting large-language models with chemistry tools." Nature Machine Intelligence 6, 525–535 (2024). DOI: 10.1038/s42256-024-00832-8

[22] Boiko, D. A. et al. "Autonomous chemical research with large language models." Nature 624, 570–578 (2023). DOI: 10.1038/s41586-023-06792-0

[23] Lála, J. et al. "PaperQA: Retrieval-Augmented Generative Agent for Scientific Research." arXiv:2312.07559 (2023).

[24] Wu, Q. et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." arXiv:2308.08155 (2023).

[25] Hong, S. et al. "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework." arXiv:2308.00352 (2023).

[26] Topoteretes/cognee. Self-Hosted Knowledge Graph and Memory for AI Agents. GitHub repository, 2026. https://github.com/topoteretes/cognee

[27] Fischer, U. et al. "EU DEMO design and R&D studies." Fusion Engineering and Design 167, 112381 (2021). DOI: 10.1016/j.fusengdes.2021.112381

[28] Shimwell, J. et al. "Multiphysics analysis with CAD-based parametric breeding blanket optimisation for DEMO." Nuclear Fusion 60, 076008 (2020). DOI: 10.1088/1741-4326/ab8d0b

[29] FENDL-3.2: Fusion Evaluated Nuclear Data Library. IAEA Nuclear Data Section, 2023. https://www-nds.iaea.org/fendl/

[30] OECD/NEA. "Benchmarks for Fusion Neutronics." NEA/NSC/DOC(2020). https://www.oecd-nea.org/

[31] Dey, N. et al. "A Critical Review on the Developments of Large Language Models for Scientific Discovery." arXiv:2506.15941 (2025).

[32] Anthropic. "Introducing Claude Code." Anthropic Blog, 2025. https://www.anthropic.com/

[33] Liu, N. et al. "From LLM to Agentic AI: A Survey of Autonomous Systems for Scientific Discovery." arXiv:2507.17287 (2025).

[34] Jimenez, C. E. et al. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" arXiv:2310.06770 (2023).

[35] Chen, M. et al. "Evaluating Large Language Models Trained on Code." arXiv:2107.03374 (2021).
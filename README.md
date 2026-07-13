# Fusion Agent Fleet 🚀

A multi-agent architecture for autonomous fusion nuclear engineering research — comprising **46 specialized agents**, **42 MCP servers**, and **33 crystallized skill workflows**.

This repository contains the agent definitions, skill workflows, shared instruction files, and portfolio validation scripts described in the paper:

> *"A Multi-Agent Architecture for Autonomous Fusion Nuclear Engineering Research"*
> Submitted to Nuclear Fusion (IOP Publishing, 2026)

## What's Here

| Directory | Contents | Count |
|-----------|----------|-------|
| [`agents/`](agents/) | Agent definition files (`.md` + `.meta.yaml`) with full architecture and delegation contracts | 46 |
| [`skills/`](skills/) | Crystallized reusable workflow definitions (`SKILL.md`) for scientific computing and fusion engineering | 33 |
| [`instructions/`](instructions/) | Shared policy and reference files consumed by agents | 51 |
| [`scripts/`](scripts/) | Portfolio validation scripts and infrastructure tooling | — |
| [`paper/`](paper/) | Manuscript source and supporting materials | — |

## What's NOT Here

This repository contains the **architectural blueprint** — agent definitions, skill descriptions, and validation logic. It does **NOT** include:

- HPC cluster configurations (SCNet profiles, Apptainer recipes)
- Model provider API keys or fallback proxy runtime configuration
- Internal project data, simulation results, or PM system records
- Docker/SIF image registries

These are maintained in a private infrastructure repository and are not required for understanding or validating the architecture described in the paper.

## Architecture Overview

The fleet is organized into a **four-tier delegation hierarchy**:

```
L0 — Gateway (2 agents)
  └── Single-source authorities for PM and HPC operations

L1 — Orchestrator (1 agent)
  └── Fusion Deep Research — end-to-end workflow coordination

L2 — Specialist (15 agents)
  └── Domain experts: simulation, literature, data analysis, review

L3 — Producer (19 agents)
  ├── External (8): papers, patents, proposals, presentations
  └── Internal (11): plan execution, gate running, documentation
```

Key innovations:
- **Sidecar metadata system** — 48% prompt compression via contract/schema separation
- **Five-chain model fallback** — GPT-5.5 → Claude → DeepSeek → Qwen → Ollama
- **Co-Scientist mechanisms** — Elo hypothesis tournament, meta-review, verify-heavy budget
- **Multi-layer QA** — 13 portfolio checks + 20 unit tests + 8 runtime quality gates

## Quick Start

```bash
# Run portfolio validation
bash scripts/validate-portfolio.sh

# Check delegation graph integrity
python3 scripts/check_agent_delegation_graph.py --max-depth 10 --max-agents 48

# Verify agent tool budgets
python3 scripts/check_agent_tool_budget.py

# Run unit tests
python3 -m pytest tests/ -v
```

## Paper

See [`paper/`](paper/) for the full manuscript. Key results:

| Scenario | Agents | Speedup | 95% CI |
|----------|--------|---------|--------|
| TBR Optimization | 8 | 15.0× | 6.8–23.2× |
| Literature Survey | 5 | 20.0× | 15.3–24.7× |
| Manuscript Draft | 5 | 30.0× | 26.5–33.5× |

## Citation

```bibtex
@article{fusion-agent-fleet-2026,
  title   = {A Multi-Agent Architecture for Autonomous Fusion Nuclear Engineering Research},
  author  = {[Author Name] and [Co-Author Name]},
  journal = {Nuclear Fusion},
  year    = {2026},
  note    = {Submitted}
}
```

See also [`CITATION.cff`](CITATION.cff).

## License

This repository is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

*Part of the copilot-agents ecosystem. Private infrastructure components not included.*

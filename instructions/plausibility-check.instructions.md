---
description: "plausibility-check MCP tool inventory: 5 tools for physical value validation against domain-specific ranges. Use for simulation output plausibility screening, numerical claim verification, and range lookups. 物理量合理性检查, 仿真输出范围验证, TBR/keff/DPA/SDR 值域检查, 自动格式检测."
applyTo: "simulation-analyst,simulation-builder,claim-verifier,citation-scanner,paper-reviewer,methodology-deep-reviewer,data-analyst"
revision: 1
---

# plausibility-check MCP Tool Inventory

**Core rule**: For structured simulation output validation (OpenMC, MCNP, FISPACT-II, YAML, JSON, CSV), use `plausibility-check/*` MCP tools. For scanning prose text to find inline numerical claims (e.g., "TBR = 1.12" in a manuscript paragraph), use `manuscript-lint/plausibility_check` instead — it regex-scans text, which plausibility-check MCP cannot do.

## Tool Inventory (5 tools)

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `check_value` | Validate a single quantity | `quantity` (required, e.g., `fusion.TBR`), `value` (required, number), `scenario` (optional, for OOM checks), `context` (optional) |
| `check_values` | Validate multiple quantities at once | `values` (required, dict `{name: number}`), `scenario` (optional), `min_level` (optional: `info`/`warning`/`error`) |
| `check_file` | Auto-detect file format, extract, and validate | `path` (required), `format` (optional hint: `auto`/`yaml`/`json`/`csv`/`openmc_csv`/`openmc_summary`/`mcnp_outp`/`mcnp_mctal`/`fispact_json`/`fispact_printlib`), `scenario`, `min_level` |
| `list_quantities` | List all defined ranges (13 quantities, 4 domains) | `ranges_path` (optional, for custom ranges) |
| `get_range` | Get range definition for one quantity | `quantity` (required, e.g., `nuclear_data.keff`), `ranges_path` (optional) |

## Quantity Naming Convention

Quantities use `domain.name` format:

| Domain | Quantities |
|--------|-----------|
| `fusion` | `TBR`, `nuclear_heating`, `dpa_rate`, `dose_rate` |
| `nuclear_data` | `keff`, `cross_section`, `flux`, `leakage` |
| `activation` | `total_activity`, `dose_rate`, `total_heat` |
| `material` | `density` |

## Verdicts

Each check returns a verdict:

| Verdict | Meaning |
|---------|---------|
| `PASS` | Value within normal range (PL-PASS) |
| `WARNING` | Value outside typical range but within absolute limits (PL-003/PL-004/PL-005/PL-008) |
| `FAIL` | Value outside absolute limits or non-physical (PL-001/PL-002/PL-006/PL-007) |
| `SKIP` | Quantity not recognized or range not defined (PL-000) |

## When to Use plausibility-check vs manuscript-lint

| Scenario | Use |
|----------|-----|
| Validate values extracted from simulation output files (statepoint, mctal, FISPACT JSON) | `plausibility-check/check_file` |
| Spot-check a specific quantity during analysis (e.g., "is TBR=1.12 reasonable?") | `plausibility-check/check_value` |
| Batch-validate multiple extracted quantities | `plausibility-check/check_values` |
| Look up what range is defined for a quantity | `plausibility-check/get_range` |
| Scan manuscript prose for inline numerical claims | `manuscript-lint/plausibility_check` |
| Verify numerical consistency across Abstract/Results/Tables | `manuscript-lint/numeric_consistency` |

## Fallback Policy

If the plausibility-check MCP server is unavailable:

1. Load `corpora/plausibility-ranges.yaml` (auto-generated snapshot, 13 quantities) using `read` tool
2. If that file is also unavailable, use inline defaults:
   - TBR: 0.8–1.5 (flag <0.5 or >2.0)
   - keff: 0–2 (flag <0.5 or >1.2)
   - Cross sections: positive and <10⁵ barn
   - Dose rate: ±2 OOM vs stated scenario
3. Annotate output: `⚠️ plausibility-check MCP unavailable — using fallback`

## Common Calling Patterns

### Single value check
```
plausibility-check/check_value(quantity="fusion.TBR", value=1.12)
→ {"verdict": "PASS", "rule": "PL-PASS", ...}
```

### Batch check after extraction
```
plausibility-check/check_values(
  values={"fusion.TBR": 1.12, "nuclear_data.keff": 0.95, "activation.total_activity": 3.2e15},
  scenario="HCPB blanket, 1 year cooling"
)
```

### Auto-detect simulation output
```
plausibility-check/check_file(path="/path/to/mctal", min_level="warning")
```

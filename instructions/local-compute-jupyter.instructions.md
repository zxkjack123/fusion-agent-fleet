---
description: "When to use Jupyter MCP kernel for local small-scale computation vs HPC submission. 本地计算：何时使用 Jupyter kernel 做小规模本地验证 vs 提交 HPC 大规模计算。"
applyTo: "**"
version: 1
revision: 1
---

# Local Compute via Jupyter — 本地 Jupyter 计算指南

## When to Use

- OpenMC test runs with < 100 batches — quick convergence check before HPC
- Data fitting and small-scale curve analysis
- Rapid visualization of tally or statepoint data
- MCNP input file validation (single particle run)
- Parameter space exploration before full parametric sweep

## When NOT to Use

- Large-scale HPC computation (> 1 node, > 1000 batches) — use `scnet-hpc-coordinator`
- Multi-hour calculations — Jupyter kernel timeout will kill them
- Production runs that need reproducibility — use experiment-tracker + HPC

## Workflow

1. **Connect**: `jupyter/use_notebook(notebook_name="local_test", notebook_path="local_test.ipynb", mode="create")`
2. **Execute**: `jupyter/execute_code(code="import openmc; ...", timeout=60)`
3. **Iterate**: Multiple `execute_code` calls for multi-step analysis
4. **Read**: `jupyter/read_notebook(notebook_name="local_test", response_format="detailed")` — extract results
5. **Cleanup**: `jupyter/unuse_notebook(notebook_name="local_test")` when done

## Fallback

If Jupyter MCP is unavailable: use `bash` + `python3 -c "<code>"` for single-line execution, or `cat << 'EOF' | python3` for multi-line scripts.

## Integration

- `simulation-builder`: Stage A → suggest local convergence test before full HPC
- `data-analyst`: initial data exploration → use Jupyter before committing to full analysis pipeline

## References

- `jupyter` MCP server — already connected in `~/.config/opencode/opencode.jsonc`
- `scnet-hpc-coordinator` — for large-scale HPC, complement to this instruction

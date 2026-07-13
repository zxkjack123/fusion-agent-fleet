#!/usr/bin/env bash
# validate-portfolio.sh — OpenCode-first portfolio health check
# Exit code: 0 = all checks pass, 1 = at least one check failed

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0
WARN=0

pass() { echo "  ✅ PASS: $1"; ((PASS++)) || true; }
fail() { echo "  ❌ FAIL: $1"; ((FAIL++)) || true; }
warn() { echo "  ⚠️  WARN: $1"; ((WARN++)) || true; }

run_warnable_check() {
    local label="$1"
    local warn_message="$2"
    local fail_message="$3"
    shift 3

    set +e
    "$@"
    local status=$?
    set -e

    case "$status" in
        0) pass "$label" ;;
        1) warn "$warn_message" ;;
        *) fail "$fail_message" ;;
    esac
}

AGENT_DIR=".opencode/agent"
CONTEXT_DIR=".opencode/context"

echo "Check 1: OpenCode agent registry"
if [[ ! -d "$AGENT_DIR" ]]; then
    fail "$AGENT_DIR missing"
    AGENT_COUNT=0
else
    AGENT_COUNT=$(find "$AGENT_DIR" -maxdepth 1 -name '*.md' | wc -l)
    if [[ "$AGENT_COUNT" -gt 0 ]]; then
        pass "OpenCode project registry has $AGENT_COUNT agents"
    else
        fail "OpenCode project registry is empty"
    fi
fi

echo ""
echo "Check 2: OpenCode frontmatter parse"
if python3 - <<'PY'
from pathlib import Path
import yaml

failures = []
checked = 0
for path in sorted(Path('.opencode/agent').glob('*.md')):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        failures.append(f'{path}: missing opening ---')
        continue
    end = text.find('\n---', 4)
    if end == -1:
        failures.append(f'{path}: missing closing ---')
        continue
    checked += 1
    try:
        data = yaml.safe_load(text[4:end]) or {}
    except Exception as exc:
        failures.append(f'{path}: {exc}')
        continue
    for key in ('name', 'description', 'mode', 'model'):
        if not data.get(key):
            failures.append(f'{path}: missing {key}')
    if data.get('name') != path.stem:
        failures.append(f'{path}: name must equal file stem {path.stem!r}')
    if data.get('mode') != 'all':
        failures.append(f'{path}: mode must be all')

if failures:
    print(f'FAIL: {len(failures)} frontmatter issue(s):')
    for failure in failures:
        print(f'  - {failure}')
    raise SystemExit(1)
print(f'PASS: {checked} OpenCode frontmatter blocks parsed strictly')
PY
then
    pass "OpenCode frontmatter parse — all agents parse"
else
    fail "OpenCode frontmatter parse failed — see output above"
fi

echo ""
echo "Check 3: Instruction frontmatter"
INSTR_COUNT=0
for f in instructions/*.instructions.md; do
    [[ -f "$f" ]] || continue
    ((INSTR_COUNT++)) || true
    header=$(head -10 "$f")
    has_desc=$(echo "$header" | grep -c '^description:' || true)
    has_apply=$(echo "$header" | grep -c '^applyTo:' || true)
    [[ "$has_desc" -gt 0 ]] && pass "$f — frontmatter OK" || fail "$f — missing description"
    [[ "$has_apply" -gt 0 ]] || warn "$f — missing applyTo"
done

echo ""
echo "Check 4: Skill SKILL.md template compliance"
SKILL_COUNT=0
REQUIRED_SECTIONS=("When to Use" "When NOT to Use" "Workflow" "Common Pitfalls" "Revision Log")
for f in skills/*/SKILL.md; do
    [[ -f "$f" ]] || continue
    ((SKILL_COUNT++)) || true
    has_name=$(head -20 "$f" | grep -c '^name:' || true)
    has_desc=$(head -20 "$f" | grep -c '^description:' || true)
    has_rev=$(head -20 "$f" | grep -c '^revision:' || true)
    [[ "$has_name" -gt 0 ]] || fail "$f — missing name"
    [[ "$has_desc" -gt 0 ]] || fail "$f — missing description"
    [[ "$has_rev" -gt 0 ]] || fail "$f — missing revision"
    for section in "${REQUIRED_SECTIONS[@]}"; do
        grep -q "^## $section" "$f" || fail "$f — missing ## $section"
    done
    [[ "$has_name" -gt 0 && "$has_desc" -gt 0 && "$has_rev" -gt 0 ]] && pass "$f — frontmatter OK"
done

echo ""
echo "Check 5: Delegation graph semantics"
run_warnable_check \
    "Delegation graph — no hard failures" \
    "Delegation graph warnings detected — see output above" \
    "Delegation graph hard failure detected — see output above" \
    python3 scripts/check_agent_delegation_graph.py

echo ""
echo "Check 6: OpenCode permission surface"
run_warnable_check \
    "OpenCode permissions — all agents within OK threshold" \
    "OpenCode permission warnings detected — not a hard portfolio failure" \
    "OpenCode permission hard failure detected — see output above" \
    python3 scripts/check_agent_tool_budget.py

echo ""
echo "Check 7: Delegation contract consistency"
if python3 scripts/check_delegation_contracts.py; then
    pass "Delegation contracts consistent"
else
    fail "Delegation contract mismatches detected"
fi

echo ""
echo "Check 8: Outbound delegation schema coverage"
if python3 scripts/check_delegation_contracts.py --require-outbound-coverage; then
    pass "Outbound delegation schema coverage complete"
else
    fail "Outbound delegation schema coverage incomplete"
fi

echo ""
echo "Check 9: Sub-agent return envelope v1"
if python3 scripts/check_subagent_return_envelopes.py; then
    pass "Return envelope v1 — all agents compliant"
else
    fail "Return envelope v1 — agents missing required fields"
fi

echo ""
echo "Check 10: OpenCode project registry validation"
if python3 scripts/check_opencode_export.py --target project; then
    pass "OpenCode project registry validates"
else
    fail "OpenCode project registry validation failed"
fi

echo ""
echo "Check 11: CONSTITUTION.md See-Also references"
if [[ -f CONSTITUTION.md ]] && [[ -f scripts/check_constitution_refs.py ]]; then
    if python3 scripts/check_constitution_refs.py; then
        pass "CONSTITUTION.md See-Also references — no FAIL"
    else
        fail "CONSTITUTION.md See-Also validation failed"
    fi
else
    warn "CONSTITUTION.md or check_constitution_refs.py missing — skipped"
fi

echo ""
echo "Check 12: Delivery tier allowlist"
if python3 scripts/check_tier_allowlist.py; then
    pass "Delivery tier allowlist — all agents within canonical set"
else
    fail "Delivery tier allowlist violation"
fi

echo ""
echo "Check 13: Guardrail regression harness"
if python3 scripts/run_harness.py; then
    pass "Guardrail harness — all regression tests pass"
else
    fail "Guardrail harness — regression detected"
fi

echo ""
echo "Check 15: Numerical intuition references (direct agent wiring)"
# These agents must have DIRECT references (not just AGENTS.md centralized)
DIRECT_WIRED_AGENTS="doublecheck fusion-chain-runner"
MISSING=0
for agent in $DIRECT_WIRED_AGENTS; do
    if ! grep -q "numerical-intuition-pitfalls" ".opencode/agent/${agent}.md" 2>/dev/null; then
        warn "$agent missing numerical-intuition-pitfalls direct reference"
        MISSING=1
    fi
done
# These agents get numerical intuition via AGENTS.md centralized injection
CENTRALIZED_AGENTS="simulation-builder simulation-analyst"
if [ "$MISSING" -eq 0 ]; then
    pass "Numerical intuition pitfalls — all directly-wired agents OK"
else
    fail "Numerical intuition pitfalls — direct references missing"
fi
# Verify AGENTS.md has the centralized reference for the other agents
if grep -q "numerical-intuition-pitfalls" AGENTS.md 2>/dev/null; then
    pass "Numerical intuition pitfalls — AGENTS.md centralized injection active"
else
    warn "Numerical intuition pitfalls — AGENTS.md centralized injection missing"
fi

echo ""
echo "Check 14: OpenCode routing context"
if [[ -f "$CONTEXT_DIR/opencode-agent-routing.md" ]]; then
    pass "OpenCode routing context present"
else
    fail "OpenCode routing context missing"
fi

echo ""
echo "=========================================="
echo " Portfolio Summary"
echo "=========================================="
echo "  OpenCode Agents: $AGENT_COUNT"
echo "  Instructions:    $INSTR_COUNT"
echo "  Skills:          $SKILL_COUNT"
echo "  ──────────────────────────"
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo "  WARN: $WARN"
echo "=========================================="

if [[ "$FAIL" -gt 0 ]]; then
    echo "❌ Portfolio validation FAILED ($FAIL failures)"
    exit 1
else
    echo "✅ Portfolio validation PASSED"
    exit 0
fi

echo ""
echo "Check 16: AGENTS.md Mandatory Rules -- high-priority agents enforce"
# DeepSeek agents that MUST have Reconciliation (high-risk, Level-A/B)
DS_MUST_RECONCILE="data-analyst diagram-architect doublecheck format-engineer fusion-chain-runner ip-protection-advisor prior-art-semantic-reviewer scientific-paper-research simulation-analyst simulation-builder"
MISSING_DS=0
for agent in $DS_MUST_RECONCILE; do
    if ! grep -q "Reconciliation\|post-tool" ".opencode/agent/${agent}.md" 2>/dev/null; then
        warn "DeepSeek agent $agent missing Reconciliation reference"
        MISSING_DS=1
    fi
done
if [ "$MISSING_DS" -eq 0 ]; then
    pass "Post-Tool Reconciliation -- all high-risk DeepSeek agents wired"
else
    fail "Post-Tool Reconciliation -- high-risk DeepSeek agents missing"
fi

# Producer-external agents that MUST have numerical-intuition or doublecheck gate
PE_MUST_PROTECT="academic-writer literature-reviewer patent-writer proposal-writer review-responder teaching-assistant"
MISSING_PE=0
for agent in $PE_MUST_PROTECT; do
    has_ni=0
    has_dc=0
    grep -q "numerical-intuition\|numerical intuition" ".opencode/agent/${agent}.md" 2>/dev/null && has_ni=1
    grep -q "doublecheck" ".opencode/agent/${agent}.md" 2>/dev/null && has_dc=1
    if [ "$has_ni" -eq 0 ] && [ "$has_dc" -eq 0 ]; then
        warn "producer-external $agent missing numerical-intuition AND doublecheck"
        MISSING_PE=1
    fi
done
if [ "$MISSING_PE" -eq 0 ]; then
    pass "Producer-external agents -- numerical-intuition or doublecheck gate wired"
else
    warn "Producer-external agents -- some unprotected"
fi

echo ""
echo "Check 17: Skills -- all SKILL.md files structurally valid"
if python3 scripts/smoke_test_skills.py; then
    pass "Skills -- all SKILL.md files structural valid"
else
    fail "Skills -- SKILL.md validation failed"
fi

echo ""
echo "Check 18: Cross-agent reference chains"
if python3 scripts/cross_agent_regression.py --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(d['broken_chains'])" 2>/dev/null; then
    pass "Cross-agent chains -- all intact"
else
    warn "Cross-agent chains -- broken chains detected (check 18)"
fi

echo ""
echo "Check 19: Physical benchmark validator"
# Quick smoke test: known good + known bad
GOOD=$(python3 scripts/benchmark_physical_quantities.py --json '{"TBR":1.15,"keff":1.0,"flux":1e14}' 2>&1)
BAD=$(python3 scripts/benchmark_physical_quantities.py --json '{"TBR":0.2}' 2>&1)
if echo "$GOOD" | grep -q "PASS" && echo "$BAD" | grep -q "FAIL"; then
    pass "Physical benchmark -- validator detects FAIL correctly"
else
    fail "Physical benchmark -- validator malfunction"
fi

echo ""
echo "Check 20: Document freshness — key docs within threshold"
if python3 scripts/check_doc_freshness.py --quiet 2>/dev/null; then
    pass "Document freshness — all key docs FRESH"
else
    warn "Document freshness — some docs stale or expired"
fi

echo ""
echo "Check 21: Per-agent readiness — producer-tier agents"
PRODUCER_AGENTS=""
for sidecar in .opencode/agent/*.meta.yaml; do
    [[ -f "$sidecar" ]] || continue
    tier=$(grep -m1 '^delivery_tier:' "$sidecar" 2>/dev/null | sed 's/delivery_tier:[[:space:]]*"\?\([^"]*\)"\?/\1/' || echo "")
    if [[ "$tier" == "producer-external" || "$tier" == "producer-internal" ]]; then
        agent_name=$(basename "$sidecar" .meta.yaml)
        PRODUCER_AGENTS="$PRODUCER_AGENTS $agent_name"
    fi
done
READY_FAIL=0
READY_PASS=0
for agent in $PRODUCER_AGENTS; do
    set +e
    python3 scripts/check_agent_readiness.py --agent "$agent" > /dev/null 2>&1
    status=$?
    set -e
    if [[ "$status" -eq 0 ]]; then
        READY_PASS=$((READY_PASS + 1))
    else
        warn "Readiness check: $agent — warnings or failures"
        READY_FAIL=$((READY_FAIL + 1))
    fi
done
if [[ "$READY_FAIL" -eq 0 ]]; then
    pass "Agent readiness — all $READY_PASS producer agents PASS"
else
    warn "Agent readiness: $READY_FAIL producer agents have warnings or failures ($READY_PASS passed)"
fi

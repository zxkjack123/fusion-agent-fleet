---
description: "Skill crystallization protocol: auto-detect reusable multi-step workflows and propose solidifying them as SKILL.md files. 工作流结晶协议, 自动识别可复用工作流并提议固化为 Skill, 工具调用链检测, repo memory 模式追踪, SKILL 版本迭代."
applyTo: "**"
revision: 1
---

# Skill Crystallization Protocol — 工作流结晶协议

## Trigger Conditions — 触发条件

After completing a task, check the following. Trigger if **any** condition is met:

| ID | Condition | Detection |
|----|-----------|-----------|
| T1 | Current task involved ≥5 distinct tool-call steps (exclude pure search/read chains) | Best-effort self-count of tool calls in current session |
| T2 | Task pattern matches an entry in `/memories/repo/workflow-patterns.md` that already has ≥2 occurrences | Read repo memory, compare task signature |
| T3 | User explicitly says "固化" / "做成 skill" / "crystallize" / "I'll do this again" | Intent recognition |

T1 is best-effort — false negatives are acceptable. T3 is the most reliable trigger.

## Confidence Scoring — 置信度评分

When recording or evaluating workflow patterns (T2 detection), use a 置信度 (confidence) score instead of a raw occurrence count to decide whether to propose crystallization.

### Confidence Scale

| Level | Score | Criterion |
|-------|-------|-----------|
| Tentative | 0.3 | First occurrence; single session, no corroboration |
| Moderate | 0.5 | 2 occurrences OR 1 occurrence with strong evidence (complex tool chain, user expressed intent to repeat) |
| Strong | 0.7 | ≥3 occurrences within 90 days, or 2 occurrences with explicit user positive feedback |
| Near-certain | 0.9 | ≥4 occurrences within 60 days with consistent tool chain across sessions |

### Evidence Chain

Each time a workflow pattern is recorded in `/memories/repo/workflow-patterns.md`, append an evidence entry:

```
| signature | count | confidence | last_seen | evidence |
|-----------|-------|------------|-----------|----------|
| openmc-dagmc-build | 3 | 0.7 | 2025-07-10 | [2025-06-15: DAGMC mesh build, 2025-07-01: TBM model rebuild, 2025-07-10: blanket parametric sweep] |
```

**Backward compatibility**: Existing entries with only `signature | count` columns are valid. Missing fields default to: `confidence = 0.5`, `last_seen = unknown`, `evidence = []`. Do not require migration of old records.

### Auto-Proposal Threshold

- Confidence ≥ 0.7 → automatically propose crystallization (equivalent to the original T2 trigger with ≥2 occurrences, plus recency validation)
- Confidence < 0.7 → record silently, do not propose

### Decay Rule

- If a pattern has not been observed for **90 days** since `last_seen`, decrease its confidence by one level (e.g., 0.7 → 0.5)
- Decayed patterns below 0.3 are archived (moved to a `## Archived` section in workflow-patterns.md), not deleted
- Any new occurrence resets the decay timer and re-evaluates confidence from scratch

## Protocol — 执行流程

**Detect** → After task completion, check T1/T2/T3. If none met, **Skip** silently (no output).

**Propose** → If any trigger fires:
1. Summarize the detected pattern in 1–2 sentences.
2. Ask: "这个工作流可以固化为 Skill — 是否创建？" Include proposed skill name and scope.
3. **Wait for user confirmation.** Do NOT create without approval.

**Crystallize** → On user confirmation:
1. Read `docs/skill-crystallization.md` for the full SKILL.md template.
2. Generate `skills/<skill-name>/SKILL.md` with content adapted from the actual task (not copied verbatim from template).
3. Append record to `/memories/repo/crystallized-skills.md`.
4. Record task signature in `/memories/repo/workflow-patterns.md` if not already present.

## Storage — 存放路径

All crystallized skills go to `skills/<skill-name>/SKILL.md`. The `skills/` directory is created on-demand at first crystallization. This path is discovered by OpenCode when the repo is symlinked to `~/.config/Code/User/prompts/`.

## Self-Improvement — 自改进

After using a SKILL.md to complete a task, compare actual execution against the documented workflow. If improvements are found (new steps, removed steps, new pitfalls):
1. Propose: "Skill `<name>` 有改进点 — 是否更新？"
2. On confirmation: increment `revision` in frontmatter, update content, append to Revision Log.
3. If no improvements, stay silent.

## Repo Memory — 记忆文件

| File | Purpose |
|------|---------|
| `/memories/repo/workflow-patterns.md` | Task signatures + occurrence count (for T2 detection) |
| `/memories/repo/crystallized-skills.md` | Registry of crystallized skills (prevents duplicate proposals) |

If either file does not exist, create it. If corrupted, rebuild from scratch and notify user.

## Expert Review Pattern Capture — 专家审阅模式捕获

When an expert (user, domain reviewer, PI) provides substantive feedback that reveals a reusable review heuristic, propose capturing it as an expert pattern in `memories/expert-review-patterns.md`. This is a **lightweight capture** (not a full skill crystallization).

**Trigger**: Expert feedback contains a **generalizable rule**, not just a specific correction:
- "Innovation points should thread through all proposal sections" → **generalizable** → capture
- "Change '15%' to '18%' on line 42" → specific fix → do NOT capture

**Capture format** (append to `memories/expert-review-patterns.md`):
```markdown
### P<N>: <short descriptive title>
- **Source**: <feedback metadata>
- **Quoted wisdom**: "<exact quote>"
- **Trigger scenario**: <when this pattern applies>
- **Checklist**: <specific items to verify>
- **Severity**: critical / important / nice-to-have
```

**Convergence detection**: When an expert pattern has been independently confirmed by ≥2 different reviewers OR ≥3 separate instances of the same feedback, propose crystallization into a full skill.

**False positives to avoid**: Do NOT capture domain trivia ("TBR is usually higher in Li2TiO3 than Li4SiO4") — capture patterns that improve agent execution, not domain facts. Domain facts go to `instructions/numerical-intuition-pitfalls.instructions.md`.

## SKILL.md Required Structure

Frontmatter: `name`, `description` (bilingual keywords), `revision` (integer, starts at 1). Required sections: **When to Use**, **When NOT to Use**, **Workflow**, **Inputs & Outputs**, **Common Pitfalls**, **Revision Log**. See `docs/skill-crystallization.md` for the full template and writing guidelines.

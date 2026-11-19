---
description: Revise an existing plan in-place after /challenge-plan (surgical edit, read-only on source code)
argument-hint: [empty if /challenge-plan just ran, OR openspec:<change-name>, OR PLAN_<slug>.md path]
allowed-tools: Read, Grep, Glob, Edit, Bash(git log:*), Bash(git diff:*), Bash(graphify:*)
# Edit is scoped to PLAN_*.md at repo root OR OpenSpec artifacts under
# openspec/changes/<name>/. No source files may be written. The plan source is
# created by /diagnose or /opsx:propose and modified in place here — git holds
# the version history.
---

$ARGUMENTS

**When to use manually**: apply corrections yourself — typically when you
interrupted the `/challenge-plan` auto-cycle (a decision was escalated), or
before re-challenging. In a normal auto-cycle, `/challenge-plan` runs the refine
step inline.

**You are the main agent** — no subagent dispatch. You have full session context
(original plan + critique) and surgically edit the active plan source
(`PLAN_<slug>.md` at repo root in PLAN mode, or the OpenSpec artifacts in
OpenSpec mode).

## Input resolution

You need the **plan source** and the **`/challenge-plan` critique**.

- **OpenSpec mode** (`openspec:<name>`, or empty after an OpenSpec challenge):
  route each critique point — scope/why → `proposal.md`, architecture/how →
  `design.md`, task breakdown → `tasks.md` (under `openspec/changes/<name>/`).
- **PLAN mode**: `$ARGUMENTS` is a path → that `PLAN_*.md`; empty → retrieve the
  last plan path + last critique from the session; prose/pasted → refuse (the
  critique is read from the session; pass the path alone). If the path or
  critique is missing, ask — do not guess.

The plan already exists on disk. Do **not** recreate it — edit in place.

## Step 1 — Counter-validate the diagnosis

Before touching the plan, question the root cause. Invoke
`superpowers:systematic-debugging` in light of the critique:

- Do the 🔴 points indicate a wrong root cause, or just wrong execution?
- Do cited existing patterns suggest a different approach?
- 3+ 🔴 in the same area → may be architectural (Phase 4.5 of
  systematic-debugging), not execution.

If the diagnosis must change, state it in chat and reflect it by editing the
relevant sections (no "v2" marker — git tracks versions).

## Step 2 — Triage the critique

| Decision | When | Action |
| --- | --- | --- |
| ✅ Accepted | valid, correction obvious | surgical `Edit` on the impacted section |
| 🔄 Accepted w/ adaptation | valid but suggested fix doesn't fit | different correction via `Edit`, explain in chat |
| ❌ Rejected | invalid / out of scope / misunderstanding | no edit; justify in chat (1–2 sentences) |
| ❓ Needs clarification | real ambiguity changing the fix's nature | **STOP**, ask before editing |

Do not accept out of politeness.

## Step 3 — Clarifying questions

Ask before editing only if: multiple valid approaches with real trade-offs; the
correction changes numeric model output or user-facing behavior; the critique
touches a god node and the impacted consumers are unknown; two points
contradict; or the critique rejects a choice the user explicitly validated.
One question at a time, 2–3 options + recommendation.

## Step 4 — Surgical edits

`Read` the plan source first so `old_string` matches byte-for-byte. Edit only
the smallest blocks the critique flagged (📝 BEFORE/AFTER, ✨ file add/remove,
🗑️ deletion target, 🧪 RED/GREEN tests, `REUSES:` paths). Do **not** rewrite
untouched sections or add a "summary of changes" block.

### Coherence checklist (self-check)

- Every 🔴 is addressed by an `Edit` or rejected with justification.
- Edited sections stay coherent (no dangling cross-reference / orphaned `REUSES:`).
- No new duplication or dead code.
- Cited paths/symbols exist (verify with Read/Grep/graphify).
- YAGNI still respected.
- `CLAUDE.md` respected: full type hints (mypy strict), flake8 complexity ≤ 10,
  Black 120, constants over magic numbers, tests mirror `RUFAS/`, `pip`/`pytest`.
- No edit to the protected `example_*.json` / `no_*.json` input files under
  `input/` (input JSON only — never `tests/`).
- Every task carries an `**EDITS**:` line with ≥ 1 path that resolves on disk
  (or appears under a `✨`/`🧪` creation marker). A dangling path is blocking.
- For each `**PARALLEL_GROUP**: X`, the `EDITS` across tasks with that letter are
  pairwise disjoint; no tagged task touches a pivot (`general_constants.py`,
  `input_manager.py`, `output_manager.py`, `data_validator.py`,
  `simulation_engine.py`, `task_manager.py`, any `__init__.py`, `pyproject.toml`,
  `changelog.md`). Strip the tag if violated.

## Chat output

After edits land, print exactly:

> Plan updated. Run `/challenge-plan` (PLAN) or `/challenge-plan openspec:<name>`
> (OpenSpec) to re-validate.

Then add any rejection justifications (after that line, not in the plan file).

## Constraints

- Read-only for source code; edits scoped to the plan source; no commits.
- Surgical edits, not rewrite. If tempted to rewrite the whole file, stop and
  question the diagnosis (Step 1).
- No capitulation: reject wrong critiques with reasons. No scope expansion.

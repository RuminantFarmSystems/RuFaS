---
description: Counter-validate a plan (read-only, via fresh-context subagent)
argument-hint: [plan file path, OR openspec:<change-name>, OR <change-name>, OR empty]
allowed-tools: Read, Grep, Glob, Agent, Bash(graphify:*)
---

$ARGUMENTS

## Plan resolution

Identify the plan to counter-validate. Resolution is **path-only** — inline plan
bodies are refused (re-embedding a plan into the `Agent` tool-call argument
causes `Stream idle timeout` on plans above a few KB).

### OpenSpec path

1. If `$ARGUMENTS` matches `openspec:<name>` OR is a bare kebab-case word AND
   `openspec/changes/<name>/` exists → resolve the artifacts:
   `openspec/changes/<name>/proposal.md`, `design.md`, `tasks.md`.
   Verify all three with `Read`; if any is missing, tell the user to run
   `/opsx:propose` first. Store `mode: openspec`, `change_name: <name>`.
2. Else if `$ARGUMENTS` is empty → `Glob openspec/changes/*/tasks.md`. If exactly
   one change exists and no `PLAN_*.md` is present, offer to validate it with
   `/challenge-plan openspec:<name>`. Stop, wait for the choice.

### PLAN_*.md path

1. `$ARGUMENTS` is a file path → resolve to that file.
2. Empty → `Glob PLAN_*.md` at repo root; if one matches the session topic, use
   it; if several, list them and ask which.
3. Prose / pasted plan / non-path → **refuse**: run `/diagnose` to produce the
   plan natively on disk (it follows the write strategy that avoids timeouts), or
   pass a `PLAN_<slug>.md` path. Do not dispatch this turn.

## Dispatch

### Pre-dispatch file verification (non-negotiable)

**OpenSpec mode**: `Read` all three artifacts; refuse if any is missing/empty.
**PLAN mode**: `Read` the resolved file. Refuse (do not dispatch) if it errors,
is empty, doesn't start with `## Plan —`, lacks any `📝`/`✨`/`🗑️`/`🧪` marker,
or has no `REUSES` section — these mean `/diagnose` timed out or wrote a stub.

### Dispatch

Dispatch a subagent (`subagent_type: general-purpose`) with **fresh context**
(it does not see session history). Pass the plan **by path** (never inline the
body). You do not evaluate yourself — the subagent is the critic.

The subagent must:

1. Invoke `superpowers:requesting-code-review` as the framework.
2. `Read`/`Grep`/`graphify` the files the plan cites to verify imports,
   functions, managers, and connection objects actually exist. A plan that
   invents paths/symbols is blocking.
3. Produce a severity-structured report — exact quote from the plan + a
   suggested correction per point:

   🔴 BLOCKING
   - Logic bug, inverted condition, unhandled `None`
   - Regression: breaks an existing consumer of shared code (especially a god
     node — `OutputManager`, `GeneralConstants`, `RufasTime`, `InputManager`)
   - Cited import / function / class that does not exist
   - Unintended change to numeric model output, or a broken mass/nutrient
     balance, without justification
   - Edits a protected input JSON file under `input/`
     (`.claude/rules/protected-inputs.md`) — input JSON only, never `tests/`
   - Introduces new mypy-strict errors (CI ratchets the count vs `dev`)

   🟠 IMPORTANT
   - Over-engineering: premature abstraction, new module for a few lines
   - Duplication: existing helper/manager/connection not reused (check
     `util.py`, `*_manager.py`, `RUFAS/data_structures/`, `units.py`)
   - Dead code: unused functions, unreachable branches
   - Missing or partial type hints (mypy strict will reject untyped defs)
   - flake8 complexity > 10 in a touched function (refactor, don't suppress)
   - Magic numbers instead of a constant in a `*_constants.py` / `general_constants.py`
   - Unit mishandling — raw numbers where `units.py` conversions belong
   - Non-compliant tests: not mirroring `RUFAS/` under `tests/`, not using
     `pytest-mock` / fixtures, not `freezegun` for time-dependent logic
   - No `changelog.md` entry planned (CI requires one on every PR)

   🟡 MINOR
   - Naming inconsistent with the module
   - Comments redundant with the code
   - Formatting that Black will fix at commit

4. Verify plan internal consistency: type/function signatures match across
   steps; tests cover the fix (not just the happy path); ambiguous decisions
   were escalated to the user; YAGNI; `REUSES:` references real code.
5. Final verdict on a single line:
   - ✅ **APPROVED** — no 🔴, 🟠 absent or acceptable
   - ⚠️ **APPROVED WITH RESERVATIONS** — no 🔴, 🟠 to fix
   - ❌ **NEEDS REVISION** — at least one 🔴

## Post-dispatch behavior — first run

1. Print the critique (relay, never re-run the review yourself).
2. If **✅ APPROVED** or only 🟡 → print "✅ Plan approved. Run `/apply-plan`
   (PLAN) or `/apply-plan openspec:<name>` (OpenSpec) when ready." End the turn.
3. If **❌** or **⚠️ with 🟠** → start the auto-cycle.

## Auto-cycle — refine + re-challenge (up to 5 iterations)

```text
CYCLE = 1
loop:
  1. Print "─── Auto cycle CYCLE/5 — refining… ───"
  2. Invoke superpowers:refine-plan (reads last critique, edits the plan source;
     if a decision is needed → STOP, ask the user, exit loop)
  3. Print "─── Auto cycle CYCLE/5 — re-validating… ───"
  4. Dispatch a new challenge subagent (same rules as ## Dispatch)
  5. Print the critique
  6. Stopping conditions (below) → may STOP
  7. CYCLE += 1; repeat
```

Stopping conditions: ✅ APPROVED or only 🟡 → print "✅ approved after N
cycle(s), run /apply-plan" and stop. Decision needed → stop and ask. CYCLE = 5
with 🔴/🟠 still present → escalate (summarize persistent points + probable
cause + options: rethink via `/diagnose`, accept current state if no 🔴, or
continue manually via `/refine-plan` + `/challenge-plan`). Stop.

## Constraints (non-negotiable)

- **Source code is read-only**: no edits outside `PLAN_*.md` (PLAN mode) or
  `openspec/changes/<name>/` (OpenSpec mode, via `refine-plan` in the cycle).
- Respect `CLAUDE.md`: `pip`/`pytest`/`mypy`/`flake8` (not Bun/vitest), Grep
  tool not `grep` in Bash, tests mirror `RUFAS/`.
- **No performative criticism**: if the plan is good, say so. Don't fabricate
  🟠 to justify the review.
- **Subagent is critic only** — corrections are applied by
  `superpowers:refine-plan` in the auto-cycle.
- Never inline the plan body into the subagent prompt — it reads the bytes on
  disk by path.

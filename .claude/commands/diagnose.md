---
description: Diagnose, produce a fix plan, and persist it to PLAN_<slug>.md
argument-hint: [description, file path, or paste logs]
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(git log:*), Bash(git diff:*), Bash(git rev-parse:*), Bash(graphify:*)
# Write and Edit are scoped to PLAN_<slug>.md at repo root. No source
# file may be written by this command. The incremental write strategy
# (see ### Write strategy) uses Write for the header and Edit for each
# subsequent section append — both required to avoid a monolithic-write
# timeout.
---

$ARGUMENTS

## Step 1 — Silent analysis

Invoke `superpowers:systematic-debugging` to find the root cause, then
`superpowers:writing-plans` to draft the plan structure internally.

For architecture / "how does X reach Y" questions, prefer the graph
(`graphify query/path/explain`) over scanning the large modules
(`output_manager.py`, `data_validator.py`, `input_manager.py`).

**Read-only at this stage**: explore with Read, Grep, Glob, graphify only.
No files may be written until Step 3.

## Step 2 — Interactive confirmation

Before writing anything to disk, confirm direction with the user.

Ask 2–4 targeted questions about:

- The root cause identified ("I found X as the cause — is that the observed
  problem?")
- Scope or behavior ambiguities (does it change numeric model outputs?).
- Preferred approach when multiple valid solutions exist: present 2–3 concrete
  options with trade-offs and a recommendation.

One question set per message. **Wait for the user's answers before continuing.**

## Constraints

- **Do not modify source files.** The only write allowed is the final
  `PLAN_<slug>.md` at repo root (Step 3).
- Respect `CLAUDE.md`: full type hints (mypy strict), Black line-length 120,
  flake8 complexity ≤ 10, use the Grep tool (not `grep` in Bash), `pip` not Bun.
- YAGNI: the minimum required to fix the identified problem, nothing more.
- Never plan an edit to a protected input JSON file under `input/`
  (`.claude/rules/protected-inputs.md`) — input JSON only, never `tests/`.

## Step 3 — Persist

Once the user confirms the direction, write the plan to disk.

### Per-task required fields

Every task block (📝/✨/🗑️/🧪) MUST carry these fields, immediately under the
block's `**File**:` line:

- `**EDITS**:` — comma-separated repo-relative paths the task creates, modifies,
  or deletes. Required even for single-file tasks. Used by `/apply-plan` §2.0
  for file-set overlap detection.
- `**READS**:` (optional) — paths the task reads but does not modify at apply
  time (runtime dependency or consistency cross-reference).
- `**PARALLEL_GROUP**: <letter>` (optional, opt-in) — tag tasks whose read-only
  phases may run in parallel under `/apply-plan`. Same-letter tasks must have
  **disjoint** `EDITS` and must **not** touch any pivot:
  - `RUFAS/general_constants.py`, `RUFAS/user_constants.py`
  - `RUFAS/input_manager.py`, `RUFAS/output_manager.py`,
    `RUFAS/data_validator.py`, `RUFAS/simulation_engine.py`,
    `RUFAS/task_manager.py`
  - any `__init__.py`
  - `pyproject.toml`, `changelog.md`
    Untagged tasks always run individually.

### Slug derivation

From the plan title, derive `<slug>` as kebab-case, ASCII only, ≤ 40 chars.
E.g. "Fix DMI domain check in manure equations" → `fix-dmi-domain-manure-eqs`.

### Collision handling (non-negotiable)

Before writing, `Glob PLAN_<slug>.md` at repo root.

- **No existing file** → write `PLAN_<slug>.md` verbatim, following the write
  strategy below.
- **File present** → **STOP**. Do not overwrite, do not auto-suffix. Ask the
  user: choose a different slug, overwrite, or abort. Wait for the answer.

### Write strategy (non-negotiable)

Plans above ~3 KB routinely cause `Stream idle timeout` on a single `Write`.
Never persist a plan in one call:

1. **Split into sections** (≤ 2 KB each): header (`## Plan — <title>`) + scope
   → first `Write` (creates the file); each `📝`/`✨`/`🗑️` block → one `Edit`
   append; `🧪` Tests → one `Edit`; `YAGNI CHECK` + `REUSES` → final `Edit`.
   Split further if any section exceeds 2 KB. Never emit a tool call whose text
   payload exceeds 2 KB.
2. **Verify after the first `Write`**: `Read` the path. If it errors or is empty,
   the write failed silently — tell the user to re-run `/diagnose`, then print
   only the header + first section (≤ 50 lines) as a copyable fallback.
3. **Chain the section writes automatically**, one section per tool call, no
   pausing between sections.
4. **Verify after the last `Edit`**: `Read` and confirm it ends with `REUSES`.
   If truncated, print only the missing sections (≤ 50 lines per block).
5. **Never retry a full-file write after a timeout.** `Read` first, append only
   the missing sections.

## Step 4 — Recap and handoff

Print:

```text
─── Plan recap ─────────────────────────────────────────────
Problem  : [root cause in 1 sentence]
Solution : [approach in 1-2 sentences]
Files    : [short EDITS list]
Tests    : [what pytest will verify]
Output   : [does it change numeric model output? yes/no]
────────────────────────────────────────────────────────────
Adjustments before challenge? Reply in chat.
Otherwise run /challenge-plan to validate.
```

**Do not proceed to challenge automatically** — the user triggers
`/challenge-plan` manually.

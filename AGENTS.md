# AGENTS.md

Instructions for AI agents (Claude Code, Cursor, Windsurf, Cline, Copilot,
Gemini) working on RuFaS (this MyForageSystem fork, branch `dev-msf`).

## Output style

Default to **caveman lite** on this project:

- Short sentences, no filler.
- No redundant intros or recaps.
- Bullets over paragraphs where it fits.
- Keep grammar and technical precision intact.

Activate in a Claude Code session with `/caveman lite`. The default mode is set
via `CAVEMAN_DEFAULT_MODE=lite` in `.claude/settings.json`. On remote sessions
(Claude Code Web) the `caveman@caveman` plugin is auto-installed by
`.claude/hooks/session-start.sh`; on desktop/CLI install it once with
`claude plugin marketplace add JuliusBrussee/caveman && claude plugin install
caveman@caveman` (see [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)).

**Do not use `caveman full` or `caveman ultra`** on sensitive tasks, where
compression can drop nuance that matters:

- Biophysical model logic and scientific equations (animal, field/soil/crop,
  manure, EEE) — correctness and unit/mass-balance integrity come first.
- mypy-strict typing work (CI ratchets the error count against `dev`).
- Protected input JSON files under `input/` (`.claude/rules/protected-inputs.md`)
  — input JSON only, never `tests/`.
- Anything that changes numeric model outputs.

## Commits & PRs

- **Commits**: Conventional-Commits-style subject ≤ 50 chars. Claude Code with
  the `caveman@caveman` plugin: `/caveman-commit`. Otherwise apply the rule
  manually.
- **`changelog.md` is mandatory on every PR** — CI fails the PR otherwise. Add
  an entry in the `### Next Version Updates` list (format: `- [PR#](url) -
  [minor change/Major change] [Area] [In/NoInputChange] [In/NoOutputChange]
  description`). See existing entries.
- **Reviews**: concise one-liners (`path:line — issue → fix`), except on the
  sensitive tasks above where a detailed analysis wins. Claude Code:
  `/caveman-review`. Otherwise apply the rule manually.
- **CI target is `dev`**; this fork integrates on `dev-msf`. Never push to a
  protected branch directly — open a PR.

## Project conventions

See the root `CLAUDE.md` (and the layered per-subsystem `CLAUDE.md` files) for
the full rules: Python 3.12, `pip install -e ".[dev]"`, Black (line-length 120),
flake8 (max-complexity 10), mypy strict, pytest, and the graphify dependency
graph at `graphify-out/`.

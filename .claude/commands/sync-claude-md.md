---
description: Audit and refresh the CLAUDE.md at the current directory against the actual code, then propose an update.
allowed-tools: Read, Grep, Glob, LSP, Bash(graphify:*)
---

# /sync-claude-md

Analyse the current directory and its **direct** subdirectories, then compare
with the existing `CLAUDE.md` at this level (if any). For a 250k-line tree,
prefer the LSP tool and `graphify query` over scanning files.

Identify:

- **Stale references** — files, modules, scripts, commands, or `*_manager.py` /
  `*_constants.py` mentioned in the CLAUDE.md that no longer exist or moved.
- **Changed conventions** — new patterns in the code not reflected in the doc
  (e.g. a new subsystem manager, a renamed module, a new connection object in
  `RUFAS/data_structures/`).
- **Undocumented dependencies** — new entries in `pyproject.toml`
  (`dependencies` / `[dev]`) or new tooling not mentioned.
- **Missing CLAUDE.md** — important subdirectories without one (e.g. a new
  package under `RUFAS/biophysical/` or a large new top-level module).
- **Command drift** — commands in the table that no longer work (check against
  `pyproject.toml`, `main.py:parse_gnu_args`, `.github/workflows/`).

Then **propose** an updated `CLAUDE.md`:

- Preserve any section that starts with `## Notes` verbatim.
- Keep it concise and structural (orientation + local commands/conventions) —
  push repo-wide rules up to the root `CLAUDE.md`, not down.
- Keep the layered-doc invariant: each subsystem file points at its own code,
  the root file stays repository-wide.

**Do not modify anything without explicit confirmation.** Show the diff first.

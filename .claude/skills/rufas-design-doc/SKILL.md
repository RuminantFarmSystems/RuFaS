---
name: rufas-design-doc
description: Follow the RuFaS design-doc-driven development process. Use when starting a feature or change that is ~1 engineer-month or larger, or any change whose design should be agreed before coding. Produces a design doc and runs the review process before implementation. Mirrors the RuFaS wiki "How to write a design doc" + "Code review" guides.
---

# RuFaS design-doc-driven development

RuFaS gates non-trivial work behind a **design doc** reviewed *before* coding. A
design doc describes how you plan to solve a problem — its goal is to get the
right work done by forcing you to think the design through and gather feedback.

**Write one when the work is ~1 engineer-month or more.** Smaller changes benefit
from a mini design doc. Pure tooling/config or a one-line bugfix usually doesn't
need one — but the *idea* of a large change must be agreed before the PR.

Sources: RuFaS wiki
[How to write a design doc](https://github.com/RuminantFarmSystems/RuFaS/wiki/How-to-write-a-design-doc%3F)
and [Code review](https://github.com/RuminantFarmSystems/RuFaS/wiki/Code-review).

## Process (do this *before* writing production code)

1. **Prototype freely** to validate ideas — but **none of the throwaway code is
   merged**. Exploratory ≠ starting the real implementation.
2. **Whiteboard review**: ask an experienced dev / SME to be your reviewer.
   Describe the *problem* first (don't skip this), then the implementation, and
   convince them it's the right thing to build.
3. **Write the design doc** (template below), addressing the corner cases the
   reviewer raised.
4. **Reviewer rubber-stamps** by adding their name to *Title and People*.
5. **Team review**: share with the team, **time-boxed to ~1 week**. Commit to
   addressing every comment in that window (leaving comments hanging = bad karma).
   For contested points, consolidate in a Discussion section; if a thread passes
   ~5 comments, move it to an in-person meeting. You make the final call.
6. **Implement** after sign-off, treating the design doc as a **living document** —
   update it whenever you learn something that changes the solution or scope.
7. **Code review + merge** (see the code-review checklist below).

## Design doc sections

Title and people · Overview · Context · Requirements · Milestones · Existing
Solution · Proposed Solution · Alternative Solutions · **Testability, Monitoring,
and Alerting** · Cross-Team Impact · Open Questions · Detailed Scoping and Timeline.

Write simply: short sentences, bulleted lists, concrete examples ("User Alice
connects her bank account, then …"), diagrams (link the editable source), and real
numbers (# rows, # animals, latency, Big-O). Apply the **Skeptic Test** (answer a
reviewer's doubts preemptively) and the **Vacation Test** (could a teammate
implement it from the doc alone?).

## Code-review checklist (every PR — author responsibilities)

- PR is **ready to merge as-is**: no temp/test scratch files, unused files removed,
  branch rebased onto the integration branch (`dev-msf` on this fork).
- **Linked to a GitHub issue**; description follows **what / why / how**, concise
  ("we boil water here", not an essay). Include a **Test Plan**.
- **≤ ~200 lines** is the target; larger = "large" and needs a prior design review.
- **Every modified/added function**: unit tests + **NumPy-style docstrings** +
  type annotations.
- Test suite covers **normal operations, edge cases, and invalid inputs**.
- Passes flake8/black/mypy and **all CI**. Keep functions small (low complexity),
  apply **DRY** and **SOLID**.
- **Comments are discouraged** — clean code should explain *what* it does; only a
  comment explaining *why* an approach was chosen is acceptable.
- **`changelog.md`**: add exactly one entry under `### Next Version Updates`
  (`[PR#](url) - [Major/minor change] [ImpactArea] description`); verify the
  "Files changed" diff shows *only* that addition.

## Merge

Needs **two reviews** (ideally one SME + one software engineer) and all CI green.
The author merges, resolves any conflicts (a large conflict resolution warrants
re-review), and **deletes the branch** afterward.

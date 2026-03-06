`FORKING.md`

---

# Forking guidelines (strategic + operational)

Forking is a first-class collaboration mechanism in RuFaS. We encourage forks when they enable experimentation, contextual adaptation, or innovation that would be difficult to pursue directly in the main repository. At the same time, RuFaS exists as a shared scientific and software commons: forks should strengthen the ecosystem, not fragment it. 

## 1) Strategic norms: when forking is appropriate
Forking is encouraged when you need to:
- **Experiment safely** (rapid prototyping, alternative implementations, or high-risk changes).
- **Adapt RuFaS to a specific context** (regional, institutional, production-system, or data constraints).
- **Develop capabilities that may later be proposed upstream**, once they are validated and documented.
- **Maintain a long-lived variant** with clearly different assumptions, scope, or roadmap.

Forking is discouraged when the goal is to:
- Create confusion about the primary RuFaS repository.
- Avoid transparency while still benefiting from RuFaS community standards and credibility.
- Make only minor, configuration-level changes that could be achieved with a plugin, adapter, parameterization, or feature flag.

**Guiding principle:** *Fork to explore and learn—then share what you learn when possible.* 

## 2) Transparency, lineage, and identity (public-facing expectations)
If your fork is public, please make its relationship to RuFaS clear to protect users and maintain scientific and operational integrity:
- Add a short **“Fork rationale”** in your README explaining the purpose of the fork and who it is for.
- State the **upstream RuFaS version or tag you forked from** (e.g., “Forked from RuFaS vX.Y.Z”) and update it when you rebase/merge upstream.
- Identify any **material deviations** (assumptions, system boundaries, datasets, algorithms, validation/calibration approach).
- Include a brief **comparability note** describing what results can and cannot be compared to upstream RuFaS given your deviations.
- Preserve required attribution, notices, and license terms.
- Public forks should not imply endorsement by the RuFaS project unless explicitly approved (see Section 5).

If your fork will be **long-lived and public**, consider opening a short GitHub discussion/issue in the RuFaS repository to share intent and reduce duplicated effort. 

## 3) Proprietary and closed-source collaborators (explicit guidance)
RuFaS welcomes collaboration with organizations building **proprietary or closed-source applications**, including those that integrate RuFaS concepts, interfaces, or modules. To protect users and the RuFaS commons:
- You may maintain **private forks** for internal development, productization, compliance, or client obligations, provided you follow the project’s license terms and preserve required attribution and notices.
- If your product includes RuFaS-derived components, clearly distinguish **RuFaS-originated work** from your proprietary IP in your internal documentation and (when public-facing) in your disclosures.
- Do not present proprietary derivatives as “RuFaS” itself; represent them as a **derivative or integration** and describe material deviations where appropriate.
- For questions about whether public descriptions or language imply RuFaS endorsement, see Section 5 (Endorsement and ‘official’ status).
- Even when code cannot be shared, we encourage sharing **non-confidential learnings** (e.g., design notes, interoperability lessons, validation insights) to support collective progress.

**Normative expectation:** closed-source constraints are respected, but ecosystem clarity and scientific integrity must be maintained at all times. 

## 4) Contributing back: public fork requirement (operational)
We fully support **private forks** for internal use, experimentation, or customization. However, **if you wish to contribute back to RuFaS via a pull request**, your fork must be **public** at the time you open the PR. This requirement exists because:
- RuFaS CI/CD workflows must be able to access your fork to run automated GitHub Actions tests and checks.
- GitHub’s pull request mechanisms for open repositories (including merge conflict resolution and review workflows) depends on repository access.

If you developed changes in a private fork and want to contribute them upstream, you can:
- Make your existing fork public before opening the PR, **or**
- Create a new public fork specifically for contributions and cherry-pick the relevant commits. 

## 5) Endorsement and “official” status (single-category rule)
**Do not imply RuFaS endorsement or “official” status for a fork unless the RuFaS Program Management Leadership (PML) has provided written approval; maintainers may offer technical guidance, but maintainer feedback does not constitute project-level endorsement.** 

Notes:
- “Endorsement” is intentionally rare and is a governance/reputation decision aligned with PML responsibilities for program oversight, strategic direction, and external representation.
- Maintainers’ roles focus on technical stewardship (review, integration, code quality, integrity/security) and may inform—but do not grant—endorsement.
- If you are unsure whether your planned representation implies endorsement, contact contact@rufas.org before publishing documentation. 

## 6) Re-integration mindset (normative expectation)
Not every fork should merge upstream—and that is okay. However, if you diverge in ways that could benefit the community, we strongly encourage you to contribute back one or more of the following:
- A pull request with the change (preferred where feasible),
- A design note summarizing the approach and tradeoffs,
- A short “lessons learned” issue describing what worked, what didn’t, and why.

RuFaS grows through shared learning. Even when code cannot be merged, insights often can.



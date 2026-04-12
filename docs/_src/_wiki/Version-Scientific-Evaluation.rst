Maintainer Team Workflow and Communication during a Version Update
===================================================================

This page describes the process that RuFaS Maintainers will use to communicate
and execute a version update.

In addition to the updated model and scientific documentation in the repository
codebase, additional deliverables of this process for **Major** and **Minor**
updates are:

- A version release note that includes:
  
  - A high-level summary of the outcomes of the SME Review
  - A summary of the changelog

- A detailed technical report of the SME Review



Before Merging ``dev`` to ``test``
------------------------------

**Major** and **Minor** updates:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


1. RuFaS Maintainers meet to discuss what work **will and will not** be
   included in the release and the proposed timeline.

2. The PML reviews and approves pending work to be included and excluded
   from the version update, with additional Maintainer input as needed.

3. The PML and team leaders create a GitProject for the version release and
   add pending issues/PRs that must be completed before the version update
   (before ``dev → test``). If a Maintainer identifies additional work that would benefit
   the version release after the project is created, issues/PRs should be added to
   the version release project or discussed with the PML at the members discretion. 

4. SME Maintainers review the scientific evaluation process and criteria from the
   previous version release and update as necessary.


**Patch** Updates
^^^^^^^^^^^^^^^^^^

Patch updates do not require a full project. Bug fixes required in the patch should be collected 
as sub-issues under a **Patch version update parent issue**.


After ``test`` is updated
-------------------------

RuFaS SME Maintainers evaluate integrated model performance:
1. The Scientific Director runs Evaluation Farm Scenarios on ``test`` and compiles their outputs.
2. SME Maintainers review model outputs Evaluation Farms on ``test``.
2. Outputs are collected and summarized for the SME Review process
   (link to upcoming SME Review page).
3. SME Maintainers conduct the SME Review led by the Scientific Director.

During this stage:

- Maintainers identify and fix any bugs or model errors surfaced during
  the SME Review following the processes outlined in the branch management
  guidelines for version updates.

- The Scientific Director prepares:

  - A high-level statement of model outcomes
  - A technical summary of the review process

These summaries are shared with SME Maintainers for input.


Release Approval and Publication
--------------------------------

After SME Maintainers have had an opportunity to review and provide
feedback on the evaluation report and technical summaries:

1. RuFaS Directors vote on the release:

   - Director of Software Engineering
   - Director of Strategic Partnerships and Governance
   - Scientific Director

2. The high-level summary of the SME review is combined with the release
   note.

3. The technical summary of the SME review is combined with release notes
   and added to the RuFaS GitHub Pages documentation.

4. The Director of Software Engineering generates the official release.
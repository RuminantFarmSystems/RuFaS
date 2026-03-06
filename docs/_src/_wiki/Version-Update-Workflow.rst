Maintainer Team Workflow/Communication for Version Update
=========================================================

This page describes the process that RuFaS Maintainers will use to communicate
and execute a version update.

In addition to the updated model and scientific documentation in the repository
codebase, additional deliverables of this process for **Major** and **Minor**
updates are:

- A version release note that includes:
  
  - A high-level summary of the outcomes of the SME Review
  - A summary of the changelog

- A detailed technical report of the SME Review


Version Update Process
======================

The process for updating the RuFaS version is as follows:


Version Release Trigger
-----------------------

When a version release is triggered according to the principles of semantic
versioning and approved by the PML:

- Announcements are made at the All Team Meeting (ATM) and in the general
  Slack channel to communicate the decision.


Major and Minor Updates
-----------------------

For **Major** and **Minor** updates:

1. RuFaS Maintainers meet to discuss what work **will and will not** be
   included in the release and the proposed timeline.

2. The PML reviews and finalizes pending work to be included and excluded
   from the version update, with additional Maintainer input as needed.

3. The PML and team leaders create a GitProject for the version release and
   add pending issues/PRs that must be completed before the version update
   (before ``dev → test``).

4. SME Maintainers review the evaluation process and criteria from the
   previous version release:

   - Are updates to benchmarks required?
   - Are new metrics required for new features?


Patch Updates
-------------

For **Patch** updates:

- A full project is not required.
- Bug fixes required in the patch should be collected as sub-issues under
  a **Patch version update parent issue**.


Evaluation Preparation
----------------------

- Maintainers update evaluation farm inputs and ensure they run on the
  ``dev`` branch.


Dev Freeze and Test Preparation
-------------------------------

For **Major and Minor updates**, when all required tasks are merged into
``dev`` (or all but one or two are pending):

1. Pooya Hekmati or Kristan Reed freezes ``dev``.
2. Maintainers merge ``dev`` into ``test``.
3. The Director of Software Engineering (Pooya Hekmati) generates a release
   note summarizing the changelog.


Evaluation and SME Review
-------------------------

When ``test`` has been updated:

1. Maintainers work together to run Evaluation Farms on ``test``.
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
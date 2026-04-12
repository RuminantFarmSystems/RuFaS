Maintainer Team Workflow and Communication during a Version Update
===================================================================

This page describes the process that RuFaS Maintainers will use to communicate
and execute a version update.

In addition to the updated model and scientific documentation in the repository
codebase, additional deliverables of this process for **Major** and **Minor**
updates are:

- A detailed technical report of the scientific review by SME Maintainers
- A version release note that includes:
  - A high-level summary of the outcomes of the SME Review
  - A summary of the changelog


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
- During the testing phase, SME Maintainers will evaluate integrated model performance. 
(link to Scientific Evaluation Process). 
- When the model performance has been verified by at least one SME Maintainer per Module, 
the Scientific Director will prepare a Scientific Report summarizing the model performance and changes in scientific methodology. 
- The Director of Software Engineering will lead preparation of a set of Release Notes to summarize model updates. 
- When the testing phase is complete, both the Scientific Report and Release notes are added to the project documentation on GitHub
and shared with the PML for approval.

Contributing to RuFaS
=======================

RuFaS welcomes contributions from researchers, developers, students, and
users. You can help with code, scientific review, documentation, testing,
bug reports, and user support. No formal selection process is required
to become a contributor.

Start with the
`contribution guidelines <https://github.com/RuminantFarmSystems/RuFaS/blob/dev/CONTRIBUTING.md>`_
linked from the repository README. They describe contribution categories,
governance, shared values, the code of conduct, and guidance for coding
and noncoding work. This page helps you find the next step.

Choose a way to help
----------------------

* **Report a bug or suggest an improvement:** follow
  :doc:`creating_github_issue`. Search existing issues first and include
  enough context for someone else to reproduce or assess the problem.
* **Improve a model or propose a substantial change:** use
  :doc:`How-to-write-a-design-doc` to describe the problem, scientific
  evidence, proposed approach, and expected behavior before implementation.
* **Improve documentation or onboarding:** edit the source pages in
  ``docs/_src/_wiki`` and follow :ref:`how-to-build-docs` to preview them.
  Scientific documentation lives in ``docs/scientific``; see
  :doc:`Scientific-Documentation` for the manual and source.
* **Review science or code:** use :doc:`Code-review` for review expectations
  and :doc:`best_practices` for testing, documentation, and code-quality
  guidance.

Make your first pull request
------------------------------

#. Read the contribution guidelines and find or create an issue that
   describes the change. Discuss its scope with the maintainers when
   the approach needs agreement.
#. Follow :doc:`Branching-Strategy-in-RuFaS` and the
   `forking guidelines <https://github.com/RuminantFarmSystems/RuFaS/blob/dev/FORKING.md>`_
   to work in a fork or a branch. The branching guide describes the
   target branch for each kind of contribution.
#. Set up RuFaS using :doc:`onboarding`. For code contributions, install
   the development tools in the activated environment:

   .. code-block:: console

      python -m pip install -e ".[dev]"

#. Make a focused change and update the relevant documentation. For code
   changes, run the appropriate tests and follow the formatting, linting,
   and type-checking guides under **Developer Tools**. For documentation
   changes, build and inspect the pages using :ref:`how-to-build-docs`.
#. Open a pull request explaining the problem, the change, and how you
   checked it. Link the related issue and respond to feedback using
   :doc:`Code-review`. :doc:`Github-Actions` explains automated checks;
   :doc:`End‐to‐End-Testing` explains simulation-level regression checks.

Understand how the team works
-------------------------------

The **Team Culture and Workflow** section provides context for collaboration:

* :doc:`what_why_how` describes how to communicate a change's purpose,
  significance, and implementation.
* :doc:`SCRUM-at-RuFaS` explains planning, task sizing, and the team's
  definition of done.
* :doc:`RuFaS-Versioning-Policy` describes release versioning and review.
* :doc:`Version-Update-Workflow` explains maintainer coordination during
  a release.

Shared values and operating principles are defined in
`Strategy.md <https://github.com/RuminantFarmSystems/RuFaS/blob/dev/Strategy.md>`_.
Follow the code of conduct linked from the contribution guidelines.
For questions about participation, email contact@rufas.org.

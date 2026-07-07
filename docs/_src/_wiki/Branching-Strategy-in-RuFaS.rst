Branching Strategy in RuFaS
===========================

In this page, we outline the branching strategy used in RuFaS, detailing
the purpose of each branch and the process for merging changes.

Branches Overview
-----------------

``dev``
~~~~~~~

- **Purpose**: Active development branch where new features and changes
  are implemented.

- **Usage**: All pull requests (PRs) are merged into ``dev``. This is
  the primary branch for ongoing development.

- **Approval**: Merging to ``dev`` requires **2 approvals**.

- **Note**: All the changes on ``dev`` are considered for the next release.
 If something is **NOT** intended to be included in the next release,
 it should be merged into a separate parking branch and not merged into ``dev``
 until it is ready for release.

``test``
~~~~~~~~

- **Purpose**: Intermediate branch used for **integration, validation,
  and stabilization** prior to a release.

- **Usage**: When preparing a release candidate, the current state of
  ``dev`` is merged into ``test``. The ``test`` branch is then used for
  validation and stabilization before releasing a new version.

  Once ``dev`` has been merged into ``test`` for a release candidate,
  no new development work should be introduced into ``test``. Only bug
  fixes discovered during testing should be applied.

- **Approval**: ``test`` is locked and only admins can merge into it.

``main``
~~~~~~~~

- **Purpose**: Primary branch representing the latest stable release
  that is ready for production.

- **Usage**: Once changes in ``test`` are confirmed to be stable and the
  version number has been updated, updates are pulled into ``main``.

- **Permissions**: The ``main`` branch is locked, and only
  repo admins have permission to merge pull requests into it.

``scientific_documentation_updates``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Purpose**: Branch used for updates to the **scientific documentation**
  that do not require changes to the RuFaS codebase.

- **Usage**: Documentation updates may be committed directly to this
  branch and merged into ``main`` without going through the ``test``
  branch.

- **Synchronization**: After merging into ``main``, the changes must
  also be merged into ``dev`` to ensure documentation remains consistent
  across development branches.

Merging Process
---------------

Merging to ``dev``
~~~~~~~~~~~~~~~~~~

1. **Develop**

   - Create feature branches from ``dev`` to implement new features,
     bug fixes, or improvements.

2. **Submit PR**

   - Once development is complete, submit a pull request to merge the
     feature branch into ``dev``.

3. **Review**

   - Code is reviewed following the
     `code review process <https://ruminantfarmsystems.github.io/RuFaS/_wiki/Code-review.html>`__
     used in RuFaS.

4. **Merge**

   - After receiving the required approvals, the PR is merged into
     ``dev``.

Merging to ``test``
~~~~~~~~~~~~~~~~~~~

1. **Prepare a Release Candidate**

   - When the development team decides to prepare a release,
     update the version number in ``pyproject.toml`` on the ``dev``
     branch and merge ``dev`` into ``test``.

2. **Testing Phase**

   - Conduct rigorous testing on the ``test`` branch to verify model
     correctness, integration stability, and expected behavior.

3. **Handling Issues During Testing**

   If an issue is discovered during testing:

   - Create a **fix branch from ``test``**.
   - Implement the fix in that branch.
   - Submit a PR to merge the fix into ``test``.
   - After the fix is merged into ``test``, create a PR to merge the
     same fix back into ``dev`` so both branches remain synchronized.

4. **Continue Stabilization**

   - Repeat this process until the ``test`` branch is confirmed to be
     stable and ready for release.

Merging to ``main``
~~~~~~~~~~~~~~~~~~~

1. **Merge Version Update into Test**

   - Merge the updated ``dev`` branch into ``test`` as part of the
     release preparation.

2. **Stability Confirmation**

   - Confirm that the ``test`` branch has passed validation and
     stabilization testing.

3. **PML Approval**

   - The **Program Management Leadership (PML)** must approve the release and
     the release notes before the merge to ``main`` is performed.

4. **Merge to Main**

   - Pull the stable updates from ``test`` into ``main``.

5. **Tag the Release**

   - Create a Git tag corresponding to the version number
     (for example ``v1.2.0``).

Best Practices
--------------

- **Consistent Testing**

  Ensure thorough validation is completed in ``test`` before merging
  into ``main``.

- **Branch Consistency**

  Fixes applied during the testing phase must always be merged back into
  ``dev`` to prevent branch divergence.

- **Clear Communication**

  Keep all team members informed about the status of release candidates
  and branch updates.

- **Documentation**

  Maintain clear and up-to-date documentation for changes and testing
  procedures.

- **Review and Approval**

  Adhere to the :doc:`Code Review Guidelines <https://ruminantfarmsystems.github.io/RuFaS/_wiki/Code-review.html>` to maintain
  code quality and model integrity.

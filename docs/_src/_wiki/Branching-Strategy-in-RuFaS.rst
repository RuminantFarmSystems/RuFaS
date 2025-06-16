Branching Strategy in RuFaS
===========================

In this wiki, we outline the branching strategy used in RuFaS, detailing
the purpose of each branch and the process for merging changes.

Branches Overview
-----------------

``dev``
~~~~~~~

- **Purpose**: Active development branch where new features and changes
  are implemented.
- **Usage**: All pull requests (PRs) are merged into ``dev``. This is
  the main branch for ongoing development.
- **Approval**: Merging to ``dev`` requires 2 approvals.

``test``
~~~~~~~~

- **Purpose**: Intermediate branch used for integration and testing of
  features before moving to ``main``.
- **Usage**: Changes from ``dev`` are periodically pulled into ``test``
  for vigorous testing. This ensures that new features and fixes are
  properly tested before being considered stable.
- **Approval**: Merging to ``test`` requires at least 1 approval.

``main``
~~~~~~~~

- **Purpose**: Primary branch representing the latest stable release
  that is ready for production.
- **Usage**: Once changes in ``test`` are confirmed to be stable, the
  version number is updated, and updates are pulled into ``main``. The
  ``main`` branch is locked, and only `Pooya
  Hekmati <https://github.com/PooyaHekmati>`__ and `Kristan
  Reed <https://github.com/KFosterReed>`__ have the permissions to merge
  PRs into it.

Merging Process
---------------

Merging to ``dev``
~~~~~~~~~~~~~~~~~~

1. **Develop**: Create feature branches off ``dev`` to work on new
   features or fixes.
2. **Submit PR**: Once the feature is ready, create a pull request to
   merge it into ``dev``.
3. **Review**: The code is reviewed following the `code review
   process <https://github.com/RuminantFarmSystems/MASM/wiki/Code-review>`__
   in RuFaS.
4. **Merge**: After approval, the PR is merged into ``dev``.

Merging to ``test``
~~~~~~~~~~~~~~~~~~~

1. **Periodic Updates**: Periodically, pull changes from ``dev`` into
   ``test``.
2. **Testing**: Conduct rigorous testing on the ``test`` branch to
   ensure all features and fixes are stable.
3. **Feedback**: Address any issues found during testing by pushing
   fixes to ``dev`` and then merging the updates back into ``test``.

Merging to ``main``
~~~~~~~~~~~~~~~~~~~

1. **Stability Confirmation**: Once the ``test`` branch is confirmed to
   be stable, update the version number in both ``TaskManager`` and the
   change log. :doc:`RuFaS Versioning Policy <RuFaS-Versioning-Policy>`
2. **Pull Updates**: Pull the stable updates from ``test`` into
   ``main``.
3. **Approval**: Only `Pooya
   Hekmati <https://github.com/PooyaHekmati>`__ and `Kristan
   Reed <https://github.com/KFosterReed>`__ can merge PRs into ``main``
   to ensure high-quality, stable releases.

Best Practices
--------------

- **Consistent Testing**: Ensure thorough testing is done in ``test``
  before merging into ``main``.
- **Clear Communication**: Keep all team members informed about the
  status of each branch and any important changes.
- **Documentation**: Maintain clear and up-to-date documentation for all
  changes and testing procedures.
- **Review and Approval**: Adhere to the :doc:`code review guidelines <Code-review>`
  to maintain code quality and stability.

By following this branching strategy, we ensure a clear and structured
workflow that supports continuous integration and delivery, maintaining
the high standards of code quality in RuFaS.

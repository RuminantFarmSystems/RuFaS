RuFaS Versioning Policy
=======================

RuFaS follows a **Semantic Versioning** policy to ensure clear
communication of changes and maintain compatibility across updates. This
page outlines how we handle versioning, branch structure, and the
process for updating version numbers in RuFaS.

Semantic Versioning in RuFaS
----------------------------

RuFaS adheres to the `Semantic Versioning
(SemVer) <https://semver.org/>`__ scheme to manage and communicate
changes across the project. The version format is as follows:
``MAJOR.MINOR.PATCH``.

- **MAJOR version** (``X.0.0``): Incremented when we make changes that
  are **backward-incompatible** or introduce significant new
  functionality that may require users to adjust their code or workflow.

- **MINOR version** (``0.Y.0``): Incremented when new features are added
  that are **backward-compatible**. This allows users to upgrade without
  needing to modify their existing setup.

- **PATCH version** (``0.0.Z``): Incremented for **backward-compatible
  bug fixes** or minor improvements that don't add new features but
  improve stability or fix known issues.

Example
~~~~~~~

For a release version ``2.1.4``:

- **2**: MAJOR update indicating a significant or breaking change.
- **1**: MINOR update indicating the addition of new features.
- **4**: PATCH update indicating minor fixes or improvements.

Branch Structure
----------------

RuFaS follows a structured branching model to manage development,
testing, and production-ready code. The three main branches are:

- **dev**: The primary development branch where new features, bug fixes,
  and improvements are implemented. Changes here are not considered
  stable and may undergo significant modifications.

- **test**: Once features are completed and pass initial testing, they
  are merged into the ``test`` branch. This branch is used for broader
  testing, including integration tests and any QA processes.

- **main**: The stable release branch. Only code that has been
  thoroughly tested and reviewed is merged into ``main``. This is the
  production-ready version of RuFaS that users rely on.

See :doc:`Branching Strategy <Branching-Strategy-in-RuFaS>`
for more details.

Version Number Update Process
-----------------------------

Every time we merge the **test** branch into the **main** branch, we
follow the steps below to update the version number and track the
changes.

Steps:
~~~~~~

1. **Decide on the Version Increment**:

   - Evaluate the changes introduced since the last merge. Based on the
     nature of the changes (major, minor, or patch), increment the
     version number accordingly following the **Semantic Versioning**
     guidelines.

2. **Update Version in TaskManager**:

   - Navigate to the version configuration file in the TaskManager and
     update the version number to reflect the changes.

3. **Changelog Updates Automatically**:

   - The changelog is automatically updated, reflecting all the pull
     requests merged up to this point. The new version number simply
     marks the last pull request included in the current version.

4. **Tag the Release**:

   - Once the version is updated, create a new Git tag with the version
     number (e.g., ``v1.2.0``) to mark the release in the **main**
     branch.

Example Workflow:
~~~~~~~~~~~~~~~~~

- A new feature is completed and tested in the ``dev`` branch.
- The feature is merged into ``test`` for broader testing and
  integration validation.
- After successful testing, The version number is incremented in
  ``TaskManager`` and change log.
- The ``test`` branch is merged into ``main``.

Changelog Format
----------------

Each entry in the Changelog follows this format:

- **PR #**: Provide the pull request number (e.g.,
  ``[123](https://github.com/RuminantFarmSystems/RuFaS/pull/123)``).
- **Type of Change**: Indicate if it is a major or minor change (e.g.,
  ``[Major change]`` or ``[Minor change]``).
- **Impact Area**: Specify which part of the codebase is affected (e.g.,
  ``[Animal Module]``, ``[Manure Module]``, etc.).
- **Description**: Provide a concise, informative description of the
  changes.

By following this process, RuFaS ensures that versioning is consistent,
changes are tracked transparently, and users are well-informed about
updates and their impacts.

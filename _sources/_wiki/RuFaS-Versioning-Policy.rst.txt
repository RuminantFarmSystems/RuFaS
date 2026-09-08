RuFaS Versioning Policy
=======================

RuFaS follows a **Semantic Versioning** policy to ensure clear
communication of changes and maintain compatibility across updates.
This page outlines how version numbers are assigned, how releases are
prepared, and how changes are documented.

Semantic Versioning in RuFaS
----------------------------

RuFaS follows the `Semantic Versioning (SemVer) <https://semver.org/>`__
standard. Versions follow the format:

``MAJOR.MINOR.PATCH``

- **MAJOR version** (``X.0.0``)

  Incremented when changes introduce **backward-incompatible behavior**
  that requires users to modify their workflows, inputs, or scripts.

- **MINOR version** (``X.Y.0``)

  Incremented when **new functionality is added in a backward-compatible
  way**. Existing simulations should continue to work without requiring
  modification.

- **PATCH version** (``X.Y.Z``)

  Incremented for **backward-compatible bug fixes and stability
  improvements**. These updates may correct model behavior but must not
  require users to change inputs or workflows.

Example
~~~~~~~

For a release version ``2.3.5``:

- **2** indicates a major update introducing incompatible changes.
- **3** indicates new backward-compatible functionality.
- **5** indicates bug fixes or minor improvements.

Compatibility in RuFaS
----------------------

In the context of RuFaS, compatibility primarily concerns **model
inputs, outputs, and user workflows**.

Typical interpretations include:

- **InputChange**

  Indicates whether a change modifies model inputs. This may include
  new required fields, changed input structures, or modified semantics.

- **OutputChange**

  Indicates whether model outputs change. Output changes may result
  from bug fixes, improved calculations, or new outputs being added.

Guidelines
~~~~~~~~~~

- **InputChange = Yes**

  Usually requires a **MAJOR version bump**, unless the change is purely
  additive and does not break existing inputs.

- **OutputChange = Yes**

  May appear in **PATCH** releases when correcting model behavior.
  Structural output changes may require a **MINOR** or **MAJOR** version
  bump depending on their impact.

Branch Structure
----------------

RuFaS uses three primary branches to manage development and releases.

- **dev**

  Primary development branch where new features, improvements, and
  fixes are implemented.

- **test**

  Integration and stabilization branch used to validate a release
  candidate before publishing a new version.

- **main**

  Stable branch representing the officially released production version
  of RuFaS.

See :doc:`Branching Strategy <https://ruminantfarmsystems.github.io/RuFaS/_wiki/Branching-Strategy-in-RuFaS.html>`
for details about how these branches interact.

Version Location
----------------

The RuFaS version number is stored in the ``pyproject.toml`` file.

Example:

.. code-block:: toml

   [project]
   version = "1.2.0"

This value represents the official version of RuFaS once the release is
merged into ``main``.

Version Number Update Process
-----------------------------

Each RuFaS release follows a structured process to ensure version
numbers and release history remain consistent.

Steps
~~~~~

1. **Determine Version Increment**

   - PML reviews all changes introduced since the previous release.
   - PML decides whether the release should increment **MAJOR**, **MINOR**, or
     **PATCH** according to Semantic Versioning.

2. **Update Version in ``dev``**

   - Repo Admin updates the ``version`` field in ``pyproject.toml`` on the ``dev``
     branch.

3. **Create Release Candidate**

   - Repo Admin merges ``dev`` into ``test`` to create a release candidate.

4. **Stabilization Testing**

   - Validate the release candidate on the ``test`` branch.
   - If issues are discovered:

     - Create a fix branch from ``test``.
     - Merge the fix into ``test``.
     - Merge the same fix back into ``dev``.

5. **PML Approval**

   - The **Program Management Leadership (PML)** must approve the release and
     the release notes before the release is finalized.

6. **Merge into Main**

   - Repo Admin merges ``test`` into ``main`` once stabilization testing is complete.

7. **Tag the Release**

   - Repo Admin creates a Git tag corresponding to the version number, for example:

   ::

     v1.2.0

Changelog Format
----------------

Each entry in the changelog must follow the format below:

::

  - [123](https://github.com/RuminantFarmSystems/RuFaS/pull/123) - [Major change/minor change] [Impact Area] [InputChange/NoInputChange] [OutputChange/NoOutputChange] Short description of the change or feature.

Fields
~~~~~~

- **PR Number**

  Link to the pull request that introduced the change.

- **Type of Change**

  Indicates whether the change is a **major change** or **minor change**.

- **Impact Area**

  The RuFaS component affected (for example ``Animal Module``,
  ``Manure Module``).

- **InputChange**

  ``InputChange`` if the change modifies model inputs; otherwise ``NoInputChange``.

- **OutputChange**

  ``OutputChange`` if the change modifies model outputs; otherwise ``NoOutputChange``.

- **Description**

  A concise description of the change or feature.

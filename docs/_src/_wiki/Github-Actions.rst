Github Actions
==============

What and Why
------------

Github Actions are a continuous integration and continuous delivery
(CI/CD) platform that allows you to automate your build, test, and
deployment pipeline.

Essentially, whenever you push code to Github or merge a branch into
``dev`` or ``main``, a series of actions are run on that code by Github.
These actions ensure that the code is meeting the testing, formatting,
and linting guidelines and standards established by RuFaS. Ensuring your
code passes these guidelines helps maintain clean, functional code and
tries to prevent bad code from being merged into the main and dev
branches.

How
---

Github Actions are in the MASM/.github/workflows folder saved as
``.yml`` files.

As of September 2024, RuFaS has two Actions files:
``combined_format_lint_test_mypy.yml`` and ``sphinx.yml``.
``combined_format_lint_test_mypy.yml`` runs 2 different jobs, described
below. ``sphinx.yml`` must be triggered manually, instructions for how
to do that are located in the :doc:`Sphinx Wiki Page <Using-Sphinx>`.

format_code
~~~~~~~~~~~

The first job in ``combined_format_lint_test_mypy.yml`` does 4 things:

1. Checks for any changes to protected files. This check is for files
   that we don't want anyone to change but that we still want to have
   tracked in Github. The Github Actions will exit out and fail at this
   point if the user has changed any unauthorized files.
2. Checks and records if the
   `changelog <https://github.com/RuminantFarmSystems/MASM/blob/dev/changelog.md>`__
   has been updated in this PR.
3. Formats the code using the :doc:`Black formatting tool <Using-Python's-Black-Formatter>`.
4. Commits and adds the Black-formatted code to the PR.

lint_test_type_check
~~~~~~~~~~~~~~~~~~~~

The second job ``combined_format_lint_test_mypy.yml`` does 6 things:

1. Takes the Black-formatted code added in the first job and uses
   :doc:`flake8 <Using-Flake8>`
   to check for any linting errors.
2. Checks that the code passes all unit testing.
3. Checks the percent of the code that is covered by unit testing.
4. Runs
   :doc:`Mypy <Using-Mypy>`
   on both the dev branch and the PR branch and compares the number of
   static type check errors found.
5. Updates the README badges for linting, testing, flake8, and MyPy
   errors.
6. Based on the logged result of the changelog check from job 1,
   notifies the user if they didn't update the changelog. The action
   will fail at this point if the user hasn't updated the changelog.

Updating and Testing Github Actions
-----------------------------------

The process of updating Github Actions can be challenging. They are
written in the YAML syntax and the behaviors can often feel
unpredictable. They are also difficult to test locally before pushing to
Github to see their behavior.

In particular, there can be challenges predicting the behavior of
running the Github Actions on a branch when comparing that branch to dev
and running the Github Actions on dev when code is merged into the dev
branch. In those latter cases, there is no base branch to which dev is
compared. There have been multiple times where Github Actions run on a
branch will function as predicted and then will error when that branch
is merged into dev.

Testing Strategy:
~~~~~~~~~~~~~~~~~

1. Create a new branch ``test-dev`` off ``dev``.
2. Update the Github action workflow .yml file in that branch to make
   ``test-dev`` the ``on push`` and ``on pull_request`` branch:

::

   on:
     push:
       branches: [ test-dev ]
     pull_request:
       branches: [ test-dev ]

3. Change all other references to ``dev`` to ``test-dev``. For example,
   this would update the ``Get all added or modified files`` step to
   reflect this new ``test-dev`` base branch:

::

   - name: Get all added or modified files
           run: |
             BASE_BRANCH=${{ github.base_ref }} || "test-dev"
             git fetch origin $BASE_BRANCH
             if ! git rev-parse --verify --quiet origin/$BASE_BRANCH; then
               echo "Fallback to test-dev branch because $BASE_BRANCH does not exist."
               BASE_BRANCH="test-dev"
               git fetch origin $BASE_BRANCH
             fi

4. Push that branch to Github.
5. Create a branch off ``test-dev`` (``test-test-dev`` or whatever you
   prefer) and make some changes and push those to github.
6. In the PR created for ``test-test-dev`` update the base branch (the
   branch to which you want to compare ``test-test-dev``) to
   ``test-dev``.

.. figure:: /_static/gh-action.png
   :alt: RuFaS Overview - GG
   :align: center
   :name: rufas overview
7. Merge ``test-test-dev`` into ``test-dev`` with the above-alterations
   to the Github action.

Using Separate Virtual Environments for RuFaS Development and Testing
=====================================================================

Why separate virtual environments are needed
--------------------------------------------

Different versions of RuFaS may require different versions of Python packages. In particular, the current development
branch may have dependency requirements that differ from those of a release or test branch used to develop and validate
a patch.

Python virtual environments isolate installed packages from one another. This allows each version of RuFaS to run with
the exact dependency versions it expects.

For example, suppose the development branch requires a newer version of ``pytest``, while the branch being used to test
a patch requires an older version. If both branches share the same virtual environment, installing the requirements for
one branch can upgrade or downgrade packages needed by the other branch. Tests may then fail because of the environment
rather than because of a change to RuFaS itself.

Using two virtual environments avoids this problem:

.. code-block:: text

   .venv       -> normal RuFaS development environment
   .venv-test  -> environment for the main/test branch

Each environment maintains its own Python packages and package versions. Switching branches does not automatically change
the contents of a virtual environment, so developers should activate the environment corresponding to the version of
RuFaS they are working with.

This is particularly important when validating patches against an older RuFaS release. A patch should be tested using
the dependencies supported by that release rather than whatever dependencies happen to be installed for current
development.


1. Create the normal development environment
--------------------------------------------

From the root of the RuFaS repository, check out the normal development branch:

.. code-block:: bash

   git checkout dev

Create the virtual environment using the Python version supported by that branch. For example, for Python 3.12:

.. code-block:: bash

   python3.12 -m venv .venv

Activate it on macOS or Linux:

.. code-block:: bash

   source .venv/bin/activate

On Windows:

.. code-block:: powershell

   .venv\Scripts\activate

Confirm that the expected Python interpreter is active:

.. code-block:: bash

   python --version

Then install RuFaS and its development dependencies:

.. code-block:: bash

   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"

The ``-e`` option installs RuFaS in editable mode, while ``.[dev]`` installs the development dependencies specified by
the ``pyproject.toml`` on the currently checked-out branch.

The ``.venv`` environment is now associated with the normal development version of RuFaS.


2. Create the test/patch/main environment
-----------------------------------------

Deactivate the current environment:

.. code-block:: bash

   deactivate

Check out the branch containing the version of RuFaS against which the patch will be developed or tested:

.. code-block:: bash

   git checkout <test-branch>

.. important::

   It is important to switch branches **before installing the dependencies**. This ensures that ``pip`` reads the
   ``pyproject.toml`` belonging to the version of RuFaS being tested.

Create a second environment:

.. code-block:: bash

   python3.12 -m venv .venv-test

Activate it on macOS or Linux:

.. code-block:: bash

   source .venv-test/bin/activate

On Windows:

.. code-block:: powershell

   .venv-test\Scripts\activate

Verify the Python version:

.. code-block:: bash

   python --version

Then install the dependencies specified by the test branch:

.. code-block:: bash

   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"

The two environments are now independent:

.. code-block:: text

   dev branch                 test/patch branch
       |                              |
       v                              v
     .venv                       .venv-test
       |                              |
       +-- dependency version A       +-- dependency version B
       +-- dependency version B       +-- dependency version C
       +-- current dev tooling        +-- test/release tooling

Installing, upgrading, or downgrading a package in ``.venv-test`` does not modify the packages installed in ``.venv``,
and vice versa.


3. Switching between RuFaS versions
-----------------------------------

When returning to normal development:

.. code-block:: bash

   deactivate
   git checkout dev
   source .venv/bin/activate

When returning to the test branch:

.. code-block:: bash

   deactivate
   git checkout <test-branch>
   source .venv-test/bin/activate

On Windows, substitute the appropriate activation command:

.. code-block:: powershell

   .venv\Scripts\activate

or:

.. code-block:: powershell

   .venv-test\Scripts\activate

You do **not** need to reinstall all dependencies each time you switch branches. The dependencies remain installed in
their respective environments.

Reinstallation is generally only necessary when the dependency requirements for that branch change.


4. Verify the active environment before testing
-----------------------------------------------

Before running tests, it can be useful to verify both the Python interpreter and important dependency versions:

.. code-block:: bash

   python --version
   python -m pytest --version

On macOS or Linux, you can also check:

.. code-block:: bash

   which python

For the development environment, this should point to something similar to:

.. code-block:: text

   .../RuFaS/.venv/bin/python

For the test environment:

.. code-block:: text

   .../RuFaS/.venv-test/bin/python

On Windows, the equivalent command is:

.. code-block:: powershell

   where python

Using ``python -m pytest`` instead of simply ``pytest`` can also help ensure that pytest is being run using the currently
active Python environment:

.. code-block:: bash

   python -m pytest


5. (for VS Code users) Configure VS Code for the appropriate environment
------------------------------------------------------------------------

.. note::

   VS Code maintains its own selected Python interpreter. Activating ``.venv-test`` in a terminal does not necessarily
   mean that the VS Code debugger is using ``.venv-test``.

When changing which RuFaS environment you are working with:

#. Open the VS Code Command Palette.
#. Select **Python: Select Interpreter**.
#. Select the appropriate interpreter.

For normal development:

.. code-block:: text

   RuFaS/.venv/bin/python

For testing the alternate branch:

.. code-block:: text

   RuFaS/.venv-test/bin/python

On Windows, these will instead be under the environment's ``Scripts`` directory.

If tests work from the terminal but fail unexpectedly when run through the VS Code debugger, checking the selected
interpreter should be one of the first troubleshooting steps.


When should an environment be recreated?
----------------------------------------

A virtual environment can generally be reused while working on the same version of RuFaS.

Consider deleting and recreating it when:

* the supported Python version changes;
* major dependency requirements change;
* the environment has accumulated incompatible manually installed packages; or
* you are no longer confident that the installed dependencies represent those specified by the branch.

For example, to completely rebuild the test environment on macOS or Linux:

.. code-block:: bash

   deactivate
   rm -rf .venv-test
   python3.12 -m venv .venv-test
   source .venv-test/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"

Recreating an environment is safe because the virtual environment itself contains no RuFaS source code and should not
be tracked by Git.


Summary
-------

The important distinction is that **Git branches isolate source-code versions, while Python virtual environments isolate
dependency versions**.

Checking out another branch changes the RuFaS source code and its ``pyproject.toml``, but it does not change packages
that have already been installed into the active virtual environment.

For this reason, when two RuFaS branches require different dependency versions, each should be tested with its own
virtual environment:

.. code-block:: text

   Git branch     -> correct RuFaS source code
   Virtual env    -> correct Python dependency versions

Keeping those two pieces aligned helps ensure that test results represent the version of RuFaS being tested rather than
an unintended mixture of source code from one version and dependencies from another.
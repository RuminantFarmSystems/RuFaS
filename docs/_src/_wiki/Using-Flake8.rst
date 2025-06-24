Using Flake8
============

What and Why
------------

"Linting is the automated checking of your source code for programmatic
and stylistic errors." -
`OWASP <https://owasp.org/www-project-devsecops-guideline/latest/01b-Linting-Code>`__.
In RuFaS, we use a linter for Python called
`Flake8 <https://flake8.pycqa.org/en/latest/>`__ to ensure that all
lines of code are consistently styled and to prevent overly complex code
from being written.

How
---

Automatic
---------

When a commit is pushed to a remote branch that is based on a protected
branch, the RuFaS repository on GitHub is configured to automatically
run ``flake8`` on all Python files that were added or modified in the
pull request.

If the linting test fails, click on the "Details" button on the status
line for the "Linting" GitHub Action at the bottom of the PR to see
where the linting errors are.

|linting_fail|

Note:
~~~~~

Changes to the GitHub "Linting" Action now make all flake8 violations
prevent merging whereas previously it was only a select few. The goal
here is to catch linting errors before they are merged into the dev
branch.

Any fixes to legacy style guide violations you can do within the files
you're working on are greatly appreciated. Often these are quick fixes
but may need to be done manually.

There may be some legacy linting violations that are not easily fixed
and/or don't make sense to fix for some reason in which case the PR
author should reach out to someone with admin privileges to override the
linting failure which would allow the PR to be merged.

Manual
------

Using the Command Line
~~~~~~~~~~~~~~~~~~~~~~

Quick Start
^^^^^^^^^^^

1. **Open A Terminal Window**:

- Windows: Press ``Win + R``, type ``cmd``, and press Enter. Or search
  "Command Prompt" and click "Open".
- macOS: Click the Launchpad icon in the Dock, type "Terminal" in the
  search field, then click Terminal. Or, in the Finder, open the
  /Applications/Utilities folder, then double-click Terminal.

2. **Navigate To RuFaS**: use the ``cd`` command to navigate to your
   local RuFaS directory. On Windows:

.. code:: sh

   cd path\to\your\RuFaS\RUFAS

On macOS:

.. code:: sh

   cd path/to/your/RuFaS/RUFAS

3. **Install Flake8**: After activating your virtual environment, run:

.. code:: sh

   pip install flake8

Or if you prefer to install and upgrade all RuFaS-required libraries,
run:

.. code:: sh

   pip install -r requirements.txt -U

4. **Running Flake8**: To run Flake8 on all files in the RUFAS
   directory, first navigate to the RUFAS directory, then run:

.. code:: sh

   flake8

To run Flake8 on a specific directory, structure and run a command that
follows the template

.. code:: sh

   flake8 <path to file to be linted> <additional path to file to be linted> <options>

If the path provided to ``flake8`` is a directory (a.k.a. a folder),
then ``flake8`` will lint every file in that directory, and it will
recursively lint all subdirectories. If no path is provided to
``flake8`` it will lint every file and directory within the directory
where it was invoked.

As long as Flake8 is run from the top-level directory of RuFaS or a
subdirectory of the top-level directory, it will be run with the
RuFaS-specific options, which are specified in the ``.flake8``
configuration file of the top level of the RuFaS directory.

*Note*: If you are using PyCharm or VScode (or a different IDE) and your
local RuFaS directory is open, you can click the "Terminal" button to
open up a terminal in your editor. In VScode the button is on the
top-left, in PyCharm it is on the bottom-left.

Using the Script
^^^^^^^^^^^^^^^^

``check_changes.sh`` and ``check_changes.bat`` are scripts that you can
run locally which check all the Python files that you have modified on
the git branch that you are currently on. In other words, it does the
same thing as the GitHub Action but locally, without requiring you to
commit and push your code. Note that this script also runs Mypy so you
may see some type errors. You can read about those
:doc:`here <Using-Mypy>`.

This tool makes it much more convenient and easy to check the files that
you have worked in your branch. Let's work through an example:

In your local feature branch, you want to implement a new feature and
then eventually have that feature merged into the ``dev`` branch. To
implement this feature, you have added code in ``file_one.py`` and
removed code in ``directory_one/file_two.py``. To run ``flake8`` on only
the files that you have modified, you would have to run

.. code:: sh

   flake8 file_one.py directory_one/file_two.py

It is cumbersome to have to type all this out every time you want to
check your work, and at some point you may find you have modified a lot
of files and don't remember exactly which ones they are.
``check_changes.sh`` (or ``check_changes.bat``) fixes this problem for
you by automatically finding the files you have modified, then running
``flake8`` on those files for you. To use it, navigate to the top-level
directory and run one of the following commands depending on your
operating system:

Windows:

.. code:: sh

   .\check_changes.bat

macOS:

.. code:: sh

   ./check_changes.sh

It will display same results as if you had run ``flake8`` directly on
the modified files.

The readout of the errors in the modified files will appear in the
terminal. It will show the location of each file where there is an
error, give a specific flake8 code for the type of error, and give a
printout of the specific line in the file where the error occurred:

::

   RUFAS/routines/feed/feed.py:804:61: E201 whitespace after '('
               self.new_forages.pop(self.new_forages.index( silo))
                                                           ^

Each flake8 violation has a specific code that explains what the style
violation is (e.g. E201 for having whitespace after a ``'('``). `This
guide <https://www.flake8rules.com/>`__ lists all the violations and
shows examples of how to fix them.

Sometimes, the branch your are working on is stacked on top of another
feature branch. In this case, we want to specify a different base branch
(the default is ``dev``). This is done by running a command that is
structured like

.. code:: sh

   .\check_changes.bat <base branch name>

or

.. code:: sh

   ./check_changes.sh <base branch name>

*Note*: If you are using a `GitBash <https://git-scm.com/downloads>`__
or `WSL <https://learn.microsoft.com/en-us/windows/wsl/install>`__
terminal on your Windows machine, follow the macOS instructions. Also,
the ``.bat`` script will only work in the Windows Command Prompt - not
PowerShell.

Configuration
-------------

There are many different options to specify how ``flake8`` runs - what
errors it looks for, how it reports the errors it finds, etc. There are
some specific options we want to consistently invoke when we run
``flake8`` on code in RuFaS, so we have a configuration file that will
take care of adding these options for you. It is written in the file
``.flake8`` in the top-level directory of the code, and looks like

::

   [flake8]
   count = True
   max-line-length = 120

Running ``flake8`` with this configuration file present is equivalent to
running

.. code:: sh

   flake8 --count --max-line-length=120

Having the configuration file makes it easy for both people working on
RuFaS code and the GitHub Action to run Flake8 with same options every
time. And as long as Flake8 is run from the top-level RuFaS directory or
a subdirectory of the top-level directory, it will run with options
specified in the ``flake8`` configuration file.

External Resources
------------------

```flake8``
Documentation <https://flake8.pycqa.org/en/latest/index.html>`__

.. |linting_fail| image:: https://github.com/RuminantFarmSystems/MASM/assets/43901812/6683becd-5b13-4482-8157-802218e1ca1b

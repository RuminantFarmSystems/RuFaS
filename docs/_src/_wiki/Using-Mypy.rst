Using Mypy
==========
What and Why
------------

"Mypy is a static type checker for Python. Type checkers help ensure
that you’re using variables and functions in your code correctly. With
mypy, add type hints (`PEP 484 <https://peps.python.org/pep-0484/>`__)
to your Python programs, and mypy will warn you when you use those types
incorrectly." - `MyPy <https://mypy.readthedocs.io/en/stable/>`__. We
use type hints extensively in RuFaS, so having Mypy is a big help!

*What the heck is a type hint?* Type hints indicate the type (string,
boolean, integer, float, etc) of a variable, function argument, or
return value.

*What constitutes a type error?* When there is a mismatch between a
variable and a value, it will be flagged as a type error. For example,
Mypy would flag the following code:

.. code:: python

   x: int = 10.5

with the error

.. code:: sh

   main.py:24:10: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]

This error message tells us that we are trying to assign a ``float``
value (10.5) to a variable (``x``) that is an ``int``.

How
---

Automatic
---------

When a commit is pushed to a remote branch that is based on a protected
branch, the RuFaS repository on GitHub is configured to automatically
run ``mypy`` on all Python files in the ``RUFAS`` and ``tests`` files
directories, as well as ``main.py``.

After the Mypy GitHub Action has run, it will write the number of errors
it found into the Mypy badge on the README.

.. figure:: /_static/mypy.png
   :alt: RuFaS Overview - GG
   :align: center
   :name: mypy

Note:
~~~~~

Currently the Mypy GitHub Action will only write the number of errors it
finds, it will not block a Pull Request based on any errors it finds.
But please consider checking your type hints carefully, and maybe fixing
a few small issues in the files you're working on so the error count
goes down. Every little bit helps!

Manual
------

Using the Command Line
~~~~~~~~~~~~~~~~~~~~~~

Quick Start
^^^^^^^^^^^

1. **Open A Terminal Window**:

Simply use the terminal provided by your IDE (VS code, PyCharm) or:

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

3. **Install Mypy**: After activating your virtual environment, run:

.. code:: sh

   pip install mypy

Or if you prefer to install and upgrade all RuFaS-required libraries,
run:

.. code:: sh

   pip install -r requirements.txt -U

4. **Running Mypy**: To run Mypy on all files in the RUFAS directory,
   first navigate to the RUFAS directory, then run:

.. code:: sh

   mypy .

To run Mypy on a specific directory, structure and run a command that
follows the template

.. code:: sh

   mypy <path to file to be checked> <additional path to file to be checked> <options>

If the path provided to ``mypy`` is a directory (a.k.a. a folder), then
``mypy`` will check every file in that directory, and it will
recursively lint all subdirectories. If no path is provided to ``mypy``
it will check every file and directory within the directory where it was
invoked.

As long as Mypy is run from the top-level directory of RuFaS or a
subdirectory of the top-level directory, it will be run with the
RuFaS-specific options, which are specified in the ``pyproject.toml``
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
same thing as the GitHub Action but locally, and only the files you have
worked (not all the files in RuFaS). Note that this script also runs
``flake8`` so you may see some linting errors. You can read about those
:doc:`here <Using-Flake8>`.

This tool makes it much more convenient and easy to check the files that
you have worked in your branch. Let's work through an example:

In your local feature branch, you want to implement a new feature and
then eventually have that feature merged into the ``dev`` branch. To
implement this feature, you have added code in ``file_one.py`` and
removed code in ``directory_one/file_two.py``. To run ``mypy`` on only
the files that you have modified, you would have to run

.. code:: sh

   mypy file_one.py directory_one/file_two.py

It is cumbersome to have to type all this out every time you want to
check your work, and at some point you may find you have modified a lot
of files and don't remember exactly which ones they are.
``check_changes.sh`` (or ``check_changes.bat``) fixes this problem for
you by automatically finding the files you have modified, then running
``mypy`` on those files for you. To use it, navigate to the top-level
directory and run one of the following commands depending on your
operating system:

Windows:

.. code:: sh

   .\check_changes.bat

macOS:

.. code:: sh

   ./check_changes.sh

It will display same results as if you had run ``mypy`` directly on the
modified files.

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

There are many different options to specify how ``mypy`` runs - what
errors it looks for, how it reports the errors it finds, etc. There are
some specific options we want to consistently invoke when we run
``mypy`` on code in RuFaS, so we have a configuration file that will
take care of adding these options for you. It is written in the file
``pyproject.toml`` in the top-level directory of the code.

Having the configuration file makes it easy for both people working on
RuFaS code and the GitHub Action to run Mypy with same options every
time. And as long as Mypy is run from the top-level RuFaS directory or a
subdirectory of the top-level directory, it will run with options
specified in the ``mypy`` configuration file.

External Resources
------------------

```mypy`` Documentation <https://mypy.readthedocs.io/en/stable/>`__

.. |image| image:: https://github.com/RuminantFarmSystems/MASM/assets/43901812/8d3f19c0-c57a-4aa6-96d8-9f00041051a7

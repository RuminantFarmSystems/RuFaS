Using Python's Black Formatter
==============================
What and Why
------------

Black is a PEP 8 compliant opinionated formatter with its own style. It
has been integrated into the Github Actions Workflow as a part of the
Linting and Formatting script. This will help our codebase to be more
unified stylistically and takes the code-styling decisions out of the
individual's hands.

How
---

Automatic
---------

When a push is made to a remote branch on Github, the code will be
automatically reformatted using the Black formatter. Those changes will
then be merged to that branch. After that is complete, the normal Flake8
Linting and Github Testing Actions will be run on the reformatted code.

**Note: We've set Black to only format .py files so if you push code
that is only changing .json or .txt files for example, it won't try to
format your code.**

Monitoring Linting and Testing Violations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As noted above, when code is pushed to Github, the Black formatting will
occur first and those changes will be merged into the PR. *The Linting
and Testing Github Actions will still be running on the original commit
pushed to Github.* To ensure code merged to main has no Linting or
Testing violations, monitor the status of this original commit. It will
be the first of 3 which will have the original commit message.

If there is a red X next to the original commit, that means either the
Linting or Testing Action has failed.

.. figure:: /_static/black1.png
   :alt: RuFaS Overview - GG
   :align: center
   :name: rufas overview

Click on the X to learn which Action(s) have failed.

.. figure:: /_static/black2.png
   :alt: RuFaS Overview - GG
   :align: center
   :name: rufas overview

Once all actions have passed and the PR has 2 approvals, it can be
merged to main as normal.

.. figure:: /_static/black3.png
   :alt: RuFaS Overview - GG
   :align: center
   :name: rufas overview

Manual
------

If you want to run Black locally to see its results before making or
adding to a pull request, start by ensuring that Black is installed in
your environment. Once your virtual environment is activated, in the
command line/terminal type:

::

   pip install black

Additionally, Black is now a part of the requirements.txt file so you
can install the requirements to get Black as well.

::

   pip install -r requirements.txt -U

Once installed, to run Black in the command line:

::

   black {source_file_or_directory}

For example, if you're working on animal_manager.py and want to run
Black on this one file to see how it would reformat the code, run:

::

   black RUFAS/routines/animal/animal_manager.py

Again, this is not necessary because the Github Action will run this
exact same formatting command when you push the changed code to Github.
But it is available as an option if you're curious and want to see the
formatting choices it is making.

Configuration
-------------

Part of the decision to use Black as opposed to another Python formatter
is that it removes the majority of the formatting decisions choices. It
is quite prescriptive. One of the key settings Black allows flexibility
with is line length. RuFaS maintains its 120 character line-length
setting despite the Black default setting preference for 88 characters.
This setting, and any future customizations RuFaS chooses, will be
written in the file ``.pyproject.toml`` in the top-level directory of
the code. It looks like this:

::

   [tool.black]
   target-version = ["py310", "py311"]
   line-length = 120
   include = '.*\.py$'

Having the configuration file makes it easy for both people working on
RuFaS code and the GitHub Action to run Black with same options every
time. And as long as Black is run from the top-level RuFaS directory or
a subdirectory of the top-level directory, it will run with options
specified in the ``.pyproject.toml`` configuration file.

External Resources
------------------

`Black
Documentation <https://black.readthedocs.io/en/stable/the_black_code_style/index.html>`__

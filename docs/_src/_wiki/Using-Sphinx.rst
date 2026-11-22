Using Sphinx
============
What and Why
------------

We use
`numpy-style <https://numpydoc.readthedocs.io/en/latest/format.html>`__
docstrings to document the codebase. This allows us to use
`Sphinx <https://www.sphinx-doc.org/>`__ which turns a documentation
structure written reStructuredText (reST) files to compile HTML and
Latex (and subsequently, PDF) documents from our docstrings.

In order to sync up documentation between the docstrings and the
codebase, both the reST files and HTML/Latex files need to be
regenerated. These are very different processes, and do not always need
to be done at the same time. See the "When" section for an explanation
of when each needs to be regenerated.

When
----

The reST files determine the structure of documentation (how different
pages of the documentation are connected to one another), but they do
not directly effect the actual contents of the HTML and Latex pages.
That is determined by the contents of the docstrings in the codebase.

--------------

   **NOTE**: As of Feb. 10, 2025 there are some reST files that do
   directly effect the context of HTML and Latex files generated with
   them. They are legacy scientific documentation and were written
   manually. They will likely be removed at some point as part of the
   scientific documentation rewrite that is currently happening, but
   until then they can be ignored when regenerating the reST files.

--------------

As a rule of thumb, the reST files do not need to be updated unless
files are added or removed from the codebase. If the docstrings in a
file are updated, then it may be appropriate to update the HTML and/or
Latex Documentation. See the "reStructuredText" and "HTML" sections of
this wiki pages for instructions to regenerate the reST and HTML files,
respectively.

If both reST and HTML/Latex files are being regenerated, it is important
to do the reST files *first*, then the HTML and/or Latex files.

How
---

reStructuredText
----------------

The reST files can be automatically generated with the
```sphinx-apidoc`` <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`__
command, an extension of Sphinx.

Run the following command from the root of the project directory to
regenerate the reST files:

::

   sphinx-apidoc -f -o docs/_src/_code/ . tests --maxdepth=1 --separate

An explanation of what the arguments to ``sphinx-apidoc`` are and what
they do:

- ``-f``: "force"; this command overwrites existing reST files based on
  what it finds in the codebase.
- ``-o docs/_src/_code/``: path where the new reST files should be
  written to. Sphinx only reads the ``docs/_src`` folder, so files
  written anywhere else are not part of the documentation.
- ``.``: path to the modules and packages that reST files will be
  generated/regenerated for.
- ``tests``: path the modules and packages that reST files will not be
  generated/regenerated for.
- ``--maxdepth=1``: when the subpackages and submodules are listed, this
  determines whether their subpackages and submodules are also listed in
  the page.
- ``--separate``: instead of listing all the documentation of modules
  from the same directory next to each other, this argument gives each
  module a separate page for its documentation.

The generated reST files are not committed, except
``docs/_src/_code/modules.rst``. The GitHub workflow generates them
again each time it builds the website (see the "Automatic" section).

HTML
----

Automatic
~~~~~~~~~

The website is built and published by the "Build and Deploy Sphinx
Docs" GitHub workflow (``.github/workflows/sphinx.yml``). It runs every
time something is pushed to ``main``. It generates the reST files,
builds the HTML, and publishes it to the
`RuFaS documentation website <https://ruminantfarmsystems.github.io/RuFaS/>`__.
It does not commit anything to a branch.

The workflow can also be started by hand from the "Actions" tab of
GitHub, with the "Run workflow" button. It publishes the documentation
of the branch you select, so select ``main``.

Manual
~~~~~~

To preview Sphinx's output locally before submitting a pull request:

1. Install the documentation tools once, from the root of the project:
   ``pip install -e ".[build_docs]"``.
2. To include the code pages, run the ``sphinx-apidoc`` command from the
   "reStructuredText" section first. Without it, only the wiki pages are
   built.
3. From the ``docs`` directory, run ``make html``. On MS Windows, run
   ``./make html``. Use ``make latexpdf`` to produce Latex files.

Where are the generated files?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Under the same ``docs`` folder, navigate to ``/_build/html`` to see
generated HTML files.

- ``index.html`` is the entry to the entire HTML pages.
- ``_code/RUFAS.html`` is the entry to the RUFAS codebase.

Alternatively, you can open other HTML files, they are mostly HTMLs for
all the different subpackages.

.. _note-1:

Note
^^^^

If you generate Latex documents, the output is in ``/_build/latex`` with
a similar pattern.

Navigating the HTML
~~~~~~~~~~~~~~~~~~~

In HTML files, subpackages act as folders, and submodules are analogous
to Python files in a specific directory. The structure mirrors the RUFAS
codebase, so navigating through the HTML files is similar to exploring
the RUFAS codebase.

External Resources
------------------

`Doc String
Reference <https://numpydoc.readthedocs.io/en/latest/format.html>`__

`Doc String Guide <https://realpython.com/documenting-python-code/>`__

`Sphinx <https://www.sphinx-doc.org/>`__

`sphinx-apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`__

Sphinx Documentation (docstrings)
=================================

What is Sphinx Documentation? What is docstring?
------------------------------------------------
A docstring is a string literal that occurs as the first statement in a module, function, class, or method definition. Such a docstring becomes the ``__doc__`` special attribute of that object. See `PEP 257 <https://www.python.org/dev/peps/pep-0257/>`_.

Sphinx is a tool that makes it easy to create intelligent and beautiful documentation. Sphinx is a powerful documentation generator that works based on docstrings and has many great features for writing technical documentation including:

- Generate web pages, printable PDFs, documents for e-readers (ePub), and more all from the same sources
- You can use reStructuredText or Markdown to write documentation
- An extensive system of cross-referencing code and documentation
- Syntax-highlighted code samples
- A vibrant ecosystem of first- and third-party extensions

See `Getting Started with Sphinx <https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html>`_.

Why are we investing in it?
---------------------------
1. We need to document the code anyway; it is better to do it sooner.
2. We want to adopt the Python Enhancement Proposal (`PEP 257 <https://www.python.org/dev/peps/pep-0257/>`_).
3. This provides an opportunity to review the code and double-check it to make sure it reflects the expectations.
4. It lets us identify the problems before they cause problems.
5. It is easy for subject-matter experts to write Sphinx docs; this can be used as a medium between them and programmers.
6. We will use this for writing unit tests.

How are we going to implement it?
---------------------------------
Similar to unit tests, first we need to make sure those who will be doing it are comfortable with doing it. Then, we will employ the same prioritization strategy to gradually add a docstring to the code. This requires collaboration between programmers and subject-matter experts.

Preferably, programmers should work on modules that they are most familiar with; however, for logistical reasons, we might need programmers to work on modules that they have not worked with before.

There are several `different docstring formats <https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html>`_ which can be used as Sphinx’s input. We will adopt the NumPy style as it is more human-readable and widely used in scientific code bases (see `NumPy Docstring Standard <https://numpydoc.readthedocs.io/en/latest/format.html>`_ and `Documenting Python Code <https://realpython.com/documenting-python-code/>`_).

Note that unit testing and Sphinx documentation go hand in hand together.
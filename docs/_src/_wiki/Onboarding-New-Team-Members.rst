Onboarding New Team Members
===========================

The onboarding checklist
========================

**Make sure you (in no particular order):**

- **Read this document in its entirety**

  - It takes a while to go through it and see all the linked resources,
    but it will save lots of time down the road.

- **Meet with your supervisor**

  - Get onboard with the team, get to know the people you will closely
    work with, learn about the work that you will be doing, clarify the
    expectations, etc…

- **Join Slack**

  - Slack is the main communication channel for the team, not email but
    an email is an option if needed
  - Download and join the RuFas Slack group.
  - Add to specific channels that are related to your work

- **Join Basecamp**

  - Basecamp is an efficient collaboration tool to keep track of
    assignments, work together on documents, plan projects, chat, and
    more.
  - Make sure you reach out to your supervisor for a Basecamp invite.

- **Join GitHub Repo**

  - Create a GitHub account if you don't have one already, reach out to
    your supervisor for a GitHub invite.
  - Look at current open pull requests and recently merged/closed pull
    requests to get an idea of what recent activity has been across the
    RuFaS model.

- **Setup RuFaS**

  - Follow the step-by-step instruction in **getting started** section.
    Do not move on to the next steps until you have installed Python,
    Git, and an IDE.

  - If using PyCharm as IDE, `these videos are a good starting
    place <https://3.basecamp.com/3486446/buckets/5296287/vaults/2713991190>`__

    - Start with "getting_started.mov" first and then watch the other 2
      videos.

  - If using another IDE such as VS Code, clone RuFaS to the local
    computer and set up a virtual environment before installing the
    requirements in the requirements.txt document.

    - If not familiar with virtual environments or how this process
      works to set them up, Niko Tomlinson (ndt2@cornell.edu) would be
      happy to help go through the process (as of 11/21/22).
    - The videos still apply in the link above but it is a best practice
      to use a virtual environment.

  - Everyone should watch this `Recorded onboarding
    session <https://3.basecamp.com/3486446/buckets/5296287/uploads/6661565836>`__
    to familiarize yourself with the overall structure of the
    repository.

  - People interested in running simulations should watch `this training
    video <https://youtu.be/A_u2cxla42c?si=fjHYxGgub9czLe8J>`__

- **Watch** `Uncle Bob's clean code philosophy
  videos <https://www.youtube.com/playlist?list=PLs4sTjbm8kLhbJy-rT4DILg-kKw3ZCwDx>`__
  (all 6 videos in the series)

  - These are coding guidelines and rules we should all be using.
  - TDD (Test Driven Development) would be nice to have down the line
    but right now are trying to refactor and increase test coverage of
    the existing code base.

- Review `Version Control
  documents <https://3.basecamp.com/3486446/buckets/5296287/vaults/2177548970>`__
  and processes in Basecamp.

  - Ask questions and explore GitHub more with the Version-Control
    process in mind.

- **Zoom meeting schedules and invites**

  - Biweekly all-team-meeting invite
  - Check-ins with the supervisor and/or team

- **Meet other team members**

  - How they navigate the model
  - How they personally use GitHub and Git (some use GitHub web app,
    some use GitHub Desktop app)
  - What they're working on
  - Why they're addressing that issue
  - How they're solving it

--------------

Getting Started
---------------

- **Install Python**

  - The `RUFAS pyproject.toml
    file <https://github.com/RuminantFarmSystems/MASM/blob/dev/pyproject.toml>`__
    has the most up-to-date information on what versions of Python are
    supported by RUFAS. Check the version requirments in that file's
    ``[project]`` > ``requires-python`` section and then go to the
    `official Python website <https://www.python.org/downloads/>`__ to
    download a Python version that is supported by RUFAS.
  - **Windows** (you can follow this detailed `tutorial by
    DigitalOcean <https://www.digitalocean.com/community/tutorials/install-python-windows-10>`__)

    - Download the latest Python installer from the `official Python
      website <https://www.python.org/downloads/>`__.
    - Follow the setup wizard to install Python. (Keep hitting next)
    - Verify the installation by:

      - Go to Start and enter cmd in the search bar. Click Command
        Prompt.
      - Enter the following command in the command prompt:
        ``python --version``
      - A message indicating the Python version should be printed out on
        your screen: ``Python 3.1x.x``

  - MacOS (you can follow this detailed `tutorial by
    DataQuest <https://www.dataquest.io/blog/installing-python-on-mac/>`__)

    - Download the latest Python installer from the `official Python
      website <https://www.python.org/downloads/>`__.
    - Follow the setup wizard to install Python. (Keep hitting next)
    - Verify the installation by:

      - Open the Terminal.
      - Enter the following command in the terminal:
        ``python --version``
      - A message indicating the Python version should be printed out on
        your screen: ``Python 3.1x.x``

  - Linux

    - If you are using Linux, I don't believe you would need help
      installing Python. If you do need any assistance, Allister Liu
      (al2562@cornell.edu) would be happy to help go through the process
      (as of 08/24/23).

- **Install Git**

  - If you don't already have git set up on your system, download git
    from the `official git website <https://git-scm.com/downloads>`__.
  - Follow the setup wizard to install git. (Keep hitting next)
  - Verify the installation by:

    - Open Command Prompt for Windows, Terminal for macOS.
    - Enter the following command: ``git --version``
    - A message indicating the git version should be printed out on your
      screen: ``git version 2.40.0.windows.1``

- **Install an IDE** of your choice

  - VisualStudio Code

    - Download VS Code from the `official VisualStudio
      website <https://code.visualstudio.com/download>`__.
    - Follow the setup wizard to install VS Code. (Keep hitting next).

  - PyCharm (make sure to choose the Community version of Pycharm)

    - Follow the `official detailed tutorial by
      JetBrains <https://www.jetbrains.com/help/pycharm/installation-guide.html#standalone>`__.
    - Download VS Code from the `official JetBrains
      website <https://www.jetbrains.com/pycharm/download>`__.
    - Follow the setup wizard to install PyCharm. (Keep hitting next).

- **Clone RuFas MASM repository**

  - Follow this `guide from
    GitHub <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository>`__
    to clone the RuFaS MASM repository.

- **Set up the environment**

  - VS Code
  - PyCharm

- **Test run**

  - Run the default scenario by typing "python main.py" in your terminal
  - Note that you will only collect outputs related to logs, warnings,
    and errors until you have created an output filter (See the Output
    Manager section of the Wiki for more information on the output
    filters).

Git Workflow
~~~~~~~~~~~~

1. **Prepare Changes in a New Branch:**

.. code:: sh

   $ git checkout -b mybranch
   $ [edit files...]
   $ git add [files...]

2. **Test your Changes:** In the root of the project, check that your
   code passes all the tests by running

.. code:: sh

   $ pytest tests

You can also check that your code matches the style of the project:

.. code:: sh

   $ flake8 . --count --show-source --statistics

For more information about how to check code style, read
`this <https://github.com/RuminantFarmSystems/MASM/wiki/Using-flake8>`__.

3. **Commit your Changes:** When all the tests pass and the code is
   properly formatted, commit your changes.

.. code:: sh

   $ git commit -m "<commit message>"

​

Submitting a Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~

To submit your changes for review and inclusion into MASM, follow these
steps:

1. **Push your branch:** Push your branch to the remote repository using
   the following command:

.. code:: sh

   $ git push origin mybranch

2. **Code Review:** Your code must be reviewed and approved by at least
   2 members of the RuFaS team. Please reach out to the team on slack so
   that others can review your work!
3. **Making changes:** To modify your pull request to address changes
   requested by your code reviewers, follow the steps outlined in the
   `git workflow <#git-workflow>`__ section, and push your branch
   following step 1 of Submitting a Pull Request.

Actively used and referenced basecamp documents
-----------------------------------------------

- Animal Module:

  - `Animal
    Background <https://docs.google.com/document/d/1rEwE4QSpZcwbx5zuMd3vJ_YxW-NLApM21ArDL9U2bw8/edit>`__
  - `Animal Grouping and Pen
    Allocation <https://docs.google.com/document/d/11msdXtKqvewv5BymfHe64S9_16qMGoVq/edit>`__
  - `Ration
    Formulation <https://3.basecamp.com/3486446/buckets/5296287/uploads/5229484750>`__
  - `Animal Life Cycle
    Pseudocode <https://3.basecamp.com/3486446/buckets/5296287/uploads/5570363102>`__

    - Being updated as of 11/22 but maybe still useful in its current
      form

- Crop & Soil Module:

  - `Crop
    Pseudocode <https://docs.google.com/document/d/11881cKjbtfXhEHQ63zTJTVwES8lImVzC7nEi0cbD9Vc/edit#heading=h.jke07n3yp5ok>`__
  - `Soil
    Pseudocode <https://docs.google.com/document/d/1yrlYhPAmNDweJMQnEp8I1H3nje39390lymnmW_YlmfE/edit>`__
  - `Field Management
    Pseudocode <https://docs.google.com/document/d/1uom3HQe999UnmCZNdeW30QrCCDTHRKoWhwNBYBF3wuk/edit>`__
  - `Soil & Water Assessment Tool (SWAT)
    Documentation <https://3.basecamp.com/3486446/buckets/5296287/uploads/2699065264>`__
  - `RuFaS Code
    Diagram <https://3.basecamp.com/3486446/buckets/5296287/uploads/5133430279>`__

    - Slightly out of date but still a useful visualization tool
    - Focused primarily on Crop & Soil Module code

Team practices and initiatives
==============================

What - Why- How framework
-------------------------

What is What - Why- How framework?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What - Why - How framework is an exercise to provide the intended
information clearly and without ambiguity, with the minimum required
effort to understand it. The order of these 3 questions varies from
discipline to discipline, for instance, in marketing, it is important to
ask why first then ask how and what. However, as a common practice in
journalism and academia, we aim to answer the "what" question first, so
the reader knows what this information is about, and can decide whether
to continue reading or not. Then, we answer the "why" question so the
reader knows its significance and importance. Finally, we complete the
message by answering the "how" question.

A great example of this framework is academic paper structure: in the
introduction, we answer the question "what is this paper about", in the
literature review section we answer the question "why is this paper
important", and in the methodology section we answer the question "how
was the research done".

Why is it important?
~~~~~~~~~~~~~~~~~~~~

RuFaS is a diverse team, we come from different cultural and academic
backgrounds, we are at different stages of our lives, and we have
different years of experience. It is important for us to be able to
communicate effectively.

How are we going to practice it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The effort of practicing this framework, as you have noticed by now,
starts from this document itself. Moving forward, we expect to have this
framework in all of our documents, especially in our reports. In other
words, when reading and writing a document, you should expect these 3
questions (what, why, how) clearly stated and answered for each part of
the document that can have some level of independence from the rest of
the document.

Unit testing
------------

What is unit testing?
~~~~~~~~~~~~~~~~~~~~~

Unit testing is a type of software testing where individual units or
components of software are tested. The purpose is to validate that each
unit of the software code performs as expected. Unit testing is done
during the development (coding phase) of an application by the
developers. Unit tests isolate a section of code and verify its
correctness. A unit may be an individual function, method, procedure,
module, or object. Unit testing is a WhiteBox testing technique that is
usually performed by the developer. See
https://realpython.com/python-testing/

Why are we investing in it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Software Development Life Cycle (SDLC), Software Testing Life Cycle
(STLC), and V Model, unit testing is the first level of testing done
before integration testing. It is a common practice to NOT accept any
new code to Version Control System (VCS, e.g., GitHub) without a
properly written test suite. Unit testing is important because it
ensures that individual components of the system are working correctly
at the most granular level. Also, when modifying the code, we can be
confident that the new code is not breaking anything because all unit
tests are passing. Although we are not advocating V model in RuFaS
(yet), here is a visualization of the V Model for reference:

|The V model|

How are we going to implement it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have started the process by making sure all programmers are
comfortable with writing unit tests in Python. When this is done, we
will continue by compiling a list of a minimal set of unit tests. Then,
we will prioritize them by counting the dependencies of each unit; i.e.
the more other units are dependent on a unit, the higher priority it
has. We will work on adding unit tests starting from the highest
priority.

Preferably, programmers should work on modules that they are most
familiar with; however, for logistic reasons, we might need programmers
to work on modules that they have not worked with before.

Note that unit testing and sphinx documentation go hand in hand
together.

Sphinx Documentation (docstrings)
---------------------------------

What is Sphinx Documentation? What is docstring?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A docstring is a string literal that occurs as the first statement in a
module, function, class, or method definition. Such a docstring becomes
the \__doc\_\_ special attribute of that object. `PEP
257 <https://www.python.org/dev/peps/pep-0257/>`__

Sphinx is a tool that makes it easy to create intelligent and beautiful
documentation. Sphinx is a powerful documentation generator that works
based on docstrings and has many great features for writing technical
documentation including:

- Generate web pages, printable PDFs, documents for e-readers (ePub),
  and more all from the same sources
- You can use reStructuredText or Markdown to write documentation
- An extensive system of cross-referencing code and documentation
- Syntax highlighted code samples
- A vibrant ecosystem of first and third-party extensions.

See
https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html

.. _why-are-we-investing-in-it-1:

Why are we investing in it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. We need to document the code anyways, it is better to do it sooner.
2. We want to adopt the Python Enhancement Proposal (`PEP
   257 <https://www.python.org/dev/peps/pep-0257/>`__).
3. This provides an opportunity to review the code and double-check it
   to make sure it reflects the expectations.
4. It lets us identify the problems before they cause problems.
5. It is easy for subject matter experts to write sphinx docs, this can
   be used as a medium between them and programmers.
6. We will use this for writing unit tests.

.. _how-are-we-going-to-implement-it-1:

How are we going to implement it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to unit tests, first we need to make sure those who will be
doing it are comfortable with doing it. Then, we will employ the same
prioritization strategy to gradually add a docstring to the code. This
requires collaboration between programmers and subject matter experts.

Preferably, programmers should work on modules that they are most
familiar with; however, for logistic reasons, we might need programmers
to work on modules that they have not worked with before.

There are several\ `different docstring
formats <https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html>`__\ which
can be used as Sphinx's input. We will adopt the Numpy style as it is
more human-readable and widely used in scientific code bases. (See
https://numpydoc.readthedocs.io/en/latest/format.html and
https://realpython.com/documenting-python-code/ )

Note that unit testing and sphinx documentation go hand in hand
together.

Test-Driven Development (TDD)
-----------------------------

What is TDD?
~~~~~~~~~~~~

Test-Driven Development (TDD) is a software development approach in
which test cases are developed to specify and validate what the code
will do. In simple terms, test cases for each functionality are created
and tested first and if the test fails then the new code is written in
order to pass the test and make the code simple and bug-free.

TDD starts with designing and developing tests for every small
functionality of an application. TDD framework instructs developers to
write new code only if an automated test has failed. This avoids
duplication of code. `see
this <https://www.agilealliance.org/glossary/tdd/#q=~(infinite~false~filters~(postType~(~'page~'post~'aa_book~'aa_event_session~'aa_experience_report~'aa_glossary~'aa_research_paper~'aa_video)~tags~(~'TDD))~searchTerm~'~sort~false~sortDirection~'asc~page~1)>`__

Why are we adopting it?
~~~~~~~~~~~~~~~~~~~~~~~

In addition to the well-known benefits of TDD (`see
this <http://bit.ly/3XeH2qX>`__), it can help us to reduce the negative
impacts of having a diverse team. Moreover, there is a trend in the
industry to adopt TDD; by following this trend, we are aiming for
industry standards and preparing our student programmers for a better
career path in the future.

.. _how-are-we-going-to-practice-it-1:

How are we going to practice it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We will adopt TDD only when we have implemented a good amount of unit
tests and programmers are familiar with writing test cases. Then, we
need to make sure everyone knows how TDD works. After which, we will
enforce TDD by emphasizing on it in meetings and reports; as well as
rejecting any pull request which does not reflect TDD.

Code Coverage
-------------

What is code coverage?
~~~~~~~~~~~~~~~~~~~~~~

Code coverage is the percentage of code that is covered by automated
tests. Code coverage measurement simply determines which statements in a
body of code have been executed through a test run, and which statements
have not. In general, a code coverage system collects information about
the running program and then combines that with source information to
generate a report on the test suite's code coverage.

`see
this <https://confluence.atlassian.com/clover/about-code-coverage-71599496.html>`__

.. _why-is-it-important-1:

Why is it important?
~~~~~~~~~~~~~~~~~~~~

Code coverage is part of a feedback loop in the development process. As
tests are developed, code coverage highlights aspects of the code that
may not be adequately tested and which require additional testing. This
loop will continue until coverage meets some specified target.

Code coverage also helps us be sure that we are doing TDD correctly and
not leaving holes in the test suite.

How can we increase it?
~~~~~~~~~~~~~~~~~~~~~~~

- Over time, we will identify the more important parts of the code which
  are lacking coverage, and we will work on adding tests for them.
- When a programmer adds code to the code base, the expectation is that
  they have followed TDD, therefore the coverage for the new code should
  be 100%.
- Modification also should follow TDD; therefore, when working on an
  existing code, the programmer is expected to have enough testing for
  it.

Type checking
-------------

What is Type checking?
~~~~~~~~~~~~~~~~~~~~~~

`see this <https://realpython.com/python-type-checking/>`__

.. _why-are-we-investing-in-it-2:

Why are we investing in it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to TDD

.. _how-are-we-going-to-implement-it-2:

How are we going to implement it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to TDD

Linting
-------

What is linting?
~~~~~~~~~~~~~~~~

Linting highlights syntactical and stylistic problems in your Python
source code, which oftentimes helps you identify and correct subtle
programming errors or unconventional coding practices that can lead to
errors. Read
`this <https://github.com/RuminantFarmSystems/MASM/wiki/Using-flake8>`__
to learn how code is linted in RuFaS.

.. _why-are-we-investing-in-it-3:

Why are we investing in it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to TDD

.. _how-are-we-going-to-implement-it-3:

How are we going to implement it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to TDD

Nice-to-haves for the onboarding experience
-------------------------------------------

- Basecamp folder specifically for new development hires.

- Basecamp Navigation document (description of high-level folders and
  what can be found there)

- Document outlining current and previous project goals (a
  summary/overview and timeline of the RuFaS development)

  - Upcoming timeline benchmarks (big picture)

- Model diagram (not exhaustive so it's digestible)

- Org chart with the role and team definitions and expectations

- Updated video instructions on:

  - installing model (for both PyCharm and at least one non-PyCharm IDE)
  - version control practices

Document version history
========================

+--------------+------------------+-----------------+--------------------+
| Date         | Doc Status       | Actor(s)        | Contact info       |
+==============+==================+=================+====================+
| Dec 9, 2021  | Initiated        | Pooya Hekmati   | sh2235@cornell.edu |
+--------------+------------------+-----------------+--------------------+
| Dec 14, 2021 | Final Draft      | Pooya Hekmati   | sh2235@cornell.edu |
+--------------+------------------+-----------------+--------------------+
| Dec 20, 2021 | Modified         | Kristan F. Reed | kfr3@cornell.edu   |
+--------------+------------------+-----------------+--------------------+
| Dec 20, 2021 | Approved         | Kristan F. Reed | kfr3@cornell.edu   |
+--------------+------------------+-----------------+--------------------+
| Nov 21, 2022 | Repurposed       | Niko Tomlinson  | ndt2@cornell.edu   |
+--------------+------------------+-----------------+--------------------+
| Nov 27, 2022 | Modified, Final  | Pooya Hekmati   | sh2235@cornell.edu |
|              | Draft            |                 |                    |
+--------------+------------------+-----------------+--------------------+
| Nov 28, 2022 | Modified,        | Kristan F. Reed | kfr3@cornell.edu   |
|              | Approved         |                 |                    |
+--------------+------------------+-----------------+--------------------+
| Jan 14, 2023 | Converted the    | Pooya Hekmati   | sh2235@cornell.edu |
|              | doc to wiki page |                 |                    |
+--------------+------------------+-----------------+--------------------+
| Sep 27, 2023 | Added links to   | Ed Hansen       | eih26@cornell.edu  |
|              | ``flake8`` wiki  |                 |                    |
|              | page             |                 |                    |
+--------------+------------------+-----------------+--------------------+

--------------

.. |The V model| image:: https://media.geeksforgeeks.org/wp-content/uploads/V-Model.png

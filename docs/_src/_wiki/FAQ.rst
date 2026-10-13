Frequently Asked Questions
============================

Start with :doc:`onboarding` for installation and a first run, or use
:doc:`How-to-Guides` for a specific task.

Which Python version do I need?
---------------------------------

RuFaS supports Python 3.12 and 3.13. Check with ``python --version`` and
activate the virtual environment before installing dependencies with
``python -m pip install .``. Python 3.14 and later are outside the current
supported range. The repository's ``pyproject.toml`` defines the supported
versions and dependencies.

Do I need VS Code or GitHub Desktop?
--------------------------------------

You can use a terminal and any text editor. VS Code and GitHub Desktop
are optional tools demonstrated in the onboarding material. You do not
need to join the development team to run RuFaS or submit a contribution.

Which file decides what simulation runs?
------------------------------------------

By default, ``python main.py`` reads ``input/task_manager_metadata.json``.
Its ``files.tasks.path`` selects a task file, and each simulation task's
``metadata_file_path`` selects the simulation metadata. That metadata
points to the input data and their validation properties. See
:ref:`how-to-change-inputs` and :doc:`Input-Manager`.

Why do I get a file-not-found error?
--------------------------------------

Run commands from the repository root, where ``main.py`` and ``input``
are located. Check the path supplied to ``-p`` and the paths inside your
metadata and task files. Installing the package supplies Python
dependencies; keep the repository's input and output filter files
available when you run a simulation.

Why are there no CSVs or graphs?
----------------------------------

Output files depend on enabled filters. A file named
``_csv_all_variables.txt`` is disabled; copy it to
``csv_all_variables.txt`` to enable it. Check the task's
``filters_directory`` and output directory settings. Graphs also need a
valid ``graph_`` filter and must not be disabled with ``--no-graphics``.
Follow :ref:`how-to-select-outputs` and check the logs for filter errors.

Where can I find errors and warnings?
---------------------------------------

Logs are normally written under ``output/logs``, although task settings
and ``--logs-dir`` can change their location. Use ``-v warnings`` to
show warnings and errors in the terminal, or ``-v logs`` for more detail.
Check both Task Manager and simulation logs: a task can fail while other
tasks continue. Review validation errors before using the results. See
:doc:`Output-Manager` and :doc:`RuFaS-Command-Line-Arguments`.

Why do repeated runs produce different results?
-------------------------------------------------

RuFaS includes stochastic processes. For a reproducible comparison, keep
the code version, dependencies, inputs, and random seed settings fixed.
The example configuration enables ``set_seed`` and the example task uses
``random_seeds: [42]``. A ``SIMULATION_SINGLE_RUN`` task accepts exactly
one seed. See :doc:`Task-Manager` for tasks that run multiple simulations,
and :doc:`Known-Limitations` for interpretation considerations.

What should I do if a simulation uses too much memory?
--------------------------------------------------------

Reduce ``parallel_workers`` in the task file and try a shorter simulation
or smaller herd. See :doc:`Chunkification` for saving output data in
chunks. Chunkification does not remove every memory cost, including
postprocessing. Keep only the output filters you need to limit exported
files; output filters do not by themselves stop variables being collected.

Where are the scientific equations and assumptions?
-----------------------------------------------------

:doc:`Scientific-Documentation` links to the downloadable scientific
manual and its source. Use the manual alongside :doc:`Data-Origins` and
:doc:`Known-Limitations` when interpreting model results.

How can I report a problem or contribute?
-------------------------------------------

Read :doc:`Contributing-to-RuFaS` for coding and noncoding contributions.
For a bug report, include the code version, Python version, steps to
reproduce, relevant input settings, and error logs. Follow
:doc:`creating_github_issue` to open an issue. For general inquiries,
email contact@rufas.org.

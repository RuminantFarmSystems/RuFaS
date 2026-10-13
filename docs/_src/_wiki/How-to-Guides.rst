How-to Guides
===============

Use these guides after :doc:`installing RuFaS <onboarding>`. Run commands
from the repository root with your virtual environment activated.

* :ref:`how-to-run-simulation`
* :ref:`how-to-change-inputs`
* :ref:`how-to-select-outputs`
* :ref:`how-to-build-docs`

For help with errors, see :doc:`FAQ`. For options and file formats, use
the pages under **Simulation Reference** in the navigation.

.. _how-to-run-simulation:

How to run a simulation
-------------------------

#. Open ``input/task_manager_metadata.json``. Its ``files.tasks.path``
   selects the task file. In the supplied example, this is
   ``input/data/tasks/example_freestall_task.json``.
#. Open that task file and check each task's ``metadata_file_path`` and
   ``output_prefix``. The example selects
   ``input/metadata/example_freestall_dairy_metadata.json`` and uses the
   output prefix ``freestall``.
#. Run the selected tasks:

   .. code-block:: console

      python main.py -p input/task_manager_metadata.json -v warnings

#. After the run finishes, check the logs in ``output/logs`` for failed
   tasks and validation errors. Look for the task's output prefix in
   the generated files. CSVs, reports, and graphs depend on the enabled
   output filters; see :ref:`how-to-select-outputs`.

To use a different task manager metadata file, replace the path after
``-p``. This option takes a **metadata file**, rather than the task file
itself. If a file cannot be found, check its path and run from the
repository root. For all options, run ``python main.py --help`` or read
:doc:`RuFaS-Command-Line-Arguments` and :doc:`Task-Manager`.

.. _how-to-change-inputs:

How to change simulation inputs
---------------------------------

Keep the supplied examples as a baseline by copying the files you change.
The input chain is: task manager metadata, task file, simulation metadata,
and finally the input data files.

#. Copy ``input/task_manager_metadata.json`` to
   ``input/my_task_manager_metadata.json`` and copy
   ``input/data/tasks/example_freestall_task.json`` to
   ``input/data/tasks/my_farm_task.json``.
#. In your task manager metadata, set ``files.tasks.path`` to
   ``input/data/tasks/my_farm_task.json``.
#. Copy ``input/metadata/example_freestall_dairy_metadata.json`` to
   ``input/metadata/my_farm_metadata.json``. In your task file, set
   ``metadata_file_path`` to this new path and ``output_prefix`` to
   ``my_farm``.
#. In your simulation metadata, follow ``files.config.path`` to the
   simulation configuration. Copy that configuration to
   ``input/data/config/my_farm_config.json`` and update the metadata path
   to match. Change a setting, such as ``end_date``, within the available
   weather data period. Follow the same copy-and-update process for any
   other input data you want to change. Keep the ``properties`` entries
   so RuFaS can validate your inputs.
#. Run your scenario:

   .. code-block:: console

      python main.py -p input/my_task_manager_metadata.json -v warnings

#. Check the logs for validation errors and confirm the output filenames
   use ``my_farm``. Compare the changed results with the baseline before
   making further changes.

If the results appear unchanged, trace each path in the chain to confirm
the task uses your copied files. For invalid values, read the validation
message and check the required units, types, and ranges in
:doc:`Input-Manager`. The :doc:`Data-Collection-App` can help you create
input files through forms.

.. _how-to-select-outputs:

How to select CSVs, reports, and graphs
-----------------------------------------

#. Check ``filters_directory`` in your task configuration. If omitted,
   the default is ``output/output_filters``.
#. To export all collected variables as a CSV, copy
   ``output/output_filters/_csv_all_variables.txt`` to
   ``output/output_filters/csv_all_variables.txt``. A leading underscore
   disables a filter because its filename no longer starts with a
   supported output prefix. Keep the copy in your task's filters directory
   if you use a different directory.
#. For a smaller export, edit the copied filter to select the variables
   you need. See :doc:`Output-Manager` for text and JSON filter formats.
   Enable a ``report_`` filter for an aggregated report or a ``graph_``
   filter for a plot, following :doc:`Report-Generator` or
   :doc:`Graph-Generator` for the required settings.
#. Run the simulation again. Check the task's ``csv_output_directory``,
   ``report_directory``, or ``graphics_directory`` for the files. Their
   defaults are ``output/CSVs``, ``output/reports``, and
   ``output/graphics``, respectively.

If an output is missing, check that the filter is enabled, is in the
selected directory, and matches variable names produced by the run.
Inspect ``output/logs`` for filter validation and generation errors.
For graphs, also check that you did not pass ``--no-graphics``.

.. _how-to-build-docs:

How to preview documentation changes
--------------------------------------

#. Edit the reStructuredText pages in ``docs/_src/_wiki``. Add new pages
   to the appropriate ``toctree`` in ``docs/_src/index.rst`` so readers
   can find them in the navigation.
#. Install the documentation dependencies in your virtual environment:

   .. code-block:: console

      python -m pip install -e ".[build_docs]"

#. Generate the code reference from the repository root. In PowerShell,
   macOS, or Linux, use:

   .. code-block:: console

      sphinx-apidoc -ed 1 --remove-old -o docs/_src/_code/ "$PWD" "$PWD/tests/"

   In Windows Command Prompt, use:

   .. code-block:: bat

      sphinx-apidoc -ed 1 --remove-old -o docs/_src/_code/ "%CD%" "%CD%/tests/"

   Then build the site:

   .. code-block:: console

      python -m sphinx -b html docs/_src docs/_build/html

#. Open ``docs/_build/html/index.html`` in a browser. Follow the new
   navigation and links, and check the build output for warnings about
   missing documents, unresolved references, and formatting errors.

If Sphinx reports a missing extension, check that the virtual environment
is active and reinstall the documentation dependencies. Submit changes
to the source pages through a pull request; see
:doc:`Contributing-to-RuFaS`. The deployment workflow publishes the built
site. See :doc:`Using-Sphinx` for more about code documentation.

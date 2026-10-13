Frequently Asked Questions
============================

Start with :doc:`onboarding` for installation and a first run, or use
:doc:`How-to-Guides` for a specific task.

.. contents:: Find a topic
   :local:
   :depth: 1

Getting started and participation
-----------------------------------

Which Python version do I need?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RuFaS supports Python 3.12 and 3.13. Check with ``python --version`` and
activate the virtual environment before installing dependencies with
``python -m pip install .``. Python 3.14 and later are outside the current
supported range. The repository's ``pyproject.toml`` defines the supported
versions and dependencies.

Do I need VS Code or GitHub Desktop?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use a terminal and any text editor. VS Code and GitHub Desktop
are optional tools demonstrated in the onboarding material. You do not
need to join the development team to run RuFaS or submit a contribution.

How can I report a problem or contribute?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Read :doc:`Contributing-to-RuFaS` and the repository README, and follow
the code of conduct linked from the contribution guidelines. For a bug
report, include the code version, Python version, steps to reproduce,
relevant input settings, and error logs. Follow
:doc:`creating_github_issue` to open an issue. For general inquiries,
email contact@rufas.org.

How do I model a scenario that is not covered by the examples?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check :doc:`Scientific-Documentation` and :doc:`Known-Limitations` to
understand the supported processes and assumptions. Ask about your
scenario on the
`RuFaS discussion board <https://github.com/RuminantFarmSystems/RuFaS/discussions>`_,
including the management system, inputs, and outputs you need. A scenario
may require new scientific methods or code rather than only input changes.

Where are the scientific equations and assumptions?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:doc:`Scientific-Documentation` links to the downloadable scientific
manual and its source. Use the manual alongside :doc:`Data-Origins` and
:doc:`Known-Limitations` when interpreting model results.

Inputs and running simulations
--------------------------------

Which file decides what simulation runs?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, ``python main.py`` reads ``input/task_manager_metadata.json``.
Its ``files.tasks.path`` selects a task file, and each simulation task's
``metadata_file_path`` selects the simulation metadata. That metadata
points to the input data and their validation properties. See
:ref:`how-to-change-inputs` and :doc:`Input-Manager`.

Why do I get a file-not-found error?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run commands from the repository root, where ``main.py`` and ``input``
are located. Check the path supplied to ``-p`` and the paths inside your
metadata and task files. Installing the package supplies Python
dependencies; keep the repository's input and output filter files
available when you run a simulation.

How should I organize input files for different scenarios?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use a consistent scenario prefix or suffix for copied task, metadata,
and data files, such as ``my_farm_task.json`` and
``my_farm_metadata.json``. Keep the example files as a baseline and
update every path in the input chain to point to the intended copy.
Give each task a distinct ``output_prefix`` so you can identify its
results. Follow :ref:`how-to-change-inputs`.

Why do repeated runs produce different results?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RuFaS includes stochastic processes. For a reproducible comparison, keep
the code version, dependencies, inputs, and random seed settings fixed.
The example configuration enables ``set_seed`` and the example task uses
``random_seeds: [42]``. A ``SIMULATION_SINGLE_RUN`` task accepts exactly
one seed. See :doc:`Task-Manager` for tasks that run multiple simulations,
and :doc:`Known-Limitations` for interpretation considerations.

What should I do if a simulation uses too much memory?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reduce ``parallel_workers`` in the task file and try a shorter simulation
or smaller herd. See :doc:`Chunkification` for saving output data in
chunks. Chunkification does not remove every memory cost, including
postprocessing. Keep only the output filters you need to limit exported
files; output filters do not by themselves stop variables being collected.

Outputs, filters, reports, and graphs
---------------------------------------

Where are the outputs?
~~~~~~~~~~~~~~~~~~~~~~~~

Check the output directories in your task file. Defaults are
``output/CSVs``, ``output/JSONs``, ``output/reports``, and
``output/graphics`` for CSVs, JSON data, reports, and graphs, respectively.
Logs normally go to ``output/logs``. Data outputs require enabled filters;
running a simulation without them can leave you with logs alone.
Follow :ref:`how-to-select-outputs`. The
`output-filter discussion <https://github.com/RuminantFarmSystems/RuFaS/discussions/2548>`_
also contains examples and community tips; check examples against your
version's :doc:`Output-Manager` reference.

Why are there no CSVs or graphs?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Output files depend on enabled filters. A file named
``_csv_all_variables.txt`` is disabled; copy it to
``csv_all_variables.txt`` to enable it. Check the task's
``filters_directory`` and output directory settings. Graphs also need a
valid ``graph_`` filter and must not be disabled with ``--no-graphics``.
Follow :ref:`how-to-select-outputs` and check the logs for filter errors.

Why is my CSV filter not running?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check its name, format, and location. A simple CSV filter can be a
``csv_*.txt`` file containing one regular expression per line. Structured
CSV filters can also use ``csv_*.json``. Use JSON for graph and report
filters so you can provide their required settings. A leading underscore
disables a filter. Make sure the file is directly in the task's
``filters_directory`` and that its expressions match collected variables.
See :doc:`Output-Manager` for supported formats.

How can I keep old filters without running them?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Move them into an archive subfolder inside your filters directory, or
add a leading underscore to each filename. Filter discovery checks files
directly in the selected directory and does not search its subfolders.
If you later select the archive folder as ``filters_directory``, supported
filter files in that folder will become active.

Why does my graph or report filter fail?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a JSON filter, ``filters`` must be a list of strings, even when you
have only one expression: for example, ``"filters": [".*"]``. A string
such as ``"filters": ".*"`` does not meet that format. Also check the
other required settings and the logs for invalid keys, empty selections,
or generation errors. Follow :doc:`Graph-Generator` or
:doc:`Report-Generator` for complete examples.

How can I report only the last 30 days?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``"slice_start": -30`` to your JSON report filter and leave
``slice_end`` unset. The negative index selects the last 30 stored values
of each selected variable. This corresponds to 30 days for daily data;
for variables reported less often, check their reporting frequency and
the data expansion options before interpreting the slice as days. See
:doc:`Output-Manager` and :doc:`Report-Generator`.

Where can I find errors and warnings?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Logs are normally written under ``output/logs``, although task settings
and ``--logs-dir`` can change their location. Use ``-v warnings`` to
show warnings and errors in the terminal, or ``-v logs`` for more detail.
Check both Task Manager and simulation logs: a task can fail while other
tasks continue. Review validation errors before using the results. See
:doc:`Output-Manager` and :doc:`RuFaS-Command-Line-Arguments`.

Animal module
---------------

Why is my chosen ration formulation not working?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check the selected nutrient standard, the feeds available to the pen,
feed composition, and ration constraints. Review the logs and the
``failed_constraint_summary_for_pen_<pen_id>`` output to identify failed
constraints; include that output in your filters if needed. A failed
formulation can cause the model to reuse a previous ration or reduce
milk production, so check the outcome before interpreting results.
The :doc:`Scientific-Documentation` manual describes the nutrition and
ration methods. Share the relevant configuration and failure messages
on the discussion board if you need help.

Manure module
---------------

How do I represent manure deposited during grazing?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For manure deposited directly on pasture, route the relevant pen manure
stream to a ``DailySpread`` processor. Configure the field's daily spread
application settings as described below. Handle milking-parlor manure
separately according to the farm's actual collection and storage system;
it may need a handler and liquid or slurry storage rather than direct
spreading. This represents the manure pathway; review the scientific
manual for assumptions about the wider grazing scenario.

How do I represent daily spreading from an indoor barn?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set an appropriate handler, such as ``AlleyScraper`` or ``FlushSystem``,
as the pen's first processor and connect its output to ``DailySpread``.
The handler accounts for housing emissions before the manure reaches
the daily spread processor. Update the processor configurations,
connections, and pen inputs together, then configure the field's daily
spread settings. See :doc:`Input-Manager` for the input-file structure.

.. _faq-daily-spread:

Why is daily spread manure not appearing in field outputs?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Daily spread is connected to the crop and soil module in the current
code. Routing manure to ``DailySpread`` alone does not enable a field
application. Check the field's manure schedule for a ``daily_spread``
block with ``is_daily_spreading`` set to ``true``. The supplied
``input/data/manure_schedule/example_daily_spread_manure_schedule.json``
shows the settings.

Choose nutrient targets through ``nitrogen_spread_amount`` and
``phosphorus_spread_amount``, or set ``spread_all_available_manure`` to
``true`` to apply the available daily spread manure. For nutrient-targeted
applications, make sure ``manure_type`` matches the available manure.
Check that manure reaches the processor, that the field uses your intended
schedule, and that the output filter selects field applications. Check
the logs for validation errors and unmet requests.

Why are some manure processor outputs zero?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A processor can have no manure arriving, stored, or emptied on a
particular day. Check the processor connections and emptying schedule
alongside its ``received``, ``accumulated``, and ``emptied`` outputs where
available. Zero values can be expected for an unused processor or a day
without a scheduled transfer; they do not by themselves establish that
the simulation failed.

.. _faq-separators:

How can I represent a different solid-liquid separator?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adjust the separated-solids dry matter and removal efficiencies in the
separator configuration, including those for solids, volatile solids,
nitrogen, phosphorus, and other fractions. Use measured or scientifically
supported values for the equipment and manure you are modelling, and
check the resulting solid and liquid streams.

The separator model performs a split of the manure stream. It does not
simulate gas emissions during prolonged retention in gravity lanes,
settling basins, or weeping walls. Changing efficiencies alone does not
add those processes. See :doc:`Known-Limitations` and
:doc:`Scientific-Documentation` when deciding how to represent them.

How should I choose the surface area of a liquid manure storage?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the farm's measured or engineered dimensions where available. The
`USDA NRCS Animal Waste Management tool <https://www.nrcs.usda.gov/resources/tech-tools/usda-animal-waste-management-version-241>`_
can help with storage sizing when those dimensions are unavailable.
Enter the surface area in square metres and check the scenario's
assumptions. Surface area affects ammonia emissions and the precipitation
received by uncovered outdoor storages, so it should reflect the storage
you intend to model. See :doc:`Scientific-Documentation` for the storage
emission methods.

What is the difference between an anaerobic lagoon and slurry storage?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current anaerobic lagoon model uses a minimum manure temperature of
1 degree Celsius and retains 10 percent of the stored manure at a
scheduled emptying. Outdoor slurry storage uses a minimum temperature of
-20 degrees Celsius and empties its stored manure at a scheduled emptying.
Underfloor slurry storage uses a different temperature model. These
differences affect stored material and emission calculations; compare the
methods in :doc:`Scientific-Documentation` when choosing a processor.

Why does an outdoor storage receive mass when no manure arrives?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Outdoor slurry storages and anaerobic lagoons with no cover or a crust
receive precipitation. That water contributes to the ``received`` volume
and water mass even when no manure stream enters the storage. Check the
weather and cover settings before interpreting these values as manure
transfers.

How do I choose the calendar day when a manure storage empties?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current input is ``storage_time_period``, the number of days between
scheduled emptyings. Periodic emptying is counted from the simulation
start rather than fixed to a calendar date. For field applications on
specific dates, configure the years and Julian days in the field's
manure application schedule and check that the required nutrients are
available. Confirm the actual timing in storage and field outputs;
changing the simulation start date also changes the weather and other
dated management events.

.. _faq-storage-capacity:

What does a manure storage's capacity do?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``capacity`` is the storage's volumetric limit in cubic metres. The
current base storage implementation checks whether stored volume exceeds
it and records an overflow warning. That warning does not automatically
remove or reroute excess manure. Review warnings and storage volume
when assessing a scenario, and choose a capacity appropriate to the
farm. See :doc:`Known-Limitations` for this modelling constraint.

Crop and soil module
----------------------

How can I reuse a management schedule for a subsequent year?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy the existing schedule file, give the copy a distinct name, and
update its years and Julian days for the new period. Check leap years,
planting and harvesting dates, and manure or fertilizer applications.
Update the field metadata paths to point to the new schedule and keep
the original as a baseline. Follow :ref:`how-to-change-inputs` and check
the simulation logs and outputs to confirm the events occurred.

Feed storage module
---------------------

.. _faq-missing-storage:

What happens if harvested crops do not match a feed storage?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Harvested crops are matched using the crop configuration name and the
field name. If no active storage matches, RuFaS logs
``No matching storage for crop`` and treats the crop as exported instead
of adding it to feed inventory. Check each storage's ``crop_name`` and
``field_names`` against the harvested crop and field.

Also check ``rufas_id`` against the available feed list. A storage whose
ID is not in that list produces a warning and is not used for feeding.
It is a separate issue from failing to route the harvested crop to a
storage. See :doc:`Scientific-Documentation` for the feed storage methods.

Can multiple feed storages use the same feed ID?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. Storages can share a ``rufas_id``, and their stored feed totals are
combined for that ID. Each storage needs a unique ``name``. Each
non-null combination of ``crop_name`` and a member of ``field_names``
must also be unique across the active storages so a harvested crop has
an unambiguous destination.

Sources and further help
--------------------------

This page combines the setup guidance with topics from the team's
`RuFaS FAQs and General Tips <https://docs.google.com/document/d/1WK29cGXSVGRcujO9Mj7n7-C22FWpUD9wP44SwqSySS0/edit>`_.
Technical answers have been checked against the code accompanying this
guide. When using a different release, check its documentation and
:doc:`release notes <_release_notes/index>`. Use the discussion board for
scenario questions and :doc:`creating_github_issue` for reproducible bugs.

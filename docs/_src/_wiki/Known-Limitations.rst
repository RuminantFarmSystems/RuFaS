Known Limitations
===================

Use this page to understand the current scope and practical constraints
of RuFaS before configuring a study or interpreting results. For setup
problems, see :doc:`FAQ`; for reported defects and ongoing work, check
the `GitHub issue tracker <https://github.com/RuminantFarmSystems/RuFaS/issues>`_.

Model scope and assumptions
-----------------------------

* **Dairy cattle focus.** RuFaS currently focuses on dairy cattle
  production systems. The broader ruminant-farming vision does not mean
  every species or production system is supported. See the
  `project strategy <https://github.com/RuminantFarmSystems/RuFaS/blob/main/Strategy.md>`_.
* **Scenario-specific inputs.** Supplied example files describe example
  scenarios. Check that herd management, feeds, weather, soils, crops,
  and manure systems represent the farm and period you intend to study.
  Input validation checks configured rules; it does not establish that
  every input is appropriate for your study.
* **Scientific assumptions.** Results depend on the equations and
  assumptions of the selected modules and settings. Review
  :doc:`Scientific-Documentation` and :doc:`Data-Origins` for methods and
  input sources, and assess their applicability to your scenario.
* **Stochastic variation.** A single run is one realization of stochastic
  processes. Preserve the code version, dependencies, inputs, and seed
  settings when comparing scenarios. Use repeated runs where your study
  needs to characterize variation; see :doc:`Task-Manager`.

Module-specific constraints
-----------------------------

* **Separator retention and emissions.** Separator processors split
  manure into solid and liquid streams using configured efficiencies.
  They do not calculate gas emissions during prolonged retention in
  gravity lanes, settling basins, or weeping walls. Changing separator
  efficiencies alone does not represent those additional processes.
  See :ref:`faq-separators`.
* **Manure storage overflow.** The base storage implementation compares
  stored volume with ``capacity`` and logs an overflow warning. It does
  not automatically remove or reroute excess manure when that limit is
  exceeded. Review the warning and storage outputs when interpreting
  results; see :ref:`faq-storage-capacity`.
* **Harvest routing.** A harvested crop without a matching active feed
  storage is treated as exported and generates a warning. A storage's
  feed ID must also be in the available feed list for its inventory to
  be used for feeding. Check the crop, field, and feed mappings; see
  :ref:`faq-missing-storage`.

Runtime and input constraints
-------------------------------

* **Supported Python versions.** The current package requires Python
  3.12 or 3.13. Other versions are outside its declared supported range.
* **Local files and paths.** The example setup uses local metadata,
  input data, and output filter files. Run from the repository root and
  keep the metadata paths connected to the files you intend to use.
  See :doc:`Input-Manager` and :ref:`how-to-change-inputs`.
* **Single-run seeds.** ``SIMULATION_SINGLE_RUN`` requires exactly one
  entry in ``random_seeds``. Use the appropriate multiple-run task type
  instead of adding several seeds to a single-run task.
* **Resource usage.** Large herds, long simulations, and concurrent
  tasks increase memory, processing time, and disk usage. Lower
  ``parallel_workers`` or start with a smaller scenario when resources
  are limited. :doc:`Chunkification` can reduce the output pool held in
  memory during a run, but postprocessing reconstructs saved data and
  still needs memory.
* **Output selection.** CSVs, reports, and graphs require enabled,
  correctly configured filters. A filter can only select variables that
  the simulation produced. Selecting fewer outputs does not eliminate
  all data collection costs. See :doc:`Output-Manager`.

Check the version you use
---------------------------

The published guide, scientific PDF, and your checkout can represent
different revisions. Record the release or commit used for your study
and check its :doc:`release notes <_release_notes/index>`. The scientific
PDF is a compiled snapshot; check the scientific source for changes made
since it was built.

To report an unsupported case or unexpected result, follow
:doc:`creating_github_issue` and include the version, relevant inputs,
logs, and a small example that reproduces the problem. Avoid posting
private farm data; share an anonymized example when needed.

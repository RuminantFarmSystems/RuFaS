End to End Testing
==================

What
~~~~

   | "End-to-end or (E2E) testing is a form of testing used to assert
     your entire application works as expected from start to finish or
     'end-to-end'."
   | — `Angular Docs <https://angular.dev/tools/cli/end-to-end>`__

In RuFaS end-to-end testing, we have a specific set of output values
saved which we expect to see from the model. When running end-to-end
testing, outputs from the model are collected and compared to these
saved values. If the values match, then end-to-end testing passes,
otherwise it fails.

Key Terms
^^^^^^^^^

- **Domain** - a module or section of the RUFAS model. Examples: Animal,
  Feed Storage, Crop & Soil.

- **Expected Results** - the set of results for a particular domain that
  should match your actual results when you run an end-to-end test on
  that domain. These are stored in the Filter File.

- **Actual Results** - the set of results generated from an end-to-end
  testing run. An Actual Results file is generated for each domain each
  time you run end-to-end testing.

- **Filter File** - a file containing the filters that were used to
  collect the expected AND actual results for a particular domain. This
  file contains:

  - The domain name
  - The filters used to collect expected and actual results
  - The set of expected results from those filters
  - The date of the last time these expected results were updated

- **Results File** - a file containing the outcome of running end-to-end
  testing on a particular domain. This file contains:

  - The outcome of the test (passing or failing)
  - Any differences found between the actual and expected results
  - A results file is generated for each domain each time you run
    end-to-end testing

- **Must-Change Variables** - variables that are expected to differ from
  the expected results, for example after an intended change to the
  model. See :ref:`Must-Change Variables <e2e-must-change-variables>`.

- **Accepted Ranges** - a minimum and a maximum for a variable. A
  variable with an accepted range is checked against that range and not
  against the expected results. See
  :ref:`Accepted Ranges <e2e-accepted-ranges>`.

Why
~~~

E2E testing will help prevent RuFaS outputs from changing in drastic or
unexpected ways as changes are made to the code.

How
~~~

As of **08/08/2025**, E2E testing can only be run with dedicated sets
of inputs. Run E2E testing with the following command:

.. code:: sh

   python main.py -p input/metadata/end_to_end_testing_tm_metadata.json

There are three sets of inputs set up:

1. Free Stall Dairy
    i. E2E testing is performed on the Crop&Soil, the Animal, and the Manure domain (module) of RuFaS.
    ii. The simulation time period for the Free Stall E2E is cut short to only one year.

2. Open Lot
    i. E2E testing is performed on the Crop&Soil, the Animal, and the Manure domain (module) of RuFaS.
    ii. The simulation time period for the Open Lot E2E is cut short to only one year.

3. No Animals
    i. No animals are simulated in this simulation. It is mainly used to verify the stand-alone C&S domain results.
    ii. E2E testing is performed on the Crop&Soil and the Manure domain (module) of RuFaS.


For Each E2E test run:

- **A domain’s E2E test passes if there are no differences between the
  expected and actual results.**

- **A domain’s E2E test fails if there are any differences.**

- **Variables in the must-change list or with an accepted range are
  checked differently.** See
  :ref:`Must-Change Variables and Accepted Ranges <e2e-must-change-and-accepted-ranges>`.

- **If an E2E test passes, the result is logged normally. If it fails,
  the result is logged as an error.**

Output File Details
^^^^^^^^^^^^^^^^^^^

For each domain, an output file will be generated with the E2E results.
The file name includes the domain name and is labeled with a timestamp.

**Example:**

``end-to-end-testing_saved_variables_feed_storage_e2e_results_16-Oct-2024_Wed_17-21-06.json``

This output file contains:

- All differences between the actual and expected results.
- A key that points to a boolean value indicating whether the E2E test
  passed or not.
- ``changed_variables``: the names of the variables that differ from the
  expected results. Variables in the must-change list or with an
  accepted range are not included.
- ``must_change_satisfied`` and ``must_change_violations``, if the
  domain has must-change variables.
- ``accepted_range_satisfied`` and ``accepted_range_violations``, if the
  domain has variables with an accepted range.

.. _e2e-must-change-and-accepted-ranges:

Must-Change Variables and Accepted Ranges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, every variable is compared against its expected value. This
is the normal comparison. Each input set can have two optional files
that change how a variable is checked:

- The **must-change variables** file lists the variables that are
  expected to change.
- The **accepted ranges** file gives variables a minimum and a maximum.

Both files are in the folder of their input set in
``input/data/end_to_end_testing``. For example, the Free Stall files
are:

- ``input/data/end_to_end_testing/freestall/freestall_must_change_variables.json``
- ``input/data/end_to_end_testing/freestall/freestall_accepted_ranges.json``

Each file covers all the domains of its input set. The variable names
are the keys of the ``expected_results`` in the E2E JSON filter files,
for example
``AnimalModuleReporter.report_305_day_milk_yield.milk_305_day_yield_herd_mean``.

RuFaS finds the two files through the ``must_change_variables_path`` and
``accepted_ranges_path`` keys in ``end_to_end_testing_result_paths.json``.
See :ref:`E2E Testing Results Paths File <e2e-testing-results-paths-file>`.

.. _e2e-must-change-variables:

Must-Change Variables
^^^^^^^^^^^^^^^^^^^^^

Use this file when a change to the code is expected to change certain
outputs. A listed variable passes only if its actual value differs from
the expected value by more than the tolerance of its domain. If the
value still matches, the domain fails.

.. code:: json

   {
       "description": "Names of variables that must differ from the expected results. Empty this list after updating the expected results.",
       "must_change_variables": [
           "AnimalModuleReporter.report_enteric_methane_emission.enteric_methane_emission_for_LAC_COW_PEN_3",
           "AnimalModuleReporter.report_manure_excretions.LAC_COW_PEN_3_manure_mass"
       ]
   }

How to use it:

1. Run E2E testing. The results file of each domain lists the variables
   that differ from the expected results under ``changed_variables``.
2. Review that list and add the variables that are expected to change to
   ``must_change_variables``.
3. Run E2E testing again. The listed variables now pass because they
   changed, and they are no longer reported as differences.
4. After the expected results are updated, empty the list. RuFaS does
   not empty it for you. A variable that stays in the list fails the
   next run, because it no longer differs from the new expected results.

In the results file, ``must_change_satisfied`` lists the variables that
changed, and ``must_change_violations`` gives the reason for each
variable that failed:

.. code:: json

   {
       "Animal.must_change_satisfied": {
           "values": [
               [
                   "AnimalModuleReporter.report_manure_excretions.LAC_COW_PEN_3_manure_mass"
               ]
           ]
       },
       "Animal.must_change_violations": {
           "values": [
               {
                   "AnimalModuleReporter.report_305_day_milk_yield.milk_305_day_yield_l1_mean": "Flagged as must change but the value still matches the expected results within the tolerance."
               }
           ]
       }
   }

.. _e2e-accepted-ranges:

Accepted Ranges
^^^^^^^^^^^^^^^

Use this file when a variable should be judged by a known range, for
example a range accepted in the literature, and not by its previous
value. A variable with an accepted range passes if all of its values are
inside the range. It does not matter whether the values changed from the
expected results.

.. code:: json

   {
       "description": "Accepted 'min' and 'max' for each variable name. All values of a listed variable must fall within them.",
       "accepted_ranges": {
           "AnimalModuleReporter.report_305_day_milk_yield.milk_305_day_yield_herd_mean": {
               "min": 10000,
               "max": 13000
           }
       }
   }

- ``min`` and ``max`` are both required. They must be numbers, and
  ``min`` cannot be greater than ``max``.
- The bounds are inclusive.
- Every number recorded for the variable is checked. For a daily
  variable, this is the value of every day. For a variable that records
  several fields, every numerical field is checked against the same
  range.

Accepted ranges are turned on or off for each task with
``use_accepted_ranges`` in
``input/data/tasks/end_to_end_testing_task.json``. The default is
``true``. When it is ``false``, the accepted ranges file is not read.

In the results file, ``accepted_range_satisfied`` and
``accepted_range_violations`` show each range with the smallest and
largest value that was found. A violation also gives the reason:

.. code:: json

   {
       "Animal.accepted_range_violations": {
           "values": [
               {
                   "AnimalModuleReporter.report_manure_excretions.LAC_COW_PEN_3_urine": {
                       "min": 0,
                       "max": 1500,
                       "observed_min": 1244.110055144196,
                       "observed_max": 1748.8818365567322,
                       "reason": "191 of 366 values fall outside the accepted range."
                   }
               }
           ]
       }
   }

.. _e2e-check-interactions:

How the Checks Work Together
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A variable can be in neither file, in one of them, or in both. The table
below shows the checks a variable gets in each case, as of
**11/22/2026**.

+-----------------------+-----------------------------+--------------------------------------------+
| Variable is in        | Checks it gets              | Passes when                                |
+=======================+=============================+============================================+
| Neither file          | Normal comparison           | It matches the expected value within the   |
|                       |                             | tolerance.                                 |
+-----------------------+-----------------------------+--------------------------------------------+
| Must-change file only | Must-change check           | It differs from the expected value by more |
|                       |                             | than the tolerance.                        |
+-----------------------+-----------------------------+--------------------------------------------+
| Accepted ranges file  | Range check                 | Every value is inside the range. A change  |
| only                  |                             | from the expected value does not matter.   |
+-----------------------+-----------------------------+--------------------------------------------+
| Both files            | Must-change check and range | It differs from the expected value by more |
|                       | check                       | than the tolerance, and every value is     |
|                       |                             | inside the range.                          |
+-----------------------+-----------------------------+--------------------------------------------+

For a variable in both files, both checks must pass:

+----------------+-------------------+--------+
| Value changed? | Inside the range? | Result |
+================+===================+========+
| Yes            | Yes               | Pass   |
+----------------+-------------------+--------+
| No             | Yes               | Fail   |
+----------------+-------------------+--------+
| Yes            | No                | Fail   |
+----------------+-------------------+--------+
| No             | No                | Fail   |
+----------------+-------------------+--------+

Things to keep in mind:

- The tolerance is the ``tolerance`` of the domain in
  ``end_to_end_testing_result_paths.json``.
- A variable in either file is left out of the normal comparison.
- If ``use_accepted_ranges`` is ``false``, the ranges are ignored. A
  variable with a range then gets the normal comparison, or only the
  must-change check if it is also in the must-change file.
- A domain passes only if all of its variables pass.
- A listed variable that is missing from the actual results fails.
- A variable with an accepted range that has no numbers to check fails.
- A name that is not in the expected results of any domain of the input
  set is a configuration error. So is a file that cannot be found or
  read, and a range without a valid ``min`` and ``max``. RuFaS logs the
  error and does not compare any domain of that input set. This is
  checked after the simulation has run.

Setting up E2E Testing
~~~~~~~~~~~~~~~~~~~~~~

Quick Setup
^^^^^^^^^^^

**Note**: E2E Testing is already ready to running on multiple domains for three sets of inputs.
This section is for creating testing for a new sets of inputs,
or setting up testing for an uncovered domain in an exisiting set of inputs.

New Input Set Setup
-------------------

In the ``input/data/end_to_end_testing`` directory:

1. **Create a folder** with its name being the name for the new input set.

2. Go into the folder, and **create the 2 necessary E2E filter files** following these formats:
   - **E2E JSON Filter File**

     - File name format: ``e2e_json_{domain}_filter.json``.
     - See :ref:`E2E JSON filter file <e2e-json-filter-file>`.
       for reference.
     - **Note:** You won't have anything to put in the
       ``expected_results`` section at setup time. This is expected.
       Keep following the steps.

   - **E2E Comparison Filter**

     - File name format: ``e2e_comparison_{domain}_differences.json``.
     - See :ref:`E2E Comparison filter file <e2e-comparison-filter-file>` for reference.

   - **Must-Change Variables and Accepted Ranges Files (optional)**

     - File name formats: ``{input set}_must_change_variables.json`` and
       ``{input set}_accepted_ranges.json``. Keep these endings. RuFaS
       uses them to tell these files apart from the filter files.
     - Copy the two files from an existing input set. They start empty.
     - See :ref:`Must-Change Variables and Accepted Ranges <e2e-must-change-and-accepted-ranges>`
       for reference.

3. **Update the ``end_to_end_testing_task.json`` file** in the ``input/data/tasks`` directory:
   - **Use the existing entries as examples.**, create a new object in the ``"tasks"`` array, specifying:
     - "task_type": "END_TO_END_TESTING"
     - "metadata_file_path": the file path to the new input set metadata.
     - "output_prefix": a custom output prefix for the new set of inputs,
       preferably following the patter ``{custom_name}_e2e``.
       **Please NOTE DOWN this output prefix name, it will be referenced later.**
     - "filters_directory": the directory path to the new directory conataining the two newly created filters.
     - "use_accepted_ranges": true to check variables against the accepted ranges file, false to ignore that file.
     - "log_verbosity": the desired verbosity, the suggested verbosity is "logs" for an E2E testing run.
     - "exclude_info_maps": true. Please set this flag to true to exclude the info maps in the outputs,
       so that we can decrease the output file size and speed up the comparison process.
     - "random_seed": the choice of random seed, default is set to 42.

4. **Update the ``update_end_to_end_testing_expected_results.json`` file** in the ``input/data/tasks`` directory:
   - **Use the existing entries as examples.**, create a new object in the ``"tasks"`` array, specifying:
     - "task_type": "UPDATE_E2E_TEST_RESULTS"
     - "metadata_file_path": the file path to the new input set metadata.
     - "output_prefix": the same output prefix from ``end_to_end_testing_task.json``.
     - "filters_directory": the directory path to the new directory conataining the two newly created filters.
     - "log_verbosity": the desired verbosity, the suggested verbosity is "logs" for a update E2E results run.
     - "exclude_info_maps": true. Please set this flag to true to exclude the info maps in the outputs,
       so that we can decrease the output file size and speed up the comparison process.
     - "random_seed": the choice of random seed, default is set to 42.

5. **Update the ``end_to_end_testing_results_paths.json`` file** in the ``input/data/end_to_end_testing`` directory:

   - Create a new key-value pair in the "end_to_end_test_result_paths" dictionary.
     The key should be the output prefix specified in step 3 and 4.
   - Specify the domains you’re testing, the path to the expected
     outputs, and the pattern used to find the actual outputs for the
     domain module.
   - If you created the must-change variables and accepted ranges files
     in step 2, add their paths with the ``must_change_variables_path``
     and ``accepted_ranges_path`` keys.
   - **Use the existing entries as examples.**
   - See :ref:`E2E Testing Results Paths File <e2e-testing-results-paths-file>` for reference.
   - **Note:** *You will not create a new results paths file. Add your
     new domain's paths to the existing file.*

6. **Update the ``default.json`` file** in the ``input/data/metadata/properties`` directory:

   - Navigate to the **"end_to_end_test_result_paths"** block under the
     **end_to_end_test_result_path_properties"** section.
   - Create a new entry in the "end_to_end_test_result_paths" dictionary by copying and pasting one of the existing
     input set, with the key being the output prefix specified in step 3 and 4.
     For example, copy the entire "freestall_e2e" dictionary, paste it as a new entry, and change the key to the output
     prefix.

7. **Run the following command:**

   .. code:: sh

      python main.py -p input/metadata/update_end_to_end_testing_tm_metadata.json -c

   - This runs a simulation and updates the existing expected results
     with the new actual results for each domain.

   - If differences are found between the existing expected results and
     the new actual results, this will be logged for reference.

   - Monitor the logs for updates. If any unexpected domains show
     differences, STOP and investigate by comparing the expected and
     actual results.

   - Open each updated filter file and remove the automatically added
     top line to ensure there is human-in-the-loop (HIL) validation.

   - Contact a member of the dev team if you have questions or need
     assistance.

8. Run the E2E testing command:

.. code:: sh

   python main.py -p input/metadata/end_to_end_testing_tm_metadata.json

9. Confirm your domain E2E test passes. If the test doesn't pass, review
   steps 1–4 or contact a member of the RuFaS maintainer team for help.

New Domain Setup
-------------------

1. Navigate to the corresponding folder for the input set you want to update in ``input/data/end_to_end_testing``
   directory.**Create the 2 necessary E2E filter files** for the new domain by following step 2 from the
   **New Input Set Setup** section.

2. **Update the ``end_to_end_testing_results_paths.json`` file** in the ``input/data/end_to_end_testing`` directory:

   - Navigate to the dictionary about the input set you want to update in the "end_to_end_test_result_paths" dictionary.
   - **Use the existing entries as examples** to add the filter files of the new domain.

3. Follow steps 7-9 from the **New Input Set Setup** section to update the expected E2E results and confirm all E2E
   tests are successful.

--------------

Automatically Updating E2E Results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As noted in step 3 of the Quick Setup instructions, you can run this
command
``python main.py -p input/metadata/update_end_to_end_testing_tm_metadata.json -c``
to automatically update end-to-end-testing "expected results" for all
domains of all input sets. These expected results are the results against which end-to-end
testing will be run.

This is a powerful tool which removes some of the steps in updating the
expected results by hand. However, there are still some safeguards
against total automation to ensure expected results aren't being
unknowingly updated when this is run.

How does it work?

1. For each input set, a simulation is run and output is filtered based on the filters in
   the existing E2E testing filters files.
2. For each domain, the filtered results generated from that simulation
   are checked against the existing expected results for that domain.
3. If any differences are found, it will automatically update the
   expected results in the appropriate filter file to reflect the actual
   results from the simulation that was just run. It will also update
   the ``expected_results_last_updated`` date in that filter file to
   reflect when the update occurred.
4. Any updated filter file will also have this line of text printed
   across the top
   ``// WARNING: This is an autogenerated file. Remove this line for valid JSON.``.
   This will cause the filter file to be invalid until a human user goes
   in, checks that the file looks correct, and removes this line. It is
   a safeguard against accidental updates to these files.

It is always good practice after running this automatic update to re-run
end-to-end testing to ensure that the results were properly updated.

The update does not read or change the must-change variables and
accepted ranges files. If the must-change list of an input set is not
empty, empty it before you re-run end-to-end testing. See
:ref:`Must-Change Variables <e2e-must-change-variables>`.

--------------

More Detailed Setup Explanation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When E2E testing runs, special filter files are needed to properly
collect the actual and expected results. These filters are very similar
to regular RuFaS filters, but are prefixed with ``e2e_`` (see the full
list of supported E2E filter prefixes
`here <https://github.com/RuminantFarmSystems/MASM/blob/dev/RUFAS/output_manager.py#L142>`__).

There are only two supported filter types currently:

1. JSON (``e2e_json_``)
2. Comparison (``e2e_comparison_``)

The E2E JSON filters are almost identical to regular JSON filters, with
one major difference:. E2E JSON filters contain a key called
"expected_results", which points to the results that are expected to be
collected from RuFaS with the patterns pointed to by the "filters" key.

The comparison filter files are regular JSON filter files that only
contain one pattern, used to collect the differences between the actual
and expected results for a single domain.

These filter file types were introduced because JSON filter files should
*only* be used in the first post-processing that RuFaS executes, and
comparison files *only* in the second post-processing.

In order for the actual and expected results to be connected, RuFaS uses
the file
``input/data/end_to_end_testing/end_to_end_testing_result_paths.json``.
This file should contain:

- a dictionay of a list of objects, each item in the dictionary represents an input set , and each object whitn the
   list contains the name of the RuFaS domain being tested.
- the path to the expected results (which is the path to the filter file
  for that domain located within the ``end_to_end_testing`` directory).
- a pattern used to identify the actual results.

Two important points:

1. The file containing the actual results is produced as RuFaS filters
   with the patterns listed in the expected results file, so it is
   critical that the "name" field of that file matches what is in the
   actual results path.
2. The filter in the comparison file must match the domain that is
   listed in the ``end_to_end_testing_result_paths.json`` file,
   otherwise the comparison file will not be able to correctly filter
   out the results of E2E testing.

Example Files
~~~~~~~~~~~~~

Example files are provided to illustrate the description of how E2E
filter files are structured.

.. _e2e-json-filter-file:

E2E JSON filter file.
^^^^^^^^^^^^^^^^^^^^^

This is the filter file for testing the Feed Storage module
(``e2e_json_feed_storage_filter.json``), which contains both filters and
expected results:

.. code:: json

   {
       "name": "e2e_feed_storage",
       "filters": [
           "Weather.*",
           "Time.*",
           "ProtectedIndoors.*",
           "ProtectedWrapped.*",
           "ProtectedTarped.*",
           "Unprotected.*",
           "Baleage.*",
           "Dry.*",
           "HighMoisture.*",
           "Bunker.*",
           "Pile.*",
           "Bag.*"
       ],
       "expected_results": {
           "DISCLAIMER": "Under construction, use the results with caution.",
           "Weather.average_annual_temperature": {
               "info_maps": [
               {
                   "prefix": "Weather",
                   "units": "\u00b0C"
               }
               ],
               "values": [
               8.178051643192488
               ]
           },
           ...
       }
   }

Like a regular filter file, it has both a "name" and "filters" entry
which RuFaS uses to filter the OutputManager's pool. But unlike regular
filter files, there is a key called "expected_results", which contains
all the data that is expected to be collected with the filters listed in
this file.

.. _e2e-comparison-filter-file:

E2E Comparison filter file.
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the filter file for collecting the E2E test results for Feed
Storage, ``e2e_comparison_feed_storage_differences.json``.

.. code:: json

   {
       "name": "feed_storage_e2e_results",
       "filters": ["FeedStorage.*"]
   }

Because the file name of this filter is prefixed with
"e2e_comparison\_", this filter file will only be after RuFaS has
finished comparing the actual and expected results from the filter file
listed above.

.. _e2e-testing-results-paths-file:

E2E Testing Results Paths File.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The results filter and the comparison filters have to be linked so that
RuFaS is able to find the correct files for the actual and expected
results, and record their differences so that they can be collected
properly. This is accomplished in the
``end_to_end_testing_result_paths.json``.

.. code:: json

   {
       "end_to_end_test_result_paths": {
        "freestall_e2e": [
               {
                   "domain": "FeedStorage",
                   "expected_results_path": "input/data/end_to_end_testing/e2e_json_feed_storage_filter.json",
                   "actual_results_path": "end-to-end-testing_saved_variables_e2e_feed_storage_",
                   "tolerance": 0.1,
                   "must_change_variables_path": "input/data/end_to_end_testing/freestall/freestall_must_change_variables.json",
                   "accepted_ranges_path": "input/data/end_to_end_testing/freestall/freestall_accepted_ranges.json"
               }
           ]
        }
   }

The "expected_results_path" points to the filter file which contains the
expected results, and the "actual_results_path" entry contains the
pattern that will start the file produced by the filter file containing
the expected results. The "tolerance" is the percent tolerance allowed
between the expected and actual results. It can be set individually for
each domain to be more or less lenient.

The "must_change_variables_path" and "accepted_ranges_path" entries are
optional. They point to the must-change variables file and the accepted
ranges file of the input set. All the domains of an input set point to
the same two files. See
:ref:`Must-Change Variables and Accepted Ranges <e2e-must-change-and-accepted-ranges>`.

Some important things to note in the "actual_results_path":

- It starts with "end-to-end-testing", this must match the output prefix
  of the task that is running E2E testing.
- It ends with "e2e_feed_storage", this must match the "name" key in the
  filter file which contains the expected results.
- The pattern is not a full file name, it is only the beginning. The
  full file name with the actual results will contain a timestamp, but
  this is not known when this entry is written so the pattern can only
  match the start of the file. It is important that the results from the
  last E2E test run are cleared before re-running E2E testing, otherwise
  it is not ensured that RuFaS will find the actual results from the
  last E2E test run.

It is also critical that the "domain" entry matches the pattern in the
Feed Storage comparison file. RuFaS uses the domain entry as the prefix
when it records E2E test results as variables to the Output Manager, so
if the pattern does not match the domain name then the results for the
E2E test will not be collected properly by the comparison file.

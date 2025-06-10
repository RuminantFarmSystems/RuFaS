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

Why
~~~

E2E testing will help prevent RuFaS outputs from changing in drastic or
unexpected ways as changes are made to the code.

How
~~~

As of **02/01/2025**, E2E testing can only be run with a dedicated set
of inputs. Run E2E testing with the following command:

.. code:: sh

   python main.py -p input/metadata/end_to_end_testing_tm_metadata.json

E2E testing checks each domain (module) of RuFaS separately—for example,
Feed Storage, Animal, Manure, etc. Each check generates a result
(passing or failing), which is both written to an output file and
logged.

- **A domain’s E2E test passes if there are no differences between the
  expected and actual results.**

- **A domain’s E2E test fails if there are any differences.**

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

Setting up E2E Testing
~~~~~~~~~~~~~~~~~~~~~~

Quick Setup
^^^^^^^^^^^

**Note**: E2E Testing is already ready to running for multiple domains.
This section is for setting up new testing for parts of the model that
aren't yet covered.

In the ``input/data/end_to_end_testing`` directory:

1. **Create the 2 necessary E2E filter files** following these formats:

   - **E2E JSON Filter File**

     - File name format: ``e2e_json_{domain}_filter.json``.
     - See `E2E JSON filter example
       file <https://github.com/RuminantFarmSystems/MASM/wiki/End%E2%80%90to%E2%80%90End-Testing/#e2e-json-filter-file>`__
       for reference.
     - **Note:** You won't have anything to put in the
       ``expected_results`` section at setup time. This is expected.
       Keep following the steps.

   - **E2E Comparison Filter**

     - File name format: ``e2e_comparison_{domain}_differences.json``.
     - See `E2E Comparison filter example
       file <https://github.com/RuminantFarmSystems/MASM/wiki/End%E2%80%90to%E2%80%90End-Testing/#e2e-comparison-filter-file>`__
       for reference.

2. **Update the ``end_to_end_testing_results_paths.json`` file** in the
   same directory:

   - Specify the domain you’re testing, the path to the expected
     outputs, and the pattern used to find the actual outputs for the
     domain module.
   - **Use the existing entries as examples.**
   - See `E2E Results Paths example
     file <https://github.com/RuminantFarmSystems/MASM/wiki/End%E2%80%90to%E2%80%90End-Testing/#e2e-testing-results-paths-file>`__
     for reference.
   - **Note:** *You will not create a new results paths file. Add your
     new domain's paths to the existing file.*

3. **Run the following command:**

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

4. Run the E2E testing command:

.. code:: sh

   python main.py -p input/metadata/end_to_end_testing_tm_metadata.json

5. Confirm your domain E2E test passes. If the test doesn't pass, review
   steps 1–4 or contact a member of the dev team for help.

--------------

Automatically Updating E2E Results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As noted in step 3 of the Quick Setup instructions, you can run this
command
``python main.py -p input/metadata/update_end_to_end_testing_tm_metadata.json -c``
to automatically update end-to-end-testing "expected results" for all
domains. These expected results are the results against which end-to-end
testing will be run.

This is a powerful tool which removes some of the steps in updating the
expected results by hand. However, there are still some safeguards
against total automation to ensure expected results aren't being
unknowingly updated when this is run.

How does it work?

1. A simulation is run and output is filtered based on the filters in
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

- a list of objects, each of which contains the name of the RuFaS domain
  being tested.
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
       "end_to_end_test_result_paths": [
           {
               "domain": "FeedStorage",
               "expected_results_path": "input/data/end_to_end_testing/e2e_json_feed_storage_filter.json",
               "actual_results_path": "end-to-end-testing_saved_variables_e2e_feed_storage_",
               "tolerance": 0.1
           }
       ]
   }

The "expected_results_path" points to the filter file which contains the
expected results, and the "actual_results_path" entry contains the
pattern that will start the file produced by the filter file containing
the expected results. The "tolerance" is the percent tolerance allowed
between the expected and actual results. It can be set individually for
each domain to be more or less lenient.

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

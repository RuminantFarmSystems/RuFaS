Output Manager
==============

Overview
--------

As its name suggests, it is in charge of managing the output. Output
Manager collects variables, warnings, logs, and errors during the
simulation (and other processes) and, as accurately as possible,
documents the source and point in the code from which the data was
generated. This will give developers and users more information about
their model simulations as well as provide some flexibility for other
uses down the road.

Output Manager works by collecting variables, logs, warnings, and errors
into separate pools, and populates requested output channels from the
pools once the simulation is done. This is done using *filter files*. If
a filter file's name begins with either ``json_`` or ``csv_``, Output
Manager handles them itself. However, filter files whose names begin
with ``report_`` and ``graph_`` are handled by the :doc:`Report Generator <Report-Generator>`
and the :doc:`Graph Generator <Graph-Generator>`
respectively.

Output Manager is a singleton, i.e., only one instance of it can exist
(per application/memory segment). After the first instance is created,
future calls to the constructor method return the first instance. Also,
the initializer method only works once.

Quick Start
-----------

To set up Output Manager to capture data from a RuFaS simulation:

1. See :ref:`Add the data you need to the Output Manager variables pool <add-label>` for details.
2. Set up an output filter file to capture your data:

- Create a .txt file in the output_filters folder
  (MASM/output/output_filters).
- The name of the file should start with either ``json`` or ``csv``
  depending on which format you desire. Be specific with your naming
  (e.g. ``json_cow_lactation.txt``).
- Add the text pattern(s) for the variables you want to capture. Output
  Manager uses RegEx pattern matching so for example if you want to
  capture all variables relating to the ``Cow`` class, you would enter
  ``^Cow.*`` into the filter .txt file you created.
- To capture all variables, you would enter ``.*``. For more details on
  how to write RegEx patterns to help capture the specific data you
  need, `see the pattern matching
  section. <https://github.com/RuminantFarmSystems/MASM/wiki/Output-Manager#here-are-some-base-example-patterns-that-can-be-used-as-templates-for-making-your-own-filter-pattern-file>`__

3. Run a simulation!

Chunkification
--------------

Using chunkification, users can periodically dump the current variable
pool and save a chunk into a JSON file. This will allow us to break down
a larger simulation pool into smaller chunks. There are three main
settings users can set in their task manager task to control how they
would like to employ chunkification:

1. ``save_chunk_threshold_call_count``: If this variable is specified,
   the OM will keep track of the number of calls to the
   OM.add_variable() function. Once it reaches the threshold number, the
   current variable pool will be dumped, and the other metrics will be
   ignored.
2. ``maximum_memory_usage``: If ``save_chunk_threshold_call_count`` is
   not specified but this variable is, the OM will set OM.max_pool_size
   to the specified maximum_memory_usage amount.
3. ``maximum_memory_usage_percent``: If neither
   save_chunk_threshold_call_count nor maximum_memory_usage is
   specified, we will use maximum_memory_usage_percent to determine the
   maximum memory usage by simply multiplying it with the available
   memory.

For a more detailed look at chunkification, some example setups, and a
diagram of how chunkification works, please see the :doc:`Chunkification wiki page. <Chunkification>`

Output Filters
--------------

Data collected by OutputManager can be filtered and handled by three
main post-processing functions:

1. It can be aggregated by :doc:`Report Generator <Report-Generator>`.
2. It can be graphed in :doc:`Graph Generator <Graph-Generator>`.
3. It can be filtered to a csv or json file right within OutputManager.

To route filtered data to any of these post-processors, you need to
create a filter file in ``.json`` format.

- To graph your data, the filter file should start with ``graph_``.
- To aggregate your data, the filter file name should start with
  ``report_``.
- To simply filter the data to a .csv or .json file, the filter file
  name should start with ``csv_`` or ``json_`` respectively.

Typically naming the file after the data it is collecting is the best
practice (e.g. ``report_average_milk_production.json``).

Within that filter file there are a number of options to specify what
data you want and how you want it presented. Here is a list of filter
options for GraphGenerator and ReportGenerator. More details are
available in their respective Wiki pages.

**Note: for filtering data using Output Manager, the only filter entries
that have any effect are ``"name"``, ``"filters"``, ``"variables"``, and
``"filter_by_exclusion"``.**

+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| Output Filter Entry       | Data Type                                                                  | Default            | Graph Generator            | Report Generator                                                                            | Example Entry                                                               | Required?        |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             | (RG/GG/BOTH)     |
+===========================+============================================================================+====================+============================+=============================================================================================+=============================================================================+==================+
| name                      | str                                                                        | N/A                | N/A                        | The name of the report to appear in the column header of report CSV.                        | ``"Average Herd Milk Fat"``                                                 | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| title                     | str                                                                        | N/A                | The title of the graph.    | N/A                                                                                         | "Gallons Milk Per Cow"                                                      | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| type                      | str                                                                        | N/A                | The type of graph you want | N/A                                                                                         | "stackplot"                                                                 | GG               |
|                           |                                                                            |                    | plotted.                   |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| filters                   | list[str]                                                                  | N/A                | RegEx pattern that defines | RegEx pattern that defines what vars will be in a report.                                   | ``[".*homegrown_feed_emissions.homegrown_corn_grain_emissions.*"]``         | GG, RG (if       |
|                           |                                                                            |                    | what vars will be plotted  |                                                                                             |                                                                             | cross_references |
|                           |                                                                            |                    | on a single graph.         |                                                                                             |                                                                             | is not provided) |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| variables                 | list[str]                                                                  | N/A                | List of keys to be plotted | List of keys to be included in the report when the data from the filters pattern is stored  | ``["nitrous_oxide_emissions", "ammonia_emissions", "carbon_stock_change"]`` | BOTH (when data  |
|                           |                                                                            |                    | when data from the filters | in a dictionary.                                                                            |                                                                             | in dictionary)   |
|                           |                                                                            |                    | pattern is stored in a     |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | dictionary.                |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| filter_by_exclusion       | bool                                                                       | false              | A partner field to the     | Similar to how it functions in GG, this specifies whether to include or exclude variables   | ``true``                                                                    | No               |
|                           |                                                                            |                    | variables field. This      | from the resulting CSV output.                                                              |                                                                             |                  |
|                           |                                                                            |                    | boolean allows the user to |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | specify if they want to    |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | plot everything in the     |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | variables field or exclude |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | what's in the field.       |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| use_name                  | bool                                                                       | false              | Whether to use the filter  | Whether to use the filter name when constructing the key name for data pulled from a        | ``true``                                                                    | No               |
|                           |                                                                            |                    | name when constructing the | dictionary.                                                                                 |                                                                             |                  |
|                           |                                                                            |                    | key name for data pulled   |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | from a dictionary.         |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| customization_details     | See :doc:`GG Wiki <Graph-Generator>`                                       | N/A                | Customization options such | N/A                                                                                         |                                                                             | No               |
|                           |                                                                            |                    | as legends, titles, and    |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | more.                      |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| legend                    | list[str]                                                                  | N/A                | Legend is customizable. If | N/A                                                                                         | ``["var1", "var2", "var3"]``                                                | No               |
|                           |                                                                            |                    | left blank, the Graph      |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | Generator auto-generates a |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | legend based on the keys   |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | of the data prepared to be |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | plotted.                   |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| use_calendar_dates        | bool                                                                       | false              | If true use dates/time as  | N/A                                                                                         | ``true``                                                                    | No               |
|                           |                                                                            |                    | measurement on graph's     |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | x-axis                     |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| date_format               | string                                                                     | ``day_month_year`` | Specifies format of        | N/A                                                                                         | ``day_of_year``                                                             | No               |
|                           |                                                                            |                    | date/time along x-axis of  |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | graph                      |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| display_units             | bool                                                                       | true               | Units measured during the  | If true, units for aggregated report data will appear in the report title.                  | ``false``                                                                   | No               |
|                           |                                                                            |                    | simulation are             |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | automatically displayed in |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | the graph legend.          |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| omit_legend_prefix/suffix | bool                                                                       | false              | Allows removal of the      | N/A                                                                                         | ``true``                                                                    | No               |
|                           |                                                                            |                    | prefix or suffix from a    |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | variable for display in    |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | the graph legend. Set      |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | "omit_legend_prefix": true |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | or "omit_legend_suffix":   |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | true.                      |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| expand_data               | bool                                                                       | false              | Graph filters support data | Boolean flag to determine if data expansion should be attempted. Other options include      | ``true``                                                                    | No               |
|                           |                                                                            |                    | expansion options:         | "fill_value", "use_fill_value_in_gaps", and "use_fill_value_at_end".                        |                                                                             |                  |
|                           |                                                                            |                    | "expand_data",             |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | "fill_value",              |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | "use_fill_value_in_gaps",  |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | and                        |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | "use_fill_value_at_end".   |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | Additionally supports      |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | "mask_values" to remove    |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | NaNs.                      |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| fill_value                | float                                                                      | ``np.nan``         | Value that is used to pad  | Value that is used to pad the front of the data values, and optionally the values in        | ``0.0``                                                                     | No               |
|                           |                                                                            |                    | the front of the data      | between original values and after the last original value.                                  |                                                                             |                  |
|                           |                                                                            |                    | values, and optionally the |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | values in between original |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | values and after the last  |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | original value.            |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| use_fill_value_in_gaps    | bool                                                                       | true               | If false, values between   | If false, values between known data points are expanded with the last known value from      | ``true``                                                                    | No               |
|                           |                                                                            |                    | known data points are      | the data set. If true, values between known data points are filled with ``fill_value``.     |                                                                             |                  |
|                           |                                                                            |                    | expanded with the last     |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | known value from the data  |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | set. If true, values       |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | between known data points  |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | are filled with            |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | ``fill_value``.            |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| use_fill_value_at_end     | bool                                                                       | true               | If false, values after last| If false, values after last known data point are padded with the last known value from      | ``true``                                                                    | No               |
|                           |                                                                            |                    | known data point are       | the data set. If true, values after the last known data point are filled                    |                                                                             |                  |
|                           |                                                                            |                    | padded with the last       | with ``fill_value``.                                                                        |                                                                             |                  |
|                           |                                                                            |                    | known value from the data  |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | set. If true, values       |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | after the known data point |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | are filled with            |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    | ``fill_value``.            |                                                                                             |                                                                             |                  |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| constants                 | dict[str, float]                                                           | N/A                | N/A                        | These are values defined within the report that can be combined with variables in           | ``{"Liters to Gallons": 0.264172}``                                         | No               |
|                           |                                                                            |                    |                            | aggregation.                                                                                |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| cross_references          | list[str]                                                                  | N/A                | N/A                        | References the values generated in other reports for aggregation operations.                | ``["Milk protein, kg_ver_agg_.*"]``                                         | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| vertical_aggregation      | str                                                                        | N/A                | N/A                        | Function used for aggregating data within each column.                                      | ``"sum"``                                                                   | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| horizontal_aggregation    | str                                                                        | N/A                | N/A                        | Function used for aggregating data within each row.                                         | ``"product"``                                                               | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| horizontal_first          | bool                                                                       | false              | N/A                        | Determines whether horizontal aggregation precedes vertical aggregation.                    | ``true``                                                                    | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| horizontal_order          | list[str]                                                                  | N/A                | N/A                        | Specifies the order in horizontal aggregation.                                              | ``["Herd FPCM, kg_hor_agg", "Milking cows_ver_agg", "Days per year"]``      | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| slice_start               | int                                                                        | N/A                | N/A                        | Index to start slicing data for the report.                                                 | ``-730``                                                                    | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| slice_end                 | int                                                                        | N/A                | N/A                        | Index to end slicing data.                                                                  | ``365``                                                                     | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| graph_details             | dict[str, str]                                                             | N/A                | N/A                        | Indicates report data should be graphed, must specify graph type (e.g., "plot",             | ``{"type": "plot"}``                                                        | No               |
|                           |                                                                            |                    |                            | "stackplot").                                                                               |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| graph_and_report          | bool                                                                       | false              | N/A                        | Boolean flag to save report data requested for graphing to CSV.                             | ``true``                                                                    | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| simplify_units            | bool                                                                       | true               | N/A                        | If false, complex units from aggregation won't be simplified.                               | ``false``                                                                   | No               |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| data_significant_digits   | int                                                                        | N/A                | # significant digits for   | # significant digits for reported data. `See further details in RG                          | ``2``                                                                       | No - only occurs |
|                           |                                                                            |                    | graphed data.              | wiki. <https://github.com/RuminantFarmSystems/MASM/wiki/Report-Generator#filter-content>`__ |                                                                             | at               |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             | post-processing  |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             | stage. Will not  |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             | cause values to  |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             | be rounded       |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             | during           |
|                           |                                                                            |                    |                            |                                                                                             |                                                                             | simulation.      |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| direction                 | str                                                                        | "portrait"         | N/A                        | The output CSV orientation. Either "portrait" or "landscape". If no value is provided or    | ``"portrait"``                                                              | No               |
|                           |                                                                            |                    |                            | providing an unexpected value, the default "portrait" direction will be used.               |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+
| use_verbose_report_name   | bool                                                                       | false              | N/A                        | When set to true, forces verbose report names (report_name.full_variable_address) for       | ``false``                                                                   | No               |
|                           |                                                                            |                    |                            | single-column reports. By default, single-column reports use compact names while            |                                                                             |                  |
|                           |                                                                            |                    |                            | multi-column reports use verbose names to ensure distinct column headers.                   |                                                                             |                  |
|                           |                                                                            |                    |                            | This flag only affects vertically aggregated single-column reports and unaggregated         |                                                                             |                  |
|                           |                                                                            |                    |                            | single-column reports; it has no effect on horizontally aggregated reports or multi-column  |                                                                             |                  |
|                           |                                                                            |                    |                            | reports (which already use verbose names).                                                  |                                                                             |                  |
+---------------------------+----------------------------------------------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+------------------+

Data Origins
------------

When variables are added to the output manager, the Output Manager
requires them to have an :ref:`info map <info-label>`
which tracks the class and function that is sending the data to output
manager. Each biophysical modules reports its data to a respective
reporter class to ensure that data from each daily update is added to
Output Manager at the same time within a module. As you can hopefully
see, this leads to obfuscation of the original class and function that
altered, created, or updated the data.

There is a feature available to be able to track the original class and
function that sent the data to its respective biophysical module
reporter. This feature is called Data Origins. More details can be found
here on the :doc:`Data Origins Wiki Page <Data-Origins>`.

Diagram
-------

.. figure:: /_static/OM_diagram.png
   :alt: RuFaS Overview - OM
   :align: center
   :name: rufas overview

   A high-level flow of OM within RuFaS.

Data Pools
----------

There are 4 main pools of data Output Manager collects:

1. Variables
2. Logs
3. Warnings
4. Errors

**Variables** are data calculated or changed as a result of the
simulation running.

**Logs** are used to track events that occur during the simulation.

**Warnings** are messages issued in situations where it is useful to
alert the user of some condition in the simulation where that condition
arising doesn't warrant terminating the simulation.

**Errors** are messages issued about a condition in the simulation where
that condition arising is greatly impacting the result of the simulation
but doesn't necessarily warrant terminating the simulation or raising an
exception.

For another way to think about logs, warnings, and errors:

Imagine you go to your car, open the door, get in, close the door, and
start the engine. All of these are logs. Then you look at the dashboard
to see there is a light on trying to draw your attention to the fact
that you haven't buckled your seat belt. This is a warning. Then you
turn on the AC, sadly, it is not working. This is an error that goes to
the errors pool because while there is a malfunction, it doesn't stop
you from getting to your destination. You start moving, your speed is
variable. Then you get a flat tire, so you have to stop and fix it. This
is an error that needs to be raised as an exception because it is not
possible to move forward and you would not add it to the errors pool.

Writing Logs, Warnings, and Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are some best practices for writing logs, warnings, and errors in
a way that is clear, actionable, and consistent. This section outlines
different paradigms for naming and structuring messages, allowing
flexibility based on the specific use case. The goal is to help users
easily navigate the logs, identify issues, and take appropriate actions.

General Best Practices
^^^^^^^^^^^^^^^^^^^^^^

1. Clarity and Brevity: Keep messages concise but informative. Avoid
   being repetitive.
2. Context: Include the necessary details—what happened, where it
   happened, and why (especially for warnings and errors). All of this
   information need to be contained in both the name and message fields,
   as well as the info map.
3. Actionability: Ensure warnings and errors provide clear, actionable
   guidance when appropriate.

Naming and Structuring Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two paradigms presented here for naming logs, warnings, and
errors, with variations in their structure and level of detail. But
these are by no means the only way to write log messages.

.. _1-consistent-naming-with-varied-messages:

1. Consistent Naming with Varied Messages
'''''''''''''''''''''''''''''''''''''''''

This approach uses a consistent name for logs, warnings, or errors
originating from the same part of the system, while the message
describes the specific event or issue.

- Logs: This approach is particularly useful for logs, where it’s
  important to track the flow of actions in the same process. Logs will
  group under a single name, making it easy to follow a sequence of
  events.

- Warnings: For warnings, consistent naming helps users monitor
  recurring issues in specific areas of the system. However, messages
  must be clear about the nature and impact of each warning.

- Errors: For errors, this paradigm highlights where critical issues are
  occurring. Each error message should provide detailed information
  about the failure, but the consistent naming makes it easy to identify
  patterns.

  - Pros: Groups related messages together for easier navigation.
  - Cons: Users might need to read through multiple messages under the
    same name to find relevant details.

*Examples*

Logs:

.. code:: json

   {
     "OutputManager.create_directory.Attempting to create a new directory.": {
       "info_maps": [...],
       "values": [
         "Attempting to create a new directory at ..",
         "Attempting to create a new directory at output/logs.",
         "Attempting to create a new directory at output/reports.",
         "Attempting to create a new directory at output/reports.",
         "Attempting to create a new directory at output/reports.",
         "Attempting to create a new directory at output/reports.",
         "Attempting to create a new directory at output/reports.",
         "Attempting to create a new directory at output/logs.",
         "Attempting to create a new directory at output/logs."
       ]
     },
   }

Warnings:

.. code:: json

   {
     "DataValidator._number_type_validator.Validation: value greater than maximum": {
       "info_maps": [...],
       "values": [
         "Variable: 'NDICP.[92]' has value: 27.0, greater than maximum value:  12.00. Violates properties defined in metadata properties section 'NRC_Comp_properties'.",
         "Variable: 'NDF.[21]' has value: 86.2, greater than maximum value:  85.00. Violates properties defined in metadata properties section 'NRC_Comp_properties'.",
         "Variable: 'ADICP.[39]' has value: 9.275, greater than maximum value:  8.00. Violates properties defined in metadata properties section 'NASEM_Comp_properties'.",
         "Variable: 'ADICP.[72]' has value: 8.306, greater than maximum value:  8.00. Violates properties defined in metadata properties section 'NASEM_Comp_properties'.",
         "Variable: 'NDICP.[39]' has value: 12.695, greater than maximum value:  12.00. Violates properties defined in metadata properties section 'NASEM_Comp_properties'.",
         "Variable: 'NDICP.[66]' has value: 30.34, greater than maximum value:  12.00. Violates properties defined in metadata properties section 'NASEM_Comp_properties'.",
         "Variable: 'NDICP.[72]' has value: 16.169, greater than maximum value:  12.00. Violates properties defined in metadata properties section 'NASEM_Comp_properties'."
       ]
     },
   }

Errors:

.. code:: json

   {
     "ReportGenerator.generate_report.report_generation_error": {
       "info_maps": [...],
       "values": [
         "Error generating report (Homegrown Feed Emissions) => ValueError: filter ['.*homegrown_.*_emissions.*'] in Homegrown Feed Emissions led to empty report data.",
         "Error generating report (Not a filter) => ValueError: filter ['Not.present.*'] in Not a filter led to empty report data."
       ]
     }
   }

.. _2-cause-effect-or-action-outcome-pattern:

2. Cause-Effect (or Action-Outcome) Pattern
'''''''''''''''''''''''''''''''''''''''''''

This paradigm focuses on using the name to describe the cause of the
log, warning, or error, and the message to describe the outcome or
action taken.

- Logs: In logs, this approach helps clarify what action was taken and
  what result it produced. It can be useful when you need to focus on
  specific actions and outcomes rather than grouping all logs from a
  particular area.

- Warnings: For warnings, the name should describe the condition that
  triggered the warning, while the message outlines what was done (or
  needs to be done) in response. This structure makes it easy to
  understand what caused the warning and its potential impact.

- Errors: In errors, the cause-effect pattern provides a clear
  description of the problem and what needs to be done to resolve it.
  This is especially helpful in critical situations where immediate
  action is required.

  - Pros: Provides clarity by directly linking cause and effect, making
    it easier for users to understand and respond.
  - Cons: Related issues may be dispersed across different categories,
    making it harder to track patterns over time.

*Examples*

Logs:

.. code:: json

   {
     "InputManager._load_metadata.load_metadata_attempt": {
       "info_maps": [...],
       "values": [
         "Attempting to load metadata from input/metadata/example_freestall_dairy_metadata.json."
       ]
     },
     "InputManager._load_metadata.load_metadata_success": {
       "info_maps": [...],
       "values": [
         "Successfully loaded metadata from input/metadata/example_freestall_dairy_metadata.json"
       ]
     }
   }

Warnings:

.. code:: json

   {
     "PurchasedFeedEmissionsEstimator.create_daily_purchased_feed_emissions_report.Missing Purchased Feed Emissions": {
       "info_maps": [...],
       "values": [
         "Missing data for RuFaS feed 216, omitting from purchased feed emissions estimation.",
         "Missing data for RuFaS feed 176, omitting from purchased feed emissions estimation."
       ]
     },
     "PurchasedFeedEmissionsEstimator.create_daily_land_use_change_feed_emissions_report.Missing Land Use Change Purchased Feed Emissions": {
       "info_maps": [...],
       "values": [
         "Missing data for RuFaS feed 216, omitting from land use change purchased feed emissions estimation.",
         "Missing data for RuFaS feed 176, omitting from land use change purchased feed emissions estimation."
       ]
     }
   }

Choosing the Right Approach
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Logs: Use consistent naming when you want to group related events from
  the same process. Use cause-effect when you want to highlight specific
  actions and their results.
- Warnings: If you expect recurring issues from a particular area,
  consistent naming helps to monitor them. Use cause-effect when you
  need to focus on the condition that triggered the warning and how the
  system is responding.
- Errors: Consistent naming is useful when tracking failures in a
  specific process. Use cause-effect to make it clear what went wrong
  and what action should be taken.

Summary of Pros and Cons
^^^^^^^^^^^^^^^^^^^^^^^^

+----------------------+----------------------+----------------------+
| Paradigm             | Pros                 | Cons                 |
+======================+======================+======================+
| Consistent Naming    | Easy to group        | Users may need to    |
|                      | related messages.    | sift through         |
|                      |                      | multiple messages.   |
+----------------------+----------------------+----------------------+
| Cause-Effect         | Clear description of | Similar issues may   |
| (Action-Outcome)     | cause and outcome.   | be scattered, making |
|                      |                      | pattern              |
|                      |                      | identification       |
|                      |                      | harder.              |
+----------------------+----------------------+----------------------+

Info Maps
^^^^^^^^^

Filling in the info maps with the context included in the name and title
makes logs, warnings, and errors easier to process on a large scale
i.e., querying logs stored in a database and processed by a script.

Naming Conventions
^^^^^^^^^^^^^^^^^^

By following patterns for the names of warnings and errors, maintainers
of RuFaS will be able to automate some parts of their processing and
analysis. This will be helpful when there are very high volumes of
warnings and errors, and manually checking them would be too time
consuming.

To keep the "name" field of warnings and errors in RuFaS consistent,
stick to the following rule of thumb:

- Whatever problem is causing the warning or error to be logged, figure
  out which Python
  `Exception <https://docs.python.org/3/library/exceptions.html>`__ it
  would be raised as.
- Remove the "Error" from the name of that exception.
- Prepend the shortened exception and ":" to the logged name.

For example, a key that is expected to be a dictionary is not there. If
this were an uncaught exception, it would be raised as a ``KeyError``.
So when if the name of the error that is being logged instead is
"Missing xyz information from abc data", the name would be rewritten as
"Key: Missing xyz information from abc data".

What **NOT** To Do
^^^^^^^^^^^^^^^^^^

*Never* leave the name or message of a log, warning, or error blank!
There should always be a name and message, no matter how unnecessary it
may seem.

Don't add errors to the Output Manager in places other than where the
error was discovered (except in cases where this is *absolutely*
necessary). Doing so makes the code more convoluted and harder to work
with.

--------------

.. _add-label:

Adding Data to the Output Manager
---------------------------------

To use the Output Manager to collect variables, logs, warnings, or
errors throughout the model:

1. Import the Output Manager class into the Python file you are working
   in. The best practice is to organize this statement alphabetically at
   the top of the file.

2. Instantiate Output Manager - most of the time within the **init** of
   the class so it's available for all functions in the class. This
   should only need to be done once in each particular program file.
   Because Output Manager is a singleton, you can instantiate it anew
   once in each program file and it will always refer back to the same
   Output Manager. Therefore you do not need to import it between
   different program files.

3. Next initialize one of the main parameters required by an entry into
   each of the Output Manager pools: the info_map. (More on info_maps
   below)

4. Avoid entering hard-coded values to the info_map and Output Manager
   pools.

5. Use the appropriate Output Manager method to add the variable, log,
   warning, or error along with its info_map.

.. _info-label:

Info_maps
---------

The Info_map requires you to send both the caller class\* and the caller
function i.e. wherever you are in a particular program file. It can take
additional optional contextual variables that might be helpful in
figuring out the state of the model and class at the moment something
was added to one of the Output Manager pools. So you will need to create
a new instance of info_map within each method/function it is needed in
within each class.

\* While many of the functions within the RuFaS model are organized into
classes, there remain some functions within the codebase that are not.
In the case where data needs to be added to the Output Manager from a
function that is not currently associated with a class, the caller
class, in this case, can be entered into the info_map as
"no_caller_class".

An info_map is meant to capture environment variables to have
reproducible results, warnings, and errors. Adding the caller class and
caller function is the bare minimum.

**HOWEVER**

Info_maps are added to the associated pool at every instance during the
simulation. Many variables are added on a daily basis so please
carefully consider the data you are adding to the info_map because the
size of the Output Manager files can grow unmanageably large over longer
simulations if large data structures are added frequently.

Info_map best practices:

- Be mindful of the frequency with which the function in which you are
  adding the data to the Output Manager is called. If it is a function
  that is called daily, look closely at the data you are adding at both
  the info_maps level and the variable/warning/error/log itself.
- Be cautious to add larger data structures such as objects to the
  info_maps (or directly to the pools). Instead look to extract specific
  pieces of data you believe would be helpful as contextual data for
  what you are adding to the Output Manager pools.
- Be considerate - each piece of data added to the Output Manager will
  be collected for every simulation run by everyone who runs the model.
  Info_maps can be intentionally excluded from the Output Manager pools
  but we want to leave the option for people to run the simulation with
  info_maps included.

Navigating Variables Pool Data
------------------------------

The ``variables_pool`` data is of primary interest to most people
running the model as it contains the data produced by the simulation
engine. After each simulation, the ``variables_pool`` data is turned
into a JSON file and multiple CSV files. The entirety of the
``variables_pool`` data is dumped to a JSON file titled
``all_variables_[timestamp].json``. Additionally, each variable is saved
into its own CSV file, titled ``[variable]_[timestamp].csv``, in the
``ouput/CSVs/om/variables/`` directory.

This ``all_variables`` JSON file contains a LOT of data generated during
a simulation and can therefore be overwhelming on its own.

Output Manager has several features to help users navigate this large
pool of data:

1. :ref:`The variable names list <the-variable-names-list>`.
2. :ref:`The exclude_info_maps flag <the-exclude_info_maps-flag>`.
3. :ref:`Filtering <filtering>`.

.. _the-variable-names-list:


The variable names list.
~~~~~~~~~~~~~~~~~~~~~~~~

At the end of each simulation, Output Manager generates a text file that
lists the names of all variables added to the variables pool during the
simulation. The name of this file follows the pattern:
``variable_names_[timestamp].txt``. This file is saved in the output
folder alongside the other JSON output files. The variable names list
provides a good overview to see what data has been reported.

The structure of each variable name is:

``ClassName.function_name.variable_name.[values/info_maps]: nested_variable_name(if applicable)``

An example variables name file generated by a simulation looks like
this:

::

   _exclude_info_maps=True, expect info_maps accordingly.
   MilkingParlor.__init__.fresh_water_use_rate
   MilkingParlor.__init__.fresh_water_use_rate.info_maps: minutes_spent_in_holding_area
   MilkingParlor.__init__.fresh_water_use_rate.info_maps: minutes_spent_per_milking
   MilkingParlor.__init__.fresh_water_use_rate.info_maps: wash_water_use_rate
   MilkingParlor.__init__.fresh_water_use_rate.info_maps: num_milkings
   ManualScraping.__init__.milking_parlor.info_maps: weather
   ManualScraping.__init__.milking_parlor.info_maps: config
   ManualScraping.__init__.milking_parlor.info_maps: time
   ManualScraping.__init__.milking_parlor.values: num_milkings
   ManualScraping.__init__.milking_parlor.values: minutes_spent_in_holding_area
   ManualScraping.__init__.milking_parlor.values: minutes_spent_per_milking
   ManualScraping.__init__.milking_parlor.values: wash_water_use_rate
   ManualScraping.__init__.milking_parlor.values: fresh_water_use_rate
   FlushSystem.__init__.milking_parlor.values: num_milkings
   FlushSystem.__init__.milking_parlor.values: minutes_spent_in_holding_area
   FlushSystem.__init__.milking_parlor.values: minutes_spent_per_milking
   FlushSystem.__init__.milking_parlor.values: wash_water_use_rate
   FlushSystem.__init__.milking_parlor.values: fresh_water_use_rate
   Cow.milking_update.milk_data_at_milk_update.values: days_in_milk
   Cow.milking_update.milk_data_at_milk_update.values: estimated_daily_milk_produced
   Cow.milking_update.milk_data_at_milk_update.values: milk_protein
   Cow.milking_update.milk_data_at_milk_update.values: milk_fat
   Cow.milking_update.milk_data_at_milk_update.values: milk_lactose
   Cow.milking_update.milk_data_at_milk_update.values: lactating
   Cow.milking_update.milk_data_at_milk_update.values: parity
   Cow.milking_update.milk_data_at_milk_update.values: cow_id
   LifeCycleManager.daily_update.life_cycle_daily_herd_update.values: calf_num
   LifeCycleManager.daily_update.life_cycle_daily_herd_update.values: heiferI_num
   LifeCycleManager.daily_update.life_cycle_daily_herd_update.values: heiferII_num
   …

.. _the-exclude_info_maps-flag:

The exclude_info_maps flag.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As stated in the :ref:`info map section <info-label>`,
an info_map is meant to capture runtime environment variables to have
reproducible results. Info_maps are added to the outputs by default.
However, a user may wish to exclude the info_maps environmental
variables to reduce the amount of data in the output files they’re
looking through.

To do this, run the model by ``python main.py -ei`` which indicates
info_maps should be excluded. (Running ``python main.py -h`` shows all
available args).

.. _filtering:

Filtering.
~~~~~~~~~~

To get the most refined variables_pool results, the Output Manager
allows a user to filter the variables_pool using pattern-matching. The
user will create text files listing the patterns they want to be
matched. These text files are expected to be stored in the
``MASM/output/output_filters`` directory.

Filtering the JSON and the CSV output is done separately. The files
containing patterns for JSON output must begin with ``json_`` and the
files containing patterns fro CSV ouput must begin with ``csv_``.

A pattern text file will have one filter pattern per line. Each line
will be treated as a separate pattern to match across the entirety of
the variables_pool.

**The pattern only checks against the
``ClassName.function_name.variable_name`` portion of each variable. The
``values/info_maps`` and ``nested variable name`` are not searched.**

At the end of a simulation, the Output Manager will look in the
``MASM/output/output_filters`` directory and create an output file for
each text file found in this directory.

Each output file will be named following the pattern
``saved_variables_<filter file name>_<timestamp>.json`` or
``saved_variables_<filter file name>_<timestamp>.csv``. All JSON output
files will be written to the ``output/`` directory, while all CSV output
files will be written to the ``output/CSVs/om/`` directory.

How does the filter work?
~~~~~~~~~~~~~~~~~~~~~~~~~

The Output Manager uses Regular Expression (or RegEx) patterns to look
for matches in the ``variables_pool``. To learn more about RegEx, jump
to the :ref:`regex section <regex-label>`.

To provide additional flexibility in filtering, the user has the option
to filter the ``variables_pool`` inclusively or exclusively.

“Inclusive” filtering will look in the patterns file and add all the
matching data from the ``variables_pool`` to the output file.

“Exclusive” filtering will look in the patterns file and add everything
*except* for the matching data from the ``variables_pool`` to the output
file.

For example, if the ``variables_pool`` contains ``a``, ``b``, ``c``:
Inclusively filtering ``a`` would lead to an output file containing just
``a`` while exclusively filtering ``a`` would lead to an output file
containing just ``b`` and ``c``.

**If the first line of the pattern file is "exclude" then the file is
treated as exclusion; otherwise, the inclusion mechanism will be
called.**

**Note:** For this reason, "exclude" is the keyword that OM uses to
differentiate inclusion and exclusion, therefore, if reported variables
have this keyword in them, unexpected outputs might be produced.

**If the first entry is not “exclude”, the filter patterns file will be
treated as inclusive and will add only the data from the variables pool
that the filter finds matches those patterns.**

\**\*

Here is an example of a filters file that would be treated as
“exclusive” by the Output Manager
(**[json\_/csv\_]filter_patterns.txt**):

::

   exclude
   Feed.summarize_feed_storage.nutrients_summary
   .*milk.*update
   MilkingParlor.calc_wash_water_volume_used_in_holding_area.wash_water_volume_used_in_holding_area
   MilkingParlor.__init__.fresh_water_use_rate
   ^LifeCycleManager.*update$

That same group of filters if you wanted the Output Manager to treat the
patterns as “inclusive” (**[json\_/csv\_]filter_patterns.txt**):

::

   Feed.summarize_feed_storage.nutrients_summary
   .*milk.*update
   MilkingParlor.calc_wash_water_volume_used_in_holding_area.wash_water_volume_used_in_holding_area
   MilkingParlor.__init__.fresh_water_use_rate
   ^LifeCycleManager.*update$

In practice, you will want to name your filters file specifically to
inform the name of your output file.

\**\*

As the user may note, some of the above filter patterns are full
variable names as listed from the ``variable_names`` text file and some
are shortened with some additional characters added in. These entries
with extra characters are filter patterns using Regular Expressions
(RegEx). Because RegEx may not be familiar to everyone using the RuFaS
model, we’re providing some examples that are adaptable to users’ needs.

One quick note for substitutions from provided examples - RegEx is case
sensitive so you must match the case of a specific search term *exactly*
e.g. LifeCycleManager NOT lifecyclemanager nor Lifecyclemanager nor
LifeCyclemanager.

--------------

Here are some base example patterns that can be used as templates for making your own filter pattern file:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**1. Match by class:**

::

   ^Cow.* 

This would match all variables added from within the Cow class.

::

       Cow.milking_update.milk_data_at_milk_update.values: days_in_milk
       Cow.milking_update.milk_data_at_milk_update.values: estimated_daily_milk_produced
       …

Cow can be substituted for any class name but keep the format
^ClassName.\* and remember to match the case exactly.

**2. Match by variable name:**

::

   .*daily_output.* 

This would match all variables that ended in “daily_output” regardless
of what class or function they were added from:

::

       ManualScraping.daily_update.daily_output.values: pen_id
       ManualScraping.daily_update.daily_output.values: simulation_day
       …
       ReceptionPit.daily_update.daily_output.values: pen_id
       ReceptionPit.daily_update.daily_output.values: simulation_day
       …
       FlushSystem.daily_update.daily_output.values: simulation_day
       FlushSystem.daily_update.daily_output.values: manure_urea
       …

It would NOT match variables like these though because of the text
between "daily" and "output":

::

       Feed.daily_update.daily_phosphorus_outputs.values: phosphorus
       Feed.daily_update.daily_nitrogen_outputs.values: nitrogen

**3. Match by a combination of class name and variable name:**

::

       ^ManualScraping.*daily_output.* 

This would match all variables added from within the ManualScraping
class that end with daily_output:

::

       ManualScraping.daily_update.daily_output.info_maps: sim_day
       ManualScraping.daily_update.daily_output.info_maps: bedding
       ManualScraping.daily_update.daily_output.values: pen_id
       …

It would NOT match either of these:

::

       ManualScraping._get_current_day_average_temperature_in_celsius.current_day_average_temperature_in_celsius
       ManualScraping.calc_cleaning_water_volume_in_main_barn.cleaning_water_volume_in_main_barn

**4. Match by keyword:**

::

       .*[nN]itrogen.* 

This would match all variables, function names, and class names
containing the word nitrogen. Note: the [nN] near the start of the
pattern indicates that in the search the first letter of “nitrogen” can
be either lowercase OR uppercase N. It would therefore capture all
instances of either.

::

       ReceptionPit.daily_update.daily_output.liquid_manure_total_ammoniacal_nitrogen
       ReceptionPit.daily_update.daily_output.liquid_manure_nitrogen
       ManualScraping.daily_update.daily_output.liquid_manure_total_ammoniacal_nitrogen
       ManualScraping.daily_update.daily_output.liquid_manure_nitrogen
       FlushSystem.daily_update.daily_output.liquid_manure_total_ammoniacal_nitrogen
       FlushSystem.daily_update.daily_output.liquid_manure_nitrogen
       Feed.summarize_feed_storage.nitrogen
       NitrogenCollection.manure_collection.daily_update

.. _regex-label:

Regular Expressions
~~~~~~~~~~~~~~~~~~~

A full explanation of Regular Expressions is not appropriate (nor
possible) in this space but users are encouraged to look more into the
subject with these resources:

`Introduction to Regular Expressions in RuFaS and its application for
filtering outputs <https://youtu.be/S5jse5_Zw40>`__

`RegEx
introduction <https://www.geeksforgeeks.org/regular-expression-python-examples-set-1/#>`__

`Second Regex
introduction <https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285>`__

`RegEx tester with cheat sheet <https://regex101.com/>`__ - remember to
specify Python in the “flavor” section on the left side.

`RegEx cheat-sheet <https://www.debuggex.com/cheatsheet/regex/python>`__

`Introduction video to pattern matching with RegEx in Python taught
using PyCharm IDE <https://www.youtube.com/watch?v=wnuBwl2ekmo>`__

`Regular Expressions full Python
documentation <https://docs.python.org/3/library/re.html>`__

**One final RegEx note:** There are a LOT of other resources related to
Regular Expressions you will find with a simple Google search. RegEx is
very widely used across a variety of programming languages. In most
cases, using a RegEx tester specifically built for JavaScript (for
example) won’t cause any issues. But because of small differences
between programming languages, RegEx can behave slightly differently
between them and give you unexpected results so the best option is to
seek out and use RegEx resources specifically geared towards use in
Python.

--------------

The Output Manager has more details, configurations, and optional
arguments for many of its methods that are not part of a typical use
case but it is still encouraged for the user to explore in the
`output_manager.py
file <https://github.com/RuminantFarmSystems/MASM/blob/master/RUFAS/output_manager.py>`__.

.. |RuFaS Overview - OM| image:: https://github.com/RuminantFarmSystems/MASM/assets/70217952/2f564287-3041-426e-97e0-2af2ab10c409

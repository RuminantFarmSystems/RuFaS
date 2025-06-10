Data Origins
============

When variables are added to the Output Manager, they are required to
have an `info
map <https://github.com/RuminantFarmSystems/MASM/wiki/Output-Manager#info_maps>`__
which tracks the class and function that is sending the data to Output
Manager. Each biophysical modules reports its data to a respective
reporter class to ensure that data from each daily update is added to
Output Manager at the same time within a module.

For example, when a cow produces milk on a particular day, that gets
reported to OutputManager by ``AnimalModuleReporter.report_milk()``.
However, that's not where the actual calculation for the amount or
contents of that milk occurs. Those calculations occur in
``Cow.milking_update()``.

As you can see, the default reporting mechanism can lead to obfuscation
of the original class and function that altered, created, or updated the
data.

There is a feature available to be able to track the original class and
function that sent the data to its respective biophysical module
reporter. This feature is called ``Data Origins``.

Vocabulary
----------

- ``True Origin`` - this is the function which originally sent the data
  to its intermediary data reporter class. (i.e. the class and function
  where the actual calculation/alteration/creation of the data occurs).
- ``Report Origin`` - this is the name of the reporting class that
  actually sent the variable data to OutputManager (i.e. the
  intermediary class and function like
  ``AnimalModuleReporter.report_ration_interval()``).
- ``detailed_values`` - where the information about the data origins
  will be located in the JSON output file.

How to use it
-------------

Data Origins is a feature available within an Output Manager JSON report
filter. This is a report filter that saves specific data to a JSON file
and the filter file name will start with ``json_``.

Within each report filter, the user can select one of the following to
set the "origin_label" to:

1. "true and report origins" - Indicates that both the true origin and
   report origin should be included.
2. "true origin" - Indicates that only the true origin should be
   included.
3. "report origin" - Indicates that only the report origin should be
   included.
4. "none" - (default) Indicates that no origin information should be
   included.

**IMPORTANT NOTES**:

- data-origins are currently available (11/25/24) for the Animal Module.
  This is not by design - the dev team has issues open to add the data
  origins info for the other biophysical modules.
- The data-origins info is located in the info-map so if a user opts to
  ``exclude_info_maps`` in their task, this feature will not be
  available to them.

Examples:
---------

For this first one, I only the ``True Origin`` (the original class and
function that created/updated the data) for ``ration_nutrient_amount``
for each pen. Filter file name
``json_ration_nutrient_amount_by_pen_true_origin.json``.

::

   {   
       "name": "Ration Nutrients True Origin",
       "filters": [ "AnimalModuleReporter.report_ration_interval_data.ration_nutrient_amount_pen_.*"
                  ],
       "origin_label": "true origin"
   }

As you can see, in the ``detailed_values`` section of the filter output,
I get the ``True Origin`` class and function
``[AnimalManager._handle_pen_ration]``:

For this second example, I want to see both the ``True Origin`` and the
``Report Origin`` Filter file name
``json_ration_nutrient_amount_by_pen_both_origins.json``

::

   {
       "name": "Ration Nutrients True and Report Origins",
       "filters": [ "AnimalModuleReporter.report_ration_interval_data.ration_nutrient_amount_pen_.*"
                  ],
       "origin_label": "true and report origins"
   }

In this version, I get BOTH the ``True Origin`` class and function AND
the ``Report Origin`` class and function
``[AnimalManager._handle_pen_ration] -> [AnimalModuleReporter.report_ration_interval_data.ration_nutrient_amount_pen_...]``:

If you don't want any origins info reported in your JSON filter, you can
either use ``"origin_label": "none"`` or leave the ``origin_label``
filter attribute completely out of your filter since the default is to
not report data origin info.

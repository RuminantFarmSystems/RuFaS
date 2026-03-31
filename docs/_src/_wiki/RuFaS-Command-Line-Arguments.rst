RuFaS Command Line Arguments
============================

Overview
--------

Command line arguments are simple parameters passed during program
execution that allow the user to affect the operation of the RuFaS
simulation. This reference will go over each of the current options and
what their effect is on the simulation.

Available Arguments (updated 05/23/2024)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **-h, --help**: A good place to start if you want a quick reminder of
  all the available arguments and what each of their effects is. This
  option displays all the currently available command line argument
  options and then exits without running a simulation.

- **-g, --no-graphics**: This option allows you to prevent the
  generation of graphics. When specified, no graphical plots or charts
  will be created for all tasks run.

- **-v, --verbose**: This option specifies which log types the user
  wants to be printed out in the terminal during the simulation. This is
  a helpful tool for simulation evaluation. Options are: errors,
  warnings, logs, none and credits. E.g. ``python main.py -v warnings``.
  Selecting ``credits`` will print out RuFaS version information and a
  disclaimer only. Selecting ``errors`` will print out errors and
  credits only. Selecting ``warnings`` will print out warnings, errors
  and credits. Selecting ``logs`` will print out all 4. The default
  option is ``none``.

- **-c, --clear-output**: This option clears the output directory before
  running the simulation. Helpful to keep your output folder clean,
  clear, and under control. The default value if not specified by the
  user is false meaning the directory will not be cleared.

- **-i, --exclude_info_maps**: This option tells Task Manager's Output
  Manager to exclude data collected in info_maps from the output
  generated while managing tasks. The default setting is false meaning
  info_maps will be included in the output.

- **-o, --output-dir**: This argument allows the user to specify which
  directory will be cleared if using the **-c** option. *EXERCISE
  CAUTION* when using this option. The default directory is ``output/``.

- **-s, --suppress-log-files**: This option will stop the Task Manager
  from writing its logs (logs, errors, warnings, and other miscellaneous
  information) to files.

- **-l, --logs-dir**: This option tells the Task Manager which directory
  it should write log files in, if it writes log files. The default
  directory is ``output/logs``.

- **-m, --metadata-depth-limit**: This option will override the limit
  for how deeply "nested" input passed to RuFaS is allowed to be. The
  default is 7.

- **-p, --path-to-metadata**: This option can be used to provide the
  path to the metadata containing the reference to the tasks that will
  be run by RuFaS. For example, the command to run
  ``herd_init_metadata.json`` would be
  ``python main.py -p input/metadata/herd_init_metadata.json``. If this
  flag is not used, RuFaS will run ``task_manager_metadata.json``.

Examples for copy-paste
~~~~~~~~~~~~~~~~~~~~~~~

Print out warnings and error messages during simulation:

::

   python main.py -v warnings

Clear output folder:

::

   python main.py -c

Specify an output directory:

::

   python main.py -o output/mydirectory

Specify a directory for Task Manager's logs to be written to:

::

   python main.py -l outputs/task_manager_logs

Limit the maximum depth of nested inputs to RuFaS:

::

   python main.py -m 5

Multiple Arguments
~~~~~~~~~~~~~~~~~~

You can pass one or combine multiple command line arguments when
executing the program.

For example maybe you want to suppress Task Manager's log files (-s) and
also clear your output folder (-c). You could do this with:

``python main.py -cs`` (you can string multiple different args
together).

or

``python main.py -sc``

or the recommended method

``python main.py -c -s``

When passing multiple arguments, if one of the arguments requires a
specific choice (e.g. verbose), you want that to either be last in a
grouped set of arguments or to be on its own with the choice for it
immediately after. For this example we're using the -v for verbose and
setting it as ``block``.

``python main.py -cv logs``

or

``python main.py -c -v logs``

If you do try to pass a choice to an argument that doesn't take one, you
will get an error message and it's not the end of the world.

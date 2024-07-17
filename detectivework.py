import os
import json
import pandas as pd
from typing import Any, List
import statistics

logfilepath = "output/logs/"
fileprefix = "test-9"
num_files = 96 + 32

# read the CSV
input_list = "output/test-9-animal_S256_inputs.csv"
input_list_read = pd.read_csv(input_list)
# add the index for each, 0-X is a columns for run
df = pd.DataFrame(input_list_read)
num_rows = len(df.index)
df.insert(0, "Simulation_number", list(range(1, num_rows + 1)), True)
print(df)

def load_json(json_filename: str) -> Any: # noqa
    with open(json_filename) as json_file:
        json_loaded = json.load(json_file)
    return json_loaded


# Get the list of files
logfiles = [filename for filename in os.listdir(logfilepath) if filename.startswith(fileprefix) and "logs" in filename]

errorfiles = [filename for filename
              in os.listdir(logfilepath) if filename.startswith(fileprefix) and "errors" in filename]

total_time_float_list: List[float | str] = []
initornotlist: List[str | bool] = []
digits = len(str(num_rows))

for row_num in range(num_rows):
    print(row_num)
    # INSIDE THE LOOP
    try:
        logfilefound = [file for file in logfiles if 'run ' + f'{row_num + 1}'.zfill(digits) in file][-1]
        logfile = load_json(logfilepath + logfilefound)
    except Exception as ex:
        print(ex)
        total_time_float_list.append(999999999999999999999999)
        initornotlist.append("Unknown")
        continue

    # list(logfile.keys())
    try:
        total_time_string = logfile["SimulationEngine.simulate.total_simulation_time"]["values"][0]
        total_time_float = float(total_time_string[total_time_string.rfind(":") + 1:])
        total_time_float_list.append(total_time_float)
    except Exception as ex:
        print(ex)
        total_time_float_list.append(999999999999999999999999)

    errorfilefound = [file for file in errorfiles if 'run ' + f'{row_num + 1}'.zfill(digits) in file][-1]
    errorfile = load_json(logfilepath + errorfilefound)
    list(errorfile.keys())
    initornot = "TaskManager.task.Failed to finish the task" in list(errorfile.keys())
    initornotlist.append(initornot)

len(initornotlist)
len(total_time_float_list)
df.insert(1, "Simulation time", total_time_float_list, True)
df.insert(2, "Failed simulation", initornotlist, True)

long_simulations = df.loc[df["Simulation time"] > 600]
normal_simulations = df.loc[df["Simulation time"] <= 600]
failed_simulations = df.loc[df["Failed simulation"] == True]
passed_simulations = df.loc[df["Failed simulation"] == False]

otherlist = ['Simulation_number', 'Simulation time', 'Failed simulation']
input_variable_list = [colname for colname in list(df.columns) if 'dummy' not in colname and colname not in otherlist]

passfail_list = []
timing_list = []
uniquely_failed_list = []
uniquely_long_list = []
input_variable = "animal.ration.formulation_interval"
for input_variable in input_variable_list:
    print(input_variable)
    failed_inputs = list(failed_simulations[input_variable])
    passed_inputs = list(passed_simulations[input_variable])

    failed_mean = f'{float(f"{statistics.mean(failed_inputs):.3g}"):g}'
    passed_mean = f'{float(f"{statistics.mean(passed_inputs):.3g}"):g}'
    passfail_list.append((passed_mean, failed_mean))

    uniquely_failed = [input for input in failed_inputs if input not in passed_inputs]
    print(uniquely_failed)
    uniquely_failed_list.append(uniquely_failed)

    long_inputs = list(long_simulations[input_variable])
    normal_inputs = list(normal_simulations[input_variable])

    long_mean = f'{float(f"{statistics.mean(long_inputs):.3g}"):g}'
    normal_mean = f'{float(f"{statistics.mean(normal_inputs):.3g}"):g}'
    timing_list.append((normal_mean, long_mean))

    uniquely_long = [input for input in long_inputs if input not in normal_inputs]
    uniquely_long_list.append(uniquely_long)

meta = pd.DataFrame({"input_variable_list" : input_variable_list,
                     "passfail_list": passfail_list,
                     "timing_list": timing_list,
                     "uniquely_failed_list": uniquely_failed_list,
                     "uniquely_long_list": uniquely_long_list})
meta.to_csv("input_meta.csv")

# for each run in the CSV, get the log file, and then append relevant info
# e.g. total runtime
# SimulationEngine.simulate.total_simulation_time
# number of warnings
# if there were errors
# TaskManager.task.Failed to finish the task
# if the simulation couldn't run!


# THEN in the CSV file: for those with errors, and ALSO for those with long runtimes (over 10 minutes)
# determine which parameters had in common?
    # Which are the same among all
    # Which are the same for those, and NOT for the rest
    # Which are the

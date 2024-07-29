#  type: ignore
import os
import json
import pandas as pd
from typing import Any, List
import statistics
from itertools import combinations, chain
import time
import gc

logfilepath = "output/logs/"
fileprefix = "test-10"
num_files = 96 + 32

# read the CSV
input_list = "output/test-10-animal_S256_inputs.csv"
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
df.to_csv(f"{fileprefix}_input_input_list_annotated.csv")

long_simulations = df.loc[df["Simulation time"] > 600]
normal_simulations = df.loc[df["Simulation time"] <= 600]
failed_simulations = df.loc[df["Failed simulation"] == True]
passed_simulations = df.loc[df["Failed simulation"] == False]

otherlist = ['Simulation_number', 'Simulation time', 'Failed simulation']
input_variable_list = [colname for colname in list(df.columns) if 'dummy' not in colname and colname not in otherlist]

passfail_list = []
timing_list = []

almost_uniquely_failed_list = []
almost_uniquely_long_list = []

uniquely_failed_list = []
uniquely_long_list = []

pass_mean_list = []
fail_mean_list = []
long_mean_list = []
normal_mean_list = []

input_variable = "animal.ration.formulation_interval"
for input_variable in input_variable_list:
    print(input_variable)
    failed_inputs = list(failed_simulations[input_variable])
    passed_inputs = list(passed_simulations[input_variable])

    failed_mean = f'{float(f"{statistics.mean(failed_inputs):.3g}"):g}'
    passed_mean = f'{float(f"{statistics.mean(passed_inputs):.3g}"):g}'
    pass_mean_list.append(passed_mean)
    fail_mean_list.append(failed_mean)
    passfail_list.append((passed_mean, failed_mean))

    if len(set(failed_inputs)) == 1:
        almost_uniquely_failed_list.append(failed_inputs[0])
    else:
        almost_uniquely_failed_list.append('')
    uniquely_failed = [input for input in failed_inputs if input not in passed_inputs]
    # print(uniquely_failed)
    uniquely_failed_list.append(uniquely_failed)

    long_inputs = list(long_simulations[input_variable])
    normal_inputs = list(normal_simulations[input_variable])

    if len(set(long_inputs)) == 1:
        almost_uniquely_long_list.append(long_inputs[0])
    else:
        almost_uniquely_long_list.append('')
    long_mean = f'{float(f"{statistics.mean(long_inputs):.3g}"):g}'
    normal_mean = f'{float(f"{statistics.mean(normal_inputs):.3g}"):g}'

    long_mean_list.append(long_mean)
    normal_mean_list.append(normal_mean)
    timing_list.append((normal_mean, long_mean))

    uniquely_long = [input for input in long_inputs if input not in normal_inputs]
    uniquely_long_list.append(uniquely_long)

meta = pd.DataFrame({"input_variable_list" : input_variable_list,
                     "pass_mean_list": pass_mean_list,
                     "fail_mean_list": fail_mean_list,
                     "normal_mean_list": normal_mean_list,
                     "long_mean_list": long_mean_list,
                     "almost_uniquely_failed_list": almost_uniquely_failed_list,
                     "almost_uniquely_long_list": almost_uniquely_long_list,
                     "uniquely_failed_list": uniquely_failed_list,
                     "uniquely_long_list": uniquely_long_list})
meta.to_csv(f"{fileprefix}_input_meta.csv")

# Example lists
list1 = [1, 2, 3, 4]
list2 = [5, 6, 3, 4]
list3 = [9, 10, 3, 12]


# Function to generate all possible subsets of a list of lists
def all_subsets(lists):
    # Create a list of all combinations of the list indices
    all_combinations = list(chain(*[combinations(range(len(lists)), i) for i in range(1, len(lists) + 1)]))
    return all_combinations


# Function to check and count combinations in a subset
def count_combinations(subset_indices, lists):
    subset_lists = [lists[i] for i in subset_indices]
    combined = list(zip(*subset_lists))
    combination_count = {}
    for combination in combined:
        if combination in combination_count:
            combination_count[combination] += 1
        else:
            combination_count[combination] = 1
    return combination_count


# long_simulations
# normal_simulations
failed_inputs_lists = failed_simulations[input_variable_list].values.tolist()
# passed_simulations

# List of lists
lists = [list1, list2, list3]

# use my data!
lists = failed_inputs_lists
#
len(input_variable_list)
len(lists[0])
thenewlists = []
for thelist in lists:
    thenewlists.append([name + ":" + str(value) for name, value in zip(input_variable_list, thelist)])

lists = thenewlists

start = time.time()
# Get all subsets of the lists
subsets = all_subsets(lists)
stop = time.time()
print(f'time to get subsets is {stop - start} seconds')


def original_combo_counting(subsets, lists):
    combination_count = {}
    for subset in subsets:
        idx_subset = [i for i in subset]
        subset_lists = [" + ".join([listy[i] for i in idx_subset]) for listy in lists]
        for sl in subset_lists:
            print(sl)

        for combination in subset_lists:
            if combination in combination_count:
                combination_count[combination] += 1
            else:
                combination_count[combination] = 1
        return combination_count


def combo_counting(subset, lists):
    combination_count = {}
    idx_subset = [i for i in subset]
    subset_lists = [" + ".join([listy[i] for i in idx_subset]) for listy in lists]

    for combination in subset_lists:
        if combination in combination_count:
            combination_count[combination] += 1
        else:
            combination_count[combination] = 1
    return combination_count


# Dictionary to count all combinations
all_combination_counts = {}

print(f'Number of subsets = {len(subsets)}')
print(subsets[100])
num_subsets = len(subsets)

# for subset in subsets:
#     if i % 100000 == 0:
#         print(i)
#     combination_count = combo_counting(subset, lists)
#     for combination, count in combination_count.items():
#         if combination in all_combination_counts:
#             all_combination_counts[combination] += count
#         else:
#             all_combination_counts[combination] = count

start = time.time()
for subset_number in range(num_subsets):
    if subset_number % 100000 == 0:
        print(subset_number)
    combination_count = combo_counting(subsets[subset_number], lists)
    for combination, count in combination_count.items():
        if combination in all_combination_counts:
            all_combination_counts[combination] += count
        else:
            all_combination_counts[combination] = count
stop = time.time()
print(f'counted combinations in {(stop - start)/60} minutes.')


start = time.time()
repeated = {}
# Find and print repeated combinations
repeated_combinations = {k: v for k, v in all_combination_counts.items() if v > 25}
if repeated_combinations:
    # print("Repeated combinations and their counts:")
    for combination, count in repeated_combinations.items():
        # print(f"{combination}: {count} times")
        repeated[combination] = count
else:
    # print("No repeated combinations found.")
    pass
stop = time.time()
print(f'counted repeats in {stop - start} seconds.')

try:
    with open('repeated.json', 'w', encoding='utf-8') as f:
        json.dump(repeated, f, ensure_ascii=False, indent=4)
except:
    pass

dfrepeated = pd.DataFrame.from_dict(repeated, orient="index")
dfrepeated.to_csv("repeated.csv")

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

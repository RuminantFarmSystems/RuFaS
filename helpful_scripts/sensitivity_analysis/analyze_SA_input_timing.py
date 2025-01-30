# flake8: noqa
#  type: ignore
import os
import json
import pandas as pd
from typing import Any, List
import statistics
# from itertools import combinations, chain
# import time
# import gc
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

config_json_filename = "model_evaluation/sensitivity_analysis/SA_analyze.json"

with open(config_json_filename) as json_file:
    config_json = json.load(json_file)

analysis = config_json["analyses"][0]

logfilepath = analysis["output_path"] + "logs/"
reportfilepath = analysis["output_path"] + "reports/"
fileprefix = analysis["analysis_prefix"]

# read the CSV
input_list = reportfilepath + "analyzed/" + f"{fileprefix}_inputs.csv"
input_list_read = pd.read_csv(input_list)
# add the index for each, 0-X is a columns for run
df = pd.DataFrame(input_list_read)
num_rows = len(df.index)
df.insert(0, "Simulation_number", list(range(1, num_rows + 1)), True)
print(df)


def load_json(json_filename: str) -> Any:  # noqa
    with open(json_filename) as json_file:
        json_loaded = json.load(json_file)
    return json_loaded


# Get the list of files
logfiles = [filename for filename in os.listdir(logfilepath) if filename.startswith(fileprefix) and "logs" in filename]

errorfiles = [
    filename for filename in os.listdir(logfilepath) if filename.startswith(fileprefix) and "errors" in filename
]

total_time_float_list: List[float | str] = []
initornotlist: List[str | bool] = []
digits = len(str(num_rows))

for row_num in range(num_rows):
    print(row_num)
    # INSIDE THE LOOP
    try:
        logfilefound = [file for file in logfiles if "run " + f"{row_num + 1}".zfill(digits) in file][-1]
        logfile = load_json(logfilepath + logfilefound)
    except Exception as ex:
        print(ex)
        total_time_float_list.append(999999999999999999999999)
        initornotlist.append("Unknown")
        continue

    # list(logfile.keys())
    try:
        total_time_string = logfile["SimulationEngine.simulate.total_simulation_time"]["values"][0]
        total_time_float = float(total_time_string[total_time_string.rfind(":") + 1 :])
        total_time_float_list.append(total_time_float)
    except Exception as ex:
        print(ex)
        total_time_float_list.append(999999999999999999999999)

    errorfilefound = [file for file in errorfiles if "run " + f"{row_num + 1}".zfill(digits) in file][-1]
    errorfile = load_json(logfilepath + errorfilefound)
    list(errorfile.keys())
    initornot = "TaskManager.task.Failed to finish the task" in list(errorfile.keys())
    initornotlist.append(initornot)

len(initornotlist)
len(total_time_float_list)
df.insert(1, "Simulation time", total_time_float_list, True)
df.insert(2, "Failed simulation", initornotlist, True)
summarized_filename = reportfilepath + 'analyzed/' + f"{fileprefix} summarized.csv"
df.to_csv(summarized_filename)

long_simulations = df.loc[df["Simulation time"] > 600]
normal_simulations = df.loc[df["Simulation time"] <= 600]
failed_simulations = df.loc[df["Failed simulation"] == True]
passed_simulations = df.loc[df["Failed simulation"] == False]

otherlist = ["Simulation_number", "Simulation time", "Failed simulation"]
input_variable_list = [colname for colname in list(df.columns) if "dummy" not in colname and colname not in otherlist]

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

    try:
        failed_mean = f'{float(f"{statistics.mean(failed_inputs):.3g}"):g}'
        passed_mean = f'{float(f"{statistics.mean(passed_inputs):.3g}"):g}'
    except:
        failed_mean = ''
        passed_mean = ''
    pass_mean_list.append(passed_mean)
    fail_mean_list.append(failed_mean)
    passfail_list.append((passed_mean, failed_mean))

    if len(set(failed_inputs)) == 1:
        almost_uniquely_failed_list.append(failed_inputs[0])
    else:
        almost_uniquely_failed_list.append("")
    uniquely_failed = [input for input in failed_inputs if input not in passed_inputs]
    # print(uniquely_failed)
    uniquely_failed_list.append(uniquely_failed)

    long_inputs = list(long_simulations[input_variable])
    normal_inputs = list(normal_simulations[input_variable])

    if len(set(long_inputs)) == 1:
        almost_uniquely_long_list.append(long_inputs[0])
    else:
        almost_uniquely_long_list.append("")
    long_mean = f'{float(f"{statistics.mean(long_inputs):.3g}"):g}'
    normal_mean = f'{float(f"{statistics.mean(normal_inputs):.3g}"):g}'

    long_mean_list.append(long_mean)
    normal_mean_list.append(normal_mean)
    timing_list.append((normal_mean, long_mean))

    uniquely_long = [input for input in long_inputs if input not in normal_inputs]
    uniquely_long_list.append(uniquely_long)

meta = pd.DataFrame(
    {
        "input_variable_list": input_variable_list,
        "pass_mean_list": pass_mean_list,
        "fail_mean_list": fail_mean_list,
        "normal_mean_list": normal_mean_list,
        "long_mean_list": long_mean_list,
        "almost_uniquely_failed_list": almost_uniquely_failed_list,
        "almost_uniquely_long_list": almost_uniquely_long_list,
        "uniquely_failed_list": uniquely_failed_list,
        "uniquely_long_list": uniquely_long_list,
    }
)
meta.to_csv(reportfilepath + 'analyzed/' + f"{fileprefix} timing divided.csv")


summarized = pd.read_csv(summarized_filename)
colnames = list(summarized.columns)
howmanydidntrun = 0
newarray = []
coltoplot = 2
yprime = summarized[colnames[coltoplot]]
yprime = list(yprime)

newarray.append(list(yprime))
for columname in colnames:
    print(columname)
    if columname not in colnames[0:4]:
        xprime = summarized[columname]
        xprime = list(xprime)

        y = []
        x = []
        for idx, val in enumerate(yprime):
            if val < 2000:
                y.append(val)
                x.append(xprime[idx])

        fig = plt.figure()
        plt.scatter(x, y)
        # plt.xscale('log')
        # plt.yscale('log')
        m, b = np.polyfit(x, y, deg=1)
        plt.axline(xy1=(0, b), slope=m, label=f'$y = {m:.1f}x {b:+.1f}$')
        plt.ylabel(colnames[coltoplot])
        plt.xlabel(columname)
        # plt.show(block=False)
        fig.savefig(reportfilepath + "analyzed/" + f'pngs/scatter {columname}.png')
        newarray.append(list(y))

        xy = pd.DataFrame([x, y]).T
        xy.columns = ['x', 'y']
        yhigh = xy['y'][xy['x'] > np.mean(xy['x'])]
        ylow = xy['y'][xy['x'] < np.mean(xy['x'])]

        fig = plt.figure()
        _, bins, _ = plt.hist(yhigh, bins=75)
        _ = plt.hist(ylow, bins=bins, alpha=0.5)
        plt.xlabel(colnames[coltoplot])
        plt.ylabel(columname)
        # plt.show()
        fig.savefig(reportfilepath + "analyzed/" + f'pngs/hist {columname}.png')

x = summarized[colnames[1]]
plt.figure()
plt.hist(x)
plt.show(block=False)


df = pd.DataFrame(newarray)
df = df.T
df_norm_col = (df - df.mean()) / df.std()

plt.figure()
ax = sns.heatmap(df_norm_col, linewidth=0.5)
plt.show(block=False)

# c = ax.pcolormesh(x, y, z, cmap='RdBu', vmin=z_min, vmax=z_max)

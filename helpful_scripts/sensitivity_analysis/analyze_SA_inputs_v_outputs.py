# flake8: noqa
#  type: ignore
import os
import json
import pandas as pd
from typing import Dict, Any, List
import statistics
from model_evaluation.sensitivity_analysis import SA_helpers
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import json

# from itertools import combinations, chain
# import time
# import gc

config_json_filename = "model_evaluation/sensitivity_analysis/SA_analyze.json"
with open(config_json_filename) as json_file:
    config_json = json.load(json_file)

analysis = config_json["analyses"][0]

input_file = analysis["input_file"]
output_path = analysis["output_path"] + "reports/"
report_name = analysis["report_name"]
fileprefix = analysis["analysis_prefix"]

with open(input_file) as json_file:
    input_config = json.load(json_file)

task_to_analyze: Dict[str, Any] = input_config["tasks"][0]

parsed_SA_input_variables = SA_helpers.parse_input_variables(task_to_analyze)
sampled_values = SA_helpers.get_sampled_values(task_to_analyze, parsed_SA_input_variables)

total_num_files = len(sampled_values)

all_report_filenames = SA_helpers.get_all_output_files(
        basedirectory=output_path, output_prefix=fileprefix, report_name=report_name
    )
basedirectory=output_path
all_report_filenames=all_report_filenames
total_num_files=total_num_files


raw_collated = SA_helpers.collate_raw(basedirectory, all_report_filenames, total_num_files)

target = max([len(raw_collated[thing]) for thing in raw_collated])
raw_collated_filtered = {}
for thing in raw_collated:
    if len(raw_collated[thing]) != target:
        pass
    else:
        raw_collated_filtered[thing] = raw_collated[thing]

raw_collated_pd = pd.DataFrame(raw_collated_filtered)

rawcollatedfilenameout = output_path + 'analyzed/' + fileprefix + " raw collated.csv"
raw_collated_pd.to_csv(rawcollatedfilenameout)


# read the CSV
input_list = output_path + "analyzed/" + f"{fileprefix}_inputs.csv"
input_list_read = pd.read_csv(input_list)
# add the index for each, 0-X is a columns for run
input_list_read_pd = pd.DataFrame(input_list_read)

# PLOTTING IN PROGRESS BELOW
list_of_inputs = list(input_list_read_pd.columns)
list_of_outputs = list(raw_collated_pd.columns)

pd.DataFrame(list_of_inputs).to_csv(output_path + "analyzed/FOR_PLOTS_list_of_inputs.csv")
pd.DataFrame(list_of_outputs).to_csv(output_path + "analyzed/FOR_PLOTS_list_of_outputs.csv")

inputlist = [0, 1, 2, 5, 14, 15, 16]
outputlist = [0, 1, 2, 3, 15, 16, 24, 25, 26, 31, 37, 39, 53, 54, 55, 56, 57, 58, 59, 60,
              64, 65, 66, 67, 68, 69, 73, 97]

for i in inputlist:
    for j in outputlist:
        input_of_choice = list_of_inputs[i]
        output_of_choice = list_of_outputs[j]
        print(input_of_choice)
        print(output_of_choice)

        y = raw_collated_pd[output_of_choice]
        x = input_list_read_pd[input_of_choice]

        fig = plt.figure()
        plt.scatter(x, y)
        # plt.xscale('log')
        # plt.yscale('log')
        m, b = np.polyfit(x, y, deg=1)
        plt.axline(xy1=(0, b), slope=m, label=f'$y = {m:.1f}x {b:+.1f}$')
        plt.ylabel(output_of_choice)
        plt.xlabel(input_of_choice)
        # plt.show(block=False)
        fig.savefig(output_path + f'analyzed/pngs/scatter {input_of_choice.replace("/","")} v {output_of_choice.replace("/","")}.png')

# xy = pd.DataFrame([x, y]).T
# xy.columns = ['x', 'y']
# yhigh = xy['y'][xy['x'] > np.mean(xy['x'])]
# ylow = xy['y'][xy['x'] < np.mean(xy['x'])]

# fig = plt.figure()
# _, bins, _ = plt.hist(yhigh, bins=75)
# _ = plt.hist(ylow, bins=bins, alpha=0.5)
# plt.xlabel(colnames[1])
# plt.ylabel(columname)
# # plt.show()
# fig.savefig(output_path + f'analyzed/pngs/hist {columname}.png')
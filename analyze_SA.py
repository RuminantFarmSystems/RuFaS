import csv
import json
import pandas as pd
# import numpy as np
from typing import Dict, Any
from model_evaluation.sensitivity_analysis import SA_helpers


import matplotlib.pyplot as plt
import numpy as np

config_json_filename = "model_evaluation/sensitivity_analysis/SA_analyze.json"
with open(config_json_filename) as json_file:
    config_json = json.load(json_file)

for analysis in config_json['analyses']:
    print(analysis)
    input_file = analysis["input_file"]
    output_path = analysis["output_path"]
    report_name = analysis["report_name"]
    only_inputs = analysis["only_inputs"]
    plot_whole_new = analysis["plot_whole_new"]

    inputs_to_collate = analysis["inputs_to_collate"]
    plot_inputs = analysis["plot_inputs"]
    outputs_to_collate = analysis["outputs_to_collate"]
    plot_outputs = analysis["plot_outputs"]

    with open(input_file) as json_file:
        input_config = json.load(json_file)

    task_to_analyze: Dict[str, Any] = input_config['tasks'][0]
    output_prefix = task_to_analyze['output_prefix']
    sampler = task_to_analyze["sampler"]

    parsed_SA_input_variables = SA_helpers.parse_input_variables(task_to_analyze)
    sampled_values = SA_helpers.get_sampled_values(task_to_analyze,
                                                   parsed_SA_input_variables)
    total_num_files = len(sampled_values)
    if only_inputs:
        print("true")
        namesfornames = [name for name in parsed_SA_input_variables["names"]]
        print(namesfornames)
        with open(output_path + output_prefix + "_inputs.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(namesfornames)
            writer.writerows(sampled_values)
        break
    print("didn't break")
    all_report_filenames = SA_helpers.get_all_output_files(
        basedirectory=output_path,
        output_prefix=output_prefix,
        report_name=report_name
    )

    collated_outputs = SA_helpers.collate_outputs(
        basedirectory=output_path,
        all_report_filenames=all_report_filenames,
        total_num_files=total_num_files
    )

    whole_output = SA_helpers.get_whole_output(collated_outputs,
                                               sampled_values,
                                               task_to_analyze,
                                               parsed_SA_input_variables)
    with open(output_path + output_prefix + "_whole analysis.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(whole_output)

    new_whole_output = SA_helpers.get_new_whole_output(whole_output)
    with open(output_path + output_prefix + "_new whole analysis.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_whole_output)

    for input in inputs_to_collate:
        new_whole_output_pd = pd.DataFrame(new_whole_output)
        column_names = new_whole_output_pd.iloc[0]
        row_names = new_whole_output_pd[0]
        new_whole_output_pd = new_whole_output_pd.iloc[1:, 1:]
        new_whole_output_pd.columns = column_names[1:]
        new_whole_output_pd.index = row_names[1:]
        new_whole_output_pd = new_whole_output_pd.loc[:, ~new_whole_output_pd.columns.duplicated(keep="last")]

        if sampler == "fractional_factorial":
            # get the input column starts with ME:
            input_col = new_whole_output_pd["ME:" + input]

            # get the total column sum of all that include it and start with IE:
            IEnames = [name for name in column_names if input in name and "IE:" in name]
            IEtable = new_whole_output_pd[IEnames]

            IEsums = IEtable.sum(axis=1)
            IEsums.columns = ["IE"]

            total_effect = IEsums + input_col
            threethings = pd.concat([input_col, IEsums, total_effect], axis=1)
            threethings.rename({0: "interaction_effects", 1: "total_effects"}, axis=1, inplace=True)

            newcols = []
            for rowname in row_names[1:]:
                print(rowname)
                # get the list of inputs (X)
                input_reformatted = input.replace(" ", ".")
                input_index = parsed_SA_input_variables["names"].index(input_reformatted)
                input_values = [value[input_index] for value in sampled_values]
                # get the list of outputs (Y)
                output_values = collated_outputs[rowname]
                slope, r2_value, p_value = SA_helpers.regression_stuff(
                    X=input_values, xname=input, Y=output_values, yname=rowname, plot_inputs=plot_inputs
                )
                newcols.append([slope, r2_value, p_value])
            newcols_pd = pd.DataFrame(newcols)
            newcols_pd.index = new_whole_output_pd.index

            output_pd = pd.concat([threethings, newcols_pd], axis=1)
            output_pd.sort_values(by="total_effects", axis=0, ascending=False, inplace=True)
            output_pd.rename({0: "slope", 1: "r2_value", 2: "p_value"}, axis=1, inplace=True)
            filenameout = output_path + output_prefix + input + "_summarytable.csv"
            output_pd.to_csv(filenameout)

        elif (sampler == "sobol" or sampler == "saltelli_sobol"):
            # get the input column main effect: starts with S1:
            input_col = new_whole_output_pd["S1:" + input]
            total_effect = new_whole_output_pd["ST:" + input]
            interaction_effects = total_effect - input_col
            threethings = pd.concat([input_col, interaction_effects, total_effect], axis=1)
            threethings.rename({0: "interaction_effects", threethings.columns[-1]: "total_effects"}, axis=1, inplace=True)

            newcols = []
            for rowname in row_names[1:]:
                print(rowname)
                # get the list of inputs (X)
                input_reformatted = input.replace(" ", ".")
                input_index = parsed_SA_input_variables["names"].index(input_reformatted)
                input_values = [value[input_index] for value in sampled_values]
                # get the list of outputs (Y)
                output_values = collated_outputs[rowname]
                slope, r2_value, p_value = SA_helpers.regression_stuff(
                    X=input_values, xname=input, Y=output_values, yname=rowname, plot_inputs=plot_inputs
                )
                newcols.append([slope, r2_value, p_value])
            newcols_pd = pd.DataFrame(newcols)
            newcols_pd.index = new_whole_output_pd.index

            output_pd = pd.concat([threethings, newcols_pd], axis=1)
            output_pd.sort_values(by="total_effects", axis=0, ascending=False, inplace=True)
            output_pd.rename({0: "slope", 1: "r2_value", 2: "p_value"}, axis=1, inplace=True)
            filenameout = output_path + output_prefix + input + "_summarytable.csv"
            output_pd.to_csv(filenameout)
        # get the total column starts with ST:
        # determine the order
        # assign rank for each - based on total
        # reorder the inputs based on their rank
        # add in the single effect column

        # run a simple linear regression, add slope, R2, and p to each
        if plot_inputs:
            # plot the input
            pass
        pass

    if plot_whole_new:
        SA_helpers.plot_whole_new(output_path=output_path,
                                  output_prefix=output_prefix)

print('did all the stuff!')

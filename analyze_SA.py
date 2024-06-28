import csv
import json
import pandas as pd
# import numpy as np
from typing import Dict, Any
from model_evaluation.sensitivity_analysis import SA_helpers


config_json_filename = "model_evaluation/sensitivity_analysis/SA_analyze.json"
with open(config_json_filename) as json_file:
    config_json = json.load(json_file)

for analysis in config_json['analyses']: # noqa
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

    if inputs_to_collate or outputs_to_collate:
        new_whole_output_pd = pd.DataFrame(new_whole_output)
        column_names = new_whole_output_pd.iloc[0]
        row_names = new_whole_output_pd[0]
        new_whole_output_pd = new_whole_output_pd.iloc[1:, 1:]
        new_whole_output_pd.columns = column_names[1:]
        new_whole_output_pd.index = row_names[1:]
        new_whole_output_pd = new_whole_output_pd.loc[:, ~new_whole_output_pd.columns.duplicated(keep="last")]
        column_names = list(new_whole_output_pd.columns)

    for input in inputs_to_collate:
        if sampler == "fractional_factorial":
            # get the input column starts with ME:
            main_effects = new_whole_output_pd["ME:" + input]

            # get the total column sum of all that include it and start with IE:
            IEnames = [name for name in column_names if input in name and "IE:" in name]
            IEtable = new_whole_output_pd[IEnames]

            IEsums = IEtable.sum(axis=1)
            IEsums.columns = ["IE"]

            total_effect = IEsums + main_effects
            threethings = pd.concat([main_effects, IEsums, total_effect], axis=1)
            threethings.rename({0: "interaction_effects", 1: "total_effects"}, axis=1, inplace=True)
        elif (sampler == "sobol" or sampler == "saltelli_sobol"):
            # get the input column main effect: starts with S1:
            main_effects = new_whole_output_pd["S1:" + input]
            total_effect = new_whole_output_pd["ST:" + input]
            interaction_effects = total_effect - main_effects
            threethings = pd.concat([main_effects, interaction_effects, total_effect], axis=1)
            threethings.rename({0: "interaction_effects",
                               threethings.columns[-1]: "total_effects"},
                               axis=1, inplace=True)
        elif (sampler == "morris"):
            mu = new_whole_output_pd["mu:" + input]
            total_effects = new_whole_output_pd["mu_star:" + input]
            sigma = new_whole_output_pd["sigma:" + input]
            mu_st_conf = new_whole_output_pd["mu_st_conf:" + input]
            threethings = pd.concat([mu, total_effects, sigma, mu_st_conf], axis=1)
            threethings.rename(
                {
                    threethings.columns[0]: "mu",
                    threethings.columns[1]: "total_effects",
                    threethings.columns[2]: "sigma",
                    threethings.columns[3]: "mu_st_conf",
                },
                axis=1,
                inplace=True,
            )

        newcols = []
        for rowname in row_names[1:]:
            # get the list of inputs (X)
            input_reformatted = input.replace(" ", ".")
            input_reformatted2 = input.replace(" ", ".").replace("ME:", "").replace("S1:", "")

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

        minmax = pd.DataFrame([(name['lower_bound'], name['upper_bound'])
                               for name in task_to_analyze['SA_input_variables']
                               if name['variable_name'] == input_reformatted2])
        output_pd = pd.concat([threethings, newcols_pd], axis=1)
        output_pd.rename({output_pd.columns[0]: output_pd.columns[0] + str(minmax.iloc[0].values)},
                         axis=1, inplace=True)
        output_pd.sort_values(by="total_effects", axis=0, ascending=False, inplace=True)
        output_pd.rename({0: "slope", 1: "r2_value", 2: "p_value"}, axis=1, inplace=True)
        filenameout = output_path + output_prefix + "_inputs_META_" + input + "_summarytable.csv"
        output_pd.to_csv(filenameout)

    # here for a single output, we sort and explore all the inputs
    for output in outputs_to_collate:

        just_output = pd.DataFrame(new_whole_output_pd.loc[output])
        MEnames = [name for name in column_names if "ME:" in name or "S1:" in name or "mu_star" in name]
        temp_output = just_output.loc[MEnames]

        # get the input column starts with ME:
        # MEnames = [name for name in column_names if "ME:" in name]
        # main_effects = new_whole_output_pd[MEnames].loc[output]

        # get the total column sum of all that include it and start with IE:
        interaction_effects = []
        total_effects = []
        for MEname in MEnames:
            if sampler == "fractional_factorial":
                IEnames_temp = [
                    name
                    for name in column_names
                    if MEname.replace(".", " ").replace("ME:", "") in name and "IE:" in name
                ]
                IEtable = just_output.loc[IEnames_temp]
                interaction_effects.append(IEtable.sum(axis=0).values[0])
                total_effects.append(interaction_effects[-1] + just_output.loc[MEname].values[0])
            elif sampler == "sobol" or sampler == "saltelli":
                total_effects.append(just_output.loc[MEname.replace("S1:", "ST:")].values[0])
                interaction_effects.append(total_effects[-1] - just_output.loc[MEname].values)
            else:
                total_effects.append(just_output.loc[MEname].values[0])
                interaction_effects.append(just_output.loc[MEname.replace("mu_star:", "sigma:")].values[0])

        inteffs = pd.DataFrame(interaction_effects)
        inteffs.index = temp_output.index
        inteffs.rename({0: "interaction_effects"}, axis=1, inplace=True)
        toteffs = pd.DataFrame(total_effects)
        toteffs.index = temp_output.index
        toteffs.rename({0: "total_effects"}, axis=1, inplace=True)

        # get ranges
        variable_names = [name['variable_name'] for name in task_to_analyze['SA_input_variables']]
        bounds = [(name['lower_bound'], name['upper_bound'])
                  for name in task_to_analyze['SA_input_variables']]

        output_temp = pd.concat([temp_output, inteffs, toteffs], axis=1)

        input_names = [name for name in output_temp.index]
        bounds2 = []
        newcols = []
        for input_name in input_names:
            input_reformatted = input_name.replace(" ", ".").replace("ME:", "").replace("S1:", "").replace("mu_star:",
                                                                                                           "")
            if input_reformatted in variable_names:
                idx = variable_names.index(input_reformatted)
                bounds2.append(bounds[idx])
            # Append the output for that input to the single_output
            input_index = parsed_SA_input_variables["names"].index(input_reformatted)
            input_values = [value[input_index] for value in sampled_values]
            # get the list of outputs (Y)
            output_values = collated_outputs[output]
            slope, r2_value, p_value = SA_helpers.regression_stuff(
                X=input_values, xname=input, Y=output_values, yname=output, plot_inputs=plot_inputs)
            newcols.append([slope, r2_value, p_value])
        newcols_pd = pd.DataFrame(newcols)
        bounds2_pd = pd.DataFrame(bounds2)
        bounds2_pd.rename({0: "input_min", 1: "input_max"}, axis=1, inplace=True)
        bounds2_pd.index = output_temp.index[0:len(bounds2)]  # TODO
        # the previous line might need to be reverted to remove the info in hard brackets
        newcols_pd.index = output_temp.index
        output_pd = pd.concat([bounds2_pd, output_temp, newcols_pd], axis=1)
        output_pd.sort_values(by="total_effects", axis=0, ascending=False, inplace=True)
        output_pd.rename({0: "slope", 1: "r2_value", 2: "p_value"}, axis=1, inplace=True)
        output_reformatted = output.replace('/', ' per ')
        filenameout = output_path + output_prefix + "_outputs_META_" + output_reformatted + "_summarytable.csv"
        output_pd.to_csv(filenameout)

    if plot_whole_new:
        SA_helpers.plot_whole_new(output_path=output_path,
                                  output_prefix=output_prefix)

print('did all the stuff!')

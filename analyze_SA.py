import csv
import json
# import pandas as pd
# import numpy as np
from typing import Dict, Any
from model_evaluation.sensitivity_analysis import SA_helpers

config_json_filename = "model_evaluation/sensitivity_analysis/SA_analyze.json"
with open(config_json_filename) as json_file:
    config_json = json.load(json_file)

for analysis in config_json['analyses']:
    input_file = analysis["input_file"]
    output_path = analysis["output_path"]
    report_name = analysis["report_name"]
    plot_whole_new = analysis["plot_whole_new"]
    only_inputs = analysis["only_inputs"]

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

    if plot_whole_new:
        SA_helpers.plot_whole_new(output_path=output_path,
                                  output_prefix=output_prefix)

print('did all the stuff!')

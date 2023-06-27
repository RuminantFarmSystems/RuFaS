"""
"""
import json
import model_evaluation.sensitivity_analysis.sensitivity_analysis_helpers as SAH

# load config json
with open('model_evaluation/sensitivity_analysis_example_1.json', 'r') as f:
    config_json = json.load(f)

input_files_to_modify = config_json["input_files_to_modify"]

# internally generate the numbers from the config, using the same methods
output_variables_of_interest = config_json["output_variables_of_interest"]

# then compare against the output_variables_of_interest


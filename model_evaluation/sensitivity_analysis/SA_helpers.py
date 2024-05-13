import os
# import csv
# import json
import pandas as pd
import numpy as np

from typing import List, Dict, Any

from SALib.sample import ff as fractional_factorial_sampler
from SALib.sample import saltelli as saltelli_sampler
from SALib.sample import sobol as sobol_sampler
from SALib.analyze import sobol as sobol_analyzer
from SALib.analyze import ff as ff_analyzer
# from SALib.test_functions import Ishigami


def rewrite_ff_analysis(analysis: Dict[str, Any]) -> List[Any]:
    """
    This reformats the output of the ff_analysis function
    Forces into something easier to parse into csvs for printing
    This will place the main effects and interaction effects into grouped columns in a single dataframe
    """
    intnames = analysis["interaction_names"]
    intnames = [str(x).replace("(", "") for x in intnames]
    intnames = [str(x).replace(")", "") for x in intnames]
    intnames = [str(x).replace(",", "*") for x in intnames]
    intnames = [str(x).replace(" ", "") for x in intnames]
    colnames = ["ME:" + x for x in analysis["names"]] + ["IE:" + str(x) for x in intnames]
    rowvalues = list(analysis["ME"]) + list(analysis["IE"])
    analysis_out = [colnames, rowvalues]
    return analysis_out


def rewrite_sobol_analysis(analysis: Dict[str, Any], p: Dict[str, Any]) -> List[Any]:
    """
    This reformats the output of the ff_sobol function
    Forces into something easier to parse into csvs for printing
    This will place the main effects and interaction effects into grouped columns in a single dataframe
    """
    intnames = p["names"]
    colnames = (
        ["S1:" + x for x in intnames]
        + ["ST:" + str(x) for x in intnames]
        + ["S2:" + str(x) for x in intnames]
        + ["S1_conf:" + x for x in intnames]
        + ["ST_conf:" + str(x) for x in intnames]
        + ["S2_conf:" + str(x) for x in intnames]
    )
    rowvalues = (
        list(analysis["S1"])
        + list(analysis["ST"])
        + list(analysis["S2"])
        + list(analysis["S1_conf"])
        + list(analysis["ST_conf"])
        + list(analysis["S2_conf"])
    )
    len(rowvalues)
    rowvalues[21]

    analysis_out = [colnames, rowvalues]
    return analysis_out


def get_all_output_files(basedirectory: str, output_prefix: str, report_name: str) -> List[str]:
    return [
        filename
        for filename in os.listdir(basedirectory)
        if filename.startswith(output_prefix) and report_name in filename
    ]


def collate_outputs(basedirectory: str,
                    all_report_filenames: List[str],
                    total_num_files: int) -> Dict[str, List[float]]:
    collected: Dict[str, List[float]] = {}
    digits = len(str(total_num_files))

    for i in range(0, total_num_files):
        file_ID = f"{i+1}".zfill(digits) + "_"
        file_ID_found = [filename for filename in all_report_filenames if file_ID in filename][-1]
        file = pd.read_csv(basedirectory + file_ID_found)
        variable_names: List[str] = []
        if not variable_names:
            variable_names = list(file.columns)
        for variable_name in variable_names:
            if variable_name not in collected.keys():
                collected[variable_name] = []
            valuetoappend = file[variable_name].values[0]
            if type(valuetoappend) is not str:
                valuetoappend = float(valuetoappend)
                collected[variable_name].append(valuetoappend)
    return collected


def analyze_it(
    task_specified: Dict[str, Any],
    parsed_SA_input_variables: Dict[str, Any],
    sampled_values: np.ndarray[Any],
    output_to_analyze: List[float],
) -> List[Any]:
    print_analysis = False
    if task_specified["sampler"] == "sobol":
        analyzed = sobol_analyzer.analyze(parsed_SA_input_variables,
                                          np.array(output_to_analyze),
                                          print_to_console=print_analysis,
                                          seed=task_specified["random_seed"]
                                          )
        analyzed_formatted = rewrite_sobol_analysis(analyzed, parsed_SA_input_variables)
    elif task_specified["sampler"] == "saltelli_sobol":
        analyzed = sobol_analyzer.analyze(parsed_SA_input_variables,
                                          np.array(output_to_analyze),
                                          print_to_console=print_analysis,
                                          seed=task_specified["random_seed"]
                                          )
        analyzed_formatted = rewrite_sobol_analysis(analyzed, parsed_SA_input_variables)
    else:
        analyzed = ff_analyzer.analyze(
            parsed_SA_input_variables,
            sampled_values,
            output_to_analyze,
            second_order=True,
            seed=task_specified["random_seed"],
            print_to_console=print_analysis
        )
        analyzed_formatted = rewrite_ff_analysis(analyzed)
    return analyzed_formatted


def get_sampled_values(task_to_analyze: Dict[str, Any],
                       parsed_SA_input_variables: Dict[str, Any]) -> np.ndarray | Any:
    if task_to_analyze["sampler"] == "sobol":
        sampled_values = sobol_sampler.sample(
            parsed_SA_input_variables,
            task_to_analyze["saltelli_number"],
            skip_values=task_to_analyze["saltelli_skip"],
            seed=task_to_analyze["random_seed"]
        )
    elif task_to_analyze["sampler"] == "saltelli_sobol":
        sampled_values = saltelli_sampler.sample(
            parsed_SA_input_variables,
            task_to_analyze["saltelli_number"],
            skip_values=task_to_analyze["saltelli_skip"],
        )
    else:
        sampled_values = fractional_factorial_sampler.sample(
            parsed_SA_input_variables,
        )
    return sampled_values


def parse_input_variables(task_to_analyze: Dict[str, Any]) -> Dict[str, Any]:
    SA_input_variables: List[Dict[str, float | str]] = task_to_analyze["SA_input_variables"]
    names: List[str] = [str(input_variable["variable_name"]) for input_variable in SA_input_variables]
    variables_count = len(names)
    bounds: List[List[float]] = [
        [float(input_variable["lower_bound"]), float(input_variable["upper_bound"])]
        for input_variable in SA_input_variables
    ]
    parsed_SA_input_variables = {
        "num_vars": variables_count,
        "names": names,
        "bounds": bounds,
        "sample_scaled": True,
    }
    return parsed_SA_input_variables


def get_whole_output(
    collated_outputs: Dict[str, Any],
    sampled_values: np.ndarray | Any,
    task_to_analyze: Dict[str, Any],
    parsed_SA_input_variables: Dict[str, Any],
) -> List[Any]:
    whole_output: List[Any] = []
    for variable_name_for_analysis in list(collated_outputs.keys()):
        output_as_list = collated_outputs[variable_name_for_analysis]
        if len(output_as_list) == len(sampled_values):
            out = analyze_it(task_to_analyze,
                             parsed_SA_input_variables,
                             sampled_values,
                             output_as_list)
            # outdf = pd.DataFrame(out)
            # prettier_variable_name = variable_name_for_analysis.replace("/", " per ")
            # prettier_variable_name = prettier_variable_name.replace(",", " ")
            # outdf.to_csv(path_or_buf=basedirectory + output_prefix + '_' + prettier_variable_name + '.csv')
            if not whole_output:
                names_and_header = ['']
                for name in out[0]:
                    names_and_header.append(name)
                whole_output.append(names_and_header)
            line_for_whole_output = []
            line_for_whole_output.append(variable_name_for_analysis)
            for thing in out[1]:
                line_for_whole_output.append(thing)
            whole_output.append(line_for_whole_output)
    return whole_output


def get_new_whole_output(whole_output: List[Any]) -> List[Any]:
    new_whole_output: List[Any] = []
    updated_names = []
    for item in whole_output[0]:
        updated_names.append(item.replace(".", " "))
    new_whole_output.append(updated_names)
    for line_num in range(1, len(whole_output)):
        reformatted_line = []
        for item in whole_output[line_num]:
            if type(item) is float or type(item) is np.float64:
                if item < 0.01:
                    item = 0
            reformatted_line.append(item)
        new_whole_output.append(reformatted_line)
    return new_whole_output

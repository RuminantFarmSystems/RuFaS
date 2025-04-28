# flake8: noqa
import os

# import csv
# import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from typing import List, Dict, Any

from SALib.sample import ff as fractional_factorial_sampler
from SALib.sample import saltelli as saltelli_sampler
from SALib.sample import sobol as sobol_sampler
from SALib.sample import morris as morris_sampler
from SALib.analyze import ff as ff_analyzer
from SALib.analyze import sobol as sobol_analyzer
from SALib.analyze import morris as morris_analyzer

# from SALib.test_functions import Ishigami
# from sklearn import datasets, linear_model
# from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm

# from scipy import stats


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
    This reformats the output of the sobol function
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
    analysis_out = [colnames, rowvalues]

    expanded_names = [str(x) for x in intnames]
    interaction_names = []
    for _ in expanded_names:
        for pos, name in enumerate(expanded_names):
            interaction_names.append(f"{name} * {expanded_names[pos]}")

    interaction_values = []
    as2 = analysis["S2"]
    for a in as2:
        # print(a)
        for i in a:
            # print(i)
            interaction_values.append(i)

    colnames_expanded = (
        ["S1:" + x for x in intnames]
        + ["ST:" + str(x) for x in intnames]
        + interaction_names
        + ["S1_conf:" + x for x in intnames]
        + ["ST_conf:" + str(x) for x in intnames]
        + ["S2_conf:" + str(x) for x in intnames]
    )
    rowvalues_expanded = (
        list(analysis["S1"])
        + list(analysis["ST"])
        + interaction_values
        + list(analysis["S1_conf"])
        + list(analysis["ST_conf"])
        + list(analysis["S2_conf"])
    )
    analysis_out_expanded = [colnames_expanded, rowvalues_expanded]

    return analysis_out_expanded


def rewrite_morris_analysis(analysis: Dict[str, Any], p: Dict[str, Any]) -> List[Any]:
    """
    This reformats the output of the morris function
    Forces into something easier to parse into csvs for printing
    This will place the main effects and interaction effects into grouped columns in a single dataframe
    """
    intnames = p["names"]
    colnames = (
        ["mu:" + x for x in intnames]
        + ["mu_star:" + x for x in intnames]
        + ["sigma:" + str(x) for x in intnames]
        + ["mu_st_conf:" + str(x) for x in intnames]
    )
    rowvalues = (
        list(analysis["mu"]) + list(analysis["mu_star"]) + list(analysis["sigma"]) + list(analysis["mu_st_conf"])
    )

    analysis_out = [colnames, rowvalues]
    return analysis_out


def get_all_output_files(basedirectory: str, output_prefix: str, report_name: str) -> List[str]:
    return [
        filename
        for filename in os.listdir(basedirectory)
        if filename.startswith(output_prefix) and report_name in filename
    ]


def collate_outputs(
    basedirectory: str, all_report_filenames: List[str], total_num_files: int
) -> Dict[str, List[float]]:
    collected: Dict[str, List[float]] = {}
    digits = len(str(total_num_files))

    for i in range(0, total_num_files):
        file_ID = f"{i+1}".zfill(digits) + "_"
        try:
            file_ID_found = [filename for filename in all_report_filenames if file_ID in filename][-1]
        except:
            file_ID_backup = f"{1}".zfill(digits) + "_"
            file_ID_found = [filename for filename in all_report_filenames if file_ID_backup in filename][-1]
            print("used dummy")
            print(i / total_num_files)
            print(i)
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
    sampled_values: np.ndarray[Any, Any],
    output_to_analyze: List[float],
) -> List[Any]:
    print_analysis = False
    if task_specified["sampler"] == "sobol":
        analyzed = sobol_analyzer.analyze(
            parsed_SA_input_variables,
            np.array(output_to_analyze),
            print_to_console=print_analysis,
            seed=task_specified["random_seed"],
        )
        analyzed_formatted = rewrite_sobol_analysis(analyzed, parsed_SA_input_variables)
    elif task_specified["sampler"] == "saltelli":
        analyzed = sobol_analyzer.analyze(
            parsed_SA_input_variables,
            np.array(output_to_analyze),
            print_to_console=print_analysis,
            seed=task_specified["random_seed"],
        )
        analyzed_formatted = rewrite_sobol_analysis(analyzed, parsed_SA_input_variables)
    elif task_specified["sampler"] == "morris":
        analyzed = morris_analyzer.analyze(
            parsed_SA_input_variables,
            sampled_values,
            np.array(output_to_analyze),
            print_to_console=print_analysis,
            seed=task_specified["random_seed"],
        )
        analyzed_formatted = rewrite_morris_analysis(analyzed, parsed_SA_input_variables)
    else:
        analyzed = ff_analyzer.analyze(
            parsed_SA_input_variables,
            sampled_values,
            output_to_analyze,
            second_order=True,
            seed=task_specified["random_seed"],
            print_to_console=print_analysis,
        )
        analyzed_formatted = rewrite_ff_analysis(analyzed)
    return analyzed_formatted


def get_sampled_values(task_to_analyze: Dict[str, Any], parsed_SA_input_variables: Dict[str, Any]) -> np.ndarray | Any:
    if task_to_analyze["sampler"] == "sobol":
        sampled_values = sobol_sampler.sample(
            parsed_SA_input_variables,
            task_to_analyze["sampler_n"],
            skip_values=task_to_analyze["skip_values"],
            seed=task_to_analyze["random_seed"],
        )
    elif task_to_analyze["sampler"] == "saltelli_sobol":
        sampled_values = saltelli_sampler.sample(
            parsed_SA_input_variables,
            task_to_analyze["sampler_n"],
            skip_values=task_to_analyze["skip_values"],
        )
    elif task_to_analyze["sampler"] == "morris":
        sampled_values = morris_sampler.sample(
            parsed_SA_input_variables,
            task_to_analyze["sampler_n"],
            seed=task_to_analyze["random_seed"],
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
            out = analyze_it(task_to_analyze, parsed_SA_input_variables, sampled_values, output_as_list)
            # outdf = pd.DataFrame(out)
            # prettier_variable_name = variable_name_for_analysis.replace("/", " per ")
            # prettier_variable_name = prettier_variable_name.replace(",", " ")
            # outdf.to_csv(path_or_buf=basedirectory + output_prefix + '_' + prettier_variable_name + '.csv')
            if not whole_output:
                names_and_header = [""]
                for name in out[0]:
                    names_and_header.append(name)
                whole_output.append(names_and_header)
            line_for_whole_output = []
            line_for_whole_output.append(variable_name_for_analysis)
            for thing in out[1]:
                line_for_whole_output.append(thing)
            whole_output.append(line_for_whole_output)

    colidx = []
    colidx.append(999)
    for column in range(1, len(whole_output[0])):
        colidx.append(0)
        for row in range(1, len(whole_output)):
            val = whole_output[row][column]
            if type(val) == np.ndarray or str(val) == "nan":
                pass
            else:
                colidx[column] += 1

    whole_output_expanded = []
    for row in whole_output:
        whole_output_expanded.append([row[i] for i in range(len(row)) if colidx[i]])

    # print(len(whole_output))
    # print(len(whole_output[0]))
    # print(len(whole_output_expanded))
    # print(len(whole_output_expanded[0]))

    return whole_output_expanded


def get_new_whole_output(whole_output: List[Any]) -> List[Any]:
    new_whole_output: List[Any] = []
    updated_names = []
    for item in whole_output[0]:
        updated_name = item.replace(".", " ")
        updated_name = updated_name.replace("'", "")
        updated_name = updated_name.replace("*", " X ")
        updated_names.append(updated_name)
    new_whole_output.append(updated_names)
    for line_num in range(1, len(whole_output)):
        reformatted_line = []
        for item in whole_output[line_num]:
            if type(item) is float or type(item) is np.float64:
                if item < 0.001:
                    item = 0
            reformatted_line.append(item)
        new_whole_output.append(reformatted_line)
    return new_whole_output


def plot_whole_new(
    output_path: str,
    output_prefix: str,
) -> None:
    whole_new_output_report = pd.read_csv(output_path + output_prefix + "_new whole analysis.csv", index_col=0)
    # ,
    #     names=0, encoding='utf-8'
    # )

    df = pd.DataFrame(whole_new_output_report)
    df_trimmed = df.select_dtypes(include=["float"])
    # df_trimmed = df.drop(df.columns[99:], axis=1)

    plt.figure()
    sns.heatmap(df_trimmed, annot=True)
    # plt.show(block=False)
    plt.savefig(output_path + output_prefix + "whole_new_heatmap.jpg")
    plt.close()


def regression_stuff(X: List[float], xname: str, Y: List[float], yname: str, plot_inputs: bool) -> Any:
    # Create linear regression object
    # regr = linear_model.LinearRegression()

    # X = input_values
    # Y = output_values

    # # diabetes = datasets.load_diabetes()
    # # X = diabetes.data
    # y = diabetes.target

    X2 = sm.add_constant(X)
    est = sm.OLS(Y, X2)
    est2 = est.fit()
    print(est2.summary())
    R2_etc = est2.summary2().tables[0]
    r2_value = R2_etc[3][0]
    p_etc = est2.summary2().tables[1]
    intercept_value = p_etc["Coef."]["const"]
    slope = p_etc["Coef."]["x1"]
    p_value = p_etc["P>|t|"]["x1"]

    # X = np.array(X).reshape(-1,1)
    # Y = np.array(Y)
    # # Train the model using the training sets
    # regr.fit(X, Y)

    # # Make predictions using the testing set
    # y_pred = regr.predict(X)

    # # The coefficients
    # print("Coefficients: \n", regr.coef_)
    # # The mean squared error
    # print("Mean squared error: %.2f" % mean_squared_error(Y, y_pred))
    # # The coefficient of determination: 1 is perfect prediction
    # r2 = r2_score(Y, y_pred)
    # print("Coefficient of determination: %.2f" % r2)

    if plot_inputs:
        # Plot outputs
        fig, ax = plt.subplots()
        plt.scatter(X, Y, color="black")
        ax.axline((0, intercept_value), slope=slope)
        ax.set_xlim(min(X) * 0.99, max(X) * 1.01)

        # plt.xticks(())
        # plt.yticks(())
        plt.xlabel(xname)
        plt.ylabel(yname)
        plt.show()

    return (slope, r2_value, p_value)


def collate_raw(basedirectory: str, all_report_filenames: List[str], total_num_files: int) -> Dict[str, List[float]]:
    collected: Dict[str, List[float]] = {}
    digits = len(str(total_num_files))

    for i in range(0, total_num_files):
        file_ID = f"{i+1}".zfill(digits) + "_"
        try:
            file_ID_found = [filename for filename in all_report_filenames if file_ID in filename][-1]
        except:
            file_ID_backup = f"{1}".zfill(digits) + "_"
            file_ID_found = [filename for filename in all_report_filenames if file_ID_backup in filename][-1]
            print("used dummy")
            print(i / total_num_files)
            print(i)
        file = pd.read_csv(basedirectory + file_ID_found)
        variable_names: List[str] = []
        if not variable_names:
            variable_names = list(file.columns)
        for variable_name in variable_names:
            if variable_name not in collected.keys():
                collected[variable_name] = []
            valuetoappend = file[variable_name].values[0]
            # if type(valuetoappend) is not str:
            if valuetoappend == "Under construction, use the results with caution.":
                pass
            else:
                valuetoappend = float(valuetoappend)
                collected[variable_name].append(valuetoappend)

    return collected

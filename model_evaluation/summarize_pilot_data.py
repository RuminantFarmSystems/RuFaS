import pandas as pd
import glob
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

def get_file_paths(file_name_in_directory):
    # Step 1: Get all CSV files in the specified directory
    csv_files = glob.glob(file_name_in_directory)
    return(csv_files)

def get_scen_name(file_path):
    file_name = Path(file_path).name
    return file_name.split(' ', 1)[0]


def get_pilot_data(csv_files, excluded_var):
    data_dict = {}
    data_dict["scen_name"] = []
    # Step 2: Read each CSV file and extract variables
    for file in csv_files:
        df = pd.read_csv(file,  usecols=lambda column: column != "DISCLAIMER")

        # Assuming the first row has variable names and the second row has the values
        variable_names = df.columns
        filtered_var = filter_variables(variable_names, excluded_var)

        df_subset = df[filtered_var]
        values = df_subset.iloc[0].astype(float)  # Convert values to float

        # Store the values in the dictionary
        for var_name, value in zip(filtered_var, values):
            if var_name not in data_dict:
                data_dict[var_name] = []
            data_dict[var_name].append(value)

        data_dict["scen_name"].append(get_scen_name(file))

    return data_dict

def get_summary_by_scen(results_dict):
    df = pd.DataFrame(results_dict)
    summary = df.groupby('scen_name').agg(['mean', 'std']).reset_index()
    return(summary)

def filter_variables(var_list, exclude_list):
    return [var for var in var_list if not any(var.startswith(prefix) for prefix in exclude_list)]



report_paths = get_file_paths("C:/Users/kfr3/OneDrive - Cornell University/RuFaS/Pilot Testing/Pilot Results/Sept2024/reports/pilotfarms_no_crops reports/*.csv")

variables_to_exclude = ["DMI by feed", "Feed emissions by feed", "LUC emissions by feed", "Storage ammonia by pen",
                        "Manure nitrous oxide (storage) by pen", "Storage ammonia by pen"]
results = get_pilot_data(report_paths, variables_to_exclude)

summary = get_summary_by_scen(results)

## save summary file as a csv
csv_file_path = "C:/Users/kfr3/OneDrive - Cornell University/RuFaS/Pilot Testing/Pilot Results/Sept2024/pilot_summary_results.csv"
summary.to_csv(csv_file_path, index=False)

## Plot summary results

# Plot the scatter plot with error bars

def scatter_plot_by_group(df, Group, Var, x_lab, y_lab, title, GroupName):
    plt.figure(figsize=(8, 6))

    # Create a color palette for different groups
    palette = sns.color_palette("husl", df[Group].nunique())

    # Loop through the groups to plot each group with specific colors and error bars
    for group, color in zip(df[Group].unique(), palette):
        subset = df[df[Group] == group]
        plt.errorbar(
            x=subset.index,
            y=subset[Var]["mean"],
            yerr=subset[Var]["std"],
            fmt='o',
            label=group,
            color=color,
            capsize=5,
            markersize=8
        )

    # Add labels and legend
    plt.xlabel(x_lab)
    plt.ylabel(y_lab)
    plt.title(title)
    plt.legend(title=GroupName)

    # Show the plot
    plt.show()


scatter_plot_by_group(summary, "scen_name", "Milk per cow/d, kg_hor_ver_agg",
                    x_lab= "Farm", y_lab = "Milk per cow/d (kg)",
                      title = "Average Milk Production", GroupName= "Farm ID")
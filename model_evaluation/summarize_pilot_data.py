import pandas as pd
import glob
from pathlib import Path

report_paths = get_file_paths("C:/Users/kfr3/3D Objects/Desktop/PilotResults/*.csv")

results = get_pilot_data(report_paths)

def get_file_paths(file_name_in_directory):
    # Step 1: Get all CSV files in the specified directory
    csv_files = glob.glob(file_name_in_directory)
    return(csv_files)

def get_scen_name(file_path):
    file_name = Path(file_path).name
    return file_name.split(' ', 1)[0]
def get_pilot_data(csv_files):
    data_dict = {}
    data_dict["scen_name"] = []
    # Step 2: Read each CSV file and extract variables
    for file in csv_files:
        df = pd.read_csv(file,  usecols=lambda column: column != "DISCLAIMER")

        # Assuming the first row has variable names and the second row has the values
        variable_names = df.columns
        values = df.iloc[0].astype(float)  # Convert values to float

        # Store the values in the dictionary
        for var_name, value in zip(variable_names, values):
            if var_name not in data_dict:
                data_dict[var_name] = []
            data_dict[var_name].append(value)

        data_dict["scen_name"].append(get_scen_name(file))

    return data_dict

def get_summary_by_scen(results_dict):
    df = pd.DataFrame(results_dict)
    summary = df.groupby('scen_name').agg(['mean', 'std']).reset_index()
    return(summary)
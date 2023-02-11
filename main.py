# !/usr/bin/env python3

"""
RUFAS: Ruminant Farm Systems Model
File name: main.py
Description: Main entry point of RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
"""

import RUFAS
import os
import shutil
import pandas as pd
import glob


def main():

    """
    Main function of RUFAS, executes simulations for all files specified.

    Prompts the user to enter an input path to a json file or a directory of
    json files. The path(s) are returned in a list, which the program loops
    through and executes the simulation for each of the files in the list.
    """

    print("\nRUFAS: Ruminant Farm Systems Model 2018")

    #
    # Prompt user for an input
    # Input could either be a json file when doing only 1 simulation
    # or a directory containing json files when doing a batch simulation
    #
    input_file_list = RUFAS.input_prompt()
    
    #
    # Begin the simulation
    # Runs the simulation for each input file in input_file_path
    # Runs only 1 simulation in the case of a single input file
    #
    for input_file_path in input_file_list:
        name = "dairy_conv"
        os.mkdir('./save_directory/' + name)
        for R in range(2):
            RUFAS.simulate(input_file_path)

            nn = "./save_directory/" + name + "/" + name + str(R) + ".csv"
            shutil.move("./output/CSVs/life_cycle_report/herd_report/herd_report.csv", nn)
        

        os.chdir('./save_directory/' + name)
        files = glob.glob('*.csv')
        dfs = []
        for f in files:
            df = pd.read_csv(f)
            df.drop(0, inplace=True) # drop the line of unit
            df.reset_index(drop = True, inplace = True)
            # try:
            #     df = df.astype(float)
            # except ValueError:
            #     print("cannot convert to float")
            # # df = df.convert_dtypes()
            # print(df)
            dfs.append(df)

        df_mean = pd.concat(dfs).groupby(level=0).mean()
        # print(df_mean)
        df_mean.to_csv(name+'.csv', encoding='utf-8', index=False)

#
# PROGRAM ENTRY POINT
#
if __name__ == '__main__':
    main()

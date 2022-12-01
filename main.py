# !/usr/bin/env python3

from RUFAS.simulation_engine import SimulationEngine
from RUFAS import input_prompt
from RUFAS.output_manager import OutputManager

def main():
    """
    Main function of RUFAS, executes simulations for all files specified.

    Prompts the user to enter an input path to a json file or a directory of
    json files. The path(s) are returned in a list, which the program loops
    through and executes the simulation for each of the files in the list.
    """

    print("RUFAS: Ruminant Farm Systems Model 2022")

    om = OutputManager()
    input_file_list = input_prompt()
    for input_file_path in input_file_list:
        simulator = SimulationEngine(input_file_path)
        simulator.simulate()
        om.save_all_pools(r'output')

if __name__ == '__main__':
    main()

"""
Parallelizing main
This requires the modified main.py and user_prompt.py, which makes main take an argument that's passed to the user_prompt
it also requires that you generate all the required config files
"""
# import json
# import model_evaluation.sensitivity_analysis.sensitivity_analysis_helpers as SAH
# import main
from main import run_rufas
from joblib import Parallel, delayed

# import the basic config file

# setupfile0 = 'C://Users//jw2574//Documents//data//MASM-yg_sensitivity-updated//outputtesting_10_saltelli//problem_list_analysis_details.json'
# f = open(setupfile0)
# setupfile = json.load(f)

# # scrape out the number of runs
# # numberofsimruns = setupfile['total_num_analyses'] # THIS NEEDS TO BE ADDED

# SAloopcode = 'SAloop1111' # INTEGRATING this into the management of the names, short code to handle different analyses, cleanup later to different collated output folders
# # get cleanup built in to clear cache? 


# simple example of how to structure the runs
# note that the function is in the first parentheses, the variable that goes inside the function in the second
# works find to have a complex variable calculated over the range/loop!
# Parallel(n_jobs=2)(delayed(sqrt)(i ** 2) for i in range(10))


def main_loop(target_input):
    run_rufas(input_path = target_input)
    return(target_input)

a = Parallel(n_jobs=6)(delayed(main_loop)(
    'input/animal_management_' + str(i).zfill(5) + '.json'
    ) for i in range(120,160))

# main_loop('input/animal_management_00042.json')
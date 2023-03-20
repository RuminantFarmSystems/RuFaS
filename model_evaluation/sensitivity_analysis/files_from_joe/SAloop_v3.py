"""
Parallelizing main
This requires the modified main.py and user_prompt.py, which makes main take an argument that's passed to the user_prompt
it also requires that required config files pre-generated
"""
import json

# import the basic config file

setupfile0 = 'C://Users//jw2574//Documents//data//MASM-yg_sensitivity-updated//outputtesting_10_saltelli//problem_list_analysis_details.json'
f = open(setupfile0)
setupfile = json.load(f)

# scrape out the number of runs
# numberofsimruns = setupfile['total_num_analyses'] # THIS NEEDS TO BE ADDED
numberofsimruns = 100

SAloopcode = 'SAloop1111' # INTEGRATING this into the management of the names, short code to handle different analyses, cleanup later to different collated output folders
# get cleanup built in to clear cache? 

import main
from joblib import Parallel, delayed
Parallel(n_jobs=4)(delayed(main.main)('animal_management_' + str(i).zfill(5) + '.json') for i in range(638,650))


# other approach? 

from joblib import parallel_backend
with parallel_backend('threading', njobs=4):
    for i in range(516,650):
        print(i)
        # inputname = str(SAloopcode) + '_animal_management_' + str(i)
        inputname = 'animal_management_' + str(i).zfill(5) + '.json'
        print(inputname)
        main.main(inputname)
        print('main.main(inputname)')
        print('# main will save to the filename specified in the config jsons!')
    

# simple example of how to structure the runs
# note that the function is in the first parentheses, the variable that goes inside the function in the second
# works find to have a complex variable calculated over the range/loop!
# Parallel(n_jobs=2)(delayed(sqrt)(i ** 2) for i in range(10))

Parallel(n_jobs=2)(delayed(main.main)('animal_management_' + str(i).zfill(5) + '.json') for i in range(516,650))



"""
"""
import json
import model_evaluation.sensitivity_analysis.sensitivity_analysis_helpers as SAH
import os
from SALib.analyze import ff as ff_a
from SALib.sample import ff as ff_s
from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.sample import fast_sampler


# load config json
with open('model_evaluation/sensitivity_analysis/config_inputs/sensitivity_analysis.json', 'r') as f:
    config_json = json.load(f)

input_files_to_modify = config_json["input_files_to_modify"]
analysis_type = config_json['sensitivity_method']
output_variables_of_interest = config_json["output_variables_of_interest"]
# internally generate the numbers from the config, using the same methods

saltelli_num = config_json['saltelli_or_fast_num']
saltelli_skip = config_json['saltelli_skip']

problem_list = config_json['problem']

problem_a = problem_list[0]

# then compare against the output_variables_of_interest

p = problem_a

if analysis_type =="ff":
    param_values = ff_s.sample(p) #fractional factorial
elif analysis_type =="saltellisobol":
    param_values = saltelli.sample(p, saltelli_num, skip_values=saltelli_skip) 
elif analysis_type == 'FAST':
    param_values = fast_sampler.sample(p, saltelli_num)


# WORKING ZONE
# COLLECTING THE OUTPUTS TO USE INSTEAD OF CURR COL IN ANALYSIS LISTS
collect_all_outputs = {}
for output_variables_of_interest in config_json['output_variables_of_interest']:
    print(output_variables_of_interest)
    output_variable_list = []
    total_num_runs = len(param_values)
    for every_run in total_num_runs:
        # get first file with the correct prefix
        for f_name in os.listdir('output/sensitivity/'):
            if f_name.startswith(str(every_run).zfill(5)) and f_name.endswith('.json'):
                break
        with open('output\\sensitivity\\00000_28-Jul-2023_Fri_12-48-33.json', 'r') as f:
            output_json = json.load(f)
        
        output_variable_list.append(output_json[output_variables_of_interest])
    collect_all_outputs[output_variables_of_interest] = collect_all_outputs


list_of_variable = output_json['MilkingParlor.__init__.fresh_water_use_rate']['values']
type(list_of_variable)
type(list_of_variable[0])

#####################
# if it's just a normal list
# this gets simple values out! for monthly data
# 386 in total
len(output_json['LifeCycleManager.daily_update.life_cycle_daily_herd_update']['values'])
oo = output_json['LifeCycleManager.daily_update.life_cycle_daily_herd_update']['values']
type(oo)
# THIS IS A LIST
ooout = [field['culled_cow_num'] for field in oo]
len(ooout)


############################################
# if it's a list of lists
stringin = 'LifeCycleManager.daily_update.life_cycle_daily_herd_update.values: culled_cow_num'
string_split = stringin.split(':')
string_split_0 = string_split[0]
if string_split_0[-6:] == 'values':
    #go ahead
    string_split_0 = string_split_0[:-7]

string_split_1 = string_split[1][1:]


oo = output_json[string_split_0]['values']
ooout = [field[string_split_1] for field in oo]
len(ooout)



import numpy as np
np.mean(ooout[-60:])

##################################################
# if it's a dict: it means there are individuals
if type(output_json['Cow.milking_update.milk_data_at_milk_update']['values'][0])==dict:
    pass
output_json['Cow.milking_update.milk_data_at_milk_update']['days_in_milk']




# BROKEN BELOW UNTIL ABOVE IS FINISHED<

for str_index in herd_structure_output:
    if analysis_type =="ff":
        analysis = ff_a.analyze(p, param_values, [r[curr_col] for r in analysis_lists], second_order=True)
        analysis = SAH.rewrite_ff_analysis(analysis) #
    if analysis_type =="saltellisobol":
        analysis = sobol.analyze(p,[r[curr_col] for r in analysis_lists]) #sobol
        analysis = SAH.rewrite_sobol_analysis(analysis) #
    # SALib.analyze.sobol.analyze(problem, Y, calc_second_order=True, num_resamples=100, conf_level=0.95, print_to_console=False, parallel=False, n_processors=None, keep_resamples=False, seed=None)
    # analysis = sol_a.analyze(p, [r[curr_col] for r in analysis_lists])
    
    curr_col += 1
    # analysis_file = dir_path + '/herd_structure/analysis_' + str_index + '.txt'
    analysis_file = dir_path + '/herd_structure/analysis_' + str_index + '.csv'
    file = open(analysis_file, 'w', newline='')
    with file:
        write = csv.writer(file)
        write.writerows(analysis)
    # file = open(analysis_file, 'w')
    # file.write(str(analysis))
    # file.close()

if os.path.exists(dir_path + '/problem_outputs/'):
    shutil.rmtree(dir_path + '/problem_outputs/')
os.mkdir(dir_path + '/problem_outputs/')

for str_index in output_indices[i]:
    if analysis_type =="ff":
        analysis = ff_a.analyze(p, param_values, [r[curr_col] for r in analysis_lists], second_order=True)
        analysis = SAH.rewrite_ff_analysis(analysis) # 
    if analysis_type =="saltellisobol":
        analysis = sobol.analyze(p,[r[curr_col] for r in analysis_lists]) #sobol
        analysis = SAH.rewrite_sobol_analysis(analysis) #
    curr_col += 1
    # analysis_file = dir_path + '/problem_outputs/analysis_' + str_index + '.txt'
    analysis_file = dir_path + '/problem_outputs/analysis_' + str_index + '.csv'
    file = open(analysis_file, 'w', newline='')
    with file:
        write = csv.writer(file)
        write.writerows(analysis)
    # file = open(analysis_file, 'w')
    # # file.write(str(analysis))
    # file.write(analysis)
    # file.close()
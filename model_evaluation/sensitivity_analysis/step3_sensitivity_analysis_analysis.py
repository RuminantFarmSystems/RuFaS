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
import numpy as np

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

param_values = np.array(config_json['param_values'])

# WORKING ZONE
# COLLECTING THE OUTPUTS TO USE INSTEAD OF CURR COL IN ANALYSIS LISTS
collect_all_outputs = {}
for output_variable_of_interest in config_json['output_variables_of_interest']:
    #output_variable_of_interest = output_variables_of_interest[2]
    #output_variable_of_interest = "LifeCycleManager.daily_update.life_cycle_daily_herd_update.values: PGF_injection_num"

    print(output_variable_of_interest)
    output_variable_list = []
    total_num_runs = len(param_values)
    for every_run in range(total_num_runs):
        # if every_run > 50:
        #     break
        print(f'run={every_run}')
        # get first file with the correct prefix
        for f_name in os.listdir('output/sensitivity/'):
            if f_name.startswith(str(every_run).zfill(5)) and f_name.endswith('.json'):
                f_name_full = 'output\\sensitivity\\' + f_name
                break
        with open(f_name_full, 'r') as f:
            output_json = json.load(f)
            print(f_name_full)
        # APPEND TO LIST IN DICT
        # E.G. all_outputs['output_variable_of_interest'] = output_json[variableparsed]
        # the = term has to use pase_output_location(output_json, variable_of_interest)
        if ':' not in output_variable_of_interest:
            analysis_time = len(output_json[output_variable_of_interest]['values'])/4
            output_variable_mean = np.mean(output_json[output_variable_of_interest]['values'][-int(analysis_time):])
            output_variable_list.append(output_variable_mean)
        else:
            string_split = output_variable_of_interest.split(':')
            string_split_0 = string_split[0]
            if string_split_0[-6:] == 'values':
                key_name = string_split_0[:-7]
                value_name = string_split[1][1:]
                values_found = output_json[key_name]['values']
                # values_found = 
                if type(values_found[0])==dict:
                    values_found_list = [field[value_name] for field in values_found]
                    #len(values_found_list)
                    output_variable_list.append(np.mean(values_found_list[-int(len(values_found_list)/4):]))
                elif type(values_found[0])==list:
                    pass
    collect_all_outputs[output_variable_of_interest] = output_variable_list



collect_all_outputs2 = {}
output_variable_list = []
total_num_runs = len(param_values)
for every_run in range(total_num_runs):
    # if every_run > 50:
    #     break
    print(f'run={every_run}')
    # get first file with the correct prefix
    for f_name in os.listdir('output/sensitivity/'):
        if f_name.startswith(str(every_run).zfill(5)) and f_name.endswith('.json'):
            f_name_full = 'output\\sensitivity\\' + f_name
            break
    with open(f_name_full, 'r') as f:
        output_json = json.load(f)
        print(f_name_full)
    for output_variable_of_interest in config_json['output_variables_of_interest']:
        #output_variable_of_interest = output_variables_of_interest[2]
        #output_variable_of_interest = "LifeCycleManager.daily_update.life_cycle_daily_herd_update.values: PGF_injection_num"
        print(output_variable_of_interest)
        # APPEND TO LIST IN DICT
        # E.G. all_outputs['output_variable_of_interest'] = output_json[variableparsed]
        # the = term has to use pase_output_location(output_json, variable_of_interest)
        if ':' not in output_variable_of_interest:
            analysis_time = len(output_json[output_variable_of_interest]['values'])/4
            output_variable_mean = np.mean(output_json[output_variable_of_interest]['values'][-int(analysis_time):])
            output_variable_list.append(output_variable_mean)
        else:
            string_split = output_variable_of_interest.split(':')
            string_split_0 = string_split[0]
            if string_split_0[-6:] == 'values':
                key_name = string_split_0[:-7]
                value_name = string_split[1][1:]
                values_found = output_json[key_name]['values']
                # values_found = 
                if type(values_found[0])==dict:
                    values_found_list = [field[value_name] for field in values_found]
                    #len(values_found_list)
                    output_variable_mean = np.mean(values_found_list[-int(len(values_found_list)/4):])
                    output_variable_list.append(output_variable_mean)
                elif type(values_found[0])==list:
                    pass
        if output_variable_of_interest not in collect_all_outputs2.keys():        
            collect_all_outputs2[output_variable_of_interest] = [output_variable_mean]
        else:
            collect_all_outputs2[output_variable_of_interest].append(output_variable_mean)


x = [value[3] for value in param_values.tolist()]
y = collect_all_outputs2[list(collect_all_outputs2.keys())[3]] 
 
 
import csv
for idx, name in enumerate(output_variables_of_interest):
    print(idx)
    print(name)
    # if idx==1:
    #     break
    print(collect_all_outputs[name])
    concatenated_output = np.concatenate(collect_all_outputs[name], axis=None)
    if analysis_type =="ff":
        analysis = ff_a.analyze(p, param_values, collect_all_outputs[name], second_order=True)
        analysis = SAH.rewrite_ff_analysis(analysis) #
    if analysis_type =="saltellisobol":
        analysis = sobol.analyze(p, concatenated_output) #sobol
        analysis = SAH.rewrite_sobol_analysis(analysis, p) #
    # SALib.analyze.sobol.analyze(problem, Y, calc_second_order=True, num_resamples=100, conf_level=0.95, print_to_console=False, parallel=False, n_processors=None, keep_resamples=False, seed=None)
    # analysis = sol_a.analyze(p, [r[curr_col] for r in analysis_lists])

    # HOW TO WRITE THESE? 
    file = open(f'sensitivity_analysis_var_{idx}.csv', 'w', newline='')
    with file:
        write = csv.writer(file)
        write.writerows(analysis)



##################################################
##################################################
##################################################
##################################################
##################################################
##################################################

##################################################
# if it's a dict: it means there are individuals
if type(output_json['Cow.milking_update.milk_data_at_milk_update']['values'][0])==dict:
    pass
key_name = 'Cow.milking_update.milk_data_at_milk_update'
value_name = 'estimated_daily_milk_produced'
['days_in_milk']




key_name = 'LifeCycleManager.daily_update.life_cycle_daily_herd_update'
type(output_json[key_name]['values'][0])






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
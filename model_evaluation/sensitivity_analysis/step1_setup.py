import os
import glob
import introcs
import pandas as pd
import json

from SALib.analyze import ff as ff_a
from SALib.sample import ff as ff_s
from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.sample import fast_sampler
import model_evaluation.sensitivity_analysis.sensitivity_analysis_helpers as SAH

with open('model_evaluation\sensitivity_analysis\config_inputs\sensitivity_analysis.json', 'r') as j:
     config_json = json.loads(j.read())

# this shows EVERYTHING in thefile
print(json.dumps(config_json, sort_keys=False, indent=4))

# this shows the file in a neat and tidy list
oout2 = SAH.find_json_terminal_variables2(config_json)
print(*oout2, sep = "\n")




potential_inputs_to_modify = list(config_json['input_files_to_modify'].keys())

# for each of the lists, check if it has items in the list
inputJSONs_to_modify = []
for l in potential_inputs_to_modify:
    if len(config_json['input_files_to_modify'][l]) > 0:
        inputJSONs_to_modify.append(l)

variable_list_a = []
for input_JSON in inputJSONs_to_modify:
    for i in range(0,len(config_json['input_files_to_modify'][input_JSON])):
        variable_list_a.append(config_json['input_files_to_modify'][input_JSON][i])    



analysis_type = config_json['sensitivity_method']

# remaking the variable groups for the SA analysis
if analysis_type=='ff':
    problem_a,problem_a_code = SAH.ff_problemmaker(variable_list_a)
    problem_list_code = [problem_a_code]
else:
    problem_a = SAH.problemmaker(variable_list_a)



problem_list = [problem_a]
xkey = []
for x, value in enumerate(problem_list):
    #print(value)
    if value == 'NA':
        xkey.append(x)
        #problem_list=problem_list[0:x]
for i in reversed(range(len(xkey))):
    del problem_list[xkey[i]]
print(problem_list)


print("These are the different 'problems' being analyzed")
print(*problem_list, sep='\n')
print('\n')

total_num_simulations = list([len(x) for x in problem_list])


saltelli_or_fast_num = config_json['saltelli_or_fast_num']
saltelli_skip = config_json['saltelli_skip']
steady_state_day = config_json['steady_state_day']

######################
# Generating X JSONs #
######################
# iterating this over each "problem"
problem_a

for i, p in enumerate(problem_list):
    if analysis_type =="ff":
        param_values = ff_s.sample(problem_a) #fractional factorial
    elif analysis_type =="saltellisobol":
        param_values = saltelli.sample(problem_a, saltelli_or_fast_num, skip_values=saltelli_skip) 
    elif analysis_type == 'FAST':
        param_values = fast_sampler.sample(p, saltelli_or_fast_num)
        # The Saltelli sampler generates N*(2D + 2) samples
        # where N = argument in sampler, D = number of model inputs
        # adding argument calc-second_order = False would generate N*(D + 2) samples
    else: param_values=[]
    # len(param_values)
    minutes_to_run = 5
    print("this problem's analysis will take approximately " + str(len(param_values)*minutes_to_run) + " minutes to run")
    print("this problem's analysis will take approximately " + str(len(param_values)*minutes_to_run/60) + " hours to run")
    print("this problem's analysis will take approximately " + str(round(len(param_values)*minutes_to_run/60/24,3)) + " days to run")

    # create directory with label for herd num
    # this may be deprecated, or used to separate out analyses based on other variables
    # num = SAH.find_value_at_path(json_object, SAH.path_finder(json_object, 'herd_num').split('.'))
    # dir_path = prefix_variable + '/problem' + str(i) + '/herdreports/'
    # plot_dir_path = prefix_variable + '/problem' + str(i) + '/graphics/'

    # if os.path.exists(dir_path):
    #     pass # shutil.rmtree(dir_path)
    # else:
    #     os.mkdir(dir_path)
    settings_decoder = []
    for i, filename in enumerate(inputJSONs_to_modify):
        for j in range(0, len(config_json['input_files_to_modify'][filename])):
            settings_decoder.append(filename)
    for s, settings in enumerate(param_values):
        print(s)
        print(settings)
        #json_to_print = str(settings_decoder[s][:-5] + '_' +  str(s).zfill(5) + '.json')
        
        namelist = problem_a['names']

        print('writing jsons for sample', s+1, 'out of', len(param_values))
        
        for jsonfile in inputJSONs_to_modify:
            json_to_modify = jsonfile
            
            # whichparams = [paramlist for x in settings_decoder if x==json_to_modify]
            paramlist = list(param_values[s])
            params_subset=[]
            for idx, j in enumerate(settings_decoder):
                if j == settings_decoder[idx]:
                    params_subset.append(paramlist[idx])
            
            json_to_print = 'input/' + json_to_modify[:-5] + '_' +  str(s).zfill(5) + '.json'
            # populate input json with settings from samples
            SAH.json_populater_duplicate(params_subset, problem_a, json_to_modify, json_to_print)


        
        lifecyclereport_tomodify = str(os.getcwd() + '\input\output\\' + 'life_cycle_report' + '_' +  str(s).zfill(5) + '.json')
        
        SAH.anim_manag_modifier(inputJSONs_to_modify, s)
        
        herdreportname = 'herd_report_' + str(s).zfill(5)
        SAH.lifecycle_modifier(lifecyclereport_tomodify, herdreportname)















# ####################
# # USER INPUT START #
# ####################
# # here user should set the folder they want to work out of
# # os.chdir('C:\\Users\\jw2574\\Documents\\data\\MASM-master-220912')
# # os.chdir('C:\\Users\\jw2574\\Documents\\data\\MASM-yg_sensitivity-updated')
# os.chdir('C:\\Users\\jw2574\\Documents\\data\\MASM-yg_sensitivity-test')
# current_directory = os.getcwd()
# user_input_filename = 'animal_management_animal'

# # See tools in SA_preanalysis_checklist prior to following section

# #######################
# # Input configuration #
# #######################

# # Note that the names MUST be identical to those in the input json
# # The names can be found using the preanalysis_checklist, or by traversing the JSON by hand
# # Must be list of lists follwing the format of inpus_variable_name, mean value, upper/lower bound
# variable_list_a = [
#  ['breeding_start_day_h', 380, 38*2],
#  ['heifer_repro_cull_time', 140, 14*2],
#  ['estrus_detection_rate_h', 0.6, 0.22],
#  ['cull_milk_production', 17.0, 12],
#  ['cow_times_milked_per_day', 2, 1.5],
#  ['wean_day', 60, 60*.45],
#  ['avg_estrus_cycle_heifer', 24, 10],
#  ['still_birth_rate', 0.065, 0.065*.45],
#  ['horizontal_dist_to_milking_parlor', 1.6, 1],
#  ['mature_body_weight_avg', 740, 100],
# ]

# variable_list_b = 'NA'
# # additional problems don't need to be defined 'NA' like this, but beyond list 'e' user needs to modify code below to add more
# variable_list_c = 'NA'
# variable_list_d = 'NA'
# variable_list_e = 'NA'

# ########################
# # Output Configuration #
# ########################
# # output_to_read = '\save_directory\dm_manure_pull_request\CSVs\life_cycle_report\herd_report\herd_report.csv'
# output_to_read = '\\output\\CSVs\\life_cycle_report\\herd_report\\herd_report.csv'
# # note that this requires running the simulation once, to "know" what output 
# # variables you're interested in
# # see SA_preanalysis_checklist.py for help
# # this will run the simulation once with the loaded defaults in the JSON, to populate a 
# # later required list

# herd_structure_output = ['culled_heifer_num','cow_percent',
#                              'avg_cow_culling_age', 'ai_num', 'cumulated_milk_production', 'cow_percent_for_parity_greater_than_3', 
#                              'preg_cow_percent', 'milking_cow_percent']

# # these are tailored to the analysis you're doing
# # if you want to modify these specific to a given problem, a new list should be made with a unique name, and inserted into the list of outputs
# # if user desires the above line, user should search for 'output_indices = {' and follow instructions in that section.
# allproblem_output1 = ['CIDR_count','GnRH_injections_heifer','PGF_injections_heifer','ed_period_heifer',
#                             'ai_num_heifer','preg_check_num_heifer','avg_breeding_to_preg_time','avg_service_rate_heifer',
#                             'avg_conception_rate_heifer','pregnancy_rate_heifer','sold_heifer_last_year','bought_heifer_last_year',
#                             'culled_heifer_last_year','culled_heifer_age','heifer_open_time','cost_feed_heifer','cost_repro_heifer']

# allproblem_output2 = ['avg_caving_interval', 'avg_breeding_to_preg_time',
#                         'milking_cow_num',	'milking_cow_percent',	'dry_cow_num',	'dry_cow_percent',	'average_days_in_milk',	
#                         'average_cow_body_weight',	'average_parity_number', 'avg_caving_interval']

# # Specify a few others to analyze in the output?
# # e.g. 
# # 'income_milk', 'cost_repro_cow',	'cost_feed',	'milk_income_over_feed_cost', 'average_days_in_milk', average_cow_body_weight

# # These are the variables to analyze specific to the problem
# # output variables to analyze are selected, user can make a unique set and replace "allproblem_output" with the new list name here where appropriate
# # for instance, if the third analysis (e.g. analysis '2') wants to change a specific subset, make something like a "problem2_output" variable (cont. on next line) 
# # and user should insert the variable name on the line of index 2 below, in place of "allproblem_output"
# output_indices = {
#     0: allproblem_output1,
#     1: allproblem_output2,
#     2: allproblem_output1,
#     3: allproblem_output1,
#     4: allproblem_output1
# }

# # this is the folder name for the outputs
# # it will be a new directory created in the base directory of the working folder
# prefix_variable = 'output_test_1111'

# # USER needs to define this, but requires careful thinking. 
# # See discussion/definition on basecamp in document "Variables for Sensitivity Analysis"
# steady_state_day = 924

# # pick between these two to determine which analysis you want
# # can simply switch order here so whichever is last is the option selected
# analysis_type = 'saltellisobol'
# analysis_type = 'ff'
# analysis_type = 'FAST'

# # number for argument in the satelli sampling function
# # Should be a power of 2 and <= `skip_values`.
# saltelli_num = 2**6
# FAST_num = 65
# # Number of points in Sobol' sequence to skip, ideally a value of base 2
# # (default: a power of 2 >= N, or 16; whichever is greater)
# saltelli_skip = 16

# ##################
# # END USER INPUT #
# ##################

# # find out which user input is required
# print('Which file are you interested in? Write the substring without quotes')
# # user_input_filename = input()
# # user_input_filename = 'animal'

# # python finds the file - prints the name
# # checks if there are more than one match, e.g. incorrect name?
# # this is hardcoded to the input folder, to avoid manipulating files we shouldn't
# # the double asterisk before the slash indicates it searches through any recurvise folder
# files_found = glob.glob(current_directory+'\\input\\**\\'+user_input_filename+'*',
#  recursive = True)
# IDs = []
# files_found_short = []
# for n in range(len(files_found)):
#     numba = n
#     IDs.append(numba)
#     fnamemark = introcs.rfind_str(files_found[n], '\\')
#     files_found_short.append(files_found[n][fnamemark:])

# # showing the results
# # pd.DataFrame({'ID': IDs,
# # 'names': files_found_short})
# print(pd.DataFrame({'names': files_found_short}))
# #print('which one do you want?')
# #filepicked = input()
# filepicked = 0
# json_to_modify = files_found[int(filepicked)]
# print('we\'re going to modify '+ json_to_modify)

# # pick the following variables
# # search inside json_to_modify
# file = open(json_to_modify)
# json_object = json.load(file)
# # type(json_object)

# # this shows EVERYTHING in thefile
# print(json.dumps(json_object, 
# sort_keys=True, indent=4))

# # this shows the file in a neat and tidy list
# oout2 = SAH.find_json_terminal_variables2(json_object)
# print(*oout2, sep = "\n")
# len(oout2)

# ################################################################################################################################################
# ################################################################################################################################################

# ##############
# # SOME STUFF #
# ##############

# # remaking the variable groups for the SA analysis
# if analysis_type=='ff':
#     problem_a,problem_a_code = SAH.ff_problemmaker(variable_list_a)
#     problem_b,problem_b_code = SAH.ff_problemmaker(variable_list_b)
#     problem_c,problem_c_code = SAH.ff_problemmaker(variable_list_c)
#     problem_d,problem_d_code = SAH.ff_problemmaker(variable_list_d)
#     problem_e,problem_e_code = SAH.ff_problemmaker(variable_list_e)
#     problem_list_code = [problem_a_code, problem_b_code, problem_c_code, problem_d_code, problem_e_code]
# else:
#     problem_a = SAH.problemmaker(variable_list_a)
#     problem_b = SAH.problemmaker(variable_list_b)
#     problem_c = SAH.problemmaker(variable_list_c)
#     problem_d = SAH.problemmaker(variable_list_d)
#     problem_e = SAH.problemmaker(variable_list_e)

# problem_list = [problem_a, problem_b, problem_c, problem_d, problem_e]
# xkey = []
# for x, value in enumerate(problem_list):
#     #print(value)
#     if value == 'NA':
#         xkey.append(x)
#         #problem_list=problem_list[0:x]
# for i in reversed(range(len(xkey))):
#     del problem_list[xkey[i]]
# print(problem_list)

# if os.path.exists(prefix_variable):
#     pass#shutil.rmtree(prefix_variable)
# else:
#     os.mkdir(prefix_variable)

# print("These are the different 'problems' being analyzed")
# print(*problem_list, sep='\n')
# print('\n')

# total_num_simulations = list([len(x) for x in problem_list])

# if analysis_type == 'saltellisobol': 
#     saltelli_or_fast_num = saltelli_num
# if analysis_type == 'ff': 
#     saltelli_or_fast_num = 0
# if analysis_type == 'FAST': 
#     saltelli_or_fast_num = FAST_num
# else: saltelli_or_fast_num = []


# ######################
# # Generating X JSONs #
# ######################
# # iterating this over each "problem"
# for i, p in enumerate(problem_list):
#     print(i)
#     print(p)
#     print('\nstarting problem ' + str(i+1) + ' out of ' + str(len(problem_list)))
#     if analysis_type =="ff":
#         param_values = ff_s.sample(p) #fractional factorial
#     if analysis_type =="saltellisobol":
#         param_values = saltelli.sample(p, saltelli_num, skip_values=saltelli_skip) 
#     if analysis_type == 'FAST':
#         param_values = fast_sampler.sample(p, FAST_num)
#         # The Saltelli sampler generates N*(2D + 2) samples
#         # where N = argument in sampler, D = number of model inputs
#         # adding argument calc-second_order = False would generate N*(D + 2) samples
#     else: param_values=[]
#     # len(param_values)
#     print("this problem's analysis will take approximately " + str(len(param_values)*3) + " minutes to run")
#     print("this problem's analysis will take approximately " + str(len(param_values)*3/60) + " hours to run")
#     print("this problem's analysis will take approximately " + str(round(len(param_values)*3/60/24,3)) + " days to run")
#     # create directory for problem
#     if os.path.exists(prefix_variable + '/problem' + str(i)):
#         pass# shutil.rmtree(prefix_variable + '/problem' + str(i))
#     else:
#         os.mkdir(prefix_variable + '/problem' + str(i))

#     # create directory with label for herd num
#     # this may be deprecated, or used to separate out analyses based on other variables
#     num = SAH.find_value_at_path(json_object, SAH.path_finder(json_object, 'herd_num').split('.'))
#     dir_path = prefix_variable + '/problem' + str(i) + '/herdreports/'
#     plot_dir_path = prefix_variable + '/problem' + str(i) + '/graphics/'

#     if os.path.exists(dir_path):
#         pass # shutil.rmtree(dir_path)
#     else:
#         os.mkdir(dir_path)
#     plotting_row = []
#     analysis_lists = []
#     # for each analysis within each problem
#     for s, settings in enumerate(param_values):
#     #for s in range(678,len(param_values)):
#         #settings = param_values[s]
#         print(s)
#         json_to_print = str(json_to_modify[:-5] + '_' +  str(s).zfill(5) + '.json')
        
#         namelist = p['names']
#         plot_dir_path = prefix_variable + '/problem' + str(i) + '/graphics/'
#         plotfilename = plot_dir_path + 'outputs_plotting.json'

#         print('writing jsons for sample', s+1, 'out of', len(param_values))

#         # populate input json with settings from samples
#         SAH.json_populater_duplicate(settings, problem_list[i], json_to_modify, json_to_print)
#         anim_manag_tomodify = str(os.getcwd() + '\input\\' + 'animal_management' + '_' +  str(s).zfill(5) + '.json')
        
#         lifecyclereport_tomodify = str(os.getcwd() + '\input\output\\' + 'life_cycle_report' + '_' +  str(s).zfill(5) + '.json')
        
#         SAH.anim_manag_modifier(anim_manag_tomodify, json_to_print, lifecyclereport_tomodify)
        
#         herdreportname = 'herd_report_' + str(s).zfill(5)
#         SAH.lifecycle_modifier(lifecyclereport_tomodify, herdreportname)

# problem_output = {'problem_list':problem_list,
# 'analysis_type':analysis_type,
# 'prefix_variable':prefix_variable,
# 'saltelli_or_fast_num':saltelli_or_fast_num,
# 'herd_structure_output': herd_structure_output,
# 'output_indices': output_indices,
# 'total_num_simulations': total_num_simulations
# }

# # Write this to a JSON to later read in
# pl_path = prefix_variable
# save_name = '\\' + pl_path + '\problem_list_analysis_details.json'
# filetosave = current_directory + save_name
# jsonString = json.dumps(problem_output, indent=4)
# print(jsonString)
# with open(filetosave, 'a', encoding="utf-8") as file:
#     file.write(jsonString)
# file.close()


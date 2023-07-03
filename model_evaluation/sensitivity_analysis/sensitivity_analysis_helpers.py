"""
helpers for the SA methods generalized version

"""
import json
import csv
import ast

def path_finder(json, key):
  """
  This will find the full path of the 'key' within the 'json' object

  Args:
    json: a json object, e.g. a file read by the json handler
    key: string of variable input name desired
  Returns: 
    key_path: string separated by periods of the key variable's path 
  """
  # don't bother with invalid json
  if not isinstance(json, dict):
    return None
    
  # if the key is in a first child, just return it
  if key in json.keys():
    return f"{key}"

  # otherwise we gotta recursively traverse our json
  key_path = None
  for json_key in json.keys():
    # spider-man pointing meme
    child_json = path_finder(json[json_key], key)
    if child_json is None:
      continue
    else:
      key_path = f"{json_key}.{child_json}"
      #print(key_path)
  return key_path

def get_full_path(json, key):
    """
    This simply calls the path_finder function - can be ignored?
    Args:
        json: a json object, e.g. a file read by the json handler
        key: string of variable input name desired
    Returns: 
        path: string separated by periods of the key variable's path 
    """
    path = path_finder(json, key)
    # print(path)
    return path

def find_value_at_path(json, path):
    """
    This recursively explores the json object 
    to find the value for a given path
      Args:
        json: a json object, e.g. a file read by the json handler
        key: string of variable input name desired
    Returns: 
        found value, type of which depends on the value in the json
    """
    if len(path) == 1:
        return json[path[0]] 
    else:
        return find_value_at_path(json[path[0]], path[1:])


def variable_list_trim(x):
    """
    This simple function merely trims the 
    """
    xkey = []
    for count, value in enumerate(x):
        if value=='NA':
            xkey.append(count)
        # print(x)
    if len(x)==0:
        x='NA'
    for i in reversed(range(len(xkey))):
        del x[xkey[i]]
    return x

def extr(lst,n):
    """
    This is simply used to take a list and extract every n items from a list of lists
    Example: where n=1, extr(x, n) will return the second (e.g. position 1) of each list in lst
    Args:
        lst is a list of lists, e.g. [[1,2], [3,4]]
    Return is a list of the extracted items
    """
    return [item[n] for item in lst]

def boundmaker(list):
    """
    This function takes the input list, which is required to be a name, a value, 
        and the bound range (i.e. the upper and lower bounds)
    It then simply returns a list of values that are the +/- values
    e.g. if the value in list[n][1] = 10, and the value in list[n][2] = 2
        Then the result will be 8 and 12
    """
    if list=='NA':
        pass
    else:
        aaapend = []
        for n in range(len(list)):
            vallisttemp = [list[n][1]-list[n][2], list[n][1]+list[n][2]]
            aaapend.append(vallisttemp)
        return aaapend

def ff_boundmaker(list):
    """
    This function takes the input list, which is required to be a name and the 
        upper and lower bounds)
    e.g. if the value in list[n][1] = 10, and the value in list[n][2] = 12
        Then the result will be 8 and 12
    """
    ff_coding = []
    if list=='NA':
        pass
    else:
        aaapend = []
        for n in range(len(list)):
            if type(list[n][1])==str:
                vallisttemp = [-99999, 99999]
                ff_coding.append([list[n][1], list[n][2]])
            else:
                vallisttemp = [list[n][1], list[n][2]]
                ff_coding.append([list[n][1], list[n][2]])
            aaapend.append(vallisttemp)
        
        return aaapend, ff_coding

def problemmaker(list):
    """
    This function takes inputs from a list and reorganizes them into a dict format
    This is the structure necessary to be readable by the SALib methods package
    Args: List needs to follow the structure of the following:
        variable1 = ['variable1_name', 100, 5]
        variable2 = ['variable2_name', 200, 50]
        variable3 = ['variable3_name', 30, 1]
        variable_list = [variable1a, variable2a, variable3]
        # Note: 'variable_list' is the input in the Arg., the other lines 
            are required to understand the structure
    """
    if type(list)==str or len(list)==0:
        problem_out = 'NA'
    else:
        problem_out = {
            'num_vars':len(list),
            'names':extr(list, 0),
            'bounds':boundmaker(list)
        }
    return problem_out

def ff_problemmaker(list):
    """
    This function takes inputs from a list and reorganizes them into a dict format
    This is the structure necessary to be readable by the SALib methods package
    Args: List needs to follow the structure of the following:
        variable1 = ['variable1_name', "A", "B"]
        variable2 = ['variable2_name', "D", "C"]
        variable3 = ['variable3_name', "E", "F"]
        variable_list = [variable1a, variable2a, variable3]
        # Note: 'variable_list' is the input in the Arg., the other lines 
            are required to understand the structure
    """
    if type(list)==str or len(list)==0:
        problem_out = 'NA'
        ff_coding = 'NA'
    else:
        aaapend,ff_coding = ff_boundmaker(list)
        problem_out = {
            'num_vars':len(list),
            'names':extr(list, 0),
            'bounds': aaapend
        }
    return problem_out, ff_coding

def json_populater(params, problem_x, json_to_modify):
    """
    Method to populate JSON file
    This needs to be used with caution, because it will override the input json
    Args:
        'Params' is the "settings" in the parameter values generated by 
            ff_s.sample(p), where 'p' is a 'problem' 
                as generated by the 'problemmaker' function
            params/settings is thus generated inside the analysis loop
        problem_x is the problem itselg, e.g. the dict generated by 'problemmaker'
        json_to_modify is the json path - not the object
            This is because the json is opened and replaced
    """
    # begin with default values
    file = open(json_to_modify)
    json_object = json.load(file)
    file.close()
    potential_inputs = find_json_terminal_variables1(json_object)
    # pen stuff isn't working - hardcoded for now, but to be later added to change pen variables following a second input
    # would have to be something like the pens being decided on with a followup variable, or that those need to be generated manually
    pen_wanted = 8
    pennamechange = 'pen' + str(pen_wanted)
    for j in range(len(problem_x['names'])):

        if problem_x['names'][j][0:5] == 'dummy':
            pass
        else:
            # find if it actually is inside the json!!!
            assert problem_x['names'][j] in potential_inputs, f"Incorrect input! The following isn't in the list!: {problem_x['names'][j]}"
            # Correct input is something like: assert 'unkown_cull_prob' in potential_inputs, f"Incorrect input!"

        if problem_x['names'][j][0:5] == 'dummy':
            pass
        else:
            full_path = get_full_path(json_object, problem_x['names'][j])
            # found_variable can be shown in comparisons if needed: 
            # found_value = find_value_at_path(json_object, path_list)
            # e.g. print('previous value was ' + str(found_value))
            path_list = full_path.split('.')
            llen = len(path_list)
            if params[j]==99999 or params[j]==-99999:
                valtouse = ff_populater_picker(params[j])
            else:
                valtouse = params[j]
            if llen==1:
                json_object[path_list[0]] = valtouse
                # print(json_object[path_list[0]])
            if llen==2:
                json_object[path_list[0]][path_list[1]] = valtouse
                # print(json_object[path_list[0]][path_list[1]])
            if llen==3 and pen_wanted != 8:
                json_object[path_list[0]][pennamechange][path_list[2]] = valtouse
                #print(json_object[path_list[0]][pennamechange][path_list[2]])
            if llen==3 and pen_wanted == 8:
                json_object[path_list[0]][path_list[1]][path_list[2]] = valtouse
                #print(json_object[path_list[0]][path_list[1]][path_list[2]])
            if llen==4:
                json_object[path_list[0]][path_list[1]][path_list[2]][path_list[3]] = valtouse
                #print(json_object[path_list[0]][path_list[1]][path_list[2]][path_list[3]])
            if llen==5:
                json_object[path_list[0]][path_list[1]][path_list[2]][path_list[3]][path_list[4]] = valtouse
                #print(json_object[path_list[0]][path_list[1]][path_list[2]][path_list[3]][path_list[4]])
    # write updated values
    file = open(json_to_modify, 'w')
    json.dump(json_object, file, indent=4) # remove , indent=4 if causes problems!
    file.close()




def json_populater_duplicate(params, problem_x, json_to_modify, json_to_print, ):
    """
    Method to populate JSON file
    This needs to be used with caution, because it will override the input json
    Args:
        'Params' is the "settings" in the parameter values generated by 
            ff_s.sample(p), where 'p' is a 'problem' 
                as generated by the 'problemmaker' function
            params/settings is thus generated inside the analysis loop
        problem_x is the problem itselg, e.g. the dict generated by 'problemmaker'
        json_to_modify is the json path - not the object
            This is because the json is opened and replaced
    """
    # begin with default values
    file = open('input/'+json_to_modify)
    json_object = json.load(file)
    file.close()
    potential_inputs = find_json_terminal_variables1(json_object)
    # pen stuff isn't working - hardcoded for now, but to be later added to change pen variables following a second input
    # would have to be something like the pens being decided on with a followup variable, or that those need to be generated manually
    pen_wanted = 8
    pennamechange = 'pen' + str(pen_wanted)
    for j in range(len(problem_x['names'])):

        if problem_x['names'][j][0:5] == 'dummy':
            pass
        else:
            # find if it actually is inside the json!!!
            assert problem_x['names'][j] in potential_inputs, f"Incorrect input! The following isn't in the list!: {problem_x['names'][j]}"
            # Correct input is something like: assert 'unkown_cull_prob' in potential_inputs, f"Incorrect input!"

        if problem_x['names'][j][0:5] == 'dummy':
            pass
        else:
            full_path = get_full_path(json_object, problem_x['names'][j])
            # found_variable can be shown in comparisons if needed: 
            # found_value = find_value_at_path(json_object, path_list)
            # e.g. print('previous value was ' + str(found_value))
            path_list = full_path.split('.')
            llen = len(path_list)
            if params[j]==99999 or params[j]==-99999:
                valtouse = ff_populater_picker(params[j])
            else:
                valtouse = params[j]
            if llen==1:
                json_object[path_list[0]] = valtouse
                # print(json_object[path_list[0]])
            if llen==2:
                json_object[path_list[0]][path_list[1]] = valtouse
                # print(json_object[path_list[0]][path_list[1]])
            if llen==3 and pen_wanted != 8:
                json_object[path_list[0]][pennamechange][path_list[2]] = valtouse
                #print(json_object[path_list[0]][pennamechange][path_list[2]])
            if llen==3 and pen_wanted == 8:
                json_object[path_list[0]][path_list[1]][path_list[2]] = valtouse
                #print(json_object[path_list[0]][path_list[1]][path_list[2]])
            if llen==4:
                json_object[path_list[0]][path_list[1]][path_list[2]][path_list[3]] = valtouse
                #print(json_object[path_list[0]][path_list[1]][path_list[2]][path_list[3]])
            if llen==5:
                json_object[path_list[0]][path_list[1]][path_list[2]][path_list[3]][path_list[4]] = valtouse
                #print(json_object[path_list[0]][path_list[1]][path_list[2]][path_list[3]][path_list[4]])
    # write updated values
    file = open(json_to_print, 'w')
    json.dump(json_object, file, indent=4) # remove , indent=4 if causes problems!
    file.close()


def ff_populater_picker(paramsj):
    global problem_list_code, i, j
    valuepicked = paramsj
    key = problem_list_code[i]
    if valuepicked == -99999:
        val_to_use = key[j][0]
    elif valuepicked == 99999:
        val_to_use = key[j][1]
    else:
        val_to_use = valuepicked
    return val_to_use



def find_avg_in_last_year(file_name, col_index, steady_state_day):
    """
    Here we're scraping the csv to return the 
    """
    result = []
    #global steady_state_day
    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 2
        for row in csv_reader:
            if line_count > steady_state_day+2: #plus column title and unit row
                if row[col_index] =='nan':
                    result.append(float(row[col_index]))
                elif type(ast.literal_eval(row[col_index])) == list or row[col_index]=='[]':
                    # print('yes')# col_index == 62 or col_index == 63: # to deal with column with lists, like 62 and 63
                    culled_heifer_age_list = ast.literal_eval(row[col_index])
                    result = result + culled_heifer_age_list
                elif  type(ast.literal_eval(row[col_index]))==str:
                    result.append(float(row[col_index]))
                else:
                    result.append(float(row[col_index]))
            line_count += 1
    if len(result) >= 365:
        return sum(result[-365:]) / 365
    else:
        llen = len(result)
        llen = 1 if llen == 0 else llen
        return sum(result) / llen

def firstlevel(jobj):
    """
    Simple function to find the highest level inside the json object
    Arg: jobj is a json object, as formatted by the json package
    """
    level0 = []
    for i in jobj:
        # print(i)
        level0.append(i)
    return level0


def find_json_terminal_variables1(jobj):
    """
    This traverses the json, using the firstlevel function
    Finds the terminal variables throughough
    It requires repeated nested hierarchical levels to find all terminal variables
    Currently works up to five levels deep, e.g. five hierarchies
    This returns a simple list of the terminal variable names
    This duplicates some functionality of the path_finder set of tools
    The benefit of this function is that it allows the user to see all possible variables
    The path_finder requires those names to be already known, e.g. it requires a specific input
    """
    listout = []
    levels_0 = firstlevel(jobj)
    for i in range(len(levels_0)):
        # print(i)
        # print(levels_0[i])
        # print(listout)
        if type(jobj[levels_0[i]]) ==dict:
            levels_1 = firstlevel(jobj[levels_0[i]])
            for j in range(len(levels_1)):
                #print(levels_0[i] + ":" + levels_1[j])
                #pass
                if type(jobj[levels_0[i]][levels_1[j]]) == dict:
                    levels_2 = firstlevel(jobj[levels_0[i]][levels_1[j]])
                    for k in range(len(levels_2)):
                        if type(jobj[levels_0[i]][levels_1[j]][levels_2[k]]) == dict:
                            levels_3 = firstlevel(jobj[levels_0[i]][levels_1[j]][levels_2[k]])
                            for l in range(len(levels_3)):
                                if type(jobj[levels_0[i]][levels_1[j]][levels_2[k]][levels_3[l]]) == dict:
                                    levels_4 = firstlevel(jobj[levels_0[i]][levels_1[j]][levels_2[k]][levels_3[l]])
                                    # print(levels_4)
                                    for m in range(len(levels_4)):
                                        # print(len(levels_4))
                                        # print(k)
                                        # print(l)
                                        listout.append(levels_4[m])
                                        # print(listout)
                                else:
                                    # pass
                                    ####print(levels_0[i] + ":" + levels_1[j] + ":" + levels_2[k])
                                    listout.append(levels_3[l])
                        else:
                            # pass
                            ####print(levels_0[i] + ":" + levels_1[j] + ":" + levels_2[k])
                            listout.append(levels_2[k])
                else: 
                    #####print(levels_0[i] + ":" + levels_1[j] )
                    listout.append(levels_1[j] )
        else:
            #####print(levels_0[i] )
            listout.append(levels_0[i])
        #print(levels_1)
    return listout


def find_json_terminal_variables2(jobj):
    """
    This traverses the json, using the firstlevel function
    Finds the terminal variables throughough
    It requires repeated nested hierarchical levels to find all terminal variables
    Currently works up to five levels deep, e.g. five hierarchies
    This returns a simple list of the full path for each terminal variable name
    This duplicates some functionality of the path_finder set of tools
    The benefit of this function is that it allows the user to see all possible variables
    The path_finder requires those names to be already known, e.g. it requires a specific input
    """
    listout = []
    levels_0 = firstlevel(jobj)
    for i in range(len(levels_0)):
        # print(i)
        # print(levels_0[i])
        # print(listout)
        if type(jobj[levels_0[i]]) ==dict:
            levels_1 = firstlevel(jobj[levels_0[i]])
            for j in range(len(levels_1)):
                #print(levels_0[i] + ":" + levels_1[j])
                #pass
                if type(jobj[levels_0[i]][levels_1[j]]) == dict:
                    levels_2 = firstlevel(jobj[levels_0[i]][levels_1[j]])
                    for k in range(len(levels_2)):
                        if type(jobj[levels_0[i]][levels_1[j]][levels_2[k]]) == dict:
                            levels_3 = firstlevel(jobj[levels_0[i]][levels_1[j]][levels_2[k]])
                            for l in range(len(levels_3)):
                                if type(jobj[levels_0[i]][levels_1[j]][levels_2[k]][levels_3[l]]) == dict:
                                    levels_4 = firstlevel(jobj[levels_0[i]][levels_1[j]][levels_2[k]][levels_3[l]])
                                    # print(levels_4)
                                    for m in range(len(levels_4)):
                                        # print(len(levels_4))
                                        # print(k)
                                        # print(l)
                                        listout.append(levels_0[i] + ":" + levels_1[j] + ":" + levels_2[k]+ ":" + levels_3[l]+ ":" + levels_4[m])
                                        # print(listout)
                                else:
                                    # pass
                                    ####print(levels_0[i] + ":" + levels_1[j] + ":" + levels_2[k])
                                    listout.append(levels_0[i] + ":" + levels_1[j] + ":" + levels_2[k]+ ":" + levels_3[l])
                        else:
                            # pass
                            ####print(levels_0[i] + ":" + levels_1[j] + ":" + levels_2[k])
                            listout.append(levels_0[i] + ":" + levels_1[j] + ":" + levels_2[k])
                else: 
                    #####print(levels_0[i] + ":" + levels_1[j] )
                    listout.append(levels_0[i] + ":" + levels_1[j] )
        else:
            #####print(levels_0[i] )
            listout.append(levels_0[i])
        #print(levels_1)
    return listout


def rewrite_ff_analysis(analysis):
    """
    This reformats the output of the ff_analysis function
    Forces into something easier to parse into csvs for printing
    This will place the main effects and interaction effects into grouped columns in a single dataframe
    """
    intnames = analysis['interaction_names']
    intnames = [str(x).replace('(', '') for x in intnames]
    intnames = [str(x).replace(')', '') for x in intnames]
    intnames = [str(x).replace(',', '*') for x in intnames]
    intnames = [str(x).replace(' ', '') for x in intnames]
    colnames = ['ME:'+x for x in analysis['names']] + ['IE:'+str(x) for x in intnames]
    rowvalues = list(analysis['ME']) + list(analysis['IE'])
    analysis_out = [colnames, rowvalues]
    return analysis_out
    # analysis
    # rewrite_ff_analysis(analysis)
    # print(*rewrite_ff_analysis(analysis), sep='\n')

def rewrite_sobol_analysis(analysis, p):
    """
    This reformats the output of the ff_sobol function
    Forces into something easier to parse into csvs for printing
    This will place the main effects and interaction effects into grouped columns in a single dataframe
    """
    intnames = p['names']
    colnames = ['S1:'+x for x in intnames] + ['ST:'+str(x) for x in intnames] + ['S2:'+str(x) for x in intnames] + ['S1_conf:'+x for x in intnames] + ['ST_conf:'+str(x) for x in intnames] + ['S2_conf:'+str(x) for x in intnames]
    rowvalues = list(analysis['S1']) + list(analysis['ST']) + list(analysis['S2']) 
    len(rowvalues)
    rowvalues[21]
    
    analysis_out = [colnames, rowvalues]
    return analysis_out




def anim_manag_modifier(inputJSONs_to_modify, s):
    """
    This function will modify the animal_management.json file
    It takes the json_to_print argument as the new value "inside" the json for where to look for the animal_management_animal.json
    It assumes the default location for animal_management.json
    It writes a new json following the string in the anim_manag_tomodify argument
    
    tested with the following
    
    json_to_print = 'C:\\Users\\jw2574\\Documents\\data\\MASM-yg_sensitivity-test\\input\\animal\\animal_management_animal_00007.json'
    
    anim_manag_tomodify = 'C:\\Users\\jw2574\\Documents\\data\\MASM-yg_sensitivity-test\\input\\animal_management_00007.json'

    """
    import os
    import json
    
    
    file = open(os.getcwd() + '\\input\\animal_management.json')
    json_object = json.load(file)
    file.close()

    for inputJSON in inputJSONs_to_modify:
        json_to_print = inputJSON[:-5] + '_' +  str(s).zfill(5) + '.json'
        cutoff = json_to_print.find('/')
        jsonname = json_to_print[cutoff+1:]
        if inputJSON == 'animal/animal_management_animal.json':
            json_object['farm']['animal'] = jsonname
        elif jsonname == 'feed/purchased_feed.json':
            json_object['farm']['feed'] = jsonname
        elif jsonname == 'manure/manure_management.json':
            json_object['farm']['manure'] = jsonname
        else:
            pass
    json_object['output'] = 'life_cycle_report_' + str(s).zfill(5) + '.json'
    anim_manag_tomodify = str(os.getcwd() + '\input\\' + 'animal_management' + '_' +  str(s).zfill(5) + '.json')

    file = open(anim_manag_tomodify, 'w')
    json.dump(json_object, file, indent=4) # remove , indent=4 if causes problems!
    file.close()


def lifecycle_modifier(lifecyclereport_tomodify, herdreportname):
    # herdreportname = 'herd_report_00007'
    # lifecyclereport_tomodify = 'C:\\Users\\jw2574\\Documents\\data\\MASM-yg_sensitivity-test\\input\\output\\life_cycle_report_00007.json'
    import os
    import json
    file = open(os.getcwd() + '\\input\\output\\life_cycle_report.json')
    json_object = json.load(file)
    file.close()
    
    json_object.keys()
    json_object['life_cycle_report']['herd_report']['report_name'] = herdreportname
    
    file = open(lifecyclereport_tomodify, 'w')
    json.dump(json_object, file, indent=4) # remove indent=4 if causes problems!
    file.close()
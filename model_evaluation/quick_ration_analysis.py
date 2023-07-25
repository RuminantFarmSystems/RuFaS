"""
File name: quick_ration_analysis.py

Description: Quick tool to explore ration_report files generated during simulation.
Model should first be run, then user can run this as a script for a printed summary.
Number of ration intervals to analyze can easily be modified in the code below

Author(s): Joseph Waddell, jw2574@cornell.edu

"""
import csv
import os
import json

def read_csv(filename):
    """
    Returns the contents read from the CSV file filename.
    
    This function reads the contents of the file filename and returns the contents as
    a 2-dimensional list. Each element of the list is a row, with the first row being
    the header. Cells in each row are all interpreted as strings; it is up to the 
    programmer to interpret this data, since CSV files contain no type information.
    
    Parameter filename: The file to read
    Precondition: filename is a string, referring to a file that exists, and that file 
    is a valid CSV file
    """
    csvout = []
    with open(filename, 'r') as file:
        csvfile = csv.reader(file)
        for line in csvfile:
            csvout.append(line)
    return csvout

def get_first_nums(key):
    listout = []
    for s in key:
        if s.isdigit():
            listout.append(s)
        else:
            break
    return int(''.join(listout))


def dict_convert(pen_report, i):
    num_animals = int(pen_report[i][2])
    ration_fed = {}
    percent_DMI = {}
    total_DMI = sum([float(pos)/float(num_animals) for pos in pen_report[i][3:]])
    keys = pen_report[0][3:]
    values = pen_report[i][3:]
    int_key_list = []
    key_list = []
    for pos, key in enumerate(keys):
        if values[pos] != '0':
            key_list.append(key)
            int_key_list.append(get_first_nums(key))
            ration_fed[key] = round(float(values[pos])/num_animals,4)
            percent_DMI[key] = round(float(values[pos])/num_animals/total_DMI, 4)*100
    
    # in order of sorted list
    # get the key from key_list
    # assign it to the new dict
    int_key_list_sorted = sorted(range(len(int_key_list)), key=lambda index:int_key_list[index])
    ration_fed_reordered = {key_list[n]: ration_fed[key_list[n]] for n in int_key_list_sorted}
    percent_DMI_reordered = {key_list[n]: percent_DMI[key_list[n]] for n in int_key_list_sorted}

    return num_animals, total_DMI, ration_fed_reordered, percent_DMI_reordered


def quickprint(pen_report, pen_name):
    print('\n ~~~~~~~ summary of ration_report for '+ str(pen_name) + ' ~~~~~~~ \n')
    print(pen_report[0][3:])
    # 
    iterator = 0
    for i in range(2,90,30):
        num_animals, total_DMI, ration_fed, percent_DMI = dict_convert(pen_report, i)
        print('')
        print('-----ration interval ' + str(iterator) + '-----')
        iterator+=1
        print('number of animals in pen = ' + str(num_animals))
        print('total fed DMI = ' + str(round(total_DMI, 2)) + ' kg')
        print('total kg of ration = ' + json.dumps(ration_fed, sort_keys = False, indent=4))
        print('percentage of DMI = ' + json.dumps(percent_DMI, sort_keys = False, indent=4))

pen0 = read_csv(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), 'output/CSVs/pen_report/pen_0/ration_report/ration_report.csv'))
pen1 = read_csv(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), 'output/CSVs/pen_report/pen_1/ration_report/ration_report.csv'))
pen2 = read_csv(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), 'output/CSVs/pen_report/pen_2/ration_report/ration_report.csv'))
pen3 = read_csv(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), 'output/CSVs/pen_report/pen_3/ration_report/ration_report.csv'))

quickprint(pen0, 'pen0')
quickprint(pen1, 'pen1')
quickprint(pen2, 'pen2')
quickprint(pen3, 'pen3')
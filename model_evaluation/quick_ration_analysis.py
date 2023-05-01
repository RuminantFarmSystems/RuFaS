"""
Quick tool to explore ration_reports faster than doing these calcs in excel
"""

import csv
import os
from config import global_variables

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

def quickprint(ccc, pen_name):
    print('\n ~~~~~~~ summary of ration_report for '+ str(pen_name) + ' ~~~~~~~ \n')
    print(ccc[0][4:])
    # 
    for i in range(2,90,30):
        num_animals = ccc[i][2]
        print('\n')
        print('num_animals = '+str(num_animals))
        [float(pos)/float(num_animals) for pos in ccc[i][4:]]
        print('ration fed = '+ str([float(pos)/float(num_animals) for pos in ccc[i][4:]]))
        summed = sum([float(pos)/float(num_animals) for pos in ccc[i][4:]])
        print('total kg of ration = '+str(summed))
        print('percentage of DMI = '+str([round(float(pos)/float(num_animals)/summed,4) for pos in ccc[i][4:]]))
        print('\n')



pen0 = read_csv(os.path.join(global_variables.ROOT_DIR, 'output\\CSVs\\pen_report\\pen_0\\ration_report\\ration_report.csv'))
pen1 = read_csv(os.path.join(global_variables.ROOT_DIR, 'output\\CSVs\\pen_report\\pen_1\\ration_report\\ration_report.csv'))
pen2 = read_csv(os.path.join(global_variables.ROOT_DIR, 'output\\CSVs\\pen_report\\pen_2\\ration_report\\ration_report.csv'))
pen3 = read_csv(os.path.join(global_variables.ROOT_DIR, 'output\\CSVs\\pen_report\\pen_3\\ration_report\\ration_report.csv'))
        
quickprint(pen0, 'pen0')
quickprint(pen1, 'pen1')
quickprint(pen2, 'pen2')
quickprint(pen3, 'pen3')
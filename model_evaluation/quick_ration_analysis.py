"""
File name: quick_ration_analysis.py

Description: Quick tool to explore ration_report files generated during simulation.
Model should first be run, then user can run this as a script for a printed summary.
Number of ration intervals to analyze can easily be modified in the code below

Author(s): Joseph Waddell, jw2574@cornell.edu

"""
import csv
import os

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

def quickprint(pen_report, pen_name):
    print('\n ~~~~~~~ summary of ration_report for '+ str(pen_name) + ' ~~~~~~~ \n')
    print(pen_report[0][4:])
    # 
    for i in range(2,90,30):
        num_animals = pen_report[i][2]
        print('\n')
        print('num_animals = '+str(num_animals))
        summed = sum([float(pos)/float(num_animals) for pos in pen_report[i][4:]])
        print('total kg of ration = '+str(round(summed,4)))
        [float(pos)/float(num_animals) for pos in pen_report[i][4:]]
        print('ration fed = '+ str([round(float(pos)/float(num_animals),4) for pos in pen_report[i][4:]]))
        print('percentage of DMI = '+str([round(float(pos)/float(num_animals)/summed,4) for pos in pen_report[i][4:]]))
        print('\n')

pen0 = read_csv(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), 'output/CSVs/pen_report/pen_0/ration_report/ration_report.csv'))
pen1 = read_csv(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), 'output/CSVs/pen_report/pen_1/ration_report/ration_report.csv'))
pen2 = read_csv(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), 'output/CSVs/pen_report/pen_2/ration_report/ration_report.csv'))
pen3 = read_csv(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), 'output/CSVs/pen_report/pen_3/ration_report/ration_report.csv'))
        
quickprint(pen0, 'pen0')
quickprint(pen1, 'pen1')
quickprint(pen2, 'pen2')
quickprint(pen3, 'pen3')
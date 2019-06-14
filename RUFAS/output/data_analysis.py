"""
RUFAS: Ruminant Farm Systems Model

File name: data_analysis.py

Author(s): Jacob Johnson, jacob8399@gmail.com
           William Donovan, wmdonovan@wisc.edu

Description: Produces graphical representations of RuFaS output data.
"""

import matplotlib.pyplot as mp, datetime as dt, csv


#
# Produces graphical representations of data passed in from a csv file.
#
from RUFAS import util


def data_analysis(output_csv, show_diagnostics, is_final):

    output_full_path = util.get_base_dir() / 'Outputs/Sample_Farm_Outputs' / output_csv
    save_dir = util.get_base_dir() / 'Outputs/diagnostics/' / output_csv.split('.')[0]

    with open(output_full_path) as csvfile:
        read_CSV = csv.reader(csvfile, delimiter=',')

        variables = {}
        units = []

        r = 0
        for row in read_CSV:
            if r == 0:
                for variable in row:
                    variable_list = []
                    variables[variable.lower()] = variable_list
            elif r == 1:
                for unit in row:
                    units.append(unit)
            else:
                c = 0
                for variable in variables:
                    variables[variable].append(float(row[c]))
                    c += 1
            r += 1

        start_year = int(variables['year'][0])
        start_day = int(variables['julian day'][0])
        start_date = dt.datetime(int(start_year), 1, 1) + dt.timedelta(start_day - 1)

        dates = [start_date + dt.timedelta(days=i) for i in range(len(variables['julian day']))]

        counter = 0
        for variable in variables:
            if counter > 1:
                mp.figure()
                mp.plot(dates, variables[variable])
                mp.title(variable.split()[0].upper())
                mp.xlabel('Dates')
                mp.ylabel(variable + " " + units[counter])
                path = str(save_dir / variable)
                mp.savefig(path + '')
                if not show_diagnostics:
                    mp.close()
                counter += 1

        if is_final:
            mp.show()

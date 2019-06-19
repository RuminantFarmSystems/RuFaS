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


def data_analysis(output_csv, show_diagnostics, produce_diagnostics, is_final):

    if produce_diagnostics:

        output_full_path = util.get_base_dir() / 'Outputs/Sample_Farm_Outputs' / output_csv

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

        if output_csv.endswith('_report.csv'):

            save_dir = util.get_base_dir() / 'Outputs/diagnostics/' / output_csv.split('.')[0]

            start_year = int(variables['year'][0])
            start_day = int(variables['julian day'][0])
            # start date
            date = dt.datetime(int(start_year), 1, 1) + dt.timedelta(start_day - 1)

            dates = []
            for i in range(len(variables['julian day'])):
                dates.append(date)
                date += dt.timedelta(days=7)

            counter = 0
            for variable in variables:
                if counter > 1:
                    mp.figure()
                    mp.plot(dates, variables[variable])
                    mp.title(variable.split()[0].upper())
                    mp.xlabel('Dates')
                    mp.ylabel(variable + ' ' + units[counter])
                    path = str(save_dir / variable)
                    mp.savefig(path + '')
                    if not show_diagnostics:
                        mp.close()
                counter += 1

        elif output_csv.endswith('_annual.csv'):

            save_dir = util.get_base_dir() / 'Outputs/diagnostics/' / output_csv.split('.')[0].strip('_annual')

            mp.figure()
            counter = 0
            years = variables['year']
            legend = []
            prev_vars = [0 for x in range(len(years))]
            width = 0.35
            table_vals = []
            row_labs = []
            colors = ['', '', '#1561ad', '#fbaf08', '#51d0de', '#431c5d']
            for variable in variables:
                if 1 < counter < 6:
                    mp.bar(years, variables[variable], width, color=colors[counter], bottom=prev_vars)
                    legend.append(variable)
                    prev_vars = [sum(x) for x in zip(prev_vars, variables[variable])]
                if counter == 6:
                    precip = variables[variable]
                    legend.insert(0, variable)
                    mp.scatter(years, precip, c='black', marker='x')
                if counter > 1:
                    table_vals.append(variables[variable])
                    row_labs.append(variable)
                counter += 1

            table = mp.table(cellText=table_vals,
                     rowLabels=row_labs,
                     bbox=[0, -.9, 1, .75])

            mp.legend(legend, loc='best')
            mp.subplots_adjust(left=0.31, bottom=0.5)
            # mp.xlabel('Dates')
            mp.ylabel('mm H2O')
            mp.title('Annual Water Balance')
            path = str(save_dir / 'annual_water_balance')
            mp.savefig(path + '')
            if not show_diagnostics:
                mp.close()

        else:

            save_dir = util.get_base_dir() / 'Outputs/diagnostics/' / output_csv.split('.')[0]

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
                    mp.ylabel(variable + ' ' + units[counter])
                    path = str(save_dir / variable)
                    mp.savefig(path + '')
                    if not show_diagnostics:
                        mp.close()
                counter += 1

    if is_final:
        mp.show()

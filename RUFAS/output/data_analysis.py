"""
RUFAS: Ruminant Farm Systems Model

File name: data_analysis.py

Author(s): Jacob Johnson, jacob8399@gmail.com
           William Donovan, wmdonovan@wisc.edu

Description: Produces graphical representations of RuFaS output data.
"""

import csv
import datetime as dt
import matplotlib.pyplot as mp
import random

#
# Produces graphical representations of data passed in from a csv file.
#
from RUFAS import util


# reads all the data from a csv and puts it in a dictionary with each variable
def read_data(output_csv):
    output_full_path = util.get_base_dir() / 'Outputs/Sample_Farm_Outputs' / output_csv

    with open(output_full_path) as csvfile:
        read_csv = csv.reader(csvfile, delimiter=',')

        variables = {}
        units = []

        r = 0
        for row in read_csv:
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
    return variables, units


# data analytics for ration
def ration_data_analysis(output_csv, show_daily, produce_diagnostics, is_final, ration_interval):

    if produce_diagnostics:
        variables, units = read_data(output_csv)

        save_dir = util.get_base_dir() / 'Outputs/diagnostics/' / output_csv.split('.')[0]

        start_year = int(variables['year'][0])
        start_day = int(variables['j_day'][0])
        # start date
        date = dt.datetime(int(start_year), 1, 1) + dt.timedelta(start_day - 1)

        dates = []
        for i in range(len(variables['j_day'])):
            dates.append(date)
            date += dt.timedelta(days=ration_interval)

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
                if not show_daily:
                    mp.close()
            counter += 1

    show_figures(is_final)


# produces the annual data analytics
def annual_data_analysis(output_csv, show_annual, produce_diagnostics):
    if produce_diagnostics:
        variables, units = read_data(output_csv)

        save_dir = util.get_base_dir() / 'Outputs/diagnostics/' / output_csv.split('.')[0].strip('_annual')

        mp.figure()
        counter = 0
        years = variables['year']
        legend = []
        prev_vars = [0 for x in range(len(years))]
        width = 0.35
        table_vals = []
        row_labs = []

        added_variables = len(variables) - 9

        colors = ['#ffffff', '#DC267F', '#648FFF', '#FFB000',  '#FE6100', '#785EF0', '#8B0000']
        for variable in variables:
            # assigns a random color to variables not originally included
            if len(colors) - 2 < counter < len(variables) - 3:
                colors.insert(counter, "#"+''.join([random.choice('1236789ABCDE') for j in range(6)]))

            # 0 through 6 are outputs we would not change
            # 6 is precip which we do not want as a bar in the graph
            if 0 < counter < len(variables) - 3:
                mp.bar(years, variables[variable], width, color=colors[counter], bottom=prev_vars)
                legend.append(variable)
                prev_vars = [sum(x) for x in zip(prev_vars, variables[variable])]
            elif counter == len(variables) - 3:
                precip = variables[variable]
                legend.insert(0, variable)
                mp.scatter(years, precip, c='#8B0000', marker='x', zorder=2)
            if counter > 0:
                variables[variable].insert(0, "")
                table_vals.append(variables[variable])
                row_labs.append(variable)
            counter += 1

        cell_colors = [['#ffffff' for i in range(len(years) + 1)] for j in range(len(variables) - 1)]
        for x in range(len(colors)):
            cell_colors[x - 1][0] = colors[x]

        # original bbox values with 9 variables ( len(variables) )
        table_bot = -1.08
        table_height = 0.75

        # added bbox adjustments when there are more variables
        table_bot -= 0.08 * added_variables
        table_height += 0.08 * added_variables

        mp.xticks(rotation=45)

        mp.axis('tight')
        table = mp.table(cellText=table_vals,
                         rowLabels=row_labs,
                         cellColours=cell_colors,
                         bbox=[0, table_bot, 1, table_height])

        # creates the color indicator in the table
        cellDict = table.get_celld()
        for x in range(len(cell_colors)):
            cellDict[(x, 0)].set_width(0.02)

        # legend toggle
        # mp.legend(legend, loc='upper center', bbox_to_anchor=(-0.35, 1.3), ncol=1, prop={'size': 9})
        mp.subplots_adjust(left=0.31, bottom=0.5)
        mp.ylabel('mm H2O')
        mp.title('Annual Water Balance')
        path = str(save_dir / 'annual_water_balance')
        mp.savefig(path + '')

        if not show_annual:
            mp.close()


# produces the daily data analysis
def data_analysis(output_csv, show_daily, produce_diagnostics, is_final):

    if produce_diagnostics:
        variables, units = read_data(output_csv)

        save_dir = util.get_base_dir() / 'Outputs/diagnostics/' / output_csv.split('.')[0]

        start_year = int(variables['year'][0])
        start_day = int(variables['j_day'][0])
        # creates the date ticks for the graphs
        start_date = dt.datetime(start_year, 1, 1) + dt.timedelta(start_day - 1)

        dates = [start_date + dt.timedelta(days=i) for i in range(len(variables['j_day']))]

        counter = 0
        # for each variable, create the figure and save it
        for variable in variables:
            if counter > 1:
                mp.figure()
                mp.plot(dates, variables[variable])
                mp.xticks(rotation=45)
                mp.title(variable.split()[0].upper())
                mp.xlabel('Dates')
                mp.ylabel(variable + ' ' + units[counter])
                mp.tight_layout()
                path = str(save_dir / variable)
                mp.savefig(path + '')
                if not show_daily:
                    mp.close()
            counter += 1

    show_figures(is_final)


# shows figures on screen for manipulation
def show_figures(is_final):
    if is_final:
        mp.show()

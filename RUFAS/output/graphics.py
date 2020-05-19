"""
RUFAS: Ruminant Farm Systems Model
File name: graphics.py

Author(s): Jacob Johnson, jacob8399@gmail.com
           William Donovan, wmdonovan@wisc.edu

Description: Produces graphical representations of RuFaS output data
                using matplotlib.
"""

import csv
import datetime as dt
import matplotlib.pyplot as mp
import random


def read_data(report, file_name):
    """
    Description:
        Reads all the data from a csv into a dictionary representing the
        reported variables
    Args:
        output_csv: file path to the csv containing the data to be read
    """

    output_full_path = report.output_dir / file_name

    with open(output_full_path) as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')

        # dictionary representing the read data in the format {variable: values}
        variables = {}
        units = []

        r = 0
        for row in read_csv:

            # the first row in the csv file contains the variable names
            if r == 0:
                for variable in row:
                    variable_list = []
                    variables[variable.lower()] = variable_list

            # the second row represents the units
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


def ration_graphics(report, ration_interval):
    """
    Description:
        Graphics handler for the ration report.
    Args:
        output_csv: the report for which graphics are being produced
        produce_graphics: indicates whether graphics should be produced for this report
    """

    if report.produce_graphics:
        variables, units = read_data(report, report.file_name)

        save_dir = report.diagnostic_dir

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
                mp.close()
            counter += 1


def annual_water_balance_graphic(report):
    """
    Description:
        Graphic handler for the specific annual water balance bar graph report.
    Args:
        report: the report for which graphics are being produced
    """

    if report.produce_graphics:
        variables, units = read_data(report, report.annual_file_name)

        save_dir = report.diagnostic_dir

        mp.figure()
        counter = 0
        years = variables['year']
        legend = []
        prev_vars = [0 for _ in range(len(years))]
        width = 0.35
        table_vals = []
        row_labs = []

        added_variables = len(variables) - 9

        # bar graph colors– currently implemented for colorblindness
        colors = ['#ffffff', '#DC267F', '#648FFF', '#FFB000',  '#FE6100', '#785EF0', '#8B0000']

        for variable in variables:

            # assigns a random color to variables not originally included
            # not currently implemented for colorblindness
            if len(colors) - 2 < counter < len(variables) - 3:
                colors.insert(counter, "#"+''.join([random.choice('1236789ABCDE') for _ in range(6)]))

            # 0 through 6 are outputs we would not change
            # 6 is total actual precipitation, represented as an x on the graph
            if 0 < counter < len(variables) - 3:

                mp.bar(years, variables[variable], width, color=colors[counter], bottom=prev_vars)
                legend.append(variable)

                # add each bar to the previous one in order to create
                # illusion of stacking
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

        # create the table. colorblind friendly
        cell_colors = [['#ffffff' for _ in range(len(years) + 1)] for _ in range(len(variables) - 1)]
        for x in range(len(colors)):
            cell_colors[x - 1][0] = colors[x]

        # original bbox values with 9 variables ( len(variables) )
        table_bot = -1.08
        table_height = 0.75

        # bbox adjustments when there are more variables
        table_bot -= 0.08 * added_variables
        table_height += 0.08 * added_variables

        mp.xticks(rotation=45)

        mp.axis('tight')
        table = mp.table(cellText=table_vals,
                         rowLabels=row_labs,
                         cellColours=cell_colors,
                         bbox=[0, table_bot, 1, table_height])

        # creates the color indicator in the table
        cell_dict = table.get_celld()
        for x in range(len(cell_colors)):
            cell_dict[(x, 0)].set_width(0.02)

        # legend toggle
        # mp.legend(legend, loc='upper center', bbox_to_anchor=(-0.35, 1.3), ncol=1, prop={'size': 9})

        mp.subplots_adjust(left=0.31, bottom=0.5)
        mp.ylabel('mm H2O')
        mp.title('Annual Water Balance')
        path = str(save_dir / 'annual_water_balance')
        mp.savefig(path + '')

        mp.close()


def daily_graphics(report):
    """
    Description:
        Graphics handler for standard daily output.
    Args:
        report: the report for which graphics are being produced
    """

    if report.produce_graphics:
        variables, units = read_data(report, report.file_name)

        save_dir = report.diagnostic_dir

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
                mp.close()
            counter += 1


def annual_graphics(report):
    """
    Description:
        Graphics handler for standard annual output.
    Args:
        report: the report for which graphics are being produced
    """

    if report.produce_graphics:
        variables, units = read_data(report, report.annual_file_name)
        save_dir = report.diagnostic_dir

        start_year = int(variables['year'][0])
        end_year = int(variables['year'][-1])

        dates = [x for x in range(start_year, end_year + 1)]

        counter = 0
        for variable in variables:
            if counter > 0:
                mp.figure()
                mp.plot(dates, variables[variable])
                mp.xticks(rotation=45)
                mp.title(variable.split()[0].upper())
                mp.xlabel('Dates')
                mp.ylabel(variable + ' ' + units[counter])
                mp.tight_layout()
                path = str(save_dir / variable) + '_annual'
                mp.savefig(path + '')
                mp.close()
            counter += 1

"""
RUFAS: Ruminant Farm Systems Model
File name: graphics.py

Description: Produces graphical representations of RuFaS output data.

Author(s): Jacob Johnson, jacob8399@gmail.com
           William Donovan, wmdonovan@wisc.edu
"""

import csv
import datetime as dt
import random
from pathlib import Path

import matplotlib.pyplot as mp
from pandas.plotting import register_matplotlib_converters


# reads all the data from a csv and puts it in a dictionary with each variable
def read_data(report, output_csv):
    output_full_path = Path(str(report.csv_dir) + '/' + output_csv)

    with open(output_full_path) as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')

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
def ration_graphics(report):
    if report.produce_graphics:
        register_matplotlib_converters()
        output_csv = report.file_name
        variables, units = read_data(report, output_csv)

        save_dir = report.graphic_dir

        start_year = int(variables['year'][0])
        start_day = int(variables['j_day'][0])
        # start date
        date = dt.datetime(int(start_year), 1, 1) + dt.timedelta(start_day - 1)

        dates = []
        for i in range(len(variables['j_day'])):
            dates.append(date)
            date += dt.timedelta(days=report.ration_interval)

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


def annual_mass_balance_graphics(report):
    if report.produce_graphics:
        annual_file_name = str(report.file_name).split('.')[0] + "_annual.csv"
        variables, units = read_data(report, annual_file_name)

        save_dir = report.graphic_dir
        mp.figure()

        variables_size = len(variables)
        width = 0.35

        table_dict = {
            'year': variables.pop('year'),
            'actual': variables.pop('actual'),
            'calculated': variables.pop('calculated'),
            'difference': variables.pop('difference')
        }

        prev_vars = [0 for _ in range(len(table_dict['year']))]

        cell_colors = [['#ffffff' for _ in range(len(table_dict['year']) + 1)] for _ in range(variables_size)]
        cell_colors[1][0] = '#8B0000'

        colors = ['#ffffff', '#785EF0', '#FE6100', '#FFB000', '#648FFF', '#DC267F']

        mp.scatter(table_dict['year'], table_dict['actual'], c='#8B0000', marker='x', zorder=2)
        for variable in variables:
            if len(colors) == 0:
                colors.append("#" + ''.join([random.choice('1236789ABCDE') for _ in range(6)]))

            color = colors.pop()
            cell_colors[len(table_dict)][0] = color

            mp.bar(table_dict['year'], variables[variable], width, color=color, bottom=prev_vars)
            prev_vars = [sum(x) for x in zip(prev_vars, variables[variable])]
            table_dict[variable] = variables[variable]

        mp.xticks(rotation=45)
        mp.axis('tight')
        table_bot = -1.08
        table_height = 0.75

        # creation of the blank cell to store the color
        cell_text = list(table_dict.values())
        for x in range(len(cell_text)):
            cell_text[x].insert(0, "")

        table = mp.table(cellText=cell_text,
                         rowLabels=list(table_dict.keys()),
                         cellColours=cell_colors,
                         bbox=[0, table_bot, 1, table_height])

        # creates the color indicator in the table
        cell_dict = table.get_celld()
        for x in range(len(cell_text)):
            cell_dict[(x, 0)].set_width(0.02)

        mp.title(report.report_name)
        # legend = ['actual']
        # mp.legend(legend, loc="upper left")
        mp.subplots_adjust(left=0.31, bottom=0.5)

        path = str(save_dir) + '/' + 'annual_' + report.report_name
        mp.savefig(path + '')

        mp.close()


def individual_animal_graphics(report):
    # for selected animals, days_born on x-axis and body_weight and
    # milk_production on y-axes
    if report.produce_graphics:
        register_matplotlib_converters()
        animals = report.animals
        save_dir = report.graphic_dir

        for (animal, animal_type, is_cow) in animals:
            body_weight = [weight_hist.__dict__
                           for weight_hist in animal.body_weight_history]
            body_weight = {bw['days_born']: bw['body_weight'] for bw in body_weight}

            days_born = body_weight.keys()

            # skip this animal if there is no data (i.e. calf born on last day)
            if not days_born:  # equivalent to days_born == []
                continue

            first_day_born_on_farm = min(days_born)

            if is_cow:
                milk_production = [milk_hist.__dict__
                                   for milk_hist in animal.milk_production_history]
                milk_production = {milk['days_born']: (
                    milk['milk_production'] if milk[
                                                   'milk_production'] > 0 else None)
                                   for milk in milk_production}

                for i in range(first_day_born_on_farm, min(milk_production.keys())):
                    milk_production[i] = None

            else:
                milk_production = {day: None for day in days_born}

            fig, ax = mp.subplots()
            fig.suptitle(animal_type + ' ' + str(animal.id))
            ax.plot(list(milk_production.keys()), list(milk_production.values()),
                    color='red')
            ax.set_xlabel('Days Born')
            ax.set_ylabel('Milk Production (kg)', color='red')

            ax2 = ax.twinx()
            ax2.plot(list(body_weight.keys()), list(body_weight.values()),
                     color='blue')
            ax2.set_ylabel('Body Weight (kg)', color='blue')

            mp.savefig(str(save_dir) + '/' + str(animal.id) + '.png')
            mp.close()


# produces the daily data analysis
def daily_graphics(report):
    if report.produce_graphics:
        register_matplotlib_converters()
        output_csv = report.file_name
        variables, units = read_data(report, output_csv)

        save_dir = report.graphic_dir

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
    if report.produce_graphics:
        register_matplotlib_converters()
        annual_file_name = str(report.file_name).split('.')[0] + "_annual.csv"
        variables, units = read_data(report, annual_file_name)
        save_dir = report.graphic_dir

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

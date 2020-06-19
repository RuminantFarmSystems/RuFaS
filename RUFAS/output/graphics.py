"""
RUFAS: Ruminant Farm Systems Model
File name: graphics.py

Description: Produces graphical representations of RuFaS output data.

Author(s): Jacob Johnson, jacob8399@gmail.com
           William Donovan, wmdonovan@wisc.edu
"""

import csv
import datetime as dt
from pathlib import Path

import matplotlib.pyplot as mp
import random


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
        output_csv = report.file_name
        variables, units = read_data(report, output_csv)

        save_dir = report.diagnostic_dir

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

        save_dir = report.diagnostic_dir

        mp.figure()

        legend = []
        width = 0.35
        table_dict = {
            'year': variables.pop('year'),
            'actual': variables.pop('actual'),
            'calculated': variables.pop('calculated'),
            'difference': variables.pop('difference'),
            'delta': variables.pop('delta')
        }
        prev_vars = [0 for _ in range(len(table_dict['year']))]

        colors = ['#ffffff', '#DC267F', '#648FFF', '#FFB000', '#FE6100', '#785EF0', '#8B0000']

        mp.scatter(table_dict['year'], table_dict['actual'], c='#8B0000', marker='x', zorder=2)
        for variable in variables:
            if len(colors) == 0:
                colors.append("#" + ''.join([random.choice('1236789ABCDE') for _ in range(6)]))

            mp.bar(table_dict['year'], variables[variable], width, color=colors.pop(), bottom=prev_vars)
            prev_vars = [sum(x) for x in zip(prev_vars, variables[variable])]
            table_dict[variable] = variables[variable]
            legend.append(variable)

        mp.xticks(rotation=45)
        mp.axis('tight')
        table_bot = -1.08
        table_height = 0.75
        mp.table(cellText=list(table_dict.values()),
                 rowLabels=list(table_dict.keys()),
                 bbox=[0, table_bot, 1, table_height])
        mp.title(report.report_name)
        mp.legend(legend)
        mp.subplots_adjust(left=0.31, bottom=0.5)

        path = str(save_dir) + '/' + 'annual_' + report.report_name
        mp.savefig(path + '')

        mp.close()


# produces the daily data analysis
def daily_graphics(report):
    if report.produce_graphics:
        output_csv = report.file_name
        variables, units = read_data(report, output_csv)

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
    if report.produce_graphics:
        annual_file_name = str(report.file_name).split('.')[0] + "_annual.csv"
        variables, units = read_data(report, annual_file_name)
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

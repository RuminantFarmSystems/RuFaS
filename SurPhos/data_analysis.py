import csv
import datetime as dt
import matplotlib.pyplot as mp
from SurPhos import util


def read_data(output_csv):
    output_full_path = util.get_base_dir()/output_csv
    with output_full_path.open('r') as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')

        variables = {}
        units = []

        r = 0
        for row in read_csv:
            if r == 0:
                for variable in row:
                    variables_list = []
                    variables[variable] = variables_list
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


def produce_graphics():
    fortran, units = read_data('SurPhos/surphos_doody3.csv')
    python, units = read_data('SurPhos/output/surphos_report.csv')

    if len(python['year']) != len(fortran['year']):
        fortran, units = read_data('output/surphos_report.csv')
        print("Could not compare Fortran and Python because of different simulation lengths.",
              "\n\t*Showing Python*")

    save_dir = util.get_base_dir()/'SurPhos/output'

    start_year = int(fortran['year'][0])
    start_day = int(fortran['j_day'][0])

    date = dt.datetime(start_year, 1, 1) + dt.timedelta(start_day - 1)

    dates = []
    for i in range(len(fortran['j_day'])):
        dates.append(date)
        date += dt.timedelta(days=1)

    counter = 0
    for variable in zip(python, fortran):
        if counter > 1:
            # print(variable, sum(fortran[variable[1]]) - sum(python[variable[0]]))
            mp.figure()
            mp.plot(dates, fortran[variable[1]])
            mp.plot(dates, python[variable[0]])
            mp.xticks(rotation=45)
            mp.legend(['fortran', 'python'])
            mp.xlabel('Dates')
            mp.ylabel(variable[0] + ' ' + units[counter])
            mp.title(variable[0])
            mp.tight_layout()
            mp.savefig(save_dir / variable[0])
            mp.close()
        counter += 1

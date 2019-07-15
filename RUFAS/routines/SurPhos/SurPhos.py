import csv
from math import log
from pathlib import Path


def daily_P_routine():
    manure()
    plow()
    solP()
    fert_leach()
    man_leach()
    P_mineralization()
    write_day()

class SurPhos():
    def __init__(self):
        print('here')
        self.time = Time()
        self.weather = Weather(self.time)

        self.cover = 3
        self.leach = 0.0
        self.area = 1.0

        self.soil_layers = 3
        self.depths_layer = [2.5, 15.0, 75.0]
        self.labile_P_layer = [23.7, 10.0, 10.0]
        self.clay_layer = [20.0, 20.0, 20.0]
        self.OM_layer = [4.8, 3.4, 2.0]
        self.bulk_density_layer = [1.3, 1.3, 1.3]
        self.OC_layer = []
        self.PSP_layer = []
        self.thick_layer = []
        self.active_P_layer = []
        self.stable_P_layer = []
        self.org_P_layer = []
        self.CNT_day_layer = []

        for x in range(self.soil_layers):
            if x == 0:
                self.thick_layer.append(self.depths_layer[x])
            else:
                self.thick_layer.append(self.depths_layer[x] - self.depths_layer[x - 1])

            self.OC_layer.append(self.OM_layer[x] * 0.58)

            self.PSP_layer.append(-0.045 * log(self.clay_layer[x]) + 0.001 *
                                  self.labile_P_layer[x] - 0.035 * self.OC_layer[x]
                                  + 0.43)
            self.labile_P_layer[x] = self.labile_P_layer[x] * self.bulk_density_layer[x] * self.thick_layer[x] * 0.1

            self.active_P_layer.append(self.labile_P_layer[x] * (1.0 - self.PSP_layer[x])
                                       / self.PSP_layer[x])

            self.stable_P_layer.append(self.active_P_layer[x] * 4.0)

            self.org_P_layer.append(self.OC_layer[x] / 8.0 / 14.0 * 10000 *
                                    self.bulk_density_layer[x] * self.thick_layer[x] * 0.1)

            self.CNT_day_layer.append(0.0)

        self.moisture = 0.5
        self.CNT = 1
        self.manure_cov = 0.0
        self.manure_mass = 0.0
        self.cover_SLP = 0.000025


class Time:
    def __init__(self):
        self.start_year = 2012
        self.start_day = 102
        self.end_year = 2013
        self.end_day = 335

        self.day = self.start_day
        self.year = self.start_year


class Weather:
    def __init__(self, time):
        self.rainfall = []
        self.runoff = []
        self.temp = []

        self.years = 2

        for i in range(self.years):
            self.rainfall.append([])
            self.runoff.append([])
            self.temp.append([])

        day = 0
        while day < time.start_day - 1:
            self.rainfall[0].append(0)
            self.runoff[0].append(0)
            self.temp[0].append(0)
            day += 1

        self.weather_csv = 'SurPhos_weather.csv'

        with open(self.weather_csv, 'r') as f:
            readCSV = csv.reader(f, delimiter=',')

            curr_row = 0
            year = 0

            for row in readCSV:
                if curr_row == 0:
                    curr_row += 1
                else:
                    self.rainfall[year].append(float(row[2]))
                    self.runoff[year].append(float(row[3]))
                    self.temp[year].append(float(row[4]))
                    if day == 364:
                        year += 1
                        day = -1
                    day += 1


def main():
    surphos = SurPhos()
    daily_P_routine(surphos)


if __name__ == '__main__':
    main()
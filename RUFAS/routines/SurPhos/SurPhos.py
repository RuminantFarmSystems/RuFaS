import csv
from math import log

from . import fert_leach, fertilizer, manure, manure_leach, p_mineralization, plow, sol_P


def daily_P_routine(surphos, weather, time):
    fertilizer.update_all(surphos, time)  # done
    manure.update_all(surphos)
    plow.update_all(surphos, time)  # done
    sol_P.update_all(surphos, weather, time)  # done
    fert_leach.update_all(surphos, weather, time)
    manure_leach.update_all(surphos)
    p_mineralization.update_all(surphos)


class SurPhos:
    def __init__(self):
        self.time = Time()
        self.weather = Weather(self.time)
        self.manure_app = Manure()
        self.fertilizer_app = Fertilizer()
        self.tillage_app = Tillage()
        self.crop_P_uptake = CropPUptake()

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

        # default values
        self.moisture = 0.5
        self.CNT = 1
        self.manure_cov = 0.0
        self.manure_mass = 0.0
        self.cover_SLP = 0.000025

        # fertilizer
        self.fert_applied_sum = 0.0
        self.no_rains = 0.0
        self.fert_CNT = 0.0
        self.fert_p_available = 0.0 # avfrtp
        self.fert_p_released = 0.0  # rsfrtp
        self.fact = 0.0

        # manure
        self.WIP = 0.0
        self.WOP = 0.0
        self.SIP = 0.0
        self.SOP = 0.0

        # plow

        # solp
        self.soil_P = [0, 0, 0]
        self.SRP_sum = 0.0

        # fert_leach
        self.fert_sorp = 0.0
        self.fert_absorbed_sum = 0.0
        self.fert_leach = 0.0
        self.PD_factor = 0.0
        self.fert_runoff_P = 0.0


class Fertilizer:
    def __init__(self):
        self.year = [0]
        self.day = [0]
        self.mass = [0.0]
        self.depth = [0.0]
        self.surface_percent = [0.0]


class Manure:
    def __init__(self):
        self.type = 1
        self.year = [2012, 2012, 2012, 2012, 2013, 2013, 2013, 2013]
        self.day = [103, 176, 226, 283, 46, 155, 241, 273]
        self.mass = [1320.0, 2120.0, 1329.0, 2228.0, 1250.0, 1587.0, 1750.0, 1555.0]
        self.total_P = [0.00820, 0.00866, 0.00941, 0.00656, 0.00748, 0.00698, 0.00721, 0.00646]
        self.WIP_rate = 0.6
        self.WOP_rate = 0.05
        self.dry_matter = [0.04, 0.07, 0.04, 0.04, 0.05, 0.05, 0.07, 0.06]
        self.percent_cover = 0.95
        self.depth = 0.0
        self.surface_percent = 1.0


class Tillage:
    def __init__(self):
        self.year = [0]
        self.day = [0]
        self.percent_incorporated = [0.0]
        self.percent_mixed = [0.0]
        self.depth = [0.0]


class CropPUptake:
    def __init__(self):
        self.year = [2012, 2013]
        self.P_uptake = 25.0


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
    while surphos.time.year != surphos.time.end_year and surphos.time.day != surphos.time.end_day:
        daily_P_routine(surphos, surphos.weather, surphos.time)

        if surphos.time.day == 364:
            surphos.time.year += 1
            surphos.time.day = -1
        surphos.time.day += 1


if __name__ == '__main__':
    main()

import csv
import json

from math import log

from SurPhos import util, surphos_summary, data_analysis
from SurPhos.routines import p_mineralization, manure, plow, fertilizer, manure_leach, sol_P, fert_leach


def simulate(json_file):

    clear_output_dir()

    with json_file.open('r') as f:
        data = json.load(f)

        surphos = SurPhos(data)

    report = surphos_summary.SurPhosSummary()
    report.initialize()
    while not (surphos.time.year == surphos.time.end_year - surphos.time.start_year
               and surphos.time.day == surphos.time.end_day + 1):
        daily_P_routine(surphos, surphos.weather, surphos.time)
        report.daily_update(surphos)
        if surphos.time.day == len(surphos.weather.rainfall[surphos.time.year])\
                and surphos.time.year != surphos.time.end_year - surphos.time.start_year:
            surphos.time.year += 1
            surphos.time.day = 0
            report.write_annual_report()
            report.annual_flush()
        surphos.time.day += 1
    report.write_annual_report()
    report.annual_flush()
    data_analysis.produce_graphics()


def clear_output_dir():
    path = util.get_base_dir()/'SurPhos/output'
    for file in path.iterdir():
        file.unlink()


def daily_P_routine(surphos, weather, time):
    fertilizer.update_all(surphos, time)  # done
    manure.update_all(surphos, time)  # done
    plow.update_all(surphos, time)  # done
    sol_P.update_all(surphos, weather, time)  # done
    fert_leach.update_all(surphos, weather, time)  # done
    manure_leach.update_all(surphos, weather, time)  # done
    p_mineralization.update_all(surphos, time)  # done


class SurPhos:
    def __init__(self, data):
        self.time = Time(data['time'])
        self.weather = Weather(self.time, data['weather'])
        self.manure_app = Manure(data['manure'])
        self.fertilizer_app = Fertilizer(data['fertilizer'])
        self.tillage_app = Tillage(data['tillage'])
        self.crop_P_uptake = CropPUptake(data['p_uptake'])

        for i in range(0, len(self.weather.rainfall)):
            self.crop_P_uptake.P_uptake_daily.append([0 for _ in range(0, len(self.weather.rainfall[i]))])

        for i in range(0, len(self.weather.rainfall)):

            if i == 0:
                days = len(self.weather.rainfall[i]) - self.time.start_day
                for j in range(self.time.start_day - 1, len(self.weather.rainfall[i])):
                    self.crop_P_uptake.P_uptake_daily[i][j] = self.crop_P_uptake.P_uptake_annual[i] / days

            elif i == len(self.weather.rainfall) - 1:
                days = self.time.end_day
                for j in range(0, self.time.end_day):
                    self.crop_P_uptake.P_uptake_daily[i][j] = self.crop_P_uptake.P_uptake_annual[i] / days
            else:
                days = len(self.weather.rainfall[i])
                for j in range(0, len(self.weather.rainfall[i])):
                    self.crop_P_uptake.P_uptake_daily[i][j] = self.crop_P_uptake.P_uptake_annual[i] / days

        soil_data = data['soil']

        self.cover = soil_data['CoverType']
        self.leach = 0.0
        self.area = soil_data['FieldArea']

        self.soil_layers = 3
        self.depths_layer = soil_data['Depth']
        self.labile_P_layer = soil_data['LabileP']
        self.clay_layer = soil_data['Clay']
        self.OM_layer = soil_data['SoilOM']
        self.bulk_density_layer = soil_data['BulkDensity']
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
        self.days = [0, 0, 0]
        self.moisture = 0.5
        self.CNT = 1
        self.manure_cov = 0.0
        self.manure_mass = 0.0
        self.cover_SLP = 0.000025
        self.count_day = [0, 0, 0]

        # fertilizer
        self.fert_applied_sum = 0.0
        self.no_rains = 0.0
        self.fert_CNT = 0.0
        self.fert_P_available = 0.0  # avfrtp
        self.fert_P_released = 0.0  # rsfrtp
        self.fact = 0.0

        # manure
        self.manure_sum = 0
        self.manure_P_sum = 0
        self.manure_N_sum = 0
        self.WIP = 0.0
        self.WOP = 0.0
        self.SIP = 0.0
        self.SOP = 0.0
        self.manure_NH4 = 0.0
        self.manure_SON = 0.0
        self.manure_mass_app = 0.0

        self.cows = []
        self.heifer = []
        self.dry_cow = []
        self.d_calf = []
        self.beef_cow = []
        self.b_calf = []

        for x in range(0, len(self.weather.rainfall)):
            self.cows.append([0 for _ in range(0, len(self.weather.rainfall[x]))])
            self.heifer.append([0 for _ in range(0, len(self.weather.rainfall[x]))])
            self.dry_cow.append([0 for _ in range(0, len(self.weather.rainfall[x]))])
            self.d_calf.append([0 for _ in range(0, len(self.weather.rainfall[x]))])
            self.beef_cow.append([0 for _ in range(0, len(self.weather.rainfall[x]))])
            self.b_calf.append([0 for _ in range(0, len(self.weather.rainfall[x]))])

        # plow

        # solp
        self.soil_P = [0, 0, 0]
        self.SRP_sum = 0.0
        self.slope = [0, 0, 0]
        self.inter = [0, 0, 0]
        self.DRP = [0, 0, 0]
        self.water = [0, 0, 0]

        # fert_leach
        self.fert_sorp = 0.0
        self.fert_absorbed_sum = 0.0
        self.fert_leach = 0.0
        self.PD_factor = 0.0
        self.fert_runoff_P = 0.0
        self.fert_R_sum = 0.0
        self.fert_L_sum = 0.0

        # p_mineralization
        self.count_it = [0, 0, 0]
        self.counts = [0, 0, 0]
        self.soil_yp = []  # soilyp
        for x in range(0, 3):
            self.soil_yp.append([0 for _ in range(0, 366)])
        self.PSP_avg = []
        for x in range(len(self.PSP_layer)):
            self.PSP_avg.append(self.PSP_layer[x])
        self.pbal = [0, 0, 0]
        self.old_pbal = [0, 0, 0]
        self.lab_P_sum = [0, 0, 0]
        self.lab_P_avg = [0, 0, 0]
        self.varA = [0, 0, 0]
        self.varB = [0, 0, 0]
        self.base = [0, 0, 0]
        self.pflow = [0, 0, 0]
        self.pd_srb_fac = [0, 0, 0]
        self.pflow_r = [0, 0, 0]
        self.PSP_fac = [0, 0, 0]
        self.pflow2 = [0, 0, 0]
        self.temp_lab = [0, 0, 0]

        # manure_leach
        self.TIP_leach = 0.0
        self.TOP_leach = 0.0
        self.TN_leach = 0.0
        self.ND_factor = 0.0
        self.WIP_R_sum = 0.0
        self.WOP_R_sum = 0.0
        self.NH_R_sum = 0.0
        self.WIP_L_sum = 0.0
        self.WOP_L_sum = 0.0
        self.NH_L_sum = 0.0
        self.DP_sum = 0.0
        self.N_sum = 0.0
        self.SRP_MGL = 0.0
        self.runoff_IP = 0.0
        self.runoff_OP = 0.0
        self.runoff_NH = 0.0
        self.T_runoff_IP = 0.0


class Fertilizer:
    def __init__(self, data):
        self.year = data['year']
        self.day = data['day']
        self.mass = data['mass']
        self.depth = data['depth']
        self.surface_percent = data['surf_perc']


class Manure:
    def __init__(self, data):
        self.type = data['type']
        self.year = data['year']
        self.day = data['day']
        self.mass = data['mass']
        self.total_P_frac = data['P_frac']
        self.WIP_frac = data['WIP_frac']
        self.WOP_frac = data['WOP_frac']
        self.total_N_frac = data['N_frac']
        self.total_NH4_frac = data['NH4_frac']
        self.dry_matter = data['dry_matter']
        self.percent_cover = data['percent_cover']
        self.depth = data['depth']
        self.surface_percent = data['surf_perc']


class Tillage:
    def __init__(self, data):
        self.year = data['year']
        self.day = data['day']
        self.percent_incorporated = data['perc_incorporated']
        self.percent_mixed = data['perc_mixed']
        self.depth = data['depth']


class CropPUptake:
    def __init__(self, data):
        self.year = data['year']
        self.P_uptake_annual = data['annual_uptake']
        self.P_uptake_daily = []


class Time:
    def __init__(self, data):
        self.start_year = int(data['StartDate'].split(':')[0])
        self.start_day = int(data['StartDate'].split(':')[1])
        self.end_year = int(data['EndDate'].split(':')[0])
        self.end_day = int(data['EndDate'].split(':')[1])

        self.day = self.start_day
        self.year = 0


class Weather:
    def __init__(self, time, data):
        self.rainfall = []
        self.runoff = []
        self.temp = []

        self.years = time.end_year - time.start_year + 1

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

        self.weather_csv = data

        weather_path = util.get_base_dir() / 'SurPhos' / self.weather_csv
        with weather_path.open('r') as f:
            read_csv = csv.reader(f, delimiter=',')

            curr_row = 0
            year = 0

            for row in read_csv:
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

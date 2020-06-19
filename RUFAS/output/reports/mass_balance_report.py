"""
RUFAS: Ruminant Farm Systems Model
File name: mass_balance_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
from pathlib import Path

from RUFAS.output import graphics
from RUFAS.output.reports.base_report import BaseReport


class MassBalanceReport:
    def __init__(self, data):

        self.diagnostic_dir = Path
        self.csv_dir = Path
        self.report_name = data['report_name']
        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']
        self.mass_balance_reports = {"water_balance": self.WaterBalance(data['water_balance']),
                                     "phosphorus_balance": self.PhosphorusBalance(data['phosphorus_balance']),
                                     "nitrogen_balance": self.NitrogenBalance(data['nitrogen_balance'])
                                     }

    def initialize(self):
        if self.produce_csv:
            for report in self.mass_balance_reports.values():
                if not report.produce_csv and report.produce_graphics:
                    print("Warning: Cannot produce graphics for inactive report:", report.report_name,
                          ". Setting produce_graphics to False")
                    report.produce_graphics = False
                if report.produce_csv:
                    report.initialize()

    def initialize_mass_balance_csv_dir(self, mass_balance_dir):
        for report_name in self.mass_balance_reports:
            csv_dir = mass_balance_dir / report_name
            csv_dir.mkdir(exist_ok=True, parents=False)
            self.mass_balance_reports[report_name].csv_dir = csv_dir

    def initialize_mass_balance_diagnostic_dir(self, mass_balance_dir):
        for report_name in self.mass_balance_reports:
            diagnostic_dir = mass_balance_dir / report_name
            diagnostic_dir.mkdir(exist_ok=True, parents=False)
            self.mass_balance_reports[report_name].diagnostic_dir = diagnostic_dir

    def daily_update(self, state, weather, time):
        if self.produce_csv:
            for report in self.mass_balance_reports.values():
                if report.produce_csv:
                    report.daily_update(state, weather, time)

    def annual_update(self, state, weather, time):
        if self.produce_csv:
            for report in self.mass_balance_reports.values():
                if report.produce_csv:
                    report.annual_update(state, weather, time)

    def write_annual_report(self):
        if self.produce_csv:
            for report in self.mass_balance_reports.values():
                if report.produce_csv:
                    report.write_annual_report()

    def annual_flush(self):
        if self.produce_csv:
            for report in self.mass_balance_reports.values():
                if report.produce_csv:
                    report.annual_flush()

    def produce_report_graphics(self):
        if self.produce_graphics:
            for report in self.mass_balance_reports.values():
                report.produce_report_graphics()

    class MassBalanceReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)

        def produce_report_graphics(self):
            super().produce_report_graphics()
            graphics.annual_mass_balance_graphics(self)

    class WaterBalance(MassBalanceReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'actual': ['soil.p_act', 'mmH2O', []],
                                    'calculated': ['soil.p_calc', 'mmH2O', []],
                                    'difference': ['soil.water_balance_difference', 'mmH2O', []],
                                    'delta': ['soil.delta_SW', 'mmH2O', []],
                                    'runoff': ['soil.runoff', 'mmH2O', []],
                                    'evaporation': ['soil.evap_sum', 'mmH2O', []],
                                    'transpiration': ['soil.trans_sum', 'mmH2O', []],
                                    'drainage': ['soil.drainage', 'mmH2O', []]
                                    }

            self.annual_variables = {'year': ['time.cal_year', '', 0],
                                     'actual': ['round(soil.p_act_annual, 3)', 'mmH2O', 0],
                                     'calculated': ['round(soil.p_calc_annual, 3)', 'mmH2O', 0],
                                     'difference': ['round(soil.water_balance_difference_annual, 3)', 'mmH2O', 0],
                                     'delta': ['round(soil.delta_SW_annual, 3)', 'mmH2O', 0],
                                     'runoff': ['round(soil.runoff_annual, 3)', 'mmH2O', 0],
                                     'evaporation': ['round(soil.evap_annual, 3)', 'mmH2O', 0],
                                     'transpiration': ['round(soil.trans_annual, 3)', 'mmH2O', 0],
                                     'drainage': ['round(soil.drainage_annual, 3)', 'mmH2O', 0],
                                     # all new variables should be added below here
                                     }

    class PhosphorusBalance(MassBalanceReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {
                'year': ['time.cal_year', '', []],
                'j_day': ['time.day', '', []],
                'actual': ['soil.manure_P', 'kg', []],
                'calculated': ['soil.P_calc', 'kg', []],
                'difference': ['soil.P_balance_difference', 'kg', []],
                'delta': ['soil.delta_P', 'kg', []],
                'P_drainage': ['soil.P_drainage', 'kg', []],
                'P_runoff': ['soil.P_runoff', 'kg', []],
                'P_erosion': ['soil.P_erosion', 'kg', []],
                'P_uptake': ['soil.P_uptake', 'kg', []]
            }

            self.annual_variables = {
                'year': ['time.cal_year', '', 0],
                'actual': ['soil.manure_P_annual', 'kg', 0],
                'calculated': ['soil.P_calc_annual', 'kg', 0],
                'difference': ['soil.P_balance_difference_annual', 'kg', 0],
                'delta': ['soil.delta_P_annual', 'kg', 0],
                'P_drainage': ['soil.P_drainage_annual', 'kg', 0],
                'P_runoff': ['soil.P_runoff_annual', 'kg', 0],
                'P_erosion': ['soil.P_erosion_annual', 'kg', 0],
                'P_uptake': ['soil.P_uptake_annual', 'kg', 0]
            }

    class NitrogenBalance(MassBalanceReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {
                'year': ['time.cal_year', '', []],
                'j_day': ['time.day', '', []],
                'actual': ['soil.manure_N', 'kg', []],
                'calculated': ['soil.N_calc', 'kg', []],
                'difference': ['soil.N_balance_difference', 'kg', []],
                'delta': ['soil.delta_N', 'kg N', []],
                # 'NH4': ['soil.NH4', 'kg', []],
                # 'NO3': ['soil.NO3', 'kg', []],
                # 'org_N': ['soil.org_N', 'kg', []],
                # 'active_N': ['soil.active_N', 'kg', []],
                # 'stable_N': ['soil.stable_N', 'kg', []],
                # 'fresh_N': ['soil.fresh_N', 'kg', []],
                # 'NO3_drainage': ['soil.NO3_drainage', 'kg', []],
                # 'NH4_drainage': ['soil.NH4_drainage', 'kg', []],
                # 'active_N_drainage': ['soil.active_N_drainage', 'kg', []],
                'N_drainage': ['soil.N_drainage', 'kg', []],
                # 'NO3_runoff': ['soil.NO3_runoff', 'kg', []],
                # 'NH4_runoff': ['soil.NH4_runoff', 'kg', []],
                'N_runoff': ['soil.N_runoff', 'kg', []],
                # 'NH4_erosion': ['soil.NH4_erosion', 'kg', []],
                # 'active_N_erosion': ['soil.active_N_erosion', 'kg', []],
                # 'fresh_N_erosion': ['soil.fresh_N_erosion', 'kg', []],
                'N_erosion': ['soil.N_erosion', 'kg', []],
                'N_uptake': ['soil.N_uptake', 'kg', []]
            }

            self.annual_variables = {
                'year': ['time.cal_year', '', 0],
                'actual': ['soil.manure_N_annual', 'kg', 0],
                'calculated': ['soil.N_calc_annual', 'kg', 0],
                'difference': ['soil.N_balance_difference_annual', 'kg', 0],
                'delta': ['soil.delta_N_annual', 'kg', 0],
                'N_drainage': ['soil.N_drainage_annual', 'kg', 0],
                'N_runoff': ['soil.N_runoff_annual', 'kg', 0],
                'N_erosion': ['soil.N_erosion_annual', 'kg', 0],
                'N_uptake': ['soil.N_uptake_annual', 'kg', 0]
            }

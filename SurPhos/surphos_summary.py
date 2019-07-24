from SurPhos import util

import csv


class SurPhosSummary:
    def __init__(self):
        self.f_path = util.get_base_dir() / 'SurPhos/output/surphos_report.csv'
        self.variables = {'year': ['time.start_year + time.year', '', []],
                          'j_day': ['time.day', '', []],
                          'precip': ['weather.rainfall[time.year][time.day - 1]', 'mmH2O', []],
                          'runoff': ['weather.runoff[time.year][time.day - 1]', 'mmH2O', []],
                          'soil_runoff_DRP': ['SRP_MGL', 'mgL', []],
                          'manure_runoff_DRP': ['runoff_IP', 'mgL', []],
                          'fert_runoff_DRP': ['fert_runoff_P', 'mgL', []],
                          'runoff_DIP': ['T_runoff_IP', 'mgL', []],
                          'manure_runoff_DOP': ['runoff_OP', 'mgL', []],
                          'manure_runoff_NH4': ['runoff_NH', 'mgL', []],
                          'PSP': ['PSP_layer[0]', '', []],
                          'Labile_P1': ['labile_P_layer[0]', 'kg HA', []],
                          'Labile_P2': ['labile_P_layer[1]', 'kg HA', []],
                          'Labile_P3': ['labile_P_layer[2]', 'kg HA', []],
                          'Available_Fert_P': ['fert_P_available', 'kg', []],
                          'Released_Fert_P': ['fert_P_released', 'kg', []],
                          'manure_WIP': ['WIP', 'kg', []],
                          'manure_WOP': ['WOP', 'kg', []],
                          'manure_SIP': ['SIP', 'kg', []],
                          'manure_SOP': ['SOP', 'kg', []],
                          'manure_NH4': ['manure_NH4', 'kg', []],
                          'manure_SON': ['manure_SON', 'kg', []],
                          'manure_mass': ['manure_mass', 'kg', []],
                          'manure_cover': ['manure_cov', 'HA', []],
                          }  # TODO: There is also a cow output file in SurPhos that we do not implement

    def write_header(self):

        mode = 'a+' if self.f_path.exists() else 'w+'

        with self.f_path.open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.variables.keys(),
                                    lineterminator='\n')
            writer.writeheader()

            units = {}
            for variable in self.variables:
                units[variable] = self.variables[variable][1]

            writer.writerow(units)

    def initialize(self):
        self.write_header()

    def daily_update(self, SurPhos):
        for variable in self.variables:
            self.variables[variable][2].append(eval(self.variables[variable][0], globals(), vars(SurPhos)))

    def write_annual_report(self):

        mode = 'a+' if self.f_path.exists() else 'w+'

        with self.f_path.open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.variables.keys(),
                                    lineterminator='\n')
            for day in range(len(self.variables['j_day'][2])):
                row = {}
                for variable in self.variables:
                    row[variable] = self.variables[variable][2][day]
                writer.writerow(row)

    def annual_flush(self):
        for variable in self.variables:
            self.variables[variable][2] = []

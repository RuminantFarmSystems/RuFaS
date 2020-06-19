"""
RUFAS: Ruminant Farm Systems Model
File name: field_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
from pathlib import Path
from RUFAS.output.reports.base_report import BaseReport


class FieldReport:
    def __init__(self, data):

        self.diagnostic_dir = Path
        self.csv_dir = Path
        self.report_name = data['report_name']
        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']
        self.field_reports = {
            'crop_report': self.CropReport(data['crop_report']),
            'soil_report': self.SoilReport(data['soil_report']),
            'soil_nitrogen_report': self.SoilNitrogenReport(data['soil_nitrogen_report']),
            'soil_phosphorus_report': self.SoilPhosphorusReport(data['soil_phosphorus_report'])
        }

    def initialize(self):
        if self.produce_csv:
            for report in self.field_reports.values():
                if not report.produce_csv and report.produce_graphics:
                    print("Warning: Cannot produce graphics for inactive report:", report.report_name,
                          ". Setting produce_graphics to False")
                    report.produce_graphics = False
                if report.produce_csv:
                    report.initialize()

    def initialize_field_csv_dir(self, field_dir):
        for report_name in self.field_reports:
            csv_dir = field_dir / report_name
            csv_dir.mkdir(exist_ok=True, parents=False)
            self.field_reports[report_name].csv_dir = csv_dir

    def initialize_field_diagnostic_dir(self, field_dir):
        for report_name in self.field_reports:
            diagnostic_dir = field_dir / report_name
            diagnostic_dir.mkdir(exist_ok=True, parents=False)
            self.field_reports[report_name].diagnostic_dir = diagnostic_dir

    def daily_update(self, state, weather, time):
        if self.produce_csv:
            for report in self.field_reports.values():
                if report.produce_csv:
                    report.daily_update(state, weather, time)

    def annual_update(self, state, weather, time):
        if self.produce_csv:
            for report in self.field_reports.values():
                if report.produce_csv:
                    report.annual_update(state, weather, time)

    def write_annual_report(self):
        if self.produce_csv:
            for report in self.field_reports.values():
                if report.produce_csv:
                    report.write_annual_report()

    def annual_flush(self):
        if self.produce_csv:
            for report in self.field_reports.values():
                if report.produce_csv:
                    report.annual_flush()

    def produce_report_graphics(self):
        if self.produce_graphics:
            for report in self.field_reports.values():
                report.produce_report_graphics()

    class BaseFieldReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)
            # TODO: add field_name in dj_fields

    class CropReport(BaseFieldReport):
        def __init__(self, data):
            super().__init__(data)
            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'fr_PHU': ['crop_type.fr_PHU', '%', []],
                                    'biomass': ['crop_type.biomass_actual', 'kg ha^-1', []],
                                    'LAI_actual': ['crop_type.LAI_actual', 'm^2/m^2', []],
                                    'Bio_N': ['crop_type.bio_N', 'kg N ha^-1', []],
                                    'Bio_P': ['crop_type.bio_P', 'kg P ha^-1', []],
                                    'rooting_depth': ['crop_type.z_root', 'mm', []],
                                    'yield_actual': ['crop_type.yield_actual', 'kg ha^-1', []]
                                    }

            self.annual_variables = {'year': ['time.cal_year', '', 0],
                                     'yield': ['crop_type.yield_annual', 'kg/ha', 0]
                                     }

    class SoilReport(BaseFieldReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'precip': ['weather.rainfall[time.year - 1][time.day - 1]', 'mm', []],
                                    'runoff': ['soil.runoff', 'mm', []],
                                    'ET_max': ['soil.ET_max', 'mm d^-1', []],
                                    'ET_act': ['soil.ET_act', 'mm H20', []],
                                    'trans_max': ['soil.trans_max', 'mm H20', []],
                                    'evap_max': ['soil.evap_max', 'mm H20', []],
                                    'surface_temp': ['soil.Tsurf', 'C', []],
                                    'sediment_yield': ['soil.sed', 'metric tons', []],
                                    'residue': ['soil.residue', 'kg/ha', []],
                                    'trans_act_L1': ['soil.soil_layers[0].trans_act', 'mm H20', []],
                                    'trans_act_L2': ['soil.soil_layers[1].trans_act', 'mm H20', []],
                                    'trans_act_L3': ['soil.soil_layers[2].trans_act', 'mm H20', []],
                                    'soil_water_L1': ['soil.soil_layers[0].soil_water', 'mm', []],
                                    'soil_water_L2': ['soil.soil_layers[1].soil_water', 'mm', []],
                                    'soil_water_L3': ['soil.soil_layers[2].soil_water', 'mm', []],
                                    'evap_L1': ['soil.soil_layers[0].evap', 'mm H20', []],
                                    'evap_L2': ['soil.soil_layers[1].evap', 'mm H20', []],
                                    'evap_L3': ['soil.soil_layers[2].evap', 'mm H20', []],
                                    'perc_L1': ['soil.soil_layers[0].perc', 'mm H20', []],
                                    'perc_L2': ['soil.soil_layers[1].perc', 'mm H20', []],
                                    'perc_L3': ['soil.soil_layers[2].perc', 'mm H20', []],
                                    'temperature_L1': ['soil.soil_layers[0].temperature', 'C', []],
                                    'temperature_L2': ['soil.soil_layers[1].temperature', 'C', []],
                                    'temperature_L3': ['soil.soil_layers[2].temperature', 'C', []],
                                    }

            self.annual_variables = {'year': ['time.cal_year', '', 0],
                                     'ET_max': ['soil.ET_max_annual', 'mm H20', 0],
                                     'ET': ['soil.ET_annual', 'mm H20', 0]
                                     }

    class SoilNitrogenReport(BaseFieldReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'NO3_L1': ['soil.soil_layers[0].NO3', 'kg', []],
                                    'NO3_L2': ['soil.soil_layers[1].NO3', 'kg', []],
                                    'NO3_L3': ['soil.soil_layers[2].NO3', 'kg', []],
                                    'NH4_L1': ['soil.soil_layers[0].NH4', 'kg', []],
                                    'NH4_L2': ['soil.soil_layers[1].NH4', 'kg', []],
                                    'NH4_L3': ['soil.soil_layers[2].NH4', 'kg', []],
                                    'active_N_L1': ['soil.soil_layers[0].active_N', 'kg', []],
                                    'active_N_L2': ['soil.soil_layers[1].active_N', 'kg', []],
                                    'active_N_L3': ['soil.soil_layers[2].active_N', 'kg', []],
                                    'stable_N_L1': ['soil.soil_layers[0].stable_N', 'kg', []],
                                    'stable_N_L2': ['soil.soil_layers[1].stable_N', 'kg', []],
                                    'stable_N_L3': ['soil.soil_layers[2].stable_N', 'kg', []],
                                    'fresh_N': ['soil.fresh_N', 'kg', []],
                                    'Nitri_L1': ['soil.soil_layers[0].nitrification', 'kg/ha', []],
                                    'Nitri_L2': ['soil.soil_layers[1].nitrification', 'kg/ha', []],
                                    'Nitri_L3': ['soil.soil_layers[2].nitrification', 'kg/ha', []],
                                    'Volati_L1': ['soil.soil_layers[0].volatilization', 'kg/ha', []],
                                    'Volati_L2': ['soil.soil_layers[1].volatilization', 'kg/ha', []],
                                    'Volati_L3': ['soil.soil_layers[2].volatilization', 'kg/ha', []],
                                    'Denitri_L1': ['soil.soil_layers[0].denitrification', 'kg/ha', []],
                                    'Denitri_L2': ['soil.soil_layers[1].denitrification', 'kg/ha', []],
                                    'Denitri_L3': ['soil.soil_layers[2].denitrification', 'kg/ha', []],
                                    'Tot_Nitri_Vol_L1': ['soil.soil_layers[0].totNitriVolatil', 'kg/ha', []],
                                    'Tot_Nitri_Vol_L2': ['soil.soil_layers[1].totNitriVolatil', 'kg/ha', []],
                                    'Tot_Nitri_Vol_L3': ['soil.soil_layers[2].totNitriVolatil', 'kg/ha', []],
                                    'N_trans_L1': ['soil.soil_layers[0].nTrans', 'kg', []],
                                    'N_trans_L2': ['soil.soil_layers[1].nTrans', 'kg', []],
                                    'N_trans_L3': ['soil.soil_layers[2].nTrans', 'kg', []],
                                    'NO3_runoff': ['soil.NO3_runoff', 'kg/ha', []],
                                    'NH4_runoff': ['soil.NH4_runoff', 'kg/ha', []],
                                    'NO3_perc_L1': ['soil.soil_layers[0].NO3_perc', 'kg/ha', []],
                                    'NO3_perc_L2': ['soil.soil_layers[1].NO3_perc', 'kg/ha', []],
                                    'NO3_perc_L3': ['soil.soil_layers[2].NO3_perc', 'kg/ha', []],
                                    'NH4_perc_L1': ['soil.soil_layers[0].NH4_perc', 'kg/ha', []],
                                    'NH4_perc_L2': ['soil.soil_layers[1].NH4_perc', 'kg/ha', []],
                                    'NH4_perc_L3': ['soil.soil_layers[2].NH4_perc', 'kg/ha', []],
                                    'active_N_perc_L1': ['soil.soil_layers[0].active_N_perc', 'kg/ha', []],
                                    'active_N_perc_L2': ['soil.soil_layers[1].active_N_perc', 'kg/ha', []],
                                    'active_N_perc_L3': ['soil.soil_layers[2].active_N_perc', 'kg/ha', []],
                                    'NH4_erosion': ['soil.NH4_erosion', 'kg/ha', []],
                                    'active_N_erosion': ['soil.active_N_erosion', 'kg/ha', []],
                                    'stable_N_erosion': ['soil.stable_N_erosion', 'kg/ha', []],
                                    'fresh_N_erosion': ['soil.fresh_N_erosion', 'kg/ha', []]
                                    }

            self.annual_variables = {'year': ['time.cal_year', '', 0],
                                     'NO3_runoff': ['soil.NO3_runoff_annual', 'kg/ha', 0],
                                     'NH4_runoff': ['soil.NH4_runoff_annual', 'kg/ha', 0],
                                     'NH4_erosion': ['soil.NH4_erosion_annual', 'kg/ha', 0],
                                     'active_N_erosion': ['soil.active_N_erosion_annual', 'kg/ha', 0],
                                     'stable_N_erosion': ['soil.stable_N_erosion_annual', 'kg/ha', 0],
                                     'fresh_N_erosion': ['soil.fresh_N_erosion_annual', 'kg/ha', 0],
                                     'NO3_drainage': ['soil.NO3_drainage_annual', 'kg/ha', 0],
                                     'NH4_drainage': ['soil.NH4_drainage_annual', 'kg/ha', 0],
                                     'active_N_drainage': ['soil.active_N_drainage_annual', 'kg/ha', 0]
                                     }

    class SoilPhosphorusReport(BaseFieldReport):
        def __init__(self, data):
            super().__init__(data)

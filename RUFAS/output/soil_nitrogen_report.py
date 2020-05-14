"""
RUFAS: Ruminant Farm Systems Model
File name: soil_nitrogen_report.py

Description: Output handler for Nitrogen cycling within the soil module

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
"""

import csv
from pathlib import Path

from RUFAS.output.graphics import daily_graphics, annual_graphics
from RUFAS.output.report_handler import BaseReportHandler


class SoilNitrogen(BaseReportHandler):

    def __init__(self, data, field_name):

        # identifies report with a field
        self.field_name = field_name

        # sets produce_csv, report_name, file_name using data
        BaseReportHandler.__init__(self, data)
        self.field_names = None

        #
        # Outputs can be added in this single place in the following format:
        # 'output_name': ['variable_name', 'unit', []],
        # 'output_name' is a user defined key that will show up in outputs/graphs.
        # avoid spaces.
        # 'variable_name' is very important. This has to be a variable defined
        # and initialized in the object. If you are interested in tracking
        # a variable not defined in the class, you need to create it there
        # first. The output handler will not work if the variable is incorrect.
        # 'unit' is user defined but will, again, show up in outputs/graphs.
        # [] is an empty list
        #

        # daily outputs
        self.daily_variables = {'year': ['time.calendar_year', '', []],
                                'j_day': ['time.day', '', []],
                                'NO3_L1': ['soil.soil_layers[0].NO3', 'kg', []],
                                'NO3_L2': ['soil.soil_layers[1].NO3', 'kg', []],
                                'NO3_L3': ['soil.soil_layers[2].NO3', 'kg', []],
                                'NH4_L1': ['soil.soil_layers[0].NH4', 'kg', []],
                                'NH4_L2': ['soil.soil_layers[1].NH4', 'kg', []],
                                'NH4_L3': ['soil.soil_layers[2].NH4', 'kg', []],
                                'ActiveN_L1': ['soil.soil_layers[0].active_N', 'kg', []],
                                'ActiveN_L2': ['soil.soil_layers[1].active_N', 'kg', []],
                                'ActiveN_L3': ['soil.soil_layers[2].active_N', 'kg', []],
                                'StableN_L1': ['soil.soil_layers[0].stable_N', 'kg', []],
                                'StableN_L2': ['soil.soil_layers[1].stable_N', 'kg', []],
                                'StableN_L3': ['soil.soil_layers[2].stable_N', 'kg', []],
                                'fresh_N': ['soil.top_layer_fresh_N', 'kg', []],
                                'Nitri_L1': ['soil.soil_layers[0].nitrification', 'kg/ha', []],
                                'Nitri_L2': ['soil.soil_layers[1].nitrification', 'kg/ha', []],
                                'Nitri_L3': ['soil.soil_layers[2].nitrification', 'kg/ha', []],
                                'Volati_L1': ['soil.soil_layers[0].volatilization', 'kg/ha', []],
                                'Volati_L2': ['soil.soil_layers[1].volatilization', 'kg/ha', []],
                                'Volati_L3': ['soil.soil_layers[2].volatilization', 'kg/ha', []],
                                'Denitri_L1': ['soil.soil_layers[0].denitrification', 'kg/ha', []],
                                'Denitri_L2': ['soil.soil_layers[1].denitrification', 'kg/ha', []],
                                'Denitri_L3': ['soil.soil_layers[2].denitrification', 'kg/ha', []],
                                'Tot_Nitri_Vol_L1': ['soil.soil_layers[0].tot_nitri_volatil', 'kg/ha', []],
                                'Tot_Nitri_Vol_L2': ['soil.soil_layers[1].tot_nitri_volatil', 'kg/ha', []],
                                'Tot_Nitri_Vol_L3': ['soil.soil_layers[2].tot_nitri_volatil', 'kg/ha', []],
                                'N_trans_L1': ['soil.soil_layers[0].N_trans', 'kg', []],
                                'N_trans_L2': ['soil.soil_layers[1].N_trans', 'kg', []],
                                'N_trans_L3': ['soil.soil_layers[2].N_trans', 'kg', []],
                                'NO3_runoff': ['soil.NO3_runoff', 'kg/ha', []],
                                'NH4_runoff': ['soil.NH4_runoff', 'kg/ha', []],
                                'NO3_perc_L1': ['soil.soil_layers[0].NO3_perc', 'kg/ha', []],
                                'NO3_perc_L2': ['soil.soil_layers[1].NO3_perc', 'kg/ha', []],
                                'NO3_perc_L3': ['soil.soil_layers[2].NO3_perc', 'kg/ha', []],
                                'NH4_perc_L1': ['soil.soil_layers[0].NH4_perc', 'kg/ha', []],
                                'NH4_perc_L2': ['soil.soil_layers[1].NH4_perc', 'kg/ha', []],
                                'NH4_perc_L3': ['soil.soil_layers[2].NH4_perc', 'kg/ha', []],
                                'active_perc_L1': ['soil.soil_layers[0].active_perc', 'kg/ha', []],
                                'active_perc_L2': ['soil.soil_layers[1].active_perc', 'kg/ha', []],
                                'active_perc_L3': ['soil.soil_layers[2].active_perc', 'kg/ha', []],
                                'NH4_erosion': ['soil.NH4_erosion', 'kg/ha', []],
                                'active_N_erosion': ['soil.active_N_erosion', 'kg/ha', []],
                                'stable_N_erosion': ['soil.stable_N_erosion', 'kg/ha', []],
                                'fresh_N_erosion': ['soil.fresh_N_erosion', 'kg/ha', []]
                                }

        # annual outputs
        self.annual_variables = {'year': ['time.calendar_year', '', 0],
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

    def write_headers(self, output_csv, variables):
        """
        Description:
            Writes variable names and units to the header of the csv

        Inputs:
            output_csv: csv to be written to
            variables: list of variables being reported
        """

        mode = 'a+' if output_csv.exists() else 'w+'

        with output_csv.open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=variables.keys(),
                                    lineterminator='\n')

            writer.writeheader()

            units = {}
            for variable in variables:
                units[variable] = variables[variable][1]

            writer.writerow(units)

    def initialize(self, state):
        """
        Description:
            Initialize report
        """

        self.write_headers(self.get_fPath(), self.daily_variables)
        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + "_annual.csv")
        self.write_headers(annual_path, self.annual_variables)

    def daily_update(self, field, weather, time):
        """
        Description:
            Called daily from the output handler to store simulation values for
             reporting at the end of the year
        Inputs:
            field: a soil nitrogen report is produced for each field simulated
        """

        soil = field.soil

        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, field, weather, time):
        """
        Description:
            Called daily from the output handler to store simulation values for
             reporting at the end of the year
        Inputs:
            field: a soil nitrogen report is produced for each field simulated
        """

        soil = field.soil

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())

    def write_annual_report(self):
        """
        Description:
            Called at the end of each simulation year to write stored values to
            the csv
        """

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csv_file:
            # Write data day by day
            writer = csv.DictWriter(csv_file, fieldnames=self.daily_variables.keys(),
                                    lineterminator='\n')

            for day in range(len(self.daily_variables['j_day'][2])):
                row = {}
                for variable in self.daily_variables:
                    row[variable] = self.daily_variables[variable][2][day]
                writer.writerow(row)

        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + "_annual.csv")

        mode = 'a+' if annual_path.exists() else 'w+'

        with annual_path.open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.annual_variables.keys(),
                                    lineterminator='\n')
            row = {}
            for variable in self.annual_variables:
                row[variable] = self.annual_variables[variable][2]
            writer.writerow(row)

    def annual_flush(self):
        """
        Description:
            Clears stored values after reporting
        """

        for variable in self.daily_variables:
            self.daily_variables[variable][2] = []

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = 0

    def produce_report_graphics(self):
        """
        Description:
            Calls functions in graphics.py
        """

        annual_graphics(self)
        daily_graphics(self)

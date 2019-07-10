################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# Output.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#          William Donovan
#
################################################################################

import csv

from RUFAS.output.data_analysis import data_analysis
from RUFAS.output.report_handler import BaseReportHandler


# -------------------------------------------------------------------------------
# Class: SoilSummary
# Creates and prints to the file soil_summary.csv
# -------------------------------------------------------------------------------
class SoilSummary(BaseReportHandler):

    def __init__(self, data):

        #
        # Sets active, report_name, file_name using data
        #

        self.set_properties(data)
        self.fieldNames = None

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.year = []
        self.julianDay = []
        self.precip = []
        self.runoff = []
        self.potentialEvapotranspiration = []
        self.ET_act = []
        self.trans_max = []
        self.sublimation = []
        self.surfaceTemp = []
        self.sedimentYield = []
        self.residue = []
        self.numSoilLayers = 0

        self.layers_trans_act = []
        self.layersSoilWater = []
        self.layers_evap = []
        self.layers_perc = []
        self.layersTemperature = []

    # ---------------------------------------------------------------------------
    # Function: write_header
    #           Writes the header (title and units) in the csvfile
    # ---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'Rainfall', 'Runoff',
                          'Potential Evapotranspiration (ET_max)',
                          'Actual Evapotranspiration (ET)',
                          'Crop Transpiration (trans_max)',
                          'Maximum Sublimation (evap_max)']

            for x in range(0, self.numSoilLayers):
                fieldnames.append("trans_act_L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("SoilWater_L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("evap_L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("perc_L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("Temp_L" + str(x+1))

            fieldnames.append("Surface Temp")
            fieldnames.append("Sediment Yield")
            fieldnames.append("Residue")

            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator='\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '',
                             'Rainfall': "mm", 'Runoff': "mm",
                             'Potential Evapotranspiration (ET_max)': "mm d^-1",
                             'Actual Evapotranspiration (ET)': "mm H2O",
                             'Crop Transpiration (trans_max)': "mm H2O",
                             'Maximum Sublimation (evap_max)': "mm H2O",
                             'Surface Temp': "C",
                             'Sediment Yield': "metric tons",
                             'Residue': "kg/ha"
                     }
            for fieldname in fieldnames:
                if fieldname.startswith("trans_act"):
                    units[fieldname] = 'mm H2O'
                elif fieldname.startswith("SoilWater"):
                    units[fieldname] = 'mm'
                elif fieldname.startswith("evap"):
                    units[fieldname] = 'mm H2O'
                elif fieldname.startswith("perc"):
                    units[fieldname] = 'mm H2O'
                elif fieldname.startswith("Temp"):
                    units[fieldname] = 'C'

            writer.writerow(units)

    # ---------------------------------------------------------------------------
    # Function: initialize
    #           Transfers the needed data from Soil object to the report handler
    # ---------------------------------------------------------------------------
    def initialize(self, state):

        soil = state.soil

        # initialize number of layer in soil summary report handler to get output
        # data pertaining to each soil layer
        # Initializes the output arrays for current soil water, evap, and
        # percolation for each soil layer
        self.numSoilLayers = len(soil.listOfSoilLayers)

        for _ in range (0, self.numSoilLayers):
            self.layers_trans_act.append([])
            self.layersSoilWater.append([])
            self.layers_evap.append([])
            self.layers_perc.append([])
            self.layersTemperature.append([])

        self.write_header()

    # ---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # Stores the daily values that need to be printed in the 'soil summary'
    # csv file
    # ---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):

        soil = state.soil

        self.year.append(time.cal_year)
        self.julianDay.append(time.day)
        self.precip.append(weather.rainfall[time.year-1][time.day-1])

        self.runoff.append(soil.runoff)
        self.potentialEvapotranspiration.append(soil.ET_max)
        self.ET_act.append(soil.ET)
        self.trans_max.append(soil.trans_max)
        self.sublimation.append(soil.evap_max)

        for x in range(0, len(soil.listOfSoilLayers)):
            self.layers_trans_act[x].append(
                                    soil.listOfSoilLayers[x].trans_act)

            self.layersSoilWater[x].append(
                                    soil.listOfSoilLayers[x].currentSoilWaterMM)

            self.layers_evap[x].append(
                                    soil.listOfSoilLayers[x].layer_evap)

            self.layers_perc[x].append(
                                    soil.listOfSoilLayers[x].perc)

            self.layersTemperature[x].append(
                                    soil.listOfSoilLayers[x].temperature)

        self.surfaceTemp.append(soil.Tsurf)
        self.sedimentYield.append(soil.sedimentYield)
        self.residue.append(soil.residue)

    # ---------------------------------------------------------------------------
    # Method: annual_update
    # ---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        pass

    # ---------------------------------------------------------------------------
    # Function: write_annual_report
    #           Appends the annual report to the output file
    # Soil Summary is a cvsfile
    # ---------------------------------------------------------------------------
    def write_annual_report(self, y):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # Write data day by day
            for x in range(0, len(self.julianDay)):
                dailySoilData = {
                    'Year':
                        str(self.year[x]),
                    'Julian Day':
                        str(self.julianDay[x]),
                    'Rainfall':
                        str(round(float(self.precip[x]), 2)),
                    'Runoff':
                        str(round(self.runoff[x], 2)),
                    'Potential Evapotranspiration (ET_max)':
                        str(round(self.potentialEvapotranspiration[x], 3)),
                    'Actual Evapotranspiration (ET)':
                        str(round(self.ET_act[x], 3)),
                    'Crop Transpiration (trans_max)':
                        str(round(self.trans_max[x], 3)),
                    'Maximum Sublimation (evap_max)':
                        str(round(self.sublimation[x], 3)),
                    'Surface Temp':
                        str(round(self.surfaceTemp[x], 3)),
                    'Sediment Yield':
                        str(round(self.sedimentYield[x], 3)),
                    'Residue':
                        str(round(self.residue[x], 3))
                }

                for y in range(0, self.numSoilLayers):
                    dailySoilData["trans_act_L" + str(y+1)] = str(
                        round(self.layers_trans_act[y][x], 3))
                    dailySoilData["SoilWater_L" + str(y+1)] = str(
                        round(self.layersSoilWater[y][x], 3))
                    dailySoilData["evap_L" + str(y+1)] = str(
                        round(self.layers_evap[y][x], 3))
                    dailySoilData["perc_L" + str(y+1)] = str(
                        round(self.layers_perc[y][x], 3))
                    dailySoilData["Temp_L" + str(y+1)] = str(
                        round(self.layersTemperature[y][x], 3))

                writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                        lineterminator='\n')
                writer.writerow(dailySoilData)

    # ---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    # ---------------------------------------------------------------------------
    def annual_flush(self):

        self.year = []
        self.julianDay = []
        self.precip = []

        self.runoff = []
        self.potentialEvapotranspiration = []
        self.ET_act = []
        self.trans_max = []
        self.sublimation = []

        for x in range(0, self.numSoilLayers):
            self.layers_trans_act[x] = []
            self.layersSoilWater[x] = []
            self.layers_evap[x] = []
            self.layers_perc[x] = []
            self.layersTemperature[x] = []

        self.surfaceTemp = []
        self.sedimentYield = []
        self.residue = []

    def produce_data_analysis(self, is_final):
        data_analysis(self.file_name, self.show_daily, self.produce_diagnostics, is_final)

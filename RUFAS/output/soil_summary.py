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
        self.Ea_actual = []
        self.Et_max = []
        self.sublimation = []
        self.surfaceTemp = []
        self.sedimentYield = []
        self.numSoilLayers = 0

        self.layers_Et_actual = []
        self.layersSoilWater = []
        self.layersEsoil = []
        self.layersPerc = []
        self.layersTemperature = []

    # ---------------------------------------------------------------------------
    # Function: write_header
    #           Writes the header (title and units) in the csvfile
    # ---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'Rainfall', 'Runoff (Q)',
                          'Potential Evapotranspiration (E0)',
                          'Actual Evapotranspiration (Ea)',
                          'Crop Transpiration (Et_max)',
                          'Maximum Sublimation (Esoil)']

            for x in range(0, self.numSoilLayers):
                fieldnames.append("Et_actual/L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("SoilWater/L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("Esoil/L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("Perc/L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("Temp/L" + str(x+1))

            fieldnames.append("Surface Temp")
            fieldnames.append("Sediment Yield")

            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator='\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '',
                             'Rainfall': "mm", 'Runoff (Q)': "mm",
                             'Potential Evapotranspiration (E0)': "mm d^-1",
                             'Actual Evapotranspiration (Ea)': "mm H2O",
                             'Crop Transpiration (Et_max)': "mm H2O",
                             'Maximum Sublimation (Esoil)': "mm H2O",
                             'Surface Temp': "C",
                             'Sediment Yield': "metric tons"}
            for fieldname in fieldnames:
                if fieldname.startswith("Et_actual"):
                    units[fieldname] = 'mm H2O'
                elif fieldname.startswith("SoilWater"):
                    units[fieldname] = 'mm'
                elif fieldname.startswith("Esoil"):
                    units[fieldname] = 'mm H2O'
                elif fieldname.startswith("Perc"):
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
        # Initializes the output arrays for current soil water, Esoil, and
        # percolation for each soil layer
        self.numSoilLayers = len(soil.listOfSoilLayers)

        for _ in range (0, self.numSoilLayers):
            self.layers_Et_actual.append([])
            self.layersSoilWater.append([])
            self.layersEsoil.append([])
            self.layersPerc.append([])
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
        self.potentialEvapotranspiration.append(soil.E0)
        self.Ea_actual.append(soil.Ea_sum)
        self.Et_max.append(soil.Et_max)
        self.sublimation.append(soil.Esoil)

        for x in range(0, len(soil.listOfSoilLayers)):
            self.layers_Et_actual[x].append(
                                    soil.listOfSoilLayers[x].Et_actual)

            self.layersSoilWater[x].append(
                                    soil.listOfSoilLayers[x].currentSoilWaterMM)

            self.layersEsoil[x].append(
                                    soil.listOfSoilLayers[x].layerEsoil)

            self.layersPerc[x].append(
                                    soil.listOfSoilLayers[x].perc)

            self.layersTemperature[x].append(
                                    soil.listOfSoilLayers[x].temperature)


        self.surfaceTemp.append(soil.Tsurf)
        self.sedimentYield.append(soil.sedimentYield)

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
                        self.julianDay[x],
                    'Rainfall':
                        str(round(float(self.precip[x]), 2)),
                    'Runoff (Q)':
                        str(round(self.runoff[x], 2)),
                    'Potential Evapotranspiration (E0)':
                        str(round(self.potentialEvapotranspiration[x], 3)),
                    'Actual Evapotranspiration (Ea)':
                        str(round(self.Ea_actual[x], 3)),
                    'Crop Transpiration (Et_max)':
                        str(round(self.Et_max[x], 3)),
                    'Maximum Sublimation (Esoil)':
                        str(round(self.sublimation[x], 3)),
                    'Surface Temp':
                        str(round(self.surfaceTemp[x], 3)),
                    'Sediment Yield':
                        str(round(self.sedimentYield[x], 3))}

                for y in range(0, self.numSoilLayers):
                    dailySoilData["Et_actual/L" + str(y+1)] = str(
                        round(self.layers_Et_actual[y][x], 3))
                    dailySoilData["SoilWater/L" + str(y+1)] = str(
                        round(self.layersSoilWater[y][x], 3))
                    dailySoilData["Esoil/L" + str(y+1)] = str(
                        round(self.layersEsoil[y][x], 3))
                    dailySoilData["Perc/L" + str(y+1)] = str(
                        round(self.layersPerc[y][x], 3))
                    dailySoilData["Temp/L" + str(y+1)] = str(
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
        self.Ea_actual = []
        self.Et_max = []
        self.sublimation = []

        for x in range(0, self.numSoilLayers):
            self.layers_Et_actual[x] = []
            self.layersSoilWater[x] = []
            self.layersEsoil[x] = []
            self.layersPerc[x] = []
            self.layersTemperature[x] = []

        self.surfaceTemp = []
        self.sedimentYield = []

    def produce_data_analysis(self):
        data_analysis(self.file_name)
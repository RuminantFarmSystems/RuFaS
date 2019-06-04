################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# soil_nitrogen.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#          William Donovan
#
################################################################################

import csv
from RUFAS.output.report_handler import BaseReportHandler


# -------------------------------------------------------------------------------
# Class: SoilNitrogen
# Creates and prints to the file soil_nitrogen.csv
# -------------------------------------------------------------------------------
class SoilNitrogen(BaseReportHandler):

    def __init__(self, data):

        #
        # Sets active, report_name, f_name using data
        #
        self.set_properties(data)
        self.fieldNames = None

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.year = []
        self.julianDay = []
        self.numSoilLayers = 0
        self.freshN = []

        self.layersNO3 = []
        self.layersNH4 = []
        self.layersActiveN = []
        self.layersStableN = []
        self.nitrification = []
        self.volatilization = []
        self.denitrification = []
        self.layersTotNitriVolatil = []
        self.layersNtrans = []

    # ---------------------------------------------------------------------------
    # Function: get_header
    #           Writes the header (title and units) in the csvfile
    # ---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'NO3/L1', 'NO3/L2', 'NO3/L3',
                          'NH4/L1', 'NH4/L2', 'NH4/L3', 'ActiveN/L1',
                          'ActiveN/L2', 'ActiveN/L3', 'StableN/L1',
                          'StableN/L2', 'StableN/L3', 'FreshN', 'Nitri/L1',
                          'Nitri/L2', 'Nitri/L3', 'Volati/L1', 'Volati/L2',
                          'Volati/L3', 'Denitri/L1', 'Denitri/L2',
                          'Denitri/L3', 'TotNitrVolatil/L1',
                          'TotNitrVolatil/L2', 'TotNitrVolatil/L3',
                          'Ntrans/L1', 'Ntrans/L2', 'Ntrans/L3']

            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    lineterminator='\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '', }
            for fieldname in fieldnames:
                if (fieldname.startswith("NO3/") or fieldname.startswith("NH4/")
                        or fieldname.startswith("ActiveN")
                        or fieldname.startswith("StableN")
                        or fieldname == "FreshN"
                        or fieldname.startswith("Ntrans")):
                    units[fieldname] = 'kg'
                elif (fieldname.startswith("Nitri")
                      or fieldname.startswith("Volati")
                      or fieldname.startswith("Denitri")
                      or fieldname.startswith("TotNitrVolatil")):
                    units[fieldname] = 'kg/ha'
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

        for _ in range(0, self.numSoilLayers):
            self.layersNO3.append([])
            self.layersNH4.append([])
            self.layersActiveN.append([])
            self.layersStableN.append([])
            self.nitrification.append([])
            self.volatilization.append([])
            self.denitrification.append([])
            self.layersTotNitriVolatil.append([])
            self.layersNtrans.append([])

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
        self.freshN.append(soil.topLayerFreshN)

        for x in range(0, len(soil.listOfSoilLayers)):
            self.layersNO3[x].append(soil.listOfSoilLayers[x].NO3)
            self.layersNH4[x].append(soil.listOfSoilLayers[x].NH4)
            self.layersActiveN[x].append(soil.listOfSoilLayers[x].activeN)
            self.layersStableN[x].append(soil.listOfSoilLayers[x].stableN)
            self.nitrification[x].append(soil.listOfSoilLayers[x].nitrification)
            self.volatilization[x].append(soil.listOfSoilLayers[x].volatilization)
            self.denitrification[x].append(soil.listOfSoilLayers[x].denitrification)
            self.layersTotNitriVolatil[x].append(soil.listOfSoilLayers[x].totNitriVolatil)
            self.layersNtrans[x].append(soil.listOfSoilLayers[x].nTrans)

    # ---------------------------------------------------------------------------
    # Method: annual_update
    # ---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        '''Stores the yearly values that need to be printed in the report.'''
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
                dailySoilNitrogenData = {
                    'Year': str(self.year[x]),
                    'Julian Day': self.julianDay[x]
                }

                for y in range(0, self.numSoilLayers):
                    dailySoilNitrogenData["NO3/L" + str(y + 1)] = str(
                        round(self.layersNO3[y][x], 3))

                    dailySoilNitrogenData["NH4/L" + str(y + 1)] = str(
                        round(self.layersNH4[y][x], 3))

                    dailySoilNitrogenData["ActiveN/L" + str(y + 1)] = str(
                        round(self.layersActiveN[y][x], 3))

                    dailySoilNitrogenData["StableN/L" + str(y + 1)] = str(
                        round(self.layersStableN[y][x], 3))

                dailySoilNitrogenData["FreshN"] = str(round(self.freshN[x], 3))

                for y in range(0, self.numSoilLayers):
                    dailySoilNitrogenData["Nitri/L" + str(y + 1)] = str(
                        round(self.nitrification[y][x], 3))

                    dailySoilNitrogenData["Volati/L" + str(y + 1)] = str(
                        round(self.volatilization[y][x], 3))

                    dailySoilNitrogenData["Denitri/L" + str(y + 1)] = str(
                        round(self.denitrification[y][x], 3))

                for y in range(0, self.numSoilLayers):
                    dailySoilNitrogenData["TotNitrVolatil/L" + str(y + 1)] = str(
                        round(self.layersTotNitriVolatil[y][x], 3))

                    dailySoilNitrogenData["Ntrans/L" + str(y + 1)] = str(
                        round(self.layersNtrans[y][x], 3))

                writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                        lineterminator='\n')
                writer.writerow(dailySoilNitrogenData)

    # ---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    # ---------------------------------------------------------------------------
    def annual_flush(self):

        self.year = []
        self.julianDay = []
        self.freshN = []

        for x in range(0, self.numSoilLayers):
            self.layersNO3[x] = []
            self.layersNH4[x] = []
            self.layersActiveN[x] = []
            self.layersStableN[x] = []
            self.nitrification[x] = []
            self.volatilization[x] = []
            self.denitrification[x] = []
            self.layersTotNitriVolatil[x] = []
            self.layersNtrans[x] = []

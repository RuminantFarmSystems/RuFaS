################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# soil_nitrogen.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import csv
from RUFAS.output.report_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: SoilNitrogen
# Creates and prints to the file soil_nitrogen.csv
#-------------------------------------------------------------------------------
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
        self.cToN = []
        self.cToP = []
        self.decayRate = []
        self.freshMin = []
        self.freshDecomp = []
        self.freshConc = []
        self. activeConc = []
        self.stableConc = []
        self.NH4Conc = []
        self.enrichmentRatio = []
        self.freshLoss = []
        self. activeLoss = []
        self.stableLoss = []
        self.NH4Loss = []
        self.NO3Runoff = []
        self.NH4Runoff = []

        self.layersNO3 = []
        self.layersNH4 = []
        self.layersActiveN = []
        self.layersStableN = []
        self.layersActiveNMineralization = []
        self.nitrification = []
        self.volatilization = []
        self.denitrification = []
        self.layersNO3Conc = []
        self.layersNO3Perc = []
        self.layersNH4Conc = []
        self.layersNH4Perc = []
        self.layersActiveNConc = []
        self.layersActiveNPerc = []
        self.layersTotNitriVolatil = []
        self.layersNtrans = []




    #---------------------------------------------------------------------------
    # Function: get_header
    #           Writes the header (title and units) in the csvfile
    #---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'NO3/L1', 'NO3/L2', 'NO3/L3',
                          'NH4/L1', 'NH4/L2', 'NH4/L3', 'ActiveN/L1',
                          'ActiveN/L2', 'ActiveN/L3', 'StableN/L1',
                          'StableN/L2', 'StableN/L3', 'FreshN', 'CToN', 'CToP',
                          'DecayRate', 'NMinAct/L1', 'NMinAct/L2', 'NMinAct/L3',
                           'FreshMin', 'FreshDecomp', 'Nitri/L1', 'Nitri/L2',
                           'Nitri/L3', 'Volati/L1', 'Volati/L2', 'Volati/L3',
                           'Denitri/L1', 'Denitri/L2', 'Denitri/L3',
                           'FreshConc', 'ActiveConc', 'StableConc', 'NH4Conc',
                           'Enrich', 'FreshLoss', 'ActiveLoss', 'StableLoss',
                           'NH4Loss', 'NO3Runoff', 'NH4Runoff', 'NO3Conc/L1',
                           'NO3Conc/L2', 'NO3Conc/L3', 'NO3Perc/L1',
                           'NO3Perc/L2', 'NO3Perc/L3', 'NH4Conc/L1',
                           'NH4Conc/L2', 'NH4Conc/L3', 'NH4Perc/L1',
                           'NH4Perc/L2', 'NH4Perc/L3', 'ActiveConc/L1',
                           'ActiveConc/L2', 'ActiveConc/L3', 'ActivePerc/L1',
                           'ActivePerc/L2', 'ActivePerc/L3', 'TotNitrVolatil/L1',
                           'TotNitrVolatil/L2', 'TotNitrVolatil/L3',
                           'Ntrans/L1',
                           'Ntrans/L2', 'Ntrans/L3' ]

            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    lineterminator = '\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '', 'CToN': '', 'CToP': '',
                     'DecayRate': '', 'FreshConc': 'g/MT', 'ActiveConc': 'g/MT',
                      'StableConc': 'g/MT', 'NH4Conc': 'g/MT', 'Enrich': '',
                      'FreshLoss': 'kg/ha', 'ActiveLoss': 'kg/ha',
                      'StableLoss': 'kg/ha', 'NH4Loss': 'kg/ha',
                      'NO3Runoff': 'kg/ha', 'NH4Runoff': 'kg/ha',}
            for fieldname in fieldnames:
                if (fieldname.startswith("NO3/") or fieldname.startswith("NH4/")
                    or fieldname.startswith("ActiveN")
                    or fieldname.startswith("StableN")
                    or fieldname == "FreshN"
                    or fieldname.startswith("NMinAct")
                    or fieldname == "FreshMin"
                    or fieldname == "FreshDecomp"
                    or fieldname.startswith("Ntrans")):
                    units[fieldname] = 'kg'
                elif (fieldname.startswith("Nitri")
                      or fieldname.startswith("Volati")
                      or fieldname.startswith("Denitri")
                      or fieldname.startswith("NO3Perc")
                      or fieldname.startswith("NH4Perc")
                      or fieldname.startswith("ActivePerc")
                      or fieldname.startswith("TotNitrVolatil")):
                    units[fieldname] = 'kg/ha'
                elif (fieldname.startswith("NO3Conc/")
                      or fieldname.startswith("NH4Conc/") or
                      fieldname.startswith("ActiveConc/")):
                    units[fieldname] = 'kg N / mm'
            writer.writerow(units)

    #---------------------------------------------------------------------------
    # Function: initialize
    #           Transfers the needed data from Soil object to the report handler
    #---------------------------------------------------------------------------
    def initialize(self, state):

        soil = state.soil

        # initialize number of layer in soil summary report handler to get output
        # data pertaining to each soil layer
        # Initializes the output arrays for current soil water, Esoil, and
        # percolation for each soil layer
        self.numSoilLayers = len(soil.listOfSoilLayers)

        for _ in range (0, self.numSoilLayers):
            self.layersNO3.append([])
            self.layersNH4.append([])
            self.layersActiveN.append([])
            self.layersStableN.append([])
            self.layersActiveNMineralization.append([])
            self.nitrification.append([])
            self.volatilization.append([])
            self.denitrification.append([])
            self.layersNO3Conc.append([])
            self.layersNO3Perc.append([])
            self.layersNH4Conc.append([])
            self.layersNH4Perc.append([])
            self.layersActiveNConc.append([])
            self.layersActiveNPerc.append([])
            self.layersTotNitriVolatil.append([])
            self.layersNtrans.append([])

        self.write_header()

    #---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # Stores the daily values that need to be printed in the 'soil summary'
    # csv file
    #---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):

        soil = state.soil

        day = time.day
        year = time.year

        self.year.append(year)
        self.julianDay.append(day)
        self.cToN.append(soil.CToN)
        self.freshN.append(soil.topLayerFreshN)
        self.cToP.append(soil.CToP)
        self.freshMin.append(soil.freshMin)
        self.freshDecomp.append(soil.freshDecomp)
        self.decayRate.append(soil.decayRate)
        self.freshConc.append(soil.freshNConc)
        self.activeConc.append(soil.activeNConc)
        self.stableConc.append(soil.stableNConc)
        self.NH4Conc.append(soil.NH4Conc)
        self.enrichmentRatio.append(soil.enrichmentRatio)
        self.freshLoss.append(soil.freshNLoss)
        self.activeLoss.append(soil.activeNLoss)
        self.stableLoss.append(soil.stableNLoss)
        self.NH4Loss.append(soil.NH4Loss)
        self.NO3Runoff.append(soil.NO3Runoff)
        self.NH4Runoff.append(soil.NH4Runoff)


        for x in range(0, len(soil.listOfSoilLayers)):
            self.layersNO3[x].append(soil.listOfSoilLayers[x].NO3)
            self.layersNH4[x].append(soil.listOfSoilLayers[x].NH4)
            self.layersActiveN[x].append(soil.listOfSoilLayers[x].activeN)
            self.layersStableN[x].append(soil.listOfSoilLayers[x].stableN)
            self.layersActiveNMineralization[x].append(
                soil.listOfSoilLayers[x].nMinAct)
            self.nitrification[x].append(soil.listOfSoilLayers[x].nitrification)
            self.volatilization[x].append(soil.listOfSoilLayers[x].volatilization)
            self.denitrification[x].append(soil.listOfSoilLayers[x].denitrification)
            self.layersNO3Conc[x].append(soil.listOfSoilLayers[x].NO3Conc)
            self.layersNO3Perc[x].append(soil.listOfSoilLayers[x].NO3Perc)
            self.layersNH4Conc[x].append(soil.listOfSoilLayers[x].NH4Conc)
            self.layersNH4Perc[x].append(soil.listOfSoilLayers[x].NH4Perc)
            self.layersActiveNConc[x].append(soil.listOfSoilLayers[x].activeNConc)
            self.layersActiveNPerc[x].append(soil.listOfSoilLayers[x].activeNPerc)
            self.layersTotNitriVolatil[x].append(soil.listOfSoilLayers[x].totNitriVolatil)
            self.layersNtrans[x].append(soil.listOfSoilLayers[x].nTrans)

    #---------------------------------------------------------------------------
    # Method: annual_update
    #---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        '''Stores the yearly values that need to be printed in the report.'''
        pass

    #---------------------------------------------------------------------------
    # Function: write_annual_report
    #           Appends the annual report to the output file
    # Soil Summary is a cvsfile
    #---------------------------------------------------------------------------
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
                    dailySoilNitrogenData["NO3/L" + str(y+1)] = str(
                        round(self.layersNO3[y][x], 3))

                    dailySoilNitrogenData["NH4/L" + str(y+1)] = str(
                        round(self.layersNH4[y][x], 3))

                    dailySoilNitrogenData["ActiveN/L" + str(y+1)] = str(
                        round(self.layersActiveN[y][x], 3))

                    dailySoilNitrogenData["StableN/L" + str(y+1)] = str(
                        round(self.layersStableN[y][x], 3))

                dailySoilNitrogenData["FreshN"] = str(round(self.freshN[x], 3))
                dailySoilNitrogenData["CToN"] = str(round(self.cToN[x], 3))
                dailySoilNitrogenData["CToP"] = str(round(self.cToP[x], 3))
                dailySoilNitrogenData["DecayRate"] = str(round(self.decayRate[x], 3))

                for y in range(0, self.numSoilLayers):
                    dailySoilNitrogenData["NMinAct/L" + str(y+1)] = str(
                        round(self.layersActiveNMineralization[y][x], 4))

                dailySoilNitrogenData["FreshMin"] = str(round(self.freshMin[x], 3))
                dailySoilNitrogenData["FreshDecomp"] = str(round(self.freshDecomp[x], 3))

                for y in range(0, self.numSoilLayers):
                    dailySoilNitrogenData["Nitri/L" + str(y+1)] = str(
                        round(self.nitrification[y][x], 3))

                    dailySoilNitrogenData["Volati/L" + str(y+1)] = str(
                        round(self.volatilization[y][x], 3))

                    dailySoilNitrogenData["Denitri/L" + str(y+1)] = str(
                        round(self.denitrification[y][x], 3))

                dailySoilNitrogenData["FreshConc"] = str(round(self.freshConc[x], 3))
                dailySoilNitrogenData["ActiveConc"] = str(round(self.activeConc[x], 3))
                dailySoilNitrogenData["StableConc"] = str(round(self.stableConc[x], 3))
                dailySoilNitrogenData["NH4Conc"] = str(round(self.NH4Conc[x], 3))
                dailySoilNitrogenData["Enrich"] = str(round(self.enrichmentRatio[x], 3))
                dailySoilNitrogenData["FreshLoss"] = str(round(self.freshLoss[x], 3))
                dailySoilNitrogenData["ActiveLoss"] = str(round(self.activeLoss[x], 4))
                dailySoilNitrogenData["StableLoss"] = str(round(self.stableLoss[x], 3))
                dailySoilNitrogenData["NH4Loss"] = str(round(self.NH4Loss[x], 4))
                dailySoilNitrogenData["NO3Runoff"] = str(round(self.NO3Runoff[x], 3))
                dailySoilNitrogenData["NH4Runoff"] = str(round(self.NH4Runoff[x], 3))

                for y in range(0, self.numSoilLayers):
                    dailySoilNitrogenData["NO3Conc/L" + str(y+1)] = str(
                        round(self.layersNO3Conc[y][x], 3))

                    dailySoilNitrogenData["NO3Perc/L" + str(y+1)] = str(
                        round(self.layersNO3Perc[y][x], 3))

                    dailySoilNitrogenData["NH4Conc/L" + str(y+1)] = str(
                        round(self.layersNH4Conc[y][x], 3))

                    dailySoilNitrogenData["NH4Perc/L" + str(y+1)] = str(
                        round(self.layersNH4Perc[y][x], 4))

                    dailySoilNitrogenData["ActiveConc/L" + str(y+1)] = str(
                        round(self.layersActiveNConc[y][x], 3))

                    dailySoilNitrogenData["ActivePerc/L" + str(y+1)] = str(
                        round(self.layersActiveNPerc[y][x], 3))

                    dailySoilNitrogenData["TotNitrVolatil/L" + str(y+1)] = str(
                        round(self.layersTotNitriVolatil[y][x], 3))

                    dailySoilNitrogenData["Ntrans/L" + str(y+1)] = str(
                        round(self.layersNtrans[y][x], 3))


                writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator = '\n')
                writer.writerow(dailySoilNitrogenData)

    #---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    #---------------------------------------------------------------------------
    def annual_flush(self):

        self.year = []
        self.julianDay = []
        self.freshN = []
        self.cToN = []
        self.cToP = []
        self.decayRate = []
        self.freshMin = []
        self.freshDecomp = []
        self.freshConc = []
        self.activeConc = []
        self.stableConc = []
        self.NH4Conc = []
        self.enrichmentRatio = []
        self.freshLoss = []
        self.activeLoss = []
        self.stableLoss = []
        self.NH4Loss = []
        self.NO3Runoff = []
        self.NH4Runoff = []

        for x in range(0, self.numSoilLayers):
            self.layersNO3[x] = []
            self.layersNH4[x] = []
            self.layersActiveN[x] = []
            self.layersStableN[x] = []
            self.layersActiveNMineralization[x] = []
            self.nitrification[x] = []
            self.volatilization[x] = []
            self.denitrification[x] = []
            self.layersNO3Conc[x] = []
            self.layersNO3Perc[x] = []
            self.layersNH4Conc[x] = []
            self.layersNH4Perc[x] = []
            self.layersActiveNConc[x] = []
            self.layersActiveNPerc[x] = []
            self.layersTotNitriVolatil[x] = []
            self.layersNtrans[x] = []
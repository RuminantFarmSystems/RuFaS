################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# Output.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

from .output_handler import ReportHandler
import csv

#-------------------------------------------------------------------------------
# Class: SampleOutput1
#        
#-------------------------------------------------------------------------------
class SoilSummary(ReportHandler):
    
    layersSoilWater = []
    layersEsoil = []
    layersPerc = []
    
    def __init__(self):
             
        super().__init__("Soil Summary", "Soil_Summary.csv")
                 
        #
        # Yearly Output
        # Single values
        #
        self.sampleYearly = None
        
        #
        # Monthly Outputs
        # 1D Lists [m]
        #
        self.sampleMonthly = [None]*12
        
        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.year = []
        self.julianDay = []
        self.precip = []
        self.runoff = []   
        self.potentialEvapotranspiration = []
        self.cropTranspiration = []
        self.sublimation = []
        self.sedimentYield = []
        self.numSoilLayers = 0   
    
    #---------------------------------------------------------------------------
    # Function: setNumSoilLayers
    # Initializes the output arrays for current soil water, Esoil, and 
    # percolation for each soil layer
    #--------------------------------------------------------------------------- 
    def setNumSoilLayers(self, numSoilLayers):
        self.numSoilLayers = numSoilLayers
        for _ in range (0, numSoilLayers):
            soilLayerSoilWater = []
            self.layersSoilWater.append(soilLayerSoilWater)
            
            soilLayerEsoil = []
            self.layersEsoil.append(soilLayerEsoil)
            
            soilLayerPerc = []
            self.layersPerc.append(soilLayerPerc)

    #---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # Stores the daily values that need to be printed in the 'soil summary'
    # csv file
    #--------------------------------------------------------------------------- 
    def daily_update(self, soil, weather, time):
        pass
    
    #---------------------------------------------------------------------------
    # Function: compile_annual_report
    #           Appends the annual report to the output file
    # Soil Summary is a cvsfile
    #---------------------------------------------------------------------------
    def compile_annual_report(self):
        with open(self.path, 'w') as csvfile:
            
            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'Rainfall', 'Runoff (Q)',
                          'Potential Evapotranspiration (E0)', 
                          'Crop Transpiration (Etrans)',
                          'Maximum Sublimation (Esoil)']
            
            for x in range(0, self.numSoilLayers):
                fieldnames.append("SoilWater/L" + str(x+1))

            for x in range(0, self.numSoilLayers):
                fieldnames.append("Esoil/L" + str(x+1))
                
            for x in range(0, self.numSoilLayers):
                fieldnames.append("Perc/L" + str(x+1))
                
            fieldnames.append("Sediment Yield")
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, 
                                    lineterminator = '\n')
            writer.writeheader()
    
            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '',
                             'Rainfall': "mm", 'Runoff (Q)': "mm", 
                             'Potential Evapotranspiration (E0)': "mm d^-1",
                             'Crop Transpiration (Etrans)': "mm H2O",
                             'Maximum Sublimation (Esoil)': "mm H2O",
                             'Sediment Yield': "metric tons"}
            for fieldname in fieldnames:
                if fieldname.startswith("SoilWater"):
                    units[fieldname] = 'mm'
                elif fieldname.startswith("Esoil"):
                    units[fieldname] = 'mm H2O'
                elif fieldname.startswith("Perc"):
                    units[fieldname] = 'mm H2O'
            writer.writerow(units)

            # 3) Write data day by day
            for x in range(0, len(self.julianDay)):
                dailySoilData = {'Year': str(self.year[x]), 
                    'Julian Day': self.julianDay[x], 
                    'Rainfall': str(round(float(self.precip[x]), 2)), 
                    'Runoff (Q)': str(round(self.runoff[x], 2)),
                    'Potential Evapotranspiration (E0)': str(round
                                    (self.potentialEvapotranspiration[x],3)),
                    'Crop Transpiration (Etrans)': str(round
                                    (self.cropTranspiration[x],3)),
                    'Maximum Sublimation (Esoil)': str(round
                                    (self.sublimation[x],3)),
                    'Sediment Yield': str(round(self.sedimentYield[x],3))}
                
                for y in range(0, self.numSoilLayers):
                        dailySoilData["SoilWater/L" + str(y+1)] = str(
                            round(self.layersSoilWater[y][x], 3))
                        dailySoilData["Esoil/L" + str(y+1)] = str(
                            round(self.layersEsoil[y][x], 3))
                        dailySoilData["Perc/L" + str(y+1)] = str(
                            round(self.layersPerc[y][x], 3))

                writer.writerow(dailySoilData)
                    
    #---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    #---------------------------------------------------------------------------
    def annual_flush(self):
        #self.precip = []
        #self.runoff = []
        pass
    
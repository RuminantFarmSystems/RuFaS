################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# Output.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

from .output_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: FarmSummary
# 
#-------------------------------------------------------------------------------
class FarmSummary(BaseReportHandler):
    
    def __init__(self, data):
             
        #
        # Sets active, report_name, f_name using data
        #
        self.set_properties(data)
                 
        #
        # ANIMAL PRODUCTION
        #
        # 1. Animal Production
        self.total_milk = 0.0           # Liters
        self.avg_milk_per_cow = 0.0     # Liters
        
        # 2. Animals Sold
        self.live_weight_sold = 0.0     # kg
        self.meat_production = 0.0      # kg
        
        # 3. Animals Purchased
        self.animals_purchased = 0      # units
        
        # 4. Feed Consumed
        self.feed_total = 0.0           # kg
        self.feed_purchased = 0.0       # kg
        self.feed_produced = 0.0        # kg
        
        #
        # MANURE
        #
        self.DM_produced = 0.0
        self.C_produced = 0.0
        self.N_produced = 0.0
        self.P_produced = 0.0
        
        self.collection_loss = 0.0
        self.storage_loss = 0.0
        
        #
        # SOIL
        #
        self.soil_balance = { 'C': 0.0,
                              'P': 0.0,
                              'N': 0.0 }
        
        self.soil_loss = { 'C': 0.0,
                           'P': 0.0,
                           'N': 0.0 }
        
        self.soil_erosion_mass = 0.0
        
        #
        # FEED
        #
        self.feed_sold = 0.0
        self.feed_consumed = 0.0
        
        #
        # NUTRIENTS
        #
        self.whole_farm_production = { 'C': 0.0,
                                       'P': 0.0,
                                       'N': 0.0,
                                       'H20': 0.0,
                                       'GHG': 0.0 }
        
    #---------------------------------------------------------------------------
    # Function: get_data
    #           Transfers the needed data from Soil object to the report handler
    #---------------------------------------------------------------------------
    def get_data(self):
        
        pass
    
    #---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # 
    #--------------------------------------------------------------------------- 
    def daily_update(self, soil, weather, time):
        
        pass 
 
    #---------------------------------------------------------------------------
    # Function: write_annual_report
    #           
    #---------------------------------------------------------------------------
    def write_annual_report(self):
        
        mode = 'a+' if self.get_fPath().exists() else 'w+'
        
        with self.get_fPath().open(mode) as f:
            
            pass
                    
    #---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    #---------------------------------------------------------------------------
    def annual_flush(self):
        
        pass
        
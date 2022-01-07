"""
RUFAS: Ruminant Farm Systems Model

File name: base_handler.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""


from ..sand_separators.sand_separation_lane import SandSeparationLane


class BaseHandler:
    """
    Description
    ------------

    Attributes
    ----------

    """ 

    def __init__(self, pen, handler, handler_data, reception_pit):
        self.pen = pen
        self.handler_name = handler
        self.sand_lane = None
        self.reception_pit = reception_pit

        self.cow_num = 0

        self.bedding = pen.bedding_type
        self.time_per_cleaning = handler_data['time_per_cleaning'] if 'time_per_cleaning' in handler_data else 8
        self.cleanings_per_day = handler_data['cleanings_per_day'] if 'cleanings_per_day' in handler_data else 2

        self.bedding_density = 0
        self.bedding_mass_per_day = 0

        self.density = 0
        self.bedding_added = 0
        self.flush_water_volume = 0
        self.flush_water_volume_mlk = 0
        self.bedding_washed_percent = 0
        self.bedding_washed = 0
        self.bedding_dry_matter = 0

        self.water_use_rate = 0
        self.flush_water_daily = 0

        self.TS_loss_perc = 0
        self.VS_loss_perc = 0
        self.flow_rate = 0

        self.K_excreted = 0
        self.P_excreted = 0
        self.N_excreted = 0
        self.WIP = 0
        self.WOP = 0
        self.CH4 = 0
        self.raw_manure = 0

        self.TS_loss = 0
        self.VS_loss = 0

        self.NH4 = 0

        self.initialize_bedding()

    def init_sand_lane(self, sand_lane_data):
        if self.bedding == 'sand':
            self.sand_lane = SandSeparationLane(sand_lane_data)

    def initialize_bedding(self):
        if self.bedding.startswith("organic"):
            self.bedding_added = 11.8
            self.bedding_dry_matter = 0.9
            self.bedding_washed_percent = 0.5
            self.density = 250
        elif self.bedding.startswith("sand"):
            self.bedding_added = 20
            self.bedding_dry_matter = 0.9
            self.bedding_washed_percent = 0.8
            self.density = 1500

    def reset_daily_variables(self):
        self.K_excreted = 0
        self.P_excreted = 0
        self.N_excreted = 0
        self.WIP = 0
        self.WOP = 0
        self.CH4 = 0
        self.raw_manure = 0

        self.TS_loss = 0
        self.VS_loss = 0

        self.NH4 = 0

    def reset_annual_variables(self):
        pass

    def update_all(self):
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure handling.
            "pseudocode_manure_management" MS.3
        """
        self.update_handler()
        self.flush_water()
        self.N_loss()
        self.P_loss()
        self.K_loss()
        self.solids()
        if self.bedding == 'sand':
            self.sand_lane.sand_lane()
        self.CH4_effluent()
        self.WIP_WOP()

    def update_handler(self):
        self.cow_num = len(self.pen.animals_in_pen)
        self.flush_water_daily = self.cow_num * self.water_use_rate
        self.K_excreted = self.pen.manure['K_manure']
        self.P_excreted = self.pen.manure['p_excrt_manure']
        self.N_excreted = self.pen.manure['MN']
        self.raw_manure = self.pen.manure['Mkg']
        self.WIP = self.pen.manure['WIP_frac'] * self.raw_manure
        self.WOP = self.pen.manure['WOP_frac'] * self.raw_manure
        self.CH4 = self.pen.manure['CH4_manure']

    def flush_water(self):
        """
        Description:
            Calculates Flush Water Volume and passes it to the associated separa
            "pseudocode_manure_management" MS.3.A
        """

        self.flush_water_volume = self.raw_manure + self.flush_water_daily + self.bedding_washed
        self.reception_pit.flush_water_volume += self.flush_water_volume

    def N_loss(self):
        """
        Description:
            Updates Nitrogen mass in the reception_pit from excreted manure
            "pseudocode_manure_management" MS.3.B
        """

        self.reception_pit.N = self.N_excreted

    def P_loss(self):
        """
        Description:
            Updates Phosphorus mass in the reception_pit from excreted manure
    "       pseudocode_manure_management" MS.3.C
        """

        self.reception_pit.P = self.P_excreted

    def K_loss(self):
        """
        Description:
            Updates Potassium mass in the reception_pit from excreted manure
            "pseudocode_manure_management" MS.3.D
        """

        self.reception_pit.K = self.K_excreted

    def solids(self):
        """
        Description:
            Updates Total and Volatile Solids in the reception_pit from excreted manure
            "pseudocode_manure_management" MS.3.E
        """
        self.TS_loss = self.flush_water_volume * self.TS_loss_perc
        self.VS_loss = self.TS_loss * self.VS_loss_perc

        self.reception_pit.TS += self.TS_loss
        self.reception_pit.VS += self.VS_loss

    # TODO: move to sand lane class
    # def sand_lane(self):
    #     """
    #     Description:
    #         Sand separation lane. Method only called for sand bedding.
    #     """
    #     sand_lane = self.sand_lane
    #     sand_lane.sand_washed_with_water = self.bedding_mass_per_day  # kg/day
    #     sand_lane.sand_mass_separated = sand_lane.sand_separation_efficiency * \
    #                                     sand_lane.sand_washed_with_water  # kg/day
    #     sand_lane.sand_volume_separated = sand_lane.sand_mass_separated / self.bedding_density  # m3/day

    def CH4_effluent(self):
        self.reception_pit.CH4 += self.CH4

    def WIP_WOP(self):
        self.reception_pit.WIP += self.WIP
        self.reception_pit.WOP += self.WOP

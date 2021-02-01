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

    def __init__(self, handler_data):

        self.bedding_density = None
        self.bedding_mass_per_day = None
        self.K_excreted = None
        self.P_excreted = None
        self.N_excreted = None
        self.flush_water_daily = None
        self.raw_manure = None
        self.separator = None
        self.sand_lane = None

        if handler_data is None or handler_data['default']:
            self.default = True
            self.set_defaults()
        else:
            self.water_use_rate = handler_data['water_use_rate']
            self.time_per_cleaning = handler_data['time_per_cleaning']
            self.cleanings_per_day = handler_data['cleanings_per_day']
            self.init_sand_lane(handler_data['sand_lane'])

        self.density = 0
        self.bedding_added = 0
        self.flush_water_volume = 0
        self.bedding_washed_percent = 0
        self.bedding_washed = 0
        self.bedding_dry_matter = 0

        self.TS_loss = 0
        self.VS_loss = 0

        self.TS_loss_perc = 0
        self.VS_loss_perc = 0
        self.flow_rate = 0
        self.NH4 = 0

        self.bedding = None

        self.flush_water_volume_mlk = 0

    def init_sand_lane(self, sand_lane_data):
        if self.bedding == 'sand':
            self.sand_lane = SandSeparationLane(sand_lane_data)

    def set_defaults(self):
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

    def update_all(self, manure):
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure handling.
            "pseudocode_manure_management" MS.3

        Args:
            manure: an instance of the ManureManagement class specified in
                manure_management.py
        """
        self.flush_water(manure)
        self.N_loss(manure)
        self.P_loss(manure)
        self.K_loss(manure)
        self.solids(manure)
        if self.bedding == 'sand':
            self.sand_lane(manure)

    def flush_water(self, manure):
        """
        Description:
            Calculates Flush Water Volume in the separator that processes the
            collected manure
            "pseudocode_manure_management" MS.3.A

        Args:
            manure
        """

        self.flush_water_volume = self.raw_manure + self.flush_water_daily + self.bedding_washed
        manure.separators[self.separator].flush_water_volume += self.flush_water_volume

    def N_loss(self, manure):
        """
        Description:
            Updates Nitrogen mass in the separator from excreted manure
            "pseudocode_manure_management" MS.3.B

        Args:
            manure
        """

        manure.separators[self.separator].N = self.N_excreted

    def P_loss(self, manure):
        """
        Description:
            Updates Phosphorus mass in the separator from excreted manure
    "       pseudocode_manure_management" MS.3.C

        Args:
            manure
        """

        manure.separators[self.separator].P = self.P_excreted

    def K_loss(self, manure):
        """
        Description:
            Updates Potassium mass in the separator from excreted manure
            "pseudocode_manure_management" MS.3.D

        Args:
            manure
        """

        manure.separators[self.separator].K = self.K_excreted

    def solids(self, manure):
        """
        Description:
            Updates Total and Volatile Solids in the separator from excreted manure
            "pseudocode_manure_management" MS.3.E

        Args:
            manure
        """
        self.TS_loss = self.flush_water_volume * self.TS_loss_perc
        self.VS_loss = self.TS_loss * self.VS_loss_perc

        manure.separators[self.separator].TS += self.TS_loss
        manure.separators[self.separator].VS += self.VS_loss

    def sand_lane(self, manure):
        """
        Description:
            Sand separation lane. Method only called for sand bedding.
        Args:
            manure:

        Returns:

        """
        sand_lane = manure.separators[self.separator]
        sand_lane.sand_washed_with_water = self.bedding_mass_per_day  # kg/day
        sand_lane.sand_mass_separated = sand_lane.sand_separation_efficiency * \
                                        sand_lane.sand_washed_with_water  # kg/day
        sand_lane.sand_volume_separated = sand_lane.sand_mass_separated / self.bedding_density  # m3/day

from .sand_lane import SandLane


class BaseHandler:
    def __init__(self, handler_data):

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
            self.sand_lane = SandLane(sand_lane_data)

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
            "pseudocode_manure_storage" MS.3

        Args:
            self: an instance of the Pen class specified in pen.py representing
                the pen from which manure is being collected
            manure: an instance of the ManureStorage class specified in
                manure_management.py
        """
        self.flush_water(manure)
        self.N_loss(manure)
        self.P_loss(manure)
        self.K_loss(manure)
        self.solids(manure)
        if self.bedding == 'sand':
            sand_lane(self, manure)

    def flush_water(pen, manure):
        """
        Description:
            Calculates Flush Water Volume in the separator that processes the
            collected manure
            "pseudocode_manure_storage" MS.3.A

        Args:
            pen
            manure
        """

        pen.flush_water_volume = pen.raw_manure + pen.flush_water_daily + pen.bedding_washed
        manure.separators[pen.separator].flush_water_volume += pen.flush_water_volume

    def N_loss(pen, manure):
        """
        Description:
            Updates Nitrogen mass in the separator from excreted manure
            "pseudocode_manure_storage" MS.3.B

        Args:
            pen
            manure
        """

        manure.separators[pen.separator].N = pen.N_excreted

    def P_loss(pen, manure):
        """
        Description:
            Updates Phosphorus mass in the separator from excreted manure
    "       pseudocode_manure_storage" MS.3.C

        Args:
            pen
            manure
        """

        manure.separators[pen.separator].P = pen.P_excreted

    def K_loss(pen, manure):
        """
        Description:
            Updates Potassium mass in the separator from excreted manure
            "pseudocode_manure_storage" MS.3.D

        Args:
            pen
            manure
        """

        manure.separators[pen.separator].K = pen.K_excreted

    def solids(pen, manure):
        """
        Description:
            Updates Total and Volatile Solids in the separator from excreted manure
            "pseudocode_manure_storage" MS.3.E

        Args:
            pen
            manure
        """
        pen.TS_loss = pen.flush_water_volume * pen.TS_loss_perc
        pen.VS_loss = pen.TS_loss * pen.VS_loss_perc

        manure.separators[pen.separator].TS += pen.TS_loss
        manure.separators[pen.separator].VS += pen.VS_loss

    def sand_lane(pen, manure):
        """
        Description:
            Sand separation lane. Method only called for sand bedding.
        Args:
            pen:
            manure:

        Returns:

        """
        sand_lane = manure.separators[pen.separator]
        sand_lane.sand_washed_with_water = pen.bedding_mass_per_day  # kg/day
        sand_lane.sand_mass_separated = sand_lane.sand_separation_efficiency * sand_lane.sand_washed_with_water  # kg/day
        sand_lane.sand_volume_separated = sand_lane.sand_mass_separated / pen.bedding_density  # m3/day
from RUFAS.routines.field.crop.crop_types import crop_config

supported_species = [item.lower() for item in crop_config.__dict__.keys() if not item.startswith("__")]


class BaseCrop:
    """BaseCrop is the parent class of all Crop type objects
       and their respective classes. Crop attributes are initialized here first
       and eventually overridden by the instantiation of a specific Crop object.
       Further description of each attribute is provided beneath the attribute's
       initialization if clarification is needed.
    """
    def __init__(self, crop_name=None, data=None, species=None):
        """create an instance of BaseCrop class

            Args:
                crop_name (str): the name of the crop
                data (dict): a dictionary containg crop data
                species (str): the species of the crop (see crop_config.py)
        """
        #  id variables
        self.crop_name = 'null'
        """str: name of the crop: alfalfa, corn, etc."""
        self.crop_type = ''  # TODO: What strings are accepted? - GitHub Issue #174
        """str: the growing type of the crop: perennial, annual ..."""
        self.harvest_quality = 'null'  # TODO: don't know what harvest quality is - GitHub Issue #168
        self.feed_id = 'null'
        """str: the ID of the feed to be modified, ending in 'g' if it is a grown feed"""
        self.raw_id = 'null'
        """str: the raw ID of the feed to be modified"""

        # planting information
        """create an instance of ``BaseCrop``"""
        self.plant_years = []
        """:obj:`list` of :obj:`float`: a list of years in which the crop will be grown"""
        self.repeat = 0
        """float: the number of years between each grow year for the crop"""
        self.planting_day = 0
        """float: the day of the year that the crop will be first planted (Julian calendar)"""
        self.harvest_day = 0
        """float: the day of the year that the crop will be harvested (Julian calendar)"""
        self.harvest_type = ''  # TODO: What strings are accepted? - GitHub Issue #174
        """str: the harvest schedule that the crop will be on: scheduled, optimal..."""
        self.planting_order = ''  # TODO: What strings are accepted? - GitHub Issue #174
        """str: in the case of double cropping, the order in which the crop will be planted"""

        # starting points for crop status
        self.planted = False
        """bool: has the crop been planted or not?"""
        self.growing = False
        """bool: is the crop is currently growing?"""
        self.killed = False
        """bool: has been killed?"""
        self.kill_year = False
        """bool: is this the year the crop is killed?"""
        self.kill_day = -1
        """float: Julian_day on which the crop will be killed"""
        self.extracted = False
        """bool: was the crop extracted from the field or not? 
             This is independent of whether or not the crop was killed.
        """
        self.fix_nitrogen = False
        "bool: does this plant fix nitrogen?"

        # heat units
        self.T_base_min = 10  # pseudocode C.2.A.3
        """float: minimum temperature required for growth (Celsius)"""
        self.T_base_max = 30  # pseudocode C.2.A.4
        """float: maximum temperature required to sustain growth (Celsius)"""
        self.PHU = 800  # psuedocode C.2.B.1
        """crop-specific total heat units required for maturity"""

        self.accumulated_HU = 0  # pseudocode C.2.B.1
        """float: heat units accumulated including the current day of the simulation"""
        self.prev_accumulated_HU = 0  # pseudocode C.2.B.1
        """float: heat units accumulated excluding the current day of the simulation"""
        self.fr_PHU = 0  # pseudocode C.2.B.1
        """float: fraction of Potential Heat Units"""
        self.prev_fr_PHU = 0  # pseudocode C.2.B.1
        """float: fraction of PHU accumulated excluding current day of simulation"""

        # LAI
        self.fr_PHU_1 = 0.15  # psuedocode C.8.A
        """float: first PHU shape coefficient, used in LAI calculations"""
        self.fr_PHU_2 = 0.50  # psuedocode C.8.A
        """float: second PHU shape coefficient, used in LAI calculations"""
        self.fr_LAI_1 = 0.01  # psuedocode C.8.A.2
        """float: first LAI shape coefficient, used in LAI calculations"""
        self.fr_LAI_2 = 0.95  # psuedocode C.8.A.1
        """float: second LAI shape coefficient, used in LAI calculations"""
        self.fr_PHU_sen = 0.90  # psuedocode C.8.A.6
        """float: crop-specific fraction of PHU, at which senescence becomes dominant growth process"""
        self.fr_PHU_harvest = 1  # psuedocode C.10.A.1
        """float: fraction of PHU at harvest"""
        self.fr_PHU_harvest_min = 0.7  # psuedocode C.11.C.2
        """float: minimum fraction of PHU acquired to warrant harvest"""
        self.LAI_max = 3  # psuedocode C.8.A.4
        """float: crop-specific maximum LAI"""
        self.LAI_min = 0  # TODO: missing psuedocode - GitHub Issue #168
        """float: crop-specific minimum possible LAI"""
        self.prev_fr_LAI_max = 0  # psuedocode C.8.A.3
        """float: accumulated LAI fraction for the previous day"""
        self.fr_LAI_max = 0  # psuedocode C.8.A.3
        """float: accumulated LAI fraction for the current day"""
        self.prev_LAI_actual = 0  # psuedocode C.8.A.4
        """float: calculated LAI for the previous day"""
        self.LAI_actual = 0
        """float: calculated LAI for the current day"""

        # root depth
        self.z_root_max = 1500  # pseudocode C.3.A.2
        """float: maximum depth of root development (mm)"""
        self.fr_root = 0  # pseudocode C.3.A.1
        """float: fraction of total biomass partitioned to roots on current day"""
        self.z_root = 0  # pseudocode C.3.A.2
        """float: depth of root development (mm)"""

        # biomass
        self.kl = 0.65  # psuedocode C.9.A.2
        """float: light extinction coefficient"""
        self.RUE = 20  # psuedocode C.9.A.2
        """float: crop-specific radiation use efficiency"""
        self.T_opt = 25  # psuedocode C.7.B.2
        """float: crop-specific optimal temperature for growth"""
        self.gamma_reg = 0  # psuedocode C.9.A.3
        """float: plant growth factor (0-1)"""
        self.d_biomass_max = 0  # psuedocode C.9.A.3
        """float: maximum potential increase in biomass for a given day"""
        self.d_biomass_actual = 0  # psuedocode C.9.A.3
        """float: calculated increase in biomass"""
        self.biomass_actual = 0  # psuedocode C.9.A.3 # TODO: What are the units? - GitHub Issue #174
        """float: calculated biomass for the current day"""
        self.prev_biomass_actual = 0  # psuedocode C.9.A.3
        """float: calculated biomass for the previous day"""

        # water uptake
        self.epco = 0  # psuedocode C.4.B.2
        """float: plant uptake compensation factor, a value between 0.01 and 1.00"""
        self.beta_w = 0  # psuedocode C.4.A.1
        """water-use distribution parameter"""
        self.water_actual_up = 0  # psuedocode C.4.A.2
        """water uptake (mm)"""
        self.water_uptake_each_layer = []  # psuedocode C.4.A.2
        """water uptake from each layer (mm)"""

        # nitrogen uptake
        self.beta_n = 10
        """float: nitrogen uptake distribution parameter.
           This value does not significantly affect N uptake, but does impact NO3 removed 
           from the surface by allowing plants to extract a greater percent of N from the 
           upper soil layers.
        """
        self.fr_n1 = 0.04  # psuedocode C.5.A.2
        """float: normal fraction of nitrogen in plant biomass before emergence"""  # TODO: GitHub Issue #179
        self.fr_n2 = 0.03  # psuedocode C.5.A.2
        """float: normal fraction of nitrogen in plant biomass at emergence"""  # TODO: GitHub Issue #179
        self.fr_n3 = 0.02  # psuedocode C.5.A.2
        """float: normal fraction of nitrogen in plant biomass at maturity"""
        self.fr_n3ish = 0.02  # psuedocode C.5.A.2
        """float: normal fraction of nitrogen in plant biomass near maturty"""
        self.N_fix = 0
        """float: Amount of nitrogen added to the plant biomass by fixation (kg/ha)"""
        self.bio_N_opt = 0  # psuedocode C.5.B.2
        """float: optimal mass of nitrogen stored in the plant on a given day (kg/ha)"""
        self.bio_N = 0  # psuedocode C.5.B.2
        """float: Actual mass of nitrogen stored in plant material (kg/ha)"""
        self.fr_N = 0  # psuedocode C.5.A.2
        """float: Fraction of nitrogen stored in plant biomass on a given day"""
        self.N_up = 0  # psuedocode C.5.B.3
        """float: potential nitrogen uptake by the plant (kg/ha)"""
        self.act_N_up_each_layer = []  # psuedocode C.5.C.4 
        """:obj:`list` of :obj:`float`: actual nitrogen uptake from each soil layer (kg/ha)"""
        self.N_actual_up = 0  # psuedocode C.5.C.7
        """float: total nitrogen uptake (kg/ha)"""

        # phosphorus uptake
        self.beta_p = 10  # psuedocode C.6.C.1
        """float: phosphorus uptake distribution parameter"""
        self.fr_PHU_50 = 0.5  # psuedocode C.6.A.1
        """fraction of potential heat units accumulated at 50% plant maturity"""
        self.fr_PHU_100 = 1.0  # psuedocode C.6.A.1
        """fraction of potential heat units accumulated at 100% plant maturity"""
        self.fr_p1 = 0.004  # psuedocode C.6.B.1
        """float: normal fraction of phosphorus in plant biomass at emergence"""  # TODO: GitHub Issue #179
        self.fr_p2 = 0.003  # psuedocode C.6.B.1
        """float: normal fraction of phosphorus in plant biomass at emergence"""  # TODO: GitHub Issue #179
        self.fr_p3 = 0.002  # psuedocode C.6.B.1
        """float: normal fraction of phosphorus in plant biomass at maturity"""
        self.fr_p3ish = 0.002  # psuedocode C.6.B.1
        """float: normal fraction of phosphorus in plant biomass near maturity"""
        self.bio_P_opt = 0  # psuedocode C.6.B.2
        """optimal mass of phosphorus stored inplant biomass on a given day (kg/ha)"""
        self.bio_P = 0  # psuedocode C.6.B.1
        """float: actual mass of phosphorus stored in plant material (kg/ha)"""
        self.fr_P = 0  # psuedocode C.6.A.2
        """float: fraction of phosphorus in the plant biomass on a given day"""
        self.P_up = 0  # psuedocode C.6.C1
        """float: potential phosphorus uptake (kg/ha)"""
        self.act_P_up_each_layer = []  # psuedocode C.6.C.4
        """:obj:`list` of :obj:`float`: phosphorus uptake from each soil layer (kg/ha)"""
        self.P_act_up = 0  # psuedocode C.6.C.7
        """float: total uptake of phosphorus from soil (kg/ha)"""

        # yield
        self.HI_max = 0  # psuedocode C.10.B.1
        """float: potential (maximum) harvest index"""
        self.HI_min = 0  # psuedocode C.10.C.1
        """float: harvest index for the plant in drought conditions (minimum)"""
        self.HI_actual = 0  # psuedocode C.10.C.1 
        """float: actual harvest index"""
        self.HI_opt = 0.9  # psuedocode C.10.D.1 
        """float: potential harvest index for the plant at maturity, given ideal growing conditions (optimal)"""
        self.harvest_eff = 0.9  # psuedocode C.10.D.1
        """float: harvest efficiency, as a percent of plant biomass"""
        self.gamma_wu = 0  # psuedocode C.9.C.1
        """float: water defficiency factor"""
        self.biomass_dry_down_percent = 0  # TODO: no pseudocode reference - GitHub Issue #168, #156
        self.DM_harvest_percent = 0.15  # TODO: no pseudocode reference - GitHub Issue #168, #156
        self.NDF_harvest_percent = 0.42  # TODO: no pseudocode reference - GitHub Issue #168, #156
        self.bio_AG = 0  # psuedocode C.10.H.1
        """float: Above ground biomass (kg/ha)"""
        self.bio_BG = 0  # psuedocode C.10.H.4
        """float: Below ground biomass (kg/ha)"""
        self.yield_max = 0  # psuedocode C.10.E.1
        """float: maximum yield (kg/ha)"""
        self.yield_actual = 0  # psuedocode C.10.E.1
        """float: actual crop yield at harvest (kg/ha)"""
        self.NDF_yield = 0  # TODO: no pseudocode reference - GitHub Issue #168
        self.N_yield = 0  # psuedocode C.10.F.1
        """float: amount of nitrogen removed in the yield (kg/ha)"""
        self.P_yield = 0  # psuedocode C.10.F.2
        """float: amount of phosphorus removed in the yield (kg/ha)"""
        self.N_yield_annual = 0
        """float: annual nitrogen yield"""
        self.P_yield_annual = 0
        """float: annual phosphorus yield"""
        self.NDF_yield_annual = 0  # TODO: no pseudocode reference - GitHub Issue #168
        self.DM_yield_annual = 0  # TODO: no pseudocode reference - GitHub Issue #168
        self.yield_annual = 0
        """float: Annual crop yield (kg/ha)"""

        # use data to set attributes, if given
        self._use_data(data)
        self._set_crop_name(crop_name)

        # fetch and set species-specific data, if needed
        if (species is not None) or (crop_name is not None):
            self._set_species(species)
            self._set_species_attributes(self._get_crop_data())

    def _use_data(self, data=None):
        """use input data to assign some attributes

           Args:
               data (dict): a dictionary of data containing "plant_years, "repeat",
               "planting_day", "harvest_day", "harvest_type", "planting_order",
               and "extracted"
        """
        if data is not None:
            self.plant_years = data['plant_years']
            self.repeat = data['repeat']
            self.planting_day = data['planting_day']
            self.harvest_day = data['harvest_day']
            self.harvest_type = data['harvest_type']
            self.planting_order = data['planting_order'].lower()
            self.extracted = data['extracted']

    def _set_crop_name(self, crop_name=None):
        """set the crop name attribute, if it is included as an argument

           Args:
               crop_name (str): the name of the crop
        """
        if crop_name is not None:
            self.crop_name = crop_name

    def _get_crop_data(self):
        """get the crop-specific data variable from crop_config.py

           Returns: a dictionary containing crop-specific data
        """
        return getattr(crop_config, self.species.upper())

    def _set_species(self, species=None):  # TODO: This should be deprecated, because species should be a required input - GitHub Issue #180
        """get the name of the species

           Args:
               species (str): one of the supported species

           Returns:
               if species is set to None (class default), then the species
               is derived from the ``crop_type`` attribute.
        """
        if species is None:
            # try to match the crop_name to items in the supported_species list
            try:
                self.species = [item.lower() for item in supported_species if self.crop_name.startswith(item.lower())].pop()
            except NameError:
                print("unsupported crop species")
        else:
            self.species = species

    def _set_species_attributes(self, data_variable):
        """set species-specific data attributes

           Args:
               data_variable: a dictionary containing BaseCrop attributes
        """
        for key, val in data_variable.items():
            setattr(self, key, val)

## TODO: The Crop() class needs to be updated to work with the new functionality of BaseCrop and the child - GitHub Issue #180
##  crop classes should have everything removed except species-specific methods.

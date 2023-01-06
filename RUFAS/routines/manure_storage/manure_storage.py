"""
RUFAS: Ruminant Farm Systems Model
File name: manure_storage.py

Description:
Description: Driver for the manure storage model

Author(s): William Donovan, wmdonovan@wisc.edu
"""
from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure_storage import (manure_emissions, manure_handling,
                                           manure_separator)

om = OutputManager()


def daily_manure_storage_routine(manure_storage, animal_management):
    manure_storage.reset_daily_variables()

    for pen_id in manure_storage.pens:
        pen = manure_storage.pens[pen_id]
        pen.update_pen(animal_management)
        manure_handling.update_all(pen, manure_storage)

    for separator_type in manure_storage.separators:
        separator = manure_storage.separators[separator_type]
        manure_separator.update_all(separator, manure_storage)

    for storage_type in manure_storage.storage:
        storage_system = manure_storage.storage[storage_type]
        manure_emissions.update_all(storage_system, manure_storage)

    manure_storage.summarize_manure_storage()
    manure_storage.summarize_annual_variables()


class ManureStorage:
    def __init__(self, animal_management):
        """
        Description:
            The ManureStorage class aggregates the components of the manure
            storage model and interacts with the animal model to access daily
            excreted manure.
            "pseudocode_manure_storage" MS.1

        Args:
            animal_management: an instance of the AnimalManagement class
                specified in animal_management.py
        """
        self.pens = {}
        self.separators = {}
        self.storage = {}

        # MS.1.2
        self.initialize_pens(animal_management)
        self.initialize_separators(animal_management)
        self.initialize_storage(animal_management)

        self.Bo = 0.24
        self.MCF = 0.01
        self.MCF = 0.01  # Methane Conversion Factor
        self.MS = 0.9  # manure handled in system (%)
        self.m3 = 0.662  # factor (CH4 to kg/m3)
        self.CH4_collection_efficiency = 0.0
        self.CH4_emissions = 0

        self.raw_manure = 0.0

        self.raw_manure_annual = 0.0

        self.initial_manure = 0.0
        self.manure_calc = 0.0
        self.manure_delta = 0.0
        self.manure_storage_balance_difference = 0.0

        self.initial_manure_annual = 0.0
        self.manure_calc_annual = 0.0
        self.manure_delta_annual = 0.0
        self.manure_storage_balance_difference_annual = 0.0

        self.manure_applied = 0.0
        self.N_applied = 0.0
        self.P_applied = 0.0

        self.manure_applied_annual = 0.0
        self.N_applied_annual = 0.0
        self.P_applied_annual = 0.0

        self.TS = 0
        self.VS = 0
        self.N = 0
        self.P = 0
        self.K = 0

        self.TS_liquid = 0
        self.VS_liquid = 0
        self.N_liquid = 0
        self.P_liquid = 0
        self.K_liquid = 0

        self.CH4_emissions_annual = 0

        self.TS_annual = 0
        self.VS_annual = 0
        self.N_annual = 0
        self.P_annual = 0
        self.K_annual = 0

        self.TS_liquid_annual = 0
        self.VS_liquid_annual = 0
        self.N_liquid_annual = 0
        self.P_liquid_annual = 0
        self.K_liquid_annual = 0

        self.TS_loss = 0.0
        self.VS_loss = 0.0

        self.TS_loss_annual = 0.0
        self.VS_loss_annual = 0.0

        self.TS_DM_effluent = 0.0

        self.TS_DM_effluent_annual = 0.0

        self.other_solids = 0.0
        self.other_liquids = 0.0

        self.other_solids_annual = 0.0
        self.other_liquids_annual = 0.0

    def initialize_pens(self, animal_management):
        """
        Description:
            Class helper method initializes ManureStorage's dictionary of pens
            based on the Animal model

        Args:
            animal_management
        """

        for pen in animal_management.all_pens:
            self.pens[pen.id] = (ManureStorage.Pen(pen))

    def initialize_separators(self, animal_management):
        """
        Description:
            Class helper method initializes ManureStorage's dictionary of
            separators based on the Animal model

        Args:
            animal_management
        """

        for pen in animal_management.all_pens:
            if not self.separators.keys().__contains__(pen.manure_separator):
                self.separators[pen.manure_separator] = (
                    ManureStorage.Separator(pen))

    def initialize_storage(self, animal_management):
        """
        Description:
            Class helper method initializes ManureStorage's dictionary of
            storage receptacles based on the Animal model

        Args:
            animal_management
        """

        for pen in animal_management.all_pens:
            if not self.storage.keys().__contains__(pen.manure_storage):
                self.storage[pen.manure_storage] = (ManureStorage.Storage(pen))

    def summarize_manure_storage(self):
        """
        Description:
            Class method summarizes whole-model variables from components for
            output
        """
        self.TS_loss = 0.0
        self.VS_loss = 0.0
        self.raw_manure = 0.0
        for pen in self.pens.values():
            self.raw_manure += pen.raw_manure
            self.TS_loss += pen.TS_loss
            self.VS_loss += pen.VS_loss

        self.TS_DM_effluent = 0.0
        for separator in self.separators.values():
            self.TS_DM_effluent += separator.TS_DM_effluent

        self.TS = 0
        self.VS = 0
        self.N = 0
        self.P = 0
        self.K = 0

        self.TS_liquid = 0
        self.VS_liquid = 0
        self.N_liquid = 0
        self.P_liquid = 0
        self.K_liquid = 0

        for storage in self.storage.values():
            self.TS += storage.TS
            self.VS += storage.VS
            self.N += storage.N
            self.P += storage.P
            self.K += storage.K

            self.TS_liquid += storage.TS_liquid
            self.VS_liquid += storage.VS_liquid
            self.N_liquid += storage.N_liquid
            self.P_liquid += storage.P_liquid
            self.K_liquid += storage.K_liquid

        manure = self.TS + self.TS_liquid
        self.manure_delta = manure - self.initial_manure
        self.initial_manure = manure
        self.manure_calc = self.manure_delta + \
            self.TS + self.TS_liquid + self.TS_DM_effluent
        self.manure_storage_balance_difference = self.raw_manure - self.manure_calc
        self.other_solids = self.TS - (self.VS + self.N + self.P + self.K)
        self.other_liquids = self.TS_liquid - \
            (self.VS_liquid + self.N_liquid + self.P_liquid + self.K_liquid)

    def reset_daily_variables(self):
        self.CH4_emissions = 0.0
        self.TS = 0.0
        self.VS = 0.0
        self.N = 0.0
        self.P = 0.0
        self.K = 0.0
        self.TS_liquid = 0.0
        self.VS_liquid = 0.0
        self.N_liquid = 0.0
        self.P_liquid = 0.0
        self.K_liquid = 0.0
        self.TS_loss = 0.0
        self.VS_loss = 0.0
        self.TS_DM_effluent = 0.0
        self.other_solids = 0.0
        self.other_liquids = 0.0

        [separator.reset_daily_variables()
         for separator in self.separators.values()]

    def summarize_annual_variables(self):
        self.raw_manure_annual += self.raw_manure

        self.CH4_emissions_annual += self.CH4_emissions

        self.TS_annual += self.TS
        self.VS_annual += self.VS
        self.N_annual += self.N
        self.P_annual += self.P
        self.K_annual += self.K

        self.TS_liquid_annual += self.TS_liquid
        self.VS_liquid_annual += self.VS_liquid
        self.N_liquid_annual += self.N_liquid
        self.P_liquid_annual += self.P_liquid
        self.K_liquid_annual += self.K_liquid

        self.TS_loss_annual += self.TS_loss
        self.VS_loss_annual += self.VS_loss

        self.TS_DM_effluent_annual += self.TS_DM_effluent

        self.other_solids_annual += self.other_solids
        self.other_liquids_annual += self.other_liquids

    def annual_mass_balance(self):
        manure = self.TS + self.TS_liquid
        self.manure_delta_annual = manure - self.initial_manure_annual
        self.initial_manure_annual = manure
        self.manure_calc_annual = self.manure_delta_annual + self.TS_annual + \
            self.TS_liquid_annual + self.TS_DM_effluent_annual + \
            self.manure_applied_annual
        self.manure_storage_balance_difference_annual = self.raw_manure_annual - \
            self.manure_calc_annual

    class Pen:
        def __init__(self, pen):
            """
            Description:
                An instance of this class represents an animal pen for manure
                storage purposes. It is primarily used by the manure handling
                sub-module

            Args:
                pen: an instance of the Pen class specified in pen.py
            """

            self.pen_id = pen.id
            self.handling_system = pen.manure_handling
            self.bedding = pen.bedding_type
            self.separator = pen.manure_separator
            self.cow_num = len(pen.animals_in_pen)
            self.raw_manure = pen.manure['Mkg']

            self.VS_excreted = pen.manure['VSd'] + pen.manure['VSnd']
            self.TS_excreted = pen.manure['TSd']
            self.N_excreted = pen.manure['MN']
            self.P_excreted = pen.manure['p_excrt_manure']
            self.WIP_frac = pen.manure['WIP_frac']
            self.WIP = self.raw_manure * self.WIP_frac
            self.WOP_frac = pen.manure['WOP_frac']
            self.WOP = self.raw_manure * self.WOP_frac
            self.CH4 = pen.manure['CH4_manure']

            self.K_excreted = pen.manure['K_manure']

            self.density = 994.0

            self.bedding_added = 0
            self.water_use_rate = 0
            self.flush_water_volume = 0
            self.bedding_washed_perc = 0
            self.bedding_washed = 0
            self.bedding_dry_matter = 0

            self.TS_loss = 0.0
            self.VS_loss = 0.0

            self.TS_loss_perc = 0.02
            self.VS_loss_perc = 0.85
            self.flow_rate = 0

            self.calibrate_water_use()
            self.calibrate_bedding()

            self.bedding_washed = self.bedding_washed_perc * self.bedding_added
            self.flush_water_daily = self.water_use_rate * self.cow_num

        def update_pen(self, animal_management):
            pen = animal_management.all_pens[self.pen_id]
            self.raw_manure = pen.manure['Mkg']
            self.VS_excreted = pen.manure['VSd'] + pen.manure['VSnd']
            self.TS_excreted = pen.manure['TSd']
            self.N_excreted = pen.manure['MN']
            self.P_excreted = pen.manure['p_excrt_manure']
            self.K_excreted = pen.manure['K_manure']
            self.CH4 = pen.manure['CH4_manure']

            self.WIP_frac = pen.manure['WIP_frac']
            self.WIP = self.raw_manure * self.WIP_frac
            self.WOP_frac = pen.manure['WOP_frac']
            self.WOP = self.raw_manure * self.WOP_frac

        def calibrate_water_use(self):
            """
            Description:
                Class helper method calibrates the empirical manure handling
                model
                "pseudocode_manure_storage" MS.2
            """

            info_map = {"class": self.__class__.__name__,
                        "function": self.calibrate_water_use.__name__, }

            if self.handling_system.startswith("flush_system"):
                self.water_use_rate = 500
            elif self.handling_system.startswith("manual_scraping"):
                self.water_use_rate = 200
            elif self.handling_system.startswith("automatic_alley_scrapers"):
                self.water_use_rate = 100
            else:
                info_map["handling_system"] = self.handling_system
                handling_system_log = f"{self.handling_system} is not currently implemented" \
                    " as a handling method."
                " Setting to flush system."
                om.add_log("handling_system", handling_system_log, info_map)
                self.handling_system = "flush_system"
                self.calibrate_water_use()

        def calibrate_bedding(self):
            """
            Description:
                Class helper method calibrates the empirical manure handling
                model
                "pseudocode_manure_storage" MS.2
            """

            info_map = {"class": self.__class__.__name__,
                        "function": self.calibrate_bedding.__name__, }

            if self.bedding.startswith("organic"):
                self.bedding_added = 11.8
                self.bedding_dry_matter = 0.9
                self.bedding_washed_perc = 0.5
            elif self.bedding.startswith("sand"):
                self.bedding_added = 20
                self.bedding_dry_matter = 0.9
                self.bedding_washed_perc = 0.8
            else:
                info_map["bedding"] = self.bedding
                bedding_log = f"{self.bedding}, is not currently implemented as a bedding type"
                " for manure storage. Setting to organic bedding."
                om.add_log("bedding", bedding_log, info_map)
                self.bedding = "organic"
                self.calibrate_bedding()

    class Separator:
        def __init__(self, pen):
            """
            Description:
                An instance of this class represents an manure separator.
                It is primarily used by the manure separator sub-module

            Args:
                pen: an instance of the Pen class specified in pen.py
            """

            self.separator = pen.manure_separator
            self.storage_system = pen.manure_storage

            self.flush_water_volume = 0

            self.TS = 0
            self.VS = 0
            self.N = 0
            self.P = 0
            self.K = 0
            self.CH4 = 0
            self.WIP = 0
            self.WOP = 0

            self.TS_liquid = 0
            self.VS_liquid = 0
            self.N_liquid = 0
            self.P_liquid = 0
            self.K_liquid = 0

            self.TS_DM_effluent = 0.0

            self.TS_removal_efficiency = 0
            self.VS_removal_efficiency = 0
            self.N_removal_efficiency = 0
            self.P_removal_efficiency = 0
            self.K_removal_efficiency = 0
            self.flow_rate_evaporation = 0

            self.TS_DM_effluent_rate = 0

            self.calibrate_separator()

        def reset_daily_variables(self):
            self.flush_water_volume = 0

            self.TS = 0
            self.VS = 0
            self.N = 0
            self.P = 0
            self.K = 0
            self.CH4 = 0
            self.WIP = 0
            self.WOP = 0

            self.TS_liquid = 0
            self.VS_liquid = 0
            self.N_liquid = 0
            self.P_liquid = 0
            self.K_liquid = 0

            self.TS_DM_effluent = 0.0

        def calibrate_separator(self):
            """
            Description:
                Class helper method calibrates the empirical manure separator
                model
                "pseudocode_manure_storage" MS.2
            """

            info_map = {"class": self.__class__.__name__,
                        "function": self.calibrate_separator.__name__, }

            # TODO these are the options in the spreadsheet but there is no difference (not implemented yet)
            if self.separator.startswith("sedimentation"):
                self.TS_removal_efficiency = 0.3
                self.VS_removal_efficiency = 0.55
                self.N_removal_efficiency = 0.3
                self.P_removal_efficiency = 0.4
                self.K_removal_efficiency = 0.15
                self.TS_DM_effluent_rate = 0.2

            elif self.separator.startswith("decanting_centrifuge"):
                self.TS_removal_efficiency = 0.3
                self.VS_removal_efficiency = 0.55
                self.N_removal_efficiency = 0.3
                self.P_removal_efficiency = 0.4
                self.K_removal_efficiency = 0.15
                self.TS_DM_effluent_rate = 0.2

            elif self.separator.startswith("screw_press"):
                self.TS_removal_efficiency = 0.3
                self.VS_removal_efficiency = 0.55
                self.N_removal_efficiency = 0.3
                self.P_removal_efficiency = 0.4
                self.K_removal_efficiency = 0.15
                self.TS_DM_effluent_rate = 0.2

            elif self.separator.startswith("rotary_screen"):
                self.TS_removal_efficiency = 0.3
                self.VS_removal_efficiency = 0.55
                self.N_removal_efficiency = 0.3
                self.P_removal_efficiency = 0.4
                self.K_removal_efficiency = 0.15
                self.TS_DM_effluent_rate = 0.2

            elif self.separator.startswith("slope_screen"):
                self.TS_removal_efficiency = 0.3
                self.VS_removal_efficiency = 0.55
                self.N_removal_efficiency = 0.3
                self.P_removal_efficiency = 0.4
                self.K_removal_efficiency = 0.15
                self.TS_DM_effluent_rate = 0.2

            elif self.separator.startswith("belt_press"):
                self.TS_removal_efficiency = 0.3
                self.VS_removal_efficiency = 0.55
                self.N_removal_efficiency = 0.3
                self.P_removal_efficiency = 0.4
                self.K_removal_efficiency = 0.15
                self.TS_DM_effluent_rate = 0.2

            elif self.separator.startswith("moving_disc_press"):
                self.TS_removal_efficiency = 0.3
                self.VS_removal_efficiency = 0.55
                self.N_removal_efficiency = 0.3
                self.P_removal_efficiency = 0.4
                self.K_removal_efficiency = 0.15
                self.TS_DM_effluent_rate = 0.2

            elif self.separator.startswith("sand_separator"):
                self.TS_removal_efficiency = 0.3
                self.VS_removal_efficiency = 0.55
                self.N_removal_efficiency = 0.3
                self.P_removal_efficiency = 0.4
                self.K_removal_efficiency = 0.15
                self.TS_DM_effluent_rate = 0.2

            else:
                info_map["separator"] = self.separator
                separator_log = f"{self.separator} is not currently implemented as a separator." \
                    " Setting to sedimentation."
                om.add_log("separator", separator_log, info_map)
                self.separator = "sedimentation"
                self.calibrate_separator()

    class Storage:
        def __init__(self, pen):
            """
            Description:
                An instance of this class represents an storage receptacle.
                It is primarily used by the emissions sub-module

            Args:
                pen: an instance of the Pen class specified in pen.py
            """

            self.storage = pen.manure_storage

            self.TS = 0
            self.VS = 0
            self.N = 0
            self.P = 0
            self.K = 0
            self.CH4 = 0
            self.WIP = 0
            self.WIP_frac = 0
            self.WOP = 0
            self.WOP_frac = 0

            self.TS_liquid = 0
            self.VS_liquid = 0
            self.N_liquid = 0
            self.P_liquid = 0
            self.K_liquid = 0

    def annual_reset(self):
        self.manure_applied_annual = 0.0
        self.N_applied_annual = 0.0
        self.P_applied_annual = 0.0

        self.CH4_emissions_annual = 0.0

        self.TS_liquid_annual = 0.0
        self.VS_liquid_annual = 0.0
        self.N_liquid_annual = 0.0
        self.P_liquid_annual = 0.0
        self.K_liquid_annual = 0.0

        self.TS_loss_annual = 0.0
        self.VS_loss_annual = 0.0

        self.TS_DM_effluent_annual = 0.0

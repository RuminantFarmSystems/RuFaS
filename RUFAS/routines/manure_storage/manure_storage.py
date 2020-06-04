"""
RUFAS: Ruminant Farm Systems Model
File name: manure_storage.py

Description:
Description: Driver for the manure storage model

Author(s): William Donovan, wmdonovan@wisc.edu
"""
from RUFAS.routines.manure_storage import manure_emissions, manure_handling, manure_separator


def daily_manure_routine(manure):
    for pen_id in manure.pens:
        pen = manure.pens[pen_id]
        manure_handling.update_all(pen, manure)

    for separator_type in manure.separators:
        separator = manure.separators[separator_type]
        manure_separator.update_all(separator, manure)

    for storage_type in manure.storage:
        storage_system = manure.storage[storage_type]
        manure_emissions.update_all(storage_system, manure)

    manure.summarize_manure_storage()


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
                specified in animal_managment.py
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

        self.TS_storage = 0

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
                self.separators[pen.manure_separator] = (ManureStorage.Separator(pen))

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

        self.TS_storage = 0
        for storage in self.separators.values():
            self.TS_storage += storage.TS

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

            self.handling_system = pen.manure_handling
            self.bedding = pen.bedding_type
            self.separator = pen.manure_separator
            self.cow_num = len(pen.animals_in_pen)
            self.raw_manure = pen.manure['Mkg']
            self.density = 994.0

            self.VS_excreted = pen.manure['VSd'] + pen.manure['VSnd']
            self.TS_excreted = self.raw_manure - self.VS_excreted
            self.N_excreted = pen.manure['MN']
            self.P_excreted = pen.manure['p_excrt_manure']

            # TODO: Excreted Potassium will eventually be calculated in animal module
            self.K_excreted = 0.181 * self.cow_num

            self.bedding_added = 0
            self.water_use_rate = 0
            self.flush_water_volume = 0
            self.bedding_washed_perc = 0
            self.bedding_washed = 0
            self.bedding_dry_matter = 0

            self.TS_loss = 0.02
            self.VS_loss = 0.85
            self.flow_rate = 0
            self.NH4 = 0

            self.calibrate_water_use()
            self.calibrate_bedding()

            self.bedding_washed = self.bedding_washed_perc * self.bedding_added
            self.flush_water_daily = self.water_use_rate * self.cow_num

        def calibrate_water_use(self):
            """
            Description:
                Class helper method calibrates the empirical manure handling
                model
                "pseudocode_manure_storage" MS.2
            """

            if self.handling_system.startswith("flush_system"):
                self.water_use_rate = 500
            elif self.handling_system.startswith("manual_scraping"):
                self.water_use_rate = 200
            elif self.handling_system.startswith("automatic_alley_scrapers"):
                self.water_use_rate = 100
            else:
                print(self.handling_system, 'is not currently implemented as a handling method. '
                                            'Setting to flush system')
                self.handling_system = "flush_system"
                self.calibrate_water_use()

        def calibrate_bedding(self):
            """
            Description:
                Class helper method calibrates the empirical manure handling
                model
                "pseudocode_manure_storage" MS.2
            """

            if self.bedding.startswith("organic"):
                self.bedding_added = 11.8
                self.bedding_dry_matter = 0.9
                self.bedding_washed_perc = 0.5
            elif self.bedding.startswith("sand"):
                self.bedding_added = 20
                self.bedding_dry_matter = 0.9
                self.bedding_washed_perc = 0.8
            else:
                print(self.bedding, 'is not currently implemented as a bedding type for manure storage. '
                                    'Setting to organic bedding')
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

            self.TS_liquid = 0
            self.VS_liquid = 0
            self.N_liquid = 0
            self.P_liquid = 0
            self.K_liquid = 0

            self.TS_removal_efficiency = 0
            self.VS_removal_efficiency = 0
            self.N_removal_efficiency = 0
            self.P_removal_efficiency = 0
            self.K_removal_efficiency = 0
            self.flow_rate_evaporation = 0

            self.TS_DM_effluent_rate = 0

            self.calibrate_separator()

        def calibrate_separator(self):
            """
            Description:
                Class helper method calibrates the empirical manure separator
                model
                "pseudocode_manure_storage" MS.2
            """

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
                print(self.separator, 'is not currently implemented as a separator. Setting to sedimentation')
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

            self.TS_liquid = 0
            self.VS_liquid = 0
            self.N_liquid = 0
            self.P_liquid = 0
            self.K_liquid = 0

            self.WOP_frac = pen.manure['WOP_frac']
            self.WIP_frac = pen.manure['WIP_frac']

    def annual_reset(self):
        pass

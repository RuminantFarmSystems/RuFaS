"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu  
"""

from RUFAS.routines.manure_management import handlers, separators, treatments, storage_options


def daily_manure_storage_routine(manure_storage, animal_management):
    manure_storage.reset_daily_variables()

    for pen in manure_storage.pens.values():
        pen.reset_daily_variables()
        pen.update_pen(animal_management)
        pen.handler.reset_daily_variables()
        pen.handler.update_all(pen, manure_storage)

    for separator in manure_storage.separators.values():
        separator.reset_daily_variables()
        separator.update_all(manure_storage)

    for treatment in manure_storage.treatments:
        treatment.reset_daily_variables()
        treatment.update_all(manure_storage)

    for storage in manure_storage.storage.values():
        storage.reset_daily_variables()
        storage.update_all(manure_storage)

    manure_storage.summarize_manure_storage()
    manure_storage.summarize_annual_variables()


class ManureManagement:
    """ 
    Description:

    Attributes
    ----------
    
    """





class ManureStorage:
    def __init__(self, manure_management_data, animal_management):
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
        self.handlers = {}
        self.separators = {}
        self.treatments = {}
        self.storage = {}

        # MS.1.2
        handler_data = manure_management_data['handling']
        separator_data = manure_management_data['separators']
        treatment_data = manure_management_data['treatment_methods']
        storage_data = manure_management_data['storage_options']

        self.initialize_pens(manure_management_data, animal_management)
        self.initialize_handlers(handler_data)
        self.initialize_separators(separator_data)
        self.initialize_treatment(treatment_data)
        self.initialize_storage(storage_data)

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

    def initialize_pens(self, manure_management_data, animal_management):
        """
        Description:
            Class helper method initializes ManureStorage's dictionary of pens
            based on the Animal model

        Args:
            manure_management_data
            animal_management
        """

        for pen in animal_management.all_pens:
            self.pens[pen.id] = (ManureStorage.Pen(manure_management_data, pen))

    def initialize_handlers(self, handler_data):
        for pen in self.pens:
            if pen.handler not in self.handlers.keys():
                self.handlers[pen.handler] = handlers.base_handler.BaseHandler(handler_data[pen.handler])

    def initialize_separators(self, separator_data):
        """
        Description:
            Class helper method initializes ManureStorage's dictionary of
            separators based on the Animal model

        Args:
            separator_data
        """

        for pen in self.pens:
            if pen.manure_separator not in self.separators.keys():
                self.separators[pen.manure_separator] = (separators.base_separator.BaseSeparator(
                    separator_data[pen.separator],
                    pen))

    def initialize_treatment(self, treatment_data):
        for pen in self.pens:
            next_treatment = pen.storage
            for treatment in range(len(pen.treatments), 0, -1):
                if pen.treatments[treatment] not in self.treatments.keys():
                    self.treatments[treatment] = treatments.base_treatment.BaseTreatment(treatment_data[treatment],
                                                                                         next_treatment)
                    next_treatment = self.treatments[treatment]

    def initialize_storage(self, storage_data):
        """
        Description:
            Class helper method initializes ManureStorage's dictionary of
            storage receptacles based on the Animal model

        Args:
            storage_data
        """

        for pen in self.pens:
            if pen.storage not in self.storage.keys():
                self.storage[pen.storage] = (storage_options.base_storage.BaseStorage(storage_data[pen.storage]))

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
        self.manure_calc = self.manure_delta + self.TS + self.TS_liquid + self.TS_DM_effluent
        self.manure_storage_balance_difference = self.raw_manure - self.manure_calc
        self.other_solids = self.TS - (self.VS + self.N + self.P + self.K)
        self.other_liquids = self.TS_liquid - (self.VS_liquid + self.N_liquid + self.P_liquid + self.K_liquid)

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
        self.manure_storage_balance_difference_annual = self.raw_manure_annual - self.manure_calc_annual

    class Pen:
        def __init__(self, manure_management_data, pen):
            """
            Description:
                An instance of this class represents an animal pen for manure
                storage purposes. It is primarily used by the manure handling
                sub-module

            Args:
                pen: an instance of the Pen class specified in pen.py
            """

            self.pen_id = pen.id
            self.management_method = pen.manure_management
            self.handling_system = manure_management_data[self.management_method]['handling_system']
            self.separator = manure_management_data[self.management_method]['separator']
            self.storage = manure_management_data[self.management_method]['storage']
            self.bedding = pen.bedding_type
            self.cow_num = len(pen.animals_in_pen)
            self.raw_manure = pen.manure['Mkg']

            self.VS_excreted = pen.manure['VSd'] + pen.manure['VSnd']
            self.TS_excreted = self.raw_manure - self.VS_excreted
            self.N_excreted = pen.manure['MN']
            self.P_excreted = pen.manure['P_excrt_manure']

            self.K_excreted = pen.manure['K_excrt_manure']
            # self.K_excreted = 0.181 * self.cow_num

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
            self.NH4 = 0

            self.calibrate_water_use()
            self.calibrate_bedding()

            self.bedding_washed = self.bedding_washed_perc * self.bedding_added
            self.flush_water_daily = self.water_use_rate * self.cow_num

        def reset_daily_variables(self):
            self.bedding_added = 0
            self.water_use_rate = 0
            self.flush_water_volume = 0
            self.bedding_washed_perc = 0
            self.bedding_washed = 0
            self.bedding_dry_matter = 0

            self.TS_loss = 0.0
            self.VS_loss = 0.0

        def update_pen(self, animal_management):
            pen = animal_management.all_pens[self.pen_id]
            self.raw_manure += pen.manure['Mkg']
            self.VS_excreted += pen.manure['VSd'] + pen.manure['VSnd']
            self.TS_excreted += (self.raw_manure - self.VS_excreted)
            self.N_excreted += pen.manure['MN']
            self.P_excreted += pen.manure['p_excrt_manure']

            # TODO: Excreted Potassium will eventually be calculated in animal module
            self.K_excreted += 0.181 * self.cow_num

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

    class Handling:
        def __init__(self, handling_data, pen):
            # Cleaning
            # Constants
            # Milking and Holding
            self.flushing_water_volume_mlk = 0  # ltrs/day
            self.scraping_water_volume_mlk = 0  # ltrs/day

            # FreeStall
            self.flushing_water_volume_fr = 830  # ltrs/day
            self.scraping_water_volume_fr = 10  # ltrs/day

            self.sand_lane = None

            # Bedding
            if pen.bedding == 'organic':
                self.bedding_added = 1.97
                self.bedding_density = 250
            elif pen.bedding == 'sand':
                self.bedding_added = 22.4
                self.bedding_density = 1500
                self.sand_lane = self.SandLane(handling_data['sand_lane'])

            if 'LC' in pen.classes:
                self.flushing_water_volume_mlk = 50  # ltrs/day
                self.scraping_water_volume_mlk = 10  # ltrs/day

            if handling_data['default']:
                self.default_handling(pen.manure_handling)
            else:
                self.water_use_rate = handling_data['water_use_rate']
                self.time_per_cleaning = handling_data['time_per_cleaning']
                self.cleanings_per_day = handling_data['cleanings_per_day']

        def default_handling(self, manure_handler):
            if manure_handler == "manual_scraping":
                self.water_use_rate = 200
                self.time_per_cleaning = 8
                self.cleanings_per_day = 2
            elif manure_handler == "flush_system":
                self.water_use_rate = 500
                self.time_per_cleaning = 8
                self.cleanings_per_day = 2
            elif manure_handler == "automatic_alley_scrapers":
                self.water_use_rate = 100
                self.time_per_cleaning = 8
                self.cleanings_per_day = 2
            else:
                print(manure_handler, "does not have default settings. Setting to manual scraping.")
                self.default_handling("manual_scraping")

        class SandLane:
            def __init__(self, sand_lane_data):
                if sand_lane_data['default']:
                    self.default_sand_lane()
                else:
                    self.sand_separated = sand_lane_data['sand_separated']

            def default_sand_lane(self):
                self.sand_separated = 0.6

    class Separator:
        def __init__(self, separator_data, pen):
            """
            Description:
                An instance of this class represents an manure separator.
                It is primarily used by the manure separator sub-module

            Args:
                pen: an instance of the Pen class specified in pen.py
            """
            self.separator = pen.manure_separator
            self.storage_system = pen.manure_storage

            if separator_data['default']:
                self.calibrate_separator()

            else:
                self.TS_removal_efficiency = separator_data['TS_removal_efficiency']
                self.VS_removal_efficiency = separator_data['TS_removal_efficiency']
                self.N_removal_efficiency = separator_data["N_removal_efficiency"]
                self.P_removal_efficiency = separator_data["P_removal_efficiency"]
                self.K_removal_efficiency = separator_data["K_removal_efficiency"]
                self.TS_DM_effluent_rate = separator_data["TS_DM_effluent_rate"]
                if self.separator == 'sand_separator':
                    self.sand_separation_efficiency = separator_data['sand_separation_efficiency']

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

            self.TS_DM_effluent = 0

        def reset_daily_variables(self):
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

            self.TS_DM_effluent = 0.0

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
        def __init__(self, storage_data, pen):
            """
            Description:
                An instance of this class represents an storage receptacle.
                It is primarily used by the emissions sub-module

            Args:
                pen: an instance of the Pen class specified in pen.py
            """

            self.storage = pen.manure_storage

            if storage_data['default']:
                self.calibrate_storage()
            else:
                self.sludge_accumulation_volume = storage_data["sludge_accumulation_volume"]
                self.hydraulic_retention_time = storage_data["hydraulic_retention_time"]
                self.sludge_accumulation_period = storage_data["sludge_accumulation_period"]

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

        def calibrate_storage(self):
            self.sludge_accumulation_volume = 0.00251
            self.hydraulic_retention_time = 180
            self.sludge_accumulation_period = 5.0

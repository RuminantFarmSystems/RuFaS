"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
            Sadman Chowdhury, skc86@cornell.edu 
"""
from RUFAS.routines.manure_management import handlers, reception_pits, manure_separators, \
    treatments, storage_options

# TODO figure out how to import just all_pens
from RUFAS.routines.animal.animal_management import AnimalManagement as Animal_Module


# TODO figure out how to run the model 
# TODO figure out how to connect to csv values
"""
The function takes in the animal_management class and returns a dictionary with 
values of manure for all of the pens combined. I.e. it takes the U, the TAN_s,
etc from all of the pens, adds up each respective categories, and returns a dic
of the total manure for all of the pens.

Parameters:
    animal_management: animal management class

"""
def compile_manure_for_all_pens(Animal_Module):
    pens = Animal_Module["all_pens"]
    total_manure = {
            "U": 0,
            "TAN_s": 0,
            "MN": 0,
            "Mkg": 0,
            "TSd": 0,
            "VSd": 0,
            "VSnd": 0,
            "WIP_frac": 0,
            "WOP_frac": 0,
            "p_excrt_manure": 0,
            "p_frac": 0,
            "K_manure": 0,
            "CH4_manure": 0
    }
    for pen in pens:
        print(pen["manure"]["U"])
        total_manure["U"] += pen["manure"]["U"]
        total_manure["TAN_s"] += pen["manure"]["TAN_s"]
        total_manure["MN"] += pen["manure"]["MN"]
        total_manure["Mkg"] += pen["manure"]["Mkg"]
        total_manure["TSd"] += pen["manure"]["TSd"]
        total_manure["VSd"] += pen["manure"]["VSd"]
        total_manure["VSnd"] += pen["manure"]["VSnd"]
        total_manure["WIP_frac"] += pen["manure"]["WIP_frac"]
        total_manure["WOP_frac"] += pen["manure"]["WOP_frac"]
        total_manure["p_excrt_manure"] += pen["manure"]["p_excrt_manure"]
        total_manure["p_frac"] += pen["manure"]["p_frac"]
        total_manure["K_manure"] += pen["manure"]["K_manure"]
        total_manure["CH4_manure"] += pen["manure"]["CH4_manure"]


    return total_manure  

"""
    Takes a list of pen numbers and an instance of animal_management class, 
    combines the manure information for the pens passed in, and returns a
    dictionary with the combined information.

    Parameters:
        list_of_pen_numbers: a list of pen numbers, e.g. [1,2] means pen 1 and 2
        animal_management: instance of animal_management class
"""
def combine_manure_for_different_pens(list_of_pen_numbers, animal_management):
    pens = animal_management["all_pens"]
    total_manure = {
            "U": 0,
            "TAN_s": 0,
            "MN": 0,
            "Mkg": 0,
            "TSd": 0,
            "VSd": 0,
            "VSnd": 0,
            "WIP_frac": 0,
            "WOP_frac": 0,
            "p_excrt_manure": 0,
            "p_frac": 0,
            "K_manure": 0,
            "CH4_manure": 0
    }
    for i in list_of_pen_numbers:
        pen = pens[i]
        total_manure["U"] += pen["manure"]["U"]
        total_manure["TAN_s"] += pen["manure"]["TAN_s"]
        total_manure["MN"] += pen["manure"]["MN"]
        total_manure["Mkg"] += pen["manure"]["Mkg"]
        total_manure["TSd"] += pen["manure"]["TSd"]
        total_manure["VSd"] += pen["manure"]["VSd"]
        total_manure["VSnd"] += pen["manure"]["VSnd"]
        total_manure["WIP_frac"] += pen["manure"]["WIP_frac"]
        total_manure["WOP_frac"] += pen["manure"]["WOP_frac"]
        total_manure["p_excrt_manure"] += pen["manure"]["p_excrt_manure"]
        total_manure["p_frac"] += pen["manure"]["p_frac"]
        total_manure["K_manure"] += pen["manure"]["K_manure"]
        total_manure["CH4_manure"] += pen["manure"]["CH4_manure"]

    return total_manure



def daily_manure_storage_routine(animal_management, manure_management):
    print("Before calling reset")
    manure_management.reset_daily_variables0()
    print("after calling reset")

    compile_manure_for_all_pens(animal_management)

    for reception_pit in manure_management.reception_pits.values():
        reception_pit.update_all()

    for separator in manure_management.separators.values():
        separator.update_all()

    for treatment in manure_management.treatments:
        treatment.update_all()

    for storage in manure_management.storage.values():
        storage.update_all()

    manure_management.summarize_manure_management()
    manure_management.summarize_annual_variables()


class ManureManagement:
    def __init__(self, manure_management_data, animal_management):
        """
        Description:
            The ManureManagement class aggregates the components of the manure
            storage model and interacts with the animal model to access daily
            excreted manure.
            "pseudocode_manure_management" MS.1

        Args:
            animal_management: an instance of the AnimalManagement class
                specified in animal_management.py
        """

        self.total_manure = 0
        self.total_animals = 0
        self.animal_manager = animal_management
        self.management_systems = {}
        self.handlers = {}
        self.reception_pits = {}
        self.separators = {}
        self.treatments = {}
        self.storage = {}

        # MS.1.2
        self.construct_systems(animal_management, manure_management_data)

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
        self.manure_management_balance_difference = 0.0

        self.initial_manure_annual = 0.0
        self.manure_calc_annual = 0.0
        self.manure_delta_annual = 0.0
        self.manure_management_balance_difference_annual = 0.0

        self.manure_applied = 0.0
        self.N_applied = 0.0
        self.P_applied = 0.0

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
        self.TS_annual = 0
        self.VS_annual = 0
        self.N_annual = 0
        self.P_annual = 0
        self.K_annual = 0

        self.manure_applied_annual = 0.0
        self.N_applied_annual = 0.0
        self.P_applied_annual = 0.0

        self.CH4_emissions_annual = 0.0
        self.TS_liquid_annual = 0
        self.VS_liquid_annual = 0
        self.N_liquid_annual = 0
        self.P_liquid_annual = 0
        self.K_liquid_annual = 0

        self.TS_loss = 0.0
        self.VS_loss = 0.0

        self.TS_loss_annual = 0.0
        self.VS_loss_annual = 0.0

        self.other_solids = 0.0
        self.other_liquids = 0.0

        self.other_solids_annual = 0.0
        self.other_liquids_annual = 0.0

        self.TS_loss = 0.0
        self.VS_loss = 0.0

        self.TS_DM_effluent = 0.0
        self.TS_DM_effluent_annual = 0.0

        self.other_solids = 0.0
        self.other_liquids = 0.0

    def construct_systems(self, animal_management, manure_management_data):
        for pen in animal_management.all_pens:
            if pen.manure_management not in self.management_systems:
                if pen.manure_management not in manure_management_data['management_methods']:
                    print('Manure management specified for pen', pen.id,
                          'not specified in manure management JSON file. Setting to default.')
                    pen.manure_management = 'default'
                system = manure_management_data['management_methods'][pen.manure_management]
                handler = system['handler'] if 'handler' in system else 'null_handler'
                handler = handler + '_pen_' + str(pen.id)
                reception_pit = system['reception_pit'] if 'reception_pit' in system else 'null_reception'
                separator = system['separator'] if 'separator' in system else 'null_separator'
                treatment = system['treatment'] if 'treatment' in system else 'null_treatment'
                storage = system['storage'] if 'storage' in system else 'storage_pond'

                self.storage[storage] = self.storage[storage] if \
                    storage in self.storage else \
                    self.initialize_storage(storage, manure_management_data['storage_options'])

                self.treatments[treatment] = self.treatments[treatment] if \
                    treatment in self.treatments else \
                    self.initialize_treatment(treatment, self.storage[storage],
                                              manure_management_data['treatment_methods'])

                self.separators[separator] = self.separators[separator] if \
                    separator in self.separators else \
                    self.initialize_separator(separator, self.treatments[treatment],
                                              manure_management_data['separators'])

                self.reception_pits[reception_pit] = self.reception_pits[reception_pit] if \
                    reception_pit in self.reception_pits else \
                    self.initialize_reception_pit(reception_pit, self.separators[separator],
                                                  manure_management_data['reception_pits'])

                self.handlers[handler] = \
                    self.initialize_handler(pen, handler, self.reception_pits[reception_pit],
                                            manure_management_data['handlers'])

                self.management_systems[pen.manure_management] = pen.manure_management

    @staticmethod
    def initialize_handler(pen, handler, reception_pit, handler_data):
        if handler.startswith('null'):
            return handlers.null_handler.NullHandler(pen, reception_pit, handler=handler)

        if handler.split('_pen')[0] not in handler_data:
            print(handler, 'is not defined in manure management JSON. Updating to null.')
            return handlers.null_handler.NullHandler(pen, reception_pit, handler=handler)

        handler_data = handler_data[handler.split('_pen')[0]]

        if handler.__contains__('alley_scraper'):
            return handlers.alley_scraper.AlleyScraper(pen, handler, handler_data, reception_pit)
        elif handler.__contains__('flush_system'):
            return handlers.flush_system.FlushSystem(pen, handler, handler_data, reception_pit)
        elif handler.__contains__('manual_scraping'):
            return handlers.manual_scraping.ManualScraping(pen, handler, handler_data, reception_pit)
        else:
            print(handler, 'not currently implemented for manure management. Creating custom handler.')
            if {'water_use_rate', 'time_per_cleaning', 'cleanings_per_day'} not in handler_data:
                print('Cannot use default values for manure handler', handler, '. Setting to manual scraping.')
                return handlers.manual_scraping.ManualScraping(pen, handler, handler_data, reception_pit)
            else:
                return handlers.custom_handler.CustomHandler(pen, handler, handler_data, reception_pit)

    @staticmethod
    def initialize_reception_pit(reception_pit, separator, reception_pit_data):
        if reception_pit.startswith('null'):
            return reception_pits.null_reception_pit.NullReceptionPit(separator)
        if reception_pit not in reception_pit_data:
            print(reception_pit, 'is not defined in manure management JSON. Updating to null.')
            return reception_pits.null_reception_pit.NullReceptionPit(separator)

        reception_pit_data = reception_pit_data[reception_pit]

        return reception_pits.base_reception_pit.BaseReceptionPit(reception_pit, reception_pit_data, separator)

    @staticmethod
    def initialize_separator(separator, treatment, separator_data):
        if separator.startswith('null'):
            return manure_separators.null_separator.NullSeparator(treatment)

        if separator not in separator_data:
            print(separator, 'is not defined in manure management JSON. Updating to null.')
            return manure_separators.null_separator.NullSeparator(treatment)

        separator_data = separator_data[separator]

        if separator == 'base_separator':
            return manure_separators.base_separator.BaseSeparator(separator, separator_data, treatment)
        elif separator.__contains__('belt_press'):
            return manure_separators.belt_press.BeltPress(separator, separator_data, treatment)
        elif separator.__contains__('decanting_centrifuge'):
            return manure_separators.decanting_centrifuge.DecantingCentrifuge(separator, separator_data, treatment)
        elif separator.__contains__('mechanical_separator'):
            return manure_separators.mechanical_separator.MechanicalSeparator(separator, separator_data, treatment)
        elif separator.__contains__('moving_disc_press'):
            return manure_separators.moving_disc_press.MovingDiscPress(separator, separator_data, treatment)
        elif separator.__contains__('rotary_screen'):
            return manure_separators.rotary_screen.RotaryScreen(separator, separator_data, treatment)
        elif separator.__contains__('screw_press'):
            return manure_separators.screw_press.ScrewPress(separator, separator_data, treatment)
        elif separator.__contains__('sedimentation'):
            return manure_separators.sedimentation.Sedimentation(separator, separator_data, treatment)
        elif separator.__contains__('slope_screen'):
            return manure_separators.slope_screen.SlopeScreen(separator, separator_data, treatment)
        else:
            print(separator, 'not currently implemented for manure management. Creating custom separator.')
            if separator_data['default']:
                print('Cannot use default values for manure separator', separator, '. Setting to sedimentation.')
                return manure_separators.sedimentation.Sedimentation(separator, separator_data, treatment)
            else:
                return manure_separators.custom_separator.CustomSeparator(separator, separator_data, treatment)

    @staticmethod
    def initialize_treatment(treatment, storage, treatment_data):
        if treatment.startswith('null'):
            return treatments.null_treatment.NullTreatment(storage)

        if treatment not in treatment_data:
            print(treatment, 'not listed under treatments in manure management JSON file. Setting to null.')
            return treatments.null_treatment.NullTreatment(storage)

        treatment_data = treatment_data[treatment]

        if treatment == 'base_treatment':
            return treatments.base_treatment.BaseTreatment(treatment, treatment_data, storage)
        elif treatment == 'anaerobic_digester':
            return treatments.anaerobic_digester.AnaerobicDigester(treatment, treatment_data, storage)
        else:
            print(treatment, 'not currently implemented for manure management. Creating custom treatment.')
            if treatment_data['default']:
                print('Cannot use default values for manure treatment', treatment, '. Setting to anaerobic digester.')
                return treatments.anaerobic_digester.AnaerobicDigester(treatment, treatment_data, storage)
            else:
                return treatments.custom_treatment.CustomTreatment(treatment, treatment_data, storage)

    @staticmethod
    def initialize_storage(storage, storage_data):
        if storage not in storage_data:
            print(storage, 'not listed under storage options in manure management JSON file. Setting to storage pond.')
            storage = 'storage_pond'
        storage_data = storage_data[storage]
        if storage.__contains__('storage_pond'):
            return storage_options.storage_pond.StoragePond(storage, storage_data)
        elif storage.__contains__('anaerobic_lagoon'):
            return storage_options.anaerobic_lagoon.AnaerobicLagoon(storage, storage_data)
        else:
            print(storage, 'not currently implemented for manure management. Creating custom storage.')
            if storage_data['default']:
                print('Cannot use default values for manure storage', storage, '. Setting to storage pond.')
                return storage_options.storage_pond.StoragePond(storage, storage_data)
            else:
                return storage_options.custom_storage.CustomStorage(storage, storage_data)

    def summarize_manure_management(self):
        """
        Description:
            Class method summarizes whole-model variables from components for
            output
        """
        for pen in self.animal_manager.all_pens:
            self.total_animals += len(pen.animals_in_pen)

        self.TS_loss = 0.0
        self.VS_loss = 0.0
        self.raw_manure = 0.0
        for handler in self.handlers.values():
            self.raw_manure += handler.raw_manure
            self.TS_loss += handler.TS_loss
            self.VS_loss += handler.VS_loss

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
        self.manure_management_balance_difference = self.raw_manure - self.manure_calc
        self.other_solids = self.TS - (self.VS + self.N + self.P + self.K)
        self.other_liquids = self.TS_liquid - (self.VS_liquid + self.N_liquid + self.P_liquid + self.K_liquid)

    def reset_daily_variables0(self):
        print("Line 448")
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
        [handler.reset_daily_variables() for handler in self.handlers.values()] 
        [reception_pit.reset_daily_variables() for reception_pit in self.reception_pits.values()]
        [separator.reset_daily_variables() for separator in self.separators.values()]
        [treatment.reset_daily_variables() for treatment in self.treatments.values()]
        [storage.reset_daily_variables() for storage in self.storage.values()]

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

        [handler.reset_annual_variables() for handler in self.handlers.values()]
        [reception_pit.reset_annual_variables() for reception_pit in self.reception_pits.values()]
        [separator.reset_annual_variables() for separator in self.separators.values()]
        [treatment.reset_annual_variables() for treatment in self.treatments.values()]
        [storage.reset_annual_variables() for storage in self.storage.values()]

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
        self.manure_management_balance_difference_annual = self.raw_manure_annual - self.manure_calc_annual

"""
RUFAS: Ruminant Farm Systems Model
File name: db_report.py
Description: The report that writes to the database.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""

from datetime import datetime
import sqlite3
from .base_report import BaseReport
import json
from pathlib import Path


def unpack_input_json(f_path):
    """
    Unpacks all of the input JSON files to be written to the outputs database.

    Args:
        f_path: the top-level JSON file to read from

    Returns: dictionary which represents the JSON input for this run
    """
    result = {}
    try:
        with f_path.open('r') as f:
            overall_data = json.load(f)

            result['config'] = overall_data['config']

            result['weather'] = overall_data['weather']

            output_file = Path('input/output/' + overall_data['output'])
            with output_file.open('r') as o:
                result['output'] = json.load(o)

            result['farm'] = {}
            result['farm']['fields'] = {}

            for field in overall_data['farm']['fields']:
                result['farm']['fields'][field] = {}

                soil_file = Path('input/soil/' +
                                 overall_data['farm']['fields'][field]['soil'])
                with soil_file.open('r') as s:
                    result['farm']['fields'][field]['soil'] = json.load(s)

                crop_file = Path('input/crop/' +
                                 overall_data['farm']['fields'][field]['crop'])
                with crop_file.open('r') as c:
                    result['farm']['fields'][field]['crop'] = json.load(c)

                management_file = \
                    Path('input/field_management/' +
                         overall_data['farm']['fields'][field][
                             'field_management'])
                with management_file.open('r') as m:
                    result['farm']['fields'][field]['field_management'] = \
                        json.load(m)

            animal_file = Path('input/animal/' + overall_data['farm']['animal'])
            with animal_file.open('r') as a:
                result['farm']['animal'] = json.load(a)

            feed_file = Path('input/feed/' + overall_data['farm']['feed'])
            with feed_file.open('r') as feed:
                result['farm']['feed'] = json.load(feed)
    except Exception as e:
        print("Error in unpack_input_json - likely an issue because the "
              "overall structure of the input JSON files has changed and "
              "this method was not updated:", e)
        raise e

    return result


class DBReport(BaseReport):
    def __init__(self, data, fPath):
        super().__init__(data)

        self.curr_result_id = -1
        self.db_file = "output_db/past_outputs.sqlite"
        self.version = data['version']
        self.user = data['user']

        # The code in this report does not write units to the tables (thus,
        # in the values of the dictionaries below, the second list item is
        # empty). Instead, there is a table called 'variable_descriptions'
        # which contains the description and units for each variable in all
        # tables.

        self.daily_variables = {
            'result_id': ['self.curr_result_id', '', []],
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []],
            'num_calf': ['len(animal_management.calves)', '', []],
            'num_heiferI': ['len(animal_management.heiferIs)', '', []],
            'num_heiferII': ['len(animal_management.heiferIIs)', '', []],
            'num_heiferIII': ['len(animal_management.heiferIIIs)', '', []],
            'num_cow': ['len(animal_management.cows)', '', []],
            'avg_milk_prod_by_cow': ['animal_management.daily_avg_milk',
                                     '', []],
            'total_milk_prod': ['animal_management.daily_total_milk', '', []],
            'total_manure_prod': ['animal_management.daily_total_manure',
                                  '', []],
            'water_runoff': ['fields.runoff', '', []],
            'water_leaching': ['fields.drainage', '', []],
            'N_runoff': ['fields.N_runoff', '', []],
            'N_leaching': ['fields.N_drainage', '', []],
            'P_runoff': ['fields.P_runoff', '', []],
            'P_leaching': ['fields.P_drainage', '', []]
        }

        self.annual_variables = {
            'result_id': ['self.curr_result_id', '', 0],
            'year': ['time.calendar_year', '', 0],
            'num_days_in_year': ['sum([(0 if day == None else 1) for day in '
                                 'time.years[time.year - 1]])', '', 0],
            'avg_num_calf': ['sum(animal_management.num_calf_lst) / '
                             'len(animal_management.num_calf_lst) '
                             'if len(animal_management.num_calf_lst) > 0 '
                             'else 0', '', 0],
            'avg_num_heiferI': ['sum(animal_management.num_heiferI_lst) / '
                                'len(animal_management.num_heiferI_lst) '
                                'if len(animal_management.num_heiferI_lst) > 0 '
                                'else 0', '', 0],
            'avg_num_heiferII': ['sum(animal_management.num_heiferII_lst) / '
                                 'len(animal_management.num_heiferII_lst) if '
                                 'len(animal_management.num_heiferII_lst) > 0 '
                                 'else 0', '', 0],
            'avg_num_heiferIII': ['sum(animal_management.num_heiferIII_lst) / '
                                  'len(animal_management.num_heiferIII_lst) if '
                                  'len(animal_management.num_heiferIII_lst) > 0'
                                  ' else 0', '', 0],
            'avg_num_cow': ['sum(animal_management.num_cow_lst) / '
                            'len(animal_management.num_cow_lst) '
                            'if len(animal_management.num_cow_lst) > 0 else 0',
                            '', 0],
            'avg_milk_prod_by_cow_per_year': [
                'sum(animal_management.avg_milk_lst) / '
                'len(animal_management.avg_milk_lst) '
                'if len(animal_management.avg_milk_lst) > 0 else 0', '', 0],
            'total_manure_prod': ['animal_management.annual_manure_prod', '',
                                  0],
            'total_water_runoff': ['fields.runoff_annual', '', 0],
            'total_water_leaching': ['fields.drainage_annual', '', 0],
            'total_N_runoff': ['fields.N_runoff_annual', '', 0],
            'total_N_leaching': ['fields.N_drainage_annual', '', 0],
            'total_P_runoff': ['fields.P_runoff_annual', '', 0],
            'total_P_leaching': ['fields.P_drainage_annual', '', 0],
        }

        self.purchased_feed_info_variables = {
            'result_id': ['self.curr_result_id', '', []],
            'year': ['time.calendar_year', '', []],
            'feed_id': ['str(feed_id)', '', []],
            'num_days_in_year': ['sum([(0 if day == None else 1) for day in '
                                 'time.years[time.year - 1]])', '', []],
            'total_purchased_feed': [
                'animal_management.purchased_feed_amounts[str(feed_id)] if '
                'str(feed_id) in '
                'animal_management.purchased_feed_amounts.keys() else 0', '',
                []],
            'total_cost': [
                'feed.feed_costs[str(feed_id)] * '
                'animal_management.purchased_feed_amounts[str(feed_id)] if '
                'str(feed_id) in '
                'animal_management.purchased_feed_amounts.keys() else 0',
                '', []],
            'embedded_C_footprint': ['0', '', []],
            'blue_water_footprint': ['0', '', []],
            'grey_water_footprint': ['0', '', []]
        }

        self.grown_feed_info_variables = {
            'result_id': ['self.curr_result_id', '', []],
            'year': ['time.calendar_year', '', []],
            'feed_id': ['str(feed_id)', '', []],
            'num_days_in_year': ['sum([(0 if day == None else 1) for day in '
                                 'time.years[time.year - 1]])', '', []],
            'crop_yield': ['total_yields[feed_id]', '', []],
            'total_hectares': ['total_hectares[feed_id]', '', []]
        }

        self.cow_print_variables = {
            'result_id': ['self.curr_result_id', '', 0],
            'year': ['time.calendar_year', '', 0],
            'num_days_in_year': ['sum([(0 if day == None else 1) for day in '
                                 'time.years[time.year - 1]])', '', 0],
            'herd_enteric_methane': ['0', '', 0],
            'lactating_cow_enteric_methane': ['0', '', 0],
            'dry_cow_enteric_methane': ['0', '', 0],
            'heifer_enteric_methane': ['0', '', 0],
            'milk_prod': ['animal_management.annual_milk_prod', '', 0],
            'milk_protein_prod': ['animal_management.annual_milk_protein_prod',
                                  '', 0],
            'milk_fat_prod': ['animal_management.annual_milk_fat_prod', '', 0],
            'avg_prod_per_lactation': [
                'animal_management.total_milk_prod_per_lactation / '
                'animal_management.num_cows_through_300_DIM if '
                'animal_management.num_cows_through_300_DIM > 0 else 0', '', 0],
            'calves_sold': ['animal_management.annual_calves_sold', '', 0],
            'heifers_sold': ['animal_management.annual_heifers_sold', '', 0],
            'cows_culled': ['animal_management.annual_cows_culled', '', 0],
            'calf_animal_days': ['animal_management.calf_animal_days', '', 0],
            'heiferI_animal_days': ['animal_management.heiferI_animal_days',
                                    '', 0],
            'heiferII_animal_days': ['animal_management.heiferII_animal_days',
                                     '', 0],
            'heiferIII_animal_days': ['animal_management.heiferIII_animal_days',
                                      '', 0],
            'lactating_cow_animal_days': [
                'animal_management.lactating_cow_animal_days', '', 0],
            'dry_cow_animal_days': ['animal_management.dry_cow_animal_days',
                                    '', 0]
        }

        self.feed_print_variables = {
            'result_id': ['self.curr_result_id', '', 0],
            'year': ['time.calendar_year', '', 0],
            'num_days_in_year': ['sum([(0 if day == None else 1) for day in '
                                 'time.years[time.year - 1]])', '', 0],
            'herd_DMI': ['animal_management.annual_herd_DMI', '', 0],
            'lactating_cow_DMI': ['animal_management.annual_lactating_cow_DMI',
                                  '', 0],
            'dry_cow_DMI': ['animal_management.annual_dry_cow_DMI', '', 0],
            'heifer_DMI': ['animal_management.annual_heifer_DMI', '', 0],
            'N2O_field_emissions': ['0', '', 0],
            'NH3_field_emissions': ['0', '', 0],
            'irrigation_blue_water_use': ['0', '', 0],
            'irrigation_grey_water_use': ['0', '', 0],
            'diesel_use': ['0', '', 0],
            'field_management_emissions': ['0', '', 0],
            'fertilizer_use': ['0', '', 0],
            'fertilizer_embedded_C_footprint': ['0', '', 0],
            'total_carbon_footprint_of_farm_grown_feed': ['0', '', 0],
            'erosion': ['fields.erosion_annual', '', 0],
            'change_in_soil_C_stock': ['0', '', 0]
        }

        self.energy_print_variables = {
            'result_id': ['self.curr_result_id', '', 0],
            'year': ['time.calendar_year', '', 0],
            'num_days_in_year': ['sum([(0 if day == None else 1) for day in '
                                 'time.years[time.year - 1]])', '', 0],
            'diesel_use': ['0', '', 0],
            'gasoline_use': ['0', '', 0],
            'kerosene': ['0', '', 0],
            'propane': ['0', '', 0],
            'compressed_methane_NG': ['0', '', 0],
            'generic_natural_gas': ['0', '', 0],
            'milk_cooling': ['0', '', 0],
            'water_heating': ['0', '', 0],
            'lighting': ['0', '', 0],
            'other': ['0', '', 0],
            'total_electricity_use': ['0', '', 0],
            'electricity_from_renewable_resource': ['0', '', 0],
            'solar_energy_generation': ['0', '', 0],
            'wind_energy_generation': ['0', '', 0],
            'anaerobic_energy_generation': ['0', '', 0],
            'anaerobic_natural_gas_generation': ['0', '', 0],
            'bioethanol_use': ['0', '', 0],
            'biodiesel_use': ['0', '', 0],
            'ghg_emissions': ['0', '', 0],
            'ghg_emission_milk_intensity': ['0', '', 0],
            'ghg_emission_land_intensity': ['0', '', 0]
        }

        self.daily_manure_variables = {
            'result_id': ['self.curr_result_id', '', []],
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []],
            'pen_id': ['pen_id', '', []],
            'number_animals': [
                'animal_management.get_num_animals_from_pen_id(pen_id)',
                '', []],
            'treatment': ['0', '', []],
            'housing_methane': ['0', '', []],
            'housing_direct_nitrous_oxide': ['0', '', []],
            'housing_indirect_nitrous_oxide': ['0', '', []],
            'housing_ammonia': ['0', '', []],
            'housing_carbon_dioxide': ['0', '', []],
            'management_methane': ['0', '', []],
            'management_direct_nitrous_oxide': ['0', '', []],
            'management_indirect_nitrous_oxide': ['0', '', []],
            'management_ammonia': ['0', '', []],
            'management_carbon_dioxide': ['0', '', []]
        }

        self.annual_manure_variables = {
            'result_id': ['self.curr_result_id', '', []],
            'year': ['time.calendar_year', '', []],
            'num_days_in_year': ['sum([(0 if day == None else 1) for day in '
                                 'time.years[time.year - 1]])', '', []],
            'pen_id': ['pen_id', '', []],
            'average_number_animals': [
                'animal_management.get_avg_num_animals_from_pen_id(pen_id)',
                '', []],
            'treatment': ['0', '', []],
            'housing_methane': ['0', '', []],
            'housing_direct_nitrous_oxide': ['0', '', []],
            'housing_indirect_nitrous_oxide': ['0', '', []],
            'housing_ammonia': ['0', '', []],
            'housing_carbon_dioxide': ['0', '', []],
            'management_methane': ['0', '', []],
            'management_direct_nitrous_oxide': ['0', '', []],
            'management_indirect_nitrous_oxide': ['0', '', []],
            'management_ammonia': ['0', '', []],
            'management_carbon_dioxide': ['0', '', []]
        }

        # For the database report, we are not producing a CSV file. This
        # check is to see if the user enabled the database report in the
        # input files.
        self.conn = None
        if self.produce_csv:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
            try:
                self.store_results_setup(unpack_input_json(fPath))
            except Exception as e:
                self.produce_csv = False

    def __del__(self):
        # close connection
        close_conn = self.produce_csv and self.conn is not None
        if close_conn:
            self.conn.close()

    def initialize(self):
        """
        Method overridden to avoid creating/writing to a CSV.
        """
        pass

    @staticmethod
    def write_headers(output_csv, variables):
        """
        Method overridden to avoid creating/writing to a CSV.
        """
        pass

    def produce_report_graphics(self):
        """
        Method overridden to avoid creating graphics.
        """
        pass

    def finalize(self, state, weather, time):
        """
        Commits the changes made to the database if the settings of this
        simulation has specified to do so.

        Args:
            state: instance of the State class
            weather: instance of the Weather class
            time: instance of the Timer class
        """
        if self.produce_csv:
            # save changes to database
            self.conn.commit()

    def get_cursor(self):
        """
        Returns a Cursor object from this instance's Connection.

        Returns: a Cursor object from this instance's Connection.
        """
        return self.conn.cursor()

    def store_results_setup(self, input_json):
        """
        Adds a row in the 'results' table for the current run.

        Args:
            input_json: dictionary representing the full JSON input for the run
        """
        try:
            c = self.get_cursor()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (self.report_name, timestamp, json.dumps(input_json),
                      self.version, self.user)
            insert_statement = "INSERT INTO results " \
                               "(title, created_at, input_data, " \
                               "version, user) VALUES (?, ?, ?, ?, ?)"

            c.execute(insert_statement, values)

            self.curr_result_id = c.lastrowid

        except Exception as e:
            print("The program has encountered the following exception while "
                  "connecting to and querying", self.db_file,
                  "during the setup of result store (store_results_setup()):\n",
                  e, "\nThis run's results will not be committed, and further "
                  "writes will not occur.")
            self.produce_csv = False

    def write_annual_report(self):
        """
        Method overridden to write to database instead of CSV.
        """
        try:
            c = self.get_cursor()
            # daily table writes
            # daily_results table
            insert_statement = \
                "INSERT INTO daily_results VALUES " + \
                "({})".format(','.join(['?'] * len(self.daily_variables)))

            row_list = []
            first_key = list(self.daily_variables.keys())[0]
            # The number of rows produced is the same as the number of entries
            # in the list for each of the variables.
            num_rows = len(self.daily_variables[first_key][2])
            for i in range(num_rows):
                curr_row = []
                for variable in self.daily_variables:
                    curr_row.append(self.daily_variables[variable][2][i])
                row_list.append(tuple(curr_row))

            c.executemany(insert_statement, row_list)

            # daily_manure table
            insert_statement = \
                "INSERT INTO daily_manure VALUES " + \
                "({})".format(','.join(['?'] *
                                       len(self.daily_manure_variables)))

            row_list = []
            first_key = list(self.daily_manure_variables.keys())[0]
            # The number of rows produced is the same as the number of entries
            # in the list for each of the variables.
            num_rows = len(self.daily_manure_variables[first_key][2])
            for i in range(num_rows):
                curr_row = []
                for variable in self.daily_manure_variables:
                    curr_row.append(self.daily_manure_variables[variable][2][i])
                row_list.append(tuple(curr_row))

            c.executemany(insert_statement, row_list)

            # annual table writes
            # annual_results table
            insert_statement = \
                "INSERT INTO annual_results VALUES " + \
                "({})".format(','.join(['?'] * len(self.annual_variables)))

            row = []
            for variable in self.annual_variables:
                row.append(self.annual_variables[variable][2])

            c.execute(insert_statement, tuple(row))

            # purchased_feed_info table
            insert_statement = \
                "INSERT INTO purchased_feed_info VALUES " + \
                "({})".format(','.join(['?'] *
                                       len(self.purchased_feed_info_variables)))

            row_list = []
            first_key = list(self.purchased_feed_info_variables.keys())[0]
            # The number of purchased feeds is the same as the number of entries
            # in the list for each of the variables.
            num_purchased_feeds = \
                len(self.purchased_feed_info_variables[first_key][2])
            for i in range(num_purchased_feeds):
                curr_row = []
                for variable in self.purchased_feed_info_variables:
                    curr_row.append(
                        self.purchased_feed_info_variables[variable][2][i])
                row_list.append(tuple(curr_row))

            c.executemany(insert_statement, row_list)

            # grown_feed_info table
            insert_statement = \
                "INSERT INTO grown_feed_info VALUES " + \
                "({})".format(','.join(['?'] *
                                       len(self.grown_feed_info_variables)))

            row_list = []
            first_key = list(self.grown_feed_info_variables.keys())[0]
            # The number of growing feeds is the same as the number of entries
            # in the list for each of the variables.
            num_growing_feeds = \
                len(self.grown_feed_info_variables[first_key][2])
            for i in range(num_growing_feeds):
                curr_row = []
                for variable in self.grown_feed_info_variables:
                    curr_row.append(
                        self.grown_feed_info_variables[variable][2][i])
                row_list.append(tuple(curr_row))

            c.executemany(insert_statement, row_list)

            # cow_print table
            insert_statement = \
                "INSERT INTO cow_print VALUES " + \
                "({})".format(','.join(['?'] * len(self.cow_print_variables)))

            row = []
            for variable in self.cow_print_variables:
                row.append(self.cow_print_variables[variable][2])

            c.execute(insert_statement, tuple(row))

            # feed_print table
            insert_statement = \
                "INSERT INTO feed_print VALUES " + \
                "({})".format(','.join(['?'] * len(self.feed_print_variables)))

            row = []
            for variable in self.feed_print_variables:
                row.append(self.feed_print_variables[variable][2])

            c.execute(insert_statement, tuple(row))

            # energy_print table
            insert_statement = \
                "INSERT INTO energy_print VALUES " + \
                "({})".format(','.join(['?'] *
                                       len(self.energy_print_variables)))

            row = []
            for variable in self.energy_print_variables:
                row.append(self.energy_print_variables[variable][2])

            c.execute(insert_statement, tuple(row))

            # annual_manure table
            insert_statement = \
                "INSERT INTO annual_manure VALUES " + \
                "({})".format(','.join(['?'] *
                                       len(self.annual_manure_variables)))

            row_list = []
            first_key = list(self.annual_manure_variables.keys())[0]
            # The number of pens is the same as the number of entries in the
            # list for each of the variables.
            num_pens = len(self.annual_manure_variables[first_key][2])
            for i in range(num_pens):
                curr_row = []
                for variable in self.annual_manure_variables:
                    curr_row.append(
                        self.annual_manure_variables[variable][2][i])
                row_list.append(tuple(curr_row))

            c.executemany(insert_statement, row_list)

        except Exception as e:
            print("The program has encountered the following exception while "
                  "connecting to and querying", self.db_file,
                  "during the annual writing of results "
                  "(write_annual_report()):\n", e,
                  "\nThis run's results will not be committed, and further "
                  "writes will not occur.")
            self.produce_csv = False

    def daily_update(self, state, weather, time):
        """
        Method overridden to also write to additional tables.

        Args:
            state: instance of the State class
            weather: instance of the Weather class
            time: instance of the Time class
        """
        super().daily_update(state, weather, time)

        animal_management = state.animal_management
        feed = state.feed
        manure_storage = state.manure_storage
        fields = state.fields
        life_cycle_manager = animal_management.life_cycle_manager

        for pen in animal_management.all_pens:
            pen_id = pen.id
            for variable in self.daily_manure_variables:
                self.daily_manure_variables[variable][2].append(
                    eval(self.daily_manure_variables[variable][0], globals(),
                         locals()))

    def annual_update(self, state, weather, time):
        """
       Method overridden to also write to additional tables.

       Args:
           state: instance of the State class
           weather: instance of the Weather class
           time: instance of the Time class
        """
        super().annual_update(state, weather, time)

        animal_management = state.animal_management
        feed = state.feed
        manure_storage = state.manure_storage
        fields = state.fields

        for feed_id in feed.purchased_feeds:
            for variable in self.purchased_feed_info_variables:
                self.purchased_feed_info_variables[variable][2].append(
                    eval(self.purchased_feed_info_variables[variable][0],
                         globals(), locals()))

        total_yields = {}
        total_hectares = {}
        for field in fields.fields.keys():
            c = fields.fields[field].crop.current_crop
            if c.raw_id not in total_yields.keys():
                total_yields[c.raw_id] = c.yield_annual
            else:
                total_yields[c.raw_id] += c.yield_annual

            if c.raw_id not in total_hectares.keys():
                total_hectares[c.raw_id] = fields.fields[field].soil.field_size
            else:
                total_hectares[c.raw_id] += fields.fields[field].soil.field_size

        for feed_id in total_yields.keys():
            for variable in self.grown_feed_info_variables:
                self.grown_feed_info_variables[variable][2].append(
                    eval(self.grown_feed_info_variables[variable][0],
                         globals(), locals()))

        for variable in self.cow_print_variables:
            self.cow_print_variables[variable][2] = \
                eval(self.cow_print_variables[variable][0], globals(), locals())

        for variable in self.feed_print_variables:
            self.feed_print_variables[variable][2] = \
                eval(self.feed_print_variables[variable][0], globals(),
                     locals())

        for variable in self.energy_print_variables:
            self.energy_print_variables[variable][2] = \
                eval(self.energy_print_variables[variable][0], globals(),
                     locals())

        for pen in animal_management.all_pens:
            pen_id = pen.id
            for variable in self.annual_manure_variables:
                self.annual_manure_variables[variable][2].append(
                    eval(self.annual_manure_variables[variable][0], globals(),
                         locals()))

    def annual_flush(self):
        """
        Method overridden to flush all of the other variables written to the
        database.
        """
        super().annual_flush()

        for variable in self.daily_manure_variables:
            self.daily_manure_variables[variable][2] = []

        for variable in self.purchased_feed_info_variables:
            self.purchased_feed_info_variables[variable][2] = []

        for variable in self.grown_feed_info_variables:
            self.grown_feed_info_variables[variable][2] = []

        for variable in self.cow_print_variables:
            self.cow_print_variables[variable][2] = 0

        for variable in self.feed_print_variables:
            self.feed_print_variables[variable][2] = 0

        for variable in self.energy_print_variables:
            self.energy_print_variables[variable][2] = 0

        for variable in self.annual_manure_variables:
            self.annual_manure_variables[variable][2] = []

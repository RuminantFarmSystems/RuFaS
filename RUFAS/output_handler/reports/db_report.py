from datetime import datetime
import sqlite3
from .base_report import BaseReport
import json
from pathlib import Path


class DBReport(BaseReport):
    def __init__(self, data, fPath):
        super().__init__(data)

        self.curr_result_id = -1
        self.db_file = "output_db/past_outputs.sqlite"
        self.version = data['version']
        self.user = data['user']

        self.daily_variables = {
            'result_id': ['self.curr_result_id', '', []],
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []],
            'num_calf': ['len(animal_management.calves)', '', []],
            'num_heiferI': ['len(animal_management.heiferIs)', '', []],
            'num_heiferII': ['len(animal_management.heiferIIs)', '', []],
            'num_heiferIII': ['len(animal_management.heiferIIIs)', '', []],
            'num_cow': ['len(animal_management.cows)', '', []],
            'avg_milk_prod_by_cow': ['animal_management.daily_avg_milk', '', []],
            'total_milk_prod': ['animal_management.daily_total_milk', '', []],
            'total_manure_prod': ['animal_management.daily_total_manure', '', []],
            'water_runoff': ['fields.runoff', '', []],
            'water_leaching': ['fields.drainage', '', []],
            'N_runoff': ['fields.N_runoff', '', []],
            'N_leaching': ['fields.N_drainage', '', []],
            'P_runoff': ['fields.P_runoff', '', []],
            'P_leaching': ['fields.P_drainage', '', []]
        }

        self.annual_variables = {
            'result_id': ['self.curr_result_id', '', []],
            'year': ['time.calendar_year', '', []],
            'num_days_in_year': ['sum([(0 if day == None else 1) for day in time.years[time.year - 1]])', '', []],
            'avg_num_calf': ['sum(animal_management.num_calf_lst) / len(animal_management.num_calf_lst) if len(animal_management.num_calf_lst) > 0 else 0', '', []],
            'avg_num_heiferI': ['sum(animal_management.num_heiferI_lst) / len(animal_management.num_heiferI_lst) if len(animal_management.num_heiferI_lst) > 0 else 0', '', []],
            'avg_num_heiferII': ['sum(animal_management.num_heiferII_lst) / len(animal_management.num_heiferII_lst) if len(animal_management.num_heiferII_lst) > 0 else 0', '', []],
            'avg_num_heiferIII': ['sum(animal_management.num_heiferIII_lst) / len(animal_management.num_heiferIII_lst) if len(animal_management.num_heiferIII_lst) > 0 else 0', '', []],
            'avg_num_cow': ['sum(animal_management.num_cow_lst) / len(animal_management.num_cow_lst) if len(animal_management.num_cow_lst) > 0 else 0', '', []],
            'avg_milk_prod_by_cow_per_year': ['sum(animal_management.avg_milk_lst) / len(animal_management.avg_milk_lst) if len(animal_management.avg_milk_lst) > 0 else 0', '', []],
            'total_manure_prod': ['animal_management.annual_manure_prod', '', []],
            'total_water_runoff': ['fields.runoff_annual', '', []],
            'total_water_leaching': ['fields.drainage_annual', '', []],
            'total_N_runoff': ['fields.N_runoff_annual', '', []],
            'total_N_leaching': ['fields.N_drainage_annual', '', []],
            'total_P_runoff': ['fields.P_runoff_annual', '', []],
            'total_P_leaching': ['fields.P_drainage_annual', '', []],
        }

        if self.produce_csv:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
            self.store_results_setup(self.unpack_input_json(fPath))

    def __del__(self):
        # close connection
        if self.produce_csv:
            self.conn.close()

    def initialize(self):
        # method overwritten to avoid creating/writing to CSV
        pass

    @staticmethod
    def write_headers(output_csv, variables):
        # method overwritten to avoid creating/writing to CSV
        pass

    def produce_report_graphics(self):
        # method overwritten to avoid creating graphics
        pass

    def finalize(self, state, weather, time):
        if self.produce_csv:
            # save changes to database
            self.conn.commit()

    def unpack_input_json(self, fPath):
        result = {}
        try:
            with fPath.open('r') as f:
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

                    soil_file = Path('input/soil/' + overall_data['farm']['fields'][field]['soil'])
                    with soil_file.open('r') as s:
                        result['farm']['fields'][field]['soil'] = json.load(s)

                    crop_file = Path('input/crop/' + overall_data['farm']['fields'][field]['crop'])
                    with crop_file.open('r') as c:
                        result['farm']['fields'][field]['crop'] = json.load(c)

                    management_file = Path('input/field_management/' +
                                           overall_data['farm']['fields'][field]['field_management'])
                    with management_file.open('r') as m:
                        result['farm']['fields'][field]['field_management'] = json.load(m)

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

        return result

    def store_results_setup(self, input_json):
        try:
            c = self.conn.cursor()

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
        # method overwritten to write to database instead of CSV
        try:
            c = self.conn.cursor()

            # daily table write
            insert_statement = \
                "INSERT INTO daily_results VALUES " + \
                "({})".format(','.join(['?'] * len(self.daily_variables)))

            for day in range(len(self.daily_variables['j_day'][2])):
                row = []
                for variable in self.daily_variables:
                    row.append(self.daily_variables[variable][2][day])

                c.execute(insert_statement, tuple(row))

            # annual table write
            insert_statement = \
                "INSERT INTO annual_results VALUES " + \
                "({})".format(','.join(['?'] * len(self.annual_variables)))

            row = []
            for variable in self.annual_variables:
                row.append(self.annual_variables[variable][2])

            c.execute(insert_statement, tuple(row))

        except Exception as e:
            print("The program has encountered the following exception while "
                  "connecting to and querying", self.db_file,
                  "during the annual writing of results "
                  "(write_annual_report()):\n", e,
                  "\nThis run's results will not be committed, and further "
                  "writes will not occur.")
            self.produce_csv = False

################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: db_view.py
Description: This file contains the RequestHandler class and when this file is
    run, the HTTP server is started locally at the specified port. The web page
    can be accessed by 'localhost:8000' (client) and this forms a connection to
    the server. This connection is kept alive until the program is killed.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################
import http.server
import socket
import socketserver
from urllib.parse import urlparse
import urllib.parse
import sqlite3
import json
import csv
import os

# port on machine through which connection to server hosted locally is made
PORT = 8000

# status codes
OK = 200
BAD_GATEWAY = 502
NOT_FOUND = 404

# directories
DB_OUTPUT_PATH = '../output/db_output/'
MANURE_PATH_SUFFIX = '/manure_module/'
FARM_ES_PATH_SUFFIX = '/farm_es_reports/'
FARM_ES_FEED_PRINT_PATH_SUFFIX = 'feed_print/'
FARM_ES_SUMMARY_PATH_SUFFIX = 'summary_report/'

# mapping from variable user sees/selects to table column name
VARIABLE_MAPPING = {}


def write_csv(file_name, column_headers, data_rows):
    file = open(file_name, "w")
    csv_writer = csv.writer(file)
    csv_writer.writerow(column_headers)
    csv_writer.writerows(data_rows)
    file.close()


def create_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        path_message = "Warning: Directory " + path + \
                       " already exists - old data will be overwritten."
        status = OK

    except OSError as e:
        path_message = "Creation of the directory " + path + \
                       " failed with exception " + str(e)
        status = BAD_GATEWAY

    else:
        path_message = "Successfully created the directory %s " % path
        status = OK

    return status, path_message


def create_all_dirs(title, result_id):
    path = DB_OUTPUT_PATH + str(result_id) + '_' + title
    status, path_message = create_dir(path)
    if not status == OK:
        return status, path_message

    manure_path = path + MANURE_PATH_SUFFIX
    status, manure_path_message = create_dir(manure_path)
    if not status == OK:
        return status, manure_path_message

    farm_es_path = path + FARM_ES_PATH_SUFFIX
    status, farm_es_path_message = create_dir(farm_es_path)
    if not status == OK:
        return status, farm_es_path_message

    feed_print_path = farm_es_path + FARM_ES_FEED_PRINT_PATH_SUFFIX
    status, feed_print_path_message = create_dir(feed_print_path)
    if not status == OK:
        return status, feed_print_path_message

    summary_path = farm_es_path + FARM_ES_SUMMARY_PATH_SUFFIX
    status, summary_path_message = create_dir(summary_path)
    if not status == OK:
        return status, summary_path_message

    return OK, "Successfully created directories", path + "/"


class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Based on which radio button is selected on the client side, a different type
    of request is sent to the server. The information that the server uses is
    the type of the request method (GET, POST, or DELETE - more specific
    information about each method type is found in the do_GET(), do_POST(),
    and do_DELETE() methods below) and the url to get information about the
    specific function that needs to be called as well as parameters provided
    by the user. The url is in the form '/path?query', where the query is in
    the form of
    'variable_name_1=value_1&variable_name_2=value_2&…&variable_name_n=value_n'.
    There are currently 5 supported paths:
        1. '/' : (GET) this signifies to the server that the client has
            requested the HTML page (i.e. the page has been refreshed).
            The server responds by sending index.html back to the client,
            which displays it on the page.
        2. '/getResults' : (GET) this signifies to the server that the client
            has requested to view the saved results that are currently in the
            'results' table of the outputs database. A JSON of this table, as
            well as the column names in the 'daily_results' and 'annual_results'
            tables are returned by the server. If the 'filter' parameter is
            specified, then the text in that parameter will be appended to the
            query.
        3. '/export' : (GET) this signifies to the server that the client has
            requested to export one or more entries in the 'results' table to
            csv files. The server responds by attempting to read the database
            and create the appropriate directories and csv files. The query for
            this request contains a list of the result IDs, a list of the
            columns from the daily results table to be exported, and a list of
            the columns from the annual results table to be exported.
        4. '/rename' : (POST) this signifies to the server that the client has
            requested to change one of the results by renaming it. The server
            responds by attempting to rename the result. The query for this
            request contains the result ID to rename as well as the new name.
        5. '/delete' : (DELETE) this signifies to the server that the client has
            requested to delete one of the results from the database. The server
            responds by deleting this result. The query for this request
            contains the result ID to delete.
    If the client sends a request with a different path than any of the ones
    listed above, the server responds with a 404 (NOT_FOUND) error.

    As described above, the client also sends the method type along with the url
    in the request to the server. The RequestHandler class inherits from
    BaseHTTPRequestHandler, which automatically calls the correct method
    (do_GET(), do_POST(), or do_DELETE()) based on the method type provided by
    the client. In each method, the url is parsed to get the path and different
    functions are called based on the path.

    For more information, see the Python documentation for http.server
    (https://docs.python.org/3/library/http.server.html) and urlib.parse
    (https://docs.python.org/3/library/urllib.parse.html).
    """

    def __init__(self, request, client_address, server):
        self.db_file = 'past_outputs.sqlite'
        super().__init__(request, client_address, server)

    def do_GET(self):
        """
        The GET HTTP method is used to request data from the server. This method
        is called when the javascript sends a request with method type "GET".
        """
        u = urlparse(self.path)
        if u.path == '/':
            file = None
            page = None

            try:
                file = open('index.html')
                page = file.read()

            except Exception as e:
                self.respond(BAD_GATEWAY, str(e))

            self.respond(OK, page)
            file.close()

        elif u.path == '/getResults':
            params = urllib.parse.parse_qs(u.query)
            if params != {}:
                query_appendix = params['filter'][0]
                status_code, returned_text = \
                    self.get_results_table(query_appendix=query_appendix)
            else:
                status_code, returned_text = self.get_results_table()

            self.respond(status_code, returned_text)

        elif u.path == '/export':
            params = urllib.parse.parse_qs(u.query)
            num_ids = [int(str_id) for str_id in params['id'][0].split(',')]
            daily_cols = params['daily'][0]
            annual_cols = params['annual'][0]
            daily_manure_cols = params['daily_manure'][0]
            annual_manure_cols = params['annual_manure'][0]
            farm_es_cols = {
                'summary_cols': params['summary'][0],
                'cow_print_cols': params['cow_print'][0],
                'feed_print_cols': params['feed_print'][0],
                'manure_print_cols': params['manure_print'][0],
                'energy_print_cols': params['energy_print'][0]
            }
            status_code, returned_text = \
                self.multiple_to_csv(num_ids, daily_cols, annual_cols,
                                     daily_manure_cols, annual_manure_cols,
                                     farm_es_cols)
            self.respond(status_code, returned_text)

        else:
            self.respond(NOT_FOUND, str(u.path) + " is not a valid path.")

    def do_POST(self):
        """
        The POST HTTP method is used to send data to a server to change a
        resource. This method is called when the javascript sends a request
        with method type "POST".
        """
        u = urlparse(self.path)
        if u.path == '/rename':
            params = urllib.parse.parse_qs(u.query)
            rename_code, rename_returned_text = \
                self.re_title(int(params['id'][0]), params['new_title'][0])

            res_code, res_returned_text = self.get_results_table()

            # the whole request is successful if both operations above are
            status_code = OK if rename_code == res_code == OK else BAD_GATEWAY

            self.respond(status_code, rename_returned_text + res_returned_text)

        else:
            self.respond(NOT_FOUND, str(u.path) + " is not a valid path.")

    def do_DELETE(self):
        """
        The DELETE HTTP method deletes a resource. This method
        is called when the javascript sends a request with method type "DELETE".
        """
        u = urlparse(self.path)
        if u.path == '/delete':
            params = urllib.parse.parse_qs(u.query)
            del_code, del_returned_text = \
                self.delete_results_set(int(params['id'][0]))

            res_code, res_returned_text = self.get_results_table()

            # the whole request is successful if both operations above are
            status_code = OK if res_code == res_code == OK else BAD_GATEWAY

            self.respond(status_code, del_returned_text + res_returned_text)

        else:
            self.respond(NOT_FOUND, str(u.path) + " is not a valid path.")

    def respond(self, status_code, text):
        """
        Sends a response with the given @status_code and @text.

        Args:
            status_code: one of OK, BAD_GATEWAY, NOT_FOUND
            text: the text that will be displayed on the page
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(text.encode())

    def get_results_table(self, query_appendix=None):
        """
        Connects to the past outputs database and obtains all entries in the
        Results table for display on the web-page. Also returns all of the daily
        and annual column names.

        Args:
            query_appendix: (optional) a string with further filtering for the
                query

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = the JSON of the Results table in the outputs database
                    and the daily & annual column names or
                text = an error message if the operation was not successful
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "SELECT result_id, title, created_at, version, user " \
                    "FROM results"
            if query_appendix is not None:
                query += " WHERE " + query_appendix

            c.execute(query)
            results_table = []
            row = c.fetchone()
            while row is not None:
                results_table.append(dict(row))
                row = c.fetchone()

            # get columns of the daily_results table
            daily_query = "PRAGMA table_info('daily_results');"
            c.execute(daily_query)
            row = c.fetchone()
            daily_columns = []
            while row is not None:
                daily_columns.append(dict(row)['name'])
                row = c.fetchone()

            # get columns of the annual_results table
            annual_query = "PRAGMA table_info('annual_results');"
            c.execute(annual_query)
            row = c.fetchone()
            annual_columns = []
            while row is not None:
                annual_columns.append(dict(row)['name'])
                row = c.fetchone()

            # get columns of the daily_manure table
            daily_manure_query = "PRAGMA table_info('daily_manure');"
            c.execute(daily_manure_query)
            row = c.fetchone()
            daily_manure_columns = []
            while row is not None:
                daily_manure_columns.append(dict(row)['name'])
                row = c.fetchone()

            # get columns of the daily_manure table
            annual_manure_query = "PRAGMA table_info('annual_manure');"
            c.execute(annual_manure_query)
            row = c.fetchone()
            annual_manure_columns = []
            while row is not None:
                annual_manure_columns.append(dict(row)['name'])
                row = c.fetchone()

            # get columns of the cow_print table
            cow_print_query = "PRAGMA table_info('cow_print');"
            c.execute(cow_print_query)
            row = c.fetchone()
            cow_print_columns = []
            while row is not None:
                cow_print_columns.append(dict(row)['name'])
                row = c.fetchone()

            # get columns of the feed tables
            feed_print_query = "PRAGMA table_info('feed_print');"
            c.execute(feed_print_query)
            row = c.fetchone()
            feed_print_columns = []
            while row is not None:
                feed_print_columns.append(dict(row)['name'])
                row = c.fetchone()

            feed_print_columns.append('total_purchased_feed')
            feed_print_columns.append('purchased_feed_cost')
            feed_print_columns.append('purchased_feed_embedded_C_footprint')
            feed_print_columns.append('purchased_feed_blue_water_footprint')
            feed_print_columns.append('purchased_feed_grey_water_footprint')

            feed_print_columns.append('total_P_runoff')
            feed_print_columns.append('total_N_runoff')
            feed_print_columns.append('total_N_leaching')

            feed_print_columns.remove('result_id')
            feed_print_columns.remove('year')
            feed_print_columns.remove('num_days_in_year')

            # get columns of the energy_print table
            energy_print_query = "PRAGMA table_info('energy_print');"
            c.execute(energy_print_query)
            row = c.fetchone()
            energy_print_columns = []
            while row is not None:
                energy_print_columns.append(dict(row)['name'])
                row = c.fetchone()

            conn.close()

            # enumerate columns for FarmES summary report
            summary_columns = ['ghg_emissions',
                               'ghg_emission_milk_intensity',
                               'ghg_emission_land_intensity',
                               'milk_prod',
                               'crop_yield',
                               'total_hectares',
                               'total_purchased_feed'
                               ]

            # enumerate columns for manure print report
            manure_print_columns = ['methane_emissions',
                                    'nitrous_oxide_emissions',
                                    'ammonia_emissions',
                                    'carbon_dioxide_emissions']

            return OK, json.dumps({
                'results_table': results_table,
                'daily_columns': daily_columns,
                'annual_columns': annual_columns,
                'manure': {
                    'daily': daily_manure_columns,
                    'annual': annual_manure_columns
                },
                'farm_es': {
                    'summary': summary_columns,
                    'cow_print': cow_print_columns,
                    'feed_print': feed_print_columns,
                    'manure_print': manure_print_columns,
                    'energy_print': energy_print_columns
                }
            })

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to obtain stored results:\n" \
                            + str(e)
            return BAD_GATEWAY, error_message

    def delete_results_set(self, id_to_delete):
        """
        Connects to the past outputs database and deletes the result with ID
        @id_to_delete.

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = empty string if the operation was successful or
                text = an error message if not
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute(
                "DELETE FROM results WHERE result_id=?", (id_to_delete,))
            c.execute("DELETE FROM daily_results WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM annual_results WHERE result_id=?",
                      (id_to_delete,))

            conn.commit()
            conn.close()
            return OK, ""

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to and querying " + \
                            self.db_file + " to delete result " + \
                            str(id_to_delete) + ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def multiple_to_csv(self, result_ids, daily_cols, annual_cols,
                        daily_manure_cols, annual_manure_cols, farm_es_cols):
        """
        Calls to_csv() for each of the ids in @result_ids.

        Args:
            result_ids: a list of result IDs for which a group of csv files
                will be created
            daily_cols: string of the columns from the daily_results table that
                will be in the resulting csv files
            annual_cols: string of the columns from the annual_results table
                that will be in the resulting csv files

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful for all IDs or
                status_code = BAD_GATEWAY if not and
                text = message for the success of creating the directory
                text = an error message if the operation was not successful
        """
        path = '../output/db_output/'
        status, folder_path_message = create_dir(path)

        if not status == OK:
            return status, folder_path_message

        for result_id in result_ids:
            status, message = self.to_csv(result_id, daily_cols, annual_cols,
                                          daily_manure_cols, annual_manure_cols,
                                          farm_es_cols)
            if not status == OK:
                return status, message

        # if none of the above queries resulted in an error, return successful
        return OK, "Successfully created all directories"

    def to_csv(self, result_id, daily_cols, annual_cols, daily_manure_cols,
               annual_manure_cols, farm_es_cols):
        """
        Connects to the past outputs database and generates the csv files
        corresponding to the the ID @result_id. These files are currently placed
        in the output/db_output directory.

        Args:
            result_id: the result ID for which the daily results,
                annual results, variable descriptions, and input file will be
                created
            daily_cols: string of the columns from the daily_results table that
                will be in the resulting csv files
            annual_cols: string of the columns from the annual_results table
                that will be in the resulting csv files

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = message for the success of creating the directory
                text = an error message if the operation was not successful
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # get name from results table
            c.execute("SELECT title FROM results where result_id=?",
                      (result_id,))
            title_rows = c.fetchall()
            title = title_rows[0][0]

            # get data from variable descriptions table
            c.execute("SELECT * FROM variable_descriptions")
            descr_cols = [description[0] for description in c.description]
            descr_rows = c.fetchall()

            # get input json data
            c.execute("SELECT input_data FROM results WHERE result_id=?",
                      (result_id,))
            input_rows = c.fetchall()
            input_data = json.loads(input_rows[0][0])
            conn.close()

            daily_vars, daily_rows = self.read_table(result_id, 'daily_results',
                                                     daily_cols)
            annual_vars, annual_rows = self.read_table(result_id,
                                                       'annual_results',
                                                       annual_cols)
            daily_manure_vars, daily_manure_rows = \
                self.read_table(result_id, 'daily_manure', daily_manure_cols)
            annual_manure_vars, annual_manure_rows = \
                self.read_table(result_id, 'annual_manure', annual_manure_cols)

            _, _, path = create_all_dirs(title, result_id)

            write_csv(path + 'daily_results.csv', daily_vars, daily_rows)
            write_csv(path + 'annual_results.csv', annual_vars,
                      annual_rows)
            write_csv(path + 'variable_descriptions.csv', descr_cols,
                      descr_rows)

            input_json_file_name = path + '/' + title + '_input.json'
            input_json_file = open(input_json_file_name, "w")
            json.dump(input_data, input_json_file, indent=4)
            input_json_file.close()

            write_csv(path + MANURE_PATH_SUFFIX + 'daily_manure.csv',
                      daily_manure_vars, daily_manure_rows)
            write_csv(path + MANURE_PATH_SUFFIX + 'annual_manure.csv',
                      annual_manure_vars, annual_manure_rows)

            self.write_farm_es_outputs(result_id, path + FARM_ES_PATH_SUFFIX,
                                       farm_es_cols)

            return OK, "Successfully wrote to result set's outputs."

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def re_title(self, id_to_re_title, new_title):
        """
        Connects to the past outputs database and renames the result with ID
        @id_to_retitle to have the name @new_title.

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = empty string if the operation was successful or
                text = an error message if not
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute("UPDATE results SET title = ? WHERE result_id=?",
                      (new_title, id_to_re_title))
            conn.commit()

            conn.close()

            return OK, ""

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to rename result " + \
                            str(id_to_re_title) + ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def find_desired_cols(self, result_id, table, columns):
        # intersection with energy_print columns
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "PRAGMA table_info('" + table + "');"
            c.execute(query)
            row = c.fetchone()
            table_columns = set()
            while row is not None:
                table_columns.add(dict(row)['name'])
                row = c.fetchone()

            conn.close()

            desired_cols = \
                list(table_columns.intersection(set(
                    columns.split(','))))

            return desired_cols

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def perform_join(self):
        pass

    def write_farm_es_outputs(self, result_id, write_path, farm_es_cols):
        if len(farm_es_cols['summary_cols']) > 0:
            self.write_farm_summary_outputs(write_path +
                                            FARM_ES_SUMMARY_PATH_SUFFIX,
                                            result_id,
                                            farm_es_cols['summary_cols'])

        if len(farm_es_cols['cow_print_cols']) > 0:
            self.write_cow_print(write_path, result_id,
                                 farm_es_cols['cow_print_cols'])

        if len(farm_es_cols['feed_print_cols']) > 0:
            self.write_feed_print(write_path + FARM_ES_FEED_PRINT_PATH_SUFFIX,
                                  result_id, farm_es_cols['feed_print_cols'])

        if len(farm_es_cols['manure_print_cols']) > 0:
            self.write_manure_print(write_path, result_id, farm_es_cols[
                'manure_print_cols'])

        if len(farm_es_cols['energy_print_cols']) > 0:
            self.write_energy_print(write_path, result_id,
                                    farm_es_cols['energy_print_cols'])

    def read_table(self, result_id, table, cols):
        # cols: comma separated list of columsn
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            result_id_param = (result_id,)

            # get data from daily results
            daily_query = "SELECT " + cols + \
                          " FROM " + table + " WHERE result_id=?"
            c.execute(daily_query, result_id_param)
            result_col_names = [description[0] for description in c.description]
            result_rows = c.fetchall()

            conn.close()

            return result_col_names, result_rows

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def write_farm_summary_outputs(self, write_path, result_id, summary_vars):
        # find the intersection of the 'summary_vars' and the columns in
        # each of the energy_print, cow_print, grown_feed_info,
        # and purchased_feed_info tables to find the data that the user
        # specified
        desired_energy_print_cols = self.find_desired_cols(result_id,
                                                           'energy_print',
                                                           summary_vars)
        desired_cow_print_cols = self.find_desired_cols(result_id, 'cow_print',
                                                        summary_vars)
        desired_grown_feed_cols = self.find_desired_cols(result_id,
                                                         'grown_feed_info',
                                                         summary_vars)
        desired_purchased_feed_cols = \
            self.find_desired_cols(result_id, 'purchased_feed_info',
                                   summary_vars)

        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            cols_in_energy_join_cow = ",".join(desired_energy_print_cols +
                                               desired_cow_print_cols)

            result_id_param = (result_id,)
            query = 'SELECT energy_print.result_id, energy_print.year, ' \
                    '' + cols_in_energy_join_cow + \
                    ' FROM energy_print JOIN cow_print ' + \
                    'ON energy_print.result_id = cow_print.result_id AND ' + \
                    'energy_print.year = cow_print.year WHERE ' + \
                    'energy_print.result_id =?'
            c.execute(query, result_id_param)
            result_col_names = [description[0] for description in c.description]
            result_rows = c.fetchall()

            conn.close()

            write_csv(write_path + 'energy_and_cow_summary.csv',
                      result_col_names, result_rows)

            if len(desired_grown_feed_cols) > 0:
                desired_grown_feed_cols = 'result_id,year,feed_id,' + \
                                          ",".join(desired_grown_feed_cols)

                result_col_names, result_rows = \
                    self.read_table(result_id, 'grown_feed_info',
                                    desired_grown_feed_cols)

                write_csv(write_path + 'grown_feed_summary.csv',
                          result_col_names, result_rows)

            if len(desired_purchased_feed_cols) > 0:
                desired_purchased_feed_cols = 'result_id,year,feed_id,' + \
                                          ",".join(desired_purchased_feed_cols)

                result_col_names, result_rows = \
                    self.read_table(result_id, 'purchased_feed_info',
                                    desired_purchased_feed_cols)

                write_csv(write_path + 'purchased_feed_summary.csv',
                          result_col_names, result_rows)

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def write_cow_print(self, write_path, result_id, cow_print_vars):
        result_col_names, result_rows = self.read_table(result_id, 'cow_print',
                                                        cow_print_vars)

        write_csv(write_path + 'cow_print.csv', result_col_names, result_rows)

    def write_feed_print(self, write_path, result_id, feed_print_vars):
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # not all of the 'feed_print_vars' are columns of the 'feed_print'
            # table, so we must find the those that are columns to perform the
            # query on the table
            query = "PRAGMA table_info('feed_print');"
            c.execute(query)
            row = c.fetchone()
            feed_print_columns = set()
            while row is not None:
                feed_print_columns.add(dict(row)['name'])
                row = c.fetchone()

            desired_feed_print_cols = \
                list(feed_print_columns.intersection(set(
                    feed_print_vars.split(','))))

            # the feed print summary also includes a few variables from other
            # the annual_results table
            annual_results_cols = {'total_P_runoff', 'total_N_runoff',
                                   'total_N_leaching'}
            desired_annual_cols = list(annual_results_cols.intersection(set(
                feed_print_vars.split(','))))

            cols_in_annual_join_feed = ",".join(desired_feed_print_cols
                                                + desired_annual_cols)

            result_id_param = (result_id,)
            query = 'SELECT annual_results.result_id, annual_results.year, ' \
                    'annual_results.num_days_in_year,' \
                    '' + cols_in_annual_join_feed + \
                    ' FROM annual_results JOIN feed_print ' + \
                    'ON annual_results.result_id = feed_print.result_id AND '\
                    + \
                    'annual_results.year = feed_print.year WHERE ' + \
                    'annual_results.result_id =?'
            c.execute(query, result_id_param)
            result_col_names = [description[0] for description in c.description]
            result_rows = c.fetchall()

            write_csv(write_path + 'feed_print.csv', result_col_names,
                      result_rows)

            query = "PRAGMA table_info('purhcased_feed_info');"
            c.execute(query)
            row = c.fetchone()
            purchased_feed_columns = set()
            while row is not None:
                purchased_feed_columns.add(dict(row)['name'])
                row = c.fetchone()

            desired_purchased_feed_cols = []

            if 'total_purchased_feed' in feed_print_vars:
                desired_purchased_feed_cols.append('total_purchased_feed')
            if 'purchased_feed_cost' in feed_print_vars:
                desired_purchased_feed_cols.append('total_cost')
            if 'purchased_feed_embedded_C_footprint' in feed_print_vars:
                desired_purchased_feed_cols.append('embedded_C_footprint')
            if 'purchased_feed_blue_water_footprint' in feed_print_vars:
                desired_purchased_feed_cols.append('blue_water_footprint')
            if 'purchased_feed_grey_water_footprint' in feed_print_vars:
                desired_purchased_feed_cols.append('grey_water_footprint')

            if len(desired_purchased_feed_cols) > 0:
                desired_purchased_feed_cols = ['result_id', 'year', 'feed_id',
                                               'num_days_in_year'] + \
                                              desired_purchased_feed_cols

                result_col_names, result_rows = \
                    self.read_table(result_id, 'purchased_feed_info',
                                    ",".join(desired_purchased_feed_cols))

                write_csv(write_path + 'purchased_feed_print.csv',
                          result_col_names, result_rows)

            conn.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def write_manure_print(self, write_path, result_id, manure_print_vars):
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "PRAGMA table_info('manure_print');"
            c.execute(query)
            row = c.fetchone()
            manure_print_columns = set()
            while row is not None:
                manure_print_columns.add(dict(row)['name'])
                row = c.fetchone()

            desired_manure_cols = []

            if 'methane_emissions' in manure_print_vars:
                desired_manure_cols.append(
                    'SUM(housing_methane + management_methane) '
                    'as methane_emissions')
            if 'nitrous_oxide_emissions' in manure_print_vars:
                desired_manure_cols.append(
                    'SUM(housing_direct_nitrous_oxide '
                    '+ housing_indirect_nitrous_oxide '
                    '+ management_direct_nitrous_oxide '
                    '+ management_indirect_nitrous_oxide) '
                    'as nitrous_oxide_emissions')
            if 'ammonia_emissions' in manure_print_vars:
                desired_manure_cols.append('SUM(housing_ammonia + '
                                           'management_ammonia) as '
                                           'ammonia_emissions')
            if 'carbon_dioxide_emissions' in manure_print_vars:
                desired_manure_cols.append('SUM(housing_carbon_dioxide + '
                                           'management_carbon_dioxide) '
                                           'as carbon_dioxide_emissions')

            if len(desired_manure_cols) > 0:
                result_id_param = (result_id,)
                query = 'SELECT result_id, year, num_days_in_year, ' + \
                        ','.join(desired_manure_cols) + ' FROM annual_manure '\
                        + 'WHERE result_id =? GROUP BY year;'

                c.execute(query, result_id_param)
                result_col_names = [description[0] for description in
                                    c.description]
                result_rows = c.fetchall()

                write_csv(write_path + 'manure_print.csv',
                          result_col_names, result_rows)

            conn.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def write_energy_print(self, write_path, result_id, energy_print_vars):
        result_col_names, result_rows = self.read_table(result_id,
                                                        'energy_print',
                                                        energy_print_vars)

        write_csv(write_path + 'energy_print.csv',
                  result_col_names, result_rows)


# start the server locally at PORT
with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    print("serving at port", PORT)
    print("to open connection, type 'localhost:" + str(PORT) +
          "' into a web browser")
    print("to close connection/end this program, ctrl-c\n")
    httpd.serve_forever()

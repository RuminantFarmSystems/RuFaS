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

# constants for the column names visible to the user for exporting data
MANURE_PRINT_VARIABLE_MAPPING = \
    {
        'methane_emissions': 'SUM(housing_methane + management_methane) '
                             'as methane_emissions',
        'nitrous_oxide_emissions': 'SUM(housing_direct_nitrous_oxide '
                                   '+ housing_indirect_nitrous_oxide '
                                   '+ management_direct_nitrous_oxide '
                                   '+ management_indirect_nitrous_oxide) '
                                   'as nitrous_oxide_emissions',
        'ammonia_emissions': 'SUM(housing_ammonia + '
                             'management_ammonia) as '
                             'ammonia_emissions',
        'carbon_dioxide_emissions': 'SUM(housing_carbon_dioxide + '
                                    'management_carbon_dioxide) '
                                    'as carbon_dioxide_emissions'
    }
FEED_PRINT_PURCHASED_FEED_VARIABLE_MAPPING = \
    {
        'total_purchased_feed': 'total_purchased_feed',
        'purchased_feed_cost': 'total_cost',
        'purchased_feed_embedded_C_footprint': 'embedded_C_footprint',
        'purchased_feed_blue_water_footprint': 'blue_water_footprint',
        'purchased_feed_grey_water_footprint': 'grey_water_footprint'
    }
COLUMNS_TO_REMOVE = \
    [
        'result_id',
        'year',
        'num_days_in_year'
     ]
FEED_PRINT_COLUMNS_TO_ADD =  \
    [
        'total_P_runoff',
        'total_N_runoff',
        'total_N_leaching'
    ]
FARM_ES_SUMMARY_REPORT_COLUMNS = \
    [
        'ghg_emissions',
        'ghg_emission_milk_intensity',
        'ghg_emission_land_intensity',
        'milk_prod',
        'crop_yield',
        'total_hectares',
        'total_purchased_feed'
    ]


def write_csv(file_name, column_headers, data_rows):
    """
    Writes the given data to a CSV file.

    Args:
        file_name: str of the name of the file to write to
        column_headers: list of the column headers of the CSV file
        data_rows: list of lists of the data of the CSV file
    """
    file = open(file_name, "w")
    csv_writer = csv.writer(file)
    csv_writer.writerow(column_headers)
    csv_writer.writerows(data_rows)
    file.close()


def create_dir(path):
    """
    Creates the given directory.

    Args:
        path: str of the name of the directory to create

    Returns:
        (status_code, text) where
            status_code = one of OK or BAD_GATEWAY
            text = the text corresponding to the result of the attempted
                directory creation
    """
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
    """
    Creates the necessary directories for an export of a result set.

    Args:
        title: str of the result set title
        result_id: int corresponding the ID of the result set

    Returns:
        (status_code, text, path) where
            status_code = one of OK or BAD_GATEWAY
            text = the text corresponding to the result of the attempted
                directory creations
            path = the outermost directory for this result set
    """
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
            well as the column names in the necessary tables are returned by
            the server. If the 'filter' parameter is specified, then the text
            in that parameter will be appended to the query.
        3. '/export' : (GET) this signifies to the server that the client has
            requested to export one or more entries in the 'results' table to
            csv files. The server responds by attempting to read the database
            and create the appropriate directories and csv files. The query for
            this request contains a list of the result IDs, and a list of the
            columns from the results tables to be exported.
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
        Results table for display on the web-page. Also returns all of the
        column names for the data that can be exported.

        Args:
            query_appendix: (optional) a string with further filtering for the
                query

        Returns:
            (status_code, obj) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                obj = the JSON of the results table in the outputs database
                    and the columns that can be exported or
                obj = an error message if the operation was not successful
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

            conn.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to obtain stored results in " \
                                           "get_results_table():\n" + str(e)
            return BAD_GATEWAY, error_message

        status, daily_columns = self.get_columns('daily_results')
        if not status == OK:
            return status, daily_columns

        status, annual_columns = self.get_columns('annual_results')
        if not status == OK:
            return status, annual_columns

        status, daily_manure_columns = self.get_columns('daily_manure')
        if not status == OK:
            return status, daily_manure_columns

        status, annual_manure_columns = self.get_columns('annual_manure')
        if not status == OK:
            return status, annual_manure_columns

        status, cow_print_columns = self.get_columns('cow_print')
        if not status == OK:
            return status, cow_print_columns

        status, energy_print_columns = self.get_columns('energy_print')
        if not status == OK:
            return status, energy_print_columns

        status, feed_print_columns = self.get_columns('feed_print')
        if not status == OK:
            return status, feed_print_columns

        feed_print_columns += FEED_PRINT_COLUMNS_TO_ADD
        feed_print_columns += \
            list(FEED_PRINT_PURCHASED_FEED_VARIABLE_MAPPING.keys())
        for col in COLUMNS_TO_REMOVE:
            feed_print_columns.remove(col)

        return OK, json.dumps({
            'results_table': results_table,
            'daily_columns': daily_columns,
            'annual_columns': annual_columns,
            'manure': {
                'daily': daily_manure_columns,
                'annual': annual_manure_columns
            },
            'farm_es': {
                'summary': FARM_ES_SUMMARY_REPORT_COLUMNS,
                'cow_print': cow_print_columns,
                'feed_print': feed_print_columns,
                'manure_print': list(MANURE_PRINT_VARIABLE_MAPPING.keys()),
                'energy_print': energy_print_columns
            }
        })

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
            daily_manure_cols: string of the columns from the daily_manure
                table that will be in the resulting csv files
            annual_manure_cols: string of the columns from the annual_manure
                table that will be in the resulting csv files
            farm_es_cols: dictionary mapping the farm ES reports to the
                variables in each report

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = success message if the operation was successful or
                text = an error message if not
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

        return OK, "Successfully wrote to output for all result sets."

    def to_csv(self, result_id, daily_cols, annual_cols, daily_manure_cols,
               annual_manure_cols, farm_es_cols):
        """
        Connects to the past outputs database and generates the csv files
        corresponding to the the ID @result_id. These files are currently placed
        in the output/db_output directory.

        Args:
            result_id: the result ID for which the output exported files will be
                created
            daily_cols: string of the columns from the daily_results table that
                will be in the resulting csv files
            annual_cols: string of the columns from the annual_results table
                that will be in the resulting csv files
            daily_manure_cols: string of the columns from the daily_manure
                table that will be in the resulting csv files
            annual_manure_cols: string of the columns from the annual_manure
                table that will be in the resulting csv files
            farm_es_cols: dictionary mapping the farm ES reports to the
                variables in each report

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = an empty string if the operation was successful or
                text = an error message if not
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
            description_cols = [description[0] for description in c.description]
            description_rows = c.fetchall()

            # get input json data
            c.execute("SELECT input_data FROM results WHERE result_id=?",
                      (result_id,))
            input_rows = c.fetchall()
            input_data = json.loads(input_rows[0][0])
            conn.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            " in to_csv():\n" + str(e)
            return BAD_GATEWAY, error_message

        status, result = self.read_table(result_id, 'daily_results', daily_cols)
        if not status == OK:
            return status, result
        daily_vars, daily_rows = result

        status, result = self.read_table(result_id, 'annual_results',
                                         annual_cols)
        if not status == OK:
            return status, result
        annual_vars, annual_rows = result

        status, result = self.read_table(result_id, 'daily_manure',
                                         daily_manure_cols)
        if not status == OK:
            return status, result
        daily_manure_vars, daily_manure_rows = result

        status, result = \
            self.read_table(result_id, 'annual_manure', annual_manure_cols)
        if not status == OK:
            return status, result
        annual_manure_vars, annual_manure_rows = result

        status, message, path = create_all_dirs(title, result_id)
        if not status == OK:
            return status, message

        # write to the JSON file
        input_json_file_name = path + '/' + title + '_input.json'
        input_json_file = open(input_json_file_name, "w")
        json.dump(input_data, input_json_file, indent=4)
        input_json_file.close()

        # write to the CSV files
        write_csv(path + 'daily_results.csv', daily_vars, daily_rows)
        write_csv(path + 'annual_results.csv', annual_vars, annual_rows)
        write_csv(path + 'variable_descriptions.csv', description_cols,
                  description_rows)
        write_csv(path + MANURE_PATH_SUFFIX + 'daily_manure.csv',
                  daily_manure_vars, daily_manure_rows)
        write_csv(path + MANURE_PATH_SUFFIX + 'annual_manure.csv',
                  annual_manure_vars, annual_manure_rows)

        status, result = \
            self.write_farm_es_outputs(result_id, path + FARM_ES_PATH_SUFFIX,
                                       farm_es_cols)

        return status, result

    def write_farm_es_outputs(self, result_id, write_path, farm_es_cols):
        """
        Calls the appropriate method for each of the reports.

        Args:
            result_id: int corresponding the ID of the result set
            write_path: the directory in which to write the results
            farm_es_cols: dictionary mapping the reports to the variables in
                each report that the user selected

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = an empty string if the operation was successful or
                text = an error message if not
        """
        if len(farm_es_cols['summary_cols']) > 0:
            status, result = \
                self.write_farm_summary_outputs(write_path +
                                                FARM_ES_SUMMARY_PATH_SUFFIX,
                                                result_id,
                                                farm_es_cols['summary_cols'])
            if not status == OK:
                return status, result

        if len(farm_es_cols['cow_print_cols']) > 0:
            status, result = \
                self.write_cow_print(write_path, result_id,
                                     farm_es_cols['cow_print_cols'])

            if not status == OK:
                return status, result

        if len(farm_es_cols['feed_print_cols']) > 0:
            status, result = \
                self.write_feed_print(write_path +
                                      FARM_ES_FEED_PRINT_PATH_SUFFIX,
                                      result_id,
                                      farm_es_cols['feed_print_cols'])

            if not status == OK:
                return status, result

        if len(farm_es_cols['manure_print_cols']) > 0:
            status, result = \
                self.write_manure_print(write_path, result_id,
                                        farm_es_cols['manure_print_cols'])

            if not status == OK:
                return status, result

        if len(farm_es_cols['energy_print_cols']) > 0:
            status, result = \
                self.write_energy_print(write_path, result_id,
                                        farm_es_cols['energy_print_cols'])

            if not status == OK:
                return status, result

        return OK, ""

    def write_farm_summary_outputs(self, write_path, result_id, summary_vars):
        """
        Writes the summary report of the Farm ES reports.

        Args:
            write_path: the directory in which to write the results
            result_id: int corresponding the ID of the result set
            summary_vars: str of a comma separated list of the variables to
                be included in the CSV files

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = an empty string if the operation was successful or
                text = an error message if not:
        """
        # find the intersection of the 'summary_vars' and the columns in
        # each of the energy_print, cow_print, grown_feed_info,
        # and purchased_feed_info tables to find the data that the user
        # specified
        status, desired_energy_print_cols = \
            self.find_desired_cols(result_id, 'energy_print', summary_vars)
        if not status == OK:
            return status, desired_energy_print_cols

        status, desired_cow_print_cols = \
            self.find_desired_cols(result_id, 'cow_print', summary_vars)
        if not status == OK:
            return status, desired_cow_print_cols

        status, desired_grown_feed_cols = \
            self.find_desired_cols(result_id, 'grown_feed_info', summary_vars)
        if not status == OK:
            return status, desired_grown_feed_cols

        status, desired_purchased_feed_cols = \
            self.find_desired_cols(result_id, 'purchased_feed_info',
                                   summary_vars)
        if not status == OK:
            return status, desired_purchased_feed_cols

        cols_in_energy_join_cow = "energy_print.result_id, " \
                                  "energy_print.year, " + \
                                  ",".join(desired_energy_print_cols +
                                           desired_cow_print_cols)
        status, result = \
            self.perform_join(result_id, 'energy_print', 'cow_print',
                              cols_in_energy_join_cow)
        if not status == OK:
            return status, result
        result_col_names, result_rows = result

        write_csv(write_path + 'energy_and_cow_summary.csv',
                  result_col_names, result_rows)

        if len(desired_grown_feed_cols) > 0:
            desired_grown_feed_cols = 'result_id,year,feed_id,' + \
                                      ",".join(desired_grown_feed_cols)

            status, result = \
                self.read_table(result_id, 'grown_feed_info',
                                desired_grown_feed_cols)
            if not status == OK:
                return status, result
            result_col_names, result_rows = result

            write_csv(write_path + 'grown_feed_summary.csv',
                      result_col_names, result_rows)

        if len(desired_purchased_feed_cols) > 0:
            desired_purchased_feed_cols = 'result_id,year,feed_id,' + \
                                      ",".join(desired_purchased_feed_cols)

            status, result = \
                self.read_table(result_id, 'purchased_feed_info',
                                desired_purchased_feed_cols)
            if not status == OK:
                return status, result
            result_col_names, result_rows = result

            write_csv(write_path + 'purchased_feed_summary.csv',
                      result_col_names, result_rows)

        return OK, ""

    def write_cow_print(self, write_path, result_id, cow_print_vars):
        """
        Writes the cow print report of the Farm ES reports.

        Args:
            write_path: the directory in which to write the results
            result_id: int corresponding the ID of the result set
            cow_print_vars: str of a comma separated list of the variables to
                be included in the CSV files

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = an empty string if the operation was successful or
                text = an error message if not:
        """
        status, result = self.read_table(result_id, 'cow_print', cow_print_vars)
        if not status == OK:
            return status, result
        result_col_names, result_rows = result

        write_csv(write_path + 'cow_print.csv', result_col_names, result_rows)

        return OK, ""

    def write_feed_print(self, write_path, result_id, feed_print_vars):
        """
        Writes the feed print report of the Farm ES reports.

        Args:
            write_path: the directory in which to write the results
            result_id: int corresponding the ID of the result set
            feed_print_vars: str of a comma separated list of the variables to
                be included in the CSV files

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = an empty string if the operation was successful or
                text = an error message if not:
        """
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

            query = "PRAGMA table_info('purchased_feed_info');"
            c.execute(query)
            row = c.fetchone()
            purchased_feed_columns = set()
            while row is not None:
                purchased_feed_columns.add(dict(row)['name'])
                row = c.fetchone()

            desired_purchased_feed_cols = []
            for key in FEED_PRINT_PURCHASED_FEED_VARIABLE_MAPPING:
                if key in feed_print_vars:
                    desired_purchased_feed_cols.append(
                        FEED_PRINT_PURCHASED_FEED_VARIABLE_MAPPING[key])

            if len(desired_purchased_feed_cols) > 0:
                desired_purchased_feed_cols = ['result_id', 'year', 'feed_id',
                                               'num_days_in_year'] + \
                                              desired_purchased_feed_cols

                status, result = \
                    self.read_table(result_id, 'purchased_feed_info',
                                    ",".join(desired_purchased_feed_cols))
                if not status == OK:
                    return status, result
                result_col_names, result_rows = result

                write_csv(write_path + 'purchased_feed_print.csv',
                          result_col_names, result_rows)

            conn.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            " in write_feed_print():\n" + str(e)
            return BAD_GATEWAY, error_message

        desired_feed_print_cols = \
            list(feed_print_columns.intersection(set(
                feed_print_vars.split(','))))

        # the feed print summary also includes a few variables from other
        # the annual_results table
        annual_results_cols = {'total_P_runoff', 'total_N_runoff',
                               'total_N_leaching'}
        desired_annual_cols = list(annual_results_cols.intersection(set(
            feed_print_vars.split(','))))

        cols_in_annual_join_feed = "annual_results.result_id, " \
                                   "annual_results.year, " \
                                   "annual_results.num_days_in_year," + \
                                   ",".join(desired_feed_print_cols
                                            + desired_annual_cols)

        status, result = \
            self.perform_join(result_id, 'annual_results', 'feed_print',
                              cols_in_annual_join_feed)
        if not status == OK:
            return status, result
        result_col_names, result_rows = result

        write_csv(write_path + 'feed_print.csv', result_col_names,
                  result_rows)

        return OK, ""

    def write_manure_print(self, write_path, result_id, manure_print_vars):
        """
        Writes the manure print report of the Farm ES reports.

        Args:
            write_path: the directory in which to write the results
            result_id: int corresponding the ID of the result set
            manure_print_vars: str of a comma separated list of the variables to
                be included in the CSV files

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = an empty string if the operation was successful or
                text = an error message if not:

        """
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
            for key in MANURE_PRINT_VARIABLE_MAPPING:
                if key in manure_print_vars:
                    desired_manure_cols.append(
                        MANURE_PRINT_VARIABLE_MAPPING[key])

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
                            " in write_manure_print():\n" + str(e)
            return BAD_GATEWAY, error_message

        return OK, ""

    def write_energy_print(self, write_path, result_id, energy_print_vars):
        """
        Writes the energy print report of the Farm ES reports.

        Args:
            write_path: the directory in which to write the results
            result_id: int corresponding the ID of the result set
            energy_print_vars: str of a comma separated list of the variables to
                be included in the CSV files

         Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = an empty string if the operation was successful or
                text = an error message if not:
        """
        status, result = self.read_table(result_id, 'energy_print',
                                         energy_print_vars)
        if not status == OK:
            return status, result

        result_col_names, result_rows = result

        write_csv(write_path + 'energy_print.csv', result_col_names,
                  result_rows)

        return OK, ""

    # GENERAL DATABASE QUERY METHODS
    def read_table(self, result_id, table, cols):
        """
        Reads the given table and returns the data.

        Args:
            result_id: int corresponding the ID of the result set
            table: str of the table to read from
            cols: comma separated list of the columns to be read

        Returns:
            (status_code, obj) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                obj = a tuple containing the resulting column names and
                    the resulting rows if the operation was successful or
                obj = an error message if not:

        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            result_id_param = (result_id,)

            query = "SELECT " + cols + " FROM " + table + " WHERE result_id=?"
            c.execute(query, result_id_param)
            result_col_names = [description[0] for description in c.description]
            result_rows = c.fetchall()

            conn.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            " in read_table():\n" + str(e)
            return BAD_GATEWAY, error_message

        return OK, (result_col_names, result_rows)

    def delete_results_set(self, id_to_delete):
        """
        Connects to the past outputs database and deletes the result with ID
        @id_to_delete.

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = success message if the operation was successful or
                text = an error message if not
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute("DELETE FROM results WHERE result_id=?", (id_to_delete,))
            c.execute("DELETE FROM daily_results WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM annual_results WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM daily_manure WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM annual_manure WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM cow_print WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM energy_print WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM feed_print WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM grown_feed_info WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM purchased_feed_info WHERE result_id=?",
                      (id_to_delete,))

            conn.commit()
            conn.close()
        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to and querying " + \
                            self.db_file + " to delete result " + \
                            str(id_to_delete) + " in delete_results_set():\n"\
                            + str(e)
            return BAD_GATEWAY, error_message

        return OK, "Successfully deleted result set"

    def get_columns(self, table):
        """
        Returns the columns of the given table.

        Args:
            table: str of the table from which to read the columns

        Returns:
            (status_code, obj) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                obj = the columns of the given table if the operation was
                    successful or
                obj = an error message if not
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "PRAGMA table_info('" + table + "');"
            c.execute(query)
            row = c.fetchone()
            columns = []
            while row is not None:
                columns.append(dict(row)['name'])
                row = c.fetchone()

            conn.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to obtain stored results in " \
                                           "get_columns():\n" + str(e)
            return BAD_GATEWAY, error_message

        return OK, columns

    def perform_join(self, result_id,  left_table, right_table,
                     desired_columns):
        """
        Executes a SQL join on the given tables on the 'result_id' and 'year'
        columns.

        Args:
            result_id: int corresponding the ID of the result set
            left_table: str representing the left table of the join
            right_table: str representing the right table of the join
            desired_columns: the columns in the SELECT clause

        Returns:
            (status_code, obj) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                obj = a tuple containing the resulting column names and
                    the resulting rows if the operation was successful or
                obj = an error message if not
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            result_id_param = (result_id,)
            query = 'SELECT ' + desired_columns + \
                    ' FROM ' + left_table + ' JOIN ' + right_table + \
                    ' ON ' + left_table + '.result_id = ' + \
                    right_table + '.result_id AND ' + \
                    left_table + '.year = ' + right_table + '.year WHERE ' + \
                    left_table + '.result_id =?'
            c.execute(query, result_id_param)
            result_col_names = [description[0] for description in c.description]
            result_rows = c.fetchall()

            conn.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            " in perform_join():\n" + str(e)
            return BAD_GATEWAY, error_message

        return OK, (result_col_names, result_rows)

    def find_desired_cols(self, result_id, table, columns):
        """
        Returns the intersection between the given columns and the columns of
        the given table.

        Args:
            result_id: int corresponding the ID of the result set
            table: str of the table to read the columns from
            columns: list of columns that is the right half of the intersection

        Returns:
            (status_code, obj) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                obj = the desired columns if the operation was successful or
                obj = an error message if not
        """
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

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            " in find_desired_cols():\n" + str(e)
            return BAD_GATEWAY, error_message

        desired_cols = \
            list(table_columns.intersection(set(
                columns.split(','))))

        return OK, desired_cols

    def re_title(self, id_to_re_title, new_title):
        """
        Connects to the past outputs database and renames the result with ID
        @id_to_re_title to have the name @new_title.

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

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to rename result " + \
                            str(id_to_re_title) + " in re_title():\n" + str(e)
            return BAD_GATEWAY, error_message

        return OK, ""


# start the server locally at PORT
with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    print("serving at port", PORT)
    print("to open connection, type 'localhost:" + str(PORT) +
          "' into a web browser")
    print("to close connection/end this program, ctrl-c\n")
    httpd.serve_forever()

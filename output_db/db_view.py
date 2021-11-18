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
            farm_es_cols = {
                'summary_cols': params['summary'][0],
                'cow_print_cols': params['cow_print'][0],
                'feed_print_cols': params['feed_print'][0],
                'manure_print_cols': params['manure_print'][0],
                'energy_print_cols': params['energy_print'][0]
            }
            status_code, returned_text = \
                self.multiple_to_csv(num_ids, daily_cols, annual_cols,
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

            feed_print_columns.append('crop_yield')
            feed_print_columns.append('total_hectares')

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

    def multiple_to_csv(self, result_ids, daily_cols, annual_cols, farm_es_cols):
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
        for result_id in result_ids:
            status, message = self.to_csv(result_id, daily_cols, annual_cols,
                                          farm_es_cols)
            if not status == OK:
                return status, message

        # if none of the above queries resulted in an error, return successful
        return OK, "Successfully created all directories"

    def to_csv(self, result_id, daily_cols, annual_cols, farm_es_cols):
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

            result_id_param = (result_id,)

            # get data from daily results
            daily_query = "SELECT " + daily_cols + \
                          " FROM daily_results WHERE result_id=?"
            c.execute(daily_query, result_id_param)
            daily_vars = [description[0] for description in c.description]
            daily_rows = c.fetchall()

            # get data from annual results
            annual_query = "SELECT " + annual_cols + \
                           " FROM annual_results WHERE result_id=?"
            c.execute(annual_query, result_id_param)
            annual_vars = [description[0] for description in c.description]
            annual_rows = c.fetchall()

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

            # the following two try-except blocks make the directories that will
            # contain the csv files
            path = '../output/db_output'
            try:
                # create db_output folder
                os.mkdir(path)
            except FileExistsError:
                folder_path_message = "Directory " + path + " already exists."
            except OSError as e:
                folder_path_message = "Creation of the directory " + path + \
                               " failed with exception " + str(e)
            else:
                folder_path_message = "Successfully created the directory %s " \
                                      % path

            path += '/' + title
            try:
                #  folder for specific result set
                os.mkdir(path)
            except FileExistsError:
                path_message = "Warning: Directory " + path + \
                               " already exists - old data will be overwritten."

            except OSError as e:
                path_message = "Creation of the directory " + path + \
                               " failed with exception " + str(e)
            else:
                path_message = "Successfully created the directory %s " % path

            # create the two csv files using the title as name, the
            # variable description csv, and the input json file
            daily_file_name = path + '/' + title + "_daily.csv"
            annual_file_name = path + '/' + title + "_annual.csv"
            var_descr_file_name = path + '/' + 'variable_descriptions.csv'
            input_json_file_name = path + '/' + title + '_input.json'

            daily_file = open(daily_file_name, "w")
            annual_file = open(annual_file_name, "w")
            var_descr_file = open(var_descr_file_name, "w")
            input_json_file = open(input_json_file_name, "w")

            # open the csv writers
            csvWriterDaily = csv.writer(daily_file)
            csvWriterAnnual = csv.writer(annual_file)
            csvWriterDescr = csv.writer(var_descr_file)

            # write the headers/column names to the csv files
            csvWriterDaily.writerow(daily_vars)
            csvWriterAnnual.writerow(annual_vars)
            csvWriterDescr.writerow(descr_cols)

            # write the data to the csv files
            csvWriterDaily.writerows(daily_rows)
            csvWriterAnnual.writerows(annual_rows)
            csvWriterDescr.writerows(descr_rows)

            # write to input json file
            json.dump(input_data, input_json_file, indent=4)

            # close files
            daily_file.close()
            annual_file.close()
            var_descr_file.close()
            input_json_file.close()

            self.write_farm_es_outputs(result_id, path, farm_es_cols)

            return OK, folder_path_message + " " + path_message

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

    def write_farm_es_outputs(self, result_id, write_path, farm_es_cols):
        write_path += '/Farm ES reports'
        try:
            #  folder for specific result set
            os.mkdir(write_path)
        except FileExistsError:
            path_message = "Warning: Directory " + write_path + \
                           " already exists - old data will be overwritten."

        except OSError as e:
            path_message = "Creation of the directory " + write_path + \
                           " failed with exception " + str(e)
        else:
            path_message = "Successfully created the directory %s " % write_path

        if len(farm_es_cols['summary_cols']) > 0:
            self.write_farm_summary_outputs(write_path, result_id,
                                            farm_es_cols['summary_cols'])
        if len(farm_es_cols['cow_print_cols']) > 0:
            self.write_cow_print(write_path, result_id,
                                 farm_es_cols['cow_print_cols'])
        if len(farm_es_cols['feed_print_cols']) > 0:
            self.write_feed_print(write_path, result_id,
                                  farm_es_cols['feed_print_cols'])
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
        summary_dir = write_path + '/summary_report'
        try:
            #  folder for specific result set
            os.mkdir(summary_dir)
        except FileExistsError:
            path_message = "Warning: Directory " + summary_dir + \
                           " already exists - old data will be overwritten."

        except OSError as e:
            path_message = "Creation of the directory " + summary_dir + \
                           " failed with exception " + str(e)
        else:
            path_message = "Successfully created the directory %s " % summary_dir

        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # find the intersection of the 'summary_vars' and the columns in
            # each of the energy_print, cow_print, grown_feed_info,
            # and purchased_feed_info tables to find the data that the user
            # specified

            # intersection with energy_print columns
            query = "PRAGMA table_info('energy_print');"
            c.execute(query)
            row = c.fetchone()
            energy_print_columns = set()
            while row is not None:
                energy_print_columns.add(dict(row)['name'])
                row = c.fetchone()

            desired_energy_print_cols = \
                list(energy_print_columns.intersection(set(
                    summary_vars.split(','))))

            # intersection with cow_print columns
            query = "PRAGMA table_info('cow_print');"
            c.execute(query)
            row = c.fetchone()
            cow_print_columns = set()
            while row is not None:
                cow_print_columns.add(dict(row)['name'])
                row = c.fetchone()

            desired_cow_print_cols = \
                list(cow_print_columns.intersection(set(
                    summary_vars.split(','))))

            # intersection with grown_feed_info columns
            query = "PRAGMA table_info('grown_feed_info');"
            c.execute(query)
            row = c.fetchone()
            grown_feed_info_columns = set()
            while row is not None:
                grown_feed_info_columns.add(dict(row)['name'])
                row = c.fetchone()

            desired_grown_feed_cols = \
                list(grown_feed_info_columns.intersection(set(
                    summary_vars.split(','))))
            # intersection with purchased_feed_info columns
            query = "PRAGMA table_info('purchased_feed_info');"
            c.execute(query)
            row = c.fetchone()
            purchased_feed_info_columns = set()
            while row is not None:
                purchased_feed_info_columns.add(dict(row)['name'])
                row = c.fetchone()

            desired_purchased_feed_cols = \
                list(purchased_feed_info_columns.intersection(set(
                    summary_vars.split(','))))

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

            summary_file_name = summary_dir + '/energy_and_cow_summary.csv'
            summary_file = open(summary_file_name, "w")
            summary_csv_writer = csv.writer(summary_file)
            summary_csv_writer.writerow(result_col_names)
            summary_csv_writer.writerows(result_rows)
            summary_file.close()

            if len(desired_grown_feed_cols) > 0:
                desired_grown_feed_cols = 'result_id,year,feed_id,' + \
                                          ",".join(desired_grown_feed_cols)

                result_col_names, result_rows = \
                    self.read_table(result_id, 'grown_feed_info',
                                    desired_grown_feed_cols)

                grown_feed_file_name = summary_dir + '/grown_feed_summary.csv'
                grown_feed_file = open(grown_feed_file_name, "w")
                grown_feed_csv_writer = csv.writer(grown_feed_file)
                grown_feed_csv_writer.writerow(result_col_names)
                grown_feed_csv_writer.writerows(result_rows)
                grown_feed_file.close()

            if len(desired_purchased_feed_cols) > 0:
                desired_purchased_feed_cols = 'result_id,year,feed_id,' + \
                                          ",".join(desired_purchased_feed_cols)

                result_col_names, result_rows = \
                    self.read_table(result_id, 'purchased_feed_info',
                                    desired_purchased_feed_cols)

                purchased_feed_file_name = summary_dir + \
                                           '/purchased_feed_summary.csv'
                purchased_feed_file = open(purchased_feed_file_name, "w")
                purchased_feed_csv_writer = csv.writer(purchased_feed_file)
                purchased_feed_csv_writer.writerow(result_col_names)
                purchased_feed_csv_writer.writerows(result_rows)
                purchased_feed_file.close()

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            ":\n" + str(e)
            return BAD_GATEWAY, error_message

        pass

    def write_cow_print(self, write_path, result_id, cow_print_vars):
        result_col_names, result_rows = self.read_table(result_id, 'cow_print',
                                                        cow_print_vars)

        cow_print_file_name = write_path + '/cow_print.csv'
        cow_print_file = open(cow_print_file_name, "w")
        cow_print_csv_writer = csv.writer(cow_print_file)
        cow_print_csv_writer.writerow(result_col_names)
        cow_print_csv_writer.writerows(result_rows)
        cow_print_file.close()

    def write_feed_print(self, write_path, result_id, feed_print_vars):
        feed_dir = write_path + '/feed_print'
        try:
            #  folder for specific result set
            os.mkdir(feed_dir)
        except FileExistsError:
            path_message = "Warning: Directory " + feed_dir + \
                           " already exists - old data will be overwritten."

        except OSError as e:
            path_message = "Creation of the directory " + feed_dir + \
                           " failed with exception " + str(e)
        else:
            path_message = "Successfully created the directory %s " % feed_dir

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

            cols_in_annual_join_feed = ",".join(desired_feed_print_cols +
                                               desired_annual_cols)

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

            feed_print_file_name = feed_dir + '/feed_print.csv'
            feed_print_file = open(feed_print_file_name, "w")
            feed_print_csv_writer = csv.writer(feed_print_file)
            feed_print_csv_writer.writerow(result_col_names)
            feed_print_csv_writer.writerows(result_rows)
            feed_print_file.close()

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

                result_col_names, result_rows = self.read_table(result_id,
                                                                'purchased_feed_info',
                                                                ",".join(
                                                                desired_purchased_feed_cols))

                purchased_feed_print_file_name = feed_dir + \
                                               '/purchased_feed_print.csv'
                purchased_feed_print_file = open(purchased_feed_print_file_name,
                                                 "w")
                purchased_feed_print_csv_writer = csv.writer(
                    purchased_feed_print_file)
                purchased_feed_print_csv_writer.writerow(result_col_names)
                purchased_feed_print_csv_writer.writerows(result_rows)
                purchased_feed_print_file.close()

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
                desired_manure_cols.append('SUM(housing_methane + management_methane) as methane_emissions')
            if 'nitrous_oxide_emissions' in manure_print_vars:
                desired_manure_cols.append('SUM(housing_direct_nitrous_oxide '
                                           '+ housing_indirect_nitrous_oxide '
                                           '+ management_direct_nitrous_oxide '
                                           '+ management_indirect_nitrous_oxide) as nitrous_oxide_emissions')
            if 'ammonia_emissions' in manure_print_vars:
                desired_manure_cols.append('SUM(housing_ammonia + '
                                           'management_ammonia) as '
                                           'ammonia_emissions')
            if 'carbon_dioxide_emissions' in manure_print_vars:
                desired_manure_cols.append('SUM(housing_carbon_dioxide + '
                                           'management_carbon_dioxide) as carbon_dioxide_emissions')

            if len(desired_manure_cols) > 0:
                result_id_param = (result_id,)
                query = 'SELECT result_id, year, num_days_in_year, ' + \
                        ','.join(desired_manure_cols) + ' FROM annual_manure '\
                        + 'WHERE result_id =? GROUP BY year;'

                c.execute(query, result_id_param)
                result_col_names = [description[0] for description in
                                    c.description]
                result_rows = c.fetchall()

                manure_print_file_name = write_path + '/manure_print.csv'
                manure_print_file = open(manure_print_file_name, "w")
                manure_print_csv_writer = csv.writer(manure_print_file)
                manure_print_csv_writer.writerow(result_col_names)
                manure_print_csv_writer.writerows(result_rows)
                manure_print_file.close()

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

        energy_print_file_name = write_path + '/energy_print.csv'
        energy_print_file = open(energy_print_file_name, "w")
        energy_print_csv_writer = csv.writer(energy_print_file)
        energy_print_csv_writer.writerow(result_col_names)
        energy_print_csv_writer.writerows(result_rows)
        energy_print_file.close()


# start the server locally at PORT
with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    print("serving at port", PORT)
    print("to open connection, type 'localhost:" + str(PORT) +
          "' into a web browser")
    print("to close connection/end this program, ctrl-c\n")
    httpd.serve_forever()
